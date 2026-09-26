"""
GreenRoute Server Log Analyzer
Extracts telemetry, endpoint distributions, HTTP status breakdowns, and noise diagnostics.
"""

import re
from typing import Dict, Any, List
from collections import Counter, defaultdict


# Common Web Log Regex (Nginx, Apache Combined & Common Log Format, Caddy, CloudFront)
COMBINED_LOG_REGEX = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<path>[^\s?]+)(?:\?(?P<query>[^\s"]*))?\s*(?P<proto>[^"]+)?"\s+(?P<status>\d{3})\s+(?P<size>\S+)(?:\s+"(?P<referrer>[^"]*)"\s+"(?P<user_agent>[^"]*)")?'
)

# JSON Log detection
JSON_HTTP_METHOD_REGEX = re.compile(r'"method"\s*:\s*"([A-Z]+)"', re.IGNORECASE)
JSON_STATUS_REGEX = re.compile(r'"status(?:_code)?"\s*:\s*(\d{3})', re.IGNORECASE)
JSON_PATH_REGEX = re.compile(r'"(?:path|url|uri|endpoint)"\s*:\s*"([^"\s?]+)', re.IGNORECASE)


class LogAnalyzer:
    @staticmethod
    def analyze(log_content: str) -> Dict[str, Any]:
        """
        Analyze log lines for HTTP status codes, endpoints, traffic types, and anomalies.
        """
        lines = log_content.splitlines()
        total_lines = len(lines)

        status_counts = Counter()
        method_counts = Counter()
        endpoint_counts = Counter()
        ip_counts = Counter()
        bot_counts = Counter()
        time_buckets = Counter()  # minute/hour buckets
        error_lines: List[str] = []

        healthcheck_line_count = 0
        static_asset_count = 0

        for line in lines:
            if not line.strip():
                continue

            # Try Apache/Nginx Combined Format first
            match = COMBINED_LOG_REGEX.match(line)
            if match:
                data = match.groupdict()
                status = int(data["status"])
                method = data["method"]
                path = data["path"]
                ip = data["ip"]
                ua = data["user_agent"] or ""

                status_counts[status] += 1
                method_counts[method] += 1
                endpoint_counts[path] += 1
                ip_counts[ip] += 1

                # Extract hour bucket from time e.g. 26/Sep/2026:14:23:45
                time_str = data.get("time", "")
                if ":" in time_str:
                    parts = time_str.split(":")
                    if len(parts) >= 2:
                        time_buckets[f"{parts[0][-2:]}:{parts[1]}"] += 1

                # Bot detection
                if any(b in ua.lower() for b in ["bot", "spider", "crawl", "slurp"]):
                    bot_counts[ua.split()[0] if ua else "Bot"] += 1

                if any(h in path.lower() for h in ["health", "ready", "live", "ping", "status", "metrics"]):
                    healthcheck_line_count += 1

                if any(path.endswith(ext) for ext in [".css", ".js", ".png", ".jpg", ".svg", ".ico", ".woff2"]):
                    static_asset_count += 1

                if status >= 500 and len(error_lines) < 20:
                    error_lines.append(f"{method} {path} -> {status}")
            else:
                # Fallback: scan for standard patterns
                # Status code check
                st_match = re.search(r'\b([2-5]\d\d)\b', line)
                if st_match:
                    st = int(st_match.group(1))
                    status_counts[st] += 1

                # Method check
                m_match = re.search(r'\b(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\b', line)
                if m_match:
                    method_counts[m_match.group(1)] += 1

                # Path check
                p_match = re.search(r'\s(/[a-zA-Z0-9_\-\./]*)\b', line)
                if p_match:
                    endpoint_counts[p_match.group(1)] += 1

                if any(h in line.lower() for h in ["healthz", "/readyz", "kube-probe", "uptime"]):
                    healthcheck_line_count += 1

                if any(err in line.lower() for err in ["error", "exception", "failed", "critical", "fatal"]):
                    if len(error_lines) < 20:
                        error_lines.append(line[:120])

        # Status distribution groups
        status_groups = {
            "2xx_success": sum(count for st, count in status_counts.items() if 200 <= st < 300),
            "3xx_redirect": sum(count for st, count in status_counts.items() if 300 <= st < 400),
            "4xx_client_err": sum(count for st, count in status_counts.items() if 400 <= st < 500),
            "5xx_server_err": sum(count for st, count in status_counts.items() if 500 <= st < 600),
        }

        # Top endpoints (top 8)
        top_endpoints = [
            {"path": path, "count": count, "pct": round(count / max(1, total_lines) * 100, 1)}
            for path, count in endpoint_counts.most_common(8)
        ]

        # Top IPs
        top_ips = [
            {"ip": ip, "count": count}
            for ip, count in ip_counts.most_common(5)
        ]

        # Sorted status breakdown
        status_breakdown = [
            {"code": code, "count": count, "pct": round(count / max(1, total_lines) * 100, 1)}
            for code, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_lines": total_lines,
            "status_groups": status_groups,
            "status_breakdown": status_breakdown,
            "top_endpoints": top_endpoints,
            "top_ips": top_ips,
            "methods": dict(method_counts.most_common(5)),
            "healthcheck_ratio_pct": round((healthcheck_line_count / max(1, total_lines)) * 100.0, 1),
            "static_asset_ratio_pct": round((static_asset_count / max(1, total_lines)) * 100.0, 1),
            "error_samples": error_lines[:5],
            "timeline": dict(sorted(time_buckets.items())[:12]),
        }
