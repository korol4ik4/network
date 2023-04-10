from cryptography.fernet import Fernet
class Coder:
    def __init__(self, de_key=None, en_key=None):
        self.encoder = None
        self.decoder = None
        self.setted = False
        self.set(de_key, en_key)

    def generate_key(self):
        return Fernet.generate_key()

    def get(self):
        return self.encoder, self.decoder

    def set(self, de_key=None, en_key=None):
        if en_key:
            try:
                self.encoder = Fernet(en_key)
            except Exception as e:
                pass

        if de_key:
            try:
                self.decoder = Fernet(de_key)
            except Exception as e:
                pass
        if self.encoder and self.decoder:
            self.setted = True
        else:
            self.setted = False

    def encrypt(self, data):
        if self.encoder:
            return self.encoder.encrypt(data)
        return data

    def decrypt(self, data):
        if self.decoder:
            return self.decoder.decrypt(data)
        return data
