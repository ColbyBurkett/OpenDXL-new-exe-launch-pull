$output = & "C:\Program Files\McAfee\Agent\cmdagent" -i
$line = $output[3] -replace '^\s+','' -split '\s+'
$MAGuid = $line[1]
$line = $output[16] -replace '^\s+','' -split '\s+'
$PullRequest = $line[1]

if ($PullRequest -eq "N") {
	$url = "http://127.0.0.1:8000/" + $MAGuid
	$output = "fileToPull"
	$start_time = Get-Date

	Invoke-WebRequest -Uri $url -OutFile $output
	Write-Output "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"
	
	$filePull = Get-Content fileToPull
}

# Reset the Custom Property to disable polling the Web Server when collector is executed
& "C:\Program Files\McAfee\Agent\maconfig" -custom -prop1 "N"

# Set the destination naming scheme.
$fileDest = $MAGuid + ".pulled"

# Copy file to new location
# Recommand a write-only UNC file share
Copy-Item -Path $filePull -Destination $fileDest

# Clean up after operation
Remove-Item fileToPull