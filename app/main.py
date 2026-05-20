from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.http.routes import auth_routes, customer_routes, service_order_routes
from app.infra.database.base import Base
from app.infra.database.session import engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Service Order Management API",
    description="API for managing technical assistance service orders",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(customer_routes.router)
app.include_router(service_order_routes.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Service Order Management API"}
