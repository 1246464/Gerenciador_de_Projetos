"""
Dashboard moderno do ProjetoX com ttkbootstrap.
Interface profissional para gerenciamento de projetos.
"""
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
try:
    from ttkbootstrap.tableview import Tableview
except ImportError:
    from ttkbootstrap.widgets.table import Tableview
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importações locais
try:
    from config import DATA_DIR
    import database as db
    USE_SQLITE = True
except ImportError:
    USE_SQLITE = False
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


class ModernDashboard(ttk.Window):
    """Dashboard moderno para gestão de projetos."""
    
    def __init__(self):
        super().__init__(themename="darkly")
        
        self.title("ProjetoX - Dashboard")
        self.geometry("1400x800")
        self.state('zoomed')  # Maximizar
        
        self.current_page = "dashboard"
        self.projetos = []
        
        self.setup_ui()
        self.carregar_dados()
        
    def setup_ui(self):
        """Configura a interface do dashboard."""
        # Container principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=YES)
        
        # Sidebar
        self.sidebar = ttk.Frame(main_container, bootstyle="dark", width=250)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)
        
        self.setup_sidebar()
        
        # Content Area
        self.content_area = ttk.Frame(main_container)
        self.content_area.pack(side=RIGHT, fill=BOTH, expand=YES, padx=20, pady=20)
        
        self.show_dashboard()
    
    def setup_sidebar(self):
        """Configura a barra lateral de navegação."""
        # Logo e título
        logo_frame = ttk.Frame(self.sidebar, bootstyle="dark")
        logo_frame.pack(fill=X, pady=20, padx=15)
        
        logo = ttk.Label(
            logo_frame,
            text="📊",
            font=("Segoe UI", 32),
            bootstyle="inverse-dark"
        )
        logo.pack()
        
        title = ttk.Label(
            logo_frame,
            text="ProjetoX",
            font=("Segoe UI", 18, "bold"),
            bootstyle="inverse-dark"
        )
        title.pack()
        
        ttk.Separator(self.sidebar, bootstyle="secondary").pack(fill=X, padx=10, pady=15)
        
        # Menu de navegação
        menu_items = [
            ("🏠 Dashboard", self.show_dashboard, "dashboard"),
            ("📁 Projetos", self.show_projetos, "projetos"),
            ("➕ Novo Projeto", self.novo_projeto, "novo"),
            ("📊 Relatórios", self.show_relatorios, "relatorios"),
        ]
        
        for text, command, page_id in menu_items:
            btn = ttk.Button(
                self.sidebar,
                text=text,
                command=lambda c=command, p=page_id: self.navigate(c, p),
                bootstyle="dark",
                width=25
            )
            btn.pack(fill=X, padx=10, pady=5)
        
        # Botão de sair no fim
        ttk.Separator(self.sidebar, bootstyle="secondary").pack(fill=X, padx=10, pady=15, side=BOTTOM)
        
        btn_sair = ttk.Button(
            self.sidebar,
            text="🚪 Sair",
            command=self.sair,
            bootstyle="danger",
            width=25
        )
        btn_sair.pack(fill=X, padx=10, pady=10, side=BOTTOM)
    
    def navigate(self, command, page_id):
        """Navega para uma página."""
        self.current_page = page_id
        command()
    
    def clear_content(self):
        """Limpa a área de conteúdo."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Exibe o dashboard principal com gráficos profissionais."""
        self.clear_content()
        
        # Recarregar dados para garantir que estejam atualizados
        self.carregar_dados()
        
        # Cabeçalho com título grande
        header = ttk.Frame(self.content_area, bootstyle="primary")
        header.pack(fill=X, pady=(0, 5))
        
        header_content = ttk.Frame(header)
        header_content.pack(fill=X, padx=20, pady=15)
        
        title = ttk.Label(
            header_content,
            text="DASHBOARD DE CONTROLE DE PROJETOS",
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-primary"
        )
        title.pack(side=LEFT)
        
        date_label = ttk.Label(
            header_content,
            text=datetime.now().strftime("%d/%m/%Y - %H:%M"),
            font=("Segoe UI", 11),
            bootstyle="inverse-secondary"
        )
        date_label.pack(side=RIGHT, pady=5)
        
        # Container principal com scroll
        main_container = ttk.Frame(self.content_area)
        main_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        if not self.projetos:
            # Mensagem quando não há projetos
            empty_frame = ttk.Frame(main_container, bootstyle="light", padding=60)
            empty_frame.pack(fill=BOTH, expand=YES)
            
            ttk.Label(
                empty_frame,
                text="📊",
                font=("Segoe UI", 64),
                bootstyle="secondary"
            ).pack(pady=(0, 20))
            
            ttk.Label(
                empty_frame,
                text="Nenhum projeto cadastrado",
                font=("Segoe UI", 20, "bold"),
                bootstyle="secondary"
            ).pack()
            
            ttk.Label(
                empty_frame,
                text="Comece criando seu primeiro projeto para visualizar estatísticas",
                font=("Segoe UI", 13),
                bootstyle="secondary"
            ).pack(pady=(10, 30))
            
            ttk.Button(
                empty_frame,
                text="➕ Criar Primeiro Projeto",
                command=self.novo_projeto,
                bootstyle="success",
                width=30
            ).pack()
            return
        
        # Linha 1: Cards de estatísticas (4 cards em linha)
        stats_row = ttk.Frame(main_container)
        stats_row.pack(fill=X, pady=(0, 15))
        
        total_projetos = len(self.projetos)
        projetos_ativos = sum(1 for p in self.projetos if p.get('status', 'ativo') == 'ativo')
        projetos_concluidos = sum(1 for p in self.projetos if p.get('status', 'ativo') == 'concluído')
        total_etapas = sum(len(p.get('etapas', [])) for p in self.projetos)
        
        self.create_modern_stat_card(stats_row, "Total de Projetos", total_projetos, "📁", "info", 0)
        self.create_modern_stat_card(stats_row, "Projetos Ativos", projetos_ativos, "✓", "success", 1)
        self.create_modern_stat_card(stats_row, "Concluídos", projetos_concluidos, "🎯", "warning", 2)
        self.create_modern_stat_card(stats_row, "Total de Etapas", total_etapas, "📋", "primary", 3)
        
        # Linha 2: Dois gráficos lado a lado
        row2 = ttk.Frame(main_container)
        row2.pack(fill=BOTH, expand=YES, pady=(0, 10))
        row2.grid_rowconfigure(0, weight=1)
        
        # Gráfico 1: Evolução de projetos por mês (Linha)
        self.create_projects_evolution_chart(row2)
        
        # Gráfico 2: Projetos por Cliente (Barras horizontais)
        self.create_projects_by_client_chart(row2)
        
        # Linha 3: Dois gráficos lado a lado (mais altura)
        row3 = ttk.Frame(main_container)
        row3.pack(fill=BOTH, expand=YES)
        row3.grid_rowconfigure(0, weight=1)
        
        # Gráfico 3: Orçamento por Projeto (Barras verticais)
        self.create_budget_by_project_chart(row3)
        
        # Gráfico 4: Progresso de Projetos (Barras horizontais)
        self.create_project_progress_chart(row3)
    
    def create_modern_stat_card(self, parent, title, value, icon, style, column):
        """Cria um card de estatística moderno."""
        card = ttk.Frame(parent, bootstyle=style, padding=10)
        card.grid(row=0, column=column, padx=5, sticky="nsew")
        parent.columnconfigure(column, weight=1)
        
        # Container interno
        inner = ttk.Frame(card, bootstyle=style)
        inner.pack(fill=BOTH, expand=YES)
        
        # Ícone no topo esquerdo
        ttk.Label(
            inner,
            text=icon,
            font=("Segoe UI", 32),
            bootstyle=f"inverse-{style}"
        ).pack(side=LEFT, padx=(5, 12))
        
        # Valor e título do lado direito
        right_frame = ttk.Frame(inner, bootstyle=style)
        right_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        
        ttk.Label(
            right_frame,
            text=str(value),
            font=("Segoe UI", 30, "bold"),
            bootstyle=f"inverse-{style}"
        ).pack(anchor=W)
        
        ttk.Label(
            right_frame,
            text=title,
            font=("Segoe UI", 11),
            bootstyle=f"inverse-{style}"
        ).pack(anchor=W, pady=(2, 0))
    
    def create_projects_evolution_chart(self, parent):
        """Gráfico de linha: Evolução de projetos ao longo dos meses."""
        chart_frame = ttk.Labelframe(parent, text="Evolução de Projetos por Mês", bootstyle="primary")
        chart_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        
        fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='#222')
        ax.set_facecolor('#222')
        
        # Agrupar projetos por mês (simulado com os últimos 12 meses)
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        # Simular distribuição (em produção, use dados reais de created_at)
        valores = []
        base = len(self.projetos) // 12
        for i in range(12):
            import random
            valores.append(max(0, base + random.randint(-2, 3)))
        
        # Linha com marcadores
        line = ax.plot(meses, valores, marker='o', linewidth=3, markersize=8, color='#3498db', label='Projetos Criados')
        ax.fill_between(range(len(meses)), valores, alpha=0.3, color='#3498db')
        
        # Adicionar valores nos pontos
        for i, (mes, val) in enumerate(zip(meses, valores)):
            ax.text(i, val + 0.5, str(val), ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
        
        ax.set_ylabel('Quantidade', color='white', fontsize=11)
        ax.set_xlabel('Mês', color='white', fontsize=11)
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.1, linestyle='--')
        ax.legend(loc='upper left', framealpha=0.8)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    def create_projects_by_client_chart(self, parent):
        """Gráfico de barras horizontais: Projetos por Cliente."""
        chart_frame = ttk.Labelframe(parent, text="Projetos por Cliente", bootstyle="success")
        chart_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(5, 0))
        
        # Contar projetos por cliente
        clientes = {}
        for p in self.projetos:
            cliente = p.get('cliente', 'Sem cliente')
            clientes[cliente] = clientes.get(cliente, 0) + 1
        
        if not clientes:
            ttk.Label(chart_frame, text="Sem dados", bootstyle="secondary").pack(expand=YES)
            return
        
        # Top 8 clientes
        top_clientes = sorted(clientes.items(), key=lambda x: x[1], reverse=True)[:8]
        nomes = [c[0][:20] + '...' if len(c[0]) > 20 else c[0] for c in top_clientes]
        valores = [c[1] for c in top_clientes]
        
        fig, ax = plt.subplots(figsize=(7, 4.5), facecolor='#222')
        ax.set_facecolor('#222')
        
        bars = ax.barh(nomes, valores, color='#27ae60', height=0.6)
        
        # Adicionar valores nas barras
        for bar, val in zip(bars, valores):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{int(val)}', ha='left', va='center', color='white', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Número de Projetos', color='white', fontsize=11)
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.1, linestyle='--')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    def create_budget_by_project_chart(self, parent):
        """Gráfico de barras verticais: Orçamento por Projeto."""
        chart_frame = ttk.Labelframe(parent, text="Orçamento por Projeto", bootstyle="warning")
        chart_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        
        # Top 10 projetos por orçamento
        projetos_com_orcamento = [(p['nome'], p.get('orcamento', 0)) for p in self.projetos]
        projetos_com_orcamento.sort(key=lambda x: x[1], reverse=True)
        top_10 = projetos_com_orcamento[:10]
        
        if not any(x[1] > 0 for x in top_10):
            ttk.Label(chart_frame, text="Nenhum orçamento cadastrado", bootstyle="secondary", 
                     font=("Segoe UI", 11)).pack(expand=YES)
            return
        
        nomes = [p[0][:12] + '...' if len(p[0]) > 12 else p[0] for p in top_10]
        valores = [p[1] for p in top_10]
        
        fig, ax = plt.subplots(figsize=(7, 6), facecolor='#222')
        ax.set_facecolor('#222')
        
        bars = ax.bar(range(len(nomes)), valores, color='#f39c12', width=0.6)
        
        # Adicionar valores em cima das barras
        for bar, val in zip(bars, valores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + max(valores)*0.02,
                   f'R$ {val:,.0f}', ha='center', va='bottom', color='white', fontsize=8, fontweight='bold')
        
        ax.set_ylabel('Orçamento (R$)', color='white', fontsize=11)
        ax.set_xticks(range(len(nomes)))
        ax.set_xticklabels(nomes, rotation=45, ha='right')
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.1, linestyle='--')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    def create_project_progress_chart(self, parent):
        """Gráfico de barras horizontais: Progresso de conclusão dos projetos."""
        chart_frame = ttk.Labelframe(parent, text="Progresso de Conclusão (%)", bootstyle="info")
        chart_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(5, 0))
        
        # Calcular progresso (top 10)
        projetos_progresso = []
        for p in self.projetos:
            etapas = p.get('etapas', [])
            if etapas:
                concluidas = sum(1 for e in etapas if e.get('status') == 'concluído')
                progresso = (concluidas / len(etapas)) * 100
            else:
                progresso = 0
            projetos_progresso.append((p['nome'], progresso))
        
        # Ordenar por progresso (menores primeiro para mostrar o que precisa atenção)
        projetos_progresso.sort(key=lambda x: x[1])
        top_10 = projetos_progresso[:10]
        
        nomes = [p[0][:20] + '...' if len(p[0]) > 20 else p[0] for p in top_10]
        valores = [p[1] for p in top_10]
        
        fig, ax = plt.subplots(figsize=(7, 6), facecolor='#222')
        ax.set_facecolor('#222')
        
        # Cores gradientes baseadas no progresso
        cores = []
        for v in valores:
            if v >= 80:
                cores.append('#27ae60')  # Verde
            elif v >= 50:
                cores.append('#f39c12')  # Laranja
            else:
                cores.append('#e74c3c')  # Vermelho
        
        bars = ax.barh(nomes, valores, color=cores, height=0.6)
        
        # Adicionar valores nas barras
        for bar, val in zip(bars, valores):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2, 
                   f'{val:.0f}%', ha='left', va='center', color='white', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Progresso (%)', color='white', fontsize=11)
        ax.set_xlim(0, 105)
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.1, linestyle='--')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    def create_stat_card(self, parent, title, value, style, column):
        """Cria um card de estatística."""
        card = ttk.Frame(parent, bootstyle=style)
        card.grid(row=0, column=column, padx=10, sticky="ew")
        parent.columnconfigure(column, weight=1)
        
        value_label = ttk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 36, "bold"),
            bootstyle=f"inverse-{style}"
        )
        value_label.pack(pady=(20, 5))
        
        title_label = ttk.Label(
            card,
            text=title,
            font=("Segoe UI", 12),
            bootstyle=f"inverse-{style}"
        )
        title_label.pack(pady=(0, 20))
    
    def create_progress_chart(self, parent):
        """Cria gráfico de progresso dos projetos."""
        chart_frame = ttk.Labelframe(
            parent,
            text="📊 Progresso dos Projetos",
            bootstyle="info"
        )
        chart_frame.pack(fill=BOTH, expand=YES, pady=10, padx=5)
        
        # Criar figura matplotlib
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='#222')
        ax.set_facecolor('#222')
        
        nomes = [p['nome'][:20] + '...' if len(p['nome']) > 20 else p['nome'] for p in self.projetos[:10]]
        progressos = []
        
        for p in self.projetos[:10]:
            etapas = p.get('etapas', [])
            if etapas:
                concluidas = sum(1 for e in etapas if e.get('status') == 'concluído')
                progresso = (concluidas / len(etapas)) * 100
            else:
                progresso = 0
            progressos.append(progresso)
        
        bars = ax.barh(nomes, progressos, color='#375a7f')
        ax.set_xlabel('Progresso (%)', color='white')
        ax.set_xlim(0, 100)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Adicionar valores nas barras
        for bar, progresso in zip(bars, progressos):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2, 
                   f'{progresso:.0f}%', ha='left', va='center', color='white')
        
        plt.tight_layout()
        
        # Incorporar no tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    def show_projetos(self):
        """Exibe a lista de projetos."""
        self.clear_content()
        
        # Cabeçalho
        header = ttk.Frame(self.content_area)
        header.pack(fill=X, pady=(0, 20))
        
        title = ttk.Label(
            header,
            text="Gerenciar Projetos",
            font=("Segoe UI", 32, "bold"),
            bootstyle="inverse"
        )
        title.pack(side=LEFT)
        
        btn_novo = ttk.Button(
            header,
            text="➕ Novo Projeto",
            command=self.novo_projeto,
            bootstyle="success",
        )
        btn_novo.pack(side=RIGHT)
        
        # Tabela de projetos
        if not self.projetos:
            empty_label = ttk.Label(
                self.content_area,
                text="Nenhum projeto encontrado.\nClique em 'Novo Projeto' para começar!",
                font=("Segoe UI", 14),
                bootstyle="secondary",
                justify=CENTER
            )
            empty_label.pack(expand=YES)
            return
        
        # Frame da tabela
        table_frame = ttk.Frame(self.content_area)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Criar dados para tabela
        columns = ["Nome", "Cliente", "Prazo", "Etapas", "Progresso", "Status"]
        rows = []
        
        for p in self.projetos:
            etapas = p.get('etapas', [])
            total_etapas = len(etapas)
            
            if total_etapas > 0:
                concluidas = sum(1 for e in etapas if e.get('status') == 'concluído')
                progresso = f"{(concluidas/total_etapas)*100:.0f}%"
            else:
                progresso = "0%"
            
            rows.append([
                p['nome'],
                p.get('cliente', 'N/A'),
                p.get('prazo', 'N/A'),
                str(total_etapas),
                progresso,
                p.get('status', 'ativo').upper()
            ])
        
        # Tableview
        table = Tableview(
            table_frame,
            coldata=columns,
            rowdata=rows,
            paginated=True,
            searchable=True,
            bootstyle="info",
            pagesize=15,
            height=20
        )
        table.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Bind duplo clique
        table.view.bind("<Double-Button-1>", self.on_projeto_double_click)
        
        # Frame de ações
        actions_frame = ttk.Frame(self.content_area)
        actions_frame.pack(fill=X, pady=(10, 0))
        
        btn_editar = ttk.Button(
            actions_frame,
            text="✏️ Editar Selecionado",
            command=lambda: self.editar_projeto_selecionado(table),
            bootstyle="primary"
        )
        btn_editar.pack(side=LEFT, padx=5)
        
        btn_excluir = ttk.Button(
            actions_frame,
            text="🗑️ Excluir Selecionado",
            command=lambda: self.excluir_projeto_selecionado(table),
            bootstyle="danger"
        )
        btn_excluir.pack(side=LEFT, padx=5)
    
    def on_projeto_double_click(self, event):
        """Handler para duplo clique em projeto."""
        # Pegar item selecionado
        widget = event.widget
        selection = widget.selection()
        if selection:
            item = widget.item(selection[0])
            nome_projeto = item['values'][0]
            
            # Buscar projeto completo
            projeto = next((p for p in self.projetos if p['nome'] == nome_projeto), None)
            if projeto:
                self.visualizar_projeto_detalhado(projeto)
    
    def editar_projeto_selecionado(self, table):
        """Edita o projeto selecionado."""
        selected = table.view.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um projeto para editar.")
            return
        
        # Pegar nome do projeto
        item = table.view.item(selected[0])
        nome_projeto = item['values'][0]
        
        # Buscar projeto completo
        projeto = next((p for p in self.projetos if p['nome'] == nome_projeto), None)
        if projeto:
            self.abrir_editor_projeto(projeto)
    
    def excluir_projeto_selecionado(self, table):
        """Exclui o projeto selecionado."""
        selected = table.view.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um projeto para excluir.")
            return
        
        # Pegar nome do projeto
        item = table.view.item(selected[0])
        nome_projeto = item['values'][0]
        
        confirma = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o projeto '{nome_projeto}'?\n\nEsta ação não pode ser desfeita e removerá:\n• Todas as etapas\n• Todos os participantes\n• Todos os dados relacionados"
        )
        
        if confirma:
            try:
                if USE_SQLITE:
                    # Buscar ID do projeto
                    projeto = next((p for p in self.projetos if p['nome'] == nome_projeto), None)
                    if projeto:
                        db.excluir_projeto(projeto['id'])
                        messagebox.showinfo("Sucesso", "Projeto excluído com sucesso!")
                        self.carregar_dados()
                        self.show_projetos()
                else:
                    messagebox.showerror("Erro", "Exclusão requer SQLite.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir projeto: {e}")
    
    def novo_projeto(self):
        """Abre janela para criar novo projeto."""
        self.clear_content()
        
        # Cabeçalho
        title = ttk.Label(
            self.content_area,
            text="Criar Novo Projeto",
            font=("Segoe UI", 32, "bold"),
            bootstyle="inverse"
        )
        title.pack(pady=(0, 30))
        
        # Formulário
        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(fill=BOTH, expand=YES, padx=100)
        
        # Nome do projeto
        ttk.Label(form_frame, text="Nome do Projeto *", font=("Segoe UI", 11)).pack(anchor=W, pady=(10, 5))
        entry_nome = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_nome.pack(fill=X, ipady=8)
        
        # Cliente
        ttk.Label(form_frame, text="Cliente *", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        entry_cliente = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_cliente.pack(fill=X, ipady=8)
        
        # Prazo
        ttk.Label(form_frame, text="Prazo (DD/MM/AAAA) *", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        entry_prazo = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_prazo.pack(fill=X, ipady=8)
        
        # Orçamento
        ttk.Label(form_frame, text="Orçamento (R$)", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        entry_orcamento = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_orcamento.pack(fill=X, ipady=8)
        
        # Descrição
        ttk.Label(form_frame, text="Descrição", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        text_descricao = ttk.Text(form_frame, height=5, font=("Segoe UI", 11))
        text_descricao.pack(fill=X)
        
        # Botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=X, pady=(30, 0))
        
        btn_salvar = ttk.Button(
            btn_frame,
            text="✓ Criar Projeto",
            command=lambda: self.salvar_novo_projeto(
                entry_nome.get(),
                entry_cliente.get(),
                entry_prazo.get(),
                entry_orcamento.get(),
                text_descricao.get("1.0", "end-1c")
            ),
            bootstyle="success",
            width=20
        )
        btn_salvar.pack(side=LEFT, padx=5)
        
        btn_cancelar = ttk.Button(
            btn_frame,
            text="✗ Cancelar",
            command=self.show_projetos,
            bootstyle="secondary",
            width=20
        )
        btn_cancelar.pack(side=LEFT, padx=5)
    
    def salvar_novo_projeto(self, nome, cliente, prazo, orcamento, descricao):
        """Salva um novo projeto."""
        # Validações básicas
        if not nome or not cliente or not prazo:
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios (*).")
            return
        
        try:
            # Adicionar ao banco
            if USE_SQLITE:
                db.adicionar_projeto(
                    nome=nome,
                    cliente=cliente,
                    prazo=prazo,
                    orcamento=float(orcamento) if orcamento else 0.0,
                    descricao=descricao if descricao else ""
                )
            else:
                messagebox.showerror("Erro", "Sistema configurado apenas para SQLite")
                return
            
            messagebox.showinfo("Sucesso", "Projeto criado com sucesso!")
            self.carregar_dados()
            self.show_projetos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar projeto: {e}")
    
    def show_relatorios(self):
        """Exibe a tela de relatórios."""
        self.clear_content()
        
        # Cabeçalho
        header = ttk.Frame(self.content_area)
        header.pack(fill=X, pady=(0, 20))
        
        title = ttk.Label(
            header,
            text="Relatórios e Gráficos",
            font=("Segoe UI", 32, "bold"),
            bootstyle="inverse"
        )
        title.pack(side=LEFT)
        
        # Botão de exportar CSV
        btn_csv = ttk.Button(
            header,
            text="📥 Exportar CSV",
            command=self.exportar_csv,
            bootstyle="info"
        )
        btn_csv.pack(side=RIGHT, padx=5)
        
        # Botão de gerar PDF
        btn_pdf = ttk.Button(
            header,
            text="📄 Gerar PDF",
            command=self.gerar_pdf,
            bootstyle="success"
        )
        btn_pdf.pack(side=RIGHT, padx=5)
        
        # Container de gráficos
        charts_container = ttk.Frame(self.content_area)
        charts_container.pack(fill=BOTH, expand=YES)
        
        # Primeira linha de gráficos
        row1 = ttk.Frame(charts_container)
        row1.pack(fill=BOTH, expand=YES, pady=(0, 10))
        
        # Gráfico de pizza - Status dos projetos
        self.create_status_pie_chart(row1)
        
        # Gráfico de barras - Projetos por mês
        self.create_projects_timeline_chart(row1)
        
        # Segunda linha de gráficos
        row2 = ttk.Frame(charts_container)
        row2.pack(fill=BOTH, expand=YES)
        
        # Gráfico de etapas
        self.create_etapas_chart(row2)
    
    def carregar_dados(self):
        """Carrega os dados dos projetos."""
        try:
            if USE_SQLITE:
                self.projetos = db.listar_projetos()
            else:
                self.projetos = []  # Fallback vazio - apenas SQLite suportado
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar projetos: {e}")
            self.projetos = []
    
    def visualizar_projeto_detalhado(self, projeto):
        """Visualiza um projeto em detalhes com possibilidade de gerenciar etapas."""
        # Criar janela modal
        dialog = ttk.Toplevel(self)
        dialog.title(f"Projeto: {projeto['nome']}")
        dialog.geometry("1000x700")
        dialog.resizable(True, True)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500)
        y = (dialog.winfo_screenheight() // 2) - (350)
        dialog.geometry(f"1000x700+{x}+{y}")
        
        # Header
        header = ttk.Frame(dialog, bootstyle="primary", padding=20)
        header.pack(fill=X)
        
        ttk.Label(
            header,
            text=projeto['nome'],
            font=("Segoe UI", 24, "bold"),
            bootstyle="inverse-primary"
        ).pack(anchor=W)
        
        ttk.Label(
            header,
            text=f"Cliente: {projeto.get('cliente', 'N/A')} | Prazo: {projeto.get('prazo', 'N/A')}",
            font=("Segoe UI", 12),
            bootstyle="inverse-secondary"
        ).pack(anchor=W, pady=(5, 0))
        
        # Notebook com abas
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        
        # Aba 1: Informações
        tab_info = ttk.Frame(notebook, padding=20)
        notebook.add(tab_info, text="📋 Informações")
        
        info_data = [
            ("Cliente:", projeto.get('cliente', 'N/A')),
            ("Prazo:", projeto.get('prazo', 'N/A')),
            ("Orçamento:", f"R$ {projeto.get('orcamento', 0):.2f}"),
            ("Status:", projeto.get('status', 'ativo').upper()),
            ("Descrição:", projeto.get('descricao', 'Sem descrição'))
        ]
        
        for label, value in info_data:
            frame = ttk.Frame(tab_info)
            frame.pack(fill=X, pady=10)
            
            ttk.Label(frame, text=label, font=("Segoe UI", 11, "bold")).pack(anchor=W)
            ttk.Label(frame, text=value, font=("Segoe UI", 11), bootstyle="secondary").pack(anchor=W, pady=(5, 0))
        
        # Aba 2: Etapas
        tab_etapas = ttk.Frame(notebook, padding=20)
        notebook.add(tab_etapas, text=f"📝 Etapas ({len(projeto.get('etapas', []))})")
        
        self.criar_gerenciador_etapas(tab_etapas, projeto)
        
        # Aba 3: Participantes
        tab_participantes = ttk.Frame(notebook, padding=20)
        notebook.add(tab_participantes, text=f"👥 Participantes ({len(projeto.get('participantes', []))})")
        
        self.criar_gerenciador_participantes(tab_participantes, projeto)
        
        # Botões de ação
        btn_frame = ttk.Frame(dialog, padding=10)
        btn_frame.pack(fill=X, side=BOTTOM)
        
        ttk.Button(
            btn_frame,
            text="✏️ Editar Projeto",
            command=lambda: [dialog.destroy(), self.abrir_editor_projeto(projeto)],
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Excluir Projeto",
            command=lambda: self.confirmar_excluir_projeto(projeto, dialog),
            bootstyle="danger"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="✗ Fechar",
            command=dialog.destroy,
            bootstyle="secondary"
        ).pack(side=RIGHT, padx=5)
    
    def criar_gerenciador_etapas(self, parent, projeto):
        """Cria o gerenciador de etapas."""
        # Botão adicionar
        btn_add = ttk.Button(
            parent,
            text="➕ Nova Etapa",
            command=lambda: self.adicionar_etapa_dialog(projeto),
            bootstyle="success"
        )
        btn_add.pack(anchor=W, pady=(0, 15))
        
        etapas = projeto.get('etapas', [])
        
        if not etapas:
            ttk.Label(
                parent,
                text="Nenhuma etapa cadastrada.\nClique em 'Nova Etapa' para adicionar.",
                bootstyle="secondary",
                justify=CENTER
            ).pack(expand=YES)
            return
        
        # Lista de etapas
        for idx, etapa in enumerate(etapas, 1):
            etapa_frame = ttk.Frame(parent, bootstyle="light", padding=15)
            etapa_frame.pack(fill=X, pady=5)
            
            # Cabeçalho da etapa
            header = ttk.Frame(etapa_frame)
            header.pack(fill=X)
            
            status_icon = "✅" if etapa.get('status') == 'concluído' else "🔄"
            ttk.Label(
                header,
                text=f"{status_icon} Etapa {idx}: {etapa.get('nome', 'Sem nome')}",
                font=("Segoe UI", 12, "bold")
            ).pack(side=LEFT)
            
            ttk.Label(
                header,
                text=etapa.get('status', 'em andamento').upper(),
                bootstyle="success" if etapa.get('status') == 'concluído' else "warning"
            ).pack(side=RIGHT)
            
            # Descrição
            if etapa.get('descricao'):
                ttk.Label(
                    etapa_frame,
                    text=etapa['descricao'],
                    bootstyle="secondary"
                ).pack(anchor=W, pady=(5, 0))
    
    def criar_gerenciador_participantes(self, parent, projeto):
        """Cria o gerenciador de participantes."""
        # Botão adicionar
        btn_add = ttk.Button(
            parent,
            text="➕ Adicionar Participante",
            command=lambda: self.adicionar_participante_dialog(projeto),
            bootstyle="success"
        )
        btn_add.pack(anchor=W, pady=(0, 15))
        
        participantes = projeto.get('participantes', [])
        
        if not participantes:
            ttk.Label(
                parent,
                text="Nenhum participante cadastrado.",
                bootstyle="secondary",
                justify=CENTER
            ).pack(expand=YES)
            return
        
        # Lista de participantes
        for participante in participantes:
            part_frame = ttk.Frame(parent, bootstyle="light", padding=15)
            part_frame.pack(fill=X, pady=5)
            
            ttk.Label(
                part_frame,
                text=f"👤 {participante.get('nome', 'Sem nome')}",
                font=("Segoe UI", 12, "bold")
            ).pack(anchor=W)
            
            ttk.Label(
                part_frame,
                text=f"Cargo: {participante.get('cargo', 'N/A')}",
                bootstyle="secondary"
            ).pack(anchor=W, pady=(3, 0))
    
    def adicionar_etapa_dialog(self, projeto):
        """Dialog para adicionar nova etapa."""
        dialog = ttk.Toplevel(self)
        dialog.title("Nova Etapa")
        dialog.geometry("600x550")
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 275
        dialog.geometry(f"600x550+{x}+{y}")
        
        # Cabeçalho
        header = ttk.Frame(dialog, bootstyle="primary", padding=15)
        header.pack(fill=X)
        
        ttk.Label(
            header,
            text="➕ Adicionar Nova Etapa",
            font=("Segoe UI", 16, "bold"),
            bootstyle="inverse-primary"
        ).pack()
        
        container = ttk.Frame(dialog, padding=20)
        container.pack(fill=BOTH, expand=NO)
        
        ttk.Label(container, text="Nome da Etapa *", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(0, 5))
        entry_nome = ttk.Entry(container, font=("Segoe UI", 12), bootstyle="info")
        entry_nome.pack(fill=X, ipady=8)
        
        ttk.Label(container, text="Descrição", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(15, 5))
        text_desc = ttk.Text(container, height=5, font=("Segoe UI", 11), wrap="word")
        text_desc.pack(fill=BOTH, expand=YES)
        
        ttk.Label(container, text="Status", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(15, 5))
        combo_status = ttk.Combobox(
            container,
            values=["em andamento", "concluído", "pausado"],
            state="readonly",
            font=("Segoe UI", 11)
        )
        combo_status.set("em andamento")
        combo_status.pack(fill=X, ipady=8)
        
        def salvar():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Preencha o nome da etapa.", parent=dialog)
                return
            
            try:
                if USE_SQLITE:
                    db.adicionar_etapa(
                        projeto_id=projeto['id'],
                        nome=nome,
                        descricao=text_desc.get("1.0", "end-1c"),
                        status=combo_status.get()
                    )
                    messagebox.showinfo("Sucesso", "Etapa adicionada com sucesso!", parent=dialog)
                    dialog.destroy()
                    self.carregar_dados()
                    self.visualizar_projeto_detalhado(
                        next(p for p in self.projetos if p['id'] == projeto['id'])
                    )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar etapa: {e}", parent=dialog)
        
        # Bind Enter no campo nome para salvar
        entry_nome.bind('<Return>', lambda e: salvar())
        entry_nome.focus()
        
        # Rodapé com botões
        footer = ttk.Frame(dialog, padding=(20, 10))
        footer.pack(fill=X, side=BOTTOM)
        
        ttk.Button(
            footer,
            text="✓ Adicionar Etapa",
            command=salvar,
            bootstyle="success",
            width=20
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(
            footer,
            text="✗ Cancelar",
            command=dialog.destroy,
            bootstyle="secondary",
            width=15
        ).pack(side=LEFT)
    
    def adicionar_participante_dialog(self, projeto):
        """Dialog para adicionar participante."""
        dialog = ttk.Toplevel(self)
        dialog.title("Adicionar Participante")
        dialog.geometry("600x450")
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 225
        dialog.geometry(f"600x450+{x}+{y}")
        
        # Cabeçalho
        header = ttk.Frame(dialog, bootstyle="success", padding=15)
        header.pack(fill=X)
        
        ttk.Label(
            header,
            text="👤 Adicionar Participante",
            font=("Segoe UI", 16, "bold"),
            bootstyle="inverse-success"
        ).pack()
        
        container = ttk.Frame(dialog, padding=20)
        container.pack(fill=BOTH, expand=YES)
        
        ttk.Label(container, text="Nome *", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(10, 5))
        entry_nome = ttk.Entry(container, font=("Segoe UI", 12), bootstyle="info")
        entry_nome.pack(fill=X, ipady=8)
        entry_nome.focus()
        
        ttk.Label(container, text="Cargo", font=("Segoe UI", 11, "bold")).pack(anchor=W, pady=(15, 5))
        entry_cargo = ttk.Entry(container, font=("Segoe UI", 12), bootstyle="info")
        entry_cargo.pack(fill=X, ipady=8)
        
        def salvar():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Preencha o nome do participante.", parent=dialog)
                return
            
            try:
                if USE_SQLITE:
                    db.adicionar_participante(
                        projeto_id=projeto['id'],
                        nome=nome,
                        cargo=entry_cargo.get().strip()
                    )
                    messagebox.showinfo("Sucesso", "Participante adicionado com sucesso!", parent=dialog)
                    dialog.destroy()
                    self.carregar_dados()
                    self.visualizar_projeto_detalhado(
                        next(p for p in self.projetos if p['id'] == projeto['id'])
                    )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar participante: {e}", parent=dialog)
        
        # Rodapé com botões
        footer = ttk.Frame(dialog, padding=(20, 10))
        footer.pack(fill=X, side=BOTTOM)
        
        ttk.Button(
            footer,
            text="✓ Adicionar Participante",
            command=salvar,
            bootstyle="success",
            width=22
        ).pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(
            footer,
            text="✗ Cancelar",
            command=dialog.destroy,
            bootstyle="secondary",
            width=15
        ).pack(side=LEFT)
    
    def abrir_editor_projeto(self, projeto):
        """Abre editor de projeto."""
        self.clear_content()
        
        title = ttk.Label(
            self.content_area,
            text=f"Editar: {projeto['nome']}",
            font=("Segoe UI", 28, "bold"),
            bootstyle="inverse"
        )
        title.pack(pady=(0, 30))
        
        # Formulário
        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(fill=BOTH, expand=YES, padx=100)
        
        ttk.Label(form_frame, text="Nome do Projeto *", font=("Segoe UI", 11)).pack(anchor=W, pady=(10, 5))
        entry_nome = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_nome.insert(0, projeto['nome'])
        entry_nome.pack(fill=X, ipady=8)
        
        ttk.Label(form_frame, text="Cliente *", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        entry_cliente = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_cliente.insert(0, projeto.get('cliente', ''))
        entry_cliente.pack(fill=X, ipady=8)
        
        ttk.Label(form_frame, text="Prazo *", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        entry_prazo = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_prazo.insert(0, projeto.get('prazo', ''))
        entry_prazo.pack(fill=X, ipady=8)
        
        ttk.Label(form_frame, text="Orçamento", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        entry_orcamento = ttk.Entry(form_frame, font=("Segoe UI", 12), bootstyle="info")
        entry_orcamento.insert(0, str(projeto.get('orcamento', 0)))
        entry_orcamento.pack(fill=X, ipady=8)
        
        ttk.Label(form_frame, text="Status", font=("Segoe UI", 11)).pack(anchor=W, pady=(15, 5))
        combo_status = ttk.Combobox(
            form_frame,
            values=["ativo", "concluído", "pausado", "cancelado"],
            state="readonly",
            font=("Segoe UI", 11)
        )
        combo_status.set(projeto.get('status', 'ativo'))
        combo_status.pack(fill=X, ipady=8)
        
        def salvar_edicao():
            nome = entry_nome.get().strip()
            cliente = entry_cliente.get().strip()
            prazo = entry_prazo.get().strip()
            
            if not nome or not cliente or not prazo:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
                return
            
            try:
                if USE_SQLITE:
                    db.atualizar_projeto(
                        projeto_id=projeto['id'],
                        nome=nome,
                        cliente=cliente,
                        prazo=prazo,
                        orcamento=float(entry_orcamento.get()) if entry_orcamento.get() else 0.0,
                        status=combo_status.get()
                    )
                    messagebox.showinfo("Sucesso", "Projeto atualizado!")
                    self.carregar_dados()
                    self.show_projetos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar: {e}")
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=X, pady=(30, 0))
        
        ttk.Button(btn_frame, text="✓ Salvar", command=salvar_edicao, bootstyle="success", width=20).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="✗ Cancelar", command=self.show_projetos, bootstyle="secondary", width=20).pack(side=LEFT, padx=5)
    
    def confirmar_excluir_projeto(self, projeto, dialog_pai):
        """Confirma exclusão de projeto."""
        if messagebox.askyesno("Confirmar", f"Excluir '{projeto['nome']}'?\n\nEsta ação é irreversível.", parent=dialog_pai):
            try:
                if USE_SQLITE:
                    db.excluir_projeto(projeto['id'])
                    messagebox.showinfo("Sucesso", "Projeto excluído!", parent=dialog_pai)
                    dialog_pai.destroy()
                    self.carregar_dados()
                    self.show_projetos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}", parent=dialog_pai)
    
    def create_status_pie_chart(self, parent):
        """Cria gráfico de pizza com status dos projetos."""
        chart_frame = ttk.Labelframe(parent, text="📊 Status dos Projetos", bootstyle="info")
        chart_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(5, 5), pady=5)
        
        # Contar status
        status_count = {}
        for p in self.projetos:
            status = p.get('status', 'ativo')
            status_count[status] = status_count.get(status, 0) + 1
        
        if not status_count:
            ttk.Label(chart_frame, text="Sem dados", bootstyle="secondary").pack(expand=YES)
            return
        
        fig, ax = plt.subplots(figsize=(5, 4), facecolor='#222')
        
        colors = {'ativo': '#375a7f', 'concluído': '#00bc8c', 'pausado': '#f39c12', 'cancelado': '#e74c3c'}
        pie_colors = [colors.get(status, '#95a5a6') for status in status_count.keys()]
        
        ax.pie(
            status_count.values(),
            labels=[s.capitalize() for s in status_count.keys()],
            autopct='%1.1f%%',
            colors=pie_colors,
            textprops={'color': 'white', 'fontsize': 10}
        )
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
    
    def create_projects_timeline_chart(self, parent):
        """Cria gráfico de timeline de projetos."""
        chart_frame = ttk.Labelframe(parent, text="📅 Projetos por Período", bootstyle="success")
        chart_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(5, 5), pady=5)
        
        if len(self.projetos) < 2:
            ttk.Label(chart_frame, text="Dados insuficientes", bootstyle="secondary").pack(expand=YES)
            return
        
        fig, ax = plt.subplots(figsize=(5, 4), facecolor='#222')
        ax.set_facecolor('#222')
        
        # Simular dados por trimestre
        trimestres = ['Q1', 'Q2', 'Q3', 'Q4']
        valores = [len(self.projetos) // 4 + i for i in range(4)]
        
        ax.plot(trimestres, valores, marker='o', linewidth=2, markersize=8, color='#00bc8c')
        ax.fill_between(range(len(trimestres)), valores, alpha=0.3, color='#00bc8c')
        ax.set_ylabel('Projetos', color='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.2)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
    
    def create_etapas_chart(self, parent):
        """Cria gráfico de etapas concluídas vs pendentes."""
        chart_frame = ttk.Labelframe(parent, text="📋 Etapas: Concluídas vs Pendentes", bootstyle="warning")
        chart_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        total_etapas = 0
        concluidas = 0
        
        for p in self.projetos:
            etapas = p.get('etapas', [])
            total_etapas += len(etapas)
            concluidas += sum(1 for e in etapas if e.get('status') == 'concluído')
        
        pendentes = total_etapas - concluidas
        
        if total_etapas == 0:
            ttk.Label(chart_frame, text="Nenhuma etapa cadastrada", bootstyle="secondary").pack(expand=YES)
            return
        
        fig, ax = plt.subplots(figsize=(10, 3), facecolor='#222')
        ax.set_facecolor('#222')
        
        categorias = ['Concluídas', 'Pendentes']
        valores = [concluidas, pendentes]
        cores = ['#00bc8c', '#f39c12']
        
        bars = ax.barh(categorias, valores, color=cores)
        
        ax.set_xlabel('Quantidade', color='white')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Adicionar valores
        for bar, valor in zip(bars, valores):
            width = bar.get_width()
            ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{valor} ({valor/total_etapas*100:.1f}%)',
                   ha='left', va='center', color='white', fontweight='bold')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
    
    def exportar_csv(self):
        """Exporta projetos para CSV."""
        try:
            import csv
            from datetime import datetime
            
            filename = f"projetos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(DATA_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Nome', 'Cliente', 'Prazo', 'Orçamento', 'Status', 'Total Etapas', 'Etapas Concluídas'])
                
                for p in self.projetos:
                    etapas = p.get('etapas', [])
                    total = len(etapas)
                    concluidas = sum(1 for e in etapas if e.get('status') == 'concluído')
                    
                    writer.writerow([
                        p['nome'],
                        p.get('cliente', ''),
                        p.get('prazo', ''),
                        p.get('orcamento', 0),
                        p.get('status', 'ativo'),
                        total,
                        concluidas
                    ])
            
            messagebox.showinfo("Sucesso", f"Exportado para:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")
    
    def gerar_pdf(self):
        """Gera relatório PDF dos projetos."""
        try:
            from fpdf import FPDF
            from datetime import datetime
            
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font("Arial", "B", 20)
            pdf.cell(0, 10, "ProjetoX - Relatório de Projetos", ln=True, align="C")
            pdf.ln(5)
            
            # Data
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="C")
            pdf.ln(10)
            
            # Estatísticas
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Estatísticas Gerais", ln=True)
            pdf.ln(2)
            
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Total de Projetos: {len(self.projetos)}", ln=True)
            
            ativos = sum(1 for p in self.projetos if p.get('status') == 'ativo')
            pdf.cell(0, 8, f"Projetos Ativos: {ativos}", ln=True)
            
            concluidos = sum(1 for p in self.projetos if p.get('status') == 'concluído')
            pdf.cell(0, 8, f"Projetos Concluídos: {concluidos}", ln=True)
            
            total_etapas = sum(len(p.get('etapas', [])) for p in self.projetos)
            pdf.cell(0, 8, f"Total de Etapas: {total_etapas}", ln=True)
            pdf.ln(10)
            
            # Lista de projetos
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Lista de Projetos", ln=True)
            pdf.ln(2)
            
            for idx, p in enumerate(self.projetos, 1):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, f"{idx}. {p['nome']}", ln=True)
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"   Cliente: {p.get('cliente', 'N/A')}", ln=True)
                pdf.cell(0, 6, f"   Prazo: {p.get('prazo', 'N/A')}", ln=True)
                pdf.cell(0, 6, f"   Status: {p.get('status', 'ativo').upper()}", ln=True)
                
                etapas = p.get('etapas', [])
                if etapas:
                    concl = sum(1 for e in etapas if e.get('status') == 'concluído')
                    pdf.cell(0, 6, f"   Etapas: {concl}/{len(etapas)} concluídas", ln=True)
                
                pdf.ln(3)
            
            # Salvar
            filename = f"relatorio_projetos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(DATA_DIR, filename)
            pdf.output(filepath)
            
            messagebox.showinfo("Sucesso", f"Relatório gerado:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}")
    
    def sair(self):
        """Fecha o aplicativo."""
        if messagebox.askyesno("Confirmar", "Deseja realmente sair?"):
            self.destroy()


if __name__ == "__main__":
    app = ModernDashboard()
    app.mainloop()
