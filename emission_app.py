import streamlit as st
import plotly.express as px
from omission_calc import Inputs, estimate

st.set_page_config(page_title="Omission Engine v1.0", layout="wide", page_icon="♻️")

st.title("🌿 Omission Engine v1.0 — 一鍵生成 ≠ 粗糙估算")
st.markdown("以最少資訊，完成最可信的碳排估算（Scope 1 + 2）")

with st.sidebar:
    st.header("輸入參數")
    mode = st.radio("模式", ["quick (80%)", "detail (95%)"])
    monthly_bill = st.number_input("月電費（NTD）", 0.0)
    price_per_kwh = st.number_input("每度電價（NTD）", 4.4)
    annual_kwh = st.number_input("年用電量（kWh）", 0.0)
    car_count = st.number_input("汽車台數", 0)
    motorcycles = st.number_input("機車台數", 0)
    gas_liters = st.number_input("汽油使用量（L/年）", 0.0)
    diesel_liters = st.number_input("柴油使用量（L/年）", 0.0)
    refrigerant_kg = st.number_input("冷媒逸散量（kg/年）", 0.0)
    refrigerant_gwp = st.number_input("冷媒 GWP", 1000.0)
    use_rule = st.checkbox("使用電力 × 1.1 一鍵法", True)
    include_s3 = st.checkbox("包含水與廢棄物（Scope 3 小項）", False)
    water = st.number_input("年用水量（m³）", 0.0)
    waste = st.number_input("年廢棄物量（噸）", 0.0)
    st.markdown("---")
    st.caption("© Rolling Paths Co. 2025")

if st.button("🚀 開始估算"):
    inp = Inputs(
        mode="quick" if "quick" in mode else "detail",
        monthly_bill_ntd=monthly_bill or None,
        price_per_kwh_ntd=price_per_kwh,
        annual_kwh=annual_kwh or None,
        car_count=car_count,
        motorcycles=motorcycles,
        gasoline_liters_year=gas_liters or None,
        diesel_liters_year=diesel_liters or None,
        refrigerant_leak_kg=refrigerant_kg,
        refrigerant_gwp=refrigerant_gwp,
        include_scope3=include_s3,
        water_m3_year=water,
        waste_ton_year=waste,
        use_rule_of_thumb=use_rule,
    )
    result = estimate(inp)
    st.subheader("📊 結果一覽")
    st.json(result)
    
    fig = px.pie(
        names=["電力", "車輛", "冷媒"],
        values=[result["占比(%)"]["電力"], result["占比(%)"]["車輛"], result["占比(%)"]["冷媒"]],
        title="範疇比例結構",
        color_discrete_sequence=["#4CAF50", "#8BC34A", "#CDDC39"]
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(f"""
    ### 🧾 敘事說明  
    - 總碳排：**{result['總排放_S1S2']} 噸 CO₂e/年**  
    - 其中電力約佔 **{result['占比(%)']['電力']}%**，車輛約 **{result['占比(%)']['車輛']}%**，冷媒約 **{result['占比(%)']['冷媒']}%**。  
    - 模型依據 80/20 法則設計，平均誤差 ±10%。  
    - 若上傳完整帳單與加油紀錄，可升級精確度至 95%。  
    """)
