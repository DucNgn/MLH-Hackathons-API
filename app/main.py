import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

from app.controller.events import start_harvest_thread
from app.config import get_settings

settings = get_settings()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def scheduler_harvesting():
    scheduler = BackgroundScheduler()
    scheduler.add_job(start_harvest_thread, "cron", minute="0", hour="9,21")
    scheduler.start()


app.mount(
    "/data",
    StaticFiles(directory=str(settings.MLH_EVENT_STORAGE_FOLDER_PATH)),
    name="events",
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
