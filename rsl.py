import streamlit as st
import pandas as pd
import datetime

# --- 1. 설정 및 디자인 정의 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
NAVER_GREEN = "#03C75A"
DEEP_NAVY = "#1B263B"

st.set_page_config(page_title="2026 라운즈 프로모션", page_icon="🔍", layout="wide")

# --- 2. 고급스러운 CSS 드레스업 (미니멀 & 프리미엄) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Pretendard', sans-serif; }}
    
    /* 제목 및 헤더 스타일 */
    .main-title {{ font-size: 22px; font-weight: 800; color: {DEEP_NAVY}; margin-bottom: 5px; line-height: 1.3; }}
    .naver-icon {{ font-size: 28px; vertical-align: middle; margin-right: 8px; color: {NAVER_GREEN}; }}
    
    /* 탭 디자인 개선 */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 45px; border-radius: 6px; background-color: #f1f3f5; 
        font-weight: 600; font-size: 15px; border: none; color: #495057;
    }}
    .stTabs [aria-selected="true"] {{ background-color: {DEEP_NAVY} !important; color: white !important; }}
    
    /* 카드 디자인 */
    .benefit-card {{
        background-color: #ffffff; padding: 24px; border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #edf2f7; margin-bottom: 16px;
    }}
    .benefit-title {{ font-size: 18px; font-weight: 800; margin-bottom: 12px; color: {DEEP_NAVY}; }}
    
    /* 게이지바 커스텀 */
    .gauge-container {{ width: 100%; background-color: #e9ecef; border-radius: 50px; height: 12px; margin: 20px 0; overflow: hidden; }}
    .gauge-fill {{ height: 100%; border-radius: 50px; transition: width 0.8s ease-in-out; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 데이터 로드 로직 ---
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
    st.error("데이터 연결을 확인해주세요.")
    st.stop()

# --- 4. 메인 헤더 (네이버 아이콘 강조 및 제목 축소) ---
st.markdown(f'<div class="main-title"><span class="naver-icon">N</span>네이버 지역광고 상단노출, <br/>라운즈에서 해드립니다.</div>', unsafe_allow_html=True)
st.markdown("---")

# --- 5. 내비게이션 탭 ---
tab1, tab2 = st.tabs(["📊 실적 조회", "🎁 달성 혜택 안내"])

# ==========================================
# [탭 1] 실적 조회
# ==========================================
with tab1:
    user_input = st.text_input("🏢 사업자번호", placeholder="숫자만 입력하세요", label_visibility="collapsed")
    
    if st.button("조회하기", use_container_width=True):
        if user_input:
            search_num = user_input.replace('-', '').strip()
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                r = result.iloc[0]
                store_display_name = f"{r['매장명']} 안경원" # '원장님'에서 '안경원'으로 변경
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
                
                st.markdown(f"### **{store_display_name}**")
                
                # 게이지바 디자인 (심플하게)
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = NAVER_GREEN if percent >= 100 else DEEP_NAVY
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 5px;">
                    <span style="font-size: 14px; font-weight: 600; color: {DEEP_NAVY};">합격선 달성률</span>
                    <span style="font-size: 20px; font-weight: 800; color: {bar_color};">{percent}%</span>
                </div>
                <div class="gauge-container">
                    <div class="gauge-fill" style="width: {display_percent}%; background-color: {bar_color};"></div>
                </div>
                """, unsafe_allow_html=True)

                if user_rank <= target_to:
                    st.success(f"🏆 **현재 {grade} 등급 {user_rank}위 | [달성 혜택 1] 안정권**")
                elif user_rank <= display_limit:
                    st.warning(f"🎯 **현재 {grade} 등급 {user_rank}위 | [달성 혜택 1]까지 {target_amt - current_amt:,}원 부족**")
                else:
                    st.info(f"🚀 **현재 {grade} 등급 {user_rank}위 | [달성 혜택 2] 집중 공략 가능**")
                
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("위탁 등급", grade)
                with c2: 
                    label = "3개월 평균" if user_rank > display_limit else f"당첨 합격선({target_to}위)"
                    val = avg_3month if user_rank > display_limit else target_amt
                    st.metric(label, f"{val:,}원")
                with c3: st.metric(f"3월 발주액({update_time_str})", f"{current_amt:,}원")
                
                st.write("")
                if st.button("🎁 이번 달 상세 혜택 보기"):
                    st.info("상단 **[🎁 달성 혜택 안내]** 탭을 클릭하시면 상세 내용을 확인하실 수 있습니다.")

# ==========================================
# [탭 2] 달성 혜택 안내
# ==========================================
with tab2:
    st.markdown(f"#### **🏆 구간별 달성 혜택**")
    
    st.markdown(f"""
    <div class="benefit-card">
        <div class="benefit-title">🎁 달성 혜택 1</div>
        <div style="font-size: 14px; color: {NAVER_GREEN}; font-weight: 700; margin-bottom: 10px;">누적 실적 상위 매장 선정</div>
        <ul style="font-size: 15px; color: #4a5568; padding-left: 20px;">
            <li><b>네이버 검색 상단 노출 광고비 전액 지원</b></li>
            <li>플레이스 최적화 및 1:1 전담 마케터 배정</li>
        </ul>
    </div>
    <div class="benefit-card">
        <div class="benefit-title">🎁 달성 혜택 2</div>
        <div style="font-size: 14px; color: #4A90E2; font-weight: 700; margin-bottom: 10px;">전월 대비 성장률 우수 매장 선정</div>
        <ul style="font-size: 15px; color: #4a5568; padding-left: 20px;">
            <li><b>네이버 파워링크 광고 무료 세팅 및 대행</b></li>
            <li>플레이스 마케팅 가이드북 증정</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("📌 선정 기준 상세 확인"):
        st.markdown(f"""
        1. **누적 실적 랭킹:** 꾸준히 많은 발주를 기록한 매장 (등급별 상위 T/O 배정)
        2. **전월 대비 급성장:** 규모와 상관없이 이번 달 발주 성장이 가장 뚜렷한 매장
        """)
