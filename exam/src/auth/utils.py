from fastapi import FastAPI, Response
from datetime import datetime, timedelta, timezone

app = FastAPI()



async def set_cookie(
    response: Response,
    key: str,
    value: str,
    max_age: int = 3600,
    httponly: bool = True,
    secure: bool = False,
    path: str = "/",
):
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        expires=datetime.now(timezone.utc) + timedelta(seconds=max_age),
        path=path,
        httponly=httponly,
        secure=secure,
    )