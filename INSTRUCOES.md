# 📋 INSTRUÇÕES DE USO - JOÃOZINHO STORE BOT

## 🚀 Início Rápido

### 1. Instalação Automática (Recomendado)
```bash
chmod +x install.sh
./install.sh
```

### 2. Instalação Manual
```bash
pip install -r requirements.txt
python quick_start.py
```

### 3. Inicialização Direta
```bash
python start_bot.py
```

## 📱 Funcionalidades Principais

### 🤖 Bot do Telegram
- **Comando**: `/start` - Menu principal
- **Comando**: `/pix [valor]` - Gerar PIX para recarga
- **Comando**: `/historico` - Histórico de compras
- **Comando**: `/afiliados` - Informações de afiliado
- **Comando**: `/id` - Seu ID único
- **Comando**: `/ranking` - Rankings diversos
- **Comando**: `/alertas` - Configurar alertas

### 📱 Bot do WhatsApp
- Funciona via CallMeBot API
- Responde automaticamente a mensagens
- Sistema de flood protection
- Notificações automáticas

### 💰 Sistema de Pagamentos
- Geração automática de PIX
- QR Code para pagamento
- Validação automática
- Expiração em 30 minutos
- Sistema de saldo

### 🛍️ Sistema de Vendas
- Catálogo de produtos
- Controle de estoque
- Entrega automática
- Histórico de compras
- Sistema de garantia

## 🔧 Administração

### Painel Web
```bash
python admin_panel.py
```
- **URL**: http://localhost:5001
- **Login**: Use seu ID do Telegram (8206910765)
- **Funcionalidades**: Gerenciar produtos, usuários, configurações

### Comandos de Administração
- `/admin` - Painel de administração
- `/addproduct` - Adicionar produto
- `/editproduct` - Editar produto
- `/config` - Configurações do bot

## 📊 Monitoramento

### Logs
- **Arquivo**: `bot.log`
- **Localização**: Diretório raiz do projeto
- **Rotação**: Automática

### Status do Sistema
```bash
python quick_start.py
# Opção 4: Ver Status
```

### Backup Automático
- **Frequência**: Diário
- **Localização**: Diretório `backups/`
- **Retenção**: 30 dias

## 🧪 Testes e Demonstração

### Executar Testes
```bash
python test_bot.py
```

### Demonstração Completa
```bash
python demo.py
```

### Verificação Rápida
```bash
python quick_start.py
# Opção 3: Executar Testes
```

## ⚙️ Configuração

### Arquivo Principal
- **Arquivo**: `config.py`
- **Configurações**: Tokens, IDs, limites, comissões

### Variáveis de Ambiente
- **Arquivo**: `.env`
- **Baseado em**: `.env.example`

### Configurações Importantes
- `ADMIN_ID`: 8206910765 (seu ID)
- `TELEGRAM_BOT_TOKEN`: Token do @BotFather
- `CALLMEBOT_API_KEY`: API key do CallMeBot
- `CALLMEBOT_PHONE`: Seu número do WhatsApp

## 🔄 Manutenção

### Reiniciar Bot
```bash
# Parar processo atual
Ctrl+C

# Iniciar novamente
python start_bot.py
```

### Atualizar Produtos
1. Acesse painel de administração
2. Vá em "Produtos"
3. Adicione/edite produtos
4. Salve alterações

### Backup Manual
```bash
python backup_system.py
```

### Limpeza de Logs
```bash
# Logs são rotacionados automaticamente
# Para limpeza manual, delete arquivos antigos em logs/
```

## 🚨 Solução de Problemas

### Bot não inicia
1. Verifique se Python 3.8+ está instalado
2. Execute: `pip install -r requirements.txt`
3. Verifique arquivo `config.py`
4. Execute: `python test_bot.py`

### PIX não funciona
1. Verifique configurações em `config.py`
2. Confirme se banco de dados foi criado
3. Teste com valores pequenos primeiro
4. Verifique logs em `bot.log`

### WhatsApp não responde
1. Verifique se CallMeBot está ativo
2. Confirme API key em `config.py`
3. Teste enviando mensagem manual
4. Verifique logs do sistema

### Erro de banco de dados
1. Verifique permissões do diretório
2. Execute: `python test_bot.py`
3. Verifique se SQLite3 está instalado
4. Delete arquivo `store_bot.db` para recriar

## 📁 Estrutura de Arquivos

```
joaozinho-store-bot/
├── start_bot.py          # Inicialização principal
├── quick_start.py        # Inicialização rápida
├── telegram_bot.py       # Bot do Telegram
├── whatsapp_bot.py       # Bot do WhatsApp
├── database.py           # Sistema de banco
├── pix_generator.py      # Gerador de PIX
├── notification_system.py # Sistema de notificações
├── backup_system.py      # Sistema de backup
├── admin_panel.py        # Painel de administração
├── config.py             # Configurações
├── requirements.txt      # Dependências
├── test_bot.py          # Testes
├── demo.py              # Demonstração
├── install.sh           # Script de instalação
├── README.md            # Documentação
├── INSTRUCOES.md        # Este arquivo
├── qr_codes/            # QR Codes gerados
├── logs/                # Arquivos de log
├── backups/             # Backups automáticos
└── data/                # Dados do sistema
```

## 🔐 Segurança

### Controle de Acesso
- Apenas administradores podem usar comandos `/admin`
- Sistema de flood protection ativo
- Logs de todas as ações administrativas

### Dados Sensíveis
- Tokens armazenados em `config.py`
- Banco de dados local (SQLite)
- Backups automáticos criptografados

## 📞 Suporte

### Contatos
- **Telegram**: @seu_usuario
- **WhatsApp**: +55 44 99831-2326
- **Email**: suporte@seudominio.com

### Documentação
- **README.md**: Visão geral completa
- **demo.py**: Demonstração interativa
- **test_bot.py**: Testes automatizados

## 🎯 Próximos Passos

1. ✅ Configure `config.py` com suas credenciais
2. ✅ Execute `python quick_start.py` para verificação
3. ✅ Inicie o bot com `python start_bot.py`
4. ✅ Acesse painel admin em http://localhost:5001
5. ✅ Configure produtos e preços
6. ✅ Teste funcionalidades com usuários
7. ✅ Monitore logs e estatísticas
8. ✅ Configure backup automático

## 🎉 Sucesso!

Se você chegou até aqui, o bot está funcionando perfeitamente! 

**Funcionalidades ativas:**
- ✅ Bot do Telegram funcionando
- ✅ Bot do WhatsApp funcionando
- ✅ Sistema de PIX automático
- ✅ Sistema de vendas completo
- ✅ Painel de administração
- ✅ Backup automático
- ✅ Monitoramento em tempo real

**Próximo passo:** Comece a vender seus produtos digitais! 🚀