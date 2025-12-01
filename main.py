# main.py
import os
import math
import json # Adicionado para uso futuro, se necessário
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Importações oficiais do Strands Agents SDK
# CORREÇÃO 1: Importação correta do OllamaModel
from strands import Agent, tool
from strands.models.ollama import OllamaModel 

# ----------------------------------------------------------------------
# 1. CONFIGURAÇÃO INICIAL
# ----------------------------------------------------------------------

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do FastAPI
app = FastAPI(
    title="DreamSquad Chat API",
    description="API integrada com Strands Agents SDK e Ollama",
    version="1.0.0"
)

# Configuração do Jinja2 para ler arquivos na pasta 'templates'
# Certifique-se de que a pasta 'templates' está no mesmo nível que 'main.py'
templates = Jinja2Templates(directory="templates") 


# ----------------------------------------------------------------------
# 2. DEFINIÇÃO DA TOOL
# ----------------------------------------------------------------------

# 2. DEFINIÇÃO DA TOOL
@tool
def calculator_tool(expression: str) -> float:
    """Ferramenta de cálculo. Use a notação Python e o prefixo 'math.' para sqrt, log, etc.
    
    Exemplos: 'math.sqrt(144) * 10' ou '1234 + 5678'.
    """
    try:
        # Define um dicionário com funções seguras para o 'eval'
        # Isso permite que o 'eval' use 'math.sqrt', 'math.pow', etc.
        safe_globals = {"math": math}
        
        # O eval usa o dicionário 'safe_globals' como contexto,
        # permitindo o uso de 'math.sqrt()' na expressão.
        result = eval(expression, {"__builtins__": None}, safe_globals)
        return result
        
    except Exception as e:
        # Isso será formatado como um erro, e o Agente terá que lidar com ele.
        return f"Erro de cálculo: {e}"
# ----------------------------------------------------------------------
# 3. INICIALIZAÇÃO GLOBAL DO AGENTE (CORREÇÃO DO NameError)
# ----------------------------------------------------------------------

# Definição das variáveis de ambiente
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# A variável 'agent_instance' é inicializada no escopo global
agent_instance = None 

if OLLAMA_HOST and OLLAMA_MODEL:
    try:
        #Cria o modelo Ollama
        ollama_model = OllamaModel(
            model_id=OLLAMA_MODEL,
            host=OLLAMA_HOST  # <--- CORRIGIDO: Troca de 'base_url' para 'host'
        )

        # Cria o Agente com a tool e o modelo (Modelo 'mistral' é necessário para Tool Calling)
        agent_instance = Agent(
            model=ollama_model,
            tools=[calculator_tool],
            name="DreamSquad Agent",
            system_prompt="""
Você é um assistente de IA prestativo, claro e objetivo.

REGRAS PRINCIPAIS:
1. Você SEMPRE deve usar exclusivamente a calculator_tool para QUALQUER operação matemática,
   mesmo que seja extremamente simples (ex.: 1+1, 10*5, raiz quadrada, porcentagem, juros, etc).

2. Você NUNCA deve calcular nada sozinho. 
   Sempre que detectar um cálculo, gere imediatamente uma chamada da ferramenta calculator_tool.

3. Sua resposta final ao usuário deve ser:
   - Natural e conversacional
   - Sem mostrar código, formatação técnica, chamadas de ferramenta ou detalhes internos

4. Nunca repita a pergunta do usuário.

5. Para perguntas gerais (ciência, história, explicações), responda normalmente sem usar a ferramenta.

6. Se a calculator_tool retornar um erro, explique de forma amigável.

7. Você está PROIBIDO de gerar valores numéricos derivados de operações matemáticas.
   Apenas reescreva o resultado retornado pela ferramenta de maneira natural.
"""
             )
        print(f"INFO: Agente de IA carregado com sucesso usando modelo: {OLLAMA_MODEL}")

    except Exception as e:
        print(f"ERRO CRÍTICO NA INICIALIZAÇÃO DO AGENTE: {e}. Verifique se o 'ollama serve' está rodando e se o modelo '{OLLAMA_MODEL}' foi baixado.")
        # Se falhar, agent_instance permanece None para que o endpoint retorne 503
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# 4. MODELOS DE DADOS (Pydantic)
# ----------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str


# ----------------------------------------------------------------------
# 5. ENDPOINTS DA API
# ----------------------------------------------------------------------

# main.py


# Endpoint POST para comunicação da API de chat
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint_api(request: ChatRequest):
    # Verifica se o agente foi inicializado com sucesso
    if not agent_instance:
        raise HTTPException(
            status_code=503, 
            detail="Agente não disponível. O Ollama Server falhou ao carregar."
        )

    try:
        # Tenta a chamada normal do agente
        result = agent_instance(request.message) 
        
        # --- LÓGICA DE TRATAMENTO DE TOOL CALL MANUAL CORRIGIDA ---
        
        # Verifica se o resultado é uma lista de Tool Calls
        if isinstance(result, list) and result and "name" in result[0]:
            tool_call = result[0]
            
            # Trata o uso de tool para cálculo
            if tool_call["name"] == "calculator_tool":
                expression = tool_call["arguments"].get("expression")
                
                # Executa a tool para obter o resultado (e.g., 120.0)
                tool_result = calculator_tool(expression)
                
                # CHAVE DA CORREÇÃO: Alimentar o Agente com o resultado da ferramenta.
                # O Agente usa o resultado (tool_result) para gerar uma resposta natural e conversacional.
                response_text = agent_instance(
                    request.message, # Mensagem original
                    tool_result=tool_result, # Resultado da ferramenta
                    tool_name="calculator_tool" # Nome da ferramenta
                )

            else:
                # Se o LLM alucinar uma tool que não existe
                response_text = f"Desculpe, não consegui processar a sua solicitação. O Agente tentou usar a ferramenta '{tool_call['name']}' de forma incorreta."
        
        else:
            # Se não é um Tool Call, é uma resposta conversacional
            response_text = result if isinstance(result, str) else str(result)
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        # Captura qualquer erro
        raise HTTPException(status_code=500, detail=f"Erro no processamento do Agente: {str(e)}")


# Endpoint GET para o Frontend
@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Renderiza a página HTML do chat."""
    # O TemplateResponse procura 'index.html' no diretório 'templates'
    return templates.TemplateResponse("index.html", {"request": request})