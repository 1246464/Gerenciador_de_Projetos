"""
Módulo de geração de relatórios.
Gera PDFs, CSVs e gráficos dos projetos.
"""
from fpdf import FPDF
import datetime
import os
import platform
import csv
import matplotlib.pyplot as plt
from typing import Dict, List

try:
    from utils import sanitizar_nome_arquivo
except ImportError:
    import re
    def sanitizar_nome_arquivo(nome: str) -> str:
        caracteres_invalidos = r'[<>:"/\\|?*]'
        nome_limpo = re.sub(caracteres_invalidos, '_', nome)
        return nome_limpo.strip()

# -----------------------
# Utilitários
# -----------------------

def abrir_arquivo(nome_arquivo: str) -> None:
    """
    Abre um arquivo conforme o sistema operacional.
    
    Args:
        nome_arquivo: Caminho do arquivo a ser aberto
    """
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(nome_arquivo)
        elif sistema == "Darwin":  # macOS
            os.system(f"open '{nome_arquivo}'")
        else:  # Linux
            os.system(f"xdg-open '{nome_arquivo}'")
    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")

# -----------------------
# Exportar PDF do projeto
# -----------------------

def gerar_pdf_projeto(projeto: Dict) -> None:
    """
    Gera um relatório em PDF com os dados do projeto.
    
    Args:
        projeto: Dicionário com dados do projeto
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        data_geracao = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        nome_proj = projeto.get('nome', 'Projeto Sem Nome')
        
        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=f"Relatório do Projeto - {nome_proj}", ln=True, align="C")

        pdf.set_font("Arial", "", 10)
        pdf.cell(200, 10, txt=f"Gerado em: {data_geracao}", ln=True, align="C")
        pdf.ln(10)

        # Informações do projeto
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt=f"Projeto: {nome_proj}", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, txt=f"Descrição: {projeto.get('descricao', 'Sem descrição')}")
        pdf.cell(200, 8, txt=f"ID: {projeto.get('id', 'N/D')}", ln=True)
        
        if 'prazo' in projeto and projeto['prazo']:
            pdf.cell(200, 8, txt=f"Prazo Geral: {projeto['prazo']}", ln=True)

        # Etapas
        etapas = projeto.get("etapas", [])
        pdf.ln(4)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(200, 8, txt=f"Etapas ({len(etapas)}):", ln=True)
        pdf.set_font("Arial", "", 10)

        if etapas:
            for idx, etapa in enumerate(etapas, 1):
                texto = (
                    f"{idx}. {etapa.get('nome', '-')}\n"
                    f"   Status: {etapa.get('status', '-')}\n"
                    f"   Prazo: {etapa.get('prazo', '-')}\n"
                    f"   Responsável: {etapa.get('responsavel', '-')}\n"
                )
                pdf.multi_cell(0, 6, txt=texto)
        else:
            pdf.cell(200, 8, txt="Sem etapas cadastradas", ln=True)
        
        # Participantes
        pessoas = projeto.get("pessoas", [])
        if pessoas:
            pdf.ln(4)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(200, 8, txt=f"Participantes ({len(pessoas)}):", ln=True)
            pdf.set_font("Arial", "", 10)
            
            for idx, pessoa in enumerate(pessoas, 1):
                texto = (
                    f"{idx}. {pessoa.get('nome', '-')}\n"
                    f"   Cargo: {pessoa.get('cargo', '-')}\n"
                    f"   Etapa: {pessoa.get('etapa', '-')}\n"
                    f"   Prazo: {pessoa.get('prazo', '-')}\n"
                )
                pdf.multi_cell(0, 6, txt=texto)

        # Salvar arquivo
        nome_arquivo = f"relatorio_{sanitizar_nome_arquivo(nome_proj)}_{projeto.get('id', 'sem_id')}.pdf"
        pdf.output(nome_arquivo)
        print(f"PDF gerado: {nome_arquivo}")
        abrir_arquivo(nome_arquivo)
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")

# -----------------------
# Gráfico de Barras Horizontais
# -----------------------

def gerar_grafico_barras(projeto: Dict) -> None:
    """
    Gera um gráfico horizontal de barras com o status das etapas.
    
    Args:
        projeto: Dicionário com dados do projeto
    """
    try:
        etapas = projeto.get("etapas", [])
        if not etapas:
            print("Sem etapas para gerar gráfico.")
            return

        nomes = [etapa.get("nome", "-")[:30] for etapa in etapas]  # Limitar tamanho
        status = [etapa.get("status", "indefinido").lower() for etapa in etapas]

        cores = {
            "pendente": "#808080",
            "em andamento": "#FF8C00",
            "concluído": "#28A745",
            "indefinido": "#6C757D"
        }
        cor_barras = [cores.get(s, "#0078D4") for s in status]

        # Ajustar tamanho da figura baseado no número de etapas
        altura = max(6, len(nomes) * 0.6)
        fig, ax = plt.subplots(figsize=(10, altura))
        
        ax.barh(nomes, [1] * len(nomes), color=cor_barras, height=0.7)
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        ax.set_title(
            f"Etapas do Projeto: {projeto.get('nome', 'Sem Nome')}", 
            fontsize=14, 
            fontweight='bold',
            pad=20
        )
        
        # Adicionar texto com status
        for i, s in enumerate(status):
            ax.text(0.5, i, s.title(), ha='center', va='center', 
                   color='white', fontsize=10, fontweight='bold')

        plt.tight_layout()
        
        nome_proj = sanitizar_nome_arquivo(projeto.get('nome', 'projeto'))
        nome_arquivo = f"grafico_{nome_proj}_{projeto.get('id')}.png"
        plt.savefig(nome_arquivo, dpi=150, bbox_inches='tight')
        print(f"Gráfico gerado: {nome_arquivo}")
        plt.close()
        abrir_arquivo(nome_arquivo)
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        plt.close()

# -----------------------
# Exportar CSV do projeto
# -----------------------

def exportar_csv_projeto(projeto: Dict) -> None:
    """
    Exporta as etapas e participantes do projeto em formato CSV.
    
    Args:
        projeto: Dicionário com dados do projeto
    """
    try:
        nome_proj = sanitizar_nome_arquivo(projeto.get('nome', 'projeto'))
        nome_arquivo = f"dados_{nome_proj}_{projeto.get('id')}.csv"
        
        with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Informações do projeto
            writer.writerow(["INFORMAÇÕES DO PROJETO"])
            writer.writerow(["ID", projeto.get("id", "")])
            writer.writerow(["Nome", projeto.get("nome", "")])
            writer.writerow(["Descrição", projeto.get("descricao", "")])
            writer.writerow(["Prazo", projeto.get("prazo", "")])
            writer.writerow([])
            
            # Etapas
            writer.writerow(["ETAPAS"])
            writer.writerow(["Nome", "Status", "Prazo", "Responsável"])
            for etapa in projeto.get("etapas", []):
                writer.writerow([
                    etapa.get("nome", ""),
                    etapa.get("status", ""),
                    etapa.get("prazo", ""),
                    etapa.get("responsavel", "")
                ])
            
            writer.writerow([])
            
            # Participantes
            pessoas = projeto.get("pessoas", [])
            if pessoas:
                writer.writerow(["PARTICIPANTES"])
                writer.writerow(["Nome", "Cargo", "Etapa", "Prazo"])
                for pessoa in pessoas:
                    writer.writerow([
                        pessoa.get("nome", ""),
                        pessoa.get("cargo", ""),
                        pessoa.get("etapa", ""),
                        pessoa.get("prazo", "")
                    ])
        
        print(f"CSV gerado: {nome_arquivo}")
        abrir_arquivo(nome_arquivo)
    except Exception as e:
        print(f"Erro ao gerar CSV: {e}")
