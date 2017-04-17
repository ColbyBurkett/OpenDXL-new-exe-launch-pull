# This script runs and listens for new PE launches reported by TIE.
# When the launch is seen, it instructs the client to copy that binary
# to another location. This location is arbitrary, but should be a write-only
# UNC path

import os
import sys
import logging
import mcafee
import urlquote
import time
import json

from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxltieclient import TieClient, FirstInstanceCallback

from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlmarclient import MarClient

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Connect to ePO with WebAPI
mc = mcafee.client('192.168.11.103','8443','admin','IsecG123!','https','json')
#ePOTag = 'Suspect'

class MyFirstInstanceCallback(FirstInstanceCallback):
    """
    My first instance callback
    """
    def on_first_instance(self, first_instance_dict, original_event):
        # Display the DXL topic that the event was received on
        print "First instance on topic: " + original_event.destination_topic

        # Dump the dictionary
        print json.dumps(first_instance_dict,
                         sort_keys=True, indent=4, separators=(',', ': '))
        agentGuid = json.dumps(first_instance_dict['agentGuid'])[1:-1]
        fileName = json.dumps(first_instance_dict['name'])[1:-1]
        sha1 = json.dumps(first_instance_dict['hashes']['sha1'])[1:-1]
        print agentGuid, fileName, sha1
        searchHASH(sha1,agentGuid,fileName)
        
# Create the client
client1 = DxlClient(config)
client2 = DxlClient(config)

# Connect to the fabric
client1.connect()
client2.connect()

# Create the McAfee Active Response (MAR) client
mar_client = MarClient(client1)

# Create the McAfee Threat Intelligence Exchange (TIE) client
tie_client = TieClient(client2)

# Create first instance callback
first_instance_callback = MyFirstInstanceCallback()

# Register first instance callback with the client
tie_client.add_file_first_instance_callback(first_instance_callback)

def searchHASH(sha1,agentGuid,fileName):
    # Performs the search
    # Execute the search
    print "Searching for hash: "+sha1
    result_context = mar_client.search(
            projections=[{
                    "name": "Files",
                    "outputs": ["full_name"]
                        }],
            conditions={
                "or": [{
                    "and": [{
                        "name": "Files",
                        "output": "sha1",
                        "op": "EQUALS",
                        "value": sha1
                    }]
                }]
            }
        )

    # Loop and display the results
    if result_context.has_results:
        search_result = result_context.get_results(limit=1)
        print "File found:"
        for item in search_result["items"]:
            filePath = item["output"]['Files|full_name']
            print filePath
            fileOut = agentGuid[1:-1]
            #fileOut = "test"
            f=open(fileOut,"w+")
            f.write(filePath)
            f.close()
            task = mc.clienttask.find('CollectFile')[0]
            taskId=task['objectId']
            productId=task['productId']
            systems = mc.system.find(agentGuid[1:-1])
            for system in systems:
                #mc.system.applyTag(system['EPOComputerProperties.ComputerName'],ePOTag)
                mc.clienttask.run(ids=system['EPOComputerProperties.ParentID'],taskId=taskId,productId=productId)
                #print system
                result_context = mar_client.search(
                        projections=[{
                                "name": "CollectFile",
                                "outputs": ["status"]
                                    }])
                print result_context

# Wait forever
print "Waiting for first instance events..."
while True:
    time.sleep(60)
