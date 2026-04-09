import hashlib
import time
import random
import string
from config.config import Config

class ChallengeService:
    def __init__(self, config: Config):
        self.config = config

    def generate_challenge_locally(self):
        timestamp = str(int(time.time() * 1000))
        nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        message = timestamp + nonce + self.config.HARD_CHALLENGE_SECRET
        challenge_hash = hashlib.sha256(message.encode()).hexdigest()
        return challenge_hash, timestamp, nonce