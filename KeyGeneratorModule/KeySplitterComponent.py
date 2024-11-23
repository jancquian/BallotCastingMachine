from sslib import shamir, randomness


class KeySplitterComponent:
    def __init__(self, required_shares=1, distributed_shares=1):
        self._required_shares = required_shares
        self._distributed_shares = distributed_shares

    def get_required_shares(self):
        return self._required_shares

    def get_distribiuted_shares(self):
        return self._distributed_shares

    def set_required_shares(self, required_shares):
        self._required_shares = required_shares

    def set_distribiuted_shares(self, distribiuted_shares):
        self._distributed_shares = distribiuted_shares

    def split_secret(self, secret):
        shamir_data = shamir.split_secret(
            secret.encode('ascii'),
            self._required_shares,
            self._distributed_shares,
            randomness_source=randomness.UrandomReader()
        )

        share_l = list()

        for idx, (x, y) in enumerate(shamir_data['shares']):
            share = {'Rs': self._required_shares,
                     'x': x,
                     'y': y.hex(),
                     'prime_mod': int.from_bytes(shamir_data['prime_mod'], byteorder='big')}
            share_l.append(share)

        return share_l
