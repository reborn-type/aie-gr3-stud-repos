from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.AppealController import router as appeal_router
from models.lifecycle import lifespan

app = FastAPI(
    title="Service for route appeals",
    version="0.1.0",
    description=(
        "Http сервис для классификации обращений в службу технической поддержки и маршрутизации их на нужный отдел"
        " Использует bert модель для классификации русскоязычных обращений в банки и определения их тематики"
    ),
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appeal_router)

@app.get(
    "/health",
    tags=["Health"],
    summary="Проверить состояние сервиса",
    description="Возвращает базовую информацию о доступности backend-сервиса.",
    responses={
        200: {
            "description": "Сервис доступен",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "service": "route-appeals",
                        "version": "0.1.0",
                    },
                }
            },
        },
    },
)
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "route-appeals",
        "version": "0.1.0",
    }
