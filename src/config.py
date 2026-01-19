"""
Configurações centralizadas do sistema.
"""
import os
import sys

# Diretório base do projeto
if getattr(sys, 'frozen', False):
    # Se estiver rodando como executável PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Se estiver rodando como script Python
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretórios
DATA_DIR = os.path.join(BASE_DIR, 'data')
SRC_DIR = os.path.join(BASE_DIR, 'src')
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Garantir que diretórios existam
os.makedirs(DATA_DIR, exist_ok=True)

# Arquivos de dados
ARQUIVO_PROJETOS = os.path.join(DATA_DIR, 'dados_projetos.json')
ARQUIVO_USUARIOS = os.path.join(DATA_DIR, 'dados_usuarios.json')

# Banco de dados SQLite
DB_PATH = os.path.join(DATA_DIR, 'projetox.db')

# Configurações da aplicação
APP_TITLE = "ProjetoX - Gerenciador de Projetos"
APP_VERSION = "2.0"
LOGIN_TITLE = "Login - ProjetoX"

# Cores e tema
THEME_MODE = "dark"
COLOR_THEME = "blue"
