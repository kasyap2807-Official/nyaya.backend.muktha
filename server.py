# main.py
from fastapi import FastAPI
from app.adminblogs import admin_app
from app.analysis import analysis_app
from app.blogs import blogs_app
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
import requests

# Create main FastAPI app
app = FastAPI(title="Main Application with mounts")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the three imported apps
app.mount("/app1", analysis_app)
app.mount("/app2", blogs_app)
app.mount("/app3", admin_app)

@app.get("/")
async def main_root():
    return {
        "message": "Main app with three mounted sub‑apps",
        "endpoints": {
            "app1": "/app1",
            "app2": "/app2",
            "app3": "/app3"
        }
    }

URL = "https://nyaya-backend-muktha.onrender.com/ping"  # self endpoint


@app.get("/ping")
def ping():
    return {"message": "I'm alive!"}


def self_ping():
    while True:
        try:
            res = requests.get(URL)
            print("Pinged:", res.status_code, res.json())
        except Exception as e:
            print("Error:", e)
        time.sleep(30)


@app.on_event("startup")
def start_self_ping():
    thread = threading.Thread(target=self_ping, daemon=True)
    thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)