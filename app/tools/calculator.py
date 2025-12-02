import math
from strands import tool

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