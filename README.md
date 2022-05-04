# Get NSX-T Stats and dump to Kusto
This is a solution for a customer to monitor thier NSX-T Edges for T0 interface metrics and Edge Node CPU metrics.
There are 4 ENV variables that must be set:
* "nsxturi": "https://NSX VIP IP"
* "nsxusername" : "Username"
* "nsxpassword" : "Password"
* "kustoingesturi" : "Kusto Ingest URI",

The local env variable can be set to allow for use of az cli creds (you must run az login before running the script):

* "local" : "True"
## Python Requirements
python3 and the modules in requirements.txt

## Kusto Requirements
The database name is "nsx-t-stats"

The tables interface and cpu must be defined:

.create table interface  (transport_node_id: string, last_update_timestamp: datetime, rx_total_bytes: double, rx_total_packets: double, rx_dropped_packets: double, rx_blocked_packets: double, rx_destination_unsupported_dropped_packets: double, rx_firewall_dropped_packets: double, rx_ipsec_dropped_packets: double, rx_ipsec_no_sa_dropped_packets: double, rx_ipsec_no_vti_dropped_packets: double, rx_ipv6_dropped_packets: double, rx_kni_dropped_packets: double, rx_l4port_unsupported_dropped_packets: double, rx_malformed_dropped_packets: double, rx_no_receiver_dropped_packets: double, rx_no_route_dropped_packets: double, rx_proto_unsupported_dropped_packets: double, rx_redirect_dropped_packets: double, rx_rpf_check_dropped_packets: double, rx_ttl_exceeded_dropped_packets: double, tx_total_bytes: double, tx_total_packets: double, tx_dropped_packets: double, tx_blocked_packets: double, tx_firewall_dropped_packets: double, tx_ipsec_dropped_packets: double, tx_ipsec_no_sa_dropped_packets: double, tx_ipsec_no_vti_dropped_packets: double, tx_dad_dropped_packets: double, tx_frag_needed_dropped_packets: double, tx_ipsec_pol_block_dropped_packets: double, tx_ipsec_pol_err_dropped_packets: double, tx_no_arp_dropped_packets: double, tx_no_linked_dropped_packets: double, tx_no_mem_dropped_packets: double, tx_non_ip_dropped_packets: double, tx_service_insert_dropped_packets: double, t0_name: string, t0_interface: string);

.create table cpu (busy_pollrounds: int, core: int, cpu_type: string, crypto: int, idle_pollrounds: int, intercore: int, kni: int, packet_processing_usage: int, rx: int, rx_pkts_pollround: int, slowpath: int, tx: int, usage:int,precise_timestamp: datetime, t0_name: string);

There is an example dashboard included dashboard-NSX-T EVM Interface Statistics.json