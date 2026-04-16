# ============================================================
#  WEEK 11 LAB — Q1: PORT SCANNER CLASS
#  COMP2152 — Karthik Madarapu
# ============================================================
#
#  You already know how to scan ports from Assignment 2.
#  Now you'll wrap that same logic inside a CLASS.
#  The scanning code doesn't change — just the organization.
#
# ============================================================

import socket
class SimpleScanner:
    def __init__(self, target):
        self.target = target
        self.open_ports = []





    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            if result == 0:
                print(f"    Port {port}: OPEN")
                self.open_ports.append(port)
                return True
            return False
        finally:
            sock.close()
    def scan_range(self, start_port, end_port):
        for port in range(start_port, end_port+1):
            self.scan_port(port)
    def display_results(self):
        print(f"    Results for {self.target}:")
        if not self.open_ports:
            print("  No open ports found.")
        else:
            for port in self.open_ports:
                print(f"  Port {port}")


# --- Main (provided) ---
if __name__ == "__main__":
    print("=" * 60)
    print("  Q1: PORT SCANNER CLASS")
    print("=" * 60)

    # Create first scanner object
    print("\n--- Scanner 1: localhost ---")
    scanner1 = SimpleScanner("127.0.0.1")
    print(f"  Scanning {scanner1.target} ports 78-82...")
    scanner1.scan_range(1, 20000)
    scanner1.display_results()

    # Create second scanner object — separate target, separate results
    print("\n--- Scanner 2: different target ---")
    scanner2 = SimpleScanner("127.0.0.1")
    print(f"  Scanning {scanner2.target} ports 20-25...")
    scanner2.scan_range(20000, 65000)
    scanner2.display_results()

    print("\n" + "=" * 60)
