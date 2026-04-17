# ============================================================
#  WEEK 14 LAB — Q2: HTTP SECURITY HEADER CHECKER
#  COMP2152 — [Karthik Madarapu]
# ============================================================

import urllib.request


# Security headers every website should have
REQUIRED_HEADERS = {
    "Content-Type":              "Defines the content format",
    "X-Frame-Options":           "Vulnerable to clickjacking",
    "X-Content-Type-Options":    "Vulnerable to MIME sniffing",
    "Strict-Transport-Security": "No HTTPS enforcement",
    "Content-Security-Policy":   "No XSS protection policy",
    "X-XSS-Protection":          "No XSS filter",
}


# Check headers of a URL
def check_headers(url):
    try:
        with urllib.request.urlopen(url) as response:
            headers = dict(response.headers)

            # normalize keys (case-insensitive)
            normalized_headers = {k.lower(): v for k, v in headers.items()}

            results = []

            for header in REQUIRED_HEADERS:
                header_lower = header.lower()

                if header_lower in normalized_headers:
                    results.append({
                        "header": header,
                        "present": True,
                        "value": normalized_headers[header_lower]
                    })
                else:
                    results.append({
                        "header": header,
                        "present": False,
                        "value": "MISSING"
                    })

            return results

    except Exception:
        return []


# Generate report
def generate_report(url, results):
    print(f"  URL: {url}")
    missing_count = 0

    for result in results:
        header = result["header"]

        if result["present"]:
            print(f"  ✓ {header}: {result['value']}")
        else:
            print(f"  ✗ {header}: MISSING — {REQUIRED_HEADERS[header]}")
            missing_count += 1

    print(f"  Missing {missing_count} of {len(results)} security headers!")


# --- Main ---
if __name__ == "__main__":
    print("=" * 60)
    print("  Q2: HTTP SECURITY HEADER CHECKER")
    print("=" * 60)

    urls = [
        "http://httpbin.org",
        "https://www.google.com",
    ]

    for url in urls:
        print(f"\n--- Checking {url} ---")
        results = check_headers(url)
        if results:
            generate_report(url, results)
        else:
            print("  (could not connect or not implemented)")

    print("\n" + "=" * 60)