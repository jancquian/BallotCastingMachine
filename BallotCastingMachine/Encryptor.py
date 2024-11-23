import random as rdom

class Encryptor:
    def __init__(self, prime, generator, public_key):
        self.prime_number = prime
        self.generator = generator
        self.public_key = public_key

    @staticmethod
    def generate_multiplicative_member(prime):
        m_member = rdom.randrange(2, prime - 1)
        while not 1 < m_member < prime - 1:
            m_member = rdom.randrange(2, prime - 1)
        return m_member

    def homomorphic_product(self, cipher_txt_a, cipher_txt_b):
        c3 = (cipher_txt_a[0]*cipher_txt_b[0]) % self.prime_number
        c4 = (cipher_txt_a[1]*cipher_txt_b[1]) % self.prime_number
        return c3, c4

    def cipher(self, plain_txt):
        k = self.generate_multiplicative_member(self.prime_number)
        c1 = pow(self.generator, k, self.prime_number)
        s = pow(self.public_key, k, self.prime_number)
        c2 = (pow(self.generator, plain_txt, self.prime_number) * s) % self.prime_number
        return c1, c2

    def cipher_std(self, plain_txt):
        k = self.generate_multiplicative_member(self.prime_number)
        c1 = pow(self.generator, k, self.prime_number)
        s = pow(self.public_key, k, self.prime_number)
        c2 = (plain_txt * s) % self.prime_number
        return c1, c2
