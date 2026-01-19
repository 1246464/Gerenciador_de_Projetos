import json
import os
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from typing import Optional, Callable, Dict, List

# Importar configurações e utilitários
try:
    from config import ARQUIVO_PROJETOS
    from utils import validar_nome, validar_data
    import database as db
    USE_SQLITE = True
except ImportError:
    # Fallback para desenvolvimento
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ARQUIVO_PROJETOS = os.path.join(os.path.dirname(BASE_DIR), 'data', 'dados_projetos.json')
    USE_SQLITE = False
    
    def validar_nome(nome: str, min_length: int = 2, max_length: int = 100) -> tuple:
        if not nome or not nome.strip():
            return False, "O nome não pode estar vazio."
        nome = nome.strip()
        if len(nome) < min_length:
            return False, f"O nome deve ter pelo menos {min_length} caracteres."
        if len(nome) > max_length:
            return False, f"O nome deve ter no máximo {max_length} caracteres."
        return True, ""
    
    def validar_data(data: str) -> bool:
        import re
        from datetime import datetime
        if not data:
            return True
        padrao = r'^\d{2}[-/]\d{2}[-/]\d{4}$'
        if not re.match(padrao, data):
            return False
        try:
            dia, mes, ano = re.split(r'[-/]', data)
            datetime(int(ano), int(mes), int(dia))
            return True
        except ValueError:
            return False

# -----------------------
# Funções de persistência
# -----------------------

def inicializar_banco() -> None:
    """Inicializa o banco de dados (SQLite ou JSON)."""
    if USE_SQLITE:
        db.inicializar_database()
    else:
        os.makedirs(os.path.dirname(ARQUIVO_PROJETOS), exist_ok=True)
        if not os.path.exists(ARQUIVO_PROJETOS):
            with open(ARQUIVO_PROJETOS, "w", encoding='utf-8') as f:
                json.dump({"projetos": []}, f, indent=4, ensure_ascii=False)

def carregar_projetos() -> Dict:
    """
    Carrega todos os projetos (compatível com SQLite e JSON).
    
    Returns:
        Dicionário com lista de projetos
    """
    if USE_SQLITE:
        try:
            db.inicializar_database()
            projetos_list = db.listar_projetos()
            # Converter para formato compatível com código existente
            projetos_completos = []
            for proj in projetos_list:
                projeto_completo = db.buscar_projeto_completo(proj['id'])
                if projeto_completo:
                    projetos_completos.append(projeto_completo)
            return {"projetos": projetos_completos}
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar projetos do banco: {e}")
            return {"projetos": []}
    else:
        inicializar_banco()
        try:
            with open(ARQUIVO_PROJETOS, "r", encoding='utf-8') as f:
                dados = json.load(f)
                if not isinstance(dados, dict) or "projetos" not in dados:
                    return {"projetos": []}
                return dados
        except (json.JSONDecodeError, FileNotFoundError) as e:
            messagebox.showerror("Erro", f"Erro ao carregar projetos: {e}")
            return {"projetos": []}

def salvar_projetos(dados: Dict) -> bool:
    """
    Salva os dados dos projetos (compatível com SQLite e JSON).
    
    Args:
        dados: Dicionário com lista de projetos
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    if USE_SQLITE:
        # No SQLite, os dados já foram salvos diretamente pelas funções específicas
        return True
    else:
        try:
            os.makedirs(os.path.dirname(ARQUIVO_PROJETOS), exist_ok=True)
            with open(ARQUIVO_PROJETOS, "w", encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")
            return False

# -----------------------
# Utilitários
# -----------------------

def gerar_novo_id(dados: Dict) -> int:
    """
    Gera um novo ID único para um projeto.
    
    Args:
        dados: Dicionário com lista de projetos
        
    Returns:
        Novo ID único
    """
    if not dados.get("projetos"):
        return 1
    return max(p.get("id", 0) for p in dados["projetos"]) + 1

def carregar_projeto_por_id(id_projeto: int) -> Optional[Dict]:
    """
    Carrega um projeto específico pelo ID (compatível com SQLite e JSON).
    
    Args:
        id_projeto: ID do projeto
        
    Returns:
        Dicionário com dados do projeto ou None se não encontrado
    """
    if USE_SQLITE:
        try:
            return db.buscar_projeto_completo(id_projeto)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar projeto: {e}")
            return None
    else:
        dados = carregar_projetos()
        for projeto in dados.get("projetos", []):
            if projeto.get("id") == id_projeto:
                return projeto
        return None

def criar_label_entry(janela: ctk.CTkToplevel, texto: str, **kwargs) -> ctk.CTkEntry:
    """
    Cria um label e um entry de forma padronizada.
    
    Args:
        janela: Janela pai
        texto: Texto do label
        **kwargs: Argumentos adicionais para o Entry
        
    Returns:
        Widget Entry criado
    """
    ctk.CTkLabel(janela, text=texto, font=("Roboto", 12)).pack(pady=(10, 0))
    entrada = ctk.CTkEntry(janela, **kwargs)
    entrada.pack(pady=(0, 5))
    return entrada

# -----------------------
# Interface - Projetos
# -----------------------

def adicionar_projeto(janela_pai: ctk.CTk, callback: Optional[Callable] = None) -> None:
    """
    Abre janela para adicionar um novo projeto.
    
    Args:
        janela_pai: Janela principal
        callback: Função a ser chamada após salvar
    """
    janela = ctk.CTkToplevel(janela_pai)
    janela.title('Adicionar Projeto')
    janela.geometry('450x350')
    janela.grab_set()  # Modal
    
    ctk.CTkLabel(
        janela, 
        text="Novo Projeto", 
        font=("Roboto", 18, "bold")
    ).pack(pady=15)

    entry_nome = criar_label_entry(janela, 'Nome do Projeto:', width=350)
    entry_desc = criar_label_entry(janela, 'Descrição:', width=350)

    def salvar():
        nome = entry_nome.get().strip()
        descricao = entry_desc.get().strip()

        # Validações
        valido, mensagem = validar_nome(nome, min_length=3, max_length=100)
        if not valido:
            messagebox.showwarning("Aviso", mensagem)
            return

        if USE_SQLITE:
            try:
                db.adicionar_projeto(nome, descricao)
                messagebox.showinfo("Sucesso", f"Projeto '{nome}' adicionado com sucesso!")
                janela.destroy()
                if callback:
                    callback()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o projeto: {e}")
        else:
            dados = carregar_projetos()
            novo_projeto = {
                "id": gerar_novo_id(dados),
                "nome": nome,
                "descricao": descricao,
                "pessoas": [],
                "etapas": []
            }
            dados["projetos"].append(novo_projeto)
            
            if salvar_projetos(dados):
                messagebox.showinfo("Sucesso", f"Projeto '{nome}' adicionado com sucesso!")
                janela.destroy()
                if callback:
                    callback()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o projeto.")

    # Botões
    btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    ctk.CTkButton(
        btn_frame, 
        text='Salvar Projeto', 
        command=salvar,
        width=150
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame, 
        text='Cancelar', 
        command=janela.destroy,
        width=150,
        fg_color="gray30",
        hover_color="gray20"
    ).pack(side="left", padx=5)

def editar_projeto(janela_pai: ctk.CTk, id_projeto: int, callback: Optional[Callable] = None) -> None:
    """
    Abre janela para editar um projeto existente.
    
    Args:
        janela_pai: Janela principal
        id_projeto: ID do projeto a ser editado
        callback: Função a ser chamada após salvar
    """
    projeto = carregar_projeto_por_id(id_projeto)
    if not projeto:
        messagebox.showerror("Erro", "Projeto não encontrado.")
        return

    janela = ctk.CTkToplevel(janela_pai)
    janela.title('Editar Projeto')
    janela.geometry('450x350')
    janela.grab_set()

    ctk.CTkLabel(
        janela, 
        text="Editar Projeto", 
        font=("Roboto", 18, "bold")
    ).pack(pady=15)

    entry_nome = criar_label_entry(janela, 'Nome do Projeto:', width=350)
    entry_nome.insert(0, projeto.get("nome", ""))

    entry_desc = criar_label_entry(janela, 'Descrição:', width=350)
    entry_desc.insert(0, projeto.get("descricao", ""))

    def salvar():
        nome = entry_nome.get().strip()
        descricao = entry_desc.get().strip()
        
        # Validações
        valido, mensagem = validar_nome(nome, min_length=3, max_length=100)
        if not valido:
            messagebox.showwarning("Aviso", mensagem)
            return
        
        projeto["nome"] = nome
        projeto["descricao"] = descricao
        
        dados = carregar_projetos()
        for i, p in enumerate(dados["projetos"]):
            if p["id"] == id_projeto:
                dados["projetos"][i] = projeto
                break
        
        if salvar_projetos(dados):
            messagebox.showinfo("Sucesso", "Projeto atualizado com sucesso!")
            janela.destroy()
            if callback:
                callback()

    # Botões
    btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    ctk.CTkButton(
        btn_frame, 
        text='Salvar Alterações', 
        command=salvar,
        width=150
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame, 
        text='Cancelar', 
        command=janela.destroy,
        width=150,
        fg_color="gray30",
        hover_color="gray20"
    ).pack(side="left", padx=5)

def excluir_projeto(janela_pai: ctk.CTk, id_projeto: int, callback: Optional[Callable] = None) -> None:
    """
    Exclui um projeto após confirmação.
    
    Args:
        janela_pai: Janela principal
        id_projeto: ID do projeto a ser excluído
        callback: Função a ser chamada após excluir
    """
    projeto = carregar_projeto_por_id(id_projeto)
    if not projeto:
        messagebox.showerror("Erro", "Projeto não encontrado.")
        return
    
    nome_projeto = projeto.get("nome", "este projeto")
    resposta = messagebox.askyesno(
        "Confirmar Exclusão", 
        f"Tem certeza que deseja excluir o projeto '{nome_projeto}'?\n\nEsta ação não pode ser desfeita."
    )
    
    if resposta:
        dados = carregar_projetos()
        dados["projetos"] = [p for p in dados["projetos"] if p.get("id") != id_projeto]
        
        if salvar_projetos(dados):
            messagebox.showinfo("Sucesso", "Projeto excluído com sucesso!")
            if callback:
                callback()

def definir_prazo_geral(janela_pai: ctk.CTk, id_projeto: int, callback: Optional[Callable] = None) -> None:
    """
    Define ou atualiza o prazo geral do projeto.
    
    Args:
        janela_pai: Janela principal
        id_projeto: ID do projeto
        callback: Função a ser chamada após salvar
    """
    projeto = carregar_projeto_por_id(id_projeto)
    if not projeto:
        messagebox.showerror("Erro", "Projeto não encontrado.")
        return
    
    janela = ctk.CTkToplevel(janela_pai)
    janela.title("Definir Prazo")
    janela.geometry("400x250")
    janela.grab_set()
    
    ctk.CTkLabel(
        janela, 
        text="Definir Prazo do Projeto", 
        font=("Roboto", 16, "bold")
    ).pack(pady=15)
    
    ctk.CTkLabel(
        janela, 
        text="Formato: DD-MM-AAAA ou DD/MM/AAAA", 
        font=("Roboto", 11),
        text_color="gray"
    ).pack()
    
    entry_prazo = criar_label_entry(janela, "Prazo:", width=250)
    if "prazo" in projeto:
        entry_prazo.insert(0, projeto["prazo"])
    
    def salvar():
        prazo = entry_prazo.get().strip()
        
        if prazo and not validar_data(prazo):
            messagebox.showwarning("Aviso", "Data inválida! Use o formato DD-MM-AAAA ou DD/MM/AAAA")
            return
        
        projeto["prazo"] = prazo
        dados = carregar_projetos()
        for i, p in enumerate(dados["projetos"]):
            if p["id"] == id_projeto:
                dados["projetos"][i] = projeto
                break
        
        if salvar_projetos(dados):
            messagebox.showinfo("Sucesso", "Prazo atualizado com sucesso!")
            janela.destroy()
            if callback:
                callback()
    
    btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    ctk.CTkButton(
        btn_frame, 
        text="Salvar", 
        command=salvar,
        width=120
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame, 
        text="Cancelar", 
        command=janela.destroy,
        width=120,
        fg_color="gray30",
        hover_color="gray20"
    ).pack(side="left", padx=5)

# -----------------------
# Interface - Etapas
# -----------------------

def adicionar_etapa_com_dados(id_projeto: int, nome: str, status: str, prazo: str, responsavel: str) -> bool:
    """
    Adiciona uma etapa a um projeto específico (compatível com SQLite e JSON).
    
    Args:
        id_projeto: ID do projeto
        nome: Nome da etapa
        status: Status da etapa
        prazo: Prazo da etapa
        responsavel: Responsável pela etapa
        
    Returns:
        True se adicionou com sucesso, False caso contrário
    """
    if USE_SQLITE:
        try:
            db.adicionar_etapa(id_projeto, nome, status, prazo, responsavel)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar etapa: {e}")
            return False
    else:
        dados = carregar_projetos()
        for projeto in dados["projetos"]:
            if projeto.get("id") == id_projeto:
                projeto.setdefault("etapas", []).append({
                    "nome": nome,
                    "status": status,
                    "prazo": prazo,
                    "responsavel": responsavel
                })
                return salvar_projetos(dados)
        return False

def janela_adicionar_etapa(janela_pai: ctk.CTk, callback: Optional[Callable] = None) -> None:
    """
    Abre janela para adicionar uma nova etapa a um projeto.
    
    Args:
        janela_pai: Janela principal
        callback: Função a ser chamada após salvar
    """
    janela = ctk.CTkToplevel(janela_pai)
    janela.title("Adicionar Etapa")
    janela.geometry("450x500")
    janela.grab_set()
    
    ctk.CTkLabel(
        janela, 
        text="Nova Etapa", 
        font=("Roboto", 18, "bold")
    ).pack(pady=15)

    entry_id = criar_label_entry(janela, "ID do Projeto:", width=350)
    entry_nome = criar_label_entry(janela, "Nome da Etapa:", width=350)

    ctk.CTkLabel(janela, text="Status:", font=("Roboto", 12)).pack(pady=(10, 0))
    option_status = ctk.CTkOptionMenu(
        janela, 
        values=["pendente", "em andamento", "concluído"],
        width=350
    )
    option_status.set("pendente")
    option_status.pack(pady=(0, 5))

    entry_prazo = criar_label_entry(janela, "Prazo (DD-MM-AAAA):", width=350)
    entry_responsavel = criar_label_entry(janela, "Responsável:", width=350)

    def salvar():
        try:
            id_projeto = int(entry_id.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "ID do projeto deve ser um número válido.")
            return

        nome = entry_nome.get().strip()
        status = option_status.get()
        prazo = entry_prazo.get().strip()
        responsavel = entry_responsavel.get().strip()

        # Validações
        valido, mensagem = validar_nome(nome, min_length=3, max_length=100)
        if not valido:
            messagebox.showwarning("Aviso", f"Nome da etapa: {mensagem}")
            return
        
        if prazo and not validar_data(prazo):
            messagebox.showwarning("Aviso", "Data inválida! Use o formato DD-MM-AAAA ou DD/MM/AAAA")
            return

        sucesso = adicionar_etapa_com_dados(id_projeto, nome, status, prazo, responsavel)
        if sucesso:
            messagebox.showinfo("Sucesso", "Etapa adicionada com sucesso!")
            janela.destroy()
            if callback:
                callback()
        else:
            messagebox.showerror("Erro", f"Projeto com ID {id_projeto} não encontrado.")

    # Botões
    btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    ctk.CTkButton(
        btn_frame, 
        text="Salvar Etapa", 
        command=salvar,
        width=150
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame, 
        text="Cancelar", 
        command=janela.destroy,
        width=150,
        fg_color="gray30",
        hover_color="gray20"
    ).pack(side="left", padx=5)

# -----------------------
# Participantes (completo)
# -----------------------

def adicionar_participante(janela: ctk.CTk, id_projeto: int, callback: Optional[Callable] = None) -> None:
    """
    Abre janela para adicionar um participante ao projeto.
    
    Args:
        janela: Janela principal
        id_projeto: ID do projeto
        callback: Função a ser chamada após salvar
    """
    if id_projeto is None:
        messagebox.showwarning("Aviso", "Selecione um projeto primeiro.")
        return
    
    projeto = carregar_projeto_por_id(id_projeto)
    if not projeto:
        messagebox.showerror("Erro", "Projeto não encontrado.")
        return

    win = ctk.CTkToplevel(janela)
    win.title("Adicionar Participante")
    win.geometry("450x450")
    win.grab_set()
    
    ctk.CTkLabel(
        win, 
        text="Novo Participante", 
        font=("Roboto", 18, "bold")
    ).pack(pady=15)

    entry_nome = criar_label_entry(win, "Nome:", width=350)
    entry_cargo = criar_label_entry(win, "Cargo:", width=350)
    entry_etapa = criar_label_entry(win, "Etapa:", width=350)
    entry_prazo = criar_label_entry(win, "Prazo (DD-MM-AAAA):", width=350)

    def salvar():
        nome = entry_nome.get().strip()
        cargo = entry_cargo.get().strip()
        etapa = entry_etapa.get().strip()
        prazo = entry_prazo.get().strip()
        
        # Validações
        valido, mensagem = validar_nome(nome, min_length=2, max_length=100)
        if not valido:
            messagebox.showwarning("Aviso", f"Nome: {mensagem}")
            return
        
        if prazo and not validar_data(prazo):
            messagebox.showwarning("Aviso", "Data inválida! Use o formato DD-MM-AAAA ou DD/MM/AAAA")
            return

        pessoa = {
            "nome": nome,
            "cargo": cargo,
            "etapa": etapa,
            "prazo": prazo
        }

        projeto["pessoas"].append(pessoa)
        dados = carregar_projetos()
        for i, p in enumerate(dados["projetos"]):
            if p["id"] == id_projeto:
                dados["projetos"][i] = projeto
                break
        
        if salvar_projetos(dados):
            messagebox.showinfo("Sucesso", "Participante adicionado!")
            win.destroy()
            if callback:
                callback()

    # Botões
    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    ctk.CTkButton(
        btn_frame, 
        text="Salvar Participante", 
        command=salvar,
        width=150
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame, 
        text="Cancelar", 
        command=win.destroy,
        width=150,
        fg_color="gray30",
        hover_color="gray20"
    ).pack(side="left", padx=5)

def editar_participante(janela: ctk.CTk, id_projeto: int, callback: Optional[Callable] = None) -> None:
    """
    Abre janela para editar um participante existente.
    
    Args:
        janela: Janela principal
        id_projeto: ID do projeto
        callback: Função a ser chamada após salvar
    """
    if id_projeto is None:
        messagebox.showwarning("Aviso", "Selecione um projeto primeiro.")
        return
    
    projeto = carregar_projeto_por_id(id_projeto)
    if not projeto or not projeto.get("pessoas"):
        messagebox.showwarning("Aviso", "Nenhum participante encontrado neste projeto.")
        return

    nomes = [p["nome"] for p in projeto["pessoas"]]
    
    # Janela de seleção
    sel_win = ctk.CTkToplevel(janela)
    sel_win.title("Selecionar Participante")
    sel_win.geometry("400x300")
    sel_win.grab_set()
    
    ctk.CTkLabel(
        sel_win, 
        text="Selecione um Participante", 
        font=("Roboto", 16, "bold")
    ).pack(pady=15)
    
    selected_name = ctk.StringVar()
    
    for nome in nomes:
        ctk.CTkRadioButton(
            sel_win, 
            text=nome, 
            variable=selected_name, 
            value=nome
        ).pack(pady=5)
    
    def continuar():
        nome_escolhido = selected_name.get()
        if not nome_escolhido:
            messagebox.showwarning("Aviso", "Selecione um participante.")
            return
        
        sel_win.destroy()
        abrir_edicao(nome_escolhido)
    
    ctk.CTkButton(sel_win, text="Continuar", command=continuar).pack(pady=20)
    
    def abrir_edicao(nome_escolhido):
        participante = next((p for p in projeto["pessoas"] if p["nome"] == nome_escolhido), None)
        if not participante:
            messagebox.showerror("Erro", "Participante não encontrado.")
            return

        win = ctk.CTkToplevel(janela)
        win.title("Editar Participante")
        win.geometry("450x450")
        win.grab_set()
        
        ctk.CTkLabel(
            win, 
            text="Editar Participante", 
            font=("Roboto", 18, "bold")
        ).pack(pady=15)

        entry_nome = criar_label_entry(win, "Nome:", width=350)
        entry_nome.insert(0, participante.get("nome", ""))
        
        entry_cargo = criar_label_entry(win, "Cargo:", width=350)
        entry_cargo.insert(0, participante.get("cargo", ""))
        
        entry_etapa = criar_label_entry(win, "Etapa:", width=350)
        entry_etapa.insert(0, participante.get("etapa", ""))
        
        entry_prazo = criar_label_entry(win, "Prazo (DD-MM-AAAA):", width=350)
        entry_prazo.insert(0, participante.get("prazo", ""))

        def salvar():
            nome = entry_nome.get().strip()
            cargo = entry_cargo.get().strip()
            etapa = entry_etapa.get().strip()
            prazo = entry_prazo.get().strip()
            
            # Validações
            valido, mensagem = validar_nome(nome, min_length=2, max_length=100)
            if not valido:
                messagebox.showwarning("Aviso", f"Nome: {mensagem}")
                return
            
            if prazo and not validar_data(prazo):
                messagebox.showwarning("Aviso", "Data inválida! Use o formato DD-MM-AAAA ou DD/MM/AAAA")
                return
            
            participante["nome"] = nome
            participante["cargo"] = cargo
            participante["etapa"] = etapa
            participante["prazo"] = prazo
            
            dados = carregar_projetos()
            for i, p in enumerate(dados["projetos"]):
                if p["id"] == id_projeto:
                    dados["projetos"][i] = projeto
                    break
            
            if salvar_projetos(dados):
                messagebox.showinfo("Sucesso", "Participante atualizado!")
                win.destroy()
                if callback:
                    callback()

        # Botões
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame, 
            text="Salvar Alterações", 
            command=salvar,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Cancelar", 
            command=win.destroy,
            width=150,
            fg_color="gray30",
            hover_color="gray20"
        ).pack(side="left", padx=5)

def remover_participante(janela: ctk.CTk, id_projeto: int, callback: Optional[Callable] = None) -> None:
    """
    Remove um participante do projeto após confirmação.
    
    Args:
        janela: Janela principal
        id_projeto: ID do projeto
        callback: Função a ser chamada após remover
    """
    if id_projeto is None:
        messagebox.showwarning("Aviso", "Selecione um projeto primeiro.")
        return
    
    projeto = carregar_projeto_por_id(id_projeto)
    if not projeto or not projeto.get("pessoas"):
        messagebox.showwarning("Aviso", "Nenhum participante para remover.")
        return

    nomes = [p["nome"] for p in projeto["pessoas"]]
    
    # Janela de seleção
    sel_win = ctk.CTkToplevel(janela)
    sel_win.title("Remover Participante")
    sel_win.geometry("400x300")
    sel_win.grab_set()
    
    ctk.CTkLabel(
        sel_win, 
        text="Selecione o Participante para Remover", 
        font=("Roboto", 16, "bold")
    ).pack(pady=15)
    
    selected_name = ctk.StringVar()
    
    for nome in nomes:
        ctk.CTkRadioButton(
            sel_win, 
            text=nome, 
            variable=selected_name, 
            value=nome
        ).pack(pady=5)
    
    def remover():
        nome_escolhido = selected_name.get()
        if not nome_escolhido:
            messagebox.showwarning("Aviso", "Selecione um participante.")
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover '{nome_escolhido}'?"
        )
        
        if not resposta:
            return
        
        projeto["pessoas"] = [p for p in projeto["pessoas"] if p["nome"] != nome_escolhido]
        dados = carregar_projetos()
        for i, p in enumerate(dados["projetos"]):
            if p["id"] == id_projeto:
                dados["projetos"][i] = projeto
                break
        
        if salvar_projetos(dados):
            messagebox.showinfo("Sucesso", "Participante removido.")
            sel_win.destroy()
            if callback:
                callback()
    
    btn_frame = ctk.CTkFrame(sel_win, fg_color="transparent")
    btn_frame.pack(pady=20)
    
    ctk.CTkButton(
        btn_frame, 
        text="Remover", 
        command=remover,
        width=120,
        fg_color="darkred",
        hover_color="red"
    ).pack(side="left", padx=5)
    
    ctk.CTkButton(
        btn_frame, 
        text="Cancelar", 
        command=sel_win.destroy,
        width=120,
        fg_color="gray30",
        hover_color="gray20"
    ).pack(side="left", padx=5)
