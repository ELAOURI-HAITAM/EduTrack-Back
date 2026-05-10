from datetime import datetime , timedelta
import jwt
import os
from dotenv import load_dotenv
load_dotenv()

secret_key =  os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRES_MINUTES = 120
def access_token(data : dict):
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({
        "exp" : expires
    })

    jwt_code = jwt.encode(to_encode,secret_key,algorithm)
    return jwt_code
