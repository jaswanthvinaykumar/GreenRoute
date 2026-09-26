"""
In-process ASGI direct routing test (Zero socket / 100% sandboxed).
Tests Starlette endpoints by calling the ASGI application interface directly.
"""

import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from greenroute.server import create_app

app = create_app()


async def asgi_request(app, method: str, path: str, body: bytes = b"", headers: dict = None):
    """Call ASGI app directly in-memory without networking."""
    if headers is None:
        headers = {}

    asgi_headers = [(k.lower().encode("latin1"), v.encode("latin1")) for k, v in headers.items()]
    scope = {
        "type": "http",
        "method": method.upper(),
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": asgi_headers,
    }

    body_sent = False
    response_started = False
    response_status = None
    response_headers = []
    response_body = bytearray()

    async def receive():
        nonlocal body_sent
        if not body_sent:
            body_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        nonlocal response_started, response_status, response_headers, response_body
        if message["type"] == "http.response.start":
            response_started = True
            response_status = message["status"]
            response_headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            response_body.extend(message.get("body", b""))

    await app(scope, receive, send)

    header_dict = {k.decode("latin1"): v.decode("latin1") for k, v in response_headers}
    return response_status, header_dict, bytes(response_body)


async def run_tests():
    print("1. In-process ASGI: Testing GET / ...")
    status, headers, body = await asgi_request(app, "GET", "/")
    assert status == 200, f"Expected 200, got {status}"
    assert b"GreenRoute" in body
    print(f"   ✓ GET / OK ({len(body)} bytes)")

    print("2. In-process ASGI: Testing GET /api/regions ...")
    status, headers, body = await asgi_request(app, "GET", "/api/regions")
    assert status == 200
    data = json.loads(body.decode("utf-8"))
    assert len(data["regions"]) >= 5
    print(f"   ✓ GET /api/regions OK ({len(data['regions'])} regions)")

    print("3. In-process ASGI: Testing POST /api/generate-sample ...")
    req_json = json.dumps({"lines": 500, "region": "us-east-1", "fleet_daily_gb": 50}).encode("utf-8")
    status, headers, body = await asgi_request(
        app, "POST", "/api/generate-sample",
        body=req_json,
        headers={"content-type": "application/json"}
    )
    assert status == 200, f"Status: {status}, Body: {body[:200]}"
    res_data = json.loads(body.decode("utf-8"))
    assert res_data["success"] is True
    assert res_data["carbon_savings"]["bytes"]["reduction_percentage"] > 70
    print(f"   ✓ POST /api/generate-sample OK (Reduction: {res_data['carbon_savings']['bytes']['reduction_percentage']}%)")

    print("4. In-process ASGI: Testing POST /api/certificate ...")
    cert_req = json.dumps({"organization_name": "Antigravity Cloud", "system_name": "Ingress-01"}).encode("utf-8")
    status, headers, body = await asgi_request(
        app, "POST", "/api/certificate",
        body=cert_req,
        headers={"content-type": "application/json"}
    )
    assert status == 200
    assert b"Certificate of Carbon Reduction" in body
    assert b"Antigravity Cloud" in body
    print(f"   ✓ POST /api/certificate OK ({len(body)} bytes)")

    print("5. In-process ASGI: Testing GET /api/download/xz ...")
    status, headers, body = await asgi_request(app, "GET", "/api/download/xz")
    assert status == 200
    assert len(body) > 0
    assert "attachment" in headers.get("content-disposition", "")
    print(f"   ✓ GET /api/download/xz OK ({len(body)} bytes)")

    print("\n🎉 ALL IN-PROCESS ASGI ROUTES PASS WITH 100% RELIABILITY!\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
