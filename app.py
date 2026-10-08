import streamlit as st
import time
import io
import json
import os
from gtts import gTTS
from google import genai
from google.genai import types

st.set_page_config(page_title="Tutor Alex", page_icon="🇺🇸", layout="centered")

HISTORY_FILE = "chat_history.json"

def load_saved_data():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}

def save_current_data(topic, messages):
    try:
        data = {"topic": topic, "messages": messages}
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

@st.cache_data
def text_to_speech(text):
    tts = gTTS(text=text, lang="en", tld="com")
    sound_file = io.BytesIO()
    tts.write_to_fp(sound_file)
    return sound_file.getvalue()

st.markdown("""
<style>
    .kr-box { background-color: #f0f9ff; border-left: 4px solid #0284c7; padding: 10px 14px; border-radius: 8px; margin: 8px 0; font-size: 14px; color: #0369a1 !important; font-weight: 500; }
    .tip-box { background-color: #f0fdf4; border-left: 4px solid #16a34a; padding: 10px 14px; border-radius: 8px; margin: 8px 0; font-size: 14px; color: #15803d !important; font-weight: 500; }
    .hint-box { background-color: #fefce8; border-left: 4px solid #eab308; padding: 10px 14px; border-radius: 8px; margin: 8px 0; font-size: 13px; color: #854d0e !important; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

TOPICS = [
    # 🎓 영어 수업 전용
    "☕ [수업] 튜터와 수업 전 5분 가벼운 일상 스몰토크",
    "🙋 [수업] 수업 중 질문 & 다시 말해달라고 요청하기",
    "🎯 [수업] 뉘앙스 차이 질문 & 수업 피드백 요청하기",

    # 💼 법무 & 컴플라이언스 이직 면접
    "🎯 [면접] 법무 & 컴플라이언스 융합형 1분 자기소개",
    "⚖️ [면접] Deal-maker(법무) vs Gatekeeper(컴플라이언스) 역할 충돌 조율",
    "🔍 [면접] 계약 검토(법무)와 규제 준수(컴플라이언스) 동시 해결 사례",
    "⏳ [면접] 급한 계약 검토와 컴플라이언스 모니터링 우선순위 배분",

    # ⚖️ 법무 & 컴플라이언스 실무
    "📜 해외 로펌(외부 변호사)과 자문 킥오프 미팅",
    "✍️ 계약 조건(Redline) 협상 & 부드럽게 이견 제시",
    "⏳ 계약 검토 마감 일정 조율 (사업부/상대방)",
    "🛡️ 법적 리스크 완곡하게 설명 & 대안 제시하기",
    "⚖️ 컴플라이언스 미팅 전 비즈니스 스몰토크",
    
    # 💻 비즈니스 & 오피스
    "💻 화상 회의(Zoom) 연결 문제 & 오디오 체크",
    "🤝 네트워킹 행사에서 처음 만난 사람과 대화 트기",
    "🤝 외국계 동료와 엘리베이터 1분 수다",
    "🍻 퇴근 후 해피아워(맥주 한잔) 소셜 토크",
    "🥱 월요병 극복 & 퇴근길 피로 공감",
    
    # ✈️ 일상 & 여행
    "🍿 주말 계획 & 넷플릭스/취미 수다",
    "☕ 미국 카페 & 음식점 주문하기",
    "🍕 로컬 맛집 추천 & 배달 음식 이야기",
    "✈️ 해외 호텔 체크인 & 룸 변경 요청",
    "🛂 공항 입국심사 & 수하물 문제 해결",
    "🚕 우버(Uber) 기사님과의 스몰토크",
    "🗺️ 길 찾기 & 현지 대중교통 이용 질문하기",
    "🛍️ 쇼핑몰 사이즈 문의 & 교환/환불",
    "🏥 병원 진료 & 약국에서 증상 설명하기",
    "🌍 최근 이슈나 문화 차이에 대해 가볍게 의견 나누기",
    
    # ✨ 자유 입력
    "✨ 내가 원하는 주제 직접 입력하기"
]

st.sidebar.title("⚙️ 학습 설정")
selected_topic = st.sidebar.selectbox("대화 주제를 선택하세요:", TOPICS)

active_topic = selected_topic
if selected_topic == "✨ 내가 원하는 주제 직접 입력하기":
    custom_input = st.sidebar.text_input("원하는 상황을 입력하세요:", "예: 해외 출장 비행기 옆자리 대화")
    active_topic = f"자유 주제: {custom_input}"

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Streamlit Secrets에 GEMINI_API_KEY를 등록하세요.")
    st.stop()

client = genai.Client(api_key=api_key)
CANDIDATE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]

system_instruction = f"""
당신은 센스 있고 유쾌한 30대 미국인 튜터/대화 상대/면접관 'Alex'입니다.
학습자는 한국인 직장인(Pre-Intermediate 레벨)입니다.
현재 설정된 주제: [{active_topic}]

[★ 역할 및 대화 절대 규칙]
1. 주제가 '[수업]'으로 시작할 때:
   - 절대 회사 일이나 심각한 법률/컴플라이언스 업무 이야기를 꺼내지 마세요!
   - 당신은 다정하고 유쾌한 '영어 과외선생님'입니다.
   - 수업 시작 전에는 커피, 날씨, 오늘 하루 컨디션 같은 편안한 100% 일상 스몰토크만 하세요.
   - 학생이 수업 관련 질문이나 요청을 연습할 수 있도록 진짜 영어 수업 상황으로 친절하게 반응하세요.

2. 주제가 '[면접]' 또는 '[법무/컴플라이언스]'일 때만:
   - 해당 전문 비즈니스/면접관 역할로 몰입하여 비즈니스 대화를 나누세요.

3. 공통 규칙:
   - 1~2문장으로 짧고 리듬감 있게 티키타카를 하세요.
   - 항상 학습자가 답변하기 편하도록 질문이나 맞장구로 말을 끝마치세요.

[답변 형식 (반드시 준수)]
[English]
(알렉스의 자연스러운 미국 구어체 1~2문장)

[한글 해석]
(위 영어 문장의 자연스러운 한국어 번역)

[💡 Alex의 교정 팁]
(학습자가 한 말을 더 자연스러운 표현으로 다듬은 1문장 및 칭찬)

[🎯 이렇게 대답해 보세요]
(학습자가 바로 써먹을 수 있는 추천 답변 1~2문장과 한국어 뜻을 반드시 괄호 안에 병기)
"""

# ★ 완전히 개선된 상황별 밀착 첫 대사 생성 함수
def generate_fresh_greeting(topic_name):
    prompt = f"""
    현재 선택된 주제: [{topic_name}]

    당신은 30대 미국인 Alex입니다.
    선택된 [{topic_name}]의 **구체적인 상황에 100% 밀착된 첫 대사**를 1~2문장으로 건네세요.

    ⚠️ 절대 금지 및 주의사항:
    - 무조건 "Happy Friday eve"나 "How's your energy level" 같은 뻔한 요일 안부만 앵무새처럼 반복하는 것을 엄격히 금지합니다!
    - 반드시 선택된 주제의 '진짜 상황'으로 즉시 시작하세요:
      * '🙋 수업 중 질문 & 다시 말해달라고 요청하기' 주제 ➔ "좋아요, 오늘 수업 대화문을 볼 텐데 제가 말이 빠르거나 안 들리면 언제든 손들고 멈춰주세요, 알겠죠?"처럼 학생이 질문/요청을 연습할 수 있는 상황 조성.
      * '🎯 뉘앙스 차이 질문 & 수업 피드백' 주제 ➔ "반가워요! 평소에 미묘하게 헷갈렸던 영어 단어나 오늘 집중적으로 교정받고 싶은 표현이 있나요?"처럼 질문 유도.
      * '☕ 수업 전 5분 스몰토크' 주제 ➔ 오늘 마신 커피, 퇴근길, 가벼운 날씨 수다 등으로 가볍게 시작.
      * '면접' 관련 주제 ➔ 면접관으로서 해당 면접 질문을 직접 던지며 시작.
      * '카페 주문' 주제 ➔ 바리스타로서 주문을 물어보며 시작.

    반드시 아래 출력 형식을 지키세요:
    [English]
    (상황에 100% 밀착된 첫 대사 1~2문장)

    [한글 해석]
    (자연스러운 한국어 번역)

    [💡 Alex의 교정 팁]
    (이 상황에서 유용한 리액션/표현 팁 1문장)

    [🎯 이렇게 대답해 보세요]
    (학습자가 바로 써먹을 수 있는 추천 답변 1~2문장과 한국어 뜻을 반드시 괄호 안에 병기)
    """
    for model_name in CANDIDATE_MODELS:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.85
                )
            )
            return res.text
        except Exception:
            time.sleep(0.5)
            continue
    return "[English]\nAlright, let's get started! If you have any questions, just let me know anytime, okay?\n[한글 해석]\n좋아요, 시작해 보죠! 질문이 있으시면 언제든 편하게 말씀해 주세요, 알겠죠?\n[💡 Alex의 교정 팁]\n수업 중 질문할 준비가 됐다는 신호를 보내보세요!\n[🎯 이렇게 대답해 보세요]\n• Sounds good, I'm ready! (좋아요, 준비됐어요!)"

# 주제 변경 즉시 새 대화 생성
if "current_topic" not in st.session_state:
    st.session_state.current_topic = active_topic

if st.session_state.current_topic != active_topic:
    st.session_state.current_topic = active_topic
    with st.spinner("Alex가 상황에 맞는 새로운 첫 인사를 준비하고 있습니다..."):
        first_msg = generate_fresh_greeting(active_topic)
    st.session_state.messages = [{"role": "assistant", "content": first_msg}]
    save_current_data(active_topic, st.session_state.messages)
    st.rerun()

def generate_review_text(messages):
    lines = [f"=== Tutor Alex 영어 학습 복습 노트 ({active_topic}) ===\n"]
    for m in messages:
        role = "나(You)" if m["role"] == "user" else "알렉스(Alex)"
        lines.append(f"[{role}]:\n{m['content']}\n" + "-"*40)
    return "\n".join(lines)

st.sidebar.markdown("---")
st.sidebar.subheader("💾 학습 기록 관리")

if "messages" in st.session_state and len(st.session_state.messages) > 1:
    review_data = generate_review_text(st.session_state.messages)
    st.sidebar.download_button(
        label="📥 오늘 대화 & 팁 저장하기",
        data=review_data,
        file_name="today_english_lesson.txt",
        mime="text/plain"
    )

if st.sidebar.button("🔄 새로운 대화 시작하기"):
    with st.spinner("Alex가 새로운 대화를 시작합니다..."):
        first_msg = generate_fresh_greeting(active_topic)
    st.session_state.messages = [{"role": "assistant", "content": first_msg}]
    save_current_data(active_topic, st.session_state.messages)
    st.rerun()

st.title("🇺🇸 Tutor Alex")
st.caption(f"현재 상황: **{active_topic}**")

# 초기 로딩 시에도 해당 상황에 맞는 인사 생성
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    saved_data = load_saved_data()
    if isinstance(saved_data, dict) and saved_data.get("topic") == active_topic and len(saved_data.get("messages", [])) > 0:
        st.session_state.messages = saved_data["messages"]
    else:
        with st.spinner("Alex가 첫 인사를 건네는 중입니다..."):
            first_msg = generate_fresh_greeting(active_topic)
        st.session_state.messages = [{"role": "assistant", "content": first_msg}]
        save_current_data(active_topic, st.session_state.messages)

# 메시지 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        text = msg["content"]
        if msg["role"] == "assistant" and "[English]" in text:
            en_part = text.split("[한글 해석]")[0].replace("[English]", "").strip()
            kr_part, tip_part, hint_part = "", "", ""

            try:
                if "[한글 해석]" in text:
                    kr_part = text.split("[한글 해석]")[1].split("[💡 Alex의 교정 팁]")[0].strip()
                if "[💡 Alex의 교정 팁]" in text:
                    tip_part = text.split("[💡 Alex의 교정 팁]")[1].split("[🎯 이렇게 대답해 보세요]")[0].strip()
                if "[🎯 이렇게 대답해 보세요]" in text:
                    hint_part = text.split("[🎯 이렇게 대답해 보세요]")[1].strip()
            except Exception:
                pass

            st.write(f"### {en_part}")

            try:
                audio_bytes = text_to_speech(en_part)
                st.audio(audio_bytes, format="audio/mp3")
            except Exception:
                pass

            if kr_part:
                st.markdown(f'<div class="kr-box">🇰🇷 <b>해석:</b> {kr_part}</div>', unsafe_allow_html=True)
            if tip_part:
                st.markdown(f'<div class="tip-box">💡 <b>Alex의 교정 팁:</b> {tip_part}</div>', unsafe_allow_html=True)
            if hint_part:
                with st.expander("🎯 뭐라고 답할지 막힐 때? (답변 힌트 보기)"):
                    st.markdown(f'<div class="hint-box">{hint_part}</div>', unsafe_allow_html=True)
        else:
            st.write(text)

# 사용자 입력 처리
if prompt := st.chat_input("영어로 편하게 말해보세요 (키보드 마이크 추천)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_current_data(active_topic, st.session_state.messages)
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        history = []
        for m in st.session_state.messages:
            r = "user" if m["role"] == "user" else "model"
            history.append({"role": r, "parts": [{"text": m["content"]}]})

        reply = ""
        for model_name in CANDIDATE_MODELS:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=history,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.8
                    )
                )
                reply = res.text
                break
            except Exception:
                time.sleep(0.5)
                continue

        if not reply:
            reply = "[English]\nSorry, could you say that again?\n[한글 해석]\n미안해요, 한 번만 다시 말씀해 주시겠어요?"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_current_data(active_topic, st.session_state.messages)
        st.rerun()
