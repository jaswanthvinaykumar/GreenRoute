"""
GreenRoute Multi-Algorithm Compression & Benchmarking Engine
Compares raw logs vs cleaned logs across Gzip, Bzip2, and LZMA/XZ.
"""

import gzip
import bz2
import lzma
import time
from typing import Dict, Any, List


class Compressor:
    @staticmethod
    def compress_all(raw_content: str, cleaned_content: str) -> Dict[str, Any]:
        """
        Run multi-codec compression benchmarks on raw vs cleaned content.
        Returns detailed stats for each codec: size, ratio, duration, throughput.
        """
        raw_bytes = raw_content.encode("utf-8")
        cleaned_bytes = cleaned_content.encode("utf-8")

        raw_size = len(raw_bytes)
        cleaned_size = len(cleaned_bytes)

        benchmarks: List[Dict[str, Any]] = []

        # 1. Baseline: Raw Uncompressed
        benchmarks.append({
            "id": "raw",
            "name": "Raw Uncompressed",
            "codec": "None",
            "size_bytes": raw_size,
            "reduction_pct": 0.0,
            "compression_ratio": 1.0,
            "duration_ms": 0.0,
            "throughput_mb_s": 0.0,
            "is_baseline": True,
            "tag": "Worst Carbon Impact"
        })

        # 2. Cleaned Uncompressed (No codec, pure noise reduction)
        clean_reduction = ((raw_size - cleaned_size) / raw_size * 100.0) if raw_size > 0 else 0.0
        benchmarks.append({
            "id": "cleaned_raw",
            "name": "GreenRoute Cleaned (Raw)",
            "codec": "None",
            "size_bytes": cleaned_size,
            "reduction_pct": round(clean_reduction, 2),
            "compression_ratio": round(raw_size / cleaned_size, 2) if cleaned_size > 0 else 1.0,
            "duration_ms": 0.0,
            "throughput_mb_s": 0.0,
            "is_baseline": False,
            "tag": "Noise-Free Plaintext"
        })

        # 3. Raw Gzip (Standard industry baseline)
        t0 = time.perf_counter()
        raw_gz = gzip.compress(raw_bytes, compresslevel=6)
        gz_time = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "raw_gzip",
            "name": "Standard Gzip (Raw)",
            "codec": "gzip-6",
            "size_bytes": len(raw_gz),
            "reduction_pct": round(((raw_size - len(raw_gz)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "compression_ratio": round(raw_size / len(raw_gz), 2) if len(raw_gz) > 0 else 1.0,
            "duration_ms": round(gz_time, 2),
            "throughput_mb_s": round((raw_size / (1024 * 1024)) / (gz_time / 1000.0), 2) if gz_time > 0 else 0.0,
            "is_baseline": False,
            "tag": "Standard Cloud Baseline"
        })

        # 4. GreenRoute Cleaned + Gzip Level 9
        t0 = time.perf_counter()
        clean_gz = gzip.compress(cleaned_bytes, compresslevel=9)
        clean_gz_time = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "green_gzip",
            "name": "GreenRoute + Gzip-9",
            "codec": "gzip-9",
            "size_bytes": len(clean_gz),
            "reduction_pct": round(((raw_size - len(clean_gz)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "compression_ratio": round(raw_size / len(clean_gz), 2) if len(clean_gz) > 0 else 1.0,
            "duration_ms": round(clean_gz_time, 2),
            "throughput_mb_s": round((cleaned_size / (1024 * 1024)) / (clean_gz_time / 1000.0), 2) if clean_gz_time > 0 else 0.0,
            "is_baseline": False,
            "tag": "Fast & High Efficiency"
        })

        # 5. GreenRoute Cleaned + Bzip2
        t0 = time.perf_counter()
        clean_bz2 = bz2.compress(cleaned_bytes, compresslevel=9)
        clean_bz2_time = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "green_bz2",
            "name": "GreenRoute + Bzip2-9",
            "codec": "bzip2-9",
            "size_bytes": len(clean_bz2),
            "reduction_pct": round(((raw_size - len(clean_bz2)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "compression_ratio": round(raw_size / len(clean_bz2), 2) if len(clean_bz2) > 0 else 1.0,
            "duration_ms": round(clean_bz2_time, 2),
            "throughput_mb_s": round((cleaned_size / (1024 * 1024)) / (clean_bz2_time / 1000.0), 2) if clean_bz2_time > 0 else 0.0,
            "is_baseline": False,
            "tag": "Ultra Dense Text"
        })

        # 6. GreenRoute Cleaned + LZMA / XZ (Maximum Density)
        t0 = time.perf_counter()
        clean_lzma = lzma.compress(cleaned_bytes, preset=9)
        clean_lzma_time = (time.perf_counter() - t0) * 1000.0
        benchmarks.append({
            "id": "green_lzma",
            "name": "GreenRoute Max (LZMA/XZ)",
            "codec": "lzma-9",
            "size_bytes": len(clean_lzma),
            "reduction_pct": round(((raw_size - len(clean_lzma)) / raw_size * 100.0), 2) if raw_size > 0 else 0.0,
            "compression_ratio": round(raw_size / len(clean_lzma), 2) if len(clean_lzma) > 0 else 1.0,
            "duration_ms": round(clean_lzma_time, 2),
            "throughput_mb_s": round((cleaned_size / (1024 * 1024)) / (clean_lzma_time / 1000.0), 2) if clean_lzma_time > 0 else 0.0,
            "is_baseline": False,
            "tag": "Maximum Green Footprint",
            "is_recommended": True
        })

        # Sort or find best
        best_codec = min(benchmarks, key=lambda b: b["size_bytes"])

        return {
            "benchmarks": benchmarks,
            "best_codec": best_codec,
            "compressed_payloads": {
                "gzip": clean_gz,
                "bz2": clean_bz2,
                "lzma": clean_lzma,
            }
        }
