"""Main application module for PromptSafe."""
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app import __version__
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.proxy.browser_extension import browser_extension_manager


# FastAPI uygulaması oluştur
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Yapay zeka modellerinden hassas veri koruması sağlayan güvenlik middleware API'si",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretim ortamında güvenlik için bunu sınırlandır
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Loglama middleware
@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log requests and responses."""
    start_time = time.time()
    
    # İstek bilgileri
    request_id = f"{int(start_time * 1000)}"
    logger.info(
        f"Request [{request_id}]: {request.method} {request.url.path}"
    )
    
    # İsteği işle
    response = await call_next(request)
    
    # İşlem süresi
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Response [{request_id}]: status={response.status_code}, " 
        f"time={process_time:.2f}ms"
    )
    
    # İşlem süresini yanıt başlıklarına ekle
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    return response


# API rotalarını ekle
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": __version__,
        "description": "Yapay zeka modellerinden hassas veri koruması sağlayan güvenlik middleware API'si",
        "docs_url": "/docs",
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for browser extension.
    
    Args:
        websocket: WebSocket connection
        client_id: Client identifier
    """
    # Rastgele bir client_id yoksa oluştur
    if not client_id or client_id == "undefined":
        client_id = str(uuid.uuid4())
    
    # Bağlantıyı kabul et
    await browser_extension_manager.connect(websocket, client_id)
    
    try:
        # Mesajları işle
        await browser_extension_manager.handle_message(websocket, client_id)
    except WebSocketDisconnect:
        # Bağlantı koptuğunda
        browser_extension_manager.disconnect(client_id) 