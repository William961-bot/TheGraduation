# Safe Browsing Guard

This standalone, menu-driven Python tool enforces Google SafeSearch mappings and blocks custom domains by updating the system `hosts` file. It backs up the existing file before making changes so you can restore quickly if needed.

## Features
- Aircrack-style numeric menu for add/remove/list/apply/restore actions
- Persists your domain list to `sbg_config.json` in the same folder
- Adds Google SafeSearch mappings (and optional YouTube restriction) alongside your custom blocks
- Backs up your current `hosts` file before writing a managed block

## Requirements
- Python 3.8+
- Administrator privileges (needed to modify `hosts`)

## Usage
1. Open an elevated terminal (PowerShell as Administrator on Windows; `sudo` on macOS/Linux).
2. Run the tool from this folder:
   ```bash
   python safe_browsing_guard.py
   ```
3. Choose from the menu:
   - `1` — Add a domain to block
   - `2` — Remove a domain
   - `3` — List configured domains
   - `4` — Apply changes (writes SafeSearch mappings + blocks into `hosts` and flushes DNS on Windows)
   - `5` — Restore the last `hosts` backup (if present)
   - `0` — Quit

### Notes
- Backups are stored next to the script as `hosts.backup`.
- Entries written by this tool are wrapped between marker comments so they can be reapplied cleanly.
- On Windows, the tool attempts to flush DNS automatically; on other platforms it prints a reminder.
- If you use DNS-over-HTTPS or a VPN that bypasses `hosts`, these changes may not take effect.
