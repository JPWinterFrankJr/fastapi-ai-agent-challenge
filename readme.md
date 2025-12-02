# 🚀 Configuração e Execução do Projeto (Ubuntu)

Siga os passos abaixo para configurar o ambiente de desenvolvimento e executar o agente de IA.

## Pré-requisitos (Python 3.12.3)
Para executar este projeto, você precisa ter instalado:

Python 3.12.3

pip (gerenciador de pacotes Python)

Git (para clonar o repositório)

Ollama (para rodar o LLM localmente)

Certifique-se de que o **Python 3.12.3** está instalado no seu sistema.

## 1. Configuração do Ambiente e  Instalação

# 1.1 Clonar o Repositório
git clone https://github.com/JPWinterFrankJr/fastapi-ai-agent-challenge.git
cd fastapi-ai-agent-challenge

# 2. Configure o .env
PORT e HOST DO SEU SERVIDOR. E o modelo do OLLAMA utilizado é o mistral
HOST=
PORT=
OLLAMA_HOST=
OLLAMA_MODEL=

## 1.2 Cria o ambiente virtual e Ativar o Ambiente Virtual
 # Cria o ambiente virtual
 python3.12 -m venv .venv
 
 # Ativa o ambiente virtual (Linux/macOS) 
 source .venv/bin/activate

## 1.3 Instalar as dependencias.
pip install -r requirements.txt
## 2. Configuração do Ollama e Variáveis de Ambiente
# 2.1. Instalar e Iniciar o Ollama
ollama serve
# 2.2. Baixar o Modelo LLM
ollama pull mistral
# 2.3. Configurar o Arquivo .env
 OLLAMA_HOST: Endereço do servidor Ollama. Padrão: http://127.0.0.1:11434
 OLLAMA_HOST=http://127.0.0.1:11434
 OLLAMA_MODEL=mistral
Configurações do Servidor FastAPI .env
 HOST=0.0.0.0
 PORT=8000
# 3. Executar o agente 
uvicorn main:app --reload 