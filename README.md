# 🤖 JOÃOZINHO STORE BOT

Bot completo para WhatsApp e Telegram com sistema de vendas, administração e pagamentos PIX automáticos.

## ✨ Funcionalidades

### 🛍️ Sistema de Vendas
- Catálogo de produtos com preços e estoque
- Sistema de carrinho e compras
- Entrega automática de produtos digitais
- Histórico de compras detalhado

### 💰 Sistema de Pagamentos
- Geração automática de PIX
- QR Code para pagamento
- Validação automática de pagamentos
- Sistema de saldo e recargas

### 👥 Sistema de Usuários
- Cadastro automático de usuários
- Sistema de afiliados com comissões
- Perfis personalizados
- Rankings e estatísticas

### 🔧 Sistema de Administração
- Painel completo de administração
- Gerenciamento de produtos
- Configurações do bot
- Estatísticas e relatórios

### 📱 Multiplataforma
- Bot do Telegram completo
- Bot do WhatsApp via CallMeBot
- Interface web para administração
- Sincronização entre plataformas

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- SQLite3
- Conta no Telegram (para bot)
- Conta no WhatsApp (para CallMeBot)

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd joaozinho-store-bot
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis
Edite o arquivo `config.py` com suas informações:

```python
# Tokens dos bots
TELEGRAM_BOT_TOKEN = "seu_token_aqui"
TELEGRAM_ADMIN_TOKEN = "seu_token_aqui"

# CallMeBot API
CALLMEBOT_API_KEY = "sua_api_key_aqui"
CALLMEBOT_PHONE = "seu_numero_aqui"

# ID do administrador
ADMIN_ID = seu_id_telegram_aqui
```

### 4. Execute o bot
```bash
python main.py
```

## 📋 Configuração

### Bot do Telegram
1. Crie um bot no @BotFather
2. Copie o token e cole em `config.py`
3. Configure o webhook se necessário

### CallMeBot (WhatsApp)
1. Acesse [CallMeBot](https://www.callmebot.com/)
2. Conecte seu WhatsApp
3. Copie a API key e cole em `config.py`

### Banco de Dados
O bot cria automaticamente um banco SQLite com:
- Tabela de usuários
- Tabela de produtos
- Tabela de transações
- Tabela de compras
- Tabela de configurações

## 🎯 Comandos Disponíveis

### Comandos do Usuário
- `/start` - Menu principal
- `/pix [valor]` - Gerar PIX para recarga
- `/historico` - Histórico de compras
- `/afiliados` - Informações de afiliado
- `/id` - Seu ID único
- `/ranking` - Rankings diversos
- `/alertas` - Configurar alertas

### Comandos de Administração
- `/admin` - Painel de administração
- `/addproduct` - Adicionar produto
- `/editproduct` - Editar produto
- `/config` - Configurações do bot

## 🔧 Funcionalidades de Administração

### Gerenciamento de Produtos
- Adicionar novos produtos
- Editar preços e descrições
- Gerenciar estoque
- Ativar/desativar produtos

### Configurações do Bot
- Nome do bot
- Número de suporte
- Links de grupo
- Limites de recarga
- Comissões de afiliados

### Estatísticas
- Total de usuários
- Vendas realizadas
- Produtos mais vendidos
- Rankings de usuários

## 💡 Como Usar

### Para Usuários
1. Inicie o bot com `/start`
2. Navegue pelos menus usando os botões
3. Faça recargas via PIX
4. Compre produtos digitais
5. Receba acesso instantâneo

### Para Administradores
1. Use `/admin` para acessar o painel
2. Gerencie produtos e configurações
3. Monitore vendas e usuários
4. Configure comissões e afiliados

## 🔒 Segurança

- Sistema de flood protection
- Validação de pagamentos
- Controle de acesso administrativo
- Logs detalhados de todas as ações

## 📊 Monitoramento

O bot inclui:
- Logs detalhados em `bot.log`
- Endpoint de saúde em `/health`
- Estatísticas em tempo real
- Notificações automáticas

## 🚨 Solução de Problemas

### Bot não inicia
- Verifique se todas as dependências estão instaladas
- Confirme se os tokens estão corretos
- Verifique os logs em `bot.log`

### PIX não funciona
- Confirme se o gerador de PIX está configurado
- Verifique se o banco de dados foi criado
- Teste com valores pequenos primeiro

### WhatsApp não responde
- Verifique se o CallMeBot está ativo
- Confirme se a API key está correta
- Teste enviando uma mensagem manual

## 🔄 Atualizações

Para atualizar o bot:
```bash
git pull origin main
pip install -r requirements.txt
python main.py
```

## 📞 Suporte

Para suporte técnico:
- Telegram: @seu_usuario
- WhatsApp: +55 44 99831-2326
- Email: suporte@seudominio.com

## 📄 Licença

Este projeto é de uso exclusivo e não pode ser redistribuído sem autorização.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

---

**Desenvolvido com ❤️ para facilitar suas vendas digitais!**