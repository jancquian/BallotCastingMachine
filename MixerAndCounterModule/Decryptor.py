import ast
import sys

from Exporter import Exporter as exp


class Decryptor:
    def __init__(self, prime, generator, private_key):
        self.prime_number = int(prime)
        self._private_key = int(private_key)
        self.generator =  int(generator)

    # Busqueda por fuerza bruta de 'm'
    @staticmethod
    def count(g_m, generator, prime):
        for x in range(0, g_m):
            sol = pow(generator, x, prime)
            # print("{0} votos contabilizados".format(x))
            if sol == g_m:
                # print("Se han contado {0} votos totales".format(x))
                return  x
        return None

    def decipher(self, cipher_txt):
        sys.set_int_max_str_digits(7000)
        print(f"tipo original: {type(cipher_txt)}\ntexto:{cipher_txt}")

        tupla = ast.literal_eval(cipher_txt)

        print(f"tipo convertido: {type(tupla)}\ntexto:{tupla}")
        s = pow(int(tupla[0]), self._private_key, self.prime_number)
        inv_s = pow(s, -1, self.prime_number)
        g_m = (int(tupla[1]) * inv_s) % self.prime_number
        m = self.count(g_m, self.generator, self.prime_number)
        print(f"s: {s}")
        print(f"g_m: {g_m}")
        print(f"m: {m}")

        return m

    def decipher_std(self, cipher_txt):
        print(type(cipher_txt))
        print(cipher_txt)
        tupla = ast.literal_eval(cipher_txt)
        print(type(tupla))
        print("tipo p: {}".format(type(self.prime_number)))
        print("tipo prk: {}".format(type(self._private_key)))
        print(self.prime_number)
        print(self._private_key)
        s = pow(int(tupla[0]), self._private_key, self.prime_number)
        inv_s = pow(s, -1, self.prime_number)
        m = (int(tupla[1]) * inv_s) % self.prime_number
        print(m)
        plaintext = exp.int_to_string(m)
        print(plaintext)
        return plaintext