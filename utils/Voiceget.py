import base64
import os

import pyaudio
import streamlit as st

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


if 'recording' not in st.session_state:
    st.session_state.recording = False
    st.session_state.frames = []
    st.session_state.stream = None

if not st.session_state.recording:
    if st.button("开始录音"):
        st.session_state.stream, st.session_state.frames = start_recording()
        st.session_state.recording = True
        while st.session_state.recording:
            st.session_state.frames.append(st.session_state.stream.read(chunk))
else:
    if st.button("停止录音"):
        stop_recording(st.session_state.stream, st.session_state.frames)
        st.session_state.recording = False

# 添加下载按钮
if os.path.exists(pcm_output_filename):
    with open(pcm_output_filename, 'rb') as f:
        pcm_data = f.read()
    b64 = base64.b64encode(pcm_data).decode()
    href = f'<a href="data:audio/x-pcm;base64,{b64}" download="listen.pcm">下载PCM_s16le录音</a>'
    st.markdown(href, unsafe_allow_html=True)
