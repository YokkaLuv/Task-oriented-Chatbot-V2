from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat_routes import router as chat_router
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory=os.getenv("FRONT_END"), html=True), name="frontend")

@app.get("/")
def root():
    return {"message": "Design Assistant API is running."}
