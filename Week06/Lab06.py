# ============================================================
#  WEEK 06 LAB: NETWORK DIAGNOSTIC LOGGER
#  COMP2152
#  Karthik Madarapu
# ============================================================

import subprocess
import csv
import platform
import re
from datetime import datetime

# ============================================================
#  SECTION A: Running System Commands
# ============================================================

def run_ping(host):
    """Run ping 3 times on a host and return the output (Windows/macOS compatible)."""
    is_windows = platform.system().lower().startswith("win")
    count_flag = "-n" if is_windows else "-c"
    result = subprocess.run(
        ["ping", count_flag, "3", host],
        capture_output=True, text=True
    )
    return result.stdout


def run_nslookup(domain):
    """Run nslookup on a domain and return the output."""
    result = subprocess.run(
        ["nslookup", domain],
        capture_output=True, text=True
    )
    return result.stdout


def get_network_info():
    """Return network interface info (Windows/macOS compatible)."""
    is_windows = platform.system().lower().startswith("win")
    cmd = ["ipconfig", "/all"] if is_windows else ["ifconfig"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def get_arp_table():
    """Run arp -a to show all devices on the local network."""
    result = subprocess.run(
        ["arp", "-a"],
        capture_output=True, text=True
    )
    return result.stdout


def get_hostname():
    """Run hostname to get the computer's network name."""
    result = subprocess.run(
        ["hostname"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


# ============================================================
#  SECTION B: Parsing Command Output
# ============================================================

def parse_ping(output):
    """Parse ping output and extract key statistics (best-effort cross-platform)."""
    lines = output.strip().split("\n")
    stats = {
        "transmitted": 0,
        "received": 0,
        "loss": "100%",
        "avg_ms": "N/A",
        "status": "Failed"
    }

    # Windows style
    for line in lines:
        if "Sent =" in line and "Received =" in line:
            parts = line.split(",")
            for part in parts:
                part = part.strip()
                if "Sent" in part:
                    stats["transmitted"] = int(part.split("=")[1].strip())
                if "Received" in part:
                    stats["received"] = int(part.split("=")[1].strip())
                if "%" in part and "loss" in part:
                    loss_text = part.strip().strip("(").strip(")")
                    stats["loss"] = loss_text.split("%")[0].strip() + "%"

        if "Average" in line:
            avg_part = line.split("=")[-1].strip()
            stats["avg_ms"] = avg_part.replace("ms", "").strip()

    # macOS/Linux style
    # Example: "3 packets transmitted, 3 packets received, 0.0% packet loss"
    # Example RTT: "round-trip min/avg/max/stddev = 10.123/12.456/..."
    for line in lines:
        if "packets transmitted" in line and "packet loss" in line:
            # extract numbers
            m = re.search(r"(\d+)\s+packets transmitted,\s+(\d+)\s+packets.*,\s+([\d\.]+)%\s+packet loss", line)
            if m:
                stats["transmitted"] = int(m.group(1))
                stats["received"] = int(m.group(2))
                stats["loss"] = m.group(3) + "%"

        if "min/avg" in line and "=" in line:
            # get avg from "min/avg/max/..." section
            right = line.split("=")[-1].strip()
            nums = right.split()[0]  # "10.1/12.4/..."
            parts = nums.split("/")
            if len(parts) >= 2:
                stats["avg_ms"] = parts[1].strip()

    if stats["received"] > 0:
        stats["status"] = "Success"

    return stats


def parse_nslookup(output):
    """Parse nslookup output and extract the resolved IP address."""
    lines = output.strip().split("\n")
    result = {"ip": "Not found", "status": "Failed"}

    found_answer = False
    for line in lines:
        if "Non-authoritative answer" in line:
            found_answer = True
        if found_answer and "Address:" in line:
            ip = line.split("Address:")[1].strip()
            if ip and "." in ip:
                result["ip"] = ip
                result["status"] = "Success"
                break

    # macOS sometimes prints "Address: 1.1.1.1" without the "Non-authoritative answer" marker
    if result["status"] == "Failed":
        for line in lines:
            if "Address:" in line:
                ip = line.split("Address:")[-1].strip()
                if ip and "." in ip:
                    result["ip"] = ip
                    result["status"] = "Success"
                    break

    return result


def parse_mac_address(output):
    """Parse network info output to extract MAC and IPv4 address (Windows/macOS compatible)."""
    lines = output.strip().split("\n")
    info = {"mac": "Not found", "ip": "Not found"}

    is_windows = platform.system().lower().startswith("win")

    if is_windows:
        for line in lines:
            line = line.strip()
            if "Physical Address" in line and ":" in line:
                mac = line.split(":")[1].strip()
                if mac and info["mac"] == "Not found":
                    info["mac"] = mac
            if "IPv4 Address" in line and ":" in line:
                ip = line.split(":")[-1].strip()
                ip = ip.replace("(Preferred)", "").strip()
                if ip and info["ip"] == "Not found":
                    info["ip"] = ip
    else:
        for line in lines:
            line = line.strip()
            if line.startswith("ether ") and info["mac"] == "Not found":
                info["mac"] = line.split()[1].strip()
            if line.startswith("inet ") and info["ip"] == "Not found":
                ip = line.split()[1].strip()
                if ip and ip != "127.0.0.1":
                    info["ip"] = ip

    return info


def parse_arp_table(output):
    """Parse arp output and return a list of devices (Windows/macOS compatible)."""
    lines = output.strip().split("\n")
    devices = []
    is_windows = platform.system().lower().startswith("win")

    if is_windows:
        for line in lines:
            line = line.strip()
            parts = line.split()
            if len(parts) >= 3:
                ip = parts[0]
                mac = parts[1]
                if "." in ip and ("-" in mac or ":" in mac):
                    if mac.lower() != "ff-ff-ff-ff-ff-ff":
                        devices.append({"ip": ip, "mac": mac})
    else:
        # macOS: "? (192.168.1.1) at aa:bb:cc:dd:ee:ff on en0 ..."
        pattern = re.compile(r"\((?P<ip>\d+\.\d+\.\d+\.\d+)\)\s+at\s+(?P<mac>[0-9a-fA-F:]{17})")
        for line in lines:
            m = pattern.search(line)
            if m:
                ip = m.group("ip")
                mac = m.group("mac")
                if mac.lower() != "ff:ff:ff:ff:ff:ff":
                    devices.append({"ip": ip, "mac": mac})

    return devices


# ============================================================
#  SECTION C: File I/O — Text Files
#  *** TASK 1 ***
# ============================================================

def write_to_log(filename, entry):
    """Append a log entry to a text file."""
    with open(filename, "a") as file:
        file.write(entry + "\n")


def read_log(filename):
    """Read and return the entire contents of a log file."""
    with open(filename, "r") as file:
        return file.read()


def log_command_result(command_name, target, output, filename):
    """Log a command result to a text file with timestamp and separator."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = "[" + timestamp + "] " + command_name + " " + target + "\n"
    entry = entry + output
    entry = entry + "-" * 40
    write_to_log(filename, entry)


# ============================================================
#  SECTION D: File I/O — CSV Files
#  *** TASK 2 ***
# ============================================================

LOG_FILE = "diagnostics.csv"


def log_to_csv(filename, command, target, result, status):
    """Append one row to the CSV log file with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, command, target, result, status])


def read_csv_log(filename):
    """Read and display all rows from the CSV log file."""
    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            print(" | ".join(row))


def analyze_csv_log(filename):
    """Read the CSV log and print a summary analysis."""
    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) == 0:
        print("Log is empty.")
        return

    total = len(rows)
    print("Total entries: " + str(total))

    command_counts = {}
    status_counts = {}

    for row in rows:
        command = row[1]
        status = row[4]

        if command in command_counts:
            command_counts[command] = command_counts[command] + 1
        else:
            command_counts[command] = 1

        if status in status_counts:
            status_counts[status] = status_counts[status] + 1
        else:
            status_counts[status] = 1

    print("\nCommands run:")
    for cmd in command_counts:
        print("  " + cmd + ": " + str(command_counts[cmd]) + " time(s)")

    print("\nResults:")
    for status in status_counts:
        print("  " + status + ": " + str(status_counts[status]))


# ============================================================
#  SECTION E: Exception Handling
#  *** TASK 3 ***
# ============================================================

def safe_ping(host):
    """Run ping with error handling for timeouts and failures."""
    try:
        flag = "-n" if platform.system().lower().startswith("win") else "-c"
        result = subprocess.run(
            ["ping", flag, "3", host],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return "Ping failed: Host unreachable or request timed out."
    except subprocess.TimeoutExpired:
        return "Ping failed: Command timed out after 10 seconds."
    except Exception as e:
        return "Ping failed: " + str(e)


def safe_nslookup(domain):
    """Run nslookup with error handling."""
    try:
        result = subprocess.run(
            ["nslookup", domain],
            capture_output=True, text=True, timeout=10
        )
        return parse_nslookup(result.stdout)
    except subprocess.TimeoutExpired:
        return {"ip": "Error: Timed out", "status": "Failed"}
    except Exception as e:
        return {"ip": "Error: " + str(e), "status": "Failed"}


def safe_read_log(filename):
    """Read a log file with error handling for missing files."""
    try:
        with open(filename, "r") as file:
            content = file.read()
            if content.strip() == "":
                print("Log file is empty.")
                return ""
            return content
    except FileNotFoundError:
        print("No log file found. Run a diagnostic first.")
        return ""
    finally:
        print("Log read attempt completed.")


def get_valid_input(prompt, valid_options):
    """Keep asking for input until the user enters a valid option."""
    while True:
        choice = input(prompt)
        if choice in valid_options:
            return choice
        else:
            print("Invalid input. Please enter one of: " + ", ".join(valid_options))


# ============================================================
#  SECTION F: The Integrated Program
# ============================================================

def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 34)
    print("   NETWORK DIAGNOSTIC LOGGER")
    print("=" * 34)
    print("1. Ping a host")
    print("2. DNS Lookup (nslookup)")
    print("3. Show Network Info (MAC/IP)")
    print("4. Show ARP Table (local devices)")
    print("5. View full log")
    print("6. Analyze log (summary)")
    print("7. Quit")
    print("=" * 34)


def do_ping():
    """Run a ping diagnostic and log the result."""
    host = input("Enter hostname to ping: ")
    print("Running ping on " + host + "...")

    output = safe_ping(host)
    ping_data = parse_ping(output)

    print("  Status:      " + ping_data["status"])
    print("  Packets:     " + str(ping_data["transmitted"]) + " sent, " + str(ping_data["received"]) + " received")
    print("  Packet Loss: " + ping_data["loss"])
    print("  Avg Latency: " + str(ping_data["avg_ms"]) + " ms")

    log_to_csv(LOG_FILE, "ping", host, ping_data["avg_ms"], ping_data["status"])
    log_command_result("PING", host, output, "network_log.txt")
    print("Result logged.")


def do_nslookup():
    """Run a DNS lookup and log the result."""
    domain = input("Enter domain to lookup: ")
    print("Running nslookup on " + domain + "...")

    dns_data = safe_nslookup(domain)

    print("  Status:  " + dns_data["status"])
    print("  Domain:  " + domain)
    print("  IP:      " + dns_data["ip"])

    log_to_csv(LOG_FILE, "nslookup", domain, dns_data["ip"], dns_data["status"])
    print("Result logged.")


def do_network_info():
    """Get and display network interface info, log to CSV."""
    print("Fetching network info...")
    hostname = get_hostname()

    try:
        output = get_network_info()
        net_data = parse_mac_address(output)

        print("  Hostname:    " + hostname)
        print("  MAC Address: " + net_data["mac"])
        print("  IP Address:  " + net_data["ip"])

        cmd_label = "ipconfig" if platform.system().lower().startswith("win") else "ifconfig"
        log_to_csv(LOG_FILE, cmd_label, "all", net_data["mac"] + " / " + net_data["ip"], "Captured")
        print("Result logged.")
    except Exception as e:
        print("  Error: " + str(e))
        cmd_label = "ipconfig" if platform.system().lower().startswith("win") else "ifconfig"
        log_to_csv(LOG_FILE, cmd_label, "all", "Error", "Failed")


def do_arp_table():
    """Show all devices on the local network."""
    print("Scanning local network (ARP table)...")

    try:
        output = get_arp_table()
        devices = parse_arp_table(output)

        if len(devices) == 0:
            print("  No devices found.")
        else:
            print("  Found " + str(len(devices)) + " device(s):\n")
            for device in devices:
                print("    IP: " + device["ip"] + "  |  MAC: " + device["mac"])

        log_to_csv(LOG_FILE, "arp", "local", str(len(devices)) + " devices", "Captured")
        print("\nResult logged.")
    except Exception as e:
        print("  Error: " + str(e))


def do_view_log():
    """Display the full CSV log."""
    print("\n=== FULL LOG ===")
    try:
        with open(LOG_FILE, "r", newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
            if len(rows) == 0:
                print("Log is empty.")
            else:
                for row in rows:
                    print(" | ".join(row))
    except FileNotFoundError:
        print("No log file found. Run a diagnostic first.")


def do_analyze():
    """Read the CSV log and show a summary analysis."""
    print("\n=== LOG ANALYSIS ===")
    try:
        analyze_csv_log(LOG_FILE)
    except FileNotFoundError:
        print("No log file found. Run some diagnostics first.")


def main():
    """Main program loop — the full Network Diagnostic Logger."""
    hostname = get_hostname()
    print("Welcome to the Network Diagnostic Logger!")
    print("Running on: " + hostname)

    while True:
        display_menu()
        choice = get_valid_input(
            "Enter your choice (1-7): ",
            ["1", "2", "3", "4", "5", "6", "7"]
        )

        if choice == "1":
            do_ping()
        elif choice == "2":
            do_nslookup()
        elif choice == "3":
            do_network_info()
        elif choice == "4":
            do_arp_table()
        elif choice == "5":
            do_view_log()
        elif choice == "6":
            do_analyze()
        elif choice == "7":
            print("Goodbye! Your log is saved in " + LOG_FILE)
            break


# Run the program
main()