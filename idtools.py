import jose
from jose import jwt
import disnake
import os
import random
import string
import typing


class TokenUser(typing.TypedDict):
    id: int
    name: str
    avatar: str


class TokenData(typing.TypedDict):
    user: TokenUser
    context: dict


class Token:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Token, cls).__new__(cls)
        return cls.instance
    secret: str
    secret_file_path = "./jwtsecret.token"

    def __init__(self):
        if not os.path.exists(self.secret_file_path):
            secretfile = open(self.secret_file_path, "w")
            secret = ''.join(random.choice(
                string.ascii_letters + string.digits) for i in range(64))
            secretfile.write(secret)
        self.secret = open(self.secret_file_path).read()

    def make_token(self, user: disnake.Member, additional_context: dict = {}) -> str:
        payload = {
            "user": {
                "id": user.id,
                "name": user.name,
                "avatar": user.avatar.url if user.avatar else "https://cdn.discordapp.com/embed/avatars/1.png"
            },
            "context": additional_context
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decrypt_token(self, token: str) -> TokenData:
        try:
            result = jwt.decode(token, self.secret, algorithms=["HS256"])
        except jose.JWTError:
            raise Exception("Invalid token")
        if "user" not in result or "context" not in result:
            raise Exception("Invalid token")
        result = typing.cast(TokenData, result)
        return result
