import streamlit as st
import pandas as pd
import datetime

# --- 1. 설정 및 디자인 변수 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
NAVER_GREEN = "#03C75A"

st.set_page_config(page_title="2026 라운즈 프로모션", page_icon="🔍", layout="centered")

# --- 2. 프리미엄 CSS (싼마이 감성 완전 제거) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Pretendard', sans-serif; background-color: #F8F9FA; }}
    
    /* 헤더 디자인 */
    .header-box {{ padding: 20px 0; border-bottom: 2px solid {NAVER_GREEN}; margin-bottom: 30px; }}
    .naver-logo {{ font-size: 36px; font-weight: 900; color: {NAVER_GREEN}; vertical-align: middle; margin-right: 12px; }}
    .main-title {{ font-size: 19px; font-weight: 700; color: #111; display: inline-block; vertical-align: middle; line-height: 1.4; }}
    
    /* 프리미엄 카드 UI */
    .p-card {{
        background: white; padding: 25px; border-radius: 12px;
        border: 1px solid #E9ECEF; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 20px;
    }}
    .p-label {{ font-size: 14px; color: #666; font-weight: 600; margin-bottom: 8px; }}
    .p-value {{ font-size: 24px; font-weight: 800; color: #111; }}
    
    /* 게이지바 커스텀 */
    .gauge-bg {{ width: 100%; background: #EDF2F7; border-radius: 100px; height: 14px; margin: 15px 0; overflow: hidden; }}
    .gauge-fill {{ height: 100%; border-radius: 100px; transition: width 0.8s; }}
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{ border-bottom: 1px solid #E9ECEF; }}
    .stTabs [data-baseweb="tab"] {{ font-weight: 600; color: #ADB5BD; }}
    .stTabs [aria-selected="true"] {{ color: {NAVER_GREEN} !important; border-bottom-color: {NAVER_GREEN} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로드 및 세션 상태 ---
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 0

@st.cache_data(ttl=300)
def load_data():
    sheet_url = st.secrets["SHEET_URL"]
    csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit', '/export?format=csv')
    df = pd.read_csv(csv_url)
    df.columns = [c.strip() for c in df.columns]
    target_col = '프로모션 기준금액(최근3개월)'
    for col in ['26/03', target_col]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    if '사업자번호' in df.columns:
        df['사업자번호'] = df['사업자번호'].astype(str).str.replace('-', '', regex=False).str.strip()
    return df

try:
    df = load_data()
except:
    st.error("데이터 연결을 확인해주세요.")
    st.stop()

# --- 4. 메인 헤더 ---
st.markdown(f'''
    <div class="header-box">
        <span class="naver-logo">N</span>
        <div class="main-title">네이버 지역광고 상단노출,<br/>라운즈에서 해드립니다.</div>
    </div>
''', unsafe_allow_html=True)

# --- 5. 내비게이션 (Tabs) ---
# 💡 세션 상태를 이용해 탭 위치를 강제 조정할 수 있게 설정
tab_titles = ["📊 실적 조회", "🎁 달성 혜택 안내"]
tabs = st.tabs(tab_titles)

# ==========================================
# [탭 1] 실적 조회
# ==========================================
with tabs[0]:
    user_input = st.text_input("🏢 사업자번호 입력", placeholder="숫자만 입력해 주세요", label_visibility="collapsed")
    
    if st.button("조회하기", use_container_width=True):
        if user_input:
            search_num = user_input.replace('-', '').strip()
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                r = result.iloc[0]
                store_name = f"{r['매장명']} 안경원"
                grade = r['등급']
                current_amt = int(r['26/03'])
                target_col = '프로모션 기준금액(최근3개월)'
                avg_3month = int(r[target_col])
                
                # 순위 로직
                grade_df = df[df['등급'] == grade].copy()
                grade_df['rank'] = grade_df['26/03'].rank(method='min', ascending=False)
                user_rank = int(grade_df[grade_df['사업자번호'] == search_num]['rank'].values[0])
                target_to = TO_MAP.get(grade, 10)
                display_limit = LIMIT_MAP.get(grade, 25)
                grade_sorted = grade_df.sort_values(by='26/03', ascending=False).reset_index(drop=True)
                target_idx = min(target_to, len(grade_sorted)) - 1
                target_amt = int(grade_sorted.loc[target_idx, '26/03'])
                
                st.markdown(f"### **{store_name}**")
                
                # 📈 프리미엄 게이지 섹션
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = NAVER_GREEN if percent >= 100 else "#FF4B4B"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                    <span style="font-size: 14px; font-weight: 700; color: #4A5568;">합격선 달성률</span>
                    <span style="font-size: 22px; font-weight: 900; color: {bar_color};">{percent}%</span>
                </div>
                <div class="gauge-bg">
                    <div class="gauge-fill" style="width: {display_percent}%; background-color: {bar_color};"></div>
                </div>
                """, unsafe_allow_html=True)

                if user_rank <= target_to:
                    st.success(f"🎊 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 1]** 안정권입니다.")
                    st.markdown(f"합격선 대비 **{current_amt - target_amt:,}원** 초과 달성 중입니다.")
                elif user_rank <= display_limit:
                    st.warning(f"🔥 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 1]**까지 단 **{target_amt - current_amt:,}원**!")
                else:
                    st.error(f"🚀 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 2]** 집중 공략 구간입니다.")
                
                st.markdown("---")
                
                # 💳 그리드 데이터 카드 (정보 보강)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="p-card"><div class="p-label">위탁 등급</div><div class="p-value">{grade}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="p-card"><div class="p-label">3개월 평균 발주액</div><div class="p-value">{avg_3month:,}원</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="p-card"><div class="p-label">당첨 합격선({target_to}위)</div><div class="p-value">{target_amt:,}원</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="p-card"><div class="p-label">3월 현재 발주액</div><div class="p-value">{current_amt:,}원</div></div>', unsafe_allow_html=True)

                st.write("")
                # 💡 실제로 혜택 탭을 보라고 유도하는 강한 메시지
                st.info("💡 랭킹별 상세 혜택과 선정 기준은 상단의 **[🎁 달성 혜택 안내]** 탭에서 바로 확인하실 수 있습니다!")

# ==========================================
# [탭 2] 달성 혜택 안내 (풍성한 내용 복원)
# ==========================================
with tabs[1]:
    st.markdown("#### **🏆 구간별 달성 혜택 상세**")
    st.markdown("모든 혜택은 네이버 지역광고 전문가가 직접 세팅해 드립니다.")
    
    st.write("")
    st.markdown(f"""
    <div class="p-card" style="border-left: 5px solid {NAVER_GREEN};">
        <div style="font-size: 18px; font-weight: 800; color: #111; margin-bottom: 5px;">🎁 달성 혜택 1</div>
        <div style="font-size: 14px; color: {NAVER_GREEN}; font-weight: 700; margin-bottom: 15px;">누적 실적 랭킹 상위 매장 (등급별 T/O 배정)</div>
        <ul style="font-size: 15px; color: #444; padding-left: 20px; line-height: 1.8;">
            <li><b>네이버 검색 상단 노출 광고비 전액 지원</b> (2개월)</li>
            <li>네이버 플레이스 최적화 전문가 1:1 세팅</li>
            <li>매장 맞춤형 로컬 마케팅 컨설팅 리포트 제공</li>
            <li>전담 마케터 배정을 통한 광고 효율 관리</li>
        </ul>
    </div>
    <div class="p-card" style="border-left: 5px solid #2E5BFF;">
        <div style="font-size: 18px; font-weight: 800; color: #111; margin-bottom: 5px;">🎁 달성 혜택 2</div>
        <div style="font-size: 14px; color: #2E5BFF; font-weight: 700; margin-bottom: 15px;">전월 대비 성장률 우수 매장 (슈퍼 루키 트랙)</div>
        <ul style="font-size: 15px; color: #444; padding-left: 20px; line-height: 1.8;">
            <li><b>네이버 파워링크 상단 노출 무료 세팅 및 대행</b></li>
            <li>실전 플레이스 마케팅 가이드북(PDF) 증정</li>
            <li>지역 광고 데이터 분석 및 세팅 최적화 지원</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("📌 당첨 및 선정 기준 상세 가이드"):
        st.markdown("""
        1. **누적 실적 랭킹:** 프로모션 기간 내 누적 발주액을 기준으로 등급별 상위 매장을 선정합니다.
        2. **전월 대비 급성장:** 규모가 작은 매장도 혜택을 받으실 수 있도록, 전월 대비 발주 성장액이 가장 높은 매장을 선정합니다.
        
        ---
        💡 지금 바로 **[📊 실적 조회]** 탭에서 사업자번호를 입력하고 나의 현재 위치를 확인해 보세요!
        """)
