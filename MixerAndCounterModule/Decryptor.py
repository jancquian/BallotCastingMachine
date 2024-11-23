class Decryptor:
    def __init__(self, prime, generator ,private_key):
        self.prime_number = prime
        self._private_key = private_key
        self.generator =  generator

    # Busqueda por fuerza bruta de 'm'
    @staticmethod
    def count(g_m, generator, prime):
        for x in range(0, g_m):
            sol = pow(generator, x, prime)
            if sol == g_m:
                return  x
        return None

    def decipher(self, cipher_txt):
        s = pow(cipher_txt[0], self._private_key, self.prime_number)
        inv_s = pow(s, -1, self.prime_number)
        g_m = (cipher_txt[1] * inv_s) % self.prime_number
        m = self.count(g_m, self.generator, self.prime_number)
        return m

    def decipher_std(self, cipher_txt):
        s = pow(cipher_txt[0], self._private_key, self.prime_number)
        inv_s = pow(s, -1, self.prime_number)
        m = (cipher_txt[1] * inv_s) % self.prime_number
        return m