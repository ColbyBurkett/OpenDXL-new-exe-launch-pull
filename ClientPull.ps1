# Pull McAfee Agent GUID, and Custom Property #1 from MA
# Custom Property #1 is set to "Y" when the host is requested to check Web Server
# for files to pull
$output = & "C:\Program Files\McAfee\Agent\cmdagent" -i
$line = $output[3] -replace '^\s+','' -split '\s+'
$MAGuid = $line[1]
$line = $output[16] -replace '^\s+','' -split '\s+'
$PullRequest = $line[1]

# Check Web Server for file with same name as Agent GUID
# This file will contain a single line of file to be copied to new location
# Recommend http server that can scale well and is available to all Corporate hosts
# Testing can be done with Python

# Change "http://127.0.0.1:8000/" to your preferred host
if ($PullRequest -eq "Y") {
	$url = "http://127.0.0.1:8000/" + $MAGuid
	$output = "C:\Users\Administrator\Desktop\"+"fileToPull"
	$start_time = Get-Date

	Invoke-WebRequest -Uri $url -OutFile $output
	Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"
	
	$filePull = Get-Content $output
}

# Reset the Custom Property to disable polling the Web Server when collector is executed
& "C:\Program Files\McAfee\Agent\maconfig" -custom -prop1 "N"

# Set the destination naming scheme.
$fileDest = "C:\Users\Administrator\Desktop\"+ $MAGuid + ".pulled"

# Copy file to new location
# Recommand a write-only UNC file share
Copy-Item -Path $filePull -Destination $fileDest

# Clean up after operation
Remove-Item $output

# Give some output to satisfy MAR
Write-Host "Done"