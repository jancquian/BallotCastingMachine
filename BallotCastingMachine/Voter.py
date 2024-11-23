import hashlib
import random as rdom
from math import gcd

class Voter:
    def __init__(self, signatories_public_key):
        self.public_key = signatories_public_key
        self._opacity_factor = None

    def hide(self, message):
        aux_message = str(message)
        digest_hex = hashlib.sha3_256(aux_message.encode('utf-8')).hexdigest()
        digest = int(digest_hex, 16)
        number_n = self.public_key['N']
        public_parameter = self.public_key['Puk']
        while True:
            opacity_factor = rdom.randrange(1, number_n)
            if gcd(opacity_factor, number_n) == 1:
                break
        hidden_message = (digest*pow(opacity_factor, public_parameter, number_n)) % number_n
        self._opacity_factor = opacity_factor
        return hidden_message

    def find(self, blind_signature):
        opacity_factor = self._opacity_factor
        number_n = self.public_key['N']
        signature = (blind_signature*pow(opacity_factor, -1, number_n)) % number_n
        return signature
