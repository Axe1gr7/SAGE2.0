from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import limiter
from app.data.database import engine
from app.models.SAGE_BD import Base
from app.routers import (
    administradores_router,
    auth_router,
    clases_router,
    equipos_router,
    espacios_router,
    estadisticas_router,
    estudiantes_router,
    eventos_router,
    reservas_router,
)

Base.metadata.create_all(bind=engine)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        return response


app = FastAPI(title="SAGE API", version="1.0")
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(estudiantes_router)
app.include_router(administradores_router)
app.include_router(espacios_router)
app.include_router(equipos_router)
app.include_router(clases_router)
app.include_router(eventos_router)
app.include_router(reservas_router)
app.include_router(estadisticas_router)

@app.get("/")
def root():
    return {"message": "SAGE API funcionando"}