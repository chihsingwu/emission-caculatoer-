# 🌿 Emission Calculator (排放計算引擎)

## 一鍵生成 ≠ 粗糙估算。Decisive AI for Carbon.

> **我們的信念 (Our Philosophy)：** 企業碳盤查的價值在於**決策**，而非**窮盡細節**。Emission Calculator 專注於 **80/20 法則**，鎖定範疇 1 (Scope 1) 與範疇 2 (Scope 2) 的主要排放源，以**極低的實施摩擦 (Zero-Friction)**，達成 **90% 以上**的**實務準確性**。

---

## 🎯 專案特色 (Key Features)

* **極簡主義計算核心 (Minimalist Core):** 程式碼模組化，核心計算邏輯清晰可見。
* **低摩擦部署 (Zero-Friction Deployment):** 基於 [Streamlit](https://streamlit.io/)，實現真正的**「一鍵運行」**和**「即時視覺化」**。
* **高彈性數據輸入 (Fluid Data Input):** 支援從**電費金額 (NTD)** 估算用電量，解決數據不完整問題。
* **在地化精確性 (Hyper-Local Accuracy):** 採用**臺電電網係數**，專為臺灣企業設計。

---

## 🚀 快速上手 (Quick Start)

讓使用者能立即體驗專案。

### 1. 先決條件 (Prerequisites)

確保您的環境已安裝 **Python 3.8+**。

### 2. 安裝 (Installation)

```bash
git clone [您的 GitHub URL]
cd emission-calculator
pip install -r requirements.txt  # 假設 requirements.txt 包含 streamlit, plotly
from emission_calc import Inputs, estimate

# 範例：年用電量 100,000 kWh，擁有 5 輛汽車
input_data = Inputs(annual_kwh=100000, car_count=5) 
result = estimate(input_data)
print(result)

# emission_config.py
# ---------------------------------------------
# 專用於儲存排放係數與預設值的配置檔案
# 確保程式碼核心邏輯與數據分離，易於維護和客製化。
# ---------------------------------------------

# === 預設排放係數 (Emission Factors) - 單位: kg CO2e / 單位量 ===

# EF_GRID: 臺電電網排放係數 (2023年最新版) [請在此處補充官方參考來源]
EF_GRID = 0.474    

# EF_GASOLINE: 汽油排放係數 (IPCC Tier 1 或當地標準)
EF_GASOLINE = 2.3  

# EF_DIESEL: 柴油排放係數
EF_DIESEL = 2.6

# EF_WATER_T_PER_M3: 年用水量 (Scope 3 小項) - 單位: 噸 CO2e / 立方公尺
EF_WATER_T_PER_M3 = 0.0004

# EF_WASTE_T_PER_TON: 年廢棄物量 (Scope 3 小項) - 單位: 噸 CO2e / 噸
EF_WASTE_T_PER_TON = 0.33


# === 預設行為參數 (Default Behavior Parameters) ===

# 預設每輛汽車年行駛公里數 (用於缺乏數據時的估算)
DEFAULT_CAR_KM_PER_YEAR = 15000

# 預設每公升汽油行駛公里數
DEFAULT_CAR_KM_PER_L = 10

# 機車對汽車的碳排等效比例 (用於缺乏數據時的估算)
BIKE_EQ = 0.5

# 預設每度電價 (NTD) - 用於從電費估算用電量
DEFAULT_PRICE_PER_KWH = 4.4

# emission_calc.py (更新內容)
# ---------------------------------------------
# 僅保留核心計算邏輯
# ---------------------------------------------

from dataclasses import dataclass
from typing import Optional, Literal
# *** 導入配置檔案中的係數和常數 ***
from emission_config import (
    EF_GRID, EF_GASOLINE, EF_DIESEL, 
    EF_WATER_T_PER_M3, EF_WASTE_T_PER_TON,
    DEFAULT_CAR_KM_PER_YEAR, DEFAULT_CAR_KM_PER_L, 
    BIKE_EQ, DEFAULT_PRICE_PER_KWH
)

# 使用常數計算車輛預設年碳排
CAR_T_CO2E_PER_YEAR = (DEFAULT_CAR_KM_PER_YEAR / DEFAULT_CAR_KM_PER_L) * EF_GASOLINE / 1000  


@dataclass
class Inputs:
    mode: Literal["quick", "detail"] = "quick"
    monthly_bill_ntd: Optional[float] = None
    # *** 這裡使用 DEFAULT_PRICE_PER_KWH 作為預設值，若沒有提供則使用配置檔中的值 ***
    price_per_kwh_ntd: float = DEFAULT_PRICE_PER_KWH 
    annual_kwh: Optional[float] = None
    # ... (其餘 Inputs 保持不變) ...
    # ...
    
# ... (compute_scope2, compute_scope1_vehicle, compute_minor_scope3, estimate 函數邏輯保持不變) ...

# *** 移除 compute_scope2 函數中 price_per_kwh_ntd 的硬編碼 4.4，改為使用參數或配置檔預設值 ***
def compute_scope2(annual_kwh, monthly_bill, price_per_kwh):
    if annual_kwh:
        return annual_kwh * EF_GRID / 1000
    if monthly_bill:
        # 使用 price_per_kwh 參數，該參數預設為 DEFAULT_PRICE_PER_KWH
        annual_kwh = (monthly_bill / price_per_kwh) * 12 
        return annual_kwh * EF_GRID / 1000
    return 0.0

# ... (其他函數保持不變) ...
# emission_app.py (關鍵行修正)
# ---------------------------------------------

# ... (檔案開頭導入) ...
import streamlit as st
import plotly.express as px
from emission_calc import Inputs, estimate
# *** 導入預設電價，用於 Streamlit 的預設值 ***
from emission_config import DEFAULT_PRICE_PER_KWH 

st.set_page_config(page_title="Emission Engine v1.0", layout="wide", page_icon="♻️")

# ... (側邊欄輸入參數) ...
with st.sidebar:
    # ...
    # *** 使用導入的 DEFAULT_PRICE_PER_KWH 作為預設值 ***
    price_per_kwh = st.number_input("每度電價（NTD）", DEFAULT_PRICE_PER_KWH) 
    # ...
