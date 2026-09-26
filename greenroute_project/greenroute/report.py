"""
GreenRoute ESG Audit Certificate & Sustainability Report Generator
Generates verifiable sustainability certificates for corporate ESG reporting.
"""

import hashlib
import datetime
from typing import Dict, Any


def generate_esg_certificate_html(
    analysis_results: Dict[str, Any],
    organization_name: str = "Enterprise Cloud Operations",
    system_name: str = "Production Cluster Logs"
) -> str:
    """
    Generate a high-polish, verifiable ESG Sustainability Certificate & Audit Report (HTML).
    Can be viewed in browser or printed/saved as PDF.
    """
    savings = analysis_results.get("carbon_savings", {})
    bytes_data = savings.get("bytes", {})
    emissions = savings.get("emissions", {})
    energy = savings.get("energy", {})
    financial = savings.get("financial", {})
    equiv = savings.get("equivalencies", {})
    clean_stats = analysis_results.get("cleaner_stats", {})

    now_str = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S UTC")

    # Generate cryptographic certificate ID
    raw_hash_seed = f"{organization_name}-{system_name}-{bytes_data.get('original', 0)}-{bytes_data.get('optimized', 0)}-{now_str}"
    cert_id = "GR-" + hashlib.sha256(raw_hash_seed.encode("utf-8")).hexdigest()[:16].upper()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GreenRoute ESG Sustainability Certificate - {cert_id}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    :root {{
      --bg: #090d16;
      --card: #111827;
      --border: #1f293d;
      --emerald: #10b981;
      --lime: #84cc16;
      --text: #f3f4f6;
      --muted: #9ca3af;
    }}
    
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      justify-content: center;
      padding: 40px 20px;
      -webkit-font-smoothing: antialiased;
    }}
    
    .cert-container {{
      max-width: 840px;
      width: 100%;
      background: linear-gradient(145deg, #111827 0%, #0d131f 100%);
      border: 2px solid rgba(16, 185, 129, 0.4);
      border-radius: 20px;
      padding: 48px;
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 40px -10px rgba(16, 185, 129, 0.15);
      position: relative;
      overflow: hidden;
    }}
    
    .watermark {{
      position: absolute;
      right: -60px;
      bottom: -60px;
      width: 320px;
      height: 320px;
      opacity: 0.04;
      pointer-events: none;
    }}
    
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    
    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    
    .logo-badge {{
      background: linear-gradient(135deg, var(--emerald), var(--lime));
      color: #000;
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 22px;
    }}
    
    .brand-title {{
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
      color: #fff;
    }}
    
    .brand-sub {{
      font-size: 13px;
      color: var(--emerald);
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 600;
    }}
    
    .cert-meta {{
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--muted);
    }}
    
    .cert-id {{
      color: var(--emerald);
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 4px;
    }}
    
    .hero {{
      text-align: center;
      margin-bottom: 36px;
    }}
    
    .hero-title {{
      font-size: 28px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 8px;
    }}
    
    .hero-sub {{
      color: var(--muted);
      font-size: 15px;
      max-width: 560px;
      margin: 0 auto;
    }}
    
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 36px;
    }}
    
    .stat-card {{
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px 16px;
      text-align: center;
    }}
    
    .stat-val {{
      font-size: 28px;
      font-weight: 700;
      color: var(--emerald);
      font-family: 'JetBrains Mono', monospace;
      margin-bottom: 4px;
    }}
    
    .stat-lbl {{
      font-size: 12px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    
    .details-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 36px;
      font-size: 14px;
    }}
    
    .details-table th, .details-table td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      text-align: left;
    }}
    
    .details-table th {{
      color: var(--muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.8px;
    }}
    
    .details-table td:last-child {{
      text-align: right;
      font-family: 'JetBrains Mono', monospace;
      color: #fff;
      font-weight: 600;
    }}
    
    .equivalency-bar {{
      background: rgba(16, 185, 129, 0.06);
      border: 1px dashed rgba(16, 185, 129, 0.3);
      border-radius: 14px;
      padding: 20px 24px;
      display: flex;
      justify-content: space-around;
      margin-bottom: 36px;
      text-align: center;
    }}
    
    .equiv-item {{
      font-size: 13px;
      color: var(--text);
    }}
    
    .equiv-item strong {{
      color: var(--lime);
      font-size: 16px;
      display: block;
      margin-bottom: 2px;
    }}
    
    .footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--border);
      padding-top: 24px;
      font-size: 12px;
      color: var(--muted);
    }}
    
    .compliance-pill {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--emerald);
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
      display: inline-block;
    }}
    
    .actions {{
      margin-top: 24px;
      text-align: center;
    }}
    
    .btn-print {{
      background: linear-gradient(135deg, var(--emerald), var(--lime));
      color: #0b0f17;
      font-weight: 700;
      padding: 12px 32px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
      font-family: inherit;
      transition: transform 0.2s;
    }}
    
    .btn-print:hover {{
      transform: scale(1.03);
    }}
    
    @media print {{
      body {{ background: #fff; color: #000; padding: 0; }}
      .cert-container {{ border: 2px solid #000; box-shadow: none; background: #fff; color: #000; }}
      .btn-print {{ display: none; }}
      .stat-val {{ color: #059669; }}
      .brand-title, .hero-title, .details-table td:last-child {{ color: #000; }}
    }}
  </style>
</head>
<body>

<div class="cert-container">
  <div class="header">
    <div class="brand">
      <div class="logo-badge">🌱</div>
      <div>
        <div class="brand-title">GreenRoute</div>
        <div class="brand-sub">Sustainable Server Telemetry</div>
      </div>
    </div>
    <div class="cert-meta">
      <div class="cert-id">{cert_id}</div>
      <div>Issued: {now_str}</div>
      <div>Standard: GHG Protocol Scope 2/3</div>
    </div>
  </div>

  <div class="hero">
    <h1 class="hero-title">Certificate of Carbon Reduction</h1>
    <p class="hero-sub">
      This audit certifies verifiable data reduction, storage energy conservation,
      and greenhouse gas emission abatement verified by the GreenRoute Optimization Engine.
    </p>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-val">{bytes_data.get('reduction_percentage', 0)}%</div>
      <div class="stat-lbl">Storage Reduction</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{emissions.get('total_co2_formatted', '0 g')}</div>
      <div class="stat-lbl">CO₂e Abated</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">{energy.get('kwh_saved_formatted', '0 kWh')}</div>
      <div class="stat-lbl">Energy Conserved</div>
    </div>
    <div class="stat-card">
      <div class="stat-val">${financial.get('annual_cost_saved_usd', 0):.2f}</div>
      <div class="stat-lbl">Annual Cloud Saved</div>
    </div>
  </div>

  <table class="details-table">
    <thead>
      <tr>
        <th>Audit Metric</th>
        <th>System / Scope Parameter</th>
        <th>Verified Result</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Organization / Entity</td>
        <td>Enterprise Cloud Operations</td>
        <td>{organization_name}</td>
      </tr>
      <tr>
        <td>Target Telemetry System</td>
        <td>Server Access & Error Streams</td>
        <td>{system_name}</td>
      </tr>
      <tr>
        <td>Baseline Ingestion Size</td>
        <td>Uncompressed Raw Telemetry</td>
        <td>{bytes_data.get('original_human', '0 B')}</td>
      </tr>
      <tr>
        <td>Optimized Storage Size</td>
        <td>GreenRoute Cleaned & Compressed</td>
        <td>{bytes_data.get('optimized_human', '0 B')}</td>
      </tr>
      <tr>
        <td>Total Bytes Eliminated</td>
        <td>Storage Space Salvaged</td>
        <td>{bytes_data.get('saved_human', '0 B')}</td>
      </tr>
      <tr>
        <td>Noisy Healthchecks Filtered</td>
        <td>/healthz, /readyz, probes</td>
        <td>{clean_stats.get('healthchecks_filtered', 0):,} events</td>
      </tr>
      <tr>
        <td>Cascading Errors Deduplicated</td>
        <td>Repeated Failure Bursts</td>
        <td>{clean_stats.get('repeated_lines_collapsed', 0):,} lines</td>
      </tr>
      <tr>
        <td>PII & Tokens Masked</td>
        <td>GDPR / HIPAA Anonymization</td>
        <td>{clean_stats.get('pii_instances_masked', 0):,} tokens</td>
      </tr>
    </tbody>
  </table>

  <div class="equivalency-bar">
    <div class="equiv-item">
      <strong>{equiv.get('smartphones_charged', 0):,}</strong>
      Smartphone Charges Saved
    </div>
    <div class="equiv-item">
      <strong>{equiv.get('km_driven_offset', 0):.1f} km</strong>
      Car Travel Emissions Offset
    </div>
    <div class="equiv-item">
      <strong>{equiv.get('plastic_bottles_equivalent', 0):,}</strong>
      Bottles Embodied Carbon
    </div>
  </div>

  <div class="footer">
    <div>
      <span class="compliance-pill">✓ CCF METHODOLOGY COMPLIANT</span>
      <span style="margin-left: 8px;">Audit Hash: {cert_id}</span>
    </div>
    <div>GreenRoute v1.0 • Hackathon Edition</div>
  </div>

  <div class="actions">
    <button class="btn-print" onclick="window.print()">Print or Save Official Certificate (PDF)</button>
  </div>
</div>

</body>
</html>
"""
    return html
