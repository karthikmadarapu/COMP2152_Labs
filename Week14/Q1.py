# ============================================================
#  WEEK 14 LAB — Q1: API EXPLORER
#  COMP2152 — [Karthik Madarapu]
# ============================================================

import urllib.request
import json


# Make HTTP request
def make_request(url):
    try:
        with urllib.request.urlopen(url) as response:
            body = response.read().decode()
            return {
                "status": response.status,
                "headers": dict(response.headers),
                "body": body
            }
    except Exception as e:
        return {
            "status": 0,
            "headers": {},
            "body": "",
            "error": str(e)
        }



def parse_json(body):
    try:
        return json.loads(body)
    except ValueError:
        return None


def check_api_info(response):
    findings = []
    headers = response.get("headers", {})

    # Normalize keys (case-insensitive handling)
    normalized_headers = {k.lower(): v for k, v in headers.items()}

    if "server" in normalized_headers:
        findings.append(f"Server version exposed: {normalized_headers['server']}")

    if "x-powered-by" in normalized_headers:
        findings.append(f"Technology exposed: {normalized_headers['x-powered-by']}")

    if normalized_headers.get("access-control-allow-origin") == "*":
        findings.append("CORS: open to all origins")

    return findings

# --- Main (provided) ---
if __name__ == "__main__":
    print("=" * 60)
    print("  Q1: API EXPLORER")
    print("=" * 60)

    url = "http://httpbin.org/headers"
    print(f"\n--- Requesting {url} ---")

    resp = make_request(url)

    if resp and resp.get("status"):
        print(f"  Status: {resp['status']}")

        print("\n--- Response Headers ---")
        for key, val in resp["headers"].items():
            print(f"  {key:<16}: {val}")

        print("\n--- Parsed JSON Body ---")
        data = parse_json(resp["body"])
        if data:
            for key, val in data.items():
                print(f"  {key}: {val}")
        else:
            print("  (not JSON or parse failed)")

        print("\n--- Security Findings ---")
        findings = check_api_info(resp)
        if findings:
            for f in findings:
                print(f"  {f}")
        else:
            print("  (no issues found)")
    else:
        error = resp.get("error", "unknown") if resp else "make_request returned None"
        print(f"  Error: {error}")

    print("\n" + "=" * 60)