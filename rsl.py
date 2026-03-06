import streamlit as st
import pandas as pd
import datetime

# --- 1. 등급별 T/O 및 노출 제한 설정 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}

# --- 2. 웹 페이지 기본 설정 ---
st.set_page_config(page_title="2026 렌즈프로모션 조회", page_icon="🌸", layout="wide")

# --- 3. 구글 시트 데이터 로드 및 전처리 ---
@st.cache_data(ttl=600) # 10분마다 새로고침
def load_data():
    # 스트림릿 Secrets에 저장된 주소 불러오기
    sheet_url = st.secrets["SHEET_URL"]
    csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit', '/export?format=csv')
    df = pd.read_csv(csv_url)
    
    # 제목 공백 제거
    df.columns = [c.strip() for c in df.columns]
    
    # 숫자 데이터 세척 (콤마, '원' 제거 후 숫자로 변환)
    target_col = '프로모션 기준금액(최근3개월)'
    numeric_cols = ['26/03', target_col]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 사업자번호 하이픈 제거 및 문자열 통일
    if '사업자번호' in df.columns:
        df['사업자번호'] = df['사업자번호'].astype(str).str.replace('-', '', regex=False).str.strip()
    
    return df

try:
    df = load_data()
    # 한국 시간 보정 (서버가 해외에 있어도 한국 시간 표시)
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    update_time_str = now.strftime("%m월 %d일 %H:%M 기준")
except Exception as e:
    st.error("⚠️ 데이터를 불러올 수 없습니다. 구글 시트 공유 설정이나 스트림릿 Secrets 주소를 확인해주세요.")
    st.stop()

# --- 4. 메인 화면 상단 타이틀 ---
st.title("🌸 2026년 3~4월 마케팅 프로모션")
st.caption("본 대시보드는 라운즈 파트너 안경원 전용 실적 확인 페이지입니다.")
st.markdown("---")

# --- 5. [중요] 모바일 최적화 상단 탭 내비게이션 ---
# 왼쪽 사이드바 대신 화면 상단에 탭을 배치하여 모바일 접근성을 높였습니다.
tab1, tab2 = st.tabs(["📊 우리 매장 실적 조회", "🎁 프로모션 혜택 안내"])

# ==========================================
# [탭 1] 실적 조회 화면 로직
# ==========================================
with tab1:
    st.markdown("#### 우리 매장 무료 마케팅 혜택 당첨 확인하기")
    
    # 하이픈 없이 입력하도록 유도
    user_input = st.text_input("🏢 매장 사업자번호를 입력해주세요.", 
                             placeholder="하이픈(-) 없이 숫자만 입력 (예: 1234567890)",
                             key="main_search")

    if st.button("조회하기", use_container_width=True):
        if user_input:
            search_num = user_input.replace('-', '').strip()
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                store_name = result['매장명'].values[0]
                grade = result['등급'].values[0]
                current_amt = int(result['26/03'].values[0])
                target_col = '프로모션 기준금액(최근3개월)'
                avg_3month = int(result[target_col].values[0])
                
                # 순위 및 커트라인 계산
                grade_df = df[df['등급'] == grade].copy()
                grade_df['내등급순위'] = grade_df['26/03'].rank(method='min', ascending=False)
                user_rank = int(grade_df[grade_df['사업자번호'] == search_num]['내등급순위'].values[0])
                
                target_to = TO_MAP.get(grade, 10)
                display_limit = LIMIT_MAP.get(grade, 25)
                
                grade_sorted = grade_df.sort_values(by='26/03', ascending=False).reset_index(drop=True)
                target_idx = min(target_to, len(grade_sorted)) - 1
                target_amt = int(grade_sorted.loc[target_idx, '26/03']) if len(grade_sorted) > 0 else 0
                
                st.markdown(f"### 👤 **{store_name}** 원장님 현황")
                
                # 임팩트 게이지바 퍼센트 계산
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = "linear-gradient(90deg, #00b09b, #96c93d)" if percent >= 100 else "linear-gradient(90deg, #ff8a00, #e52e71)"
                
                gauge_html = f"""
                <div style="width: 100%; background-color: #f0f2f6; border-radius: 20px; margin-top: 10px; margin-bottom: 5px;">
                    <div style="width: {display_percent}%; height: 28px; background: {bar_color}; border-radius: 20px; display: flex; align-items: center; justify-content: flex-end; padding-right: 12px; color: white; font-weight: 900; font-size: 14px;">
                        {percent}%
                    </div>
                </div>
                """

                # 상태별 메시지 출력 (상위권/중위권/하위권)
                if user_rank <= target_to:
                    st.success(f"🟢 **당첨 안정권 진입! (현재 {grade} {user_rank}위)**")
                    st.markdown(gauge_html, unsafe_allow_html=True)
                    st.markdown(f"**🎉 목표 달성! 현재 당첨 합격선을 <span style='color:#00b09b;'>{current_amt - target_amt:,}원</span> 초과했습니다.**", unsafe_allow_html=True)
                elif user_rank <= display_limit:
                    gap = target_amt - current_amt
                    st.warning(f"🟡 **당첨 가시권! (현재 {grade} {user_rank}위)**")
                    st.markdown(gauge_html, unsafe_allow_html=True)
                    st.markdown(f"**🔥 당첨권 진입까지 딱 <span style='color:#ff8a00;'>{gap:,}원</span> 부족합니다! 조금만 더 힘내세요!**", unsafe_allow_html=True)
                else:
                    st.error(f"🚀 **슈퍼 루키 부문 (역전의 기회!)**")
                    st.warning(f"원장님, 매출 순위는 조금 낮지만 걱정 마세요! 이번 달 발주량을 확 늘리시면 **[혜택 2: 전월 대비 급성장 부문]** 당첨이 유력합니다!")
                
                st.write("")
                # 실적 지표 카드 (모바일에서는 세로로 나열됨)
                col1, col2, col3 = st.columns(3)
                col1.metric("🏅 위탁 등급", grade)
                # 하위권일 경우만 3개월 평균 노출, 그 외엔 합격선 노출
                if user_rank > display_limit:
                    col2.metric("📊 나의 3개월 평균액", f"{avg_3month:,}원")
                else:
                    col2.metric(f"🎯 현재 당첨 합격선 ({grade} {target_to}위)", f"{target_amt:,}원")
                col3.metric(f"🛒 3월 발주액 ({update_time_str})", f"{current_amt:,}원")
                
                st.markdown("---")
                st.info("💡 위 실적을 바탕으로 받을 수 있는 상세 혜택이 궁금하신가요? 상단 메뉴의 **[🎁 프로모션 혜택 안내]**를 클릭해 보세요!")

            else:
                st.error("⚠️ 일치하는 매장 정보가 없습니다. 숫자만 정확히 입력했는지 확인해 주세요.")

# ==========================================
# [탭 2] 프로모션 혜택 안내 화면 로직
# ==========================================
with tab2:
    st.markdown("### 🚨 네이버 지역 광고, 라운즈가 쏩니다!")
    st.markdown("어설픈 대행사에 돈 쓰지 마세요. 본사 전문가가 원장님 매장을 네이버 맛집처럼 띄워드립니다.")
    
    st.markdown("---")
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("#### 🎁 [ 올인원 풀케어 마케팅 ]") 
        st.success("비용: **전액 무상 지원** (광고비 0원)")
        st.markdown("""
        * **네이버 검색 상단 노출** (2개월)
        * **네이버 플레이스** 전문가 최적화 세팅
        * **1:1 전담 마케터** 밀착 관리
        """)
    
    with col_h2:
        st.markdown("#### 🎁 [ 마스터 세팅 & 광고 대행 ]")
        st.info("비용: **운영 및 세팅비 무상** (광고 실비만 부담)")
        st.markdown("""
        * **네이버 파워링크** 무료 세팅 및 대행
        * **플레이스 최적화** 가이드 제공
        * **광고 효율 분석** 보고서 제공
        """)
    
    st.markdown("---")    

    # 아코디언 방식으로 숨겨두기
    with st.expander("📌 어떻게 뽑나요? (총 60곳 한정 - 클릭하여 확인)"):
        st.write("대형 매장만 유리하지 않도록 두 가지 기준으로 공평하게 선정합니다.")
        st.markdown("""
        🏆 **[ 올인원 풀케어 ] 선정 기준**
        * 꾸준히 라운즈/한샘렌즈를 많이 주문해 주신 누적 발주 랭킹 우수 매장

        🚀 **[ 마스터 세팅 ] 선정 기준**
        * "우리 매장은 작은데..." 걱정 마세요! 전월 대비 이번 달 발주량이 가장 많이 늘어난 '슈퍼 루키' 매장
        """)
