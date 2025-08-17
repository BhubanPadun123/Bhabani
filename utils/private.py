from datetime import datetime,timedelta
from jose import JWSError,jwt
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2AuthorizationCodeBearer,OAuth2PasswordBearer


SECRET_KEY="siw jwirwi  ijwirhi wrwerhwi reihruie rjwo qijrowq rwhr hewiurh wrewrwr"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60 


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/")
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWSError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
SUPABASE_URL="https://rerwkrshqiwoxumshjzk.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJlcndrcnNocWl3b3h1bXNoanprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjE3ODksImV4cCI6MjA3MDEzNzc4OX0.aZNkW5hZqhQCHw7ElQAD41WVhprwCJoagX2vhzgXlyk"

GOOGLE_KEY="e3cbb2381a8e92c5fa1d19d34f2a6ef2e2b22bb3a7e7d4b589b88a39baf00c67"

RAZORPAY_KEY_ID = "rzp_test_R604rQabxOe3Fw"
RAZORPAY_KEY_SECRET = "VBDyk9dYdA7Hcr82985xeaCX"
