"""
Módulo de gerenciamento do banco de dados SQLite.
Substitui o sistema de arquivos JSON por um banco relacional.
"""
import sqlite3
import json
import os
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager

try:
    from config import DATA_DIR
except ImportError:
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Caminho do banco de dados
DB_PATH = os.path.join(DATA_DIR, 'projetox.db')


@contextmanager
def get_connection():
    """
    Context manager para conexão com o banco de dados.
    Garante que a conexão seja fechada após o uso.
    
    Yields:
        Conexão SQLite
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def inicializar_database() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas necessárias.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de Projetos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projetos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cliente TEXT,
                descricao TEXT,
                prazo TEXT,
                orcamento REAL DEFAULT 0.0,
                status TEXT DEFAULT 'ativo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Etapas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS etapas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projeto_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT,
                status TEXT DEFAULT 'em andamento',
                prazo TEXT,
                responsavel TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de Participantes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projeto_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                cargo TEXT,
                etapa TEXT,
                prazo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para melhor performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_etapas_projeto 
            ON etapas(projeto_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_participantes_projeto 
            ON participantes(projeto_id)
        """)
        
        conn.commit()


# =========================
# FUNÇÕES DE PROJETOS
# =========================

def adicionar_projeto(nome: str, cliente: str = "", descricao: str = "", 
                     prazo: str = "", orcamento: float = 0.0, status: str = "ativo") -> int:
    """
    Adiciona um novo projeto ao banco de dados.
    
    Args:
        nome: Nome do projeto
        cliente: Nome do cliente
        descricao: Descrição do projeto
        prazo: Prazo do projeto
        orcamento: Orçamento do projeto
        status: Status do projeto (ativo, concluído, pausado, cancelado)
        
    Returns:
        ID do projeto criado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projetos (nome, cliente, descricao, prazo, orcamento, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, cliente, descricao, prazo, orcamento, status))
        return cursor.lastrowid


def buscar_projeto(projeto_id: int) -> Optional[Dict]:
    """
    Busca um projeto pelo ID.
    
    Args:
        projeto_id: ID do projeto
        
    Returns:
        Dicionário com dados do projeto ou None se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cliente, descricao, prazo, orcamento, status, created_at, updated_at
            FROM projetos WHERE id = ?
        """, (projeto_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def buscar_projeto_completo(projeto_id: int) -> Optional[Dict]:
    """
    Busca um projeto com todas suas etapas e participantes.
    
    Args:
        projeto_id: ID do projeto
        
    Returns:
        Dicionário completo com projeto, etapas e participantes
    """
    projeto = buscar_projeto(projeto_id)
    if not projeto:
        return None
    
    projeto['etapas'] = listar_etapas(projeto_id)
    projeto['participantes'] = listar_participantes(projeto_id)
    
    return projeto


def listar_projetos() -> List[Dict]:
    """
    Lista todos os projetos com suas etapas e participantes.
    
    Returns:
        Lista de dicionários com dados dos projetos
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cliente, descricao, prazo, orcamento, status, created_at, updated_at
            FROM projetos
            ORDER BY created_at DESC
        """)
        
        projetos = [dict(row) for row in cursor.fetchall()]
        
        # Adicionar etapas e participantes a cada projeto
        for projeto in projetos:
            projeto['etapas'] = listar_etapas(projeto['id'])
            projeto['participantes'] = listar_participantes(projeto['id'])
        
        return projetos


def atualizar_projeto(projeto_id: int, nome: str = None, cliente: str = None, 
                     descricao: str = None, prazo: str = None, 
                     orcamento: float = None, status: str = None) -> bool:
    """
    Atualiza dados de um projeto.
    
    Args:
        projeto_id: ID do projeto
        nome: Novo nome (opcional)
        cliente: Novo cliente (opcional)
        descricao: Nova descrição (opcional)
        prazo: Novo prazo (opcional)
        orcamento: Novo orçamento (opcional)
        status: Novo status (opcional)
        
    Returns:
        True se atualizou com sucesso, False caso contrário
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = ?")
        params.append(nome)
    
    if cliente is not None:
        updates.append("cliente = ?")
        params.append(cliente)
    
    if descricao is not None:
        updates.append("descricao = ?")
        params.append(descricao)
    
    if prazo is not None:
        updates.append("prazo = ?")
        params.append(prazo)
    
    if orcamento is not None:
        updates.append("orcamento = ?")
        params.append(orcamento)
    
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if not updates:
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(projeto_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE projetos
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        return cursor.rowcount > 0


def excluir_projeto(projeto_id: int) -> bool:
    """
    Exclui um projeto e todos seus dados relacionados.
    
    Args:
        projeto_id: ID do projeto
        
    Returns:
        True se excluiu com sucesso, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projetos WHERE id = ?", (projeto_id,))
        return cursor.rowcount > 0


# =========================
# FUNÇÕES DE ETAPAS
# =========================

def adicionar_etapa(projeto_id: int, nome: str, descricao: str = "", 
                    status: str = "em andamento", prazo: str = "", responsavel: str = "") -> int:
    """
    Adiciona uma etapa a um projeto.
    
    Args:
        projeto_id: ID do projeto
        nome: Nome da etapa
        descricao: Descrição da etapa
        status: Status da etapa (em andamento, concluído, pausado)
        prazo: Prazo da etapa
        responsavel: Responsável pela etapa
        
    Returns:
        ID da etapa criada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO etapas (projeto_id, nome, descricao, status, prazo, responsavel)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (projeto_id, nome, descricao, status, prazo, responsavel))
        return cursor.lastrowid


def listar_etapas(projeto_id: int) -> List[Dict]:
    """
    Lista todas as etapas de um projeto.
    
    Args:
        projeto_id: ID do projeto
        
    Returns:
        Lista de dicionários com dados das etapas
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, projeto_id, nome, descricao, status, prazo, responsavel, created_at
            FROM etapas
            WHERE projeto_id = ?
            ORDER BY created_at
        """, (projeto_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, status, prazo, responsavel
            FROM etapas
            WHERE projeto_id = ?
            ORDER BY id
        """, (projeto_id,))
        
        return [dict(row) for row in cursor.fetchall()]


def atualizar_etapa(etapa_id: int, nome: str = None, status: str = None,
                    prazo: str = None, responsavel: str = None) -> bool:
    """
    Atualiza dados de uma etapa.
    
    Args:
        etapa_id: ID da etapa
        nome: Novo nome (opcional)
        status: Novo status (opcional)
        prazo: Novo prazo (opcional)
        responsavel: Novo responsável (opcional)
        
    Returns:
        True se atualizou com sucesso, False caso contrário
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = ?")
        params.append(nome)
    
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if prazo is not None:
        updates.append("prazo = ?")
        params.append(prazo)
    
    if responsavel is not None:
        updates.append("responsavel = ?")
        params.append(responsavel)
    
    if not updates:
        return False
    
    params.append(etapa_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE etapas
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        return cursor.rowcount > 0


def excluir_etapa(etapa_id: int) -> bool:
    """
    Exclui uma etapa.
    
    Args:
        etapa_id: ID da etapa
        
    Returns:
        True se excluiu com sucesso, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM etapas WHERE id = ?", (etapa_id,))
        return cursor.rowcount > 0


# =========================
# FUNÇÕES DE PARTICIPANTES
# =========================

def adicionar_participante(projeto_id: int, nome: str, cargo: str = "",
                          etapa: str = "", prazo: str = "") -> int:
    """
    Adiciona um participante a um projeto.
    
    Args:
        projeto_id: ID do projeto
        nome: Nome do participante
        cargo: Cargo do participante
        etapa: Etapa associada
        prazo: Prazo do participante
        
    Returns:
        ID do participante criado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO participantes (projeto_id, nome, cargo, etapa, prazo)
            VALUES (?, ?, ?, ?, ?)
        """, (projeto_id, nome, cargo, etapa, prazo))
        return cursor.lastrowid


def listar_participantes(projeto_id: int) -> List[Dict]:
    """
    Lista todos os participantes de um projeto.
    
    Args:
        projeto_id: ID do projeto
        
    Returns:
        Lista de dicionários com dados dos participantes
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cargo, etapa, prazo
            FROM participantes
            WHERE projeto_id = ?
            ORDER BY id
        """, (projeto_id,))
        
        return [dict(row) for row in cursor.fetchall()]


def buscar_participante_por_nome(projeto_id: int, nome: str) -> Optional[Dict]:
    """
    Busca um participante pelo nome em um projeto específico.
    
    Args:
        projeto_id: ID do projeto
        nome: Nome do participante
        
    Returns:
        Dicionário com dados do participante ou None
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cargo, etapa, prazo
            FROM participantes
            WHERE projeto_id = ? AND nome = ?
        """, (projeto_id, nome))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def atualizar_participante(participante_id: int, nome: str = None, cargo: str = None,
                          etapa: str = None, prazo: str = None) -> bool:
    """
    Atualiza dados de um participante.
    
    Args:
        participante_id: ID do participante
        nome: Novo nome (opcional)
        cargo: Novo cargo (opcional)
        etapa: Nova etapa (opcional)
        prazo: Novo prazo (opcional)
        
    Returns:
        True se atualizou com sucesso, False caso contrário
    """
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = ?")
        params.append(nome)
    
    if cargo is not None:
        updates.append("cargo = ?")
        params.append(cargo)
    
    if etapa is not None:
        updates.append("etapa = ?")
        params.append(etapa)
    
    if prazo is not None:
        updates.append("prazo = ?")
        params.append(prazo)
    
    if not updates:
        return False
    
    params.append(participante_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE participantes
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        return cursor.rowcount > 0


def excluir_participante(participante_id: int) -> bool:
    """
    Exclui um participante.
    
    Args:
        participante_id: ID do participante
        
    Returns:
        True se excluiu com sucesso, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM participantes WHERE id = ?", (participante_id,))
        return cursor.rowcount > 0


# =========================
# FUNÇÕES DE USUÁRIOS
# =========================

def adicionar_usuario(nome: str, senha_hash: str) -> int:
    """
    Adiciona um novo usuário.
    
    Args:
        nome: Nome do usuário
        senha_hash: Hash SHA-256 da senha
        
    Returns:
        ID do usuário criado
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nome, senha_hash)
            VALUES (?, ?)
        """, (nome, senha_hash))
        return cursor.lastrowid


def buscar_usuario(nome: str) -> Optional[Dict]:
    """
    Busca um usuário pelo nome.
    
    Args:
        nome: Nome do usuário
        
    Returns:
        Dicionário com dados do usuário ou None
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, senha_hash, created_at
            FROM usuarios
            WHERE nome = ?
        """, (nome,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def atualizar_senha_usuario(nome: str, novo_hash: str) -> bool:
    """
    Atualiza a senha de um usuário.
    
    Args:
        nome: Nome do usuário
        novo_hash: Novo hash SHA-256 da senha
        
    Returns:
        True se atualizou com sucesso, False caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET senha_hash = ?
            WHERE nome = ?
        """, (novo_hash, nome))
        
        return cursor.rowcount > 0


def listar_usuarios() -> List[Dict]:
    """
    Lista todos os usuários (sem as senhas).
    
    Returns:
        Lista de dicionários com dados dos usuários
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, created_at
            FROM usuarios
            ORDER BY nome
        """)
        
        return [dict(row) for row in cursor.fetchall()]
