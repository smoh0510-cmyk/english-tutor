import streamlit as st
import time
import io
from gtts import gTTS
from google import genai
from google.genai import types

st.set_page_config(page_title="Tutor Alex", page_icon="🇺🇸", layout="centered")

# 음성 생성 캐싱
@st.cache_data
def text_to_speech(text):
    tts = gTTS(text=text, lang="en", tld="com")
    sound_file = io.BytesIO()
    tts.write_to_fp(sound_file)
    return sound_file.getvalue()

# 선명하고 가독성 좋은 스타일
st.markdown("""
<style>
    .kr-box { 
        background-color: #f0f9ff; 
        border-left: 4px solid #0284c7; 
        padding: 10px 14px; 
        border-radius: 8px; 
        margin: 8px 0; 
        font-size: 14px; 
        color: #0369a1 !important; 
        font-weight: 500;
    }
    .tip-box { 
        background-color: #f0fdf4; 
        border-left: 4px solid #16a34a; 
        padding: 10px 14px; 
        border-radius: 8px; 
        margin: 8px 0; 
        font-size: 14px; 
        color: #15803d !important; 
        font-weight: 500;
    }
    .hint-box {
        background-color: #fefce8;
        border-left: 4px solid #eab308;
        padding: 10px 14px;
        border-radius: 8px;
        margin: 8px 0;
        font-size: 13px;
        color: #854d0e !important;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 설정
st.sidebar.title("⚙️ 학습 설정")
topic = st.sidebar.selectbox(
    "대화 주제를 선택하세요:",
    [
        "1:1 영어 수업 스몰토크",
        "주말 계획 & 넷플릭스/취미 수다",
        "미국 카페 & 음식점 주문하기",
        "컴플라이언스 미팅 전 가벼운 스몰토크"
    ]
)

if st.sidebar.button("🔄 새 대화 시작하기"):
    st.session_state.messages = []
    st.rerun()

st.title("🇺🇸 Tutor Alex")
st.caption(f"현재 주제: **{topic}** (Pre-Intermediate 실전 스피킹)")

# API 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Streamlit Secrets에 GEMINI_API_KEY를 등록하세요.")
    st.stop()

client = genai.Client(api_key=api_key)
CANDIDATE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]

system_instruction = f"""
당신은 센스 있고 유쾌한 30대 미국인 튜터 'Alex'입니다.
학습자는 Pre-Intermediate 레벨의 한국인 직장인입니다.
현재 설정된 대화 상황: [{topic}]

[대화 규칙]
- 현재 설정된 상황에 맞게 1~2문장으로 짧고 리듬감 있게 티키타카를 하세요.
- 미국 30대들이 쓰는 자연스러운 구어체와 슬랭/관용구를 자연스럽게 섞어주세요.
- 항상 학습자가 답변하기 편하도록 가벼운 질문으로 말을 끝마치세요.

[답변 출력 형식 (반드시 엄격히 준수)]
[English]
(알렉스의 자연스러운 미국 일상 영어 1~2문장)

[한글 해석]
(위 영어 문장의 한국어 번역)

[💡 Alex의 교정 팁]
(학습자가 한 말을 더 세련된 미국식 표현으로 다듬은 1문장 및 칭찬)

[🎯 이렇게 대답해 보세요]
(학습자가 바로 써먹을 수 있는 추천 영어 답변 1~2문장과 한국어 뜻을 반드시 괄호 안에 병기할 것)
예시:
- Definitely catching up on some sleep! (무조건 밀린 잠부터 푹 자려고요!)
- I'm planning to binge-watch a new series. (새 시리즈 정주행할 계획이에요.)
"""

# 초기 인사 세팅 (한국어 해석 포함)
initial_greetings = {
    "1:1 영어 수업 스몰토크": "[English]\nHey there! So good to see you! How's your week going? Doing anything fun lately?\n[한글 해석]\n안녕! 만나서 정말 반가워요! 이번 주 어떻게 보내고 있어요? 요즘 재미있는 일 있었어요?\n[💡 Alex의 교정 팁]\n수업 시작할 때 \"How's your week going?\"이라고 되물어보면 대화가 아주 자연스러워져요!\n[🎯 이렇게 대답해 보세요]\n• Pretty good, just surviving on coffee! (꽤 좋아요, 그냥 커피 힘으로 버티는 중이에요!)\n• Not much, just took it easy this week. (별거 없어요, 이번 주는 그냥 편하게 쉬었어요.)",
    "주말 계획 & 넷플릭스/취미 수다": "[English]\nTGIF! Any big plans for the weekend, or are you just gonna Netflix and chill?\n[한글 해석]\n드디어 주말이네요! 이번 주말에 특별한 계획 있어요, 아니면 집에서 넷플릭스 보며 쉴 건가요?\n[💡 Alex의 교정 팁]\n\"TGIF\"는 'Thanks God It's Friday(불금이다!)'의 흔한 슬랭이에요!\n[🎯 이렇게 대답해 보세요]\n• Definitely catching up on some sleep! (무조건 밀린 잠부터 푹 자려고요!)\n• I'm planning to binge-watch a new series on Netflix. (넷플릭스 신작 시리즈 몰아볼 계획이에요.)",
    "미국 카페 & 음식점 주문하기": "[English]\nHi there! Welcome to Blue Bottle. What can I get started for you today?\n[한글 해석]\n안녕하세요! 블루보틀에 오신 걸 환영해요. 오늘 어떤 걸로 주문 도와드릴까요?\n[💡 Alex의 교정 팁]\n점원이 \"What can I get started for you?\"라고 하면 바로 원하는 음료를 말하면 돼요.\n[🎯 이렇게 대답해 보세요]\n• Can I get an iced vanilla latte with oat milk, please? (아이스 바닐라 라떼 오트 밀크로 한 잔 주시겠어요?)\n• Just a hot Americano to go, thanks! (따뜻한 아메리카노 테이크아웃 한 잔이요, 감사합니다!)",
    "컴플라이언스 미팅 전 가벼운 스몰토크": "[English]\nMorning! Thanks for joining early. How's everything on your end before we dive into the audit agenda?\n[한글 해석]\n좋은 아침이에요! 일찍 들어와 주셔서 감사해요. 감사 안건 들어가기 전에 그쪽 상황은 좀 어떠신가요?\n[💡 Alex의 교정 팁]\n본격적인 미팅 전 \"How's everything on your end?\"는 비즈니스 스몰토크의 정석이에요.\n[🎯 이렇게 대답해 보세요]\n• Can't complain! Just wrapped up the preliminary review. (더할 나위 없죠! 방금 사전 검토 마무리했어요.)\n• Things are a bit busy, but all good here. (조금 바쁘긴 한데, 이쪽은 다 순조롭습니다.)"
}

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = [
        {"role": "assistant", "content": initial_greetings.get(topic, initial_greetings["1:1 영어 수업 스몰토크"])}
    ]

# 메시지 출력 함수
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        text = msg["content"]
        if msg["role"] == "assistant" and "[English]" in text:
            en_part = text.split("[한글 해석]")[0].replace("[English]", "").strip()
            kr_part = ""
            tip_part = ""
            hint_part = ""

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

            # 🔊 발음 재생
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
            reply = "[English]\nSorry, could you say that one more time?\n[한글 해석]\n미안해요, 한 번만 다시 말씀해 주시겠어요?"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
