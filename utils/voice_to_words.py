# -*- encoding:utf-8 -*-
import base64
import hashlib
import hmac
import json
import logging
import threading
import time
from socket import *
from urllib.parse import quote

import websocket
from websocket import create_connection


# reload(sys)
# sys.setdefaultencoding("utf8")

class Client():
    def __init__(self, app_id, api_key):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"

        self.ws = create_connection(base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa))
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()
        self.result = None

    def send(self, file_path):
        file_object = open(file_path, 'rb')
        try:
            index = 1
            while True:
                chunk = file_object.read(1280)
                if not chunk:
                    break
                self.ws.send(chunk)

                index += 1
                time.sleep(0.04)
        finally:
            file_object.close()

        self.ws.send(bytes(self.end_tag.encode('utf-8')))
        print("send end tag success")

    def recv(self):
        try:
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    result_1 = result_dict
                    self.result = result_1["data"]
                    # result_2 = json.loads(result_1["cn"])
                    # result_3 = json.loads(result_2["st"])
                    # result_4 = json.loads(result_3["rt"])

                    print("rtasr result: " + result_1["data"])

                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return

        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        self.ws.close()
        print("connection closed")


def main(file_path=r"test_1.pcm"):
    logging.basicConfig()

    app_id = "dea0700e"
    api_key = "c9eadb576584e11e3736253eeff1a0ee"

    client = Client(app_id, api_key)
    client.send(file_path)

    # 尝试将client.result解析为字典
    try:

        result_dict = json.loads(client.result)
    except json.JSONDecodeError:
        print("无法解析结果为JSON")
        result_dict = None
    text = ""
    # 在尝试访问结果之前，检查client.result是否为None
    if result_dict is not None:
        # 确保result_dict["cn"]["st"]["rt"]是一个列表，并且至少有一个元素
        rt = result_dict.get("cn", {}).get("st", {}).get("rt", [])
        if isinstance(rt, list) and rt:
            for ws in rt[0]["ws"]:
                # 提取文字
                for cw in ws["cw"]:
                    text += cw["w"]
                print(text)
        else:
            print("结果格式不正确或缺少必要的数据")
    else:
        print("没有获取到结果")
    text = text.replace('\n', ' ').replace(' ', '')
    return text


if __name__ == '__main__':
    text = main()
    print(text)
