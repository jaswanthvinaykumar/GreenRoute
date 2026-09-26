"""
GreenRoute Realistic Production Server Log Generator
Simulates realistic web traffic with healthchecks, cascading outages, PII, and bot traffic.
"""

import random
import datetime
from typing import List


ENDPOINTS = [
    # Normal user routes
    ("/api/v1/auth/login", "POST", 200, 1420),
    ("/api/v1/products/search", "GET", 200, 4820),
    ("/api/v1/cart/items", "POST", 201, 850),
    ("/api/v1/checkout/process", "POST", 200, 2190),
    ("/dashboard/overview", "GET", 200, 18500),
    ("/assets/bundle.min.js", "GET", 200, 124500),
    ("/assets/theme.css", "GET", 200, 34200),
    # Common 404 scans
    ("/wp-login.php", "GET", 404, 210),
    ("/.env", "GET", 404, 180),
    ("/api/v1/user/legacy", "GET", 404, 340),
]

HEALTHCHECK_ENDPOINTS = [
    ("/healthz", "GET", 200, 45),
    ("/readyz", "GET", 200, 32),
    ("/actuator/health", "GET", 200, 68),
    ("/ping", "GET", 200, 22),
]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "curl/8.4.0",
]

HEALTHCHECK_UAS = [
    "kube-probe/1.28+",
    "ELB-HealthChecker/2.0",
    "Consul-Agent-Health/1.16",
    "Amazon-Route53-Health-Check-Service",
]

IPS = [
    "192.168.1.45", "10.0.2.14", "172.16.50.88", "198.51.100.23",
    "203.0.113.195", "185.220.101.5", "142.250.190.46"
]


def generate_sample_logs(num_lines: int = 5000, error_cascade_size: int = 500) -> str:
    """
    Generate realistic multi-megabyte log simulation.
    ~45% health checks, ~10% cascading 500 errors, ~35% normal traffic, ~10% PII/tokens.
    """
    lines: List[str] = []
    base_time = datetime.datetime.now() - datetime.timedelta(hours=2)

    for i in range(num_lines):
        curr_time = base_time + datetime.timedelta(seconds=int(i * 1.4))
        time_str = curr_time.strftime("%d/%b/%Y:%H:%M:%S +0000")

        # 1. Simulate Cascading Failure burst
        if 1200 <= i < (1200 + error_cascade_size):
            ip = "10.0.4.15"
            line = (
                f'{ip} - - [{time_str}] "POST /api/v1/payments/charge HTTP/1.1" 500 482 '
                f'"https://app.greenroute.io/checkout" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0" '
                f'[ERROR] database connection pool exhausted: timeout 5000ms acquire connection'
            )
            lines.append(line)
            continue

        # 2. Simulate high-frequency healthchecks (40% probability)
        roll = random.random()
        if roll < 0.42:
            endpoint, method, status, size = random.choice(HEALTHCHECK_ENDPOINTS)
            ua = random.choice(HEALTHCHECK_UAS)
            ip = "127.0.0.1" if random.random() < 0.5 else "10.0.0.1"
            line = f'{ip} - - [{time_str}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "{ua}"'
            lines.append(line)
            continue

        # 3. Simulate normal user traffic
        endpoint, method, status, size = random.choice(ENDPOINTS)
        ip = random.choice(IPS)
        ua = random.choice(USER_AGENTS)

        # Occasionally inject PII or auth tokens
        extra_pii = ""
        if random.random() < 0.15:
            user_id = random.randint(1000, 9999)
            extra_pii = f' ?email=user_{user_id}@cloudcorp.io&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'

        line = f'{ip} - user_{random.randint(100, 999)} [{time_str}] "{method} {endpoint}{extra_pii} HTTP/1.1" {status} {size} "https://company.internal/dashboard" "{ua}"'
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    sample = generate_sample_logs(1000)
    print(f"Generated sample: {len(sample.splitlines())} lines, {len(sample.encode('utf-8'))} bytes")
