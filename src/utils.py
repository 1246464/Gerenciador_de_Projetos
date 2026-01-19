"""
Utilitários e funções auxiliares.
"""
import hashlib
import re
from datetime import datetime
from typing import Optional


def hash_senha(senha: str) -> str:
    """
    Cria hash SHA-256 da senha para armazenamento seguro.
    
    Args:
        senha: Senha em texto plano
        
    Returns:
        Hash SHA-256 da senha
    """
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """
    Verifica se a senha corresponde ao hash armazenado.
    
    Args:
        senha: Senha fornecida pelo usuário
        hash_armazenado: Hash SHA-256 armazenado
        
    Returns:
        True se a senha estiver correta, False caso contrário
    """
    return hash_senha(senha) == hash_armazenado


def validar_data(data: str) -> bool:
    """
    Valida formato de data DD-MM-AAAA ou DD/MM/AAAA.
    
    Args:
        data: String com a data
        
    Returns:
        True se a data for válida, False caso contrário
    """
    if not data:
        return True  # Data vazia é permitida
    
    # Aceita tanto - quanto /
    padrao = r'^\d{2}[-/]\d{2}[-/]\d{4}$'
    if not re.match(padrao, data):
        return False
    
    try:
        # Tenta converter para validar se é uma data real
        dia, mes, ano = re.split(r'[-/]', data)
        datetime(int(ano), int(mes), int(dia))
        return True
    except ValueError:
        return False


def validar_nome(nome: str, min_length: int = 2, max_length: int = 100) -> tuple[bool, str]:
    """
    Valida nome de usuário, projeto, etapa, etc.
    
    Args:
        nome: Nome a ser validado
        min_length: Tamanho mínimo permitido
        max_length: Tamanho máximo permitido
        
    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not nome or not nome.strip():
        return False, "O nome não pode estar vazio."
    
    nome = nome.strip()
    
    if len(nome) < min_length:
        return False, f"O nome deve ter pelo menos {min_length} caracteres."
    
    if len(nome) > max_length:
        return False, f"O nome deve ter no máximo {max_length} caracteres."
    
    return True, ""


def sanitizar_nome_arquivo(nome: str) -> str:
    """
    Remove caracteres inválidos para nomes de arquivo.
    
    Args:
        nome: Nome original
        
    Returns:
        Nome sanitizado
    """
    # Remove caracteres especiais não permitidos em nomes de arquivo
    caracteres_invalidos = r'[<>:"/\\|?*]'
    nome_limpo = re.sub(caracteres_invalidos, '_', nome)
    return nome_limpo.strip()


def calcular_progresso(etapas: list) -> int:
    """
    Calcula o progresso do projeto baseado nas etapas concluídas.
    
    Args:
        etapas: Lista de etapas do projeto
        
    Returns:
        Porcentagem de progresso (0-100)
    """
    if not etapas:
        return 0
    
    concluidas = sum(1 for etapa in etapas if etapa.get('status', '').lower() == 'concluído')
    return int((concluidas / len(etapas)) * 100)
