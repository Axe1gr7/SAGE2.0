from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.auth import limiter
from app.routers import (
    auth_router, estudiantes_router, administradores_router,
    espacios_router, equipos_router, clases_router,
    eventos_router, reservas_router, estadisticas_router
)
from app.data.database import engine
from app.models.SAGE_BD import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SAGE API", version="1.0")
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