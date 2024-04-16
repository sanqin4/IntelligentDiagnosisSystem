import ssl
from datetime import datetime

import streamlit as st
import websocket
import base64
import os

import pyaudio
from param import params
from utils.DocumentQA import DocumentQuestionAndAnswer
from utils import voice_to_words

rate = 16000
pcm_output_filename = 'listen.pcm'
chunk = 1024
format = pyaudio.paInt16  # 16-bit depth
channels = 1

pa = pyaudio.PyAudio()


def start_recording():
    stream = pa.open(
        format=format,
        channels=channels,
        rate=rate,
        input=True,
        frames_per_buffer=chunk,
    )
    frames = []
    return stream, frames


def stop_recording(stream, frames):
    stream.stop_stream()
    stream.close()
    pa.terminate()
    with open(pcm_output_filename, 'wb') as f:
        for frame in frames:
            f.write(frame)
    return


class ModelManager:
    def __init__(self):
        self.body = None
        self.gpt = None
        self.ws = None
        self.question = None
        self.answer = None

    def initialize(self):
        if not self.gpt:
            self.gpt = DocumentQuestionAndAnswer(params.APPID, params.APISecret, params.APIKey)
            wsURL = self.gpt.getURL()
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(wsURL, on_message=self.gpt.on_message, on_error=self.gpt.on_error,
                                             on_close=self.gpt.on_close, on_open=self.gpt.on_open)
            self.body = self.gpt.getBody(fileID=params.upLoadFileName['背影'])
            self.ws.appid = self.gpt.appID
            self.ws.question = self.body


# 初始化历史记录
if 'chatHistory' not in st.session_state:
    st.session_state['chatHistory'] = []

if "massageBody" not in st.session_state:
    st.session_state['massageBody'] = []

if "ChineseGPT" not in st.session_state:
    st.session_state.ChineseGPT = ModelManager()

if 'recording' not in st.session_state:
    st.session_state.recording = False
    st.session_state.frames = []
    st.session_state.stream = None

st.title("IntelligentDiagnosisSystem")
st.session_state.ChineseGPT.initialize()
gpt = st.session_state.ChineseGPT.gpt
ws = st.session_state.ChineseGPT.ws
body = st.session_state.ChineseGPT.body

userQuestion = st.text_input("What can I help you today?")
if st.button("提交"):
    gpt.getAppQuestion(userQuestion)
    ws.question = gpt.addTokens(body)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    gpt.getAnswer()
    gpt.cleanBody(body)
    response = st.write(gpt.answer["content"])
    st.session_state['chatHistory'].append(
        {
            'time': datetime.now().strftime("%H:%M:%S"),
            'user': userQuestion,
            'response': gpt.answer["content"]
        }
    )
    # 添加一个按钮来控制是否显示对话历史记录

if not st.session_state.recording:
    if st.button("开始录音"):
        st.session_state.stream, st.session_state.frames = start_recording()
        st.session_state.recording = True
        while st.session_state.recording:
            st.session_state.frames.append(st.session_state.stream.read(chunk))
else:
    if st.button("提交音频"):
        stop_recording(st.session_state.stream, st.session_state.frames)
        st.session_state.recording = False
        words = voice_to_words.main()
        gpt.getAppQuestion(words)
        ws.question = gpt.addTokens(body)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        gpt.getAnswer()
        gpt.cleanBody(body)
        response = st.write(gpt.answer["content"])
        st.session_state['chatHistory'].append(
            {
                'time': datetime.now().strftime("%H:%M:%S"),
                'user': words,
                'response': gpt.answer["content"]
            }
        )

if st.button("查看对话历史记录"):
    if st.session_state.chatHistory:
        st.subheader("对话历史记录")
        for chat in reversed(st.session_state.chatHistory):  # 从最新的对话开始显示
            st.write(f"{chat['time']} - 用户：{chat['user']}")
            st.write(f"{chat['time']} - 助手：{chat['response']}")
    else:
        st.write("没有对话历史记录。")

    if st.button("清除输出"):
        st.session_state.show_output = False

if st.button("Look Body"):
    st.write(st.session_state.ChineseGPT.body)
