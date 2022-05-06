from threading import local
from urllib import request
import requests
import json
import datetime
from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.data.data_format import DataFormat
import pandas
from time import sleep
from azure.kusto.ingest import (
    QueuedIngestClient,
    IngestionProperties
)
import urllib3
import os

class NSXTConnection:
    def __init__(self, nsxtUri,nsxtUsername, nsxtPassword):
        self.nsxtUri = nsxtUri
        self.nsxtUsername = nsxtUsername
        self.nsxtPassword = nsxtPassword
        self.nsxtPolicyUri = nsxtUri+ "/policy/api/v1"

class NSXTTier0Interface:
    def __init__(self, path, edge_path,T0):
        self.path = path
        self.edge_path = edge_path
        self.name = path[path.rfind("/")+1:]
        self.NSXTier0 = T0
        self.connection= T0.connection
    def getInterfaceStats(self):
        return _getInterfaceStats(self)

class NSXTTier0:
    def __init__(self, path, name, connection):
        self.path = path
        self.name = name
        self.connection = connection
        self.local_services = _getT0LocaleServices(self.connection,self.path)
        self.interfaces = _getT0Interfaces(self)
    def getInterfacesStats(self):
        interfaceStats = []
        for interface in self.interfaces:
            interfaceStats.append(interface.getInterfaceStats())
        return pandas.concat(interfaceStats)

class NSXEdgeNode:
    def __init__(self, id, display_name, connection):
        self.id = id
        self.display_name = display_name
        self.connection = connection
    def getCPUStats(self):
        nodecpu = json.loads(_getAPIResults(nsxtConnection=self.connection,uri= "/api/v1/transport-nodes/"+self.id+"/node/services/dataplane/cpu-stats",policy=False))
        df = pandas.json_normalize(nodecpu, record_path=['cores'])
        df.columns = df.columns.str.replace('/','_',regex=False)
        df['precise_timestamp'] = datetime.datetime.now(tz=datetime.timezone.utc)
        df['t0_name'] = self.display_name
        return df

def _getT0Interfaces(NSXTTier0):
    interfaces = []
    results = json.loads(_getAPIResults(nsxtConnection=NSXTTier0.connection,uri= NSXTTier0.local_services+"/interfaces"))
    for tier0interface in results['results']:
        interfaces.append(NSXTTier0Interface(path = tier0interface['path'], edge_path=tier0interface['edge_path'],T0= NSXTTier0))
    return interfaces
    
def _getT0(nsxtConnection, id):
    results = json.loads(_getAPIResults(nsxtConnection=nsxtConnection, uri="/infra/tier-0s/"+id))
    return NSXTTier0(path = results['path'], name = results['display_name'], connection=nsxtConnection)

def getT0s(nsxtConnection):
    T0s = []
    results = json.loads(_getAPIResults(nsxtConnection=nsxtConnection, uri="/infra/tier-0s"))
    for t0 in results['results']:
        T0s.append(_getT0(nsxtConnection=nsxtConnection, id=t0['display_name']))
    return T0s

def _getT0LocaleServices(nsxtConnection,path):
    tier0locales = json.loads(_getAPIResults(nsxtConnection=nsxtConnection, uri=path+"/locale-services"))  
    return tier0locales['results'][0]['path']

def getInterfacesStats(tier0interfaces):
    frames =[]
    for tier0interface in tier0interfaces:
        interfaceStats = _getInterfaceStats(tier0interface)
        frames.append(interfaceStats)
    return pandas.concat(frames)

def _getInterfaceStats(tier0interface):
    statsuri = tier0interface.path+"/statistics?enforcement_point_path=/infra/sites/default/enforcement-points/default&edge_path="+tier0interface.edge_path
    tier0interfacestats = json.loads(_getAPIResults(nsxtConnection=tier0interface.connection, uri=statsuri))
    df = pandas.json_normalize(tier0interfacestats, record_path=['per_node_statistics'])
    #df = pandas.json_normalize(tier0interfacestats, record_path=['per_node_statistics'], meta='logical_router_port_id')
    #cols = df.columns.tolist()
    #cols = cols[-1:] + cols[:-1]
    #df = df[cols]
    df.columns = df.columns.str.replace('.','_',regex=False)
    df['precise_timestamp'] = datetime.datetime.fromtimestamp(int(tier0interfacestats['per_node_statistics'][0]['last_update_timestamp'])/1000,tz=datetime.timezone.utc)
    df['t0_name'] = tier0interface.NSXTier0.name
    df['t0_interface'] = tier0interface.name
    return(df)

def getEdgeNodes(nsxtConnection):
    nodes = []
    results = json.loads(_getAPIResults(nsxtConnection=nsxtConnection, uri="/api/v1/transport-nodes?node_types=EdgeNode", policy=False))['results']
    for node in results:
        nodes.append(NSXEdgeNode(id = node['node_id'],display_name = node['display_name'], connection=nsxtConnection))
    return nodes

def getCpuStats(nodes):
    frames = []
    for node in nodes:
        frames.append(node.getCPUStats())
    return pandas.concat(frames)

def _getAPIResults(nsxtConnection, uri,json_body=None, policy = True):
    if (policy == True):
        r = requests.request(method="GET",url=nsxtConnection.nsxtPolicyUri+uri ,json=json_body,auth = requests.auth.HTTPBasicAuth (nsxtConnection.nsxtUsername, nsxtConnection.nsxtPassword), verify=False)
    else:
        r = requests.request(method="GET",url=nsxtConnection.nsxtUri+uri ,json=json_body,auth = requests.auth.HTTPBasicAuth (nsxtConnection.nsxtUsername, nsxtConnection.nsxtPassword), verify=False)
    if r.status_code == "200":
        return str(r.content).replace("\\n","")[2:-1]
    return r.content


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    nsxtConnection = NSXTConnection(nsxtUri=os.environ['nsxturi'], nsxtUsername=os.environ['nsxusername'], nsxtPassword=os.environ['nsxpassword'])
    cluster = os.environ['kustoingesturi']
    ### Use cli auth if local
    if os.environ['local'] == "True":
            kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(cluster)
    else:
        kcsb = KustoConnectionStringBuilder.with_aad_managed_service_identity_authentication(cluster)
    client = QueuedIngestClient(kcsb)
    database_name = "nsx-t-stats"
    interface_ingestion_props = IngestionProperties(
        database=database_name,
        table="interface",
        data_format=DataFormat.CSV
    )
    cpu_ingestion_props = IngestionProperties(
        database=database_name,
        table="cpu",
        data_format=DataFormat.CSV
    )
    ### Get T0s Interfaces ###
    nsxtT0  = getT0s(nsxtConnection=nsxtConnection)[0]
    ### Get EVM Transport Nodes ###
    nodes = getEdgeNodes(nsxtConnection=nsxtConnection)
    while True:
        print("Get Interface Stats")
        interfacestats = nsxtT0.getInterfacesStats()
        print("Get CPU Stats")
        cpustats = getCpuStats(nodes=nodes)
        print("Ingest Interface Stats")
        client.ingest_from_dataframe(df=interfacestats,ingestion_properties=interface_ingestion_props)
        print("Ingest CPU Stats")
        client.ingest_from_dataframe(df=cpustats,ingestion_properties=cpu_ingestion_props)
        sleep(10)
    return

if __name__ == '__main__':
    main()