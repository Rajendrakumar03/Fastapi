import bcrypt


def hash_password(plain_password:str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'),salt).decode('utf-8')

def verify_password(plain_password:str,hashed_password:str):
    return bcrypt.checkpw(plain_password.encode('utf-8'),hashed_password.encode('utf-8'))