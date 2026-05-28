from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.http.routes import auth_routes, customer_routes, service_order_routes, part_routes
from app.infra.database.base import Base
from app.infra.database.session import engine
from app.infra.models.user_model import User  # noqa: F401
from app.infra.models.password_recovery_model import PasswordRecovery  # noqa: F401
from app.infra.models.customer_model import Customer  # noqa: F401
from app.infra.models.service_order_model import ServiceOrder  # noqa: F401
from app.infra.models.technician_model import Technician  # noqa: F401
from app.infra.models.part_model import Part  # noqa: F401
from app.infra.models.order_part_model import OrderPart  # noqa: F401
from app.infra.models.history_model import History  # noqa: F401

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Service Order Management API",
    description="API para gerenciamento de ordens de serviço técnicas",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(auth_routes.router)
app.include_router(customer_routes.router)
app.include_router(service_order_routes.router)
app.include_router(part_routes.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Service Order Management API"}