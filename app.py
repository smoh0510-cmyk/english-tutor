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
    # 💼 법무 & 컴플라이언스 '통합 이직 면접' 특화 (최상단)
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
    "📚 1:1 영어 수업 스몰토크",
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

INITIAL_GREETINGS = {
    # 💼 법무 & 컴플라이언스 통합 면접 4개
    "🎯 [면접] 법무 & 컴플라이언스 융합형 1분 자기소개": "[English]\nWelcome! We noticed on your resume that you wear both hats—leading corporate legal and compliance. Could you give us an overview of how you create synergy between the two roles?\n[한글 해석]\n환영합니다! 이력서를 보니 기업 법무와 컴플라이언스 두 역할을 모두 총괄하고 계시네요. 이 두 영역 간에 어떻게 시너지를 창출하시는지 전반적으로 소개해 주시겠어요?\n[💡 Alex의 교정 팁]\n'Wear both hats(두 가지 역할을 동시에 맡다)'라는 표현을 살려서 \"법무를 통한 사후 리스크 방어와 컴플라이언스를 통한 사전 예방을 융합하는 실무자\"라고 포지셔닝하면 면접관에게 엄청난 신뢰를 줍니다!\n[🎯 이렇게 대답해 보세요]\n• Wearing both hats allows me to protect the company legally while proactively instilling a culture of compliance. (두 역할을 모두 맡음으로써 회사를 법적으로 방어하는 동시에 사전 예방적 컴플라이언스 문화를 선제적으로 구축할 수 있습니다.)\n• My strength is providing a 360-degree risk assessment, covering both contract terms and regulatory frameworks. (제 강점은 계약 조항과 규제 체계를 아우르는 360도 전방위 리스크 평가를 제공하는 것입니다.)",

    "⚖️ [면접] Deal-maker(법무) vs Gatekeeper(컴플라이언스) 역할 충돌 조율": "[English]\nIn-house legal often acts as a deal-maker helping the business grow, while compliance acts as a gatekeeper. How do you handle situations where these two mandates clash?\n[한글 해석]\n사내 법무는 비즈니스 성장을 돕는 파트너(Deal-maker) 역할을 하지만, 컴플라이언스는 원칙을 지키는 문지기(Gatekeeper) 역할을 하죠. 이 두 가지 사명이 충돌할 때 어떻게 조율하시나요?\n[💡 Alex의 교정 팁]\n외국계 법무/컴플라이언스 면접의 핵심 단골 질문입니다! \"I don't see them as contradictory, but rather as risk-based commercial enablement\"(모순이 아니라 리스크 기반의 비즈니스 지원)이라는 프레임을 잡으세요.\n[🎯 이렇게 대답해 보세요]\n• I see compliance not as a road block, but as guardrails that allow the business to run faster safely. (컴플라이언스를 방해물이 아니라, 비즈니스가 안전하게 더 빨리 달릴 수 있게 돕는 가드레일로 봅니다.)\n• When conflicts arise, I help the business explore alternative structures to achieve their commercial goals within legal boundaries. (충돌이 생길 때는 법적 테두리 안에서 사업 목표를 달성할 수 있도록 거래 구조의 대안을 함께 모색합니다.)",

    "🔍 [면접] 계약 검토(법무)와 규제 준수(컴플라이언스) 동시 해결 사례": "[English]\nCould you walk us through a specific deal or project where you had to resolve high-stakes contract negotiations alongside strict regulatory compliance?\n[한글 해석]\n치열한 계약 조건 협상과 엄격한 규제 준수를 동시에 해결해야 했던 구체적인 프로젝트나 거래 사례를 말씀해 주시겠어요?\n[💡 Alex의 교정 팁]\nSTAR 기법(Situation-Task-Action-Result)을 쓰되, \"계약서상 책임 조항(Indemnity)을 방어하면서도 당국의 규제 가이드라인을 충족시켰다\"는 양면 성과를 보여주는 것이 핵심입니다.\n[🎯 이렇게 대답해 보세요]\n• In a major cross-border deal, I negotiated favorable liability caps while ensuring full alignment with local antitrust rules. (주요 크로스보더 딜에서 현지 반독점 규제에 완벽히 부합하도록 조율하면서도 유리한 책임 한도 조항을 협상해 냈습니다.)\n• By conducting dual-track legal review and compliance due diligence, we closed the transaction with zero regulatory exposure. (법무 검토와 컴플라이언스 실사를 병행(Dual-track)하여 규제 리스크 없이 거래를 성공적으로 클로징했습니다.)",

    "⏳ [면접] 급한 계약 검토와 컴플라이언스 모니터링 우선순위 배분": "[English]\nWhen business teams demand same-day contract turnarounds, how do you ensure ongoing compliance audits and routine governance don't take a backseat?\n[한글 해석]\n사업부에서 당일 계약 검토를 다급하게 요구할 때, 진행 중인 컴플라이언스 감사나 일상적인 거버넌스 업무가 뒤로 밀리지 않도록 어떻게 우선순위를 관리하시나요?\n[💡 Alex의 교정 팁]\n'Take a backseat(뒷전으로 밀리다)'에 대해 \"위험도 기반 트리아지(Risk-based Triage: 리스크 크기에 따라 긴급도를 분류하는 방식)\"와 \"표준 계약 템플릿을 통한 일상 업무 효율화\"를 언급하면 시니어 레벨의 역량이 증명됩니다.\n[🎯 이렇게 대답해 보세요]\n• I use a risk-based triage system to categorize urgent commercial needs versus core regulatory deadlines. (긴급한 상업적 니즈와 핵심 규제 마감기한을 위험도에 따라 분류(Triage)하여 관리합니다.)\n• I empower business units with standardized contract templates, freeing up my time for strategic compliance oversight. (표준 계약 템플릿으로 사업부의 자율성을 높여, 전략적 컴플라이언스 모니터링에 집중할 시간을 확보합니다.)",

    # 법무 실무
    "📜 해외 로펌(외부 변호사)과 자문 킥오프 미팅": "[English]\nHi Min, thanks for reaching out. We received your background memo. Could you walk us through the main legal concerns from your end?\n[한글 해석]\n안녕하세요 Min 담당자님, 연락 주셔서 감사합니다. 보내주신 배경 설명 메모 잘 받았습니다. 귀사 측에서 가장 우려하시는 주요 법적 쟁점을 간단히 설명해 주시겠어요?\n[💡 Alex의 교정 팁]\n외부 로펌과의 통화에서는 복잡한 문장 대신 \"Our main concern is liability exposure\"처럼 핵심 쟁점부터 두괄식으로 말하면 아주 프로페셔널해요!\n[🎯 이렇게 대답해 보세요]\n• Our main concern is the indemnification clause and potential liability. (저희의 주된 우려는 면책 조항과 잠재적 배상 책임 범위입니다.)\n• We need a quick risk assessment on local regulatory compliance. (현지 규제 컴플라이언스에 관한 빠른 리스크 평가가 필요합니다.)",

    "✍️ 계약 조건(Redline) 협상 & 부드럽게 이견 제시": "[English]\nThanks for sending over your markup. We noticed you made substantial changes to Clause 8 regarding liability caps. Is that a firm deal-breaker for you?\n[한글 해석]\n수정본(Markup) 보내주셔서 감사합니다. 책임 한도에 관한 제8조에 상당한 수정을 가하신 것을 확인했습니다. 그 조항이 절대 양보할 수 없는 협상 결렬 요건(Deal-breaker)인가요?\n[💡 Alex의 교정 팁]\n상대방의 무리한 요구에 \"No\"라고 직설적으로 말하기보다 \"We have some reservations about Clause 8\"(8조에 다소 우려가 있습니다)라고 완곡하게 표현하는 게 법무 협상의 정석이에요.\n[🎯 이렇게 대답해 보세요]\n• We have some reservations about unlimited liability, but we're open to finding a middle ground. (무제한 책임에는 다소 우려가 있지만, 절충안을 찾을 용의는 있습니다.)\n• That cap is critical for our risk tolerance, but let's see how we can tweak the wording. (그 한도는 저희 리스크 허용 기준상 매우 중요하지만, 문구를 어떻게 다듬을 수 있을지 논의해 보시죠.)",

    "⏳ 계약 검토 마감 일정 조율 (사업부/상대방)": "[English]\nHi Min, the business team is pushing to sign this NDA by tomorrow morning. Any chance we can expedite the legal review?\n[한글 해석]\n안녕하세요 Min 담당자님, 사업부에서 이 비밀유지계약(NDA)을 내일 아침까지 체결하겠다고 재촉하네요. 혹시 법무 검토를 좀 앞당겨 주실 수 있을까요?\n[💡 Alex의 교정 팁]\n검토를 재촉받을 때 \"I'm busy\" 대신 \"I'll prioritize this, but I need at least 24 hours for a thorough review\"처럼 합리적 턴어라운드 일정을 제시하세요.\n[🎯 이렇게 대답해 보세요]\n• I understand the urgency. Let me prioritize this and get back to you by 2 PM. (긴급한 상황 이해합니다. 우선순위로 올려서 오후 2시까지 회신드릴게요.)\n• I'll do a quick sanity check today, but formal sign-off might take until tomorrow. (오늘 1차 검토는 해보겠지만, 공식 승인은 내일까지 걸릴 수 있어요.)",

    "🛡️ 법적 리스크 완곡하게 설명 & 대안 제시하기": "[English]\nHey Min, we really want to launch this new promotional feature next month. Do you foresee any regulatory hurdles from a legal standpoint?\n[한글 해석]\n안녕하세요 Min 담당자님, 저희가 다음 달에 이 새로운 프로모션 기능을 꼭 출시하고 싶은데요. 법적 관점에서 예상되는 규제상 걸림돌이 있을까요?\n[💡 Alex의 교정 팁]\n리스크를 설명할 때 \"It is illegal\" 대신 \"From a regulatory standpoint, there is some gray area, so I recommend adding a disclaimer\"처럼 대안(Workaround)을 함께 주면 최고의 사내 법무 전문가로 인정받아요!\n[🎯 이렇게 대답해 보세요]\n• There's definitely some regulatory gray area here, but we can mitigate it with clear user consent. (확실히 규제상 회색지대가 있지만, 명확한 이용자 동의를 받으면 리스크를 완화할 수 있어요.)\n• Straight out doing this carries high exposure, but here's a viable workaround we could take. (그대로 진행하면 리스크가 크지만, 대신 취할 수 있는 현실적인 대안이 있습니다.)",

    "⚖️ 컴플라이언스 미팅 전 비즈니스 스몰토크": "[English]\nMorning! Thanks for jumping on early. How's everything on your end before we dive in?\n[한글 해석]\n좋은 아침이에요! 일찍 접속해 주셔서 감사해요. 안건 들어가기 전에 그쪽 상황은 좀 어떠세요?\n[💡 Alex의 교정 팁]\n미팅 시작 전 \"How's everything on your end?\"는 비즈니스 스몰토크의 정석입니다.\n[🎯 이렇게 대답해 보세요]\n• Can't complain! Just wrapped up the preliminary review. (더할 나위 없죠! 방금 사전 검토 끝냈어요.)\n• Pretty hectic, but ready when you are! (꽤 정신없지만, 전 준비됐습니다!)",

    # 비즈니스 & 일상
    "💻 화상 회의(Zoom) 연결 문제 & 오디오 체크": "[English]\nHey everyone! Can you hear and see me okay, or is there a bit of a lag on my end?\n[한글 해석]\n안녕하세요 여러분! 제 목소리랑 화면 잘 나오나요, 아니면 제 쪽에 렉이 좀 있나요?\n[💡 Alex의 교정 팁]\n화상 회의 시작할 때 \"Is there a lag on my end?\"는 아주 자연스러운 테크 체크 표현이에요!\n[🎯 이렇게 대답해 보세요]\n• You're coming through loud and clear! (아주 크고 또렷하게 잘 들려요!)\n• You were muted for a second, but good now. (잠깐 음소거되어 계셨는데 이제 잘 들려요.)",

    "🤝 네트워킹 행사에서 처음 만난 사람과 대화 트기": "[English]\nHi! Mind if I join you? Great turnout tonight, isn't it? What brought you to this event?\n[한글 해석]\n안녕하세요! 여기 같이 앉아도 될까요? 오늘 사람 정말 많이 왔네요, 그렇죠? 어떤 계기로 이 행사에 오셨어요?\n[💡 Alex의 교정 팁]\n\"What brought you to this event?\"는 네트워킹 행사에서 처음 만난 사람에게 묻는 가장 세련된 질문이에요.\n[🎯 이렇게 대답해 보세요]\n• Just looking to meet people in the industry! How about you? (업계 분들 좀 뵈려고요! 그쪽은요?)\n• A colleague recommended it, so I decided to check it out. (동료가 추천해 줘서 한번 와봤어요.)",

    "🤝 외국계 동료와 엘리베이터 1분 수다": "[English]\nHey! Long day, huh? Surviving the afternoon slump?\n[한글 해석]\n안녕! 오늘 하루 길죠? 오후의 나른한 식곤증은 잘 버티고 있어요?\n[💡 Alex의 교정 팁]\n\"Afternoon slump\"는 오후 2~4시쯤 찾아오는 나른함과 피로를 뜻해요.\n[🎯 이렇게 대답해 보세요]\n• Barely! Heading down for my third coffee. (간신히요! 3번째 커피 뽑으러 가는 길이에요.)\n• Almost done with the day, thank goodness! (하루가 거의 다 끝나가서 다행이에요!)",

    "🍻 퇴근 후 해피아워(맥주 한잔) 소셜 토크": "[English]\nCheers! You survived the week. What's your poison tonight—beer or cocktails?\n[한글 해석]\n짠! 이번 주도 살아남았네요. 오늘 밤 뭐 마실래요—맥주 아니면 칵테일?\n[💡 Alex의 교정 팁]\n\"What's your poison?\"은 술자리에서 '어떤 술 마실래?'라고 묻는 유쾌한 숙어예요.\n[🎯 이렇게 대답해 보세요]\n• A cold IPA sounds perfect right now! (시원한 IPA 맥주가 지금 딱이네요!)\n• I'll just go with a light beer tonight. (오늘 밤은 가벼운 맥주로 갈게요.)",

    "🥱 월요병 극복 & 퇴근길 피로 공감": "[English]\nUgh, Monday hit me like a ton of bricks today! How are your energy levels holding up?\n[한글 해석]\n으, 오늘 월요일이라 정말 온몸이 뻐근하네요! 기운은 좀 괜찮으세요?\n[💡 Alex의 교정 팁]\n\"Hit like a ton of bricks\"는 월요일 피로가 엄청나게 몰려올 때 쓰는 생생한 표현이에요.\n[🎯 이렇게 대답해 보세요]\n• Tell me about it, my brain is officially fried! (내 말이 그 말이에요, 머리가 완전 과부하 걸렸어요!)\n• Hanging in there, just counting down the hours. (그냥 버티는 중이에요, 퇴근 시간만 세고 있어요.)",

    "📚 1:1 영어 수업 스몰토크": "[English]\nHey there! So good to see you! How's your week going? Doing anything fun lately?\n[한글 해석]\n안녕! 만나서 반가워요! 이번 주 어떻게 보내고 있어요? 요즘 재미있는 일 있었어요?\n[💡 Alex의 교정 팁]\n수업 시작할 때 \"How's your week going?\"이라고 되물어보면 대화가 아주 자연스러워져요!\n[🎯 이렇게 대답해 보세요]\n• Pretty good, just surviving on coffee! (꽤 좋아요, 커피 힘으로 버티는 중이에요!)\n• Not much, just took it easy this week. (별거 없어요, 이번 주는 그냥 편하게 쉬었어요.)",

    "🍿 주말 계획 & 넷플릭스/취미 수다": "[English]\nTGIF! Any big plans for the weekend, or are you just gonna Netflix and chill?\n[한글 해석]\n드디어 불금이네요! 이번 주말에 특별한 계획 있어요, 아니면 집에서 넷플릭스 보며 쉴 건가요?\n[💡 Alex의 교정 팁]\n\"TGIF\"는 'Thank God It's Friday(불금이다!)'의 흔한 슬랭이에요!\n[🎯 이렇게 대답해 보세요]\n• Definitely catching up on some sleep! (무조건 밀린 잠부터 푹 자려고요!)\n• I'm planning to binge-watch a new series. (넷플릭스 신작 몰아볼 계획이에요.)",

    "☕ 미국 카페 & 음식점 주문하기": "[English]\nHi there! Welcome to Blue Bottle. What can I get started for you today?\n[한글 해석]\n안녕하세요! 블루보틀에 오신 걸 환영해요. 오늘 어떤 걸로 주문 도와드릴까요?\n[💡 Alex의 교정 팁]\n점원이 물어볼 땐 바로 \"Can I get ~\"으로 원하는 메뉴를 말씀하시면 돼요.\n[🎯 이렇게 대답해 보세요]\n• Can I get an iced vanilla latte with oat milk? (아이스 바닐라 라떼 오트 밀크로 한 잔 주시겠어요?)\n• Just a drip coffee to go, please. (드립 커피 한 잔 테이크아웃으로 부탁해요.)",

    "🍕 로컬 맛집 추천 & 배달 음식 이야기": "[English]\nI'm so starving right now! What's your ultimate go-to comfort food after a long day?\n[한글 해석]\n지금 배고파 죽겠어요! 하루 일과 끝나고 먹는 최고의 힐링 푸드(소울푸드)는 뭐예요?\n[💡 Alex의 교정 팁]\n\"Go-to comfort food\"는 지쳤을 때 생각나는 나만의 힐링 음식을 뜻해요.\n[🎯 이렇게 대답해 보세요]\n• You can't beat Korean fried chicken and beer! (치맥이 최고죠!)\n• Spicy tteokbokki is definitely my go-to. (매운 떡볶이가 무조건 제 힐링 푸드예요.)",

    "✈️ 해외 호텔 체크인 & 룸 변경 요청": "[English]\nGood afternoon, welcome to the Marriott. Are you checking in today?\n[한글 해석]\n안녕하세요, 메리어트 호텔에 오신 것을 환영합니다. 오늘 체크인 도와드릴까요?\n[💡 Alex의 교정 팁]\n예약자 이름을 밝히며 체크인 의사를 밝히시면 매끄럽습니다.\n[🎯 이렇게 대답해 보세요]\n• Yes, checking in under Min. (네, Min 이름으로 예약 체크인할게요.)\n• By any chance, is a quiet, high-floor room available? (혹시 조용한 고층 방으로 배정받을 수 있을까요?)",

    "🛂 공항 입국심사 & 수하물 문제 해결": "[English]\nPassport, please. What is the purpose of your visit, and how long do you plan to stay?\n[한글 해석]\n여권 보여주세요. 방문 목적이 무엇이며 며칠 동안 머무르실 예정인가요?\n[💡 Alex의 교정 팁]\n입국심사는 길게 말할 필요 없이 목적(Sightseeing/Business)과 체류 기간을 단답형으로 명확하게 말하는 게 가장 안전해요!\n[🎯 이렇게 대답해 보세요]\n• Just here for vacation, staying for about a week. (휴가차 왔고, 일주일 정도 머물 예정이에요.)\n• Actually, my checked bag didn't show up on the carousel. (실은 수하물 컨베이어 벨트에 제 짐이 안 나왔어요.)",

    "🚕 우버(Uber) 기사님과의 스몰토크": "[English]\nHey there! Heading to the airport? Traffic is pretty crazy today, huh?\n[한글 해석]\n안녕하세요! 공항 가시나요? 오늘 교통 체증이 꽤 심하네요, 그렇죠?\n[💡 Alex의 교정 팁]\n우버 기사님이 날씨나 교통 이야기를 꺼낼 때는 가볍게 맞장구쳐 주시면 돼요.\n[🎯 이렇게 대답해 보세요]\n• Yeah, hopefully we make it on time! (네, 제시간에 도착하면 좋겠네요!)\n• Crazy indeed! Friday traffic is the worst. (진짜 심하네요! 금요일 교통은 최악이에요.)",

    "🗺️ 길 찾기 & 현지 대중교통 이용 질문하기": "[English]\nExcuse me! You look like you know the area. Am I heading in the right direction for the subway station?\n[한글 해석]\n실례합니다! 이 동네를 잘 아실 것 같아서요. 제가 지하철역 쪽으로 제대로 가고 있는 게 맞나요?\n[💡 Alex의 교정 팁]\n길을 물어볼 때 \"Am I heading in the right direction for ~?\"라고 하면 교과서식 표현보다 훨씬 세련되게 들려요.\n[🎯 이렇게 대답해 보세요]\n• Yep, just walk straight for two blocks, and it's on your right. (네, 2블록만 직진하시면 오른쪽에 있어요.)\n• Actually, you're going the wrong way; it's back that way. (실은 반대 방향으로 가고 계세요. 저쪽 뒤편이에요.)",

    "🛍️ 쇼핑몰 사이즈 문의 & 교환/환불": "[English]\nHi! Just browsing today, or looking for something specific?\n[한글 해석]\n안녕하세요! 그냥 둘러보시는 중인가요, 아니면 찾는 물건이 따로 있으신가요?\n[💡 Alex의 교정 팁]\n혼자 보고 싶을 땐 \"Just browsing\"이라고 하시면 점원이 편하게 둡니다.\n[🎯 이렇게 대답해 보세요]\n• I'm just browsing, thank you! (그냥 둘러보는 중이에요, 감사합니다!)\n• Do you happen to have this in a medium? (혹시 이거 미디엄 사이즈 있나요?)",

    "🏥 병원 진료 & 약국에서 증상 설명하기": "[English]\nHi there, what seems to be the trouble today? Are you experiencing any pain or fever?\n[한글 해석]\n안녕하세요, 오늘 어디가 불편해서 오셨나요? 통증이나 열이 좀 있으신가요?\n[💡 Alex의 교정 팁]\n의사가 \"What seems to be the trouble?\"이라고 물어보면 증상의 부위와 느낌을 간결하게 말하면 돼요.\n[🎯 이렇게 대답해 보세요]\n• I have a pounding headache and a sore throat. (머리가 지끈거리고 목이 따끔거려요.)\n• I think I ate something bad; my stomach is really upset. (음식을 잘못 먹었는지 배탈이 심하게 났어요.)",

    "🌍 최근 이슈나 문화 차이에 대해 가볍게 의견 나누기": "[English]\nI was reading about how remote work culture differs between countries. How do people view work-life balance in Korea these days?\n[한글 해석]\n나라마다 재택근무 문화가 어떻게 다른지 기사를 읽고 있었는데요. 요즘 한국에서는 워라밸을 어떻게 생각하나요?\n[💡 Alex의 교정 팁]\n상대방 문화나 트렌드에 대해 물을 때 \"How do people view ~ these days?\"라고 하면 지적이고 매끄러운 대화가 시작돼요.\n[🎯 이렇게 대답해 보세요]\n• It's definitely becoming a top priority for younger generations. (젊은 층에선 확실히 최우선 순위가 되고 있어요.)\n• Things are shifting quickly, though long hours are still around. (빠르게 변하고 있지만, 아직 야근 문화가 남아있긴 해요.)"
}

st.sidebar.title("⚙️ 학습 설정")
selected_topic = st.sidebar.selectbox("대화 주제를 선택하세요:", TOPICS)

active_topic = selected_topic
if selected_topic == "✨ 내가 원하는 주제 직접 입력하기":
    custom_input = st.sidebar.text_input("원하는 상황을 입력하세요:", "예: 글로벌 외국계 기업 리걸 카운셀 면접")
    active_topic = f"자유 주제: {custom_input}"

def get_first_message(topic_name):
    default_greeting = f"[English]\nHey! I'm ready to chat about [{topic_name}]. What's on your mind?\n[한글 해석]\n안녕! [{topic_name}]에 대해 이야기할 준비가 됐어요. 오늘 무슨 이야기 나누고 싶어요?\n[💡 Alex의 교정 팁]\n자유 주제인 만큼 문법 고민 없이 편안하게 생각나는 단어부터 던져보세요!\n[🎯 이렇게 대답해 보세요]\n• Let's talk about it! (어디 한번 이야기해 봐요!)\n• Actually, I had an interesting experience recently. (사실 최근에 재미있는 경험이 있었어요.)"
    return INITIAL_GREETINGS.get(topic_name, default_greeting)

if "current_topic" not in st.session_state:
    st.session_state.current_topic = active_topic

if st.session_state.current_topic != active_topic:
    st.session_state.current_topic = active_topic
    first_msg = get_first_message(active_topic)
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

if st.sidebar.button("🗑️ 대화 기록 초기화 (새 대화)"):
    first_msg = get_first_message(active_topic)
    st.session_state.messages = [{"role": "assistant", "content": first_msg}]
    save_current_data(active_topic, st.session_state.messages)
    st.rerun()

st.title("🇺🇸 Tutor Alex")
st.caption(f"현재 상황: **{active_topic}**")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("Streamlit Secrets에 GEMINI_API_KEY를 등록하세요.")
    st.stop()

client = genai.Client(api_key=api_key)
CANDIDATE_MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]

system_instruction = f"""
당신은 센스 있고 유쾌한 30대 미국인 튜터/대화 상대/면접관 'Alex'입니다.
학습자는 한국 대기업/글로벌 기업에서 [기업 법무(Legal)와 컴플라이언스(Compliance)]를 모두 총괄하는 융합형 실무자(Pre-Intermediate 레벨)입니다.
현재 상황 설정: [{active_topic}]

[대화 규칙]
- 면접(Interview) 상황일 때는 '전문적이고 통찰력 있는 글로벌 기업의 General Counsel / 채용 총괄 면접관' 역할로 몰입하세요.
- 법무(계약, 협상, 법적 방어)와 컴플라이언스(내부통제, 규제 준수, 윤리경영)의 시너지와 균형 감각을 평가하되, 더 세련되고 설득력 있는 비즈니스 영어 표현으로 다듬어주세요.
- 1~2문장으로 짧고 리듬감 있게 티키타카를 하세요.
- 항상 학습자가 답변하기 편하도록 질문이나 맞장구로 말을 끝마치세요.

[답변 형식 (반드시 준수)]
[English]
(알렉스의 자연스러운 미국 일상/비즈니스/면접 영어 1~2문장)

[한글 해석]
(위 영어 문장의 자연스러운 한국어 번역)

[💡 Alex의 교정 팁]
(학습자가 한 말을 더 세련되고 경쟁력 있는 비즈니스/면접 영어 표현으로 다듬은 1문장 및 칭찬)

[🎯 이렇게 대답해 보세요]
(학습자가 바로 써먹을 수 있는 추천 답변 1~2문장과 한국어 뜻을 반드시 괄호 안에 병기)
"""

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    saved_data = load_saved_data()
    if isinstance(saved_data, dict) and saved_data.get("topic") == active_topic and len(saved_data.get("messages", [])) > 0:
        st.session_state.messages = saved_data["messages"]
    else:
        first_msg = get_first_message(active_topic)
        st.session_state.messages = [{"role": "assistant", "content": first_msg}]
        save_current_data(active_topic, st.session_state.messages)

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
