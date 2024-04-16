from param import params, baseParam
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
import random
import requests

baseParam = baseParam.BaseParam(params.APPID, params.APISecret, params.APIKey,
                                timeStamp=str(int(time.time())), originURL=params.fileUploadURL)


def getHeader():
    headers = {
        "appID": baseParam.appID,
        "timeStamp": baseParam.timeStamp,
        "signature": baseParam.getSignature()
    }
    return headers


def getBodyFromNet(url="", filetype="wiki", filename=""):
    body = {
        "file": "",
        # 文件网络地址 例如： https://xxx.xx.com/xxx.pdf",
        "url": url,
        # fileType是一个固定值
        "fileType": filetype,
        "fileName": filename
    }
    form = MultipartEncoder(fields=body, boundary='------------------' + str(random.randint(1e28, 1e29 - 1)))
    return form


def getBodyFromFile(url="", filetype="wiki", filename="", needSummary=False, stepByStep=False):
    body = {
        "url": url,
        "fileType": filetype,
        "fileName": filename,
        "needSummary": needSummary,
        "stepByStep": stepByStep
    }
    files = {"file": open("../data/knowledge/" + filename, "rb")}
    return files, body


if __name__ == "__main__":
    baseParam.timeStamp = str(int(time.time()))
    headers = getHeader()
    files, body = getBodyFromFile(filename="本草纲目.pdf")
    response = requests.post(baseParam.originURL, files=files, data=body, headers=headers)
    print("请求头", response.headers)
    print("response massage:\n", response.text)
