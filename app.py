import streamlit as st
import pandas as pd

st.set_page_config(page_title="상증세법 주식평가 시스템", layout="wide")

st.title("📊 비상장주식 가치평가 시스템 (실무 엑셀형)")
st.markdown("---")

# 1. 엑셀 계정과목 기본 세팅 (0원으로 초기화)
asset_accounts = [
    "현금및현금성자산", "매출채권", "재고자산", "기타유동자산", 
    "토지", "건물", "기계장치", "투자유가증권", "기타비유동자산"
]
liab_accounts = [
    "매입채무", "단기차입금", "미지급금", "기타유동부채", 
    "장기차입금", "퇴직급여충당부채", "기타비유동부채"
]

# 세션에 데이터 저장 (새로고침해도 날아가지 않음)
if 'assets' not in st.session_state:
    st.session_state.assets = pd.DataFrame({
        "계정과목": asset_accounts, 
        "장부가액": [0]*len(asset_accounts), 
        "평가가액": [0]*len(asset_accounts)
    })
if 'liabs' not in st.session_state:
    st.session_state.liabs = pd.DataFrame({
        "계정과목": liab_accounts, 
        "장부가액": [0]*len(liab_accounts), 
        "평가가액": [0]*len(liab_accounts)
    })

# 사이드바: 주식수 입력
with st.sidebar:
    st.header("📌 기본 정보")
    total_shares = st.number_input("발행주식총수 (주)", min_value=1, value=10000)

# 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["📑 1. 순손익액 입력", "🏢 2. 재무상태표(엑셀입력)", "🖨️ 3. 평가명세서 및 최종결과"])

# --- TAB 1: 순손익액 ---
with tab1:
    st.subheader("최근 3개년 순손익액")
    col1, col2, col3 = st.columns(3)
    profits = []
    years = ["2024(직전)", "2023", "2022"]
    
    for i, yr in enumerate([col1, col2, col3]):
        with yr:
            st.markdown(f"**{years[i]} 사업연도**")
            p = st.number_input(f"조정 순손익액 ({years[i]})", value=0, key=f"p{i}")
            profits.append(p)

# --- TAB 2: 재무상태표 엑셀 입력 ---
with tab2:
    st.subheader("재무상태표 및 평가가액 입력")
    st.info("💡 아래 표의 숫자를 엑셀처럼 더블클릭해서 직접 입력하세요. (평가가액을 입력하지 않으면 장부가액과 동일하게 취급됩니다)")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### [ 자 산 ]")
        # 엑셀처럼 직접 수정 가능한 데이터프레임
        edited_assets = st.data_editor(st.session_state.assets, use_container_width=True, hide_index=True)
        st.session_state.assets = edited_assets
        
    with col_b:
        st.markdown("#### [ 부 채 ]")
        edited_liabs = st.data_editor(st.session_state.liabs, use_container_width=True, hide_index=True)
        st.session_state.liabs = edited_liabs

# --- TAB 3: 평가차액명세서 및 자동검증 결과 ---
with tab3:
    st.subheader("검증 및 평가차액명세서")
    
    # 평가차액 자동 계산 로직
    df_a = st.session_state.assets.copy()
    # 평가가가 0이고 장부가가 0이 아니면, 평가가 입력을 안 한 것으로 간주해 장부가 적용 (실무 편의성)
    df_a['적용평가가'] = df_a.apply(lambda x: x['장부가액'] if x['평가가액'] == 0 else x['평가가액'], axis=1)
    df_a['평가차액(+)'] = df_a['적용평가가'] - df_a['장부가액']
    
    df_l = st.session_state.liabs.copy()
    df_l['적용평가가'] = df_l.apply(lambda x: x['장부가액'] if x['평가가액'] == 0 else x['평가가액'], axis=1)
    # 부채는 평가가가 커지면 순자산이 감소하므로 차액을 반대로 계산하거나 마이너스로 표시
    df_l['평가차액(-)'] = df_l['적용평가가'] - df_l['장부가액'] 

    # 화면에 명세서 출력 (0원이어도 모두 출력됨)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**자산 평가차액 명세서**")
        st.dataframe(df_a[['계정과목', '장부가액', '적용평가가', '평가차액(+)']], use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**부채 평가차액 명세서**")
        st.dataframe(df_l[['계정과목', '장부가액', '적용평가가', '평가차액(-)']], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🚀 비상장주식 최종 가치평가 결과")
    
    # 1. 순자산가치 계산
    total_asset = df_a['적용평가가'].sum()
    total_liab = df_l['적용평가가'].sum()
    net_asset = total_asset - total_liab
    a_val = net_asset / total_shares if total_shares > 0 else 0
    
    # 2. 순손익가치 계산 (3:2:1 가중평균)
    avg_profit = (profits[0]*3 + profits[1]*2 + profits[2]*1) / 6
    p_val = (avg_profit / 0.1) / total_shares if total_shares > 0 else 0
    
    # 3. 최종 가중평균 (원칙 3:2, 부동산과다 등 예외는 생략된 기본모델)
    weighted = (p_val * 0.6) + (a_val * 0.4)
    final = max(weighted, a_val * 0.8) # 순자산가치의 80% 하한선 적용
    
    # 대시보드 출력
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("1주당 순손익가치", f"{int(p_val):,} 원")
    col_r2.metric("1주당 순자산가치", f"{int(a_val):,} 원")
    col_r3.metric("최종 1주당 평가가액", f"{int(final):,} 원", delta="하한선 검증 완료")