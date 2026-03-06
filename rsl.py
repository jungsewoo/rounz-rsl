import streamlit as st
import pandas as pd
import datetime

# --- 1. 설정 및 디자인 변수 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
NAVER_GREEN = "#03C75A"

st.set_page_config(page_title="2026 라운즈 프로모션", page_icon="🔍", layout="centered")

# --- 2. 프리미엄 CSS (폰트 충돌 해결 및 레이아웃 안정화) ---
st.markdown(f"""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"] {{ font-family: 'Pretendard', -apple-system, sans-serif; line-height: 1.5; color: #333; }}
    
    /* 메인 헤더 레이아웃 */
    .header-container {{ padding: 15px 0 25px 0; border-bottom: 2px solid {NAVER_GREEN}; margin-bottom: 25px; }}
    .sub-title {{ font-size: 19px; font-weight: 800; color: #111; margin-bottom: 12px; letter-spacing: -0.5px; }}
    
    /* 로고와 텍스트 줄 맞춤 */
    .title-flex-box {{ display: flex; align-items: flex-start; gap: 8px; }}
    .naver-logo {{ font-size: 30px; font-weight: 900; color: {NAVER_GREEN}; line-height: 1.2; }}
    .main-title-text {{ font-size: 26px; font-weight: 800; color: #111; line-height: 1.35; letter-spacing: -1px; word-break: keep-all; }}
    
    /* 탭(버튼) 커스텀 */
    div[data-testid="column"] div.stButton > button {{
        border-radius: 8px 8px 0 0 !important; height: 50px; font-weight: 600; font-size: 16px;
        background-color: #F8F9FA !important; color: #868E96 !important;
        border: 1px solid #EAECEF !important; border-bottom: 2px solid #EAECEF !important; transition: all 0.2s;
    }}
    div[data-testid="column"] div.stButton > button[kind="primary"] {{
        background-color: #FFFFFF !important; color: {NAVER_GREEN} !important;
        border: 1px solid #EAECEF !important; border-bottom: 3px solid {NAVER_GREEN} !important; font-weight: 800;
    }}
    
    /* 혜택 카드 및 그리드 데이터 */
    .p-card {{ background: white; padding: 22px; border-radius: 12px; border: 1px solid #EAECEF; box-shadow: 0 4px 10px rgba(0,0,0,0.03); margin-bottom: 15px; }}
    .p-label {{ font-size: 13px; color: #888; font-weight: 600; margin-bottom: 5px; }}
    .p-value {{ font-size: 22px; font-weight: 800; color: #111; }}
    
    /* 게이지바 */
    .gauge-bg {{ width: 100%; background: #F1F3F5; border-radius: 50px; height: 16px; margin: 15px 0; overflow: hidden; }}
    .gauge-fill {{ height: 100%; border-radius: 50px; transition: width 1s; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로드 및 탭 제어 로직 ---
if 'active_tab' not in st.session_state:
    st.session_state['active_tab'] = "check"

def go_to_benefit():
    st.session_state['active_tab'] = "benefit"

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
        <div class="sub-title">🌸 라운즈 3~4월 렌즈 프로모션</div>
        <div class="title-flex-box">
            <div class="naver-logo">N</div>
            <div class="main-title-text">네이버 지역광고 상단노출,<br/>라운즈에서 해드립니다.</div>
        </div>
    </div>
''', unsafe_allow_html=True)

# --- 5. 내비게이션 (진짜 탭 버튼) ---
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("📊 프로모션 달성 확인하기", use_container_width=True, type="primary" if st.session_state['active_tab'] == "check" else "secondary"):
        st.session_state['active_tab'] = "check"
        st.rerun()
with col_nav2:
    if st.button("🎁 달성 혜택 안내", use_container_width=True, type="primary" if st.session_state['active_tab'] == "benefit" else "secondary"):
        st.session_state['active_tab'] = "benefit"
        st.rerun()

st.markdown("---")

# ==========================================
# [화면 1] 프로모션 달성 확인하기
# ==========================================
if st.session_state['active_tab'] == "check":
    user_input = st.text_input("🏢 사업자번호 입력", placeholder="안경원 사업자번호를 숫자만 입력해주세요", key="search_bar", label_visibility="collapsed")
    
    if st.button("조회하기", use_container_width=True):
        if user_input:
            search_num = user_input.replace('-', '').strip()
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                r = result.iloc[0]
                store_display_name = f"{r['매장명']} 안경원"
                grade = r['등급']
                current_amt = int(r['26/03'])
                target_col = '프로모션 기준금액(최근3개월)'
                avg_3month = int(r[target_col])
                
                grade_df = df[df['등급'] == grade].copy()
                grade_df['rank'] = grade_df['26/03'].rank(method='min', ascending=False)
                user_rank = int(grade_df[grade_df['사업자번호'] == search_num]['rank'].values[0])
                target_to = TO_MAP.get(grade, 10)
                display_limit = LIMIT_MAP.get(grade, 25)
                
                grade_sorted = grade_df.sort_values(by='26/03', ascending=False).reset_index(drop=True)
                target_idx = min(target_to, len(grade_sorted)) - 1
                target_amt = int(grade_sorted.loc[target_idx, '26/03'])
                
                st.markdown(f"### **{store_display_name}**")
                
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = NAVER_GREEN if percent >= 100 else "#FF5252"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                    <span style="font-size: 14px; font-weight: 700; color: #555;">혜택 달성 커트라인 대비 달성률</span>
                    <span style="font-size: 24px; font-weight: 900; color: {bar_color};">{percent}%</span>
                </div>
                <div class="gauge-bg">
                    <div class="gauge-fill" style="width: {display_percent}%; background-color: {bar_color};"></div>
                </div>
                """, unsafe_allow_html=True)

                if user_rank <= target_to:
                    st.success(f"🏆 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 1]** 안정권")
                    st.markdown(f"커트라인 대비 **{current_amt - target_amt:,}원** 초과 달성 중입니다.")
                elif user_rank <= display_limit:
                    st.warning(f"🎯 현재 **{grade} 등급 {user_rank}위** | **[달성 혜택 1]** 커트라인 진입까지 **{target_amt - current_amt:,}원**")
                else:
                    st.error(f"🚀 **[달성 혜택 2] 슈퍼 루키 특별 공략 구간**")
                    st.info("💡 **누적 랭킹이 부담스러우신가요? 걱정 마세요!**\n\n나의 **3개월 평균 발주액**을 뛰어넘어 이번 달 가장 높은 성장률을 보여주시면 **[혜택 2: 스탠다드 패키지]**의 주인공이 되실 수 있습니다. 지금 바로 추가 발주하세요!")
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f'<div class="p-card"><div class="p-label">위탁 등급</div><div class="p-value">{grade}</div></div>', unsafe_allow_html=True)
                with col2:
                    if user_rank > display_limit:
                        label, val = "나의 3개월 평균", avg_3month
                    else:
                        label, val = f"혜택 달성 커트라인({target_to}위)", target_amt
                    st.markdown(f'<div class="p-card"><div class="p-label">{label}</div><div class="p-value">{val:,}원</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="p-card"><div class="p-label">3월 발주액({update_time_str})</div><div class="p-value">{current_amt:,}원</div></div>', unsafe_allow_html=True)

                st.write("")
                st.info("💡 지금 바로 하단의 버튼을 눌러 우리 매장이 받을 수 있는 상세 혜택을 확인하세요!")
                if st.button("🎁 이번 달 상세 혜택 보러가기", on_click=go_to_benefit, use_container_width=True):
                    pass
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
        <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 5px;">
            <div style="font-size: 18px; font-weight: 800; color: #111;">🎁 달성 혜택 1: 올인원 패키지</div>
            <div style="font-size: 12px; font-weight: 800; color: #FF4B4B; background-color: #FFEAEA; padding: 3px 8px; border-radius: 6px;">총 20곳 한정</div>
        </div>
        <div style="font-size: 13px; color: {NAVER_GREEN}; font-weight: 700; margin-bottom: 15px;">약정 등급별 매출 상위매장 선정</div>
        <ul style="font-size: 15px; color: #444; padding-left: 18px; line-height: 1.8;">
            <li><b>네이버 플레이스 상단노출 광고대행 및 광고비 지원</b> (2개월)</li>
            <li>네이버 플레이스 점검 및 최적화 세팅</li>
            <li>안경원 마케팅 상담채널 제공</li>
            <li>네이버 성과관리 리포트 제공</li>
        </ul>
    </div>
    <div class="p-card" style="border-left: 5px solid #2E5BFF;">
        <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 5px;">
            <div style="font-size: 18px; font-weight: 800; color: #111;">🎁 달성 혜택 2: 스탠다드 패키지</div>
            <div style="font-size: 12px; font-weight: 800; color: #2E5BFF; background-color: #E6F0FF; padding: 3px 8px; border-radius: 6px;">총 40곳 한정</div>
        </div>
        <div style="font-size: 13px; color: #2E5BFF; font-weight: 700; margin-bottom: 15px;">최근3개월 대비 성장률 우수 매장 선정 (슈퍼 루키)</div>
        <ul style="font-size: 15px; color: #444; padding-left: 18px; line-height: 1.8;">
            <li><b>네이버 플레이스 상단노출 광고대행(비용 안경원 부담)</b></li>
            <li>네이버 플레이스 점검 및 최적화 세팅</li>
            <li>안경원 마케팅 상담채널 제공</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("📌 혜택 달성 및 선정 기준 상세 가이드"):
        st.markdown(f"""
        <div style="padding: 5px 0;">
            <div style="margin-bottom: 20px;">
                <span style="background-color: #E8F5E9; color: {NAVER_GREEN}; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 13px; margin-right: 8px;">달성 혜택 1</span>
                <span style="font-weight: 800; color: #111; font-size: 15px;">누적 실적 랭킹</span>
                <p style="margin-top: 8px; font-size: 14px; color: #555; line-height: 1.6; word-break: keep-all;">꾸준히 많은 발주를 기록 중인 매장을 등급별 상위 T/O에 맞춰 선정합니다.</p>
            </div>
            <div>
                <span style="background-color: #E6F0FF; color: #2E5BFF; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 13px; margin-right: 8px;">달성 혜택 2</span>
                <span style="font-weight: 800; color: #111; font-size: 15px;">전월 대비 급성장</span>
                <p style="margin-top: 8px; font-size: 14px; color: #555; line-height: 1.6; word-break: keep-all;">규모와 상관없이, 이번 달 발주 성장이 가장 뚜렷한 매장을 <b style="color:#2E5BFF;">'슈퍼 루키'</b>로 선정합니다.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)




