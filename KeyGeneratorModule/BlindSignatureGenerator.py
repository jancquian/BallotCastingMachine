from Crypto.Util import number
from Crypto.Random import random


class BlindSignatureGenerator:
    def __init__(self, security_parameter=4096):
        self._security_parameter = security_parameter
        self._n_number = None
        self._phi_n = None
        self._private_key = None
        self._public_key = None

    @staticmethod
    def generate_primes(length):
        inner_length = int(length/2)
        number_p = number.getPrime(inner_length)
        number_q = number.getPrime(inner_length)
        while number_q == number_p:
            number_q = number.getPrime(inner_length)
        # print("Q: ", number_q)
        # print("P: ", number_p)
        # print("QP: ", number_q*number_p)
        return number_p, number_q

    def compute_n(self, number_p, number_q):
        self._n_number = number_p * number_q

    def compute_phi_n(self, number_p, number_q):
        self._phi_n = (number_p - 1) * (number_q - 1)

    def create_random_public_key(self):
        key = random.randrange(2, self._phi_n - 1)
        while number.GCD(key, self._phi_n)!= 1:
            key = random.randrange(2, self._phi_n - 1)
        self._public_key = key

    def compute_private_key(self):
        self._private_key = number.inverse(self._public_key, self._phi_n)
        while number.GCD(self._private_key, self._public_key) != 1:
            self.create_random_public_key()
            self._private_key = number.inverse(self._public_key, self._phi_n)

    def generate_keys(self):
        number_p, number_q = self.generate_primes(self._security_parameter)
        self.compute_n(number_p, number_q)
        self.compute_phi_n(number_p, number_q)
        self.create_random_public_key()
        self.compute_private_key()
        return self._public_key, self._private_key, self._n_number

    def get_private_key(self):
        return {'Prk': self._private_key, 'N': self._n_number}

    def get_public_key(self):
        return {'Puk': self._public_key, 'N': self._n_number}

    def set_security_parameter(self, size):
        self._security_parameter = size
