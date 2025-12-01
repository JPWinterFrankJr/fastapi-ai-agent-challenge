# 🚀 Configuração e Execução do Projeto (Ubuntu)

Siga os passos abaixo para configurar o ambiente de desenvolvimento e executar o agente de IA.

## 1. Pré-requisitos (Python 3.12.3)

Certifique-se de que o **Python 3.12.3** está instalado no seu sistema.

# 2. Configure o .env
PORT e HOST DO SEU SERVIDOR. E o modelo do OLLAMA utilizado é o mistral
HOST=
PORT=
OLLAMA_HOST=
OLLAMA_MODEL=

# 3. Cria o ambiente virtual 'venv'
python3.12 -m venv venv

# 4. Ativação do Ambiente Virtual 'venv'
source venv/bin/activate
# 5. Instala as dependencias.
pip install -r requirements.txt

# 6. Executa o agente 
vicorn main:app --reload 