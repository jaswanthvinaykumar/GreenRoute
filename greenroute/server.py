"""
GreenRoute Local Server & API
Fast, lightweight Starlette + Uvicorn server providing the local Desktop Web UI and REST API.
"""

import os
import json
import gzip
import bz2
import lzma
from typing import Dict, Any

from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from greenroute.carbon_engine import CarbonEngine, REGIONAL_PROFILES, STORAGE_SPECS
from greenroute.cleaner import LogCleaner
from greenroute.compressor import Compressor
from greenroute.analyzer import LogAnalyzer
from greenroute.generator import generate_sample_logs
from greenroute.report import generate_esg_certificate_html


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# In-memory store for last optimization run (for download & certificate generation)
LAST_RUN: Dict[str, Any] = {}


async def get_index(request: Request) -> HTMLResponse:
    """Serve the single-page application dashboard."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content)
    return HTMLResponse("<h1>GreenRoute: Static index.html not found.</h1>", status_code=404)


async def api_regions(request: Request) -> JSONResponse:
    """Return available carbon grid regions and storage specs."""
    regions = [
        {
            "key": k,
            "name": v.name,
            "grid_intensity": v.grid_intensity_g_per_kwh,
            "renewable_pct": v.renewable_percentage,
            "description": v.description,
        }
        for k, v in REGIONAL_PROFILES.items()
    ]
    return JSONResponse({
        "regions": regions,
        "storage_types": [
            {"key": k, "name": v["name"], "watts_per_tb": v["watts_per_tb"]}
            for k, v in STORAGE_SPECS.items()
        ]
    })


async def api_generate_sample(request: Request) -> JSONResponse:
    """Generate sample logs and optimize them."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    lines = int(body.get("lines", 3000))
    lines = min(max(lines, 500), 20000)

    sample_text = generate_sample_logs(num_lines=lines, error_cascade_size=int(lines * 0.1))

    # Run optimization on the generated sample
    return await _run_optimization_pipeline(sample_text, body)


async def api_optimize(request: Request) -> JSONResponse:
    """Process uploaded or submitted log text."""
    content_type = request.headers.get("content-type", "")

    log_text = ""
    options = {}

    if "multipart/form-data" in content_type:
        form = await request.form()
        upload_file = form.get("file")
        if upload_file:
            raw_bytes = await upload_file.read()
            # If uploaded file is gzipped, decompress first
            if upload_file.filename.endswith(".gz"):
                raw_bytes = gzip.decompress(raw_bytes)
            log_text = raw_bytes.decode("utf-8", errors="replace")

        # Parse options from form
        for key in form.keys():
            if key != "file":
                val = form.get(key)
                if val in ["true", "false"]:
                    options[key] = (val == "true")
                else:
                    options[key] = val
    else:
        try:
            body = await request.json()
            log_text = body.get("log_text", "")
            options = body
        except Exception:
            return JSONResponse({"error": "Invalid request body or JSON"}, status_code=400)

    if not log_text.strip():
        return JSONResponse({"error": "Empty log text provided"}, status_code=400)

    return await _run_optimization_pipeline(log_text, options)


async def _run_optimization_pipeline(log_text: str, options: Dict[str, Any]) -> JSONResponse:
    """Internal pipeline executing Cleaner, Compressor, Analyzer, and Carbon Engine."""
    global LAST_RUN

    # Cleaner configuration
    filter_hc = options.get("filter_healthchecks", True)
    if isinstance(filter_hc, str):
        filter_hc = (filter_hc.lower() == "true")

    dedup = options.get("dedup_repeats", True)
    if isinstance(dedup, str):
        dedup = (dedup.lower() == "true")

    mask_pii = options.get("mask_pii", True)
    if isinstance(mask_pii, str):
        mask_pii = (mask_pii.lower() == "true")

    norm_ua = options.get("normalize_user_agents", True)
    if isinstance(norm_ua, str):
        norm_ua = (norm_ua.lower() == "true")

    strip_debug = options.get("strip_debug", False)
    if isinstance(strip_debug, str):
        strip_debug = (strip_debug.lower() == "true")

    # 1. Clean Logs
    cleaner = LogCleaner(
        filter_healthchecks=filter_hc,
        dedup_repeats=dedup,
        mask_pii=mask_pii,
        normalize_user_agents=norm_ua,
        strip_debug_logs=strip_debug,
        max_preview_lines=200,
    )
    clean_result = cleaner.clean_text(log_text)

    # 2. Multi-Codec Benchmarks & Compression
    compression_result = Compressor.compress_all(log_text, clean_result["cleaned_text"])

    # 3. Log Analytics
    analytics_result = LogAnalyzer.analyze(log_text)

    # 4. Carbon Footprint & Energy Calculation
    region = options.get("region", "us-east-1")
    storage_type = options.get("storage_type", "ssd")
    pue = float(options.get("pue", 1.20))
    replication = int(options.get("replication_factor", 3))
    retention_days = int(options.get("retention_days", 365))

    engine = CarbonEngine(
        region_key=region,
        storage_type=storage_type,
        pue=pue,
        replication_factor=replication,
        retention_days=retention_days,
    )

    # Best compression size
    best_size = compression_result["best_codec"]["size_bytes"]
    raw_size = len(log_text.encode("utf-8"))

    fleet_daily_gb = float(options.get("fleet_daily_gb", 50.0))

    carbon_savings = engine.calculate_savings(
        original_bytes=raw_size,
        optimized_bytes=best_size,
        daily_log_volume_multiplier=fleet_daily_gb
    )

    # Store in memory for direct download and certificate generation
    LAST_RUN = {
        "raw_text": log_text,
        "cleaned_text": clean_result["cleaned_text"],
        "cleaner_stats": clean_result["stats"],
        "benchmarks": compression_result["benchmarks"],
        "best_codec": compression_result["best_codec"],
        "compressed_payloads": compression_result["compressed_payloads"],
        "analytics": analytics_result,
        "carbon_savings": carbon_savings,
        "options": options,
    }

    return JSONResponse({
        "success": True,
        "cleaner_stats": clean_result["stats"],
        "benchmarks": compression_result["benchmarks"],
        "best_codec": compression_result["best_codec"],
        "analytics": analytics_result,
        "carbon_savings": carbon_savings,
        "raw_preview": clean_result["raw_preview"],
        "cleaned_preview": clean_result["cleaned_preview"],
    })


async def api_download(request: Request) -> Response:
    """Download the optimized compressed file."""
    codec = request.path_params.get("codec", "gzip").lower()
    global LAST_RUN

    if not LAST_RUN or "cleaned_text" not in LAST_RUN:
        return Response("No optimization run available. Run optimize first.", status_code=404)

    cleaned_bytes = LAST_RUN["cleaned_text"].encode("utf-8")

    if codec == "gzip" or codec == "gz":
        data = gzip.compress(cleaned_bytes, compresslevel=9)
        filename = "greenroute_optimized.log.gz"
        media_type = "application/gzip"
    elif codec == "bz2":
        data = bz2.compress(cleaned_bytes, compresslevel=9)
        filename = "greenroute_optimized.log.bz2"
        media_type = "application/x-bzip2"
    elif codec == "lzma" or codec == "xz":
        data = lzma.compress(cleaned_bytes, preset=9)
        filename = "greenroute_optimized.log.xz"
        media_type = "application/x-xz"
    elif codec == "clean":
        data = cleaned_bytes
        filename = "greenroute_cleaned.log"
        media_type = "text/plain"
    else:
        return Response("Invalid codec specified", status_code=400)

    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


async def api_certificate(request: Request) -> HTMLResponse:
    """Generate and return the official HTML ESG certificate."""
    global LAST_RUN
    if not LAST_RUN:
        return HTMLResponse("<h3>No audit data available yet. Please optimize a log first.</h3>", status_code=400)

    try:
        body = await request.json()
    except Exception:
        body = {}

    org = body.get("organization_name", "Enterprise Cloud Operations")
    system = body.get("system_name", "Production Server Logs")

    html = generate_esg_certificate_html(LAST_RUN, organization_name=org, system_name=system)
    return HTMLResponse(html)


def create_app() -> Starlette:
    """Factory to create configured Starlette application."""
    routes = [
        Route("/", endpoint=get_index, methods=["GET"]),
        Route("/api/regions", endpoint=api_regions, methods=["GET"]),
        Route("/api/optimize", endpoint=api_optimize, methods=["POST"]),
        Route("/api/generate-sample", endpoint=api_generate_sample, methods=["POST"]),
        Route("/api/download/{codec}", endpoint=api_download, methods=["GET"]),
        Route("/api/certificate", endpoint=api_certificate, methods=["POST", "GET"]),
        Mount("/static", StaticFiles(directory=STATIC_DIR), name="static"),
    ]

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    return Starlette(debug=True, routes=routes, middleware=middleware)


def run_server(host: str = "127.0.0.1", port: int = 8080):
    """Run server with uvicorn."""
    import uvicorn
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")
