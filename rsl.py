import streamlit as st
import pandas as pd
import datetime

# --- 1. 설정 및 디자인 변수 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
NAVER_GREEN = "#03C75A"
DEEP_GRAY = "#333333"

st.set_page_config(page_title="2026 라운즈 프로모션", page_icon="🔍", layout="centered")

# --- 2. 프리미엄 CSS (줄간격 및 카드 디자인 최적화) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Pretendard', sans-serif; line-height: 1.6; color: #333; }}
    
    /* 헤더 및 아이콘 */
    .header-container {{ padding: 25px 0; border-bottom: 2px solid {NAVER_GREEN}; margin-bottom: 35px; }}
    .naver-logo {{ font-size: 32px; font-weight: 900; color: {NAVER_GREEN}; vertical-align: middle; margin-right: 15px; }}
    .main-title {{ font-size: 20px; font-weight: 700; color: #111; display: inline-block; vertical-align: middle; line-height: 1.3; }}
    
    /* 프리미엄 카드 */
    .p-card {{
        background: white; padding: 20px; border-radius: 12px;
        border: 1px solid #EAECEF; box-shadow: 0 2px 8px rgba(0,0,0,0.02); margin-bottom: 15px;
    }}
    .p-label {{ font-size: 13px; color: #888; font-weight: 600; margin-bottom: 5px; }}
    .p-value {{ font-size: 22px; font-weight: 800; color: #111; }}
    
    /* 게이지바 */
    .gauge-bg {{ width: 100%; background: #F1F3F5; border-radius: 50px; height: 16px; margin: 15px 0; overflow: hidden; }}
    .gauge-fill {{ height: 100%; border-radius: 50px; transition: width 1s; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로드 및 탭 제어 로직 ---
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = 0

def change_tab():
    st.session_state['active_tab'] = 1

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
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    update_time_str = now.strftime("%m/%d %H:%M")
except:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# --- 4. 메인 헤더 ---
st.markdown(f'''
    <div class="header-container">
        <span class="naver-logo">N</span>
        <div class="main-title">라운즈 3~4월 렌즈 프로모션 <br/>네이버 지역광고 상단노출,<br/>라운즈에서 해드립니다.</div>
    </div>
''', unsafe_allow_html=True)

# --- 5. 내비게이션 (Tabs 대신 State 기반으로 변경) ---
# 💡 버튼 클릭으로 화면을 전환하기 위해 세션 상태를 사용합니다.
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = "check"

# 상단 메뉴 구성 (클릭 시 페이지 전환)
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("📊 프로모션 달성 확인하기", use_container_width=True, 
                 type="primary" if st.session_state['active_tab'] == "check" else "secondary"):
        st.session_state['active_tab'] = "check"
        st.rerun()
with col_nav2:
    if st.button("🎁 달성 혜택 안내", use_container_width=True,
                 type="primary" if st.session_state['active_tab'] == "benefit" else "secondary"):
        st.session_state['active_tab'] = "benefit"
        st.rerun()

st.markdown("---")

# ==========================================
# [화면 1] 프로모션 달성 확인하기
# ==========================================
if st.session_state['active_tab'] == "check":
    user_input = st.text_input("🏢 사업자번호 입력", placeholder="안경원 사업자번호를 숫자만 입력해주세요 ", key="search_bar", label_visibility="collapsed")
    
    if st.button("조회하기", use_container_width=True):
        if user_input:
            search_num = user_input.replace('-', '').strip()
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                r = result.iloc[0]
                store_display_name = f"{r['매장명']} 안경원" # '원장님'에서 '안경원'으로 예우
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
                
                st.markdown(f"### **{store_display_name}**")
                
                # 게이지바
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = NAVER_GREEN if percent >= 100 else "#FF5252"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                    <span style="font-size: 14px; font-weight: 700; color: #555;">달성 합격선 대비 달성률</span>
                    <span style="font-size: 24px; font-weight: 900; color: {bar_color};">{percent}%</span>
                </div>
                <div class="gauge-bg">
                    <div class="gauge-fill" style="width: {display_percent}%; background-color: {bar_color};"></div>
                </div>
                """, unsafe_allow_html=True)

                if user_rank <= target_to:
                    st.success(f"🏆 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 1]** 안정권")
                    st.markdown(f"합격선 대비 **{current_amt - target_amt:,}원** 초과 달성 중입니다.")
                elif user_rank <= display_limit:
                    st.warning(f"🎯 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 1]** 진입까지 **{target_amt - current_amt:,}원**")
                else:
                    st.error(f"🚀 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 2]** 집중 공략 구간")
                
                st.markdown("---")
                
                # 💳 그리드 데이터 (조건부 노출 반영)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'<div class="p-card"><div class="p-label">위탁 등급</div><div class="p-value">{grade}</div></div>', unsafe_allow_html=True)
                with col2:
                    if user_rank > display_limit:
                        label, val = "나의 3개월 평균", avg_3month
                    else:
                        label, val = f"당첨 합격선({target_to}위)", target_amt
                    st.markdown(f'<div class="p-card"><div class="p-label">{label}</div><div class="p-value">{val:,}원</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="p-card"><div class="p-label">3월 발주액({update_time_str})</div><div class="p-value">{current_amt:,}원</div></div>', unsafe_allow_html=True)

                st.write("")
                # 💡 [해결 포인트] 버튼 클릭 시 세션 상태를 변경하여 페이지 이동
                st.info("💡 지금 바로 상세 혜택을 확인해 보세요!")
                if st.button("🎁 이번 달 상세 혜택 보러가기", use_container_width=True):
                    st.session_state['active_tab'] = "benefit"
                    st.rerun()
            else:
                st.error("사업자번호를 정확히 입력했는지 확인해 주세요.")

# ==========================================
# [화면 2] 달성 혜택 안내
# ==========================================
elif st.session_state['active_tab'] == "benefit":
    st.markdown("#### **🏆 구간별 달성 혜택 상세**")
    st.write("")
    
    st.markdown(f"""
    <div class="p-card" style="border-left: 5px solid {NAVER_GREEN};">
        <div style="font-size: 18px; font-weight: 800; color: #111; margin-bottom: 5px;">🎁 달성 혜택 1: 올인원 패키지</div>
        <div style="font-size: 13px; color: {NAVER_GREEN}; font-weight: 700; margin-bottom: 15px;">매출 상위매장 선정</div>
        <ul style="font-size: 15px; color: #444; padding-left: 18px; line-height: 1.8;">
            <li><b>네이버 플레이스 상단노출 광고대행 및 광고비 지원</b> (2개월)</li>
            <li>네이버 플레이스 점검 및 최적화 세팅</li>
            <li>안경원 마케팅 상담채널 제공</li>
            <li>네이버 성과관리 리포트 제공</li>
        </ul>
    </div>
    <div class="p-card" style="border-left: 5px solid #2E5BFF;">
        <div style="font-size: 18px; font-weight: 800; color: #111; margin-bottom: 5px;">🎁 달성 혜택 2: 스탠다드 패키지</div>
        <div style="font-size: 13px; color: #2E5BFF; font-weight: 700; margin-bottom: 15px;">전월 대비 성장률 우수 매장 선정 (슈퍼 루키)</div>
        <ul style="font-size: 15px; color: #444; padding-left: 18px; line-height: 1.8;">
            <li><b>네이버 플레이스 상단노출 광고대행(비용 안경원 부담)</b></li>
            <li>네이버 플레이스 점검 및 최적화 세팅</li>
            <li>안경원 마케팅 상담채널 제공</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("📌 당첨 및 선정 기준 상세 가이드"):
        st.markdown("""
        **달성 혜택 1** : 꾸준히 많은 발주를 기록 중인 매장을 등급별 상위 T/O에 맞춰 선정합니다.(**누적 실적 랭킹**)
        
        **달성 혜택 2** : 규모와 상관없이, 이번 달 발주 성장이 가장 뚜렷한 매장을 '슈퍼 루키'로 선정합니다.(**전월 대비 급성장**)
        """)









