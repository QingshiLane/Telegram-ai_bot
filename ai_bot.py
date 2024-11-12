from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
from collections import deque
import random
import threading
import time,os,io
import ffmpeg
import speech_recognition as sr
from pydub import AudioSegment

if_start=0
XAI_API_KEY = ""#x_ai——API
TELEGRAM_BOT_TOKEN = ""#电报机器人TOKEN
ALLOWED_USER_ID = #允许用户的ID
refuse_other = [
    "我是一个AI助手，只服务于我的主人，而你无权访问！",
    "我是AI助手，专属服务于我家主人，外人免进！",
    "此AI助手只效忠于主人，其他人请止步！",
    "你面前站着的是主人的私人AI助手，请另寻他路！",
    "警告：私人AI助手，未经许可不得访问！",
    "此地为私人AI助手领域，闲人勿扰！",
    "抱歉，我只听我主人的命令，其他请求一概无效！",
    "我是主人的专属AI，外人请走开，不打扰是种美德！",
    "你现在试图访问一个只对主人开放的AI助手，抱歉，你不在服务名单上！",
    "该AI助手仅为主人服务，擅闯者将面对我的无情忽视！"
]

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)
# message="You are Grok, a chatbot inspired by the Hitchhikers Guide to the Galaxy."
messages = deque(maxlen=59)#定义最长信息存储列表30轮对话
# messages=[]
# def create(message,question):
#     completion = client.chat.completions.create(
#         model="grok-beta",
#         messages=[
#             {"role": "system", "content": f"{message}"},
#             {"role": "user", "content": f"{question}"},
#         ],
#     )
#     print(completion.choices[0].message)

def monitor_variable():
    global if_start
    global messages
    while True:
        if if_start:
            t=1200
            while(t and if_start):
                t-=1
                time.sleep(1)  
            if if_start:
                messages.clear()
                if_start=0
        time.sleep(1)  

async def start(update: Update, context):
    if update.effective_user.id == ALLOWED_USER_ID:
        await update.message.reply_text("我是一个AI助手，有啥不会的，别问我，我也不会哦！")
    else:await update.message.reply_text(random.choice(refuse_other))
async def new_talk(update: Update, context):
    if update.effective_user.id == ALLOWED_USER_ID:
        messages.clear()
        await update.message.reply_text("我的大脑短路了，记不清之前的对话了，请开始新的话题！")
    else:await update.message.reply_text(random.choice(refuse_other))

async def chat(update: Update, context):
    if update.effective_user.id == ALLOWED_USER_ID:
        global messages
        global if_start
        if_start=0
        user_message = update.message.text
        print("用户问：",user_message)
        messages.append({"role": "user", "content": user_message})#添加人类命令
        completion = client.chat.completions.create(
            model="grok-beta",
            messages=messages,
        )
        print("助手回复：",completion.choices[0].message.content)
        messages.append({"role": "assistant", "content": completion.choices[0].message.content})#添加AI回复
        await update.message.reply_text(completion.choices[0].message.content)#发送回复
        if_start=1
    else:await update.message.reply_text(random.choice(refuse_other))
async def handle_voice(update: Update, context):
    if update.effective_user.id == ALLOWED_USER_ID:
        # 下载语音文件
        file = await update.message.voice.get_file()
    
        # 将语音文件加载到内存中
        voice_data = await file.download_as_bytearray()
        
        # 使用 pydub 将 .ogg 转换为 .wav
        audio = AudioSegment.from_file(io.BytesIO(voice_data), format="ogg")
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        
        # 使用 SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            audio = recognizer.record(source)
        
        try:
            # 将语音转换为文字
            user_message = recognizer.recognize_google(audio,language='zh-CN')#进行语音识别，不只能识别英文
            print("用户问：",user_message)#输出识别结果
            global if_start
            global messages
            if_start=0
            messages.append({"role": "user", "content": user_message})#添加人类命令
            completion = client.chat.completions.create(
                model="grok-beta",
                messages=messages,
            )
            print("助手回复：",completion.choices[0].message.content)
            messages.append({"role": "assistant", "content": completion.choices[0].message.content})#添加AI回复
            await update.message.reply_text(completion.choices[0].message.content)#发送回复
            if_start=1
        except sr.UnknownValueError:
            await update.message.reply_text("无法识别语音内容。")
        except sr.RequestError as e:
            await update.message.reply_text(f"语音识别服务出错: {e}")
    else:await update.message.reply_text(random.choice(refuse_other))
    

def main():
    monitor_thread = threading.Thread(target=monitor_variable)
    monitor_thread.daemon = True  
    monitor_thread.start()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new_talk", new_talk))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice))

    application.run_polling()

if __name__ == "__main__":
    main()
