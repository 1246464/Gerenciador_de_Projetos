# 💼 ProjetoX — Sistema de Gestão de Projetos

**ProjetoX** é uma aplicação desktop de gerenciamento de projetos desenvolvida em Python com interface gráfica moderna usando `customtkinter`. Sistema completo para organizar projetos, etapas, participantes e gerar relatórios profissionais.

---

## ✨ Funcionalidades

### 🔐 Autenticação
- Sistema de login e cadastro de usuários
- **Senhas criptografadas com SHA-256** para segurança
- Migração automática de senhas antigas

### 📊 Gerenciamento de Projetos
- Criar, editar e excluir projetos
- Adicionar descrições detalhadas
- Definir prazos gerais
- Visualização em lista organizada

### 📋 Controle de Etapas
- Adicionar múltiplas etapas por projeto
- Status: Pendente, Em Andamento, Concluído
- Definir prazos individuais
- Atribuir responsáveis

### 👥 Gestão de Participantes
- Adicionar membros ao projeto
- Definir cargos e responsabilidades
- Vincular participantes a etapas específicas

### 📈 Relatórios e Exportação
- **PDF**: Relatório completo do projeto
- **CSV**: Exportação de dados para Excel/Sheets
- **Gráficos**: Visualização de status das etapas

### 🎨 Interface
- Tema escuro moderno
- Menu lateral com gavetas expansíveis
- Gráfico de pizza em tempo real
- Barra de progresso do projeto

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **customtkinter** - Interface gráfica moderna
- **matplotlib** - Gráficos e visualizações
- **fpdf** - Geração de PDFs
- **SQLite3** - Banco de dados relacional (migrado de JSON)
- **hashlib** - Criptografia de senhas

---

## 🚀 Como Executar

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/projetox.git
cd projetox
```

### 2. Criar ambiente virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Executar o aplicativo
```bash
cd src
python login.py
```

---

## 📁 Estrutura do Projeto

```
projetox/
├── src/
│   ├── login.py           # Tela de login e cadastro
│   ├── tela_inicial.py    # Dashboard principal
│   ├── banco.py           # Gerenciamento de dados
│   ├── relatorio.py       # Geração de relatórios
│   ├── database.py        # Módulo SQLite (novo!)
│   ├── config.py          # Configurações centralizadas
│   └── utils.py           # Funções utilitárias
├── data/
│   └── projetox.db        # Banco de dados SQLite
├── docs/
│   └── README.md
├── requirements.txt
└── .gitignore
```

---

## 🔒 Segurança

- ✅ Senhas criptografadas com **SHA-256**
- ✅ Validação de entrada de dados
- ✅ Tratamento robusto de erros
- ✅ Validação de formato de datas
- ✅ Migração automática de senhas antigas

---

## 📝 Melhorias Implementadas (v2.0)

### Segurança
- ✅ Hash SHA-256 para senhas
- ✅ Validação robusta de entrada
- ✅ Tratamento de erros aprimorado

### Banco de Dados (v2.1)
- ✅ **Migrado de JSON para SQLite**
- ✅ Integridade referencial com Foreign Keys
- ✅ Transações ACID
- ✅ Índices para otimização
- ✅ Performance melhorada

### Código
- ✅ Type hints em todas as funções
- ✅ Docstrings completas
- ✅ Arquitetura modular
- ✅ Separação de responsabilidades
- ✅ Configurações centralizadas

### Interface
- ✅ Botões de cancelar em todos os diálogos
- ✅ Janelas modais (grab_set)
- ✅ Mensagens de confirmação
- ✅ Validação de datas em tempo real
- ✅ Melhor feedback visual

### Funcionalidades
- ✅ Exportação de participantes em CSV
- ✅ Participantes no relatório PDF
- ✅ Gráficos mais bonitos e informativos
- ✅ Nomes de arquivo sanitizados

---

## 🎯 Roadmap Futuro

- [x] Banco de dados SQLite ✅ **CONCLUÍDO!**
- [ ] Backup automático
- [ ] Múltiplos usuários com permissões
- [ ] Dashboard com estatísticas
- [ ] Notificações de prazos
- [ ] Tema claro/escuro alternável
- [ ] Suporte a anexos
- [ ] Integração com calendário

---

## 📸 Capturas de Tela

### Tela de Login
![Login](../docs/screenshots/login.png)

### Dashboard Principal
![Dashboard](../docs/screenshots/dashboard.png)

### Relatório PDF
![Relatório](../docs/screenshots/relatorio.png)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👨‍💻 Autor

**Maicon**

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Nome](https://linkedin.com/in/seu-perfil)

---

## 🙏 Agradecimentos

- CustomTkinter pela excelente biblioteca de UI
- Comunidade Python por todo suporte
- Todos que contribuíram com feedback

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**
