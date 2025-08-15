# 🤖 Joãozinho Store Bot

Sistema completo de loja automatizada com integração WhatsApp e Telegram, sistema de PIX automático, afiliados e painel administrativo.

## 🚀 Características

### 📱 WhatsApp Bot (CallMeBot API)
- ✅ Sistema de mensagens automatizadas
- ✅ Controle de flood e anti-spam
- ✅ Integração com PIX automático
- ✅ Menu interativo completo
- ✅ Suporte a comandos de voz

### 🤖 Telegram Bot da Loja
- ✅ Interface com botões inline editáveis
- ✅ Sistema de produtos premium
- ✅ Carrinho de compras integrado
- ✅ Histórico de compras em PDF/TXT
- ✅ Sistema de pesquisa de produtos
- ✅ Rankings em tempo real
- ✅ Sistema de afiliados
- ✅ Alertas de reestoque

### 🛠️ Painel Administrativo (Telegram)
- ✅ Gerenciamento completo de produtos
- ✅ Controle de usuários e vendas
- ✅ Relatórios detalhados
- ✅ Configurações do sistema
- ✅ Backup automático do banco
- ✅ Broadcast para todos os usuários
- ✅ Estatísticas em tempo real

### 💰 Sistema Financeiro
- ✅ PIX automático com QR Code
- ✅ Controle de saldo de usuários
- ✅ Sistema de comissões (afiliados)
- ✅ Relatórios de vendas
- ✅ Ranking de compradores

### 🔧 Funcionalidades Técnicas
- ✅ Banco de dados SQLite
- ✅ API REST para integrações
- ✅ Webhooks para PIX e WhatsApp
- ✅ Sistema de logs detalhados
- ✅ Interface web de monitoramento

## 📋 Requisitos

- Node.js 16+ 
- NPM ou Yarn
- Conta CallMeBot (WhatsApp)
- Bot Token Telegram (2 bots necessários)

## ⚙️ Instalação

### 1. Clone o projeto
```bash
git clone <repository-url>
cd joaozinho-store-bot
```

### 2. Instale as dependências
```bash
npm install
```

### 3. Configure as variáveis de ambiente
Crie um arquivo `.env` com as configurações:

```env
# WhatsApp CallMeBot API
WHATSAPP_PHONE=5544998312326
WHATSAPP_API_KEY=8334846
CALLMEBOT_API_URL=https://api.callmebot.com/whatsapp.php

# Telegram Bot Tokens
TELEGRAM_STORE_BOT_TOKEN=SEU_TOKEN_BOT_LOJA
TELEGRAM_ADMIN_BOT_TOKEN=SEU_TOKEN_BOT_ADMIN

# Admin Settings
ADMIN_TELEGRAM_ID=8206910765
STORE_NAME=JOÃOZINHO STORE BOT
WHATSAPP_GROUP_URL=https://chat.whatsapp.com/EAMz3pt1kPe9VPO9rK8ccF

# PIX Settings
PIX_PROVIDER=EAFI
PIX_MERCHANT_ID=EFISA
PIX_MERCHANT_CITY=SAOPAULO

# Database
DATABASE_PATH=./database.db

# Server Settings
PORT=3000
HOST=localhost

# Commission Settings
DEFAULT_COMMISSION_RATE=0.50

# Support Settings
SUPPORT_PHONE=5544998312326
SUPPORT_NAME=JOÃO
```

### 4. Inicie o sistema
```bash
npm start
```

Ou para desenvolvimento:
```bash
npm run dev
```

## 🔑 Configuração das APIs

### CallMeBot (WhatsApp)
1. Adicione o número +34 644 94 85 97 no WhatsApp
2. Envie a mensagem: `I allow callmebot to send me messages`
3. Você receberá sua API key
4. Configure no `.env`

### Telegram Bots
1. Crie 2 bots no @BotFather:
   - Um para a loja (clientes)
   - Um para administração
2. Obtenha os tokens e configure no `.env`
3. Configure o ID do administrador

## 🎯 Como Usar

### Para Clientes (WhatsApp)
1. Envie qualquer mensagem para o número configurado
2. Use os emojis para navegar:
   - 💸 Adicionar Saldo
   - 🛍️ Produtos Premium
   - 💼 Minha Conta
   - 🆘 Suporte

### Para Clientes (Telegram)
1. Inicie conversa com o bot da loja
2. Use `/start` para acessar o menu
3. Navegue pelos botões inline
4. Comandos disponíveis:
   - `/pix 10` - Gerar PIX de R$ 10
   - `/historico` - Ver compras
   - `/afiliados` - Sistema de indicação
   - `/ranking` - Rankings do sistema

### Para Administradores (Telegram)
1. Inicie conversa com o bot admin
2. Use `/start` para acessar o painel
3. Funcionalidades:
   - Gerenciar produtos
   - Ver relatórios
   - Configurar sistema
   - Fazer backup
   - Enviar mensagens em massa

## 📊 Monitoramento

Acesse `http://localhost:3000` para:
- Ver status do sistema
- Estatísticas em tempo real
- APIs de integração

### Endpoints da API
- `GET /api/status` - Status do sistema
- `GET /api/stats` - Estatísticas
- `GET /api/products` - Listar produtos
- `POST /api/products` - Criar produto
- `GET /api/rankings/:type` - Rankings
- `POST /webhook/pix` - Webhook PIX
- `POST /webhook/whatsapp` - Webhook WhatsApp

## 🛡️ Segurança

- ✅ Controle de acesso por ID
- ✅ Anti-flood com timeout progressivo
- ✅ Validação de dados de entrada
- ✅ Logs de segurança
- ✅ Rate limiting nas APIs

## 📁 Estrutura do Projeto

```
joaozinho-store-bot/
├── package.json              # Dependências e scripts
├── .env                      # Configurações (não versionar)
├── index.js                  # Arquivo principal do sistema
├── database.js               # Gerenciador do banco SQLite
├── whatsapp-bot.js          # Bot WhatsApp
├── telegram-store-bot.js    # Bot Telegram da loja
├── telegram-admin-bot.js    # Bot admin Telegram
├── database.db              # Banco SQLite (criado automaticamente)
└── README.md                # Este arquivo
```

## 🔧 Scripts Disponíveis

```bash
# Iniciar sistema completo
npm start

# Desenvolvimento com auto-reload
npm run dev

# Apenas WhatsApp bot
npm run whatsapp

# Apenas bot da loja
npm run telegram-store

# Apenas bot admin
npm run telegram-admin
```

## 💾 Backup e Restauração

### Backup Manual
```bash
# Via bot admin: Use o comando /backup
# Ou copie o arquivo database.db
```

### Restauração
```bash
# Substitua o arquivo database.db pelo backup
# Reinicie o sistema
```

## 🎨 Personalização

### Alterar Textos e Emojis
- Edite os arquivos dos bots
- Modifique as configurações no banco via admin
- Use o painel admin para mudanças em tempo real

### Adicionar Novos Produtos
- Use o bot admin
- Ou via API: `POST /api/products`

### Configurar PIX
- Configure seu provedor PIX
- Modifique o método `generatePixKey` no database.js
- Integre webhooks de confirmação

## 🔄 Atualizações

### Sistema de Versionamento
- Versão atual: 1.0.0
- Atualizações via git pull
- Backup automático recomendado

## 🐛 Solução de Problemas

### Bot não responde
1. Verifique os tokens no `.env`
2. Confirme se os bots estão ativos
3. Veja os logs no console

### Erro de banco de dados
1. Verifique permissões do arquivo
2. Restaure backup se necessário
3. Reinicie o sistema

### CallMeBot não funciona
1. Confirme a API key
2. Verifique se o número está autorizado
3. Teste com o endpoint direto

### Problemas de PIX
1. Configure seu provedor real
2. Verifique webhooks
3. Teste com valores pequenos

## 📞 Suporte

- **Desenvolvedor**: João
- **WhatsApp**: +55 44 99831-2326
- **Telegram**: Configurável no sistema

## 📄 Licença

Este projeto é privado e proprietário. Todos os direitos reservados.

## 🚀 Próximas Atualizações

- [ ] Integração com APIs de PIX reais
- [ ] Sistema de cupons de desconto
- [ ] Relatórios em PDF
- [ ] App mobile
- [ ] Dashboard web avançado
- [ ] Integração com marketplaces

---

## ⚡ Quick Start

```bash
# Clone, configure .env e rode:
npm install && npm start

# Acesse: http://localhost:3000
# Configure seus bots no Telegram
# Ative CallMeBot no WhatsApp
# Pronto! 🎉
```

**🎯 Seu sistema de loja automatizada está pronto para usar!**