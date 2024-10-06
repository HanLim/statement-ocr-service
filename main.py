from fastapi import FastAPI

from webserver.urls import router as router

app = FastAPI()
app.include_router(router)
