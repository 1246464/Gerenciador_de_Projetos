# 🔄 Migração para SQLite - ProjetoX

## ✅ Migração Concluída com Sucesso!

O ProjetoX foi migrado de arquivos JSON para banco de dados SQLite com sucesso!

---

## 📊 Resultado da Migração

### Dados Migrados:
- ✅ **2 usuários** migrados (senhas convertidas para hash SHA-256)
- ✅ **2 projetos** migrados
- ✅ **2 etapas** migradas
- ✅ **2 participantes** migrados

### Backups Criados:
- 💾 `dados_projetos.json.backup_20260119_113201`
- 💾 `dados_usuarios.json.backup_20260119_113201`

---

## 🎯 Vantagens do SQLite

### Performance
- ✅ **Consultas mais rápidas** com índices
- ✅ **Transações ACID** (Atomicidade, Consistência, Isolamento, Durabilidade)
- ✅ **Menor uso de memória**

### Segurança
- ✅ **Integridade referencial** com Foreign Keys
- ✅ **Prevenção de corrupção** de dados
- ✅ **Validação automática** de tipos

### Funcionalidades
- ✅ **Queries SQL complexas**
- ✅ **Relacionamentos entre tabelas**
- ✅ **Índices para otimização**
- ✅ **Backup e restauração** simplificados

---

## 🗄️ Estrutura do Banco de Dados

### Tabelas Criadas:

#### 1. **projetos**
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- nome (TEXT NOT NULL)
- descricao (TEXT)
- prazo (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 2. **etapas**
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- projeto_id (INTEGER - Foreign Key)
- nome (TEXT NOT NULL)
- status (TEXT DEFAULT 'pendente')
- prazo (TEXT)
- responsavel (TEXT)
- created_at (TIMESTAMP)
```

#### 3. **participantes**
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- projeto_id (INTEGER - Foreign Key)
- nome (TEXT NOT NULL)
- cargo (TEXT)
- etapa (TEXT)
- prazo (TEXT)
- created_at (TIMESTAMP)
```

#### 4. **usuarios**
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- nome (TEXT UNIQUE NOT NULL)
- senha_hash (TEXT NOT NULL)
- created_at (TIMESTAMP)
```

### Índices:
- `idx_etapas_projeto` - Otimiza consultas de etapas por projeto
- `idx_participantes_projeto` - Otimiza consultas de participantes por projeto

---

## 🔧 Arquivos Criados/Modificados

### Novos Arquivos:
1. **[database.py](src/database.py)** - Módulo completo de gerenciamento SQLite
2. **[migrar_para_sqlite.py](migrar_para_sqlite.py)** - Script de migração
3. **[SQLITE_MIGRATION.md](SQLITE_MIGRATION.md)** - Esta documentação

### Arquivos Modificados:
1. **[config.py](src/config.py)** - Adicionado caminho do banco SQLite
2. **[login.py](src/login.py)** - Suporte a SQLite e JSON (fallback)
3. **[banco.py](src/banco.py)** - Suporte a SQLite e JSON (fallback)

---

## 🚀 Como Usar

### Iniciar a Aplicação
```bash
cd src
python login.py
```

O sistema agora usa automaticamente o SQLite! 🎉

### Credenciais Migradas
- Os usuários existentes foram migrados
- As senhas foram convertidas para hash SHA-256
- Login funciona normalmente

---

## 🔄 Retrocompatibilidade

O código mantém **retrocompatibilidade** com JSON:

- Se `database.py` não estiver disponível → usa JSON
- Se houver erro no SQLite → fallback para JSON
- Código detecta automaticamente qual sistema usar

```python
USE_SQLITE = True  # Tentará usar SQLite primeiro
```

---

## 📁 Localização do Banco

O banco de dados está em:
```
data/projetox.db
```

---

## 🛠️ Operações Disponíveis

### Projetos
- ✅ `adicionar_projeto(nome, descricao, prazo)`
- ✅ `buscar_projeto(projeto_id)`
- ✅ `buscar_projeto_completo(projeto_id)`
- ✅ `listar_projetos()`
- ✅ `atualizar_projeto(projeto_id, ...)`
- ✅ `excluir_projeto(projeto_id)`

### Etapas
- ✅ `adicionar_etapa(projeto_id, nome, status, prazo, responsavel)`
- ✅ `listar_etapas(projeto_id)`
- ✅ `atualizar_etapa(etapa_id, ...)`
- ✅ `excluir_etapa(etapa_id)`

### Participantes
- ✅ `adicionar_participante(projeto_id, nome, cargo, etapa, prazo)`
- ✅ `listar_participantes(projeto_id)`
- ✅ `buscar_participante_por_nome(projeto_id, nome)`
- ✅ `atualizar_participante(participante_id, ...)`
- ✅ `excluir_participante(participante_id)`

### Usuários
- ✅ `adicionar_usuario(nome, senha_hash)`
- ✅ `buscar_usuario(nome)`
- ✅ `atualizar_senha_usuario(nome, novo_hash)`
- ✅ `listar_usuarios()`

---

## 🔍 Como Consultar o Banco

### Usando Python:
```python
from src import database as db

# Listar todos os projetos
projetos = db.listar_projetos()
for p in projetos:
    print(f"ID: {p['id']} - Nome: {p['nome']}")

# Buscar projeto completo
projeto = db.buscar_projeto_completo(1)
print(f"Etapas: {len(projeto['etapas'])}")
print(f"Participantes: {len(projeto['pessoas'])}")
```

### Usando SQLite CLI:
```bash
sqlite3 data/projetox.db

# Listar projetos
SELECT * FROM projetos;

# Listar etapas de um projeto
SELECT * FROM etapas WHERE projeto_id = 1;

# Contar participantes por projeto
SELECT p.nome, COUNT(part.id) as total_participantes
FROM projetos p
LEFT JOIN participantes part ON p.id = part.projeto_id
GROUP BY p.id;
```

---

## 💡 Dicas e Boas Práticas

### Backup
O banco SQLite é um único arquivo (`projetox.db`):
```bash
# Fazer backup
cp data/projetox.db data/backup_projetox_$(date +%Y%m%d).db

# Restaurar backup
cp data/backup_projetox_20260119.db data/projetox.db
```

### Performance
- ✅ Use índices para queries frequentes
- ✅ Evite SELECT * quando não for necessário
- ✅ Use transações para múltiplas operações

### Segurança
- ✅ Banco com permissões adequadas
- ✅ Senhas sempre em hash SHA-256
- ✅ Validação de entrada de dados

---

## 🎯 Próximos Passos

### Opcional - Limpeza
Se tudo estiver funcionando perfeitamente, você pode:

1. **Manter os backups** (recomendado):
   ```bash
   # Os arquivos .backup_* estão seguros
   ```

2. **Remover JSONs originais** (opcional):
   ```bash
   # Apenas se tiver certeza que está tudo OK
   rm data/dados_projetos.json
   rm data/dados_usuarios.json
   ```

### Melhorias Futuras
- [ ] Adicionar migrations automáticas
- [ ] Sistema de versionamento do schema
- [ ] Exportação/importação de dados
- [ ] Análises e relatórios SQL
- [ ] API REST para o banco de dados

---

## ❓ Troubleshooting

### Problema: "Banco de dados bloqueado"
**Solução:** Feche todas as instâncias da aplicação

### Problema: "Arquivo não encontrado"
**Solução:** Verifique se `data/projetox.db` existe. Execute a migração novamente.

### Problema: "Erro ao conectar"
**Solução:** Verifique permissões da pasta `data/`

### Reverter para JSON
Se precisar voltar ao JSON:
1. Renomeie ou remova `database.py`
2. Restaure os backups `.backup_*`
3. A aplicação detectará automaticamente e usará JSON

---

## 📊 Comparação: JSON vs SQLite

| Aspecto | JSON | SQLite | Vencedor |
|---------|------|--------|----------|
| Performance | 😐 Lenta | ⚡ Rápida | SQLite |
| Integridade | ❌ Manual | ✅ Automática | SQLite |
| Consultas | ❌ Limitado | ✅ SQL completo | SQLite |
| Backup | ✅ Simples | ✅ Um arquivo | Empate |
| Portabilidade | ✅ Texto | ✅ Binário | Empate |
| Transações | ❌ Não | ✅ ACID | SQLite |
| Tamanho | 😐 Maior | ✅ Menor | SQLite |

**Conclusão: SQLite é superior em quase todos os aspectos!**

---

## 📝 Changelog

### v2.1 - SQLite Migration (19/01/2026)
- ✅ Migrado de JSON para SQLite
- ✅ Criado módulo `database.py`
- ✅ Backups automáticos antes da migração
- ✅ Retrocompatibilidade com JSON
- ✅ Todas as senhas convertidas para hash SHA-256
- ✅ Integridade referencial com Foreign Keys
- ✅ Índices para otimização de performance

---

## 🎉 Conclusão

A migração para SQLite foi **100% bem-sucedida**! 

O ProjetoX agora tem:
- ⚡ **Performance melhorada**
- 🔒 **Segurança aprimorada**
- 🗄️ **Estrutura profissional**
- 🚀 **Pronto para escalar**

**Parabéns pela evolução do projeto! 🎊**
