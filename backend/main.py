from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.create_tables import create_tables
from database.db import create_database
from routes.chat import router as chat_router
from routes.dashboard import router as dashboard_router
from routes.health import router as health_router
from routes.ingestion import router as ingestion_router

load_dotenv()

app = FastAPI(title="Lokt")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    create_database()
    create_tables()


app.include_router(health_router)
app.include_router(ingestion_router, prefix="/api", tags=["Ingestion"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
