from pwdlib import PasswordHash   # type: ignore
from pwdlib.hashers.argon2 import Argon2Hasher  # type: ignore


hash_password = PasswordHash((Argon2Hasher(), ))



def password_hasher(password: str) -> str:
    return hash_password.hash(password)


# print(password_hasher("ZainAli1245"))



def verify_password(plain_password: str , hashed_password: str) -> bool:
    return hash_password.verify(plain_password, hashed_password)


print(verify_password("ZainAli124", "$argon2id$v=19$m=65536,t=3,p=4$m6AnCzFLWq69ZDB88kxJ/w$mE94vKUMAePc5SPxf36Z8dsUhz3KrLqu4eQ67lN6Gpo"))
print(verify_password("ZainAli1245", "$argon2id$v=19$m=65536,t=3,p=4$bdAnFoCcCSBaQxryrbmYjQ$a6EX+7ft9ZA4xSdAEWnr07S3u/v32IHHGkTo7/CgcCk"))


# same password different hash every time due to salting mechanism.
# salting in easy words is adding some random text to the password before hashing it, so even if two users have the same password, their hashed passwords will be different.
# this mechanism helps to protect against rainbow table attacks.
# rainbow table attack is a type of attack where attacker uses precomputed tables of hashed passwords to crack the passwords.
