param (
    [string]$name = "Davidson",
    [string]$ip = ""
)

Write-Output "Hello $name"
if ($ip -ne "") {
    ping $ip
}
Write-Output "Script finished"
