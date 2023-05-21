from fastapi import FastAPI, Request, Depends

from logic.token import oauth2_bearer, get_current_user_from_jwt_token
from router import image, admin, login
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(docs_url=None, redoc_url=None)
app.include_router(image.router)
app.include_router(admin.router)
app.include_router(login.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ip")
async def login(request: Request):
    return {
        "data": {
            "headers": request.headers,
            "host": request.client.host
        }
    }


@app.get("/auth")
async def auth_local_storage_token(token: str = Depends(oauth2_bearer)):
    user_id = get_current_user_from_jwt_token(token)
    return {
        "code": 1,
        "hint": "valid_jwt_token"
    }
