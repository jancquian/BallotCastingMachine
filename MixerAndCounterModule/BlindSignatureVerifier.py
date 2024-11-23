import hashlib

class BlindSignatureVerifier:
    def __init__(self, signatories_public_key):
        self.public_key = signatories_public_key

    def verify(self, signature, message):
        public_parameter = self.public_key['Puk']
        number_n = self.public_key['N']
        digest_hex = hashlib.sha3_256(message.encode('utf-8')).hexdigest()
        digest = int(digest_hex, 16)
        hidden_message = pow(signature, public_parameter, number_n)
        if digest == hidden_message:
            return True
        else:
            return False