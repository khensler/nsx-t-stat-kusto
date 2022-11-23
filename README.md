- create a managed identity
- grant contributor and metrics publisher on the SDDC object for the managed identity
- create an ubuntu 22.04 vm in azure connected to a vnet with access to the private cloud and the internet
- assign the managed identity to the VM
- set the user data to AVS_CLOUD_ID=<AVS CLOUD RESOURCE ID>

- get a https credential for cloning https://dev.azure.com/msazure/One/_git/Azure-Dedicated-AVS-CPE/
- install:

`git clone https://<USERNAME>@dev.azure.com/msazure/One/_git/Azure-Dedicated-AVS-CPE -b azure-monitor`  
`sudo Azure-Dedicated-AVS-CPE/AVS-Azure-Monitor/Worker/install.sh`  

Look at the metrics of the SDDC.



https://portal.azure.com/#blade/Microsoft_Azure_CreateUIDef/CustomDeploymentBlade/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fkhensler%2Fnsx-t-stat-kusto%2Fazure-custom-metrics%2FDeployment%2Ftemplate.json/uiFormDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2Fkhensler%2Fnsx-t-stat-kusto%2Fazure-custom-metrics%2FDeployment%2FcreateUiDefinition.json