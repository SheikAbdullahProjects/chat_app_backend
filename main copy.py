from fastapi import FastAPI
from dotenv import load_dotenv
from database import Base, engine
from auth.routes import router as a_router
from conversation.routes import router as c_router
from fastapi.middleware.cors import CORSMiddleware




load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chat Application",
    description="Chat Application with Images sending functionality",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(a_router)
app.include_router(c_router)

@app.get("/")
async def get_root():
    return {
        "detail" : "Working Fine"
    }
    
    
