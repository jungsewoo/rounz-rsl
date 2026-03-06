import streamlit as st
import pandas as pd
import os
import datetime

# --- 프로모션 설정 (등급별 T/O 및 노출 배수 커트라인) ---
TO_MAP = {"VIP": 6, "GOLD": 4, "SILVER": 10}
LIMIT_MAP = {"VIP": 15, "GOLD": 10, "SILVER": 25}
# -----------------------------------------------------

st.set_page_config(page_title="2026 3~4월 렌즈프로모션 조회", page_icon="🌸", layout="wide")

FILE_PATH = '매장실적데이터.xlsx'

@st.cache_data
def load_data():
    return pd.read_excel(FILE_PATH)

try:
    df = load_data()
    mtime = os.path.getmtime(FILE_PATH)
    dt_mtime = datetime.datetime.fromtimestamp(mtime)
    update_time_str = dt_mtime.strftime("%m월 %d일 기준")
except Exception as e:
    st.error("⚠️ 데이터 파일을 찾을 수 없습니다. '매장실적데이터.xlsx' 파일을 확인해주세요.")
    st.stop()

if '26/03' in df.columns:
    df['26/03'] = df['26/03'].fillna(0)

if '프로모션 기준금액(최근3개월)' not in df.columns:
    st.error("⚠️ 엑셀 파일에 '프로모션 기준금액(최근3개월)' 열(Column)이 없습니다.")
    st.stop()
else:
    df['프로모션 기준금액(최근3개월)'] = df['프로모션 기준금액(최근3개월)'].fillna(0)


# --- 사이드바 메뉴 ---
st.sidebar.title("🌸 라운즈 프로모션")
st.sidebar.markdown("원하시는 메뉴를 선택하세요.")

menu = st.sidebar.radio("메뉴 이동", ["📊 우리 매장 실적 조회", "🎁 프로모션 혜택 안내"])

st.sidebar.markdown("---")
st.sidebar.info("본 프로모션은 라운즈 파트너 안경원을 대상으로 진행됩니다.")


# --- 메인 화면 UI 시작 ---
st.title("🌸 2026년 3~4월 마케팅 프로모션")
st.markdown("---")

# ==========================================
# [메뉴 1] 실적 조회 화면
# ==========================================
if menu == "📊 우리 매장 실적 조회":
    st.markdown("#### 우리 매장 무료 마케팅 혜택 당첨 확인하기")
    
    search_num = st.text_input("🏢 매장 사업자번호를 입력해주세요.", placeholder="숫자와 하이픈(-) 포함 (예: 123-45-67890)")

    if st.button("조회하기", use_container_width=True):
        if search_num:
            result = df[df['사업자번호'] == search_num]
            
            if not result.empty:
                store_name = result['매장명'].values[0]
                grade = result['등급'].values[0]
                current_amt = int(result['26/03'].values[0])
                avg_3month = int(result['프로모션 기준금액(최근3개월)'].values[0])
                
                grade_df = df[df['등급'] == grade].copy()
                grade_df['내등급순위'] = grade_df['26/03'].rank(method='min', ascending=False)
                
                user_rank = int(grade_df[grade_df['사업자번호'] == search_num]['내등급순위'].values[0])
                target_to = TO_MAP.get(grade, 10)
                display_limit = LIMIT_MAP.get(grade, 25)
                
                grade_sorted = grade_df.sort_values(by='26/03', ascending=False).reset_index(drop=True)
                target_idx = min(target_to, len(grade_sorted)) - 1
                target_amt = int(grade_sorted.loc[target_idx, '26/03']) if len(grade_sorted) > 0 else 0
                
                st.markdown(f"### 👤 **{store_name}** 원장님 현황")
                
                # 게이지바용 퍼센트 계산 로직
                # 💡 게이지바용 퍼센트 및 커스텀 디자인 세팅
                if target_amt > 0:
                    percent = int((current_amt / target_amt) * 100)
                else:
                    percent = 100
                
                # 게이지바가 100%를 넘어도 꽉 차보이게 처리
                display_percent = min(percent, 100)
                
                # 초록권(100% 이상)과 노랑권(100% 미만)의 게이지바 색상 다르게 (그라데이션)
                bar_color = "linear-gradient(90deg, #00b09b, #96c93d)" if percent >= 100 else "linear-gradient(90deg, #ff8a00, #e52e71)"
                
                custom_gauge_html = f"""
                <div style="width: 100%; background-color: #e6e6e6; border-radius: 20px; margin-top: 10px; margin-bottom: 5px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="width: {display_percent}%; height: 26px; background: {bar_color}; border-radius: 20px; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: 900; font-size: 14px; transition: width 0.5s ease-in-out;">
                        {percent}%
                    </div>
                </div>
                """

                if user_rank <= target_to:
                    st.success(f"🟢 **당첨 안정권 진입! (현재 {grade} {user_rank}위)**")
                    st.info(f"축하합니다! 현재 **[혜택 1: 올인원 풀케어] 당첨 안정권**입니다. 밑에서 무서운 속도로 추격 중이니 마감일까지 이 페이스를 꼭 유지해 주세요!")
                    
                    st.markdown("---")
                    
                    # 💡 임팩트 게이지바 & 문구 적용 (안정권)
                    st.markdown(custom_gauge_html, unsafe_allow_html=True)
                    st.markdown(f"**🎉 목표 달성! 당첨 합격선을 <span style='color:#00b09b;'>{current_amt - target_amt:,}원</span> 초과했습니다.**", unsafe_allow_html=True)
                    st.write("") # 간격 띄우기
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🏅 위탁 등급", grade)
                    col2.metric(f"🎯 현재 당첨 합격선 ({grade} {target_to}위)", f"{target_amt:,}원")
                    col3.metric(f"🛒 3월 발주액 ({update_time_str})", f"{current_amt:,}원")

                elif user_rank <= display_limit:
                    gap = target_amt - current_amt if target_amt > current_amt else 0
                    st.warning(f"🟡 **당첨 가시권! (현재 {grade} {user_rank}위)**")
                    st.error(f"원장님, 당첨 합격선({target_to}위) 진입까지 딱 **[{gap:,}원]** 모자랍니다! 이번 주 추가 발주 한 번이면 순위가 단번에 뒤집힙니다. 지금 바로 발주하세요!")
                    
                    st.markdown("---")
                    
                    # 💡 임팩트 게이지바 & 문구 적용 (가시권)
                    st.markdown(custom_gauge_html, unsafe_allow_html=True)
                    st.markdown(f"**🔥 당첨권 진입까지 딱 <span style='color:#ff8a00;'>{gap:,}원</span> 부족합니다! 조금만 더 텐션을 올려주세요!**", unsafe_allow_html=True)
                    st.write("") # 간격 띄우기
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🏅 위탁 등급", grade)
                    col2.metric(f"🎯 현재 당첨 합격선 ({grade} {target_to}위)", f"{target_amt:,}원")
                    col3.metric(f"🛒 3월 발주액 ({update_time_str})", f"{current_amt:,}원")

                else:
                    st.error(f"🚀 **슈퍼 루키 트랙 (역전의 기회!)**")
                    st.warning(f"누적 매출 랭킹이 부담스러우신가요? 걱정 마세요! 이번 달 발주를 확 늘려주시면 **[혜택 2: 전월 대비 급성장 트랙]** 당첨이 유력해집니다. 아래 3개월 평균 발주액을 뛰어넘어 보세요!")
                    
                    st.markdown("---")
                    # 하위권은 기존대로 3개월 평균 노출
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🏅 위탁 등급", grade)
                    col2.metric("📊 나의 3개월 평균액", f"{avg_3month:,}원")
                    col3.metric(f"🛒 3월 발주액 ({update_time_str})", f"{current_amt:,}원")
                
            else:
                st.error("⚠️ 일치하는 매장 정보가 없습니다. 사업자번호를 다시 확인해 주세요.")

# ==========================================
# [메뉴 2] 프로모션 상세 혜택 안내 화면
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
        * 원장님 매장을 네이버 검색 맨 위에 띄워드립니다. (비용은 라운즈가 냅니다!)
    * **2. 플레이스 완벽 세팅**
        * 동네 고객이 찾아오도록 네이버 지도 세팅을 전문가가 싹 고쳐드립니다.
    * **3. 1:1 전담 마케터 배정**
        * 궁금한 점은 언제든 다이렉트로 물어보세요.
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🎁 [ 마스터 세팅 & 광고 대행 ] - **차상위 40곳 한정**")
    st.info("비용: **세팅/대행 무상 지원 (단, 네이버 클릭 광고 실비는 안경원 부담)**")
    
    st.markdown("""
    * **1. 네이버 상단 노출 광고 대행 (무료 대행)**
        * 원장님 매장을 검색 상단에 띄우기 위한 광고 세팅과 운영을 본사가 무료로 대행해 드립니다. (광고 실비만 직접 충전)
    * **2. 플레이스 완벽 세팅 (무료)**
        * 우리 매장이 상단에 잘 노출될 수 있도록 지도 세팅을 전문가가 고쳐드립니다.
    * **3. 1:1 전담 마케터 배정**
        * 세팅부터 광고 효율 관리까지 꼼꼼하게 컨설팅해 드립니다.
    """)
    
    st.markdown("---")    

    # 💡 아코디언 UI 및 텍스트 변경 완료
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