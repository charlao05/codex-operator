"""
FastAPI Server para NEXUS
Servidor principal com suporte a Stripe Payment Intents
"""

import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importar rotas
from backend.app.api.payments import router as payments_router
from backend.app.api.adsense import router as adsense_router

# ==================== CONFIGURAÇÃO ====================

# Carregar variáveis de ambiente
load_dotenv('.env.local', override=True)
load_dotenv('.env', override=True)

# Configurar logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciar o ciclo de vida da aplicação
    """
    # Startup
    logger.info("🚀 Iniciando servidor NEXUS...")

    # Validar Stripe
    stripe_key = os.getenv('STRIPE_SECRET_KEY')
    if stripe_key:
        logger.info("✅ Stripe configurado")
    else:
        logger.warning("⚠️  STRIPE_SECRET_KEY não configurada")

    yield

    # Shutdown
    logger.info("⛔ Encerrando servidor NEXUS...")

# ==================== APLICAÇÃO ====================

app = FastAPI(
    title="NEXUS API",
    description="API para Diagnósticos com Integração Stripe",
    version="2.0.0",
    lifespan=lifespan
)

# ==================== MIDDLEWARE ====================

# CORS - Permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev server
        "http://localhost:3000",      # Alternate port
        os.getenv('FRONTEND_URL', ''),  # Config from env
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ROTAS ====================

# Health Check
@app.get("/health")
async def health_check():
    """Verificar se o servidor está funcionando"""
    return {
        "status": "ok",
        "service": "NEXUS API",
        "stripe": "configured" if os.getenv('STRIPE_SECRET_KEY') else "not_configured",
        "adsense": "configured" if os.getenv('GOOGLE_ADSENSE_ACCOUNT_ID') else "not_configured"
    }


# Raiz
@app.get("/")
async def root() -> dict[str, str | dict[str, str]]:
    """Rota raiz - informações da API"""
    return {
        "name": "NEXUS API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "payments": "/api/payments",
            "adsense": "/api/adsense",
            "docs": "/docs"
        }
    }

# Incluir rotas de pagamento
app.include_router(payments_router)

# Incluir rotas do AdSense
app.include_router(adsense_router)


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Tratador global de exceções"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8000))

    logger.info(f"🌐 Iniciando servidor na porta {port}...")
    logger.info(f"📚 Documentação: http://localhost:{port}/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
