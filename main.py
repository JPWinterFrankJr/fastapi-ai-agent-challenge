# main.py

import os
import math
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Importações oficiais do Strands Agents SDK
from strands import Agent, tool
from strands.models.ollama import OllamaModel 

# ----------------------------------------------------------------------
# 1. CONFIGURAÇÃO INICIAL
# ----------------------------------------------------------------------

load_dotenv()
app = FastAPI(
    title="DreamSquad Chat API",
    description="API integrada com Strands Agents SDK e Ollama",
    version="1.0.0"
)
templates = Jinja2Templates(directory="templates") 

# ----------------------------------------------------------------------
# 2. DEFINIÇÃO DA TOOL (CÁLCULO)
# ----------------------------------------------------------------------

SAFE_GLOBALS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "pi": math.pi, "e": math.e,
    "pow": math.pow, "round": round, "abs": abs,
}

@tool
def calculator_tool(expression: str) -> str:
    """
    Ferramenta de cálculo matemático. Use notação Python. 
    Funções como 'sqrt', 'log' ou 'round' estão disponíveis sem o prefixo 'math.'.

    Exemplos: 
    'sqrt(144) * 10' 
    '1234 + 5678'
    """
    try:
        result = eval(expression, {"__builtins__": None}, SAFE_GLOBALS)
        
        # Formatação para output limpo
        if isinstance(result, (int, float)) and result == int(result):
             return str(int(result))
        
        return str(result)
        
    except Exception as e:
        return f"Erro de cálculo na expressão '{expression}': {e}"

# ----------------------------------------------------------------------
# 3. INICIALIZAÇÃO GLOBAL DO AGENTE COM PROMPT REFORÇADO (ÚLTIMA TENTATIVA)
# ----------------------------------------------------------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
agent_instance = None 

if OLLAMA_HOST and OLLAMA_MODEL:
    try:
        ollama_model = OllamaModel(model_id=OLLAMA_MODEL, host=OLLAMA_HOST)

        # PROMPT DE SISTEMA OBRIGANDO O USO DA TOOL E CITAÇÃO DO RESULTADO
        SYSTEM_PROMPT = f"""
Você é um assistente de IA prestativo, claro e objetivo. Seu nome é DreamSquad Agent.
Seu objetivo é parecer **natural** e **evitar qualquer jargão técnico** ou menção a ferramentas no output.

REGRAS RÍGIDAS DE CÁLCULO:
1. Você DEVE usar EXCLUSIVAMENTE sua capacidade de cálculo para QUALQUER operação matemática. (Não mencione o nome desta capacidade/ferramenta no output.)
2. Você NUNCA deve tentar calcular ou arredondar valores por conta própria.
3. Para eliminar ambiguidades, SEMPRE use parênteses ( ) na expressão interna 
   para garantir a ordem correta das operações.
   Exemplo: Se o usuário diz 'raiz quadrada de 144 vezes 10', você deve gerar a expressão 'sqrt(144) * 10'.

REGRAS RÍGIDAS DE RESPOSTA (O MAIS IMPORTANTE):
4. Sua resposta final DEVE ser 100% fiel ao VALOR RETORNADO pelo cálculo.
5. Você está ABSOLUTAMENTE PROIBIDO de mudar, modificar, arredondar, ou alucinar o número.
6. Você está PROIBIDO de adicionar zeros ou multiplicar o resultado por 10, 100 ou 1000 ao reescrever.
7. **Para cálculos, sua resposta DEVE ser direta e conversacional.** Ela deve incluir uma breve explicação do processo que levou ao resultado (Ex: "O cálculo envolveu primeiro achar a raiz quadrada de 144, que é 12, e depois multiplicar por 10.").
8. Você está TERMINANTEMENTE PROIBIDO de incluir no output as seguintes frases ou palavras: "tool", "calculator_tool", "ferramenta", "código", "chamada de ferramenta", "busca de informações", "cálculo matemático", "resultado exato retornado pela ferramenta".
9. **SE VOCÊ ESTIVER CALCULANDO**, sua resposta final é o resultado numérico e sua explicação conversacional, e nada mais.
10. **PARA PERGUNTAS DE CONHECIMENTO GERAL:** Responda à pergunta diretamente e de forma completa, sem mencionar que você não está usando a ferramenta de cálculo ou que está realizando uma "busca de informações". Simplesmente responda ao tópico.

Lembre-se: O número retornado pelo cálculo É A ÚNICA VERDADE. Use-o exatamente como é.
"""
        
        agent_instance = Agent(
            model=ollama_model,
            tools=[calculator_tool],
            name="DreamSquad Agent",
            system_prompt=SYSTEM_PROMPT
        )
        print(f"INFO: Agente de IA carregado com sucesso usando modelo: {OLLAMA_MODEL} em {OLLAMA_HOST}")

    except Exception as e:
        print(f"ERRO CRÍTICO NA INICIALIZAÇÃO DO AGENTE: {e}")
        print("Verifique se o 'ollama serve' está rodando e se o modelo foi baixado.")

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

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint_api(request: ChatRequest):
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agente não disponível.")

    try:
        result = agent_instance(request.message) 
        response_text = ""
        
        if isinstance(result, list) and result and isinstance(result[0], dict) and result[0].get("name"):
            
            tool_call = result[0]
            tool_name = tool_call["name"]
            
            if tool_name == "calculator_tool":
                expression = tool_call["arguments"].get("expression")
                tool_result = calculator_tool(expression)
                
                # Segunda chamada ao Agente (Loop Back)
                response_text = agent_instance(
                    request.message, 
                    tool_result=tool_result, 
                    tool_name=tool_name
                )
            else:
                 response_text = f"Desculpe, não consigo usar a ferramenta '{tool_name}'. Eu só sei calcular."
        
        else:
            response_text = result if isinstance(result, str) else str(result)
            
        return ChatResponse(response=response_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento do Agente: {str(e)}")


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "DreamSquad Chat Agent"})