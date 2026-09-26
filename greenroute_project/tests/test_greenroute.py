"""
GreenRoute Automated Test Suite
Verifies Carbon Engine, Log Cleaner, Compressor, Analyzer, and Report Generator.
"""

import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from greenroute.carbon_engine import CarbonEngine, human_bytes, REGIONAL_PROFILES
from greenroute.cleaner import LogCleaner
from greenroute.compressor import Compressor
from greenroute.analyzer import LogAnalyzer
from greenroute.generator import generate_sample_logs
from greenroute.report import generate_esg_certificate_html


class TestCarbonEngine(unittest.TestCase):
    def test_carbon_math_positive_savings(self):
        engine = CarbonEngine(region_key="us-east-1", storage_type="ssd", replication_factor=3)
        res = engine.calculate_savings(original_bytes=100_000_000, optimized_bytes=10_000_000)

        # 90% reduction
        self.assertEqual(res["bytes"]["reduction_percentage"], 90.0)
        self.assertGreater(res["energy"]["kwh_saved"], 0)
        self.assertGreater(res["emissions"]["total_kg_co2_saved"], 0)
        self.assertGreater(res["equivalencies"]["smartphones_charged"], 0)

    def test_regional_profiles(self):
        engine_us = CarbonEngine(region_key="us-east-1")
        engine_se = CarbonEngine(region_key="eu-north-1")
        res_us = engine_us.calculate_savings(100_000_000, 10_000_000)
        res_se = engine_se.calculate_savings(100_000_000, 10_000_000)

        # Sweden grid has ~24.6 gCO2/kWh vs US East ~379 gCO2/kWh
        self.assertGreater(res_us["emissions"]["operational_kg_co2"], res_se["emissions"]["operational_kg_co2"])

    def test_human_bytes(self):
        self.assertEqual(human_bytes(0), "0 B")
        self.assertEqual(human_bytes(1024), "1.00 KB")
        self.assertEqual(human_bytes(1024 * 1024), "1.00 MB")


class TestLogCleaner(unittest.TestCase):
    def test_healthcheck_filter(self):
        cleaner = LogCleaner(filter_healthchecks=True)
        raw = (
            '127.0.0.1 - - [26/Sep/2026:14:00:00 +0000] "GET /healthz HTTP/1.1" 200 12 "-" "kube-probe/1.28"\n'
            '10.0.0.1 - - [26/Sep/2026:14:00:01 +0000] "GET /api/v1/users HTTP/1.1" 200 450 "-" "curl/8.4.0"'
        )
        res = cleaner.clean_text(raw)
        self.assertEqual(res["stats"]["healthchecks_filtered"], 1)
        self.assertEqual(res["stats"]["clean_lines_output"], 1)
        self.assertIn("/api/v1/users", res["cleaned_text"])
        self.assertNotIn("/healthz", res["cleaned_text"])

    def test_pii_masking(self):
        cleaner = LogCleaner(mask_pii=True)
        raw = '192.168.1.55 - - [26/Sep/2026:14:00:00 +0000] "POST /login?email=test@example.com HTTP/1.1" 200 12 "Bearer eyJhbGciOi.token" "Chrome"'
        res = cleaner.clean_text(raw)
        self.assertIn("192.168.1.0/24", res["cleaned_text"])
        self.assertIn("t***@example.com", res["cleaned_text"])
        self.assertIn("[REDACTED_JWT]", res["cleaned_text"])

    def test_error_cascade_dedup(self):
        cleaner = LogCleaner(dedup_repeats=True)
        raw = "\n".join([
            '2026-09-26 14:00:01 ERROR Connection to postgres failed: 5432'
            for _ in range(20)
        ])
        res = cleaner.clean_text(raw)
        self.assertIn("[DEDUP x20]", res["cleaned_text"])
        self.assertEqual(res["stats"]["clean_lines_output"], 1)


class TestCompressor(unittest.TestCase):
    def test_multi_codec_compression(self):
        raw = ("2026-09-26 GET /api/v1/search?q=greenroute 200 OK " * 500)
        cleaned = ("2026-09-26 GET /api/v1/search?q=greenroute 200 OK " * 100)
        res = Compressor.compress_all(raw, cleaned)
        benchmarks = res["benchmarks"]
        self.assertTrue(len(benchmarks) >= 5)

        best = res["best_codec"]
        self.assertIn(best["codec"], ["gzip-9", "bz2-9", "lzma-9"])
        self.assertLess(best["size_bytes"], len(raw.encode("utf-8")))


class TestLogAnalyzer(unittest.TestCase):
    def test_status_and_endpoint_analysis(self):
        raw = (
            '192.168.1.1 - - [26/Sep/2026:10:00:00 +0000] "GET /api/checkout HTTP/1.1" 200 500\n'
            '192.168.1.2 - - [26/Sep/2026:10:00:01 +0000] "GET /missing HTTP/1.1" 404 120\n'
            '192.168.1.3 - - [26/Sep/2026:10:00:02 +0000] "POST /pay HTTP/1.1" 500 80'
        )
        res = LogAnalyzer.analyze(raw)
        self.assertEqual(res["status_groups"]["2xx_success"], 1)
        self.assertEqual(res["status_groups"]["4xx_client_err"], 1)
        self.assertEqual(res["status_groups"]["5xx_server_err"], 1)
        self.assertEqual(len(res["top_endpoints"]), 3)


class TestESGReport(unittest.TestCase):
    def test_esg_certificate_html(self):
        engine = CarbonEngine()
        savings = engine.calculate_savings(1_000_000, 100_000)
        data = {
            "carbon_savings": savings,
            "cleaner_stats": {"healthchecks_filtered": 50, "repeated_lines_collapsed": 20, "pii_instances_masked": 10}
        }
        html = generate_esg_certificate_html(data, "Acme Tech", "Main Gateway")
        self.assertIn("Certificate of Carbon Reduction", html)
        self.assertIn("Acme Tech", html)
        self.assertIn("GR-", html)


if __name__ == "__main__":
    unittest.main()
