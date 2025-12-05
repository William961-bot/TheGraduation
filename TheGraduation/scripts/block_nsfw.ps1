<#
    Block NSFW domains, enforce Google SafeSearch, and self-delete after execution.
    The script prompts for a password before making any changes. Update $ExpectedPasswordHash
    with the SHA-256 hash of your chosen password. The default hash corresponds to
    the password "ChangeMe123!"; change it before using the script.

    Usage (run PowerShell as Administrator):
        Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
        .\block_nsfw.ps1

    To generate a new SHA-256 hash in PowerShell:
        "YourPasswordHere" |
            ForEach-Object { [System.Text.Encoding]::UTF8.GetBytes($_) } |
            ForEach-Object { (New-Object System.Security.Cryptography.SHA256Managed).ComputeHash($_) } |
            ForEach-Object { $_ | ForEach-Object { $_.ToString("x2") } -join "" }
#>

param(
    [string]$HostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
)

function Get-PasswordHash {
    param([Parameter(Mandatory = $true)][string]$Text)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        $hashBytes = $sha256.ComputeHash($bytes)
        return ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
    } finally {
        $sha256.Dispose()
    }
}

function ConvertFrom-SecureStringToPlain {
    param([Parameter(Mandatory = $true)][System.Security.SecureString]$SecureText)
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureText)
    try {
        return [System.Runtime.InteropServices.Marshal]::PtrToStringUni($ptr)
    } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

function Ensure-HostsEntry {
    param(
        [Parameter(Mandatory = $true)][string]$IP,
        [Parameter(Mandatory = $true)][string]$Domain,
        [Parameter(Mandatory = $true)][string[]]$CurrentHosts,
        [Parameter(Mandatory = $true)][string]$HostsFile
    )

    $entry = "$IP`t$Domain"
    if ($CurrentHosts -notcontains $entry) {
        Add-Content -Path $HostsFile -Value $entry
    }
}

function Show-AircrackStyleMenu {
    param(
        [Parameter(Mandatory = $true)][string[]]$Domains
    )

    Write-Host ""  # spacing
    Write-Host "==================== Block List Menu ====================" -ForegroundColor Cyan
    Write-Host " [1] Add domain to block list"
    Write-Host " [2] View current block list"
    Write-Host " [3] Proceed with updates"
    Write-Host " [4] Cancel and exit"
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "Current total: $($Domains.Count) domains"
    return Read-Host "Select an option"
}

function Prompt-ForDomain {
    $newDomain = Read-Host "Enter a domain to block (leave blank to return to menu)"
    if ([string]::IsNullOrWhiteSpace($newDomain)) {
        return $null
    }

    $cleanDomain = $newDomain.Trim()
    if ($cleanDomain -match "\s") {
        Write-Warning "Domains cannot contain spaces."
        return $null
    }

    return $cleanDomain
}

$ExpectedPasswordHash = "9a4aabf0e5cf71cae2cea646613ce7e2a5919fa758e56819704be25a3a2c1f0b"  # SHA-256 for "ChangeMe123!"

$enteredSecure = Read-Host -AsSecureString -Prompt "Enter script password"
$enteredPlain = ConvertFrom-SecureStringToPlain -SecureText $enteredSecure
if (Get-PasswordHash -Text $enteredPlain -ne $ExpectedPasswordHash) {
    Write-Error "Incorrect password. No changes were made."
    exit 1
}

if (-not (Test-Path -LiteralPath $HostsPath)) {
    Write-Error "Hosts file not found at $HostsPath"
    exit 1
}

$nsfwDomains = @(
    "example1.com",
    "example2.com",
    "badsite.com"
)

while ($true) {
    $selection = Show-AircrackStyleMenu -Domains $nsfwDomains

    switch ($selection) {
        "1" {
            while ($true) {
                $entered = Prompt-ForDomain
                if (-not $entered) { break }

                if ($nsfwDomains -notcontains $entered) {
                    $nsfwDomains += $entered
                    Write-Host " [+] Added $entered" -ForegroundColor Yellow
                } else {
                    Write-Host " [=] $entered already present" -ForegroundColor Cyan
                }
            }
        }
        "2" {
            Write-Host "\nCurrent block list:" -ForegroundColor Green
            $nsfwDomains | Sort-Object | ForEach-Object { Write-Host "  - $_" }
        }
        "3" { break }
        "4" { Write-Host "Cancelled. No changes made." -ForegroundColor Red; exit 0 }
        default { Write-Warning "Unrecognized option. Choose 1-4." }
    }
}

$googleSafeSearchIPs = @("216.239.38.120", "216.239.38.119", "216.239.38.117", "216.239.38.118")
$googleDomains = @("www.google.com", "google.com", "www.google.co.uk", "www.google.ca")
$youtubeDomains = @("www.youtube.com", "youtube.com")

$hostsLines = Get-Content -Path $HostsPath -ErrorAction Stop

foreach ($domain in $nsfwDomains) {
    Ensure-HostsEntry -IP "127.0.0.1" -Domain $domain -CurrentHosts $hostsLines -HostsFile $HostsPath
}

$primarySafeIP = $googleSafeSearchIPs[0]
foreach ($domain in $googleDomains) {
    Ensure-HostsEntry -IP $primarySafeIP -Domain $domain -CurrentHosts $hostsLines -HostsFile $HostsPath
}
foreach ($domain in $youtubeDomains) {
    Ensure-HostsEntry -IP $primarySafeIP -Domain $domain -CurrentHosts $hostsLines -HostsFile $HostsPath
}

ipconfig /flushdns | Out-Null
Write-Host "Host entries updated and DNS cache flushed." -ForegroundColor Green

$scriptPath = $MyInvocation.MyCommand.Path
if ($scriptPath -and (Test-Path -LiteralPath $scriptPath)) {
    Start-Sleep -Seconds 1
    Remove-Item -LiteralPath $scriptPath -Force
}
