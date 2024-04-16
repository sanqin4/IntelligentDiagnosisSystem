import hashlib
import base64
import hmac
from param import params


class BaseParam(object):
    def __init__(self, appID, apiSecret, apiKey, timeStamp, originURL):
        self.appID = appID
        self.apiSecret = apiSecret
        self.apiKey = apiKey
        self.timeStamp = timeStamp
        self.originURL = originURL

    def getSignature(self):
        md5 = hashlib.md5()
        data = bytes(self.appID + self.timeStamp, encoding='utf-8')
        md5.update(data)
        originSignature = md5.hexdigest()
        signature = hmac.new(self.apiSecret.encode('utf-8'), originSignature.encode('utf-8'),
                             digestmod=hashlib.sha1).digest()
        signature = base64.b64encode(signature).decode('utf-8')
        return signature
