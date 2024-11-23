import random as rdom
from Crypto.Util import number
import SophieGermainPrimeGenerator as Sophie


class EncryptionKeyGenerator:
    def __init__(self, key_size=2048):
        self._key_size = key_size
        self.prime_number = None
        self.generator = None
        self._factors = []
        self._private_key = None
        self.public_key = None

    # Retorna un número de n bits
    @staticmethod
    def generate_prime(size):
        return number.getPrime(size)

    # Retorna un número "x" comprendido en 1 < x < p-1.
    # Aclaracion: El metodo randrange tiene un intervalo de valores entre [n, m)
    @staticmethod
    def generate_multiplicative_member(prime):
        m_member = rdom.randrange(2, prime - 1)
        while not 1 < m_member < prime - 1:
            m_member = rdom.randrange(2, prime - 1)
        return m_member

    # Genera un número primo de Sophie Germain de n bits y guarda sus coeficientes primos.
    # Nota: Función descartada por su alto costo en tiempo de ejecución.
    def set_up_prime(self):
        sophie = Sophie.SophieGermainPrimeGenerator(self._key_size)
        factor, primo = sophie.generate()
        self.prime_number = primo
        self._factors.append(factor)
        self._factors.append(2)

    def set_key_size(self, size):
        self._key_size =  size

    # Se usa el primo dado en el RFC 3526 así como su generador
    def set_up_standard_parameters(self):
        if self._key_size == 3072:
            hex_s = '''FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
                       29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
                       EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
                       E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
                       EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
                       C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
                       83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
                       670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
                       E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
                       DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
                       15728E5A 8AAAC42D AD33170D 04507A33 A85521AB DF1CBA64
                       ECFB8504 58DBEF0A 8AEA7157 5D060C7D B3970F85 A6E1E4C7
                       ABF5AE8C DB0933D7 1E8C94E0 4A25619D CEE3D226 1AD2EE6B
                       F12FFA06 D98A0864 D8760273 3EC86A64 521F2B18 177B200C
                       BBE11757 7A615D6C 770988C0 BAD946E2 08E24FA0 74E5AB31
                       43DB5BFC E0FD108E 4B82D120 A93AD2CA FFFFFFFF FFFFFFFF'''
        else:
            hex_s = '''FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
                       29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
                       EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
                       E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
                       EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
                       C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
                       83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
                       670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
                       E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
                       DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
                       15728E5A 8AACAA68 FFFFFFFF FFFFFFFF'''
        hex_s = hex_s.replace("\n", "").replace(" ", "")
        self.prime_number = int(hex_s, 16)
        self.generator = 2

    # Teniendose el número primo de Sophie G., se obtiene la raíz primita (generador) a tráves de los coeficientes
    # primos del número primo.
    # Nota: Descartado por su vinculación con set_up_prime().
    def set_up_generator(self):
        if pow(2, (self.prime_number - 1) // self._factors[0], self.prime_number) != 1:
            if pow(2, (self.prime_number - 1) // self._factors[1], self.prime_number) != 1:
                self.generator = 2
                return

        for primitive in range(1, self.prime_number, 2):
            if pow(primitive, (self.prime_number - 1) // self._factors[0], self.prime_number) != 1:
                if pow(primitive, (self.prime_number - 1) // self._factors[1], self.prime_number) != 1:
                    self.generator = primitive
                    return
        return

    def generate_private_parameter(self):
        key = self.generate_multiplicative_member(self.prime_number)
        self._private_key = {"P": self.prime_number, "G": self.generator, "PrK": key}

    def compute_public_parameter(self):
        y = pow(self.generator, self._private_key["PrK"], self.prime_number)
        self.public_key = {"P": self.prime_number, "G": self.generator, "PuK": y}

    def create_key_pair(self):
        self.set_up_standard_parameters()
        self.generate_private_parameter()
        self.compute_public_parameter()

    def get_private_key(self):
        return self._private_key

    def get_public_key(self):
        return self.public_key
