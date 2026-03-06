import streamlit as st
import pandas as pd
import datetime

# --- 프로모션 설정 ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
# -----------------------------------------------------

st.set_page_config(page_title="2026 3~4월 렌즈프로모션 조회", page_icon="🌸", layout="wide")

@st.cache_data(ttl=600)
def load_data():
    sheet_url = st.secrets["SHEET_URL"]
    csv_url = sheet_url.replace('/edit?usp=sharing', '/export?format=csv').replace('/edit', '/export?format=csv')
    df = pd.read_csv(csv_url)
    
    # 제목 공백 제거
    df.columns = [c.strip() for c in df.columns]
    
    # 💡 [핵심] 숫자 열 전처리: 콤마(,)와 '원' 제거 후 진짜 숫자로 변환
    target_col = '프로모션 기준금액(최근3개월)'
    numeric_cols = ['26/03', target_col]
    
    for col in numeric_cols:
        if col in df.columns:
            # 문자열로 변환 -> 콤마 제거 -> 숫자로 변환 (에러 시 0처리)
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 사업자번호 하이픈 제거
    if '사업자번호' in df.columns:
        df['사업자번호'] = df['사업자번호'].astype(str).str.replace('-', '', regex=False).str.strip()
    
    return df

try:
    df = load_data()
    # 한국 시간 기준 업데이트 (서버 시간 보정)
    now = datetime.datetime.now() + datetime.timedelta(hours=9)
    update_time_str = now.strftime("%m월 %d일 %H:%M 기준")
except Exception as e:
    st.error("⚠️ 데이터를 불러올 수 없습니다. 시트 공유 상태나 Secrets 설정을 확인해주세요.")
    st.stop()

# --- 사이드바 메뉴 ---
st.sidebar.title("🌸 라운즈 프로모션")
menu = st.sidebar.radio("메뉴 이동", ["📊 우리 매장 실적 조회", "🎁 프로모션 혜택 안내"])
st.sidebar.markdown("---")
st.sidebar.info("본 프로모션은 라운즈 파트너 안경원을 대상으로 진행됩니다.")

# --- 메인 화면 ---
st.title("🌸 2026년 3~4월 마케팅 프로모션")
st.markdown("---")

if menu == "📊 우리 매장 실적 조회":
    st.markdown("#### 우리 매장 무료 마케팅 혜택 당첨 확인하기")
    
    user_input = st.text_input("🏢 매장 사업자번호를 입력해주세요.", placeholder="하이픈(-) 없이 숫자만 입력 (예: 1234567890)")

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
                
                # 순위 계산
                grade_df = df[df['등급'] == grade].copy()
                grade_df['내등급순위'] = grade_df['26/03'].rank(method='min', ascending=False)
                user_rank = int(grade_df[grade_df['사업자번호'] == search_num]['내등급순위'].values[0])
                
                target_to = TO_MAP.get(grade, 10)
                display_limit = LIMIT_MAP.get(grade, 25)
                
                grade_sorted = grade_df.sort_values(by='26/03', ascending=False).reset_index(drop=True)
                target_idx = min(target_to, len(grade_sorted)) - 1
                target_amt = int(grade_sorted.loc[target_idx, '26/03']) if len(grade_sorted) > 0 else 0
                
                st.markdown(f"### 👤 **{store_name}** 원장님 현황")
                
                # 게이지바 및 퍼센트 계산
                percent = int((current_amt / target_amt) * 100) if target_amt > 0 else 100
                display_percent = min(percent, 100)
                bar_color = "linear-gradient(90deg, #00b09b, #96c93d)" if percent >= 100 else "linear-gradient(90deg, #ff8a00, #e52e71)"
                
                gauge_html = f"""
                <div style="width: 100%; background-color: #f0f2f6; border-radius: 20px; margin-top: 10px;">
                    <div style="width: {display_percent}%; height: 26px; background: {bar_color}; border-radius: 20px; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: 900; font-size: 14px;">
                        {percent}%
                    </div>
                </div>
                """

                if user_rank <= target_to:
                    st.success(f"🟢 **당첨 안정권 진입! (현재 {grade} {user_rank}위)**")
                    st.markdown(gauge_html, unsafe_allow_html=True)
                    st.markdown(f"**🎉 목표 달성! 현재 당첨 합격선을 <span style='color:#00b09b;'>{current_amt - target_amt:,}원</span> 초과했습니다.**", unsafe_allow_html=True)
                elif user_rank <= display_limit:
                    gap = target_amt - current_amt
                    st.warning(f"🟡 **당첨 가시권! (현재 {grade} {user_rank}위)**")
                    st.markdown(gauge_html, unsafe_allow_html=True)
                    st.markdown(f"**🔥 당첨권 진입까지 딱 <span style='color:#ff8a00;'>{gap:,}원</span> 부족합니다!**", unsafe_allow_html=True)
                else:
                    st.error("🚀 **슈퍼 루키 부문 (역전의 기회!)**")
                    st.warning("전월 대비 급성장 부문 당첨을 노려보세요!")
                
                st.write("")
                col1, col2, col3 = st.columns(3)
                col1.metric("🏅 위탁 등급", grade)
                col2.metric(f"🎯 현재 당첨 합격선 ({grade} {target_to}위)", f"{target_amt:,}원")
                col3.metric(f"🛒 3월 발주액 ({update_time_str})", f"{current_amt:,}원")
            else:
                st.error("⚠️ 일치하는 매장 정보가 없습니다. 숫자만 정확히 입력했는지 확인해 주세요.")

# ==========================================
# [메뉴 2] 프로모션 혜택 안내 화면
# ==========================================
elif menu == "🎁 프로모션 혜택 안내":
    st.markdown("### 🚨 네이버 지역 광고, 라운즈가 쏩니다!")
    st.markdown("""
어설픈 대행사에 돈 쓰지 마세요. 파트너담당 전문가가 직접 도와드립니다.

봄 시즌 렌즈 재고도 넉넉히 채우시고, 라운즈가 쏘는 든든한 마케팅 지원도 챙겨가세요!
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🎁 [ 올인원 풀케어 마케팅 ] - **상위 20곳 한정**") 
    st.info("비용: **전액 무상 지원 (광고비 0원!)**")
    
    st.markdown("""
    * **1. 네이버 상단 노출 무료 (2개월)**
    * **2. 플레이스 완벽 세팅**
    * **3. 1:1 전담 마케터 배정**
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🎁 [ 마스터 세팅 & 광고 대행 ] - **차상위 40곳 한정**")
    st.info("비용: **세팅/대행 무상 지원 (단, 네이버 클릭 광고 실비는 안경원 부담)**")
    
    st.markdown("""
    * **1. 네이버 상단 노출 광고 대행 (무료 대행)**
    * **2. 플레이스 완벽 세팅 (무료)**
    * **3. 1:1 전담 마케터 배정**
    """)
    
    st.markdown("---")    

    with st.expander("📌 어떻게 뽑나요? (총 60곳 한정)"):
        st.success("대형 매장만 유리한가요? 절대 아닙니다! 체급에 상관없이 두 가지 부문으로 공평하게 뽑습니다.")
        
        st.markdown("""
        🏆 **[ 올인원 풀케어 ] 선정 기준**
        * 꾸준히 라운즈/한샘렌즈를 많이 주문해 주신 누적 발주 랭킹 우수 매장 (등급별 T/O 배정)

        🚀 **[ 마스터 세팅 ] 선정 기준**
        * "우리 매장은 작은데..." 걱정 마세요! 이번 달 렌즈 주문량을 확 늘려주신 '전월 대비 급성장' 슈퍼 루키 매장
        
        ---
        💡 왼쪽 메뉴의 **[📊 우리 매장 실적 조회]**를 눌러 실시간 당첨 합격선을 확인하시고, 지금 바로 렌즈를 추가 발주하세요!
        """)

