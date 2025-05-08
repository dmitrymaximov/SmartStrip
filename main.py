import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.api.routes import router as api_router


app = FastAPI(redoc_url=None, debug=True, docs_url=None)

app.include_router(api_router)

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=443,
                reload=True,
                ssl_keyfile="./ssl/key.pem",
                ssl_certfile="./ssl/cert.pem")