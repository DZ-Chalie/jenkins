from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.api.board import router as board_router
from app.api.ocr import router as ocr_router
from app.api.search import router as search_router
from app.api.cocktail import router as cocktail_router
from app.api.chatbot import router as chatbot_router
from app.api.tasting_note import router as tasting_note_router
from app.api.weather import router as weather_router
from app.api.hansang import router as hansang_router
from app.api.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(board_router, prefix="/board", tags=["board"])
app.include_router(ocr_router, prefix="/ocr", tags=["ocr"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(cocktail_router, prefix="/cocktail", tags=["cocktail"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
app.include_router(tasting_note_router, prefix="/notes", tags=["notes"])
app.include_router(weather_router, prefix="/weather", tags=["weather"])
app.include_router(hansang_router, prefix="/hansang", tags=["hansang"])
from app.api.fair import router as fair_router
app.include_router(fair_router, prefix="/fair", tags=["fair"])
app.include_router(health_router, prefix="/health", tags=["health"])

# CORS Configuration
origins = [
    "*",  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
