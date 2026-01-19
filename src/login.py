"""
Tela de login moderna com ttkbootstrap.
Design profissional inspirado em aplicações modernas.
"""
import os
import sys
import subprocess
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import Image, ImageTk

# Importar configurações e utilitários
try:
    from config import LOGIN_TITLE, SRC_DIR
    from utils import hash_senha, verificar_senha, validar_nome
    import database as db
    USE_SQLITE = True
except ImportError:
    LOGIN_TITLE = "Login - ProjetoX"
    SRC_DIR = os.path.dirname(__file__)
    USE_SQLITE = False
    
    import hashlib
    def hash_senha(senha: str) -> str:
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()
    
    def verificar_senha(senha: str, hash_armazenado: str) -> bool:
        return hash_senha(senha) == hash_armazenado
    
    def validar_nome(nome: str, min_length: int = 2, max_length: int = 100) -> tuple:
        if not nome or not nome.strip():
            return False, "O nome não pode estar vazio."
        nome = nome.strip()
        if len(nome) < min_length:
            return False, f"O nome deve ter pelo menos {min_length} caracteres."
        if len(nome) > max_length:
            return False, f"O nome deve ter no máximo {max_length} caracteres."
        return True, ""


class ModernLoginApp(ttk.Window):
    """Aplicação moderna de login com design profissional."""
    
    def __init__(self):
        # Tema flatly - mais corporativo e profissional
        super().__init__(themename="flatly")
        
        self.title("ProjetoX - Sistema de Gestão de Projetos")
        self.geometry("1100x700")
        self.resizable(False, False)
        
        # Centralizar janela
        self.center_window()
        
        # Aplicar estilos customizados
        self.setup_styles()
        
        self.setup_ui()
        
    def center_window(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        width = 1100
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Define estilos customizados para um look premium."""
        style = ttk.Style()
        
        # Estilo para a coluna de branding (azul escuro corporativo)
        style.configure('Brand.TFrame', background='#2c3e50')
        
        # Estilo para a coluna de login (branco limpo)
        style.configure('Login.TFrame', background='#ffffff')
        
        # Estilos de texto para o branding
        style.configure('Header.TLabel', 
                       font=("Helvetica", 32, "bold"), 
                       foreground="white", 
                       background='#2c3e50')
        
        style.configure('SubHeader.TLabel', 
                       font=("Helvetica", 12), 
                       foreground="#bdc3c7", 
                       background='#2c3e50')
    
    def setup_ui(self):
        """Configura a interface moderna."""
        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES)
        
        # --- COLUNA ESQUERDA (BRANDING) ---
        left_col = ttk.Frame(main_container, style='Brand.TFrame', width=450)
        left_col.pack(side=LEFT, fill=BOTH)
        left_col.pack_propagate(False)
        
        self.setup_branding(left_col)
        
        # --- COLUNA DIREITA (LOGIN) ---
        right_col = ttk.Frame(main_container, style='Login.TFrame')
        right_col.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        self.setup_login_form(right_col)
    
    def setup_branding(self, parent):
        """Configura a área de branding/informações."""
        # Container centralizado
        brand_container = ttk.Frame(parent, style='Brand.TFrame')
        brand_container.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Logo/Ícone
        logo_label = ttk.Label(
            brand_container,
            text="📊",
            font=("Segoe UI", 90),
            style='Header.TLabel'
        )
        logo_label.pack(pady=(0, 20))
        
        # Título
        title = ttk.Label(
            brand_container,
            text="PROJETOX",
            style='Header.TLabel'
        )
        title.pack(pady=(0, 15))
        
        # Subtítulo
        subtitle = ttk.Label(
            brand_container,
            text="Gestão Integrada de Projetos",
            style='SubHeader.TLabel'
        )
        subtitle.pack(pady=(0, 40))
        
        # Card de informações
        info_card = ttk.Frame(brand_container, bootstyle="light")
        info_card.pack(fill=X, padx=30, pady=20)
        
        features = [
            "Controle completo de projetos",
            "Gestão de equipes e etapas",
            "Relatórios profissionais"
        ]
        
        for feat in features:
            ttk.Label(
                info_card,
                text=f"  • {feat}",
                font=("Helvetica", 11),
                bootstyle="inverse-light"
            ).pack(anchor=W, pady=6, padx=15)
    
    def setup_login_form(self, parent):
        """Configura o formulário de login."""
        # Container do formulário centralizado
        login_form = ttk.Frame(parent, style='Login.TFrame')
        login_form.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.7)
        
        # Cabeçalho do formulário
        ttk.Label(
            login_form,
            text="Login",
            font=("Helvetica", 26, "bold"),
            foreground="#2c3e50",
            background='white'
        ).pack(anchor=W, pady=(0, 5))
        
        ttk.Label(
            login_form,
            text="Acesse sua conta para gerenciar projetos.",
            font=("Helvetica", 11),
            foreground="#7f8c8d",
            background='white'
        ).pack(anchor=W, pady=(0, 35))
        
        # Campo de usuário
        self.create_input(login_form, "NOME DE USUÁRIO", "entry_usuario")
        
        # Campo de senha
        self.create_input(login_form, "SENHA", "entry_senha", show="●")
        
        # Botão de Login
        btn_login = ttk.Button(
            login_form,
            text="ENTRAR NO SISTEMA",
            command=self.login,
            bootstyle="primary",
            cursor="hand2"
        )
        btn_login.pack(fill=X, ipady=14, pady=(15, 20))
        
        # Bind Enter
        self.entry_senha.bind("<Return>", lambda e: self.login())
        
        # Divisor
        sep_frame = ttk.Frame(login_form, style='Login.TFrame')
        sep_frame.pack(fill=X, pady=15)
        
        ttk.Separator(sep_frame).pack(side=LEFT, fill=X, expand=YES)
        ttk.Label(
            sep_frame,
            text=" ou ",
            background="white",
            foreground="#bdc3c7",
            font=("Helvetica", 10)
        ).pack(side=LEFT)
        ttk.Separator(sep_frame).pack(side=LEFT, fill=X, expand=YES)
        
        # Botão de Cadastro
        btn_cadastro = ttk.Button(
            login_form,
            text="Solicitar Acesso",
            command=self.cadastro,
            bootstyle="outline-primary",
            cursor="hand2"
        )
        btn_cadastro.pack(fill=X, ipady=14, pady=10)
        
        # Versão
        version_label = ttk.Label(
            login_form,
            text="v2.1 - SQLite Edition",
            font=("Helvetica", 9),
            foreground="#95a5a6",
            background='white'
        )
        version_label.pack(side=BOTTOM, pady=(30, 0))
    
    def create_input(self, parent, label_text, var_name, show=""):
        """Helper para criar campos de entrada padronizados."""
        ttk.Label(
            parent,
            text=label_text,
            font=("Helvetica", 9, "bold"),
            foreground="#34495e",
            background="white"
        ).pack(anchor=W, pady=(20, 6))
        
        entry = ttk.Entry(
            parent,
            font=("Helvetica", 12),
            show=show,
            bootstyle="secondary"
        )
        entry.pack(fill=X, ipady=10)
        setattr(self, var_name, entry)
        
        # Focus no primeiro campo
        if var_name == "entry_usuario":
            entry.focus()
    
    def cadastro(self):
        """Realiza o cadastro de um novo usuário."""
        nome = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        
        # Validações
        valido, mensagem = validar_nome(nome, min_length=3, max_length=50)
        if not valido:
            messagebox.showwarning("Aviso", mensagem, parent=self)
            return
        
        if not senha or len(senha) < 4:
            messagebox.showwarning("Aviso", "A senha deve ter pelo menos 4 caracteres.", parent=self)
            return
        
        # Verificar se usuário já existe
        if USE_SQLITE:
            usuario_existente = db.buscar_usuario(nome)
            if usuario_existente:
                messagebox.showinfo("Aviso", "Usuário já existe. Faça login.", parent=self)
                return
            
            try:
                db.adicionar_usuario(nome, hash_senha(senha))
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!", parent=self)
                self.entry_usuario.delete(0, 'end')
                self.entry_senha.delete(0, 'end')
                self.entry_usuario.focus()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível cadastrar o usuário: {e}", parent=self)
        else:
            messagebox.showerror("Erro", "Sistema de banco de dados não disponível.", parent=self)
    
    def login(self):
        """Realiza o login do usuário."""
        nome = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        
        if not nome or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos.", parent=self)
            return
        
        if USE_SQLITE:
            try:
                db.inicializar_database()
                usuario = db.buscar_usuario(nome)
                
                if not usuario:
                    messagebox.showerror("Erro", "Usuário não encontrado.", parent=self)
                    self.entry_senha.delete(0, 'end')
                    return
                
                senha_armazenada = usuario['senha_hash']
                
                if verificar_senha(senha, senha_armazenada):
                    messagebox.showinfo("Sucesso", f"Bem-vindo, {nome}!", parent=self)
                    self.destroy()
                    self.abrir_dashboard()
                else:
                    messagebox.showerror("Erro", "Senha incorreta.", parent=self)
                    self.entry_senha.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao fazer login: {e}", parent=self)
        else:
            messagebox.showerror("Erro", "Sistema de banco de dados não disponível.", parent=self)
    
    def abrir_dashboard(self):
        """Abre a tela principal do sistema."""
        caminho_dashboard = os.path.join(SRC_DIR, "tela_inicial.py")
        
        if os.path.exists(caminho_dashboard):
            try:
                subprocess.Popen([sys.executable, caminho_dashboard])
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir o dashboard: {e}")
        else:
            messagebox.showerror("Erro", f"Arquivo 'tela_inicial.py' não encontrado em:\n{caminho_dashboard}")


if __name__ == "__main__":
    app = ModernLoginApp()
    app.mainloop()
