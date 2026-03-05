import requests
import json
import random
import base64
from Cryptodome.Cipher import AES

class Netease_params(object):
    def __init__(self, data):
        self.data = data
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

    def create_secret_key(self, size):
        return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', size))

    def aes_encrypt(self, text, key):
        iv = '0102030405060708'
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
        result = encryptor.encrypt(text.encode())
        result = base64.b64encode(result).decode()
        return result

    def rsa_encrypt(self, text, pubKey, modulus):
        text = text[::-1]
        rs = pow(int.from_bytes(text.encode(), byteorder='big'), int(pubKey, 16), int(modulus, 16))
        return format(rs, 'x').zfill(256)

    def get_params(self):
        text = json.dumps(self.data)
        secKey = self.create_secret_key(16)
        encText = self.aes_encrypt(self.aes_encrypt(text, '0CoJUm6Qyw8W8jud'), secKey)
        encSecKey = self.rsa_encrypt(secKey, '010001', '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        )
        return {'params': encText, 'encSecKey': encSecKey}

    def run(self, url):
        params = self.get_params()
        response = requests.post(url, data=params, headers=self.headers)
        return response.json()