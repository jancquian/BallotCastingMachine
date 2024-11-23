from sslib import shamir


class KeyRecoveryComponent:
    def __init__(self, shares):
        print(f"despues: {shares}")
        self.required_shares = shares[0]['Rs']
        self.shares = shares
        self.prime_mod = shares[0]['prime_mod']


    @staticmethod
    def get_required_shares(self):
        return self.required_shares

    def load_shares(self, shares):

        if len(shares) < self.required_shares:
            raise ValueError(
                f"No se encontraron suficientes shares. Se requieren {self.required_shares}, pero solo se encontraron {len(shares)}."
            )


    def recover_secret(self):
        if not self.shares or self.prime_mod is None:
            raise ValueError("No se han cargado suficientes shares para la recuperación.")

        shares = list()

        for share in self.shares:
            shares.append((share['x'], bytes.fromhex(share['y'])))

        recovered_secret = shamir.recover_secret({
            'shares': shares,
            'prime_mod': self.prime_mod,
            'required_shares': self.required_shares
        })

        return recovered_secret.decode('ascii')
