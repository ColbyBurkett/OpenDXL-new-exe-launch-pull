import os
import sys
import mcafee
import urlquote

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
mc = mcafee.client('10.10.0.10','8443','podadmin','MFEpoc92!','https','json')
ePOTag = 'Suspect'

# Create the client
with DxlClient(config) as client:

    # Read in hashes from file
    hashes = []
    hashesFile = open('bad-hashes.txt', 'r')
    for rowofdata in hashesFile:
        rowofdata = rowofdata.strip('\r\n')
        rowofdata = list(rowofdata.split(','))
        hashes.append(rowofdata[1])
    hashesFile.close()

    # Connect to the fabric
    client.connect()

    # Create the McAfee Active Response (MAR) client
    mar_client = MarClient(client)

    for hashitem in hashes:
        # Performs the search
        # Execute the search
        print "Searching for hash: "+hashitem
        result_context = mar_client.search(
                projections=[{
                        "name": "HostInfo",
                        "outputs": ["hostname"]
                            }],
                conditions={
                    "or": [{
                        "and": [{
                            "name": "Files",
                            "output": "sha1",
                            "op": "EQUALS",
                            "value": hashitem
                        }]
                    }]
                }
            )

        # Loop and display the results
        if result_context2.has_results:
            search_result = result_context.get_results(limit=10)
            print "Hash "+hashitem+" found on:"
            for item in search_result["items"]:
                print item["output"]['HostInfo|hostname']
                systems = mc.system.find(item["output"]['HostInfo|hostname'])
                for system in systems:
                    mc.system.applyTag(system['EPOComputerProperties.ComputerName'],ePOTag)
