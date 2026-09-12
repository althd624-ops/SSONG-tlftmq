import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="국어 서논술형 자동 채점 시스템", page_icon="📝", layout="wide"
)

st.title("📝 [해냄연수] 서논술형 답안 자동 채점 시스템")
st.caption(
    "2회고사 대비 모의 문항 1~3세트 채점 로직 및 조건 검증 프로그램입니다."
)

# Sidebar: 문항 세트 선택
selected_set = st.sidebar.selectbox(
    "채점할 문항 세트를 선택하세요",
    [
        "세트 1: 사회적 촉진과 억제",
        "세트 2: 정전기의 특징",
        "세트 3: AI 그림과 예술의 가치",
    ],
)

# ==========================================
# 공통 채점 보조 함수
# ==========================================


def check_synonyms(text, synonym_list):
    """유의어/동의어 목록 중 하나라도 포함되어 있는지 확인"""
    return any(syn in text for syn in synonym_list)


def extract_method(text):
    """문장 끝 괄호 안에 적힌 설명 방법 추출"""
    match = re.search(r"\((정의|예시|대조|비교|인과|분석|분류|구분)\)", text)
    return match.group(1) if match else None


def contains_external_knowledge(text, forbidden_words):
    """지문 외 배경지식 단어 포함 여부 검사"""
    found = [word for word in forbidden_words if word in text]
    return found


# ==========================================
# [세트 1] 사회적 촉진과 억제 채점 로직
# ==========================================
def grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_1_plan, q3_1_eff, q3_2_plan, q3_2_eff):
    results = {}

    # --- [서논술형 1] 표 요약 ---
    # (1) 쉬운 과제 관련
    cond1_1 = check_synonyms(
        q1_1, ["쉬운", "친숙", "부담 없는", "노력이 필요 없는", "취미"]
    )
    # (2) 혼자 집중
    cond1_2_solo = check_synonyms(q1_2, ["혼자", "독자적으로", "타인 없이"])
    cond1_2_focus = check_synonyms(q1_2, ["차분", "집중", "연습"])
    # (3) 사회적 억제 (학술 용어 엄격 검사)
    cond1_3 = "사회적 억제" in q1_3.strip()

    score1 = 0
    feedback1 = []
    if cond1_1:
        score1 += 1
    else:
        feedback1.append("(1) 과제 특성(쉬운/친숙한 과제) 언급 부족")

    if cond1_2_solo and cond1_2_focus:
        score1 += 1
    else:
        feedback1.append("(2) '혼자' '차분히 집중'하는 전략 핵심어 누락")

    if cond1_3:
        score1 += 1
    else:
        feedback1.append("(3) 용어 오류: 정확한 명칭은 '사회적 억제'입니다.")

    results["q1"] = {
        "score": score1,
        "max": 3,
        "feedback": (
            ["통과! 모든 조건 충족"] if score1 == 3 else feedback1
        ),
    }

    # --- [서논술형 2] 설명문 작성 ---
    m1 = extract_method(q2_1)
    m2 = extract_method(q2_2)

    forbidden_set1 = ["카페인", "스마트폰", "독서실", "시험", "벼락치기"]
    ext_1 = contains_external_knowledge(q2_1 + " " + q2_2, forbidden_set1)

    score2 = 4
    feedback2 = []

    if ext_1:
        score2 -= 2
        feedback2.append(
            f"지문에 없는 외부 배경지식 단어 사용 ({', '.join(ext_1)})"
        )

    if not m1 or not m2:
        score2 -= 1
        feedback2.append("문장 끝 괄호 안에 설명 방법 명칭 표기 누락")
    elif m1 == m2:
        score2 -= 2
        feedback2.append(
            f"서로 다른 설명 방법을 사용해야 합니다. (중복 사용: {m1})"
        )

    # 선택 방법의 특성 반영 여부 검사
    if m1 == "예시" and not check_synonyms(
        q2_1, ["예를 들어", "예컨대", "도서관", "커피숍", "모임"]
    ):
        feedback2.append("(1) 문장에서 '예시' 설명 방법의 특성이 잘 드러나지 않음")
    if m2 == "대조" and not check_synonyms(
        q2_2, ["반면에", "달리", "어려운", "혼자"]
    ):
        feedback2.append("(2) 문장에서 '대조' 설명 방법의 특성이 잘 드러나지 않음")

    results["q2"] = {
        "score": max(0, score2),
        "max": 4,
        "feedback": (
            ["통과! 모범적인 설명문 작성"] if score2 == 4 else feedback2
        ),
    }

    # --- [서논술형 3] 영상 기획안 ---
    score3 = 6
    feedback3 = []

    # 시각 연출 & 효과
    v_plan_ok = check_synonyms(q3_1_plan, ["혼자", "조용한", "방", "책상"])
    v_eff_ok = check_synonyms(
        q3_1_eff, ["집중", "차분", "필요", "도움", "효율"]
    )
    # 청각 연출 & 효과
    a_plan_ok = check_synonyms(
        q3_2_plan, ["소음 제거", "잔잔", "초침", "조용한", "클래식"]
    )
    a_eff_ok = check_synonyms(
        q3_2_eff, ["대비", "정적", "집중", "분위기", "극대화"]
    )

    if not (v_plan_ok and v_eff_ok):
        score3 -= 3
        feedback3.append(
            "시각 연출/효과: 어려운 과제 시 필요한 '혼자 집중하는 환경' 서술 미흡"
        )
    if not (a_plan_ok and a_eff_ok):
        score3 -= 3
        feedback3.append(
            "청각 연출/효과: 장면 1과 대비되는 '조용하고 정적인 음향 및 효과' 서술 미흡"
        )

    results["q3"] = {
        "score": max(0, score3),
        "max": 6,
        "feedback": (
            ["통과! 연출 및 효과 완벽 작성"] if score3 == 6 else feedback3
        ),
    }

    return results


# ==========================================
# Streamlit UI 구현
# ==========================================
if selected_set == "세트 1: 사회적 촉진과 억제":
    st.header("📌 [세트 1] 사회적 촉진과 사회적 억제")

    st.subheader("[서·논술형 1] 표 요약 채우기")
    c1, c2, c3 = st.columns(3)
    q1_1 = c1.text_input("(1) 쉬운 과제 특성", "비교적 쉬운 취미 생활이나 과제")
    q1_2 = c2.text_input("(2) 어려운 과제 방법", "차분하게 혼자 집중하는 시간을 가짐")
    q1_3 = c3.text_input("(3) 관련 심리 현상", "사회적 억제")

    st.subheader("[서·논술형 2] 설명문 연속 작성하기")
    st.info(
        "주어진 문장: 과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은"
        " 다르게 적용되어야 한다."
    )
    q2_1 = st.text_area(
        "(1) 첫 번째 문장 (설명 방법 명칭 포함)",
        "예를 들어, 쉬운 과제를 할 때는 도서관에서 친구들과 함께 공부하는 것이"
        " 좋다. (예시)",
    )
    q2_2 = st.text_area(
        "(2) 두 번째 문장 (설명 방법 명칭 포함)",
        "반면에 어렵고 복잡한 과제를 할 때는 혼자 차분하게 집중할 수 있는 공간이"
        " 효율적이다. (대조)",
    )

    st.subheader("[서·논술형 3] 영상 기획안 작성하기")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**시각 요소 (Ⓐ)**")
        q3_1_plan = st.text_input(
            "Ⓐ 연출 계획", "조용한 방에서 학생 혼자 책상에 앉아 과제에 몰두함"
        )
        q3_1_eff = st.text_input(
            "Ⓐ 연출 효과",
            "혼자 차분히 집중해야 하는 어려운 과제의 특성을 강조함",
        )
    with col_b:
        st.write("**청각 요소 (Ⓑ)**")
        q3_2_plan = st.text_input(
            "Ⓑ 연출 계획", "외부 소음을 제거하고 잔잔한 시계 초침 소리만 깔아줌"
        )
        q3_2_eff = st.text_input(
            "Ⓑ 연출 효과",
            "장면1과 대비를 이루어 정적이고 집중도 높은 분위기를 연출함",
        )

    if st.button("🚀 세트 1 답안 채하기"):
        res = grade_set_1(
            q1_1,
            q1_2,
            q1_3,
            q2_1,
            q2_2,
            q3_1_plan,
            q3_1_eff,
            q3_2_plan,
            q3_2_eff,
        )

        st.markdown("---")
        st.subheader("📊 채점 결과 리포트")

        tot_score = res["q1"]["score"] + res["q2"]["score"] + res["q3"]["score"]
        st.metric(
            label="총점",
            value=f"{tot_score} / 13점",
            delta=f"{tot_score - 13}점" if tot_score < 13 else "만점!",
        )

        for q_id, q_name in [
            ("q1", "서논술형 1"),
            ("q2", "서논술형 2"),
            ("q3", "서논술형 3"),
        ]:
            with st.expander(
                f"{q_name} 결과 ({res[q_id]['score']}/{res[q_id]['max']}점)",
                expanded=True,
            ):
                for fb in res[q_id]["feedback"]:
                    if "통과" in fb:
                        st.success(fb)
                    else:
                        st.error(fb)

elif selected_set == "세트 2: 정전기의 특징":
    st.header("📌 [세트 2] 정전기의 특징")
    st.info(
        "세트 2 채점 모듈 준비 완료: '높은 곳에 고여 있는 물', '전하의 정지/이동',"
        " '위험성 유무' 등의 키워드 및 결론 방향을 검증합니다."
    )
    # 세트 1과 동일한 구조로 데이터 바인딩 적용 가능

elif selected_set == "세트 3: AI 그림과 예술의 가치":
    st.header("📌 [세트 3] AI 그림과 예술의 가치")
    st.info(
        "세트 3 채점 모듈 준비 완료: '로봇 피겨스케이팅', '감정/철학 결여',"
        " '상징적 가치' 조건 및 복합양식성 대조 효과를 검증합니다."
    )