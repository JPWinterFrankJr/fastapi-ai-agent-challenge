### IMPORTANTE:
# O agente está levando de 2 min até mais para responder as perguntas, caso demore espere por um tempo que ele irá responder. 

# 🚀 Configuração e Execução do Projeto (Ubuntu)

Siga os passos abaixo para configurar o ambiente de desenvolvimento e executar o agente de IA.

### 1. Configuração do Ambiente e  Instalação

## 1.1 Clonar o Repositório
git clone https://github.com/JPWinterFrankJr/fastapi-ai-agent-challenge.git;
cd fastapi-ai-agent-challenge

## 1.2 Cria o ambiente virtual e Ativar o Ambiente Virtual
 # Cria o ambiente virtual
 python3.12 -m venv .venv
 # Ativa o ambiente virtual (Linux/macOS) 
 source .venv/bin/activate
 # Instalar python 3 no ambiente virtual
 sudo apt install python3

## 1.3 Instalar as dependencias.
pip install -r requirements.txt
### 2. Configuração do Ollama e Variáveis de Ambiente
## 2.1. Verificar se o ollama está instalado
ollama list
## 2.2. Configurar no arquivo .env o modelo e o host do Ollama
 OLLAMA_HOST: Endereço do servidor Ollama.
 # Host padrão do ollama
 OLLAMA_HOST=http://127.0.0.1:11434 
 OLLAMA_MODEL=mistral
### 3. Executar o agente 
uvicorn main:app --reload 