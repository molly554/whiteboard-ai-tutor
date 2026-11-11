# Prompts for an API key with hidden input and stores it as a USER-level environment variable.
# The key is never printed and never written to any file.
# Usage: set_key.ps1 -Name DEEPSEEK_API_KEY     (default name: OPENROUTER_API_KEY)
param([string]$Name = 'OPENROUTER_API_KEY')
$sec = Read-Host -Prompt "Paste your $Name value (input is hidden), then press Enter" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try {
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
if ([string]::IsNullOrWhiteSpace($plain)) {
    Write-Host 'No key entered. Nothing was changed.'
    return
}
[Environment]::SetEnvironmentVariable($Name, $plain.Trim(), 'User')
$plain = $null
Write-Host "Saved $Name as a user environment variable (value not shown)."
