from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd.hash(password)



def verify_password(request_password : str , hashed_password : str):
    return pwd.verify(request_password, hashed_password)
