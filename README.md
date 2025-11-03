# Hercruz Presença - Sistema de Gerenciamento de Presença Médica

## Visão Geral do Projeto

O projeto Hercruz Presença é uma aplicação web desenvolvida para facilitar o gerenciamento de presença de profissionais de saúde em um ambiente hospitalar. Inspirado nas mensagens de grupo do WhatsApp utilizadas atualmente para controlar escalas de plantão e rotinas, este sistema visa substituir o processo manual de "cópia e cola" por uma solução automatizada, eficiente e segura.

O sistema permite que enfermeiras e outros profissionais façam check-in e check-out de suas jornadas de trabalho através de códigos QR ou botões diretos (adaptado para mobile), com autenticação via CPF, relatórios pessoais e administrativos, e restrições de horário para evitar abusos.

### Contexto e Motivação

Atualmente, o gerenciamento de presença no hospital Hercruz é realizado via mensagens de grupo no WhatsApp. Cada dia, mensagens são enviadas com um template padrão contendo:

- Data
- Indicação de plantão diurno (marcado com 'x' se ativo)
- Indicação de plantão noturno (marcado com 'x' se ativo)
- Seção para Enfermeiras 3 e 4 (nomes dos profissionais)
- Seção para Rotina (nomes dos profissionais)
- Seção para Enfermeiras 5 e 6 (nomes dos profissionais)
- Plantão (nomes dos profissionais de plantão)
- Rotina (nomes dos profissionais de rotina)

Exemplo de mensagem:

```
Gerenciamento Presença Médica

Data : 02/11

Plantão dia :
Plantão noite :  x

Enf 3 e 4
Werner
Sinaila

Rotina

Enf 5e 6

Plantão
Giulia
Juliana

Rotina
```

Este processo é repetitivo, propenso a erros humanos, e consome tempo valioso dos profissionais. Além disso, não oferece rastreabilidade adequada nem integração com sistemas de folha de pagamento ou relatórios.

O Hercruz Presença digitaliza esse processo, permitindo check-in e check-out via QR code ou interface direta, com autenticação por CPF, relatórios administrativos e adaptação para dispositivos móveis.

O objetivo do Hercruz Presença é digitalizar esse processo, diferenciando entre dois tipos principais de trabalho:

- **Plantonista**: Profissionais em plantão, com carga horária de 12 horas, divididos em diurno e noturno.
- **Rotina**: Profissionais em jornada padrão, com carga horária de 8 horas.

## Stack Tecnológica

### Backend e Frontend Unificados
- **Linguagem**: Python 3.8+
- **Framework**: Flask (para API RESTful e servir frontend)
- **Banco de Dados**: SQLite (para simplicidade e facilidade de desenvolvimento local)
- **Frontend**: SPA hardcoded em HTML/CSS/JS puro (sem frameworks externos)
- **Geração de QR**: Biblioteca qrcode (Python)

### Outras Ferramentas
- **Controle de Versão**: Git
- **Gerenciamento de Dependências**: pip
- **Testes**: pytest (backend)
- **Linting**: flake8 (backend)
- **Documentação**: Este README
- **Deploy**: ngrok para exposição pública

## Funcionalidades Principais

### 1. Autenticação e Acesso
- Validação via CPF (11 dígitos), com registro automático para novos usuários (nome e CRM opcional).
- Geração dinâmica de QR codes para acesso público.
- Interface adaptada: QR para desktop, botões diretos para mobile.
- Restrição: 1 check-in por período de 12h (7h-19h ou 19h-7h), timezone America/Sao_Paulo.

### 2. Gerenciamento de Presença
- Check-in/check-out com cálculo automático de horas trabalhadas.
- Relatórios pessoais (semanal/mensal) para usuários logados.
- Painel administrativo com relatórios gerais/diários/mensais, filtros por usuário, e impressão.

### 3. Interface Adaptada
- Desktop: QR code clicável para iniciar processo.
- Mobile: Botões diretos para check-in/check-out, otimizados para toque.
- Campos de input (CPF/CRM) com teclado numérico em mobile.

### 4. Relatórios e Impressão
- Usuários: Relatórios pessoais semanais/mensais com tabela de presenças e botão de impressão.
- Administradores: Relatórios gerais/diários/mensais, filtráveis por usuário, com impressão direta do navegador.

### 5. Segurança e Controle
- Autenticação admin com login/senha e troca obrigatória no primeiro acesso.
- Sessões para controle de acesso.
- Validação de CPF e restrições de horário para prevenir abusos.

### 6. Administração
- Painel acessível via link no rodapé (oculto para logados).
- Login admin/admin, força troca de senha.
- Geração de relatórios avançados com filtros e impressão.

## Arquitetura do Sistema

O sistema segue uma arquitetura cliente-servidor simples:

- **Frontend (React)**: Responsável pela interface do usuário, renderização de escalas, e interação com QR codes.
- **Backend (Flask)**: API RESTful para lógica de negócio, autenticação, e persistência de dados.
- **Banco de Dados (SQLite)**: Armazenamento de usuários, escalas, registros de presença.

### Fluxo de Uso Típico

#### Acesso Inicial
1. **Compartilhamento:** Administrador compartilha o link público (ex.: via WhatsApp) gerado pelo ngrok.
2. **Abertura da Página:** Usuário acessa a URL. A interface se adapta:
   - **Desktop:** Exibe QR code com instrução "Escaneie o QR Code ou clique para registrar presença".
   - **Mobile:** Exibe botões "Check-in" e "Check-out" diretamente (sem QR).

#### Autenticação e Registro
3. **Interação Inicial:**
   - Desktop: Escaneia QR ou clica na imagem.
   - Mobile: Clica em "Check-in" ou "Check-out".
4. **Modal de CPF:** Abre modal solicitando CPF (11 dígitos, campo otimizado para mobile).
5. **Validação:**
   - Sistema verifica se CPF existe no banco.
   - Se **não existe**: Exibe formulário adicional para nome e CRM (opcional), registra usuário e realiza check-in automático.
   - Se **existe**: Para desktop/mobile sem ação pré-definida, exibe botões "Check-in" e "Check-out". Para mobile com botão clicado, executa a ação diretamente.

#### Check-in/Check-out
6. **Restrições:** Permite apenas 1 check-in por período de 12 horas (7h-19h ou 19h-7h). Se tentar novamente no mesmo período, exibe erro.
7. **Execução:** Registra horário em timezone America/Sao_Paulo, calcula horas trabalhadas automaticamente.
8. **Feedback:** Modal fecha com mensagem de sucesso, lista de presenças é atualizada.

#### Relatórios
9. **Usuário Logado:** Seção "Meu Relatório" fica visível, permitindo gerar relatórios semanais ou mensais (tabela com check-in, check-out, horas), com opção de impressão.
10. **Administrador:** Link no rodapé (visível apenas para não-logados) leva a painel admin com login (admin/admin, força troca de senha). Gera relatórios gerais/diários/mensais por usuário, com filtros e impressão.

#### Segurança e Logout
11. **Admin:** Logout limpa sessão.
12. **Usuário:** Não há logout explícito; sessão implícita via CPF validado.

O sistema garante praticidade, segurança e conformidade com horários hospitalares.

## Esquema do Banco de Dados

O banco de dados SQLite será estruturado com as seguintes tabelas principais:

### Tabela: users
- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- email (TEXT UNIQUE NOT NULL)
- cpf (TEXT UNIQUE)
- crm (TEXT)
- role (TEXT: 'plantonista', 'rotina')
- password (TEXT)  # Hash para senha padrão
- created_at (DATETIME DEFAULT CURRENT_TIMESTAMP)

### Tabela: shifts
- id (INTEGER PRIMARY KEY)
- date (DATE NOT NULL)
- type (TEXT: 'day_shift', 'night_shift', 'routine')
- nurse_group (TEXT: '3-4', '5-6')  # Para enfermeiras específicas
- assigned_users (TEXT)  # JSON array de user_ids
- created_at (DATETIME DEFAULT CURRENT_TIMESTAMP)

### Tabela: attendance
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER REFERENCES users(id))
- shift_id (INTEGER REFERENCES shifts(id))
- check_in (DATETIME)
- check_out (DATETIME)
- qr_code (TEXT)  # Hash do QR usado
- hours_worked (REAL)  # Calculado automaticamente
- created_at (DATETIME DEFAULT CURRENT_TIMESTAMP)



Este esquema permite rastreabilidade completa e cálculos precisos de horas trabalhadas.

## Endpoints da API (Flask)

### Autenticação
- POST /api/auth/validate_cpf: Validar CPF existente (retorna se existe e user_id).
- POST /api/auth/register_cpf: Registrar novo usuário via CPF (dados: cpf, name, crm opcional).

### Escalas
- GET /api/shifts: Listar escalas (com filtros por data).
- POST /api/shifts: Criar nova escala.
- PUT /api/shifts/{id}: Editar escala existente.
- DELETE /api/shifts/{id}: Remover escala.

### Presença
- POST /api/attendance/checkin: Registrar check-in (dados: user_id, shift_id=1).
- POST /api/attendance/checkout: Registrar check-out (dados: attendance_id do último check-in aberto).
- GET /api/attendance: Listar todas as presenças (usado para relatórios).

### Relatórios
- GET /api/reports/daily: Relatório diário.
- GET /api/reports/monthly: Relatório mensal.
- GET /api/reports/export: Exportar relatório (PDF/Excel).

Todos os endpoints retornarão JSON, com códigos de status HTTP apropriados.

## Frontend (SPA Hardcoded)

O frontend é uma Single Page Application (SPA) simples, implementada em HTML/CSS/JS puro, servida diretamente pelo Flask. Inclui:

- **Página Principal**: Exibe QR code, modal para CPF, lista de presenças.
- **Interatividade**: JavaScript para validação de CPF, registro e check-in via fetch() para a API.
- **Design**: Responsivo, mobile-first, sem dependências externas.

## Configuração e Desenvolvimento

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- Git

### Instalação
1. Clone o repositório: `git clone <url> && cd hercruz-presenca`
2. Configure ambiente: `source .venv/bin/activate` (se venv existir) ou instale globalmente.
3. Instale dependências: `~/.local/bin/uv pip install -r backend/requirements.txt`
4. Execute o app: `python backend/app.py`
5. Para público: `ngrok http 5000` e use a URL gerada.
6. Acesse a URL para testar (desktop: QR; mobile: botões).

### Estrutura de Diretórios
```
hercruz-presenca/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── requirements.txt
│   └── hercruz.db  # Banco de dados SQLite
├── templates/
│   └── index.html  # SPA hardcoded
├── static/  # Arquivos estáticos (se necessário)
├── instance/
├── README.md
└── install_ngrok.sh
```

### Testes
- Backend: `pytest` (se configurado).
- Manual: Acesse local/ngrok, teste check-in/check-out, relatórios, admin.

### Deploy
- Local: `python backend/app.py`
- Público: `ngrok http 5000` + compartilhe URL.
- Produção: Use Gunicorn/Nginx, configure domínio, certifique HTTPS.

## Status Atual

O sistema está totalmente implementado: SPA hardcoded com Flask, autenticação CPF, check-in/check-out com restrições, relatórios pessoais/admin, adaptação mobile/desktop. Pronto para uso via ngrok ou deploy dedicado.

## Considerações de Segurança

- Use HTTPS em produção (ngrok fornece automaticamente).
- Validação de entrada (CPF 11 dígitos, etc.).
- Hashes de senha para admin.
- Sessões Flask para controle de acesso.
- Restrições de horário para prevenir check-ins excessivos.
- Limitação de tentativas pode ser adicionada futuramente.

## Melhorias Futuras

- Notificações push ou lembretes.
- Exportação de relatórios para PDF/Excel.
- Integração com sistemas hospitalares (HL7).
- Autenticação multi-fator para admin.
- PWA para offline.

## Contribuição

1. Fork o projeto.
2. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request.

## Licença

Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.

---

Este README detalha completamente o projeto Hercruz Presença, permitindo que qualquer desenvolvedor, incluindo futuras sessões do assistente, compreenda e continue o desenvolvimento de forma independente. Com aproximadamente 1800 palavras, cobre todos os aspectos essenciais do projeto, desde a motivação até a implementação técnica.