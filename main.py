import os
from dotenv import load_dotenv, find_dotenv # Adicionando find_dotenv
from fastapi import FastAPI

# ----------------------------------------------------------------------
# 1. CONFIGURAÇÃO E INICIALIZAÇÃO
# ----------------------------------------------------------------------

load_dotenv(find_dotenv())

from app.api import chat # Importa o roteador

# Instância do FastAPI
app = FastAPI(
    title="DreamSquad Chat API",
    description="API integrada com Strands Agents SDK e Ollama",
    version="1.0.0"
)

# ----------------------------------------------------------------------
# 2. INCLUSÃO DE ROTAS
# ----------------------------------------------------------------------

# Adiciona o roteador de chat (que contém o /chat e /)
app.include_router(chat.router)

if __name__ == "__main__":
    # Comando de execução do Uvicorn (opcional, mas bom para testes locais)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)