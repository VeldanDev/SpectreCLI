#!/usr/bin/env python3
# spectra_cli.py
# Lightweight CLI-only SPECTRE for Raspberry Pi Zero 2 W
# Preserves biometric flow (face + gesture) and audit/history logging.
# Tools inspired by GhostTR (ipwho.is, phonenumbers, simple username checks)
# Credit: Spectre Framework — Developed by: VeldanDev

import os
import sys
import json
import socket
import time
from datetime import datetime
from getpass import getpass

# Biometric modules (MUST NOT be changed)
from face_register import register_face
from face_auth import authenticate_face
from gesture_auth import authenticate_gesture

# Optional modules (graceful fallback)
try:
    import requests
except Exception:
    requests = None

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone as pn_timezone, NumberParseException
except Exception:
    phonenumbers = None

try:
    import dns.resolver  # type: ignore
    import dns.rdatatype  # type: ignore
except Exception:
    dns = None

try:
    import whois  # type: ignore
except Exception:
    whois = None

# Color
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except Exception:
    # Fallback no color
    class _C:
        def __getattr__(self, name):
            return ""
    Fore = Style = _C()

# Files
HISTORY_FILE = "history.json"
AUDIT_FILE = "audit.json"
OWNER_FACE = "owner_face.pkl"

# Network timeouts (short for Pi)
REQ_TIMEOUT = 4
SHORT_TIMEOUT = 3

# Utility functions
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def save_audit_log(feature, data):
    try:
        if os.path.exists(AUDIT_FILE):
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = {}
    except Exception:
        logs = {}

    logs.setdefault(feature, [])
    entry = dict(data) if isinstance(data, dict) else {"value": data}
    entry["time"] = now_str()
    logs[feature].append(entry)
    try:
        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def save_history(item_type, target, result):
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = []
    except Exception:
        history = []

    entry = {
        "time": now_str(),
        "type": item_type,
        "target": target,
        "result": result
    }
    history.append(entry)
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def read_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def last_scan():
    h = read_history()
    if not h:
        return None
    return h[-1]

def safe_get_json(url, timeout=REQ_TIMEOUT):
    if not requests:
        return None
    try:
        with requests.Session() as s:
            r = s.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.json()
    except Exception:
        return None
    return None

# Banner
BANNER = (
    "███████╗██████╗ ███████╗ ██████╗████████╗██████╗ ███████╗\n"
    "██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔════╝\n"
    "███████╗██████╔╝█████╗  ██║        ██║   ██████╔╝█████╗\n"
    "╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══██╗██╔══╝\n"
    "███████║██║     ███████╗╚██████╗   ██║   ██║  ██║███████╗\n"
    "╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝\n"
)

CREDIT_LINE = "Spectre Framework — Developed by: VeldanDev"

# IP Tracker (Ghost style, optimized)
def ip_tracker():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "IP Tracker (ipwho.is, offline fallback)\n")
    q = input("Enter IP or domain: ").strip()
    if not q:
        print(Fore.RED + "Empty input. Returning to menu.")
        input("\nPress Enter to continue...")
        return

    # local resolve
    try:
        resolved = socket.gethostbyname(q)
    except Exception:
        resolved = "N/A"

    print(f"\nResolved IP: {resolved}")

    data = None
    if requests:
        url = f"https://ipwho.is/{q}"
        data = safe_get_json(url, timeout=REQ_TIMEOUT)

    if not data:
        print(Fore.YELLOW + "Remote lookup unavailable or failed. Showing local info only.\n")
        save_history("ip", q, {"resolved": resolved, "note": "local_only"})
        save_audit_log("IP Tracker", {"query": q, "resolved": resolved, "status": "local_only"})
        input("\nPress Enter to continue...")
        return

    # Display required fields compactly
    ip = data.get("ip", "N/A")
    _type = data.get("type", "N/A")
    country = data.get("country", "N/A")
    city = data.get("city", "N/A")
    region = data.get("region", "N/A")
    lat = data.get("latitude", None)
    lon = data.get("longitude", None)
    connection = data.get("connection", {}) or {}
    asn = connection.get("asn", "N/A")
    isp = connection.get("isp", "N/A")
    timezone = data.get("timezone", {}) or {}
    tz_id = timezone.get("id", "N/A")
    tz_utc = timezone.get("utc", "")
    current_time = timezone.get("current_time", "N/A")

    print(Fore.CYAN + f"\nIP            : " + Fore.GREEN + str(ip))
    print(Fore.CYAN + f"Type          : " + Fore.GREEN + str(_type))
    print(Fore.CYAN + f"Country       : " + Fore.GREEN + str(country))
    print(Fore.CYAN + f"City          : " + Fore.GREEN + str(city))
    print(Fore.CYAN + f"Region        : " + Fore.GREEN + str(region))
    print(Fore.CYAN + f"Latitude/Long : " + Fore.GREEN + f"{lat} / {lon}")
    if lat and lon:
        print(Fore.CYAN + f"Google Maps   : " + Fore.MAGENTA + f"https://www.google.com/maps/search/?api=1&query={lat},{lon}")
    print(Fore.CYAN + f"ASN           : " + Fore.GREEN + str(asn))
    print(Fore.CYAN + f"ISP           : " + Fore.GREEN + str(isp))
    print(Fore.CYAN + f"Timezone      : " + Fore.GREEN + f"{tz_id} {tz_utc}")
    print(Fore.CYAN + f"Current Time  : " + Fore.GREEN + str(current_time))

    # Save
    save_history("ip", q, data)
    save_audit_log("IP Tracker", {"query": q, "ip": ip})
    input("\nPress Enter to continue...")

# Show My IP
def show_my_ip():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "Show My IP\n")
    local_ip = "N/A"
    public_ip = "N/A"
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = "N/A"

    if requests:
        try:
            r = requests.get("https://api.ipify.org", timeout=SHORT_TIMEOUT)
            if r.status_code == 200:
                public_ip = r.text.strip()
        except Exception:
            public_ip = "N/A"

    print(Fore.CYAN + f"Local IP : " + Fore.GREEN + str(local_ip))
    print(Fore.CYAN + f"Public IP: " + (Fore.GREEN + str(public_ip) if public_ip and public_ip != "N/A" else Fore.RED + "Unavailable"))

    save_history("show_my_ip", local_ip or public_ip, {"local_ip": local_ip, "public_ip": public_ip})
    save_audit_log("Show My IP", {"local_ip": local_ip, "public_ip": public_ip})
    input("\nPress Enter to continue...")

# Phone Analyzer
def phone_analyzer():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "Phone Analyzer\n")
    if not phonenumbers:
        print(Fore.RED + "phonenumbers module not installed. Install with: pip install phonenumbers")
        input("\nPress Enter to continue...")
        return

    raw = input("Enter phone number (include +countrycode recommended): ").strip()
    if not raw:
        print(Fore.RED + "Empty input.")
        input("\nPress Enter to continue...")
        return

    try:
        num = phonenumbers.parse(raw, None)
    except Exception as e:
        print(Fore.RED + f"Parse error: {e}")
        input("\nPress Enter to continue...")
        return

    loc = geocoder.description_for_number(num, "en") or "N/A"
    prov = carrier.name_for_number(num, "en") or "N/A"
    tzs = pn_timezone.time_zones_for_number(num) or []
    valid = phonenumbers.is_valid_number(num)
    possible = phonenumbers.is_possible_number(num)
    international = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    number_type = phonenumbers.number_type(num)

    print(Fore.CYAN + f"\nLocation     : " + Fore.GREEN + str(loc))
    print(Fore.CYAN + f"Provider     : " + Fore.GREEN + str(prov))
    print(Fore.CYAN + f"Timezone     : " + Fore.GREEN + (", ".join(tzs) if tzs else "N/A"))
    print(Fore.CYAN + f"Valid        : " + (Fore.GREEN + "Yes" if valid else Fore.RED + "No"))
    print(Fore.CYAN + f"Possible     : " + (Fore.GREEN + "Yes" if possible else Fore.RED + "No"))
    print(Fore.CYAN + f"International: " + Fore.GREEN + str(international))
    print(Fore.CYAN + f"Type         : " + Fore.GREEN + str(number_type))

    save_history("phone", raw, {
        "intl": international, "valid": valid, "possible": possible, "provider": prov, "location": loc
    })
    save_audit_log("Phone Tracker", {"input": raw, "intl": international, "valid": valid})
    input("\nPress Enter to continue...")

# Username Lookup
PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}",
    "Facebook": "https://www.facebook.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Medium": "https://medium.com/@{}",
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "Pypi": "https://pypi.org/user/{}",
    "StackOverflow": "https://stackoverflow.com/users/{}"
}

def username_lookup():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "Username Lookup\n")
    if not requests:
        print(Fore.RED + "requests module not installed. Install with: pip install requests")
        input("\nPress Enter to continue...")
        return

    username = input("Enter username: ").strip()
    if not username:
        print(Fore.RED + "Empty input.")
        input("\nPress Enter to continue...")
        return

    session = requests.Session()
    results = {}
    for name, fmt in PLATFORMS.items():
        url = fmt.format(username)
        try:
            r = session.get(url, timeout=SHORT_TIMEOUT, allow_redirects=True)
            found = (r.status_code < 400 and "not found" not in r.text.lower())
            results[name] = (found, url)
        except Exception:
            results[name] = (None, url)

    # Display with colors
    for name, (status, url) in results.items():
        if status is True:
            print(Fore.GREEN + f"[FOUND] {name:12}: " + Fore.CYAN + url)
        elif status is False:
            print(Fore.RED + f"[MISS ] {name:12}: " + Fore.LIGHTBLACK_EX + url)
        else:
            print(Fore.YELLOW + f"[SKIP ] {name:12}: " + Fore.LIGHTBLACK_EX + url + " (timeout/error)")

    found_list = [n for n, (s, _) in results.items() if s is True]
    save_history("username", username, {"found": found_list})
    save_audit_log("Username Lookup", {"username": username, "found": found_list})
    input("\nPress Enter to continue...")

# Metadata Viewer (last scan)
def metadata_viewer():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "Metadata Viewer (last scan)\n")
    last = last_scan()
    if not last:
        print(Fore.RED + "No scan history available.")
        input("\nPress Enter to continue...")
        return
    print(json.dumps(last, indent=2, ensure_ascii=False))
    input("\nPress Enter to continue...")

# History Viewer
def history_viewer():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "History Viewer\n")
    history = read_history()
    if not history:
        print(Fore.RED + "No history entries.")
        input("\nPress Enter to continue...")
        return
    # show last 200 or all if fewer
    to_show = history[-200:]
    for i, h in enumerate(reversed(to_show), 1):
        t = h.get("time", "")
        typ = h.get("type", "")
        tgt = h.get("target", "")
        print(Fore.CYAN + f"{i:3}. " + Fore.GREEN + f"{t} | {typ} | {tgt}")
    input("\nPress Enter to continue...")

# Export History
def export_history():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "Export History\n")
    history = read_history()
    if not history:
        print(Fore.RED + "No history to export.")
        input("\nPress Enter to continue...")
        return
    fname = input("Enter export filename (example: /home/pi/export.json or export.txt): ").strip()
    if not fname:
        print(Fore.RED + "Cancelled.")
        input("\nPress Enter to continue...")
        return
    try:
        if fname.lower().endswith(".txt"):
            with open(fname, "w", encoding="utf-8") as f:
                for h in history:
                    f.write(f"{h.get('time','')} | {h.get('type','')} | {h.get('target','')} | {json.dumps(h.get('result',{}), ensure_ascii=False)}\n")
        else:
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        print(Fore.GREEN + f"Exported to {fname}")
        save_audit_log("Export History", {"file": fname})
    except Exception as e:
        print(Fore.RED + f"Export failed: {e}")
    input("\nPress Enter to continue...")

# Main menu
def main_menu():
    while True:
        clear()
        print(Fore.BLUE + BANNER + Style.RESET_ALL)
        print(Fore.GREEN + CREDIT_LINE + "\n")
        print(Fore.CYAN + "@Spectra~~#\n")
        print("1. IP Tracker")
        print("2. Show My IP")
        print("3. Phone Analyzer")
        print("4. Username Lookup")
        print("5. Metadata Viewer")
        print("6. History Viewer")
        print("7. Export History")
        print("0. Exit")
        choice = input("\nSelect option: ").strip()
        if choice == "1":
            ip_tracker()
        elif choice == "2":
            show_my_ip()
        elif choice == "3":
            phone_analyzer()
        elif choice == "4":
            username_lookup()
        elif choice == "5":
            metadata_viewer()
        elif choice == "6":
            history_viewer()
        elif choice == "7":
            export_history()
        elif choice == "0":
            print(Fore.YELLOW + "\nExiting SPECTRE...")
            time.sleep(0.3)
            break
        else:
            print(Fore.RED + "Invalid choice.")
            time.sleep(0.6)

# Entry flow with biometric sequence (MUST keep)
def run_cli():
    clear()
    print(Fore.BLUE + BANNER + Style.RESET_ALL)
    print(Fore.GREEN + "Starting secure boot sequence...\n")
    # 1. Register face if missing
    if not os.path.exists(OWNER_FACE):
        try:
            print(Fore.CYAN + "No owner_face found. Starting face registration...")
            register_face()
        except Exception as e:
            print(Fore.RED + f"Face registration failed: {e}")
            # proceed no further if registration fails irrecoverably
            input("\nPress Enter to exit...")
            sys.exit(1)

    # 2. Face authentication
    try:
        authenticate_face()
    except Exception as e:
        print(Fore.RED + "Face authentication failed or aborted.")
        sys.exit(1)

    # 3. Gesture authentication
    try:
        authenticate_gesture()
    except Exception as e:
        print(Fore.RED + "Gesture authentication failed or aborted.")
        sys.exit(1)

    # 4. Access granted
    clear()
    print(Fore.GREEN + "ACCESS GRANTED. Welcome, Operator.\n")
    time.sleep(0.4)
    main_menu()

if __name__ == "__main__":
    run_cli()