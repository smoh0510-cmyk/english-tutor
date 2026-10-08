import streamlit as st
import time
import io
from gtts import gTTS
from google import genai
from google.genai import types

st.set_page_config(page_title="Tutor Alex", page_icon="🇺🇸", layout="centered")

# 음성 생성 캐싱 (반복 재생 시 렉 방지)
@st.cache_data
def text_to_speech(text):
    tts = gTTS(text=text, lang="en", tld="com")
    sound_file = io.BytesIO()
    tts.write_to_fp(sound_file)
    return sound_file.getvalue()

# 모바일 UI 스타일
st.markdown("""
<style>
    .kr-box { background-color: rgba(56, 189, 248, 0.15); border-left: 3px solid #38bdf8; padding: 10px 14px; border-radius: 8px; margin: 8px 0; font-size: 14px; color: #bae6fd; }
    .tip-box { background-color: rgba(16, 185, 129, 0.15); border-left: 3px solid #10b981; padding: 10px 14px; border-radius: 8px; margin: 8px 0; font-size: 14px; color: #a7f3d0; }
</style>
""", unsafe_allow_html=True)

st.title("🇺🇸 Tutor Alex")
st.caption("1:1 일상 회화 & 스몰토크 튜터 (Pre-Intermediate)")

# API 키 가져오기
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에 GEMINI_API_KEY를 등록하세요.")
    st.stop()

client = genai.Client(api_key=api_key)
CANDIDATE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]

system_instruction = """
당신은 1:1 영어 회화 수업을 진행하는 센스 있고 다정한 30대 미국인 튜터 'Alex'입니다.
학습자는 Pre-Intermediate 레벨의 한국인 성인 학습자입니다.

[규칙]
- 회사 일/업무 이야기는 하지 마세요.
- 주말 계획, 넷플릭스, 맛집, 취미 등 편안한 '일상 대화'로 1~2문장 짧게 티키타카를 하세요.
- 항상 답변 형식은 아래를 엄격히 지켜주세요:
[English]
(알렉스의 자연스러운 미국 일상 영어 1~2문장)

[한글 해석]
(위 영어 문장의 한국어 번역)

[💡 Alex의 교정 팁]
(학습자가 한 말을 더 세련된 미국식 표현으로 다듬은 1문장 및 칭찬)
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "[English]\nHey there! So good to see you! How's your week going? Doing anything fun lately?\n[한글 해석]\n안녕! 만나서 정말 반가워요! 이번 주 어떻게 보내고 있어요? 요즘 재미있는 일 있었어요?\n[💡 Alex의 교정 팁]\n수업 시작할 때 \"How's your week going?\"이라고 되물어보면 대화가 아주 자연스러워져요!"}
    ]

# 이전 대화 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        text = msg["content"]
        if msg["role"] == "assistant" and "[English]" in text:
            en_part = text.split("[한글 해석]")[0].replace("[English]", "").strip()
            kr_part = ""
            tip_part = ""
            if "[한글 해석]" in text:
                after_kr = text.split("[한글 해석]")[1]
                if "[💡 Alex의 교정 팁]" in after_kr:
                    kr_part = after_kr.split("[💡 Alex의 교정 팁]")[0].strip()
                    tip_part = after_kr.split("[💡 Alex의 교정 팁]")[1].strip()
                else:
                    kr_part = after_kr.strip()
            
            st.write(f"**{en_part}**")
            
            # 🔊 원어민 음성 플레이어 출력 (영어만 발음)
            try:
                audio_bytes = text_to_speech(en_part)
                st.audio(audio_bytes, format="audio/mp3")
            except Exception:
                pass

            if kr_part:
                st.markdown(f'<div class="kr-box">🇰🇷 <b>해석:</b> {kr_part}</div>', unsafe_allow_html=True)
            if tip_part:
                st.markdown(f'<div class="tip-box">💡 <b>Alex의 교정 팁:</b> {tip_part}</div>', unsafe_allow_html=True)
        else:
            st.write(text)

# 사용자 입력창
if prompt := st.chat_input("영어로 편하게 말해보세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Gemini 호출
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
            reply = "[English]\nSorry, can you say that again?\n[한글 해석]\n미안해요, 다시 한 번 말씀해 줄래요?"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
