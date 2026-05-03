import streamlit as st
import pandas as pd
from weasyprint import HTML
import base64

# 세션 상태 초기화 (데이터 보존용)
if 'data' not in st.session_state:
    st.session_state.data = {}

st.set_page_config(page_title="상증세법 주식평가 시스템", layout="wide")

st.title("📊 비상장주식 가치평가 시스템")
st.markdown("---")

# 사이드바: 기본 정보
with st.sidebar:
    st.header("📌 기본 정보")
    comp_name = st.text_input("법인명", "가나다주식회사")
    base_date = st.date_input("평가기준일")
    total_shares = st.number_input("발행주식총수", min_value=1, value=10000)

# 메인 화면: 탭으로 시트 구분
tab1, tab2, tab3 = st.tabs(["📑 법인세/순손익액", "🏢 자산/부채(평가차액)", "🖨️ 결과 및 PDF"])

with tab1:
    st.subheader("최근 3개년 세무조정 및 순손익액")
    col1, col2, col3 = st.columns(3)
    years = ["2024(직전)", "2023", "2022"]
    profits = []
    
    for i, yr in enumerate([col1, col2, col3]):
        with yr:
            st.markdown(f"**{years[i]} 사업연도**")
            base = st.number_input(f"차감전이익", key=f"b{i}")
            plus = st.number_input(f"가산항목(+)", key=f"p{i}")
            minus = st.number_input(f"차감항목(-)", key=f"m{i}")
            tax = st.number_input(f"법인세결정세액", key=f"t{i}")
            adj_p = base + plus - minus - tax
            st.info(f"조정 순손익: {adj_p:,.0f}")
            profits.append(adj_p)

with tab2:
    st.subheader("재무상태표 및 평가차액명세서")
    items = ["토지", "건물", "유가증권", "기계/기타"]
    asset_data = {}
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**[자산 항목 평가]**")
        for item in items:
            c1, c2 = st.columns(2)
            with c1: b = st.number_input(f"{item} 장부가", key=f"ab{item}")
            with c2: e = st.number_input(f"{item} 평가가", key=f"ae{item}")
            asset_data[item] = e
            
    with col_b:
        st.write("**[부채 및 기타]**")
        liab = st.number_input("부채총계(퇴직급여 등 포함)", value=0)
        other_assets = st.number_input("기타 유동자산 합계", value=0)

with tab3:
    if st.button("🚀 최종 가치평가 실행"):
        # 1. 순손익가치 계산
        avg_profit = (profits[0]*3 + profits[1]*2 + profits[2]*1) / 6
        p_val = (avg_profit / 0.1) / total_shares
        
        # 2. 순자산가치 계산
        net_asset = (sum(asset_data.values()) + other_assets) - liab
        a_val = net_asset / total_shares
        
        # 3. 가중평균 및 하한선
        weighted = (p_val * 0.6) + (a_val * 0.4)
        final = max(weighted, a_val * 0.8)
        
        # 결과 대시보드
        c1, c2, c3 = st.columns(3)
        c1.metric("1주당 순손익가치", f"{int(p_val):,}원")
        c2.metric("1주당 순자산가치", f"{int(a_val):,}원")
        c3.metric("최종 평가가액", f"{int(final):,}원", delta="상증법 시가")
        
        # PDF 생성 로직 (생략 - 이전 코드와 동일하게 구현 가능)
        st.success("✅ 평가가 완료되었습니다. 하단 리포트를 확인하세요.")