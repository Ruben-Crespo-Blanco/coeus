from fastapi import FastAPI
from src.database import engine, Base
import uvicorn

# Routers
from src.routers import content, exam, review, recall, unit_exam

def create_app() -> FastAPI:
    app = FastAPI(title="Coeus")

    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    # Include Routers
    app.include_router(content.router, prefix="/content", tags=["Content"])
    app.include_router(exam.router, prefix="/exam", tags=["Exam"])
    app.include_router(review.router, prefix="/review", tags=["Review"])
    app.include_router(recall.router, prefix="/remember", tags=["Recall"])
    app.include_router(unit_exam.router, prefix="/unit_exam", tags=["Unit Exam"])
    
    return app

app = create_app()
if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)