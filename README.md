# Hercruz Presença - Sistema de Gerenciamento de Presença Médica

## Visão Geral do Projeto

O projeto Hercruz Presença é uma aplicação web desenvolvida para facilitar o gerenciamento de presença de profissionais de saúde em um ambiente hospitalar. Inspirado nas mensagens de grupo do WhatsApp utilizadas atualmente para controlar escalas de plantão e rotinas, este sistema visa substituir o processo manual de "cópia e cola" por uma solução automatizada, eficiente e segura.

O sistema permite que enfermeiras e outros profissionais façam check-in e check-out de suas jornadas de trabalho através de códigos QR gerados dinamicamente, com autenticação via CPF, garantindo praticidade, especialmente em dispositivos móveis.

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

### 1. Autenticação Simples
- Validação via CPF, com registro automático para novos usuários.
- Geração de códigos QR para acesso direto ao sistema.
- Interface mobile-friendly.

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
1. Profissional acessa a URL pública (via ngrok).
2. Escaneia o QR code exibido na página.
3. Digita o CPF no modal que aparece.
4. Se CPF existe, check-in automático; se não, registra-se e faz check-in.
5. Sistema calcula horas e exibe presenças registradas.

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
- POST /api/auth/validate_cpf: Validar CPF existente.
- POST /api/auth/register_cpf: Registrar novo usuário via CPF.

### Escalas
- GET /api/shifts: Listar escalas (com filtros por data).
- POST /api/shifts: Criar nova escala.
- PUT /api/shifts/{id}: Editar escala existente.
- DELETE /api/shifts/{id}: Remover escala.

### Presença
- POST /api/attendance/checkin: Registrar check-in.
- POST /api/attendance/checkout: Registrar check-out.
- GET /api/attendance: Listar todas as presenças.

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
2. Instale dependências: `pip install -r backend/requirements.txt`
3. Execute o app: `python backend/app.py`
4. Acesse http://localhost:5000 (ou via ngrok para público)

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
- Backend: `pytest`

### Deploy
- Execute `python backend/app.py` e exponha via ngrok: `ngrok http 5000`
- Para produção, use Gunicorn: `gunicorn -w 4 backend.app:app`

## Status Atual

O MVP está implementado como uma SPA hardcoded servida por Flask, com autenticação via CPF e check-in/check-out via QR. Pronto para deploy via ngrok ou servidor dedicado.

## Considerações de Segurança

- Use HTTPS em produção (ngrok fornece automaticamente).
- Validação de entrada em todos os endpoints.
- Hashes de senha para usuários registrados.
- Limitação de tentativas pode ser adicionada futuramente.

## Melhorias Futuras

- Adicionar autenticação mais robusta (ex.: senhas customizadas).
- Relatórios e exportação de dados.
- Notificações push.
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