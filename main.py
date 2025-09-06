from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI,Request
from database import Base,engine
from utils.private import GOOGLE_KEY
from app.auth.user_route import router as user_router
from app.auth.user_monitor import routes as user_moditor
from app.class_room.classes.classes_route import route as classes_route
from app.class_room.subjects.subject_route import route as subject_route
from app.class_room.topics.topic_route import route as topic_route
from app.class_room.video.video_route import route as video_route
from app.business_control.sales.sales_routes import routes as sales_rotes
from app.platform_control.route import routes as platform_routes
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/statics", StaticFiles(directory="statics"), name="statics")
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://192.168.183.166", "http://localhost:19006"] (Expo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=GOOGLE_KEY
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/content/{page}", response_class=HTMLResponse)
def load_content(request: Request, page: str):
    return templates.TemplateResponse(f"partials/{page}.html", {"request": request})

app.include_router(user_router, prefix="/auth")
app.include_router(user_moditor,prefix="/api")
app.include_router(classes_route,prefix="/route")
app.include_router(subject_route,prefix="/route")
app.include_router(topic_route,prefix="/route")
app.include_router(video_route,prefix="/route")
app.include_router(sales_rotes,prefix="/route")
app.include_router(platform_routes,prefix="/route")
