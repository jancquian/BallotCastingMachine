import random as rdom

class FakeMixNet:
    def __init__(self, prime, generator, public_key):
        self.prime_number = prime
        self.generator = generator
        self.public_key = public_key
        self.factors = []

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

    def recipher(self, chiper_txt, recipher_factor=0):
        # Elemento c1 del texto cifrado original
        alpha = chiper_txt[0]
        # Elemento c2 del texto cifrado original
        betha = chiper_txt[1]

        if recipher_factor == 0:
            k = self.generate_multiplicative_member(self.prime_number)
        else:
            k = recipher_factor
        c1 = (pow(self.generator, k, self.prime_number) * alpha) % self.prime_number

        s = pow(self.public_key, k, self.prime_number)
        c2 = (betha * s) % self.prime_number
        # Tambien devuelve el factor de recifrado para guardarlo en una lista
        return (c1, c2), k

    def permute(self, ciphertexts):
        permutation = []
        # Conjunto de indices que ya fueron usados
        used_indices = set()
        size = len(ciphertexts)
        #permutation_factors = [x for x in range(0, size)]

        # Iteramos hasta que hayamos usado todos los índices
        while len(used_indices) < size:
        #while len(permutation_factors) > 0:
            # Obtenemos un factor de permutación aleatorio
            sel_index = rdom.randrange(0, size)
            #sel_index = permutation_factors.pop(rdom.randrange(0, len(permutation_factors)))
            if sel_index not in used_indices: # Entonces no se ha recifrado el ciphertext de ese indice
                reciphertext, k = self.recipher(ciphertexts[sel_index])
                alpha = reciphertext[0]
                self.factors.append({f"{alpha}": [sel_index, k]})
                permutation.append(reciphertext)
                # Se establece el indice como usado
                used_indices.add(sel_index)

        return permutation

    def challenge(self, alpha):
        for _dict in self.factors:
            for k, v in _dict.items():
                if str(k) == str(alpha):
                    return v


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