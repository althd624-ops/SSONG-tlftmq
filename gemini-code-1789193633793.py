import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="서논술형 답안 작성 및 자동 채점", page_icon="📝", layout="wide"
)

# 커스텀 CSS: 회색 박스(조건용) 스타일 정의
st.markdown(
    """
    <style>
    .condition-box {
        background-color: #f8f9fa;
        border-left: 5px solid #6c757d;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .condition-box p {
        margin-bottom: 8px;
        font-size: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("📝 서논술형 답안 작성 및 자동 채점 시스템")
st.caption(
    "2회고사 대비 모의 문항 연습 자료를 바탕으로 작성한 답안을 채점합니다."
)

# 사이드바: 문항 세트 선택
selected_set = st.sidebar.selectbox(
    "학습 및 채점할 문항 세트를 선택하세요",
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
    return [word for word in forbidden_words if word in text]


# ==========================================
# [세트 1] 채점 로직
# ==========================================
def grade_set_1(q1_1, q1_2, q1_3, q2_1, q2_2, q3_1_plan, q3_1_eff, q3_2_plan, q3_2_eff):
    results = {}

    # 서논술형 1 채점
    cond1_1 = check_synonyms(
        q1_1, ["쉬운", "친숙", "부담 없는", "노력이 필요 없는", "취미"]
    )
    cond1_2_solo = check_synonyms(q1_2, ["혼자", "독자적으로", "타인 없이"])
    cond1_2_focus = check_synonyms(q1_2, ["차분", "집중", "연습"])
    cond1_3 = "사회적 억제" in q1_3.strip()

    score1 = 0
    feedback1 = []
    if cond1_1:
        score1 += 1
    else:
        feedback1.append("1번 영역: 과제 특성(쉬운 과제/친숙한 과목) 서술 부족")

    if cond1_2_solo and cond1_2_focus:
        score1 += 1
    else:
        feedback1.append(
            "2번 영역: 혼자서 차분히 집중한다는 핵심 행동 서술 누락"
        )

    if cond1_3:
        score1 += 1
    else:
        feedback1.append("3번 영역: 정확한 용어 명칭은 사회적 억제입니다.")

    results["q1"] = {
        "score": score1,
        "max": 3,
        "feedback": (
            ["모든 요건을 충족하여 만점 처리되었습니다."]
            if score1 == 3
            else feedback1
        ),
    }

    # 서논술형 2 채점
    m1 = extract_method(q2_1)
    m2 = extract_method(q2_2)
    forbidden_set1 = ["카페인", "스마트폰", "독서실", "시험", "벼락치기"]
    ext_1 = contains_external_knowledge(q2_1 + " " + q2_2, forbidden_set1)

    score2 = 4
    feedback2 = []

    if ext_1:
        score2 -= 2
        feedback2.append(
            f"지문에 없는 외부 배경지식 단어가 사용되었습니다: {', '.join(ext_1)}"
        )

    if not m1 or not m2:
        score2 -= 1
        feedback2.append(
            "문장 끝 괄호 안에 사용한 설명 방법 명칭 표기가 누락되었습니다."
        )
    elif m1 == m2:
        score2 -= 2
        feedback2.append(
            f"서로 다른 설명 방법을 사용해야 합니다. (중복 표기: {m1})"
        )

    if m1 == "예시" and not check_synonyms(
        q2_1, ["예를 들어", "예컨대", "도서관", "커피숍", "모임"]
    ):
        feedback2.append("첫 번째 문장에서 예시 설명 방법의 특성이 충분히 나타나지 않았습니다.")
    if m2 == "대조" and not check_synonyms(
        q2_2, ["반면에", "달리", "어려운", "혼자"]
    ):
        feedback2.append("두 번째 문장에서 대조 설명 방법의 특성이 충분히 나타나지 않았습니다.")

    results["q2"] = {
        "score": max(0, score2),
        "max": 4,
        "feedback": (
            ["조건에 맞게 설명문이 잘 작성되었습니다."]
            if score2 == 4
            else feedback2
        ),
    }

    # 서논술형 3 채점
    score3 = 6
    feedback3 = []
    v_plan_ok = check_synonyms(q3_1_plan, ["혼자", "조용한", "방", "책상"])
    v_eff_ok = check_synonyms(
        q3_1_eff, ["집중", "차분", "필요", "도움", "효율"]
    )
    a_plan_ok = check_synonyms(
        q3_2_plan, ["소음 제거", "잔잔", "초침", "조용한", "클래식"]
    )
    a_eff_ok = check_synonyms(
        q3_2_eff, ["대비", "정적", "집중", "분위기", "극대화"]
    )

    if not (v_plan_ok and v_eff_ok):
        score3 -= 3
        feedback3.append(
            "시각 연출 및 효과: 어려운 과제를 할 때 필요한 혼자 집중하는 환경에 대한 서술이 부족합니다."
        )
    if not (a_plan_ok and a_eff_ok):
        score3 -= 3
        feedback3.append(
            "청각 연출 및 효과: 장면 1과 대비되는 조용하고 정적인 음향 서술이 부족합니다."
        )

    results["q3"] = {
        "score": max(0, score3),
        "max": 6,
        "feedback": (
            ["연출 계획과 연출 효과가 지문 내용에 맞게 작성되었습니다."]
            if score3 == 6
            else feedback3
        ),
    }

    return results


# ==========================================
# 화면 출력: 세트 1
# ==========================================
if selected_set == "세트 1: 사회적 촉진과 억제":

    # --- [서논술형 1] ---
    st.header("서논술형 1번 문항")

    # 1. 자료 (파란 상자)
    st.info("""
    📘 [제시문]
    기자: 심리학 용어인 사회적 촉진과 사회적 억제를 일상생활, 특히 우리의 학습에 어떻게 적용할 수 있을까요?
    전문가: 이 두 가지 개념을 알면 상황에 맞춰 유용하게 활용할 수 있습니다. 예를 들어, 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 어떨까요?
    기자: 음, 그냥 집에서 편하게 혼자 하는 게 집중이 잘되지 않을까요?
    전문가: 그렇지 않습니다. 오히려 집에서 혼자 하는 것보다는 커피숍이나 도서관에서 하는 것이 더 효율적일 수 있습니다. 평소 친숙하고 좋아하는 과목이라면 공부 모임을 만들어서 다른 사람들과 함께 공부하는 것도 좋은 방법이죠.
    기자: 그렇다면 어렵고 복잡한 과제를 할 때는 어떻게 해야 하나요?
    전문가: 그럴 때는 반대입니다. 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다.
    """)

    # 2. 문제 발문 (바탕 텍스트)
    st.markdown(
        "##### 윗글을 요약하여 표로 정리하고자 한다. 빈칸 1번부터 3번에 들어갈 내용을 지문에서 찾아 쓰시오."
    )

    # 답안 입력 칸
    c1, c2, c3 = st.columns(3)
    q1_1 = c1.text_input("1번 답안", "비교적 쉬운 취미 생활이나 과제")
    q1_2 = c2.text_input("2번 답안", "차분하게 혼자 집중하는 시간을 가짐")
    q1_3 = c3.text_input("3번 답안", "사회적 억제")

    st.markdown("---")

    # --- [서논술형 2] ---
    st.header("서논술형 2번 문항")

    # 1. 자료 (파란 상자)
    st.info("""
    📘 [주어진 첫 문장]
    과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.
    """)

    # 2. 문제 발문 (바탕 텍스트)
    st.markdown(
        "##### 윗글을 활용하여 과제 난이도에 따른 효율적인 학습 전략에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 작성하시오."
    )

    # 3. 조건 (회색 박스 + 이모지)
    st.markdown(
        """
    <div class="condition-box">
        <p><b>📌 [작성 조건]</b></p>
        <p>🔔 서로 다른 2가지의 설명 방법을 사용하여, 주어진 문장에 이어지는 문장을 1번과 2번에 각각 하나씩 작성할 것.</p>
        <p>⚠️ 윗글에 제시된 내용만을 활용하여 문장을 구성할 것. 지문에 없는 외부 배경지식을 활용할 경우 감점 처리함.</p>
        <p>🏷️ 각 문장의 끝에 자신이 사용한 설명 방법의 명칭을 괄호 안에 넣어서 표기할 것.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 답안 입력 칸
    q2_1 = st.text_area(
        "1번 문장 작성",
        "예를 들어, 쉬운 과제를 할 때는 도서관에서 친구들과 함께 공부하는 것이"
        " 좋다. (예시)",
    )
    q2_2 = st.text_area(
        "2번 문장 작성",
        "반면에 어렵고 복잡한 과제를 할 때는 혼자 차분하게 집중할 수 있는 공간이"
        " 효율적이다. (대조)",
    )

    st.markdown("---")

    # --- [서논술형 3] ---
    st.header("서논술형 3번 문항")

    # 1. 자료 (파란 상자)
    st.info("""
    📘 [영상 기획안]
    주제: 사회적 촉진과 억제를 활용한 스마트한 공부법

    [장면 1] 쉬운 과제를 할 때
    - 시각 요소: 백색소음이 있는 밝은 도서관에서 친구들과 가볍게 미소 지으며 공부하는 학생들의 모습을 넓은 화면으로 보여줌.
    - 청각 요소: 경쾌하고 리듬감 있는 배경음악과 함께 사람들의 가벼운 발소리와 책장 넘기는 소리를 깔아줌.

    [장면 2] 어려운 과제를 할 때
    - 시각 요소: A
    - 청각 요소: B
    """)

    # 2. 문제 발문 (바탕 텍스트)
    st.markdown(
        "##### 윗글을 바탕으로 상황에 맞는 학습 공간 선택법을 설명하는 영상을 제작하려 한다. 기획안의 A와 B에 들어갈 연출 계획과 효과를 작성하시오."
    )

    # 3. 조건 (회색 박스 + 이모지)
    st.markdown(
        """
    <div class="condition-box">
        <p><b>📌 [작성 조건]</b></p>
        <p>🎬 윗글을 참고하여 어려운 과제를 할 때 필요한 환경의 특성이 잘 드러나도록 A와 B에 들어갈 연출 계획을 세울 것.</p>
        <p>💡 자신이 설정한 시각 요소와 청각 요소가 글의 내용을 전달하는 데 어떤 효과가 있는지 각각 서술할 것.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 답안 입력 칸
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("시각 요소 A")
        q3_1_plan = st.text_input(
            "A 연출 계획", "조용한 방에서 학생 혼자 책상에 앉아 과제에 몰두함"
        )
        q3_1_eff = st.text_input(
            "A 연출 효과",
            "혼자 차분히 집중해야 하는 어려운 과제의 특성을 시각적으로 강조함",
        )
    with col_b:
        st.subheader("청각 요소 B")
        q3_2_plan = st.text_input(
            "B 연출 계획", "외부 소음을 제거하고 잔잔한 시계 초침 소리만 깔아줌"
        )
        q3_2_eff = st.text_input(
            "B 연출 효과",
            "장면 1과 대비를 이루어 정적이고 집중도 높은 분위기를 연출함",
        )

    # --- 채점 버튼 ---
    st.markdown("---")
    if st.button("🚀 작성한 답안 제출 및 채점하기", use_container_width=True):
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

        st.subheader("📊 답안 채점 결과 리포트")
        tot_score = res["q1"]["score"] + res["q2"]["score"] + res["q3"]["score"]
        st.metric(label="최종 점수", value=f"{tot_score} / 13점")

        for q_id, q_name in [
            ("q1", "서논술형 1번"),
            ("q2", "서논술형 2번"),
            ("q3", "서논술형 3번"),
        ]:
            with st.expander(
                f"{q_name} 결과 ({res[q_id]['score']} / {res[q_id]['max']}점)",
                expanded=True,
            ):
                for fb in res[q_id]["feedback"]:
                    if "충족" in fb or "완성" in fb or "맞게" in fb:
                        st.success(fb)
                    else:
                        st.error(fb)

elif selected_set == "세트 2: 정전기의 특징":
    st.header("세트 2 문항 화면")
    st.info("세트 1과 동일한 회색 조건 상자 및 파란 지문 상자 디자인이 적용됩니다.")

elif selected_set == "세트 3: AI 그림과 예술의 가치":
    st.header("세트 3 문항 화면")
    st.info("세트 1과 동일한 회색 조건 상자 및 파란 지문 상자 디자인이 적용됩니다.")