import random as rdom

class FakeMixNet:
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

    @staticmethod
    def get_random_index(number):
        rnd = rdom.randrange(0, number)
        print(rnd)

    def recipher(self, chiper_txt):
        # Elemento c1 del texto cifrado original
        alpha = chiper_txt[0]
        # Elemento c2 del texto cifrado original
        betha = chiper_txt[1]

        k = self.generate_multiplicative_member(self.prime_number)
        c1 = (pow(self.generator, k, self.prime_number) * alpha) % self.prime_number

        s = pow(self.public_key, k, self.prime_number)
        c2 = (betha * s) % self.prime_number
        return c1, c2

    def permute(self, ciphertexts):

        permutation = list()
        while True:
            size = len(ciphertexts)
            if size == 0:
                break
            else:
                sel_index = rdom.randrange(0, size)
                reciphertext = self.recipher(ciphertexts[sel_index])
                permutation.append(reciphertext)
                ciphertexts.pop(sel_index)
        return permutation

'''
generador = EncryptionKeyGenerator()
generador.create_key_pair()
puk = generador.get_public_key()
prk = generador.get_private_key()


lst = list()
cifrador =  Encryptor(puk["P"], puk["G"], puk["PuK"])
ctx = cifrador.cipher(1)
lst.append(ctx)
ctx = cifrador.cipher(2)
lst.append(ctx)
ctx = cifrador.cipher(3)
lst.append(ctx)
ctx = cifrador.cipher(4)
lst.append(ctx)
ctx = cifrador.cipher(5)
lst.append(ctx)

for element in lst:
    print(element)

print("----------")
recifrador = FakeMixNet(puk["P"], puk["G"], puk["PuK"])

lst = recifrador.permute(lst)
for element in lst:
    print(element)
print("----------")

lst = recifrador.permute(lst)
for element in lst:
    print(element)
print("----------")

lst = recifrador.permute(lst)
for element in lst:
    print(element)
print("----------")


descifrador = Decryptor(prk["P"], prk["G"], prk["PrK"])
for element in lst:
    print(descifrador.decipher(element))
'''