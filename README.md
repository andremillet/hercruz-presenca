# Hercruz Presença - Sistema de Gerenciamento de Presença Médica

## Visão Geral do Projeto

O projeto Hercruz Presença é uma aplicação web desenvolvida para facilitar o gerenciamento de presença de profissionais de saúde em um ambiente hospitalar. Inspirado nas mensagens de grupo do WhatsApp utilizadas atualmente para controlar escalas de plantão e rotinas, este sistema visa substituir o processo manual de "cópia e cola" por uma solução automatizada, eficiente e segura.

O sistema permite que enfermeiras e outros profissionais façam check-in e check-out de suas jornadas de trabalho através de códigos QR gerados dinamicamente, com validade de 12 horas, e autenticação via passkey (WebAuthn), garantindo segurança e praticidade, especialmente em dispositivos móveis.

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

O objetivo do Hercruz Presença é digitalizar esse processo, diferenciando entre dois tipos principais de trabalho:

- **Plantonista**: Profissionais em plantão, com carga horária de 12 horas, divididos em diurno e noturno.
- **Rotina**: Profissionais em jornada padrão, com carga horária de 8 horas.

## Stack Tecnológica

### Backend
- **Linguagem**: Python 3.8+
- **Framework**: Flask (para API RESTful)
- **Banco de Dados**: SQLite (para simplicidade e facilidade de desenvolvimento local)
- **Autenticação**: WebAuthn (passkeys) para login seguro
- **Geração de QR**: Biblioteca qrcode (Python)

### Frontend
- **Framework**: React 18+ (com hooks e componentes funcionais)
- **Linguagem**: JavaScript (ES6+)
- **Styling**: Tailwind CSS (para responsividade e design mobile-first)
- **HTTP Client**: Axios (para comunicação com API)
- **Roteamento**: React Router

### Outras Ferramentas
- **Controle de Versão**: Git
- **Gerenciamento de Dependências**: pip (backend), npm (frontend)
- **Testes**: pytest (backend), Jest (frontend)
- **Linting**: ESLint (frontend), flake8 (backend)
- **Documentação**: Este README, com planos para Swagger/OpenAPI

## Funcionalidades Principais

### 1. Autenticação Segura
- Login via passkey (WebAuthn), compatível com dispositivos móveis e desktops.
- Geração de códigos QR únicos por sessão, válidos por 12 horas.
- Suporte a múltiplos dispositivos por usuário.

### 2. Gerenciamento de Escalas
- Criação e edição de escalas diárias/semanal/mensal.
- Atribuição de profissionais a turnos: Plantão Diurno, Plantão Noturno, Rotina.
- Diferenciação automática de carga horária (12h para plantonista, 8h para rotina).

### 3. Check-in/Check-out
- Interface mobile-friendly para check-in via QR code.
- Registro automático de horários de entrada e saída.
- Validação de turnos para evitar sobreposições ou ausências.

### 4. Relatórios e Analytics
- Geração de relatórios de presença por período.
- Cálculo de horas trabalhadas, incluindo extras.
- Exportação para PDF ou Excel.

### 5. Notificações
- Alertas para escalas incompletas.
- Lembretes de check-in/check-out.
- Notificações push (futuro: integração com PWA).

### 6. Administração
- Painel para administradores criarem/editarem escalas.
- Gerenciamento de usuários (adicionar/remover profissionais).
- Logs de auditoria para mudanças.

## Arquitetura do Sistema

O sistema segue uma arquitetura cliente-servidor simples:

- **Frontend (React)**: Responsável pela interface do usuário, renderização de escalas, e interação com QR codes.
- **Backend (Flask)**: API RESTful para lógica de negócio, autenticação, e persistência de dados.
- **Banco de Dados (SQLite)**: Armazenamento de usuários, escalas, registros de presença.

### Fluxo de Uso Típico
1. Administrador cria escala para o dia via painel web.
2. Profissional acessa app web em dispositivo móvel.
3. Faz login via passkey.
4. Escaneia QR code gerado (válido 12h).
5. Registra check-in/check-out automaticamente.
6. Sistema calcula horas e atualiza relatórios.

## Esquema do Banco de Dados

O banco de dados SQLite será estruturado com as seguintes tabelas principais:

### Tabela: users
- id (INTEGER PRIMARY KEY)
- name (TEXT NOT NULL)
- email (TEXT UNIQUE NOT NULL)
- role (TEXT: 'admin', 'plantonista', 'rotina')
- passkey_credential (TEXT)  # Armazenamento seguro de credenciais WebAuthn
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

### Tabela: qr_codes
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER REFERENCES users(id))
- code (TEXT UNIQUE)  # Código QR gerado
- expires_at (DATETIME)  # Validade de 12 horas
- used (BOOLEAN DEFAULT FALSE)
- created_at (DATETIME DEFAULT CURRENT_TIMESTAMP)

Este esquema permite rastreabilidade completa e cálculos precisos de horas trabalhadas.

## Endpoints da API (Flask)

### Autenticação
- POST /api/auth/register: Registrar novo usuário com passkey.
- POST /api/auth/login: Login via passkey.
- POST /api/auth/qr/generate: Gerar QR code para sessão.
- POST /api/auth/qr/validate: Validar QR code escaneado.

### Escalas
- GET /api/shifts: Listar escalas (com filtros por data).
- POST /api/shifts: Criar nova escala.
- PUT /api/shifts/{id}: Editar escala existente.
- DELETE /api/shifts/{id}: Remover escala.

### Presença
- POST /api/attendance/checkin: Registrar check-in.
- POST /api/attendance/checkout: Registrar check-out.
- GET /api/attendance/{user_id}: Histórico de presença do usuário.

### Relatórios
- GET /api/reports/daily: Relatório diário.
- GET /api/reports/monthly: Relatório mensal.
- GET /api/reports/export: Exportar relatório (PDF/Excel).

Todos os endpoints retornarão JSON, com códigos de status HTTP apropriados.

## Componentes do Frontend (React)

### Estrutura de Pastas
```
src/
├── components/
│   ├── Auth/
│   │   ├── LoginForm.js
│   │   ├── QRScanner.js
│   │   └── PasskeySetup.js
│   ├── Dashboard/
│   │   ├── ShiftList.js
│   │   ├── AttendanceForm.js
│   │   └── ReportView.js
│   └── Admin/
│       ├── ShiftEditor.js
│       └── UserManager.js
├── pages/
│   ├── Home.js
│   ├── AdminPanel.js
│   └── Profile.js
├── services/
│   ├── api.js  # Axios instance
│   └── auth.js
├── hooks/
│   ├── useAuth.js
│   └── useShifts.js
├── utils/
│   ├── qrUtils.js
│   └── dateUtils.js
└── App.js
```

### Componentes Chave
- **QRScanner**: Usa biblioteca como react-qr-scanner para escanear códigos.
- **ShiftList**: Exibe escalas em formato de lista/calendário responsivo.
- **AttendanceForm**: Formulário simples para check-in/out.
- **ShiftEditor**: Interface drag-and-drop para criar escalas.

## Configuração e Desenvolvimento

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- Git

### Instalação
1. Clone o repositório: `git clone <url> && cd hercruz-presenca`
2. Backend:
   - `cd backend`
   - `python -m venv venv`
   - `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
   - `pip install -r requirements.txt`
   - `flask run`
3. Frontend:
   - `cd frontend`
   - `npm install`
   - `npm start`

### Estrutura de Diretórios
```
hercruz-presenca/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   ├── requirements.txt
│   └── config.py
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── tailwind.config.js
├── docs/
├── tests/
└── README.md
```

### Testes
- Backend: `pytest`
- Frontend: `npm test`

### Deploy
- Backend: Gunicorn + Nginx
- Frontend: Build com `npm run build`, servir estático ou via CDN.

## Plano de Desenvolvimento

### Fase 1: MVP (1-2 semanas)
- Configurar projeto base (Flask + React).
- Implementar autenticação básica (sem passkey inicialmente).
- Criar CRUD de escalas.
- Interface básica para check-in/out.

### Fase 2: Autenticação Avançada (1 semana)
- Integrar WebAuthn para passkeys.
- Geração e validação de QR codes.

### Fase 3: Funcionalidades Avançadas (2 semanas)
- Relatórios e exportação.
- Notificações.
- Otimização mobile.

### Fase 4: Testes e Deploy (1 semana)
- Testes unitários/integração.
- Deploy em servidor (Heroku, DigitalOcean).

## Considerações de Segurança

- Todas as comunicações via HTTPS.
- Credenciais WebAuthn armazenadas de forma segura.
- Validação de entrada em todos os endpoints.
- Logs de auditoria para mudanças sensíveis.
- Limitação de tentativas de login.

## Melhorias Futuras

- Integração com sistemas hospitalares existentes (HL7, FHIR).
- Suporte a PWA para notificações offline.
- IA para otimização de escalas.
- Multi-idioma (Português, Inglês).
- Integração com folha de pagamento.

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