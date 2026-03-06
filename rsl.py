import streamlit as st
import pandas as pd
import datetime

# --- 1. 설정 및 상단 디자인 정의 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
NAVER_GREEN = "#03C75A"

st.set_page_config(page_title="2026 렌즈 프로모션", page_icon="🔍", layout="wide")

# --- 2. CSS 드레스업 (모바일 가독성 및 카드 디자인) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Noto Sans KR', sans-serif; line-height: 1.6; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 50px; border-radius: 8px 8px 0 0; background-color: #f8f9fa; 
        font-weight: 700; font-size: 16px; border: 1px solid #e9ecef;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {NAVER_GREEN} !important; color: white !important; }}
    .metric-card {{
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #f1f3f5; margin-bottom: 10px;
    }}
    .naver-badge {{
        background-color: {NAVER_GREEN}; color: white; padding: 2px 8px;
        border-radius: 4px; font-weight: 900; font-size: 12px; margin-right: 5px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로드 (구글 시트) ---
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
    update_time_str = now.strftime("%m월 %d일 %H:%M")
except:
    st.error("데이터 연결을 확인해주세요.")
    st.stop()

# --- 4. 메인 헤더 ---
st.markdown(f'# <span class="naver-badge">N</span> 네이버 지역광고 상단노출, **라운즈에서 해드립니다.**', unsafe_allow_html=True)
st.caption(f"🕒 실시간 데이터 취합 중 (최종 업데이트: {update_time_str})")
st.markdown("---")

# --- 5. 상단 탭 내비게이션 ---
tab1, tab2 = st.tabs(["📊 우리 매장 실적 조회", "🎁 달성 혜택 및 선정 안내"])

# ==========================================
# [탭 1] 실적 조회
# ==========================================
with tab1:
    st.markdown("### **우리 매장 혜택 당첨 확인**")
    user_input = st.text_input("🏢 사업자번호 입력", placeholder="숫자만 입력 (예: 1234567890)")

    if st.button("실적 확인하기", use_container_width=True):
        if user_input:
            search_num = user_input.replace('-', '').strip()
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                r = result.iloc[0]
                grade = r['등급']
                current_amt = int(r['26/03'])
                target_col = '프로모션 기준금액(최근3개월)'
                avg_3month = int(r[target_col])
                
                # 순위 계산
                grade_df = df[df['등급'] == grade].copy()
                grade_df['rank'] = grade_df['26/03'].rank(method='min', ascending=False)
                user_rank = int(grade_df[grade_df['사업자번호'] == search_num]['rank'].values[0])
                target_to = TO_MAP.get(grade, 10)
                display_limit = LIMIT_MAP.get(grade, 25)
                
                grade_sorted = grade_df.sort_values(by='26/03', ascending=False).reset_index(drop=True)
                target_idx = min(target_to, len(grade_sorted)) - 1
                target_amt = int(grade_sorted.loc[target_idx, '26/03'])
                
                st.markdown(f"## 👤 **{r['매장명']}** 원장님")
                
                # 게이지바 디자인
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = NAVER_GREEN if percent >= 100 else "#FF4B4B"
                
                st.markdown(f"""
                <div style="width: 100%; background-color: #eee; border-radius: 20px; height: 30px; margin: 15px 0;">
                    <div style="width: {display_percent}%; height: 30px; background: {bar_color}; border-radius: 20px; display: flex; align-items: center; justify-content: flex-end; padding-right: 15px; color: white; font-weight: 900;">
                        {percent}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if user_rank <= target_to:
                    st.success(f"🎊 **현재 {grade} 등급 {user_rank}위! [달성 혜택 1] 안정권입니다.**")
                    st.markdown(f"합격선 대비 **{current_amt - target_amt:,}원** 초과 달성 중!")
                elif user_rank <= display_limit:
                    st.warning(f"🔥 **현재 {grade} 등급 {user_rank}위! 조금만 더 하면 [달성 혜택 1] 확정!**")
                    st.markdown(f"당첨 합격선까지 딱 **{target_amt - current_amt:,}원** 남았습니다.")
                else:
                    st.error(f"🚀 **현재 {grade} 등급 {user_rank}위! [달성 혜택 2]를 노려보세요!**")
                    st.info("전월 대비 성장률이 높으면 '슈퍼 루키'로 선정되어 마케팅 지원을 받으실 수 있습니다.")
                
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("🏅 위탁 등급", grade)
                with c2: 
                    label = f"📊 나의 3개월 평균" if user_rank > display_limit else f"🎯 현재 당첨 합격선({target_to}위)"
                    val = avg_3month if user_rank > display_limit else target_amt
                    st.metric(label, f"{val:,}원")
                with c3: st.metric("🛒 3월 현재 발주액", f"{current_amt:,}원")

                st.write("")
                st.info("💡 랭킹에 따른 **자세한 달성 혜택**을 지금 바로 확인해 보세요!")
                # 가짜 버튼 (상단 탭이 있으므로 안내만)
                st.success("👇 화면 상단의 **[🎁 달성 혜택 및 선정 안내]** 탭을 클릭해 주세요!")
            else:
                st.error("사업자번호를 다시 확인해주세요.")

# ==========================================
# [탭 2] 달성 혜택 안내
# ==========================================
with tab2:
    st.markdown(f"### <span style='color:{NAVER_GREEN}'>🏆 이번 달 달성 혜택 안내</span>", unsafe_allow_html=True)
    st.markdown("매출 규모에 상관없이, 모든 파트너 원장님들께 공평한 기회를 드립니다.")
    
    st.write("")
    st.markdown(f"""
    <div class="metric-card">
        <h4>🎁 <strong>달성 혜택 1: [ 올인원 풀케어 마케팅 ]</strong></h4>
        <p style="color:{NAVER_GREEN}; font-weight:700;">비용: 전액 무상 지원 (본사 부담)</p>
        <ul>
            <li><strong>네이버 검색 상단 노출</strong> (2개월간 광고비 전액 지원)</li>
            <li><strong>플레이스 최적화</strong> 전문가 1:1 세팅</li>
            <li><strong>매장별 마케팅 컨설팅</strong> 리포트 제공</li>
        </ul>
    </div>
    <div class="metric-card">
        <h4>🎁 <strong>달성 혜택 2: [ 마스터 세팅 & 광고 대행 ]</strong></h4>
        <p style="color:#2E5BFF; font-weight:700;">비용: 운영/세팅비 무상 (광고 실비만 원장님 부담)</p>
        <ul>
            <li><strong>네이버 파워링크</strong> 상단 노출 무료 세팅</li>
            <li><strong>플레이스 마스터 가이드</strong> 및 실전 교육 지원</li>
            <li><strong>광고 효율 관리</strong> 및 전담 마케터 배정</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("📌 당첨 기준 확인 (클릭하여 펼치기)"):
        st.markdown(f"""
        **1. [ 누적 실적 랭킹 ]**
        * 꾸준히 발주해주신 파트너 매장을 선정합니다. (등급별 상위 T/O 배정)
        
        **2. [ 전월 대비 급성장 ]**
        * 작은 매장도 역전 가능! 발주량이 가장 많이 늘어난 매장을 '슈퍼 루키'로 선정합니다.
        
        ---
        💡 지금 바로 **[📊 우리 매장 실적 조회]** 탭에서 나의 현재 등수를 확인해 보세요!
        """)
