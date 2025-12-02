from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.core.agent import AGENT_INSTANCE
from app.tools.calculator import calculator_tool

router = APIRouter()
templates = Jinja2Templates(directory="templates") 

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint_api(request: ChatRequest):
    agent_instance = AGENT_INSTANCE
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agente não disponível. Verifique a inicialização.")

    try:
        result = agent_instance(request.message) 
        response_text = ""
        
        # Lógica de Tool Call (Tool Use -> Tool Response)
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
        # Erros internos do agente ou do Strands
        raise HTTPException(status_code=500, detail=f"Erro no processamento do Agente: {str(e)}")


@router.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "DreamSquad Chat Agent"})