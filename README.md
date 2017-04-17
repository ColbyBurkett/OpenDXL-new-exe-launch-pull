# OpenDXL-new-exe-launch-pull

Requirements:
  * ePO v5.1.1+
  * DXL v3.0.1+
  * TIE v2.0.1+
  * MAR v2.0+
  * MA v5.0.5+

1) Setup Web Server of any kind. The output of the Python OpenDXL script will be placed here. I used a simple Python Web Serve for this
2) Place contents of CollectFile.ps1 in a MAR Collector (edit IP/FQDN of Web Server)
3) Run Python script and watch for new files to be executed. When a file executes, the OpenDXL callback listener will see the message and will then issue a MAR search for that file to gather more info about it. Once found, the Python script creates a stub file on the Web Server with the path & filename to retrieve. An MA Custom Property is then dynamically applied to let the system executing the collector know that there is a file on the Web Server to retrieve. The OpenDXL/Python script then executes that collector.
4) The collector initially executes on all nodes, but terminates quickly as the Custom Property is only set on the node(s) which have work to do. These nodes connect to the Web Server and retrieve the file that contains a path & file to copy to a central location. The file is copied.

Note: the central location should be a write-only UNC share.
