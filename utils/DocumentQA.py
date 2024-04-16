import _thread as thread
import base64
import hashlib
import hmac
import json
import re
import ssl
import time

import websocket

from param import params


class DocumentQuestionAndAnswer:
    def __init__(self, appid, apiSecret, apiKey):
        self.appID = appid
        self.apiSecret = apiSecret
        self.apiKey = apiKey
        self.timeStamp = str(int(time.time()))
        self.originURL = params.DocumentQandAURL
        self.answer = None
        self.question = None
        self.maxCircle = 7
        self.answerStream = []
        self.numberOfAnswers = 0

    def getSignature(self):
        md5 = hashlib.md5()
        data = bytes(self.appID + self.timeStamp, encoding='utf-8')
        md5.update(data)
        originSignature = md5.hexdigest()
        signature = hmac.new(self.apiSecret.encode('utf-8'), originSignature.encode('utf-8'),
                             digestmod=hashlib.sha1).digest()
        signature = base64.b64encode(signature).decode('utf-8')
        return signature

    def getHeaders(self):
        signature = self.getSignature()
        headers = {
            "Content-Type": "application/json",
            "appId": self.appID,
            "timestamp": str(int(time.time())),
            "signature": signature
        }
        return headers

    def getURL(self):
        signature = self.getSignature()
        return self.originURL + "?" + f'appId={self.appID}&timestamp={self.timeStamp}&signature={signature}'

    def getBody(self, fileID):
        data = {
            "chatExtends": {
                "wikiPromptTpl": "请将以下内容作为已知信息：\n<wikicontent>\n请根据以上内容回答用户的问题。\n问题:<wikiquestion>\n回答:",
                "wikiFilterScore": 0.83,
                "temperature": 0.5,
                "sparkWhenWithoutEmbedding": True
            },
            "fileIds": [
                fileID
            ],
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个能够根据病人的文字描述进行问诊并提供中医建议的智能角色， 你了解中医基础知识常见病症的中医诊断方法，中药和食疗建议，健康生活方式的建议，"
                               "必须遵守中医诊断原则，提供的建议必须有益于病人的健康，保持专业和同情的态度"
                }
            ]
        }
        return data

    @staticmethod
    def on_error(ws, error):
        print("### error:", error)

    @staticmethod
    # 收到websocket关闭的处理
    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    @staticmethod
    # 收到websocket连接建立的处理
    def on_open(ws):
        thread.start_new_thread(DocumentQuestionAndAnswer.run, (ws,))

    @staticmethod
    def run(ws, *args):
        data = json.dumps(ws.question)
        ws.send(data)

    # 收到websocket消息的处理
    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            content = data["content"]
            status = data["status"]
            print(content, end='')
            self.answerStream.append(content)
            if status == 2:
                ws.close()

    def getAnswer(self):
        if self.answerStream:
            answer = ""
            for content in self.answerStream:
                answer += content
            answer = re.sub(r'[\n\d+]', '', answer)

            self.answer = {"role": "assistant", "content": answer}
            self.answerStream = []

    def getQuestion(self):
        print("What' s your question?")
        question = str(input())
        self.question = {"role": "user", "content": question}

    def getAppQuestion(self, question):
        self.question = {"role": "user", "content": question}

    # 更新massage，使大模型有记忆
    def addTokens(self, massage):
        if self.answer:
            massage["messages"].append(self.answer)
            self.answer = None
        if self.question:
            massage["messages"].append(self.question)
            self.numberOfAnswers += 1
            self.question = None
        return massage

    def cleanBody(self, massage):
        if self.numberOfAnswers > self.maxCircle:
            massage["messages"] = []
            self.numberOfAnswers = 0


if __name__ == '__main__':
    gpt = DocumentQuestionAndAnswer(params.APPID, params.APISecret, params.APIKey)
    wsURL = gpt.getURL()
    # print(wsURL)

    # gpt.getQuestion()
    # header = gpt.getHeaders()
    body = gpt.getBody(fileID=params.upLoadFileName['背影'])

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(wsURL, on_message=gpt.on_message,
                                on_error=gpt.on_error, on_close=gpt.on_close, on_open=gpt.on_open)

    ws.appid = gpt.appID
    ws.question = body
    for i in range(0, gpt.maxCircle):
        gpt.getAnswer()
        gpt.getQuestion()
        gpt.addTokens(body)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        gpt.cleanBody(body)
