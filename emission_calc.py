#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omission Engine Core Module
---------------------------
Scope 1 + 2 Carbon Estimation for Non-Boiler Enterprises
哲學：一鍵生成 ≠ 粗糙估算；以 80/20 法則鎖定主要排放。
Author: 翻滾索徑有限公司 Rolling Paths Co.
Version: 1.0
"""

from dataclasses import dataclass
from typing import Optional, Literal

# === 預設係數 ===
EF_GRID = 0.474    # Taipower kg CO2/kWh
EF_GASOLINE = 2.3  # kg CO2/L
EF_DIESEL = 2.6
DEFAULT_CAR_KM_PER_YEAR = 15000
DEFAULT_CAR_KM_PER_L = 10
CAR_T_CO2E_PER_YEAR = (DEFAULT_CAR_KM_PER_YEAR / DEFAULT_CAR_KM_PER_L) * EF_GASOLINE / 1000  # ~3.45
BIKE_EQ = 0.5
EF_WATER_T_PER_M3 = 0.0004
EF_WASTE_T_PER_TON = 0.33


@dataclass
class Inputs:
    mode: Literal["quick", "detail"] = "quick"
    monthly_bill_ntd: Optional[float] = None
    price_per_kwh_ntd: float = 4.4
    annual_kwh: Optional[float] = None
    car_count: float = 0.0
    motorcycles: float = 0.0
    gasoline_liters_year: Optional[float] = None
    diesel_liters_year: Optional[float] = None
    refrigerant_leak_kg: float = 0.0
    refrigerant_gwp: float = 1000.0
    include_scope3: bool = False
    water_m3_year: float = 0.0
    waste_ton_year: float = 0.0
    use_rule_of_thumb: bool = False


def compute_scope2(annual_kwh, monthly_bill, price_per_kwh):
    if annual_kwh:
        return annual_kwh * EF_GRID / 1000
    if monthly_bill:
        annual_kwh = (monthly_bill / price_per_kwh) * 12
        return annual_kwh * EF_GRID / 1000
    return 0.0


def compute_scope1_vehicle(car, mc, gas_liters, diesel_liters):
    if gas_liters or diesel_liters:
        return (gas_liters or 0) * EF_GASOLINE / 1000 + (diesel_liters or 0) * EF_DIESEL / 1000
    car_equiv = car + mc * BIKE_EQ
    return car_equiv * CAR_T_CO2E_PER_YEAR


def compute_scope1_refrigerant(leak_kg, gwp):
    return leak_kg * gwp / 1000


def compute_minor_scope3(water, waste):
    return water * EF_WATER_T_PER_M3 + waste * EF_WASTE_T_PER_TON


def estimate(inputs: Inputs):
    s2 = compute_scope2(inputs.annual_kwh, inputs.monthly_bill_ntd, inputs.price_per_kwh_ntd)
    s1v = compute_scope1_vehicle(inputs.car_count, inputs.motorcycles, inputs.gasoline_liters_year, inputs.diesel_liters_year)
    s1r = compute_scope1_refrigerant(inputs.refrigerant_leak_kg, inputs.refrigerant_gwp)
    s1 = s1v + s1r
    total = s1 + s2

    if inputs.use_rule_of_thumb and s2 > 0:
        total = s2 * 1.1
        s1 = total - s2
        s1v = s1 * 0.9
        s1r = s1 * 0.1

    share_s2 = s2 / total * 100 if total else 0
    share_s1v = s1v / total * 100 if total else 0
    share_s1r = s1r / total * 100 if total else 0
    s3_minor = compute_minor_scope3(inputs.water_m3_year, inputs.waste_ton_year) if inputs.include_scope3 else 0

    return {
        "Scope2_電力": round(s2, 2),
        "Scope1_車輛": round(s1v, 2),
        "Scope1_冷媒": round(s1r, 2),
        "Scope1_合計": round(s1, 2),
        "總排放_S1S2": round(total, 2),
        "占比(%)": {"電力": round(share_s2, 1), "車輛": round(share_s1v, 1), "冷媒": round(share_s1r, 1)},
        "Scope3_小項": round(s3_minor, 2),
    }
