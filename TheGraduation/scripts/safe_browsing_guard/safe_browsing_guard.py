import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

DEFAULT_DOMAINS = [
    "example.com",
    "badsite.com",
]

SAFESEARCH_IP = "216.239.38.120"
SAFESEARCH_DOMAINS = [
    "google.com",
    "www.google.com",
    "www.google.co.uk",
    "www.google.ca",
    "youtube.com",
    "www.youtube.com",
]

BEGIN_MARKER = "# >>> SafeBrowsingGuard begin"
END_MARKER = "# <<< SafeBrowsingGuard end"
CONFIG_FILE = "sbg_config.json"
BACKUP_FILE = "hosts.backup"


def hosts_path() -> Path:
    system = platform.system().lower()
    if system.startswith("win"):
        return Path(os.environ.get("SystemRoot", r"C:\\Windows")) / "System32/drivers/etc/hosts"
    return Path("/etc/hosts")


def load_config(config_dir: Path) -> list[str]:
    path = config_dir / CONFIG_FILE
    if not path.exists():
        return DEFAULT_DOMAINS.copy()
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [str(item) for item in data]
    except Exception:
        pass
    return DEFAULT_DOMAINS.copy()


def save_config(config_dir: Path, domains: list[str]) -> None:
    path = config_dir / CONFIG_FILE
    with path.open("w", encoding="utf-8") as f:
        json.dump(sorted(set(domains)), f, indent=2)


def ensure_backup(hosts: Path, backup: Path) -> None:
    if not backup.exists():
        shutil.copy2(hosts, backup)


def strip_managed_block(lines: list[str]) -> list[str]:
    cleaned = []
    skipping = False
    for line in lines:
        if line.strip() == BEGIN_MARKER:
            skipping = True
            continue
        if line.strip() == END_MARKER:
            skipping = False
            continue
        if not skipping:
            cleaned.append(line)
    return cleaned


def render_block(domains: list[str]) -> list[str]:
    block = [BEGIN_MARKER]
    block.append(f"# SafeSearch mappings -> {SAFESEARCH_IP}")
    for d in SAFESEARCH_DOMAINS:
        block.append(f"{SAFESEARCH_IP}\t{d}")
    if domains:
        block.append("# Custom blocked domains -> 127.0.0.1")
        for d in sorted(set(domains)):
            block.append(f"127.0.0.1\t{d}")
    block.append(END_MARKER)
    return [line + "\n" for line in block]


def apply_changes(config_dir: Path, domains: list[str]) -> None:
    hosts = hosts_path()
    backup = config_dir / BACKUP_FILE
    ensure_backup(hosts, backup)

    with hosts.open("r", encoding="utf-8") as f:
        original_lines = f.readlines()

    unmanaged = strip_managed_block(original_lines)
    managed = render_block(domains)

    with hosts.open("w", encoding="utf-8") as f:
        f.writelines(unmanaged)
        if unmanaged and not unmanaged[-1].endswith("\n"):
            f.write("\n")
        f.writelines(managed)

    flush_dns()
    print("Changes applied. Managed block written between markers. Backup at:", backup)


def restore_backup(config_dir: Path) -> None:
    backup = config_dir / BACKUP_FILE
    hosts = hosts_path()
    if not backup.exists():
        print("No backup found.")
        return
    shutil.copy2(backup, hosts)
    flush_dns()
    print("Backup restored. DNS cache refreshed where supported.")


def flush_dns() -> None:
    system = platform.system().lower()
    if system.startswith("win"):
        try:
            subprocess.run(["ipconfig", "/flushdns"], check=True, capture_output=True)
            print("DNS cache flushed (Windows).")
        except Exception as exc:
            print(f"Unable to flush DNS automatically: {exc}")
    else:
        print("Reminder: flush DNS manually if needed (e.g., 'sudo killall -HUP mDNSResponder' on macOS or 'sudo systemd-resolve --flush-caches' on systemd-resolved).")


def prompt_domain(prompt: str) -> str:
    value = input(prompt).strip().lower()
    return value


def menu_loop(config_dir: Path) -> None:
    domains = load_config(config_dir)
    actions = {
        "1": "Add a domain",
        "2": "Remove a domain",
        "3": "List configured domains",
        "4": "Apply changes (update hosts)",
        "5": "Restore hosts backup",
        "0": "Quit",
    }

    while True:
        print("\n=== Safe Browsing Guard ===")
        for key in sorted(actions):
            print(f"[{key}] {actions[key]}")
        choice = input("Select an option: ").strip()

        if choice == "1":
            domain = prompt_domain("Enter domain to block (e.g., badsite.com): ")
            if domain:
                domains.append(domain)
                save_config(config_dir, domains)
                print(f"Added {domain}.")
            else:
                print("No domain entered.")
        elif choice == "2":
            domain = prompt_domain("Enter domain to remove: ")
            if domain in domains:
                domains = [d for d in domains if d != domain]
                save_config(config_dir, domains)
                print(f"Removed {domain}.")
            else:
                print("Domain not found.")
        elif choice == "3":
            unique = sorted(set(domains))
            if not unique:
                print("No domains configured.")
            else:
                print("Configured domains:")
                for d in unique:
                    print(" -", d)
        elif choice == "4":
            apply_changes(config_dir, domains)
        elif choice == "5":
            restore_backup(config_dir)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please choose again.")


def main():
    config_dir = Path(__file__).resolve().parent
    menu_loop(config_dir)


if __name__ == "__main__":
    main()
