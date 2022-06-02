import math
from datetime import datetime

from cryptography.fernet import Fernet


def func_10_to_2(num, n):
    ans = ""
    while num != 0:
        ans = str(num % 2) + ans
        num //= 2
    while len(ans) < n:
        ans = '0' + ans
    return ans


def encrypt(text: str):
    p = 241
    g = 51
    x = 98
    k = 12
    b01 = ""
    for c in text:
        b01 += str(func_10_to_2(ord(c), 8))

    int(math.log(p, 2))
    while len(b01) % (int(math.log(p, 2))) != 0:
        b01 = '0' + b01

    y = (g ** x) % p
    a = (g ** k) % p
    ans = chr(a)
    for i in range(0, len(b01), 7):
        bin_dig = int(b01[i:i + 7], 2)
        ans += chr((y ** k * bin_dig) % p)
    return ans


def decrypt(data: str):
    p = 241
    x = 98
    a = ord(data[0])
    a_1 = (a ** (p - 2)) % p
    a_1 = (a_1 ** x) % p
    b01 = ""
    for i in range(1, len(data)):
        b01 += func_10_to_2((ord(data[i]) * a_1) % p, int(math.log(p, 2)))
    extra_nums = len(b01) % 8
    b01 = b01[extra_nums: len(b01)]
    res = ""
    for i in range(0, len(b01), 8):
        res += chr(int(b01[i:i + 8], 2))
    return res


def encode_string(text):
    s = datetime.today().toordinal() + 20
    result = ""
    for i in range(len(text)):
        char = text[i]
        if char.isupper():
            result += chr((ord(char) + s - 65) % 26 + 65)
        else:
            result += chr((ord(char) + s - 97) % 26 + 97)

    return result


class CryptoGraphy:
    def __init__(self):
        self.key = "RMdRW--40NEscVSJ2xNO7ClOCSSkUWVZnJTWj8NA1j8="
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, text: str):
        return self.cipher_suite.encrypt(bytes(text, encoding="utf8")).decode("utf-8")

    def decrypt(self, text: str):
        return self.cipher_suite.decrypt(bytes(text, encoding="utf8")).decode("utf-8")
