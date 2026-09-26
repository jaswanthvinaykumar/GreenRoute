#!/usr/bin/env python3
"""
GreenRoute - Sustainable Server Log Optimizer
Main Entrypoint: Run GUI server, CLI optimizer, or sample generator.
"""

import sys
import os
import argparse
import webbrowser
import threading
import time

# Ensure greenroute package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from greenroute.carbon_engine import CarbonEngine, human_bytes
from greenroute.cleaner import LogCleaner
from greenroute.compressor import Compressor
from greenroute.analyzer import LogAnalyzer
from greenroute.generator import generate_sample_logs
from greenroute.report import generate_esg_certificate_html


def launch_gui(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True):
    """Launch the Starlette + Uvicorn desktop web application."""
    from greenroute.server import run_server

    print("\n" + "=" * 65)
    print("  🌱 GreenRoute — Sustainable Server Log Optimizer")
    print("  Local Desktop Dashboard starting on:")
    print(f"  👉 http://{host}:{port}")
    print("=" * 65 + "\n")

    if open_browser:
        def _open():
            time.sleep(1.2)
            try:
                webbrowser.open(f"http://{host}:{port}")
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    run_server(host=host, port=port)


def run_cli_optimize(args):
    """Run CLI log optimization on a local file."""
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    print(f"\n🌱 GreenRoute CLI: Reading {args.file}...")
    with open(args.file, "r", encoding="utf-8", errors="replace") as f:
        raw_text = f.read()

    raw_bytes = len(raw_text.encode("utf-8"))
    print(f"📦 Input Log Size: {human_bytes(raw_bytes)} ({len(raw_text.splitlines())} lines)")

    # 1. Clean
    print("🧹 Cleaning telemetry (filtering healthchecks, deduplicating errors, masking PII)...")
    cleaner = LogCleaner(
        filter_healthchecks=not args.keep_healthchecks,
        dedup_repeats=not args.no_dedup,
        mask_pii=not args.no_mask_pii,
        normalize_user_agents=not args.no_norm_ua,
        strip_debug_logs=args.strip_debug,
    )
    clean_res = cleaner.clean_text(raw_text)
    clean_text = clean_res["cleaned_text"]

    # 2. Compress
    print("⚡ Benchmarking compression algorithms...")
    comp_res = Compressor.compress_all(raw_text, clean_text)
    best_codec = comp_res["best_codec"]

    # 3. Carbon calculations
    engine = CarbonEngine(
        region_key=args.region,
        storage_type=args.storage,
        pue=args.pue,
        replication_factor=args.replication,
        retention_days=args.retention,
    )
    savings = engine.calculate_savings(raw_bytes, best_codec["size_bytes"])

    # Output summary
    print("\n" + "=" * 60)
    print("                    OPTIMIZATION SUMMARY")
    print("=" * 60)
    print(f"  Baseline Size:       {human_bytes(raw_bytes)}")
    print(f"  Cleaned Plaintext:   {human_bytes(clean_res['stats']['clean_bytes_output'])}")
    print(f"  Best Codec:          {best_codec['name']}")
    print(f"  Optimized Size:      {human_bytes(best_codec['size_bytes'])}")
    print(f"  Space Salvaged:      {savings['bytes']['saved_human']} (-{savings['bytes']['reduction_percentage']}%)")
    print("-" * 60)
    print(f"  ⚡ Energy Conserved:  {savings['energy']['kwh_saved_formatted']}")
    print(f"  🌍 CO2e Averted:      {savings['emissions']['total_co2_formatted']}")
    print(f"  💵 Annual Cloud Save: ${savings['financial']['annual_cost_saved_usd']:.2f}")
    print(f"  📱 Phone Charges:    {savings['equivalencies']['smartphones_charged']:,} charges")
    print(f"  🚗 Car Offset:       {savings['equivalencies']['km_driven_offset']:.1f} km")
    print("=" * 60)

    # Save output if specified
    out_file = args.output
    if not out_file:
        out_file = args.file + ".green.xz"

    payload = comp_res["compressed_payloads"].get("lzma") or comp_res["compressed_payloads"].get("gzip")
    if payload:
        with open(out_file, "wb") as f:
            f.write(payload)
        print(f"\n✅ Saved optimized archive to: {out_file}")


def run_sample_gen(args):
    """Generate realistic server log sample."""
    print(f"🌱 Generating {args.lines} realistic server log lines...")
    sample = generate_sample_logs(num_lines=args.lines)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(sample)
    size = len(sample.encode("utf-8"))
    print(f"✅ Generated '{args.output}' ({human_bytes(size)}, {args.lines} lines)")


def main():
    parser = argparse.ArgumentParser(
        description="GreenRoute: Sustainable Server Log Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch interactive Desktop Web UI")
    gui_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default 127.0.0.1)")
    gui_parser.add_argument("--port", type=int, default=8080, help="Port (default 8080)")
    gui_parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")

    # CLI Optimize command
    cli_parser = subparsers.add_parser("optimize", help="Optimize a server log file via CLI")
    cli_parser.add_argument("file", help="Path to server log file (.log, .txt, .json)")
    cli_parser.add_argument("-o", "--output", help="Output compressed path")
    cli_parser.add_argument("--region", default="us-east-1", help="Datacenter region (us-east-1, eu-central-1, etc.)")
    cli_parser.add_argument("--storage", default="ssd", choices=["ssd", "hdd"], help="Storage medium")
    cli_parser.add_argument("--pue", type=float, default=1.20, help="Datacenter PUE (default 1.20)")
    cli_parser.add_argument("--replication", type=int, default=3, help="Storage replication factor (default 3)")
    cli_parser.add_argument("--retention", type=int, default=365, help="Log retention in days (default 365)")
    cli_parser.add_argument("--keep-healthchecks", action="store_true", help="Do not strip healthchecks")
    cli_parser.add_argument("--no-dedup", action="store_true", help="Do not deduplicate error cascades")
    cli_parser.add_argument("--no-mask-pii", action="store_true", help="Do not mask IPs/emails/tokens")
    cli_parser.add_argument("--no-norm-ua", action="store_true", help="Do not normalize user agents")
    cli_parser.add_argument("--strip-debug", action="store_true", help="Filter DEBUG/TRACE lines")

    # Sample generator command
    sample_parser = subparsers.add_parser("sample", help="Generate realistic sample server log")
    sample_parser.add_argument("-n", "--lines", type=int, default=5000, help="Number of log lines")
    sample_parser.add_argument("-o", "--output", default="samples/production_sample.log", help="Output path")

    args = parser.parse_args()

    if args.command == "optimize":
        run_cli_optimize(args)
    elif args.command == "sample":
        run_sample_gen(args)
    else:
        # Default action: launch GUI
        port = getattr(args, "port", 8080)
        host = getattr(args, "host", "127.0.0.1")
        no_browser = getattr(args, "no_browser", False)
        launch_gui(host=host, port=port, open_browser=not no_browser)


if __name__ == "__main__":
    main()
