from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

hash_password = PasswordHash((Argon2Hasher(), ))


def password_hash(password: str):
    hashed = hash_password.hash(password)
    return hashed



# print(password_hash("Zain432!"))



def verify_password(plain_pass: str, hashed_pass: str):
    is_correct = hash_password.verify(plain_pass, hashed_pass)
    return is_correct


print(verify_password("Zain432!", password_hash("Zain432!")))

