# 🌳 Estratégia Git e Desenvolvimento

## 📋 Plano de Commits e Branches

### **Commit Atual - Baseline do Projeto**
```bash
# 1. Verificar status atual
git status

# 2. Adicionar todos os arquivos criados
git add .

# 3. Commit inicial completo
git commit -m "feat: complete project architecture and documentation

- Add CLI transcription tool with environment variables
- Create comprehensive documentation (README, API, WebSocket, etc.)
- Design deployment architecture for legenda.iaforte.com.br
- Add Docker configurations for development and production
- Include specialized scripts for Brazilian use cases
- Create database schema and API specifications
- Add local development guide with RTX 3060 support

Co-authored-by: Architect Mode"

# 4. Verificar commit
git log --oneline -1
```

---

## 🌿 Estratégia de Branching (GitHub Flow Simplificado)

### **Branch Structure**
```
main (produção)
├── dev/web-interface (desenvolvimento principal)
    ├── feature/backend-api
    ├── feature/frontend-ui
    ├── feature/websocket-integration
    ├── feature/gpu-worker
    └── feature/deployment-config
```

### **Comandos Git**
```bash
# Criar branch principal de desenvolvimento
git checkout -b dev/web-interface

# Branches para features específicas
git checkout -b feature/backend-api
git checkout -b feature/frontend-ui
git checkout -b feature/gpu-worker
```

---

## 📝 Convenção de Commits (Conventional Commits)

### **Tipos de Commit**
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Alterações na documentação
- `style:` - Formatação, sem mudança de código
- `refactor:` - Refatoração de código
- `test:` - Adicionar ou modificar testes
- `chore:` - Manutenção, build, dependencies

### **Exemplos**
```bash
# Features
git commit -m "feat: add FastAPI backend with job management"
git commit -m "feat: implement WebSocket real-time updates"
git commit -m "feat: create file upload component"

# Fixes
git commit -m "fix: resolve GPU memory leak in worker"
git commit -m "fix: handle large file uploads correctly"

# Documentation
git commit -m "docs: update API documentation with new endpoints"
git commit -m "docs: add deployment guide for production"
```

---

## 🎯 Estratégia de Desenvolvimento

### **Fase 1: Fundação Backend (1-2 semanas)**
```bash
# Branch para backend
git checkout dev/web-interface
git checkout -b feature/backend-api

# Desenvolvimento incremental:
# Commit 1: Structure e configuração
# Commit 2: Database models
# Commit 3: API endpoints básicos
# Commit 4: Job management
# Commit 5: WebSocket integration
```

### **Fase 2: Frontend Interface (1-2 semanas)**
```bash
# Branch para frontend
git checkout dev/web-interface
git checkout -b feature/frontend-ui

# Desenvolvimento incremental:
# Commit 1: Next.js setup e structure
# Commit 2: Upload component
# Commit 3: Progress tracking
# Commit 4: Results display
# Commit 5: WebSocket integration
```

### **Fase 3: GPU Worker (3-5 dias)**
```bash
# Branch para worker
git checkout dev/web-interface
git checkout -b feature/gpu-worker

# Desenvolvimento incremental:
# Commit 1: Celery setup
# Commit 2: Transcription service
# Commit 3: Diarization integration
# Commit 4: Progress reporting
# Commit 5: Error handling
```

---

## 🔄 Workflow de Desenvolvimento

### **Ciclo Diário**
```bash
# 1. Atualizar branch principal
git checkout dev/web-interface
git pull origin dev/web-interface

# 2. Criar/atualizar feature branch
git checkout feature/backend-api
git rebase dev/web-interface

# 3. Desenvolver e testar
# ... código ...
docker-compose -f docker-compose.dev.yml up --build

# 4. Commit incremental
git add .
git commit -m "feat: add job status endpoints"

# 5. Push regular
git push origin feature/backend-api
```

### **Merge para Dev**
```bash
# Quando feature estiver pronta
git checkout dev/web-interface
git merge feature/backend-api
git push origin dev/web-interface

# Deletar branch local (opcional)
git branch -d feature/backend-api
```

### **Release para Main**
```bash
# Quando dev estiver estável
git checkout main
git merge dev/web-interface
git tag -a v1.0.0 -m "Release: Web interface MVP"
git push origin main --tags
```

---

## 📊 Tracking de Progresso

### **Milestones**
1. **✅ Milestone 1**: Arquitetura e documentação completa
2. **🔄 Milestone 2**: Backend API funcional (dev/web-interface)
3. **⏳ Milestone 3**: Frontend MVP (feature/frontend-ui)
4. **⏳ Milestone 4**: Integração completa (feature/websocket-integration)
5. **⏳ Milestone 5**: Deploy produção (feature/deployment-config)

### **Issues/Tasks Tracking**
```bash
# Criar issues para cada feature
# GitHub Issues ou usar TODO comments no código

# TODO: Implementar upload de arquivos
# TODO: Adicionar autenticação JWT
# TODO: Configurar WebSocket server
# TODO: Otimizar performance GPU
# TODO: Adicionar testes unitários
```

---

## 🚀 Comandos Úteis

### **Setup Inicial (Agora)**
```bash
# Fazer commit atual
git add .
git commit -m "feat: complete project architecture and documentation"

# Criar branch de desenvolvimento
git checkout -b dev/web-interface

# Verificar status
git branch
git log --oneline -3
```

### **Desenvolvimento Ativo**
```bash
# Status rápido
git status --short

# Commit rápido
git add . && git commit -m "wip: working on upload component"

# Sync com remote
git pull --rebase origin dev/web-interface

# Backup local
git push origin feature/backend-api
```

### **Utilities**
```bash
# Ver diferenças
git diff HEAD~1

# Histórico visual
git log --graph --oneline --all

# Limpar branches antigas
git branch --merged | grep -v main | xargs git branch -d
```

---

## 🎯 Próximos Passos Imediatos

### **Agora (5 minutos)**
```bash
# 1. Commit atual
git add .
git commit -m "feat: complete project architecture and documentation"

# 2. Criar branch desenvolvimento
git checkout -b dev/web-interface

# 3. Configurar remote (se necessário)
# git remote add origin https://github.com/seu-usuario/transcritor.git
# git push -u origin main
```

### **Hoje (2-3 horas)**
```bash
# 1. Setup ambiente Docker
chmod +x setup-dev.sh
./setup-dev.sh

# 2. Iniciar desenvolvimento backend
git checkout -b feature/backend-api

# 3. Criar estrutura básica FastAPI
mkdir -p backend/app
# ... desenvolvimento ...
```

### **Esta Semana**
- ✅ **Backend API básico** funcionando
- ✅ **Upload de arquivos** implementado
- ✅ **Job management** com database
- ✅ **WebSocket** para updates em tempo real

---

## 💡 Dicas de Produtividade

### **Aliases Git Úteis**
```bash
# Adicionar ao ~/.gitconfig
[alias]
    st = status --short
    co = checkout
    br = branch
    ci = commit
    ca = commit -am
    lg = log --graph --oneline --all
    rb = rebase
    pu = push -u origin HEAD
```

### **Hooks Úteis**
```bash
# .git/hooks/pre-commit (opcional)
#!/bin/bash
# Rodar testes antes de commit
python -m pytest backend/tests/ --fast
npm run lint --prefix frontend/
```

**Resultado**: Estratégia Git estruturada para desenvolvimento eficiente e organizado!