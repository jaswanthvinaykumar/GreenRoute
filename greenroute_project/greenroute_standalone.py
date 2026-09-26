#!/usr/bin/env python3
"""
========================================================================================
 🌱 GreenRoute — Sustainable Server Log Optimizer (Single-File Complete Prototype)
========================================================================================
 Hackathon Edition for HackerRing 2.0 (GDG RVITM)

 ZERO EXTERNAL DEPENDENCIES REQUIRED: Runs on pure standard Python 3.10+!
 Includes:
   - Full Web GUI (Cyber-Green Dark Dashboard with embedded CSS & JS)
   - Intelligent Log Sanitizer (Health-checks, Cascade Dedup, PII Redaction, UA Normalizer)
   - Multi-Algorithm Compression Benchmark (Raw, Cleaned, Gzip-9, Bzip2-9, LZMA-9)
   - Scientific Carbon Footprint & Energy Engine (CCF & GHG Protocol Scope 2/3)
   - Enterprise Fleet Scaled Simulator (5 GB/day to 500 GB/day)
   - Cryptographic ESG Audit Certificate Generator (Printable PDF/HTML)
   - Full CLI Mode & Automated Self-Test Suite

 USAGE:
   1. Launch Desktop GUI:     python3 greenroute_standalone.py
   2. Optimize a File (CLI):  python3 greenroute_standalone.py cli /path/to/server.log
   3. Generate Sample Log:    python3 greenroute_standalone.py sample -n 5000 -o sample.log
   4. Run Embedded Tests:     python3 greenroute_standalone.py test
========================================================================================
"""

import sys
import os
import re
import json
import time
import gzip
import bz2
import lzma
import random
import hashlib
import datetime
import argparse
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from typing import Dict, Any, List

# ======================================================================================
# 1. SCIENTIFIC CARBON FOOTPRINT & ENERGY ENGINE
# ======================================================================================

REGIONAL_PROFILES = {
    "us-east-1": {
        "name": "US East (N. Virginia)",
        "grid_intensity": 379.2,  # gCO2e / kWh
        "renewable_pct": 28.0,
        "description": "PJM Grid - Coal & Gas dominant"
    },
    "us-west-2": {
        "name": "US West (Oregon Hydro)",
        "grid_intensity": 85.4,
        "renewable_pct": 74.0,
        "description": "Northwest Pool - Hydroelectric heavy"
    },
    "eu-central-1": {
        "name": "Europe (Frankfurt)",
        "grid_intensity": 338.0,
        "renewable_pct": 52.0,
        "description": "German Grid - Transitional energy mix"
    },
    "eu-north-1": {
        "name": "Europe (Stockholm Clean Grid)",
        "grid_intensity": 24.6,
        "renewable_pct": 98.0,
        "description": "Nordic Grid - 98% Carbon Free (Hydro & Nuclear)"
    },
    "ap-south-1": {
        "name": "Asia Pacific (Mumbai, India)",
        "grid_intensity": 660.0,
        "renewable_pct": 22.0,
        "description": "Western Regional Grid - Coal dominant"
    },
    "global-avg": {
        "name": "Global Datacenter Average",
        "grid_intensity": 436.0,
        "renewable_pct": 35.0,
        "description": "IEA Worldwide Commercial Datacenter Average"
    }
}

STORAGE_SPECS = {
    "ssd": {"name": "Enterprise NVMe / SATA SSD", "watts_per_tb": 1.25, "embodied_kg_yr": 1.45},
    "hdd": {"name": "Enterprise 7.2k SAS/SATA HDD", "watts_per_tb": 6.50, "embodied_kg_yr": 0.85}
}

CLOUD_STORAGE_PRICE_PER_GB_MONTH = 0.023  # Standard AWS S3 tier


def human_bytes(size_bytes: int) -> str:
    """Convert bytes into human-readable string (KB, MB, GB, TB)."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"


class CarbonEngine:
    def __init__(
        self,
        region_key: str = "us-east-1",
        storage_type: str = "ssd",
        pue: float = 1.20,
        replication_factor: int = 3,
        retention_days: int = 365,
    ):
        self.region_key = region_key if region_key in REGIONAL_PROFILES else "us-east-1"
        self.profile = REGIONAL_PROFILES[self.region_key]
        self.storage = STORAGE_SPECS.get(storage_type, STORAGE_SPECS["ssd"])
        self.pue = max(1.0, float(pue))
        self.replication_factor = max(1, int(replication_factor))
        self.retention_days = max(1, int(retention_days))

    def calculate_savings(
        self,
        original_bytes: int,
        optimized_bytes: int,
        fleet_daily_gb: float = 50.0
    ) -> Dict[str, Any]:
        saved_bytes = max(0, original_bytes - optimized_bytes)
        reduction_percentage = (saved_bytes / original_bytes * 100.0) if original_bytes > 0 else 0.0

        saved_tb = saved_bytes / (1024 ** 4)
        effective_saved_tb = saved_tb * self.replication_factor

        # Storage Energy Consumption (kWh)
        hours_stored = (self.retention_days / 365.0) * 8760.0
        kw_per_tb = self.storage["watts_per_tb"] / 1000.0
        operational_kwh_saved = effective_saved_tb * kw_per_tb * hours_stored * self.pue

        # Operational Carbon (kg CO2e)
        operational_kg_co2_saved = (operational_kwh_saved * self.profile["grid_intensity"]) / 1000.0

        # Embodied Carbon from hardware manufacturing
        fraction_of_year = self.retention_days / 365.0
        embodied_kg_co2_saved = effective_saved_tb * self.storage["embodied_kg_yr"] * fraction_of_year
        total_kg_co2_saved = operational_kg_co2_saved + embodied_kg_co2_saved

        # Cloud Costs
        saved_gb = saved_bytes / (1024 ** 3)
        monthly_cost_saved = saved_gb * CLOUD_STORAGE_PRICE_PER_GB_MONTH * self.replication_factor
        annual_cost_saved = monthly_cost_saved * (self.retention_days / 30.4)

        # Real-World Equivalencies
        smartphones_charged = max(1, int(round(operational_kwh_saved / 0.012))) if operational_kwh_saved > 0 else 0
        km_driven_offset = total_kg_co2_saved / 0.170 if total_kg_co2_saved > 0 else 0.0
        plastic_bottles_equivalent = max(1, int(round((total_kg_co2_saved * 1000) / 82.8))) if total_kg_co2_saved > 0 else 0

        # Scaled Enterprise Projections
        fleet_reduction_ratio = (saved_bytes / original_bytes) if original_bytes > 0 else 0.85
        fleet_daily_saved_bytes = (fleet_daily_gb * (1024 ** 3)) * fleet_reduction_ratio
        fleet_annual_saved_tb = ((fleet_daily_saved_bytes * 365.0) / (1024 ** 4)) * self.replication_factor

        fleet_annual_kwh = fleet_annual_saved_tb * kw_per_tb * 8760.0 * self.pue
        fleet_annual_co2_kg = (
            (fleet_annual_kwh * self.profile["grid_intensity"] / 1000.0)
            + (fleet_annual_saved_tb * self.storage["embodied_kg_yr"])
        )
        fleet_annual_cost_usd = (fleet_annual_saved_tb * 1024) * CLOUD_STORAGE_PRICE_PER_GB_MONTH
        fleet_trees_offset = fleet_annual_co2_kg / 21.77

        return {
            "bytes": {
                "original": original_bytes,
                "optimized": optimized_bytes,
                "saved": saved_bytes,
                "reduction_percentage": round(reduction_percentage, 2),
                "original_human": human_bytes(original_bytes),
                "optimized_human": human_bytes(optimized_bytes),
                "saved_human": human_bytes(saved_bytes),
            },
            "parameters": {
                "region": self.profile["name"],
                "region_key": self.region_key,
                "grid_intensity": f"{self.profile['grid_intensity']} gCO2e/kWh",
                "storage_type": self.storage["name"],
                "pue": self.pue,
                "replication_factor": self.replication_factor,
                "retention_days": self.retention_days,
            },
            "energy": {
                "kwh_saved": round(operational_kwh_saved, 4),
                "kwh_saved_formatted": f"{operational_kwh_saved:.3f} kWh",
            },
            "emissions": {
                "operational_kg_co2": round(operational_kg_co2_saved, 4),
                "embodied_kg_co2": round(embodied_kg_co2_saved, 4),
                "total_kg_co2_saved": round(total_kg_co2_saved, 4),
                "total_co2_formatted": f"{total_kg_co2_saved:.3f} kg CO2e"
                if total_kg_co2_saved >= 1.0
                else f"{(total_kg_co2_saved * 1000.0):.1f} g CO2e",
            },
            "financial": {
                "annual_cost_saved_usd": round(annual_cost_saved, 2),
            },
            "equivalencies": {
                "smartphones_charged": smartphones_charged,
                "km_driven_offset": round(km_driven_offset, 2),
                "plastic_bottles_equivalent": plastic_bottles_equivalent,
            },
            "projections": {
                "fleet_daily_gb": fleet_daily_gb,
                "fleet_annual_saved_tb": round(fleet_annual_saved_tb, 2),
                "fleet_annual_kwh": round(fleet_annual_kwh, 1),
                "fleet_annual_co2_kg": round(fleet_annual_co2_kg, 1),
                "fleet_annual_co2_metric_tons": round(fleet_annual_co2_kg / 1000.0, 2),
                "fleet_annual_cost_usd": round(fleet_annual_cost_usd, 2),
                "fleet_trees_offset": round(fleet_trees_offset, 1),
            }
        }


# ======================================================================================
# 2. INTELLIGENT LOG SANITIZATION & DEDUPLICATION ENGINE
# ======================================================================================

HEALTHCHECK_REGEX = re.compile(
    r"(GET|HEAD|POST)\s+(/healthz|/health|/readyz|/livez|/actuator/health|/ping|/status|/metrics|/robots\.txt|/favicon\.ico)\b",
    re.IGNORECASE
)
HEALTHCHECK_UA_REGEX = re.compile(
    r"(kube-probe|ELB-HealthChecker|Amazon-Route53-Health-Check|Consul|GoogleHC|Pingdom|UptimeRobot|Datadog)",
    re.IGNORECASE
)

IPV4_REGEX = re.compile(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})\b")
EMAIL_REGEX = re.compile(r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
BEARER_TOKEN_REGEX = re.compile(r"Bearer\s+[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_=]*", re.IGNORECASE)
API_KEY_PARAM_REGEX = re.compile(r"(api[_-]?key|token|secret|password|auth)=([^\s&\"']+)", re.IGNORECASE)

UA_CHROME = re.compile(r"Mozilla/5.0.*Chrome/(\d+).*Safari", re.IGNORECASE)
UA_FIREFOX = re.compile(r"Mozilla/5.0.*Firefox/(\d+)", re.IGNORECASE)
UA_SAFARI = re.compile(r"Mozilla/5.0.*Version/(\d+).*Safari", re.IGNORECASE)
UA_BOT = re.compile(r"(Googlebot|bingbot|Baiduspider|YandexBot|DuckDuckBot)/(\d+)", re.IGNORECASE)
UA_CURL = re.compile(r"curl/(\d+\.\d+)", re.IGNORECASE)


class LogCleaner:
    def __init__(
        self,
        filter_healthchecks: bool = True,
        dedup_repeats: bool = True,
        mask_pii: bool = True,
        normalize_user_agents: bool = True,
    ):
        self.filter_healthchecks = filter_healthchecks
        self.dedup_repeats = dedup_repeats
        self.mask_pii = mask_pii
        self.normalize_user_agents = normalize_user_agents

    def clean_text(self, log_content: str) -> Dict[str, Any]:
        raw_lines = log_content.splitlines()
        total_raw_lines = len(raw_lines)
        total_raw_bytes = len(log_content.encode("utf-8"))

        cleaned_lines: List[str] = []
        raw_preview: List[str] = []

        stats = {
            "total_raw_lines": total_raw_lines,
            "total_raw_bytes": total_raw_bytes,
            "healthchecks_filtered": 0,
            "repeated_lines_collapsed": 0,
            "pii_instances_masked": 0,
            "user_agents_compacted": 0,
            "clean_lines_output": 0,
            "clean_bytes_output": 0,
        }

        last_signature = None
        repeat_count = 0
        pending_line = None

        for line in raw_lines:
            if len(raw_preview) < 150:
                raw_preview.append(line)

            # Health check filter
            if self.filter_healthchecks:
                if HEALTHCHECK_REGEX.search(line) or HEALTHCHECK_UA_REGEX.search(line):
                    stats["healthchecks_filtered"] += 1
                    continue

            transformed = line

            # Mask PII
            if self.mask_pii:
                def mask_ip(m):
                    stats["pii_instances_masked"] += 1
                    return f"{m.group(1)}0/24"
                transformed = IPV4_REGEX.sub(mask_ip, transformed)

                def mask_email(m):
                    stats["pii_instances_masked"] += 1
                    return f"{m.group(1)}***@{m.group(2)}"
                transformed = EMAIL_REGEX.sub(mask_email, transformed)

                if "bearer" in transformed.lower():
                    transformed = BEARER_TOKEN_REGEX.sub("[REDACTED_JWT]", transformed)
                    stats["pii_instances_masked"] += 1

                transformed = API_KEY_PARAM_REGEX.sub(r"\1=[REDACTED]", transformed)

            # Compact User Agents
            if self.normalize_user_agents:
                m = UA_CHROME.search(transformed)
                if m:
                    stats["user_agents_compacted"] += 1
                    transformed = UA_CHROME.sub(f"UA:Chrome/{m.group(1)}", transformed)
                else:
                    m = UA_FIREFOX.search(transformed)
                    if m:
                        stats["user_agents_compacted"] += 1
                        transformed = UA_FIREFOX.sub(f"UA:Firefox/{m.group(1)}", transformed)
                    else:
                        m = UA_BOT.search(transformed)
                        if m:
                            stats["user_agents_compacted"] += 1
                            transformed = UA_BOT.sub(f"UA:Bot:{m.group(1)}", transformed)

            # Deduplicate repeated errors/lines
            if self.dedup_repeats:
                line_sig = re.sub(r"\d{4}[-/]\d{2}[-/]\d{2}[\sT]\d{2}:\d{2}:\d{2}(\.\d+)?", "", transformed)
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
                    pending_line = transformed
            else:
                cleaned_lines.append(transformed)

        if self.dedup_repeats and pending_line:
            if repeat_count > 0:
                cleaned_lines.append(f"[DEDUP x{repeat_count + 1}] {pending_line}")
            else:
                cleaned_lines.append(pending_line)

        cleaned_text = "\n".join(cleaned_lines)
        stats["clean_lines_output"] = len(cleaned_lines)
        stats["clean_bytes_output"] = len(cleaned_text.encode("utf-8"))

        return {
            "cleaned_text": cleaned_text,
            "stats": stats,
            "raw_preview": raw_preview,
            "cleaned_preview": cleaned_lines[:150],
        }


# ======================================================================================
# 3. MULTI-ALGORITHM COMPRESSION BENCHMARKING
# ======================================================================================

class Compressor:
    @staticmethod
    def compress_all(raw_content: str, cleaned_content: str) -> Dict[str, Any]:
        raw_bytes = raw_content.encode("utf-8")
        clean_bytes = cleaned_content.encode("utf-8")
        raw_size = len(raw_bytes)
        clean_size = len(clean_bytes)

        benchmarks = []

        # 1. Baseline
        benchmarks.append({
            "id": "raw", "name": "Raw Baseline (Plaintext)", "codec": "None",
            "size_bytes": raw_size, "reduction_pct": 0.0,
            "duration_ms": 0.0, "is_baseline": True, "tag": "Worst Footprint"
        })

        # 2. Cleaned Plaintext
        clean_red = ((raw_size - clean_size) / raw_size * 100.0) if raw_size > 0 else 0.0
        benchmarks.append({
            "id": "clean_raw", "name": "GreenRoute Cleaned (Plaintext)", "codec": "None",
            "size_bytes": clean_size, "reduction_pct": round(clean_red, 2),
            "duration_ms": 0.0, "is_baseline": False, "tag": "Noise Filtered"
        })

        # 3. Standard Gzip-6 on Raw
        t0 = time.perf_counter()
        raw_gz = gzip.compress(raw_bytes, compresslevel=6)
        gz_dur = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "raw_gzip", "name": "Standard Cloud Gzip (Raw)", "codec": "gzip-6",
            "size_bytes": len(raw_gz),
            "reduction_pct": round(((raw_size - len(raw_gz)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "duration_ms": round(gz_dur, 2), "is_baseline": False, "tag": "Cloud Standard"
        })

        # 4. GreenRoute + Gzip-9
        t0 = time.perf_counter()
        clean_gz = gzip.compress(clean_bytes, compresslevel=9)
        cgz_dur = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "green_gzip", "name": "GreenRoute + Gzip-9", "codec": "gzip-9",
            "size_bytes": len(clean_gz),
            "reduction_pct": round(((raw_size - len(clean_gz)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "duration_ms": round(cgz_dur, 2), "is_baseline": False, "tag": "Fast & Efficient"
        })

        # 5. GreenRoute + Bzip2-9
        t0 = time.perf_counter()
        clean_bz2 = bz2.compress(clean_bytes, compresslevel=9)
        cbz_dur = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "green_bz2", "name": "GreenRoute + Bzip2-9", "codec": "bzip2-9",
            "size_bytes": len(clean_bz2),
            "reduction_pct": round(((raw_size - len(clean_bz2)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "duration_ms": round(cbz_dur, 2), "is_baseline": False, "tag": "High Density"
        })

        # 6. GreenRoute Max (LZMA/XZ-9)
        t0 = time.perf_counter()
        clean_lzma = lzma.compress(clean_bytes, preset=9)
        clz_dur = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "green_lzma", "name": "GreenRoute Max (LZMA/XZ)", "codec": "lzma-9",
            "size_bytes": len(clean_lzma),
            "reduction_pct": round(((raw_size - len(clean_lzma)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "duration_ms": round(clz_dur, 2), "is_baseline": False, "tag": "Max Green Footprint",
            "is_recommended": True
        })

        best = min(benchmarks, key=lambda b: b["size_bytes"])
        return {
            "benchmarks": benchmarks,
            "best_codec": best,
            "payloads": {"gzip": clean_gz, "bz2": clean_bz2, "lzma": clean_lzma}
        }


# ======================================================================================
# 4. LOG ANALYZER & REALISTIC SAMPLE GENERATOR
# ======================================================================================

class LogAnalyzer:
    @staticmethod
    def analyze(log_content: str) -> Dict[str, Any]:
        lines = log_content.splitlines()
        total = len(lines)
        status_counts = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}
        endpoint_counts: Dict[str, int] = {}

        for line in lines:
            m_stat = re.search(r'\b([2-5]\d\d)\b', line)
            if m_stat:
                st = int(m_stat.group(1))
                if 200 <= st < 300: status_counts["2xx"] += 1
                elif 300 <= st < 400: status_counts["3xx"] += 1
                elif 400 <= st < 500: status_counts["4xx"] += 1
                elif 500 <= st < 600: status_counts["5xx"] += 1

            m_path = re.search(r'"(?:GET|POST|PUT|DELETE)\s+([^\s?]+)', line)
            if m_path:
                path = m_path.group(1)
                endpoint_counts[path] = endpoint_counts.get(path, 0) + 1

        top_endpoints = [
            {"path": p, "count": c, "pct": round(c / max(1, total) * 100, 1)}
            for p, c in sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:6]
        ]

        return {
            "status_groups": status_counts,
            "top_endpoints": top_endpoints,
        }


def generate_sample_logs(lines: int = 5000) -> str:
    """Generate realistic server logs containing healthchecks, cascades, PII, and user traffic."""
    endpoints = [
        ("/api/v1/auth/login", "POST", 200, 1420),
        ("/api/v1/products/search", "GET", 200, 4820),
        ("/api/v1/checkout", "POST", 200, 2190),
        ("/dashboard/home", "GET", 200, 18500),
        ("/assets/bundle.min.js", "GET", 200, 124500),
    ]
    probes = ["/healthz", "/readyz", "/ping", "/status"]
    ips = ["192.168.1.45", "10.0.2.14", "172.16.50.88", "203.0.113.195"]
    uas = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "kube-probe/1.28+",
        "ELB-HealthChecker/2.0"
    ]

    base_time = datetime.datetime.now() - datetime.timedelta(hours=2)
    out_lines = []

    for i in range(lines):
        t_str = (base_time + datetime.timedelta(seconds=int(i * 1.2))).strftime("%d/%b/%Y:%H:%M:%S +0000")

        # Simulate cascade outage (10% of logs)
        if 800 <= i < 1300:
            out_lines.append(
                f'10.0.4.15 - - [{t_str}] "POST /api/v1/checkout HTTP/1.1" 500 482 '
                f'"-" "Mozilla/5.0" [ERROR] database connection pool exhausted: timeout 5000ms acquire connection'
            )
            continue

        # Simulate synthetic healthcheck (42% of logs)
        if random.random() < 0.42:
            probe = random.choice(probes)
            out_lines.append(f'127.0.0.1 - - [{t_str}] "GET {probe} HTTP/1.1" 200 24 "-" "kube-probe/1.28+"')
            continue

        # Normal user traffic
        ep, method, st, sz = random.choice(endpoints)
        ip = random.choice(ips)
        ua = random.choice(uas)
        pii = ""
        if random.random() < 0.15:
            pii = f' ?email=user_{random.randint(10,99)}@corp.io&auth=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.secret'

        out_lines.append(f'{ip} - user_{random.randint(100,999)} [{t_str}] "{method} {ep}{pii} HTTP/1.1" {st} {sz} "-" "{ua}"')

    return "\n".join(out_lines)


# ======================================================================================
# 5. CRYPTOGRAPHIC ESG SUSTAINABILITY CERTIFICATE GENERATOR
# ======================================================================================

def generate_esg_certificate_html(
    analysis_data: Dict[str, Any],
    org_name: str = "Enterprise Cloud Operations",
    sys_name: str = "Production Cluster Logs"
) -> str:
    savings = analysis_data.get("carbon_savings", {})
    bytes_data = savings.get("bytes", {})
    emissions = savings.get("emissions", {})
    energy = savings.get("energy", {})
    financial = savings.get("financial", {})
    clean_stats = analysis_data.get("cleaner_stats", {})
    now_str = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S UTC")

    cert_id = "GR-" + hashlib.sha256(f"{org_name}-{bytes_data.get('saved', 0)}-{now_str}".encode("utf-8")).hexdigest()[:16].upper()

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>GreenRoute ESG Certificate - {cert_id}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f17; color: #f3f4f6; display: flex; justify-content: center; padding: 30px; }}
  .cert {{ max-width: 800px; width: 100%; background: #111827; border: 2px solid #10b981; border-radius: 16px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
  .head {{ display: flex; justify-content: space-between; border-bottom: 1px solid #1f293d; padding-bottom: 18px; margin-bottom: 24px; }}
  .logo {{ font-size: 24px; font-weight: 800; color: #10b981; }}
  .cert-id {{ font-family: monospace; color: #84cc16; font-size: 13px; text-align: right; }}
  h1 {{ font-size: 26px; text-align: center; margin-bottom: 8px; color: #fff; }}
  .sub {{ text-align: center; color: #9ca3af; font-size: 14px; margin-bottom: 28px; }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 28px; text-align: center; }}
  .card {{ background: #162032; border: 1px solid #1f293d; border-radius: 10px; padding: 14px 8px; }}
  .val {{ font-size: 22px; font-weight: 800; color: #10b981; font-family: monospace; }}
  .lbl {{ font-size: 11px; color: #9ca3af; text-transform: uppercase; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; font-size: 13px; }}
  th, td {{ padding: 10px 14px; border-bottom: 1px solid #1f293d; text-align: left; }}
  th {{ color: #9ca3af; text-transform: uppercase; font-size: 11px; }}
  td:last-child {{ text-align: right; font-family: monospace; color: #fff; font-weight: 600; }}
  .btn {{ background: linear-gradient(135deg, #10b981, #84cc16); color: #000; font-weight: 700; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; display: block; margin: 0 auto; }}
  @media print {{ body {{ background: #fff; color: #000; }} .cert {{ border: 2px solid #000; background: #fff; color: #000; box-shadow: none; }} .btn {{ display: none; }} .val {{ color: #059669; }} td:last-child {{ color: #000; }} }}
</style>
</head>
<body>
<div class="cert">
  <div class="head">
    <div class="logo">🌱 GreenRoute</div>
    <div class="cert-id">
      <div>CERT: {cert_id}</div>
      <div>STANDARD: GHG Scope 2/3 & CCF</div>
      <div>Issued: {now_str}</div>
    </div>
  </div>
  <h1>Certificate of Carbon Reduction</h1>
  <p class="sub">Verifiable telemetry optimization, power conservation, and greenhouse gas abatement audit.</p>
  
  <div class="grid">
    <div class="card"><div class="val">-{bytes_data.get('reduction_percentage', 0)}%</div><div class="lbl">Storage Saved</div></div>
    <div class="card"><div class="val">{emissions.get('total_co2_formatted', '0 g')}</div><div class="lbl">CO₂e Abated</div></div>
    <div class="card"><div class="val">{energy.get('kwh_saved_formatted', '0 kWh')}</div><div class="lbl">Energy Conserved</div></div>
    <div class="card"><div class="val">${financial.get('annual_cost_saved_usd', 0):.2f}</div><div class="lbl">Annual Cloud Saved</div></div>
  </div>

  <table>
    <tr><th>Metric</th><th>Parameter</th><th>Verified Result</th></tr>
    <tr><td>Entity / Org</td><td>Enterprise Cloud System</td><td>{org_name}</td></tr>
    <tr><td>Service Target</td><td>Server Telemetry Stream</td><td>{sys_name}</td></tr>
    <tr><td>Baseline Ingestion</td><td>Raw Uncompressed Telemetry</td><td>{bytes_data.get('original_human', '0 B')}</td></tr>
    <tr><td>GreenRoute Optimized</td><td>Cleaned & Compressed Archive</td><td>{bytes_data.get('optimized_human', '0 B')}</td></tr>
    <tr><td>Space Salvaged</td><td>Effective Storage Eliminated</td><td>{bytes_data.get('saved_human', '0 B')}</td></tr>
    <tr><td>Noisy Probes Filtered</td><td>/healthz, /readyz, uptime</td><td>{clean_stats.get('healthchecks_filtered', 0):,} events</td></tr>
    <tr><td>Cascades Deduplicated</td><td>Repeated Stack Trace Bursts</td><td>{clean_stats.get('repeated_lines_collapsed', 0):,} lines</td></tr>
    <tr><td>PII Redacted</td><td>GDPR / HIPAA Anonymization</td><td>{clean_stats.get('pii_instances_masked', 0):,} items</td></tr>
  </table>

  <button class="btn" onclick="window.print()">Print or Save Official Certificate (PDF)</button>
</div>
</body>
</html>"""


# ======================================================================================
# 6. EMBEDDED DASHBOARD (HTML, CSS & JS)
# ======================================================================================

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GreenRoute — Sustainable Server Log Optimizer</title>
  <style>
    :root {
      --bg: #0a0e17; --card: #111827; --card-sub: #162032; --border: #1f293d;
      --emerald: #10b981; --lime: #84cc16; --cyan: #06b6d4; --gold: #f59e0b;
      --text: #f9fafb; --muted: #9ca3af; --mono: monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    .navbar { display: flex; justify-content: space-between; align-items: center; padding: 14px 28px; background: rgba(17,24,39,0.9); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }
    .brand { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 800; }
    .brand span { color: var(--emerald); }
    .badge { background: rgba(16,185,129,0.15); color: var(--emerald); font-size: 10px; padding: 2px 7px; border-radius: 4px; border: 1px solid rgba(16,185,129,0.3); font-weight: 700; }
    .btn { font-family: inherit; font-size: 13px; font-weight: 600; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
    .btn-emerald { background: linear-gradient(135deg, var(--emerald), var(--lime)); color: #000; font-weight: 700; }
    .btn-secondary { background: var(--card-sub); color: #fff; border: 1px solid var(--border); }
    .btn-outline { background: transparent; color: #fff; border: 1px solid var(--border); }
    .btn:hover { opacity: 0.9; transform: translateY(-1px); }
    .main { display: grid; grid-template-columns: 380px 1fr; gap: 20px; padding: 20px 28px; max-width: 1680px; margin: 0 auto; }
    @media (max-width: 1024px) { .main { grid-template-columns: 1fr; } }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .dropzone { border: 2px dashed rgba(16,185,129,0.4); background: rgba(16,185,129,0.03); text-align: center; padding: 28px 16px; border-radius: 12px; cursor: pointer; }
    .dropzone:hover { border-color: var(--emerald); background: rgba(16,185,129,0.08); }
    .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
    .form-group label { font-size: 11px; text-transform: uppercase; color: var(--muted); font-weight: 700; }
    .control { background: var(--card-sub); border: 1px solid var(--border); color: #fff; padding: 8px 10px; border-radius: 6px; font-family: inherit; font-size: 13px; }
    .range { accent-color: var(--emerald); cursor: pointer; }
    .chk-list { display: flex; flex-direction: column; gap: 10px; margin-top: 10px; }
    .chk-item { display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer; }
    .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
    @media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
    .kpi { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; position: relative; }
    .kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--emerald); }
    .kpi.lime::before { background: var(--lime); }
    .kpi.cyan::before { background: var(--cyan); }
    .kpi.gold::before { background: var(--gold); }
    .kpi-val { font-size: 24px; font-weight: 800; font-family: var(--mono); margin: 4px 0; }
    .kpi-lbl { font-size: 11px; text-transform: uppercase; color: var(--muted); font-weight: 700; }
    .ent-banner { background: linear-gradient(135deg, rgba(6,182,212,0.08), rgba(16,185,129,0.05)); border: 1px solid rgba(6,182,212,0.3); border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; }
    .ent-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; text-align: center; margin-top: 10px; }
    .ent-box { background: rgba(255,255,255,0.02); border: 1px solid var(--border); padding: 12px; border-radius: 8px; }
    .ent-num { font-size: 18px; font-weight: 800; font-family: var(--mono); color: var(--cyan); }
    .bar-row { display: grid; grid-template-columns: 180px 1fr 90px; align-items: center; gap: 12px; margin-bottom: 10px; font-size: 13px; }
    .track { height: 22px; background: var(--card-sub); border-radius: 6px; overflow: hidden; }
    .fill { height: 100%; border-radius: 6px; background: var(--emerald); display: flex; align-items: center; padding-left: 8px; font-size: 11px; font-weight: 700; color: #000; transition: width 0.6s ease; }
    .fill.raw { background: #64748b; color: #fff; }
    .fill.lzma { background: linear-gradient(90deg, var(--emerald), var(--lime)); }
    .table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 14px; }
    .table th, .table td { padding: 10px; border-bottom: 1px solid var(--border); text-align: left; }
    .table th { color: var(--muted); font-size: 11px; text-transform: uppercase; }
    .diff-view { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
    .pane { background: #070a10; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
    .pane-title { background: var(--card-sub); padding: 8px 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--muted); }
    .pane pre { font-family: var(--mono); font-size: 11px; padding: 12px; height: 240px; overflow: auto; white-space: pre-wrap; word-break: break-all; color: #cbd5e1; }
    .modal { position: fixed; inset: 0; background: rgba(0,0,0,0.85); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
    .modal-box { background: var(--card); border: 1px solid var(--border); border-radius: 14px; max-width: 860px; width: 100%; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; }
    .hidden { display: none !important; }
  </style>
</head>
<body>

  <header class="navbar">
    <div class="brand">🌱 GreenRoute <span>Optimizer</span> <span class="badge">STANDALONE v1.0</span></div>
    <div style="display: flex; gap: 10px;">
      <button class="btn btn-secondary" onclick="triggerSample()">⚡ Load 5,000 Sample Logs</button>
      <button class="btn btn-emerald" id="btn-cert" onclick="openCert()" disabled>📜 ESG Certificate</button>
    </div>
  </header>

  <main class="main">
    <!-- Controls Column -->
    <section>
      <div class="card dropzone" onclick="document.getElementById('file-input').click()">
        <h3 style="margin-bottom: 6px;">Drop Server Logs Here</h3>
        <p style="font-size: 12px; color: var(--muted);">Click to browse (.log, .txt, .json, .gz)</p>
        <input type="file" id="file-input" style="display: none;" onchange="handleFile(this.files[0])">
      </div>

      <div class="card">
        <h4 style="margin-bottom: 14px; font-size: 14px; text-transform: uppercase; color: var(--emerald);">Tuning Parameters</h4>
        <div class="form-group">
          <label>Datacenter Region</label>
          <select id="sel-region" class="control">
            <option value="us-east-1" selected>US East (N. Virginia) • 379 gCO2e/kWh</option>
            <option value="us-west-2">US West (Oregon Hydro) • 85 gCO2e/kWh</option>
            <option value="eu-central-1">Europe (Frankfurt) • 338 gCO2e/kWh</option>
            <option value="eu-north-1">Europe (Sweden Clean) • 25 gCO2e/kWh</option>
            <option value="ap-south-1">Asia Pacific (Mumbai, India) • 660 gCO2e/kWh</option>
            <option value="global-avg">Global Datacenter Average • 436 gCO2e/kWh</option>
          </select>
        </div>

        <div class="form-group">
          <label>Storage Medium</label>
          <select id="sel-storage" class="control">
            <option value="ssd" selected>Enterprise NVMe / SATA SSD (1.25 W/TB)</option>
            <option value="hdd">Enterprise 7.2k HDD (6.50 W/TB)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Fleet Scale: <span id="lbl-fleet" style="color: var(--emerald); font-family: var(--mono);">50 GB / Day</span></label>
          <input type="range" id="rng-fleet" min="5" max="500" step="15" value="50" class="range" oninput="updateFleetLabel(this.value)">
        </div>

        <div class="chk-list">
          <label class="chk-item"><input type="checkbox" id="chk-hc" checked> Filter Healthchecks (/healthz, probes)</label>
          <label class="chk-item"><input type="checkbox" id="chk-dedup" checked> Deduplicate Error Cascade Storms</label>
          <label class="chk-item"><input type="checkbox" id="chk-pii" checked> Mask PII & Redact Bearer JWT Tokens</label>
          <label class="chk-item"><input type="checkbox" id="chk-ua" checked> Normalize User-Agent Bloat</label>
        </div>

        <button class="btn btn-emerald" style="width: 100%; margin-top: 16px; justify-content: center;" onclick="reoptimize()">
          🔄 Run GreenRoute Optimizer
        </button>
      </div>
    </section>

    <!-- Results Column -->
    <section>
      <div id="results" class="hidden">
        <!-- KPI Cards -->
        <div class="kpi-grid">
          <div class="kpi">
            <div class="kpi-lbl">Storage Salvaged</div>
            <div class="kpi-val" id="kpi-saved">0 B</div>
            <div style="font-size: 11px; color: var(--emerald);" id="kpi-pct">-0%</div>
          </div>
          <div class="kpi lime">
            <div class="kpi-lbl">CO₂e Abatement</div>
            <div class="kpi-val" id="kpi-co2">0 g</div>
            <div style="font-size: 11px; color: var(--muted);">Direct Scope 2/3 GHG</div>
          </div>
          <div class="kpi cyan">
            <div class="kpi-lbl">Energy Conserved</div>
            <div class="kpi-val" id="kpi-kwh">0 kWh</div>
            <div style="font-size: 11px; color: var(--muted);">PUE 1.2x factored</div>
          </div>
          <div class="kpi gold">
            <div class="kpi-lbl">Annual Cloud Saved</div>
            <div class="kpi-val" id="kpi-cost">$0</div>
            <div style="font-size: 11px; color: var(--muted);">AWS S3 multi-AZ 3x</div>
          </div>
        </div>

        <!-- Enterprise Scaled Banner -->
        <div class="ent-banner">
          <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; color: var(--cyan);">
            🏢 Enterprise Fleet Annual Scaled Impact (<span id="ent-scale-lbl">50 GB/day</span>)
          </div>
          <div class="ent-grid">
            <div class="ent-box"><div class="ent-num" id="ent-co2">0 Tons</div><div class="kpi-lbl">Annual CO₂ Abated</div></div>
            <div class="ent-box"><div class="ent-num" id="ent-kwh">0 MWh</div><div class="kpi-lbl">Energy Conserved</div></div>
            <div class="ent-box"><div class="ent-num" id="ent-cost">$0</div><div class="kpi-lbl">Cloud Bill Slashed</div></div>
            <div class="ent-box"><div class="ent-num" id="ent-trees">0 Trees</div><div class="kpi-lbl">Tree Absorption Equiv.</div></div>
          </div>
        </div>

        <!-- Compression Benchmarks -->
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h4 style="font-size: 14px;">Multi-Algorithm Compression Benchmark</h4>
            <div>
              <span style="font-size: 12px; color: var(--muted); margin-right: 6px;">Download:</span>
              <button class="btn btn-outline" style="padding: 4px 10px; font-size: 11px;" onclick="downloadCodec('lzma')">XZ Archive</button>
              <button class="btn btn-outline" style="padding: 4px 10px; font-size: 11px;" onclick="downloadCodec('gzip')">Gzip</button>
            </div>
          </div>
          <div id="bars"></div>
          <table class="table">
            <thead><tr><th>Codec</th><th>Size</th><th>Reduction</th><th>Duration</th><th>Tag</th></tr></thead>
            <tbody id="table-body"></tbody>
          </table>
        </div>

        <!-- Side-by-Side Diff -->
        <div class="card">
          <h4 style="font-size: 14px; margin-bottom: 10px;">Live Telemetry Stream: Raw vs Cleaned</h4>
          <div class="diff-view">
            <div class="pane"><div class="pane-title">Raw Ingested (Noisy & Unsanitized)</div><pre id="raw-pre">...</pre></div>
            <div class="pane"><div class="pane-title">GreenRoute Cleaned & Anonymized</div><pre id="clean-pre">...</pre></div>
          </div>
        </div>
      </div>

      <div id="empty-state" class="card" style="text-align: center; padding: 60px 20px;">
        <h2 style="margin-bottom: 8px;">🌱 Ready to optimize server telemetry</h2>
        <p style="color: var(--muted); font-size: 14px; margin-bottom: 20px;">Drop a server log on the left or click below to run the live 5,000-line simulation.</p>
        <button class="btn btn-emerald" style="padding: 12px 24px; font-size: 15px;" onclick="triggerSample()">🚀 Run 5,000 Production Sample Logs</button>
      </div>
    </section>
  </main>

  <!-- Modal -->
  <div id="modal" class="modal hidden">
    <div class="modal-box">
      <div style="display: flex; justify-content: space-between; padding: 14px 20px; border-bottom: 1px solid var(--border);">
        <h3 style="font-size: 16px;">🌱 Official ESG Sustainability Audit Certificate</h3>
        <button style="background: none; border: none; color: #fff; font-size: 18px; cursor: pointer;" onclick="closeCert()">✕</button>
      </div>
      <iframe id="cert-frame" style="width: 100%; height: 500px; border: none;"></iframe>
    </div>
  </div>

  <script>
    let activeData = null;
    let activeLogText = "";

    function updateFleetLabel(v) {
      document.getElementById('lbl-fleet').textContent = v + ' GB / Day';
      document.getElementById('ent-scale-lbl').textContent = v + ' GB/day';
    }

    function getParams() {
      return {
        region: document.getElementById('sel-region').value,
        storage_type: document.getElementById('sel-storage').value,
        fleet_daily_gb: parseFloat(document.getElementById('rng-fleet').value),
        filter_healthchecks: document.getElementById('chk-hc').checked,
        dedup_repeats: document.getElementById('chk-dedup').checked,
        mask_pii: document.getElementById('chk-pii').checked,
        normalize_user_agents: document.getElementById('chk-ua').checked,
      };
    }

    async function triggerSample() {
      const p = getParams();
      p.lines = 5000;
      const res = await fetch('/api/generate-sample', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(p)
      });
      activeData = await res.json();
      render(activeData);
    }

    async function handleFile(f) {
      if (!f) return;
      const text = await f.text();
      activeLogText = text;
      const p = getParams();
      p.log_text = text;
      const res = await fetch('/api/optimize', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(p)
      });
      activeData = await res.json();
      render(activeData);
    }

    async function reoptimize() {
      if (activeLogText) {
        const p = getParams();
        p.log_text = activeLogText;
        const res = await fetch('/api/optimize', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(p)
        });
        activeData = await res.json();
        render(activeData);
      } else {
        triggerSample();
      }
    }

    function render(d) {
      document.getElementById('empty-state').classList.add('hidden');
      document.getElementById('results').classList.remove('hidden');
      document.getElementById('btn-cert').disabled = false;

      const sav = d.carbon_savings;
      document.getElementById('kpi-saved').textContent = sav.bytes.saved_human;
      document.getElementById('kpi-pct').textContent = '-' + sav.bytes.reduction_percentage + '% storage reduction';
      document.getElementById('kpi-co2').textContent = sav.emissions.total_co2_formatted;
      document.getElementById('kpi-kwh').textContent = sav.energy.kwh_saved_formatted;
      document.getElementById('kpi-cost').textContent = '$' + sav.financial.annual_cost_saved_usd.toFixed(2);

      const pr = sav.projections;
      document.getElementById('ent-scale-lbl').textContent = pr.fleet_daily_gb + ' GB/day';
      document.getElementById('ent-co2').textContent = pr.fleet_annual_co2_metric_tons.toFixed(2) + ' Tons';
      document.getElementById('ent-kwh').textContent = (pr.fleet_annual_kwh / 1000).toFixed(2) + ' MWh';
      document.getElementById('ent-cost').textContent = '$' + Math.round(pr.fleet_annual_cost_usd).toLocaleString();
      document.getElementById('ent-trees').textContent = Math.round(pr.fleet_trees_offset).toLocaleString() + ' Trees';

      // Bars & table
      const bars = document.getElementById('bars');
      const tbody = document.getElementById('table-body');
      bars.innerHTML = ''; tbody.innerHTML = '';
      const maxB = Math.max(...d.benchmarks.map(b => b.size_bytes), 1);

      d.benchmarks.forEach(b => {
        const pct = Math.max(5, (b.size_bytes / maxB) * 100);
        let fClass = 'fill';
        if (b.id === 'raw') fClass += ' raw';
        if (b.id === 'green_lzma') fClass += ' lzma';

        bars.innerHTML += `
          <div class="bar-row">
            <div>${b.name}</div>
            <div class="track"><div class="${fClass}" style="width: ${pct}%">${b.reduction_pct > 0 ? '-' + b.reduction_pct + '%' : 'Baseline'}</div></div>
            <div style="text-align: right; font-family: var(--mono);">${formatBytes(b.size_bytes)}</div>
          </div>`;

        tbody.innerHTML += `
          <tr>
            <td><strong>${b.name}</strong></td>
            <td>${formatBytes(b.size_bytes)}</td>
            <td style="color: ${b.reduction_pct > 0 ? 'var(--emerald)' : 'inherit'};">${b.reduction_pct > 0 ? '-' + b.reduction_pct + '%' : '0%'}</td>
            <td>${b.duration_ms > 0 ? b.duration_ms + ' ms' : '—'}</td>
            <td><span class="badge">${b.tag}</span></td>
          </tr>`;
      });

      document.getElementById('raw-pre').textContent = d.raw_preview.slice(0, 80).join('\\n');
      document.getElementById('clean-pre').textContent = d.cleaned_preview.slice(0, 80).join('\\n');
    }

    function formatBytes(bytes) {
      if (bytes === 0) return "0 B";
      const k = 1024, sizes = ["B", "KB", "MB", "GB", "TB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    async function openCert() {
      const res = await fetch('/api/certificate', {method: 'POST'});
      const html = await res.text();
      document.getElementById('cert-frame').srcdoc = html;
      document.getElementById('modal').classList.remove('hidden');
    }

    function closeCert() { document.getElementById('modal').classList.add('hidden'); }
    function downloadCodec(c) { window.location.href = '/api/download/' + c; }
  </script>
</body>
</html>"""


# ======================================================================================
# 7. EMBEDDED HTTP SERVER (ZERO DEPENDENCY / PYTHON BUILT-IN)
# ======================================================================================

LAST_STATE = {}


class GreenRouteHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy standard request logs in terminal
        return

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif path.startswith("/api/download/"):
            codec = path.split("/")[-1].lower()
            if not LAST_STATE or "cleaned_text" not in LAST_STATE:
                self.send_error(404, "No optimized log found. Run optimization first.")
                return

            cleaned_bytes = LAST_STATE["cleaned_text"].encode("utf-8")
            if codec in ["lzma", "xz"]:
                payload = lzma.compress(cleaned_bytes, preset=9)
                fname = "greenroute_optimized.log.xz"
            elif codec == "bz2":
                payload = bz2.compress(cleaned_bytes, compresslevel=9)
                fname = "greenroute_optimized.log.bz2"
            else:
                payload = gzip.compress(cleaned_bytes, compresslevel=9)
                fname = "greenroute_optimized.log.gz"

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        global LAST_STATE
        parsed = urlparse(self.path)
        path = parsed.path

        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(raw_body)
        except Exception:
            body = {}

        if path == "/api/generate-sample":
            lines = min(max(int(body.get("lines", 5000)), 500), 20000)
            sample_text = generate_sample_logs(lines)
            res = self._process_optimization(sample_text, body)
            self.send_json(res)

        elif path == "/api/optimize":
            log_text = body.get("log_text", "")
            if not log_text.strip():
                self.send_json({"error": "Empty log content provided"}, status_code=400)
                return
            res = self._process_optimization(log_text, body)
            self.send_json(res)

        elif path == "/api/certificate":
            if not LAST_STATE:
                self.send_error(400, "No audit data available. Please run optimization first.")
                return
            html = generate_esg_certificate_html(LAST_STATE)
            body_bytes = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body_bytes)))
            self.end_headers()
            self.wfile.write(body_bytes)

        else:
            self.send_error(404, "Not Found")

    def _process_optimization(self, text: str, options: dict) -> dict:
        global LAST_STATE
        cleaner = LogCleaner(
            filter_healthchecks=options.get("filter_healthchecks", True),
            dedup_repeats=options.get("dedup_repeats", True),
            mask_pii=options.get("mask_pii", True),
            normalize_user_agents=options.get("normalize_user_agents", True),
        )
        clean_res = cleaner.clean_text(text)
        comp_res = Compressor.compress_all(text, clean_res["cleaned_text"])
        analytics = LogAnalyzer.analyze(text)

        engine = CarbonEngine(
            region_key=options.get("region", "us-east-1"),
            storage_type=options.get("storage_type", "ssd"),
        )
        best_size = comp_res["best_codec"]["size_bytes"]
        raw_size = len(text.encode("utf-8"))
        fleet_scale = float(options.get("fleet_daily_gb", 50.0))

        savings = engine.calculate_savings(raw_size, best_size, fleet_daily_gb=fleet_scale)

        LAST_STATE = {
            "cleaned_text": clean_res["cleaned_text"],
            "cleaner_stats": clean_res["stats"],
            "carbon_savings": savings,
            "benchmarks": comp_res["benchmarks"],
            "best_codec": comp_res["best_codec"],
            "analytics": analytics,
            "raw_preview": clean_res["raw_preview"],
            "cleaned_preview": clean_res["cleaned_preview"],
        }
        return LAST_STATE


# ======================================================================================
# 8. CLI & ENTRYPOINT CONTROLLER
# ======================================================================================

def run_tests():
    print("Testing GreenRoute Standalone Engine...")
    engine = CarbonEngine(region_key="us-east-1")
    sav = engine.calculate_savings(1_000_000, 100_000, fleet_daily_gb=50)
    assert sav["bytes"]["reduction_percentage"] == 90.0, "Math error"
    print("  ✓ CarbonEngine calculation OK")

    cleaner = LogCleaner()
    c_res = cleaner.clean_text('127.0.0.1 - - [26/Sep/2026:12:00:00 +0000] "GET /healthz HTTP/1.1" 200 12 "-" "kube-probe"\n10.0.0.1 - - [26/Sep/2026:12:00:01 +0000] "GET /api HTTP/1.1" 200 50 "-" "curl"')
    assert c_res["stats"]["healthchecks_filtered"] == 1
    assert c_res["stats"]["clean_lines_output"] == 1
    print("  ✓ LogCleaner health check filter OK")

    comp = Compressor.compress_all("test " * 500, "test " * 100)
    assert len(comp["benchmarks"]) >= 5
    print("  ✓ Multi-codec compressor OK")

    html = generate_esg_certificate_html({"carbon_savings": sav, "cleaner_stats": c_res["stats"]})
    assert "Certificate of Carbon Reduction" in html
    print("  ✓ ESG Certificate generator OK")

    print("\n🎉 ALL EMBEDDED SELF-TESTS PASSED (100% OK)!\n")


def run_cli_optimize(file_path: str, region: str = "us-east-1"):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    print(f"\n🌱 GreenRoute CLI: Optimizing {file_path}...")
    cleaner = LogCleaner()
    clean_res = cleaner.clean_text(content)
    comp_res = Compressor.compress_all(content, clean_res["cleaned_text"])
    best = comp_res["best_codec"]

    engine = CarbonEngine(region_key=region)
    raw_bytes = len(content.encode("utf-8"))
    savings = engine.calculate_savings(raw_bytes, best["size_bytes"])

    print("\n" + "=" * 60)
    print("                   GREENROUTE SUMMARY")
    print("=" * 60)
    print(f"  Original Size:    {human_bytes(raw_bytes)}")
    print(f"  Optimized Size:   {human_bytes(best['size_bytes'])} ({best['name']})")
    print(f"  Space Salvaged:   {savings['bytes']['saved_human']} (-{savings['bytes']['reduction_percentage']}%)")
    print("-" * 60)
    print(f"  ⚡ Energy Saved:   {savings['energy']['kwh_saved_formatted']}")
    print(f"  🌍 CO2e Avoided:   {savings['emissions']['total_co2_formatted']}")
    print(f"  💵 Annual Cloud:   ${savings['financial']['annual_cost_saved_usd']:.2f}")
    print(f"  📱 Phone Charges:  {savings['equivalencies']['smartphones_charged']:,}")
    print("=" * 60 + "\n")


def launch_gui(host: str = "127.0.0.1", port: int = 8080):
    server = HTTPServer((host, port), GreenRouteHandler)
    url = f"http://{host}:{port}"
    print("\n" + "=" * 65)
    print("  🌱 GreenRoute — Sustainable Server Log Optimizer")
    print("  Hackathon Edition • Standalone Single-File Engine")
    print(f"  👉 Dashboard live at: {url}")
    print("=" * 65 + "\n")

    def _open():
        time.sleep(1.0)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down GreenRoute...")
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description="GreenRoute: Standalone Server Log Optimizer")
    subparsers = parser.add_subparsers(dest="cmd")

    # GUI
    gui_p = subparsers.add_parser("gui", help="Launch Web GUI")
    gui_p.add_argument("--port", type=int, default=8080)

    # CLI
    cli_p = subparsers.add_parser("cli", help="Optimize file via CLI")
    cli_p.add_argument("file", help="Path to log file")
    cli_p.add_argument("--region", default="us-east-1")

    # Sample
    sample_p = subparsers.add_parser("sample", help="Generate sample log")
    sample_p.add_argument("-n", "--lines", type=int, default=5000)
    sample_p.add_argument("-o", "--output", default="sample.log")

    # Test
    subparsers.add_parser("test", help="Run embedded self-tests")

    args = parser.parse_args()

    if args.cmd == "cli":
        run_cli_optimize(args.file, args.region)
    elif args.cmd == "sample":
        data = generate_sample_logs(args.lines)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"✅ Generated {args.lines} lines in {args.output} ({human_bytes(len(data.encode('utf-8')))})")
    elif args.cmd == "test":
        run_tests()
    else:
        # Default action: launch GUI
        port = getattr(args, "port", 8080)
        launch_gui(port=port)


if __name__ == "__main__":
    main()
