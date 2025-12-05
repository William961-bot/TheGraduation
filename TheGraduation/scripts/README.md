# Block NSFW Hosts (PowerShell)

`block_nsfw.ps1` updates the Windows `hosts` file to block NSFW domains and force Google SafeSearch. The script self-deletes after a successful run and requires a password before it makes any changes.

## Usage
1. **Set your password hash:**
   - The script uses a SHA-256 hash for verification. Replace the value of `$ExpectedPasswordHash` in `block_nsfw.ps1` with the hash of your desired password.
   - Example PowerShell snippet to generate a hash:
     ```powershell
     "YourPasswordHere" |
       ForEach-Object { [System.Text.Encoding]::UTF8.GetBytes($_) } |
       ForEach-Object { (New-Object System.Security.Cryptography.SHA256Managed).ComputeHash($_) } |
       ForEach-Object { $_ | ForEach-Object { $_.ToString("x2") } -join "" }
     ```
2. **Update domain lists:**
   - Populate `$nsfwDomains` with the sites you want blocked.
   - When running, you can use the Aircrack-style menu to press `1` to add additional domains or `2` to review the list before proceeding.
   - Add any regional Google domains to `$googleDomains` and adjust `$youtubeDomains` if needed.
3. **Run with Administrator privileges:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
   .\block_nsfw.ps1
   ```

The script will prompt for your password. On success, it shows the menu, updates the `hosts` file, flushes DNS, reports completion, and deletes itself.
