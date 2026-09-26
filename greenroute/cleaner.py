"""
GreenRoute Log Sanitization, Deduplication, and Optimization Engine
Reduces noise, strips uninformative telemetry, redacts PII, and groups cascades.
"""

import re
import hashlib
from typing import Dict, Any, List, Tuple, Generator, Optional
from collections import defaultdict


# Common healthcheck patterns
HEALTHCHECK_REGEX = re.compile(
    r"(GET|HEAD|POST)\s+(/healthz|/health|/readyz|/livez|/actuator/health|/ping|/status|/metrics|/robots\.txt|/favicon\.ico)\b",
    re.IGNORECASE
)

# Common bot / healthcheck User-Agents
HEALTHCHECK_UA_REGEX = re.compile(
    r"(kube-probe|ELB-HealthChecker|Amazon-Route53-Health-Check|Consul|GoogleHC|Pingdom|UptimeRobot|Datadog)",
    re.IGNORECASE
)

# PII Patterns
IPV4_REGEX = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})\b")
EMAIL_REGEX = re.compile(r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
BEARER_TOKEN_REGEX = re.compile(r"Bearer\s+[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_=]*", re.IGNORECASE)
API_KEY_PARAM_REGEX = re.compile(r"(api[_-]?key|token|secret|password|auth)=([^\s&\"']+)", re.IGNORECASE)

# User-Agent canonical patterns
UA_CHROME = re.compile(r"Mozilla/5.0.*Chrome/(\d+).*Safari", re.IGNORECASE)
UA_FIREFOX = re.compile(r"Mozilla/5.0.*Firefox/(\d+)", re.IGNORECASE)
UA_SAFARI = re.compile(r"Mozilla/5.0.*Version/(\d+).*Safari", re.IGNORECASE)
UA_BOT = re.compile(r"(Googlebot|bingbot|Baiduspider|YandexBot|DuckDuckBot)/(\d+)", re.IGNORECASE)
UA_CURL = re.compile(r"curl/(\d+\.\d+)", re.IGNORECASE)
UA_PYTHON = re.compile(r"python-requests/(\d+\.\d+)", re.IGNORECASE)

# Debug/Trace level log detection
DEBUG_TRACE_REGEX = re.compile(r"\b(DEBUG|TRACE|FINE|FINER|FINEST)\b")


class LogCleaner:
    def __init__(
        self,
        filter_healthchecks: bool = True,
        aggregate_healthchecks: bool = False,
        dedup_repeats: bool = True,
        mask_pii: bool = True,
        normalize_user_agents: bool = True,
        strip_debug_logs: bool = False,
        max_preview_lines: int = 200,
    ):
        self.filter_healthchecks = filter_healthchecks
        self.aggregate_healthchecks = aggregate_healthchecks
        self.dedup_repeats = dedup_repeats
        self.mask_pii = mask_pii
        self.normalize_user_agents = normalize_user_agents
        self.strip_debug_logs = strip_debug_logs
        self.max_preview_lines = max_preview_lines

    def clean_text(self, log_content: str) -> Dict[str, Any]:
        """
        Process multi-line raw log content and return cleaned text,
        metrics, statistics, and diff preview.
        """
        raw_lines = log_content.splitlines()
        total_raw_lines = len(raw_lines)
        total_raw_bytes = len(log_content.encode("utf-8"))

        cleaned_lines: List[str] = []
        raw_preview: List[str] = []
        cleaned_preview: List[str] = []

        stats = {
            "total_raw_lines": total_raw_lines,
            "total_raw_bytes": total_raw_bytes,
            "healthchecks_filtered": 0,
            "repeated_lines_collapsed": 0,
            "pii_instances_masked": 0,
            "user_agents_compacted": 0,
            "debug_lines_dropped": 0,
            "clean_lines_output": 0,
            "clean_bytes_output": 0,
        }

        # Track repeats for deduplication
        last_signature = None
        repeat_count = 0
        pending_line = None
        consecutive_healthcheck_count = 0

        for line in raw_lines:
            if len(raw_preview) < self.max_preview_lines:
                raw_preview.append(line)

            # 1. Debug log filter
            if self.strip_debug_logs and DEBUG_TRACE_REGEX.search(line):
                stats["debug_lines_dropped"] += 1
                continue

            # 2. Health check detector
            is_healthcheck = bool(
                HEALTHCHECK_REGEX.search(line) or HEALTHCHECK_UA_REGEX.search(line)
            )

            if is_healthcheck:
                stats["healthchecks_filtered"] += 1
                if not self.aggregate_healthchecks:
                    # Strip completely
                    continue
                else:
                    consecutive_healthcheck_count += 1
                    continue
            else:
                if consecutive_healthcheck_count > 0:
                    summary_line = f"[GREENROUTE-AGGR] Collapsed {consecutive_healthcheck_count} synthetic healthchecks / status polls"
                    cleaned_lines.append(summary_line)
                    consecutive_healthcheck_count = 0

            # 3. Clean line transformations (PII + User Agent)
            transformed_line = line

            if self.mask_pii:
                # Mask IPv4 (keep subnet for geo-analytics, mask host)
                def mask_ip(m):
                    stats["pii_instances_masked"] += 1
                    return f"{m.group(1)}0/24"
                transformed_line = IPV4_REGEX.sub(mask_ip, transformed_line)

                # Mask Email
                def mask_email(m):
                    stats["pii_instances_masked"] += 1
                    return f"{m.group(1)}***@{m.group(2)}"
                transformed_line = EMAIL_REGEX.sub(mask_email, transformed_line)

                # Mask Bearer token
                if "bearer" in transformed_line.lower():
                    transformed_line = BEARER_TOKEN_REGEX.sub("[REDACTED_JWT]", transformed_line)
                    stats["pii_instances_masked"] += 1

                # Mask API keys / query secrets
                transformed_line = API_KEY_PARAM_REGEX.sub(r"\1=[REDACTED]", transformed_line)

            if self.normalize_user_agents:
                # Compact standard bulky User-Agent strings
                def compact_ua(text: str) -> str:
                    nonlocal stats
                    # Chrome
                    m = UA_CHROME.search(text)
                    if m:
                        stats["user_agents_compacted"] += 1
                        return UA_CHROME.sub(f"UA:Chrome/{m.group(1)}", text)
                    m = UA_FIREFOX.search(text)
                    if m:
                        stats["user_agents_compacted"] += 1
                        return UA_FIREFOX.sub(f"UA:Firefox/{m.group(1)}", text)
                    m = UA_SAFARI.search(text)
                    if m:
                        stats["user_agents_compacted"] += 1
                        return UA_SAFARI.sub(f"UA:Safari/{m.group(1)}", text)
                    m = UA_BOT.search(text)
                    if m:
                        stats["user_agents_compacted"] += 1
                        return UA_BOT.sub(f"UA:Bot:{m.group(1)}/{m.group(2)}", text)
                    m = UA_CURL.search(text)
                    if m:
                        return UA_CURL.sub(f"UA:curl/{m.group(1)}", text)
                    return text

                transformed_line = compact_ua(transformed_line)

            # 4. Error / Line Deduplication
            if self.dedup_repeats:
                # Compute a fuzzy signature by stripping numbers/timestamps
                line_sig = re.sub(r"\d{4}[-/]\d{2}[-/]\d{2}[\sT]\d{2}:\d{2}:\d{2}(\.\d+)?", "", transformed_line)
                line_sig = re.sub(r"\b\d+\b", "", line_sig).strip()

                if line_sig and line_sig == last_signature:
                    repeat_count += 1
                    stats["repeated_lines_collapsed"] += 1
                    continue
                else:
                    if repeat_count > 0 and pending_line:
                        cleaned_lines.append(f"[DEDUP x{repeat_count + 1}] {pending_line}")
                    elif pending_line:
                        cleaned_lines.append(pending_line)

                    last_signature = line_sig
                    repeat_count = 0
                    pending_line = transformed_line
            else:
                cleaned_lines.append(transformed_line)

        # Flush final pending line
        if self.dedup_repeats and pending_line:
            if repeat_count > 0:
                cleaned_lines.append(f"[DEDUP x{repeat_count + 1}] {pending_line}")
            else:
                cleaned_lines.append(pending_line)

        if consecutive_healthcheck_count > 0:
            cleaned_lines.append(f"[GREENROUTE-AGGR] Collapsed {consecutive_healthcheck_count} synthetic healthchecks / status polls")

        cleaned_text = "\n".join(cleaned_lines)
        cleaned_bytes = len(cleaned_text.encode("utf-8"))

        stats["clean_lines_output"] = len(cleaned_lines)
        stats["clean_bytes_output"] = cleaned_bytes
        stats["space_saved_bytes"] = max(0, total_raw_bytes - cleaned_bytes)
        stats["reduction_ratio"] = (
            round((stats["space_saved_bytes"] / total_raw_bytes) * 100.0, 2)
            if total_raw_bytes > 0 else 0.0
        )

        cleaned_preview = cleaned_lines[:self.max_preview_lines]

        return {
            "cleaned_text": cleaned_text,
            "stats": stats,
            "raw_preview": raw_preview,
            "cleaned_preview": cleaned_preview,
        }
