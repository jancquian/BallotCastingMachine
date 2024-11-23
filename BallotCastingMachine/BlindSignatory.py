class BlindSignatory:
    def __init__(self, private_key):
        self._private_key = private_key

    def sign(self, hidden_message):
        private_parameter = self._private_key['Prk']
        number_n = self._private_key['N']
        blind_signature = pow(hidden_message, private_parameter, number_n)
        return blind_signature

    def authorize(self, private_key):
        if self._private_key == private_key:
            return True
        else:
            return False