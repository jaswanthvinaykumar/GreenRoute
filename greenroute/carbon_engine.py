"""
GreenRoute Carbon Footprint & Energy Calculation Engine
Based on Cloud Carbon Footprint (CCF) & GHG Protocol Scope 2/Scope 3 standards.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CarbonProfile:
    name: str
    grid_intensity_g_per_kwh: float  # gCO2e per kWh
    renewable_percentage: float
    description: str


# Regional Carbon Intensity (gCO2e / kWh) - Updated based on standard cloud datacenter grid data
REGIONAL_PROFILES: Dict[str, CarbonProfile] = {
    "us-east-1": CarbonProfile(
        name="US East (N. Virginia)",
        grid_intensity_g_per_kwh=379.2,
        renewable_percentage=28.0,
        description="PJM Interconnection - Coal & Natural Gas dominant"
    ),
    "us-west-2": CarbonProfile(
        name="US West (Oregon)",
        grid_intensity_g_per_kwh=85.4,
        renewable_percentage=74.0,
        description="Northwest Power Pool - High Hydroelectric share"
    ),
    "eu-central-1": CarbonProfile(
        name="Europe (Frankfurt)",
        grid_intensity_g_per_kwh=338.0,
        renewable_percentage=52.0,
        description="German Energy Mix - Transitional grid"
    ),
    "eu-north-1": CarbonProfile(
        name="Europe (Stockholm, Sweden)",
        grid_intensity_g_per_kwh=24.6,
        renewable_percentage=98.0,
        description="Nordic Grid - 98% Carbon Free (Hydro & Nuclear)"
    ),
    "ap-south-1": CarbonProfile(
        name="Asia Pacific (Mumbai, India)",
        grid_intensity_g_per_kwh=660.0,
        renewable_percentage=22.0,
        description="Western Regional Grid - Coal dominant"
    ),
    "global-avg": CarbonProfile(
        name="Global Datacenter Average",
        grid_intensity_g_per_kwh=436.0,
        renewable_percentage=35.0,
        description="IEA Global Grid Average for Commercial Centers"
    ),
}

# Storage Power Consumption in Watts per Terabyte (Active/Idle weighted average)
# Source: Cloud Carbon Footprint Methodology (v2024), Dell PowerEdge Server Specs
STORAGE_SPECS = {
    "ssd": {
        "name": "Enterprise NVMe/SATA SSD",
        "watts_per_tb": 1.25,      # 1.25 Watts per TB
        "embodied_kg_per_tb_yr": 1.45  # Manufacturing & disposal amortized per TB-year
    },
    "hdd": {
        "name": "Enterprise SAS/SATA HDD (7200 RPM)",
        "watts_per_tb": 6.50,      # 6.50 Watts per TB
        "embodied_kg_per_tb_yr": 0.85
    }
}

# S3 / Cloud Storage Pricing ($ per GB / month standard tier)
CLOUD_STORAGE_PRICE_PER_GB_MONTH = 0.023


class CarbonEngine:
    def __init__(
        self,
        region_key: str = "us-east-1",
        storage_type: str = "ssd",
        pue: float = 1.20,             # Typical hyperscale PUE (AWS/GCP avg is ~1.15-1.25)
        replication_factor: int = 3,   # Standard multi-AZ redundancy (e.g. 3 copies)
        retention_days: int = 365,     # 1 year standard enterprise retention
    ):
        self.region_key = region_key if region_key in REGIONAL_PROFILES else "us-east-1"
        self.profile = REGIONAL_PROFILES[self.region_key]
        self.storage_type = storage_type if storage_type in STORAGE_SPECS else "ssd"
        self.storage = STORAGE_SPECS[self.storage_type]
        self.pue = max(1.0, float(pue))
        self.replication_factor = max(1, int(replication_factor))
        self.retention_days = max(1, int(retention_days))

    def calculate_savings(
        self,
        original_bytes: int,
        optimized_bytes: int,
        daily_log_volume_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate energy, carbon, and dollar savings for compressed/cleaned logs.
        daily_log_volume_multiplier: If this sample represents 1 hour or 1 day of logs,
        can project annual enterprise savings. Default 1.0 evaluates the exact bytes provided.
        """
        saved_bytes = max(0, original_bytes - optimized_bytes)
        reduction_percentage = (saved_bytes / original_bytes * 100.0) if original_bytes > 0 else 0.0

        # Convert to Terabytes (TB)
        saved_tb = saved_bytes / (1024 ** 4)
        original_tb = original_bytes / (1024 ** 4)
        optimized_tb = optimized_bytes / (1024 ** 4)

        # Apply multi-AZ storage replication
        effective_saved_tb = saved_tb * self.replication_factor

        # Annual energy calculation for storage (kWh)
        # Power (kW) = Watts / 1000
        # Energy (kWh) = Power (kW) * Hours * PUE
        hours_stored = (self.retention_days / 365.0) * 8760.0
        kw_per_tb = self.storage["watts_per_tb"] / 1000.0

        # Operational Energy Saved (kWh)
        operational_kwh_saved = effective_saved_tb * kw_per_tb * hours_stored * self.pue

        # Operational Carbon Saved (kg CO2e)
        operational_kg_co2_saved = (operational_kwh_saved * self.profile.grid_intensity_g_per_kwh) / 1000.0

        # Embodied Carbon Saved (kg CO2e) from reduced drive provisioning
        fraction_of_year = self.retention_days / 365.0
        embodied_kg_co2_saved = (
            effective_saved_tb * self.storage["embodied_kg_per_tb_yr"] * fraction_of_year
        )

        total_kg_co2_saved = operational_kg_co2_saved + embodied_kg_co2_saved

        # Cloud Cost Savings (USD)
        saved_gb = saved_bytes / (1024 ** 3)
        monthly_cost_saved = saved_gb * CLOUD_STORAGE_PRICE_PER_GB_MONTH * self.replication_factor
        annual_cost_saved = monthly_cost_saved * (self.retention_days / 30.4)

        # Real-World Equivalencies
        # 1 smartphone charge ~= 0.012 kWh (or ~5.2g CO2)
        smartphones_charged = max(1, int(round(operational_kwh_saved / 0.012))) if operational_kwh_saved > 0 else 0

        # 1 urban tree absorbs ~21.77 kg CO2 / year (~0.0596 kg / day)
        tree_years_offset = total_kg_co2_saved / 21.77 if total_kg_co2_saved > 0 else 0.0

        # 1 km driven in a standard internal combustion engine car ~= 0.170 kg CO2
        km_driven_offset = total_kg_co2_saved / 0.170 if total_kg_co2_saved > 0 else 0.0

        # Plastic water bottles saved equivalent (production of 1 PET bottle ~= 82.8g CO2)
        plastic_bottles_equivalent = max(1, int(round((total_kg_co2_saved * 1000) / 82.8))) if total_kg_co2_saved > 0 else 0

        # Scaled enterprise projection based on fleet volume (default 50 GB/day)
        fleet_daily_gb = float(daily_log_volume_multiplier) if daily_log_volume_multiplier > 1.0 else 50.0
        fleet_reduction_ratio = (saved_bytes / original_bytes) if original_bytes > 0 else 0.85
        fleet_daily_saved_bytes = (fleet_daily_gb * (1024 ** 3)) * fleet_reduction_ratio
        fleet_annual_saved_tb = ((fleet_daily_saved_bytes * 365.0) / (1024 ** 4)) * self.replication_factor

        fleet_annual_kwh = fleet_annual_saved_tb * kw_per_tb * 8760.0 * self.pue
        fleet_annual_co2_kg = (
            (fleet_annual_kwh * self.profile.grid_intensity_g_per_kwh / 1000.0)
            + (fleet_annual_saved_tb * self.storage["embodied_kg_per_tb_yr"])
        )
        fleet_annual_cost_usd = (
            (fleet_annual_saved_tb * 1024) * CLOUD_STORAGE_PRICE_PER_GB_MONTH
        )
        fleet_trees_offset = fleet_annual_co2_kg / 21.77
        fleet_car_km = fleet_annual_co2_kg / 0.170

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
                "region": self.profile.name,
                "region_key": self.region_key,
                "grid_intensity": f"{self.profile.grid_intensity_g_per_kwh} gCO2e/kWh",
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
                "total_g_co2_saved": round(total_kg_co2_saved * 1000.0, 2),
                "total_co2_formatted": f"{total_kg_co2_saved:.3f} kg CO2e"
                if total_kg_co2_saved >= 1.0
                else f"{(total_kg_co2_saved * 1000.0):.1f} g CO2e",
            },
            "financial": {
                "monthly_cost_saved_usd": round(monthly_cost_saved, 2),
                "annual_cost_saved_usd": round(annual_cost_saved, 2),
            },
            "equivalencies": {
                "smartphones_charged": smartphones_charged,
                "tree_years_offset": round(tree_years_offset, 2),
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
                "fleet_car_km": round(fleet_car_km, 1),
            }
        }


def human_bytes(size_bytes: int) -> str:
    """Format bytes into readable human format (KB, MB, GB, TB)."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"
