from Crypto.Util import number
from gmpy2 import mpz
class SophieGermainPrimeGenerator:
    def __init__(self, length):
        self.bit_len = length

    def generate(self):
        candidate = mpz(number.getPrime(self.bit_len))
        while True:
            sophie_prime = 2 * candidate + 1
            criteria = mpz.is_probab_prime(sophie_prime)
            if criteria >= 1:
                return int(candidate), int(2 * candidate + 1)
            else:
                candidate = mpz(number.getPrime(self.bit_len))
