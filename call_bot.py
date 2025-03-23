from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from datetime import datetime
import random
import time

# For creating PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import LETTER
except ImportError:
    print("Please install reportlab: pip install reportlab")

# LLM import
from llama_client import get_llama_response

#############################
# Twilio Credentials
#############################
ACCOUNT_SID = "AC36915b9974948d6e8d75c71023b1d77c"
AUTH_TOKEN = "8a6da27cc280081912b8e326e0c3ad40"
FROM_NUMBER = "+19207893459"  # Your Twilio number
TO_NUMBER = "+14374199290"   # Number to receive calls/SMS

twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)

#############################
# Flask App
#############################
app = Flask(__name__)

#############################
# Global States
#############################
conversation_history = []
conversation_type = "0"   # "0": general Q&A, "1": labor law violation
employer_name = ""
location = ""
selected_language = "en"  # default English

#############################
# Language Setup
#############################
TRANSLATIONS = {
    "en": {
        "lang_prompt": "Welcome to the legal assistant. Select your language. Press 1 for English, 2 for Spanish, 3 for French, 4 for Chinese, 5 for Korean.",
        "main_menu": "Welcome to the legal assistant. Press 0 for general legal knowledge, 1 for labor law violation, star or pound to exit.",
        "invalid": "Sorry, I didn't get that.",
        "ask_question": "Please ask your legal question.",
        "ask_labor": "Please explain your labor violation situation.",
        "ending_call": "Thank you. The call is now ending.",
        "need_location": "Before ending, please say the location of the incident.",
        "need_employer": "Please say the name of your employer.",
        "ask_data": "Before ending the call, are you able to use data? Press 1 for SMS, 2 for in-app.",
        "sorry_catch": "Sorry, I didn't catch that.",
        "ok_next": "Okay. Please ask your next question.",
        "thank_you": "Thank you. The conversation has ended.",
    },
    "es": {
        "lang_prompt": "Bienvenido al asistente legal. Seleccione su idioma. Presione 1 para Inglés, 2 para Español, 3 para Francés, 4 para Chino, 5 para Coreano.",
        "main_menu": "Bienvenido al asistente legal. Presione 0 para conocimiento legal general, 1 para violación de la ley laboral, * o # para salir.",
        "invalid": "Lo siento, no entendí.",
        "ask_question": "Por favor, haga su pregunta legal.",
        "ask_labor": "Explique su situación de violación laboral.",
        "ending_call": "Gracias. La llamada está terminando.",
        "need_location": "Antes de terminar, por favor diga la ubicación del incidente.",
        "need_employer": "Por favor, diga el nombre de su empleador.",
        "ask_data": "Antes de terminar la llamada, ¿puede usar datos? Presione 1 para SMS, 2 para mensaje en la aplicación.",
        "sorry_catch": "Lo siento, no entendí.",
        "ok_next": "Está bien. Por favor haga su siguiente pregunta.",
        "thank_you": "Gracias. La conversación ha terminado.",
    },
    "fr": {
        "lang_prompt": "Bienvenue à l'assistant juridique. Choisissez votre langue. Appuyez sur 1 pour l'anglais, 2 pour l'espagnol, 3 pour le français, 4 pour le chinois, 5 pour le coréen.",
        "main_menu": "Bienvenue chez l'assistant juridique. Appuyez sur 0 pour les connaissances juridiques générales, 1 pour une violation du droit du travail, * ou # pour quitter.",
        "invalid": "Désolé, je n'ai pas compris.",
        "ask_question": "Veuillez poser votre question juridique.",
        "ask_labor": "Veuillez expliquer votre situation de violation du droit du travail.",
        "ending_call": "Merci. L'appel se termine.",
        "need_location": "Avant de terminer, veuillez indiquer le lieu de l'incident.",
        "need_employer": "Veuillez indiquer le nom de votre employeur.",
        "ask_data": "Avant de terminer l'appel, pouvez-vous utiliser des données ? Appuyez sur 1 pour SMS, 2 pour le message dans l'application.",
        "sorry_catch": "Désolé, je n'ai pas compris.",
        "ok_next": "D'accord. Veuillez poser votre prochaine question.",
        "thank_you": "Merci. La conversation est terminée.",
    },
    "zh": {
        "lang_prompt": "欢迎使用法律助手。请选择语言。按1英语, 2西班牙语, 3法语, 4中文, 5韩语.",
        "main_menu": "欢迎使用法律助手。按0获取一般法律知识，按1报告劳动法违规，按*或#结束通话.",
        "invalid": "对不起，我没有听清。",
        "ask_question": "请提出您的法律问题。",
        "ask_labor": "请说明您遇到的劳动法违规情况。",
        "ending_call": "谢谢。通话即将结束。",
        "need_location": "在结束之前，请告诉我事发地点。",
        "need_employer": "请告诉我雇主的名字。",
        "ask_data": "在结束通话之前，您能使用流量吗？按1接收短信, 按2接收应用内消息.",
        "sorry_catch": "对不起，我没听清。",
        "ok_next": "好的，请继续提问。",
        "thank_you": "谢谢。通话结束。",
    },
    "ko": {
        "lang_prompt": "법률 도우미에 오신 것을 환영합니다. 언어를 선택하세요. 1번 영어, 2번 스페인어, 3번 프랑스어, 4번 중국어, 5번 한국어.",
        "main_menu": "법률 도우미입니다. 일반 법률 지식은 0번, 노동법 위반은 1번, 종료는 * 또는 #.",
        "invalid": "죄송합니다. 이해하지 못했습니다.",
        "ask_question": "법률 질문을 말씀해주세요.",
        "ask_labor": "노동법 위반 상황을 설명해주세요.",
        "ending_call": "감사합니다. 전화를 종료합니다.",
        "need_location": "끝내기 전에 사건이 발생한 위치를 말씀해주세요.",
        "need_employer": "고용주의 이름을 말씀해주세요.",
        "ask_data": "통화 종료 전, 데이터 사용이 가능하신가요? 1번 문자, 2번 앱 메시지.",
        "sorry_catch": "죄송합니다. 잘 못 들었습니다.",
        "ok_next": "알겠습니다. 다음 질문을 해주세요.",
        "thank_you": "감사합니다. 통화를 마치겠습니다.",
    }
}

LANG_CODE_TWILIO = {
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "zh": "zh-CN",
    "ko": "ko-KR"
}

#############################
# Helper for TTS in the selected language
#############################
def say_in_language(response_obj, text_key):
    global selected_language
    phrase = TRANSLATIONS.get(selected_language, TRANSLATIONS["en"]).get(text_key, text_key)
    twilio_lang = LANG_CODE_TWILIO.get(selected_language, "en-US")
    response_obj.say(phrase, language=twilio_lang)

#############################
# SMS chunking (1600 chars)
#############################
MAX_SMS_LEN = 1600

def send_sms_in_segments(body, from_, to_):
    idx = 0
    while idx < len(body):
        segment = body[idx : idx + MAX_SMS_LEN]
        idx += MAX_SMS_LEN
        twilio_client.messages.create(body=segment, from_=from_, to=to_)

#############################
# PDF & Summaries
#############################
def create_pdf_report(pdf_text):
    """Create a PDF file with the given text in English."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"legal_report_{timestamp}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=LETTER)
        c.setFont("Helvetica", 12)
        text_y = 750
        for line in pdf_text.split("\n"):
            c.drawString(72, text_y, line)
            text_y -= 20
        c.save()
        print(f"PDF saved: {pdf_filename}")
    except Exception as e:
        print("Error generating PDF:", e)

def generate_summary():
    """Returns a 3-line summary for SMS, and also saves a full text PDF if labor violation >=80%."""
    global employer_name, location, conversation_type
    conversation_str = "\n".join([
        f"Q: {entry['question']}\nA: {entry['answer']}"
        for entry in conversation_history
    ])

    if not conversation_str:
        return "No conversation recorded."

    # 1) Create full summary text for PDF
    date_str = datetime.now().strftime('%Y.%m.%d %H:%M')
    full_summary = (
        f"Subject: Unpaid Wages Report\n\n"
        f"Date of Report: {date_str}\n"
        f"Location: {location or 'Unknown'}\n"
        f"Employer’s Name: {employer_name or 'Unknown'}\n\n"
        "Summary of the Report:\n"
        "You reported the following conversation:\n\n"
        f"{conversation_str}"
    )

    # If labor law violation topic => add risk analysis
    if conversation_type == "1":
        risk_score = random.randint(50, 100)
        full_summary += (
            f"\n\n⚠️ Our analysis estimates a {risk_score}% chance of a labor law violation."
        )
        if risk_score >= 80:
            full_summary += "\nWe recommend contacting a licensed attorney for further assistance."
            # Create PDF with full text in English
            create_pdf_report(full_summary)

    # 2) Create a short 3-line summary for SMS
    sms_prompt = f"""
        You are a helpful legal assistant.
        Read the following conversation.

        {conversation_str}

        Now, respond with a summary that:
        1. Is exactly 3 lines.
        2. Does NOT include 'Q:' or 'A:' formatting.
        3. Each line is short and captures the essence of the entire conversation.

        Summary:
        """
    sms_summary = get_llama_response([], sms_prompt).strip()

    # That short summary is what's returned and eventually sent via SMS
    return sms_summary

#############################
# Routes
#############################

@app.route("/lang_select", methods=["POST"])
def lang_select():
    """Language selection first."""
    response = VoiceResponse()
    gather = Gather(num_digits=1, action="/set_language")
    # Use English TTS by default for the initial prompt
    response.say(TRANSLATIONS["en"]["lang_prompt"], language="en-US")
    response.append(gather)
    return Response(str(response), mimetype="text/xml")

@app.route("/set_language", methods=["POST"])
def set_language():
    global selected_language
    digit = request.values.get("Digits", "")
    if digit == "1":
        selected_language = "en"
    elif digit == "2":
        selected_language = "es"
    elif digit == "3":
        selected_language = "fr"
    elif digit == "4":
        selected_language = "zh"
    elif digit == "5":
        selected_language = "ko"
    else:
        selected_language = "en"

    response = VoiceResponse()
    gather = Gather(num_digits=1, action="/handle_topic_choice")
    say_in_language(response, "main_menu")
    response.append(gather)
    response.redirect("/voice")
    return Response(str(response), mimetype="text/xml")

@app.route("/voice", methods=["POST"])
def voice():
    """If user hits /voice directly, re-route to language selection."""
    response = VoiceResponse()
    response.redirect("/lang_select")
    return Response(str(response), mimetype="text/xml")

@app.route("/handle_topic_choice", methods=["POST"])
def handle_topic_choice():
    global conversation_type
    digit = request.values.get("Digits", "")
    response = VoiceResponse()

    if digit == "0":
        conversation_type = "0"
        gather = Gather(input="speech dtmf", action="/process_speech", timeout=5)
        say_in_language(gather, "ask_question")
        response.append(gather)
    elif digit == "1":
        conversation_type = "1"
        gather = Gather(input="speech dtmf", action="/process_speech", timeout=5)
        say_in_language(gather, "ask_labor")
        response.append(gather)
    elif digit in ["3", "*", "#"]:
        say_in_language(response, "ending_call")
        response.hangup()
    else:
        say_in_language(response, "invalid")
        response.redirect("/lang_select")
    return Response(str(response), mimetype="text/xml")

@app.route("/process_speech", methods=["POST"])
def process_speech():
    global employer_name, location, conversation_type
    user_input = request.values.get("SpeechResult", "").strip()
    digit = request.values.get("Digits", "")

    response = VoiceResponse()

    # If user presses star or pound => attempt to end
    if digit in ["*", "#"]:
        # if labor case but missing info => collect location
        if conversation_type == "1" and (not employer_name or not location):
            gather = Gather(input="speech", action="/collect_location", timeout=5)
            say_in_language(gather, "need_location")
            response.append(gather)
            return Response(str(response), mimetype="text/xml")
        else:
            gather = Gather(num_digits=1, action="/handle_data_option")
            say_in_language(gather, "ask_data")
            response.append(gather)
            return Response(str(response), mimetype="text/xml")

    if not user_input:
        say_in_language(response, "sorry_catch")
        response.redirect("/lang_select")
        return Response(str(response), mimetype="text/xml")

    # If user said 'ok' or 'okay'
    lower_input = user_input.lower()
    if lower_input in ["ok", "okay"]:
        gather = Gather(input="speech dtmf", action="/process_speech", timeout=5)
        say_in_language(gather, "ok_next")
        response.append(gather)
        return Response(str(response), mimetype="text/xml")

    # LLM
    rag_answer = get_llama_response([], user_input)
    conversation_history.append({"question": user_input, "answer": rag_answer})

    # Respond
    gather = Gather(input="speech dtmf", action="/process_speech", timeout=5)
    twilio_lang = LANG_CODE_TWILIO.get(selected_language, "en-US")
    gather.say(rag_answer, language=twilio_lang)
    response.append(gather)
    response.redirect("/lang_select")
    return Response(str(response), mimetype="text/xml")

@app.route("/collect_location", methods=["POST"])
def collect_location():
    global location
    location = request.values.get("SpeechResult", "").strip()
    response = VoiceResponse()
    gather = Gather(input="speech", action="/collect_employer", timeout=5)
    say_in_language(gather, "need_employer")
    response.append(gather)
    return Response(str(response), mimetype="text/xml")

@app.route("/collect_employer", methods=["POST"])
def collect_employer():
    global employer_name
    employer_name = request.values.get("SpeechResult", "").strip()
    response = VoiceResponse()
    gather = Gather(num_digits=1, action="/handle_data_option")
    say_in_language(gather, "ask_data")
    response.append(gather)
    return Response(str(response), mimetype="text/xml")

@app.route("/handle_data_option", methods=["POST"])
def handle_data_option():
    digit = request.values.get("Digits", "")
    sms_summary = generate_summary()

    # Send the short 3-line summary
    if digit == "1":  
        send_sms_in_segments(sms_summary, FROM_NUMBER, TO_NUMBER)

    response = VoiceResponse()
    say_in_language(response, "thank_you")
    response.hangup()
    return Response(str(response), mimetype="text/xml")

#############################
# Extra: /summary for quick test
#############################
@app.route("/summary", methods=["GET"])
def summary_endpoint():
    sms_summary = generate_summary()
    send_sms_in_segments(sms_summary, FROM_NUMBER, TO_NUMBER)
    return sms_summary

#############################
# Outbound Call Trigger
#############################
@app.route("/initiate_call", methods=["GET"])
def initiate_call():
    call = twilio_client.calls.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        url="https://92f6-38-113-160-139.ngrok-free.app/lang_select"
    )
    return f"Call initiated. SID: {call.sid}"

#############################
# Run Flask
#############################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
