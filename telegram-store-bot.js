const TelegramBot = require('node-telegram-bot-api');
const db = require('./database');
const moment = require('moment');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

class TelegramStoreBot {
    constructor() {
        this.token = process.env.TELEGRAM_STORE_BOT_TOKEN;
        this.bot = new TelegramBot(this.token, { polling: true });
        this.userStates = new Map();
        this.setupHandlers();
        this.setupCommands();
    }

    setupCommands() {
        // Comandos do bot
        this.bot.setMyCommands([
            { command: 'start', description: '🚀 Iniciar o bot' },
            { command: 'pix', description: '💰 Gerar PIX para recarga' },
            { command: 'historico', description: '📋 Histórico de compras' },
            { command: 'afiliados', description: '👥 Sistema de afiliados' },
            { command: 'id', description: '🆔 Mostrar seu ID' },
            { command: 'ranking', description: '🏆 Ver rankings' },
            { command: 'alertas', description: '🔔 Gerenciar alertas de produtos' }
        ]);
    }

    setupHandlers() {
        // Handler para /start
        this.bot.onText(/\/start(.*)/, async (msg, match) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            const username = msg.from.username || msg.from.first_name;
            const affiliateCode = match[1] ? match[1].trim() : null;

            await this.handleStart(chatId, userId, username, affiliateCode);
        });

        // Handler para comandos específicos
        this.bot.onText(/\/pix (.+)/, async (msg, match) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            const amount = parseFloat(match[1]);

            if (isNaN(amount) || amount < 1) {
                await this.bot.sendMessage(chatId, `❌ Você enviou em um formato incorreto. Envie /pix e o valor que deseja...

*Exemplo:*
/pix 10
/pix 6.26`, { parse_mode: 'Markdown' });
                return;
            }

            await this.generatePixForUser(chatId, userId, amount);
        });

        // Handler para /pix sem valor
        this.bot.onText(/^\/pix$/, async (msg) => {
            const chatId = msg.chat.id;
            await this.bot.sendMessage(chatId, `❌ Você enviou em um formato incorreto. Envie /pix e o valor que deseja...

*Exemplo:*
/pix 10
/pix 6.26`, { parse_mode: 'Markdown' });
        });

        // Handler para /historico
        this.bot.onText(/\/historico/, async (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            await this.sendUserHistory(chatId, userId);
        });

        // Handler para /afiliados
        this.bot.onText(/\/afiliados/, async (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            await this.showAffiliateInfo(chatId, userId);
        });

        // Handler para /id
        this.bot.onText(/\/id/, async (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            await this.bot.sendMessage(chatId, `🆔 *Seu id é:* \`${userId}\``, { parse_mode: 'Markdown' });
        });

        // Handler para /ranking
        this.bot.onText(/\/ranking/, async (msg) => {
            const chatId = msg.chat.id;
            await this.showRankingMenu(chatId);
        });

        // Handler para /alertas
        this.bot.onText(/\/alertas/, async (msg) => {
            const chatId = msg.chat.id;
            const userId = msg.from.id;
            await this.showProductAlerts(chatId, userId);
        });

        // Handler para callback queries (botões inline)
        this.bot.on('callback_query', async (query) => {
            await this.handleCallbackQuery(query);
        });

        // Handler para mensagens de texto (pesquisa)
        this.bot.on('message', async (msg) => {
            if (msg.text && !msg.text.startsWith('/')) {
                await this.handleTextMessage(msg);
            }
        });
    }

    async handleStart(chatId, userId, username, affiliateCode = null) {
        try {
            // Criar ou buscar usuário
            let user = await db.getUserByTelegramId(userId.toString());
            if (!user) {
                await db.createUser(userId.toString(), username);
                user = await db.getUserByTelegramId(userId.toString());
            }

            const storeName = await db.getConfig('store_name') || 'JOÃOZINHO STORE BOT';
            const storeImage = await db.getConfig('store_logo');
            const whatsappGroup = await db.getConfig('whatsapp_group');
            const supportPhone = await db.getConfig('support_phone');

            const welcomeText = `🥇*Descubra como nosso bot pode transformar sua experiência de compras!*
Ele facilita a busca por diversos produtos e serviços, garantindo que você encontre o que precisa com o melhor preço e excelente custo-benefício.

*Importante:* Não realizamos reembolsos em dinheiro. O suporte estará disponível por até 48 horas após a entrega das informações, com reembolso em créditos no bot, se necessário.

👥*Grupo De Clientes:* ${whatsappGroup}

👨‍💻 *Link De Suporte:* https://t.me/${this.bot.options.username}

ℹ️*Seus Dados:*
🆔*ID:* ${userId}
💸*Saldo Atual:* R$ ${user.balance.toFixed(2)}
🪪*Usuário:* @${username}`;

            const keyboard = {
                inline_keyboard: [
                    [{ text: '💎  Logins | Contas Premium', callback_data: 'premium_logins' }],
                    [
                        { text: '🪪 PERFIL', callback_data: 'profile' },
                        { text: '💰 RECARGA', callback_data: 'recharge' }
                    ],
                    [{ text: '🎖️ Ranking', callback_data: 'ranking' }],
                    [
                        { text: '👩‍💻 Suporte', callback_data: 'support' },
                        { text: 'ℹ️ Informações', callback_data: 'info' }
                    ],
                    [{ text: '🔎 Pesquisar Serviços', callback_data: 'search_services' }]
                ]
            };

            if (storeImage) {
                await this.bot.sendPhoto(chatId, storeImage, {
                    caption: welcomeText,
                    parse_mode: 'Markdown',
                    reply_markup: keyboard
                });
            } else {
                await this.bot.sendMessage(chatId, welcomeText, {
                    parse_mode: 'Markdown',
                    reply_markup: keyboard
                });
            }

        } catch (error) {
            console.error('Erro no /start:', error);
            await this.bot.sendMessage(chatId, '❌ Erro interno. Tente novamente.');
        }
    }

    async handleCallbackQuery(query) {
        const chatId = query.message.chat.id;
        const userId = query.from.id;
        const data = query.data;
        const messageId = query.message.message_id;

        try {
            await this.bot.answerCallbackQuery(query.id);

            switch (data) {
                case 'premium_logins':
                    await this.showPremiumProducts(chatId, messageId, userId);
                    break;
                case 'profile':
                    await this.showUserProfile(chatId, messageId, userId);
                    break;
                case 'recharge':
                    await this.showRechargeMenu(chatId, messageId, userId);
                    break;
                case 'ranking':
                    await this.showRankingMenu(chatId, messageId);
                    break;
                case 'support':
                    await this.showSupportInfo(chatId, messageId);
                    break;
                case 'info':
                    await this.showBotInfo(chatId, messageId);
                    break;
                case 'search_services':
                    await this.initiateSearch(chatId, messageId);
                    break;
                case 'back_main':
                    await this.handleStart(chatId, userId, query.from.username || query.from.first_name);
                    await this.bot.deleteMessage(chatId, messageId);
                    break;
                case 'pushin_pay':
                    await this.showPushinPayMenu(chatId, messageId, userId);
                    break;
                case 'purchase_history':
                    await this.sendUserHistory(chatId, userId);
                    break;
                default:
                    if (data.startsWith('product_')) {
                        const productId = data.split('_')[1];
                        await this.showProductDetails(chatId, messageId, userId, productId);
                    } else if (data.startsWith('buy_')) {
                        const productId = data.split('_')[1];
                        await this.processPurchase(chatId, messageId, userId, productId);
                    } else if (data.startsWith('ranking_')) {
                        const type = data.split('_')[1];
                        await this.showSpecificRanking(chatId, messageId, type);
                    }
                    break;
            }
        } catch (error) {
            console.error('Erro no callback query:', error);
            await this.bot.answerCallbackQuery(query.id, { text: '❌ Erro interno' });
        }
    }

    async showPremiumProducts(chatId, messageId, userId) {
        const user = await db.getUserByTelegramId(userId.toString());
        const products = await db.getAllProducts();

        if (products.length === 0) {
            await this.createSampleProducts();
        }

        const updatedProducts = await db.getAllProducts();
        
        let text = `🎟️ *Logins Premium | Acesso Exclusivo*

🏦 *Carteira*
💸 *Saldo Atual:* R$ ${user.balance.toFixed(2)}

📱 *PRODUTOS DISPONÍVEIS:*`;

        const keyboard = { inline_keyboard: [] };
        
        updatedProducts.forEach(product => {
            keyboard.inline_keyboard.push([{
                text: `${product.name} - R$ ${product.price.toFixed(2)}`,
                callback_data: `product_${product.id}`
            }]);
        });

        keyboard.inline_keyboard.push([{ text: '↩️ Voltar', callback_data: 'back_main' }]);

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showProductDetails(chatId, messageId, userId, productId) {
        const user = await db.getUserByTelegramId(userId.toString());
        const product = await db.getProductById(productId);

        if (!product) {
            await this.bot.answerCallbackQuery(query.id, { text: '❌ Produto não encontrado' });
            return;
        }

        const text = `⚜️*ACESSO: ${product.name}* ⚜️

💵 *Preço:* R$ ${product.price.toFixed(2)}
💼 *Saldo Atual:* R$ ${user.balance.toFixed(2)}
📥 *Estoque Disponível:* ${product.stock}

🗒️ *Descrição:* ${product.description || 'Aviso Importante: O acesso é disponibilizado na hora. Não atendemos ligações nem ouvimos mensagens de áudio; pedimos que aguarde sua vez. Informamos que não realizamos reembolsos via Pix, apenas em créditos no bot, correspondendo aos dias restantes até o vencimento. Agradecemos pela compreensão e desejamos boas compras!'}

♻️ *Garantia:* ${product.guarantee_days || 30} dias`;

        const keyboard = {
            inline_keyboard: [
                [{ text: '🛒 Comprar', callback_data: `buy_${product.id}` }],
                [{ text: '↩️ Voltar', callback_data: 'premium_logins' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async processPurchase(chatId, messageId, userId, productId) {
        const user = await db.getUserByTelegramId(userId.toString());
        const product = await db.getProductById(productId);

        if (!product) {
            await this.bot.answerCallbackQuery(query.id, { text: '❌ Produto não encontrado' });
            return;
        }

        if (user.balance < product.price) {
            const shortage = product.price - user.balance;
            await this.bot.answerCallbackQuery(query.id, {
                text: `❌ Saldo insuficiente! Faltam R$ ${shortage.toFixed(2)}. Faça uma recarga e tente novamente. Seu saldo: R$ ${user.balance.toFixed(2)}`,
                show_alert: true
            });
            return;
        }

        if (product.stock <= 0) {
            await this.bot.answerCallbackQuery(query.id, {
                text: '❌ Produto fora de estoque!',
                show_alert: true
            });
            return;
        }

        // Processar compra
        await db.updateUserBalance(user.id, product.price, 'subtract');
        await db.updateProductStock(product.id, 1, 'subtract');
        await db.createPurchase(user.id, product.id, product.price);

        // Gerar dados de acesso (simulado)
        const accessData = this.generateAccessData(product.name);

        const successText = `✅ *Compra Realizada com Sucesso!*

🎉 *Produto:* ${product.name}
💰 *Valor:* R$ ${product.price.toFixed(2)}
💼 *Saldo Restante:* R$ ${(user.balance - product.price).toFixed(2)}

📧 *Dados de Acesso:*
${accessData}

*Importante:* Guarde bem esses dados! O suporte estará disponível por 48 horas.`;

        await this.bot.editMessageText(successText, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Voltar ao Menu', callback_data: 'back_main' }]]
            }
        });

        // Atualizar ranking
        await this.updateUserRanking(user.id, user.username, 'purchases', 1);
    }

    generateAccessData(productName) {
        // Simular geração de dados de acesso
        const email = `user${Math.floor(Math.random() * 10000)}@example.com`;
        const password = Math.random().toString(36).substr(2, 8);
        
        return `📧 *Email:* ${email}
🔐 *Senha:* ${password}

📱 *Instruções:*
1. Baixe o app na App Store ou Google Play
2. Faça login com os dados acima
3. Aproveite seu ${productName}!`;
    }

    async showUserProfile(chatId, messageId, userId) {
        const user = await db.getUserByTelegramId(userId.toString());
        const purchases = await db.getUserPurchases(user.id);

        const text = `🙋‍♂️ *Meu perfil*

🔎 *Veja aqui os detalhes da sua conta:*

👤 *Informações:*
🆔 *ID da Carteira:* ${userId}
💰 *Saldo Atual:* R$ ${user.balance.toFixed(2)}

📊 *Suas movimentações:*
—🛒 *Compras Realizadas:* ${purchases.length}
—💠 *Pix Inseridos:* 0
—🎁 *Gifts Resgatados:* R$ 0.00`;

        const keyboard = {
            inline_keyboard: [
                [{ text: '🛍️ Historico De Compras', callback_data: 'purchase_history' }],
                [{ text: '↩️ Voltar', callback_data: 'back_main' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showRechargeMenu(chatId, messageId, userId) {
        const user = await db.getUserByTelegramId(userId.toString());

        const text = `💼 *ID da Carteira:* ${userId}
💵 *Saldo Disponível:* R$ ${user.balance.toFixed(2)}

💡*Selecione uma opção para recarregar:*`;

        const keyboard = {
            inline_keyboard: [
                [{ text: 'PUSHIN PAY', callback_data: 'pushin_pay' }],
                [{ text: '↩️ Voltar', callback_data: 'back_main' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showPushinPayMenu(chatId, messageId, userId) {
        const text = `ℹ️ *Informe o valor que deseja recarregar:*

🔻 *Recarga mínima:* R$ 1.00

⚠️ Por favor, envie o valor que deseja recarregar agora.

*Resposta:* @${this.bot.options.username}
Informe o valor que deseja recarregar`;

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Voltar', callback_data: 'recharge' }]]
            }
        });

        // Ativar estado de espera por valor
        this.userStates.set(userId, 'waiting_recharge_amount');
    }

    async generatePixForUser(chatId, userId, amount) {
        try {
            const user = await db.getUserByTelegramId(userId.toString());
            if (!user) return;

            await this.bot.sendMessage(chatId, '*Gerando pagamento...*', { parse_mode: 'Markdown' });

            const transaction = await db.createPixTransaction(user.id, amount);
            const expiresAt = moment(transaction.expires_at).format('DD/MM/YYYY [às] HH:mm:ss');

            const pixText = `💰 *Comprar Saldo com Pix Automático:*

⏱️ *Expira em:* ${expiresAt}
💵 *Valor:* R$ ${amount.toFixed(2)}
✨ *ID da Recarga:* ${transaction.transaction_id}

🗞️ *Atenção:* Este código é válido para apenas um único pagamento.
Se você utilizá-lo mais de uma vez, o saldo adicional será perdido sem direito a reembolso.

💎 *Pix Copia e Cola:*

\`${transaction.pix_key}\`

💡 *Dica:* Clique no código acima para copiar.

🇧🇷 Após o pagamento, seu saldo será liberado instantaneamente.`;

            const keyboard = {
                inline_keyboard: [
                    [{ text: '⏰ Aguardando Pagamento', callback_data: 'waiting_payment' }]
                ]
            };

            await this.bot.sendMessage(chatId, pixText, {
                parse_mode: 'Markdown',
                reply_markup: keyboard
            });

            // Simular verificação de pagamento
            setTimeout(async () => {
                await this.simulatePaymentConfirmation(chatId, userId, amount, transaction.transaction_id);
            }, 30000);

        } catch (error) {
            console.error('Erro ao gerar PIX:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao gerar PIX. Tente novamente.');
        }
    }

    async simulatePaymentConfirmation(chatId, userId, amount, transactionId) {
        // Simular confirmação de pagamento (70% de chance)
        if (Math.random() > 0.3) {
            const user = await db.getUserByTelegramId(userId.toString());
            await db.updateUserBalance(user.id, amount, 'add');

            await this.bot.sendMessage(chatId, `✅ *Pagamento Confirmado!*

💰 R$ ${amount.toFixed(2)} foram adicionados ao seu saldo!
🆔 Transação: ${transactionId}

💼 *Saldo atual:* R$ ${(user.balance + amount).toFixed(2)}`, {
                parse_mode: 'Markdown'
            });

            // Atualizar ranking de recargas
            await this.updateUserRanking(user.id, user.username, 'recharges', amount);
        }
    }

    async showRankingMenu(chatId, messageId = null) {
        const text = `🏆 *Rankings do Sistema*

Escolha o tipo de ranking que deseja visualizar:`;

        const keyboard = {
            inline_keyboard: [
                [{ text: '🛒 Serviços', callback_data: 'ranking_services' }],
                [{ text: '💰 Recargas', callback_data: 'ranking_recharges' }],
                [{ text: '🛍️ Compras', callback_data: 'ranking_purchases' }],
                [{ text: '🎁 Gift Cards', callback_data: 'ranking_gifts' }],
                [{ text: '💰 Saldo', callback_data: 'ranking_balance' }],
                [{ text: '↩️ Voltar', callback_data: 'back_main' }]
            ]
        };

        if (messageId) {
            await this.bot.editMessageText(text, {
                chat_id: chatId,
                message_id: messageId,
                parse_mode: 'Markdown',
                reply_markup: keyboard
            });
        } else {
            await this.bot.sendMessage(chatId, text, {
                parse_mode: 'Markdown',
                reply_markup: keyboard
            });
        }
    }

    async showSpecificRanking(chatId, messageId, type) {
        const rankings = await db.getRanking(type);
        let title = '';
        let emoji = '';

        switch (type) {
            case 'services':
                title = 'serviços mais vendidos';
                emoji = '🛒';
                break;
            case 'recharges':
                title = 'usuários que mais recarregaram';
                emoji = '💰';
                break;
            case 'purchases':
                title = 'usuários que mais compraram';
                emoji = '🛍️';
                break;
            case 'gifts':
                title = 'usuários que mais resgataram gift card';
                emoji = '🎁';
                break;
            case 'balance':
                title = 'usuários com maior saldo';
                emoji = '💰';
                break;
        }

        let text = `🏆 *Ranking dos ${title} (deste mês)*\n\n`;

        if (rankings.length === 0) {
            text += 'Ainda não há dados para este ranking.';
        } else {
            rankings.forEach((rank, index) => {
                const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
                const position = index + 1;
                const value = type === 'recharges' || type === 'balance' || type === 'gifts' 
                    ? `R$ ${rank.value.toFixed(2)}` 
                    : `${rank.count}`;
                
                text += `${position}°) ${rank.username} ${medal}`;
                if (type === 'recharges') text += ` - Com ${value} em recargas\n`;
                else if (type === 'purchases') text += ` - Com ${value} compras\n`;
                else if (type === 'gifts') text += ` - Com ${value} resgatados\n`;
                else if (type === 'balance') text += ` - Com ${value} de saldo\n`;
                else text += ` - Com ${value} vendas\n`;
            });
        }

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Voltar', callback_data: 'ranking' }]]
            }
        });
    }

    async showBotInfo(chatId, messageId) {
        const text = `ℹ️ *SOFTWARE INFO:*
🤖*BOT:* @${this.bot.options.username}
🤖*VERSION:* 1.0.0

🛠️ *DEVELOPER INFO:*
O Desenvolvedor não possui responsabilidade alguma sobre este Bot e nem sobre o adm do mesmo, caso entre em contato para reclamar sobre material ou pedir para chamar o adm deste Bot ou algo do tipo, será bloqueado de imediato... Apenas o chame, caso queira conhecer os Bots disponíveis.`;

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Voltar', callback_data: 'back_main' }]]
            }
        });
    }

    async showSupportInfo(chatId, messageId) {
        // Integração com sistema de ligação automática
        await this.requestPhoneForSupport(chatId, messageId);
    }

    async requestPhoneForSupport(chatId, messageId) {
        const text = `📞 *Suporte por Ligação*

Para conectá-lo ao nosso sistema de suporte automatizado via WhatsApp, precisamos do seu número de telefone.

Por favor, envie seu número no formato:
*+5511999999999*

Após o envio, você receberá uma ligação de voz automática no WhatsApp.`;

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Voltar', callback_data: 'back_main' }]]
            }
        });

        this.userStates.set(chatId, 'waiting_phone_support');
    }

    async handleTextMessage(msg) {
        const chatId = msg.chat.id;
        const userId = msg.from.id;
        const text = msg.text;
        const userState = this.userStates.get(userId) || this.userStates.get(chatId);

        if (userState === 'waiting_recharge_amount') {
            const amount = parseFloat(text);
            if (!isNaN(amount) && amount >= 1) {
                await this.generatePixForUser(chatId, userId, amount);
                this.userStates.delete(userId);
            } else {
                await this.bot.sendMessage(chatId, '❌ Valor inválido. Digite um valor mínimo de R$ 1,00');
            }
        } else if (userState === 'waiting_phone_support') {
            await this.processSupportCall(chatId, text);
            this.userStates.delete(chatId);
        } else if (text.length > 2) {
            // Busca de produtos
            await this.searchProducts(chatId, text);
        }
    }

    async searchProducts(chatId, searchTerm) {
        const products = await db.getAllProducts();
        const filteredProducts = products.filter(product => 
            product.name.toLowerCase().includes(searchTerm.toLowerCase())
        );

        if (filteredProducts.length === 0) {
            await this.bot.sendMessage(chatId, `❌ Nenhum produto encontrado para: "${searchTerm}"`);
            return;
        }

        let text = `🔍 *Resultados da busca:* "${searchTerm}"\n\n`;

        filteredProducts.forEach(product => {
            text += `*${product.name}* - R$ ${product.price.toFixed(2)}\n`;
            text += `Descrição: ${product.description?.substring(0, 50)}...\n\n`;
        });

        const keyboard = { inline_keyboard: [] };
        filteredProducts.forEach(product => {
            keyboard.inline_keyboard.push([{
                text: `Ver ${product.name}`,
                callback_data: `product_${product.id}`
            }]);
        });

        await this.bot.sendMessage(chatId, text, {
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async processSupportCall(chatId, phoneNumber) {
        // Simular sistema de ligação automática
        const cleanPhone = phoneNumber.replace(/\D/g, '');
        
        if (cleanPhone.length < 10) {
            await this.bot.sendMessage(chatId, '❌ Número inválido. Tente novamente com o formato: +5511999999999');
            return;
        }

        await this.bot.sendMessage(chatId, `📞 *Ligação Agendada!*

Você receberá uma ligação de voz automática no WhatsApp em alguns instantes no número: ${phoneNumber}

O robô irá explicar sobre nossos produtos e tirar suas dúvidas.

*Aguarde a ligação...* 📱`);

        // Aqui seria integrado com sistema real de ligação
        // Por enquanto, apenas simular
        setTimeout(async () => {
            await this.bot.sendMessage(chatId, '✅ Ligação realizada! Caso não tenha recebido, verifique seu WhatsApp.');
        }, 5000);
    }

    async sendUserHistory(chatId, userId) {
        const user = await db.getUserByTelegramId(userId.toString());
        const purchases = await db.getUserPurchases(user.id);

        const storeName = await db.getConfig('store_name') || 'JOÃOZINHO STORE BOT';
        
        let historyText = `HISTORICO DETALHADO\n@ ${storeName}\n_______________________\n\nCOMPRAS:\n_______________________\n\n`;

        if (purchases.length === 0) {
            historyText += 'Nenhuma compra realizada ainda.\n\n';
        } else {
            purchases.forEach((purchase, index) => {
                historyText += `${index + 1}. ${purchase.product_name}\n`;
                historyText += `Valor: R$ ${purchase.amount.toFixed(2)}\n`;
                historyText += `Data: ${moment(purchase.created_at).format('DD/MM/YYYY HH:mm')}\n\n`;
            });
        }

        historyText += '_______________________\n\nPAGAMENTOS:\n\nEm desenvolvimento...\n';

        // Criar arquivo temporário
        const fileName = `historico_${userId}_${Date.now()}.txt`;
        const filePath = path.join(__dirname, fileName);
        
        fs.writeFileSync(filePath, historyText);

        await this.bot.sendDocument(chatId, filePath, {
            caption: '📋 Seu histórico detalhado'
        });

        // Remover arquivo temporário
        fs.unlinkSync(filePath);
    }

    async showAffiliateInfo(chatId, userId) {
        const user = await db.getUserByTelegramId(userId.toString());
        const affiliateLink = `https://t.me/${this.bot.options.username}?start=${user.affiliate_code}`;

        const text = `ℹ️ *Status:*
📊 *Comissão por Indicação:* ${(user.commission_rate * 100).toFixed(0)}%
👥 *Total de Afiliados:* 0
🔗 *Link para Indicar:* ${affiliateLink}

*Como Funciona?*
Copie seu link de indicação e envie para outras pessoas.
Cada vez que alguém indicado por você fizer uma recarga no bot, você receberá uma porcentagem desse valor!

Por exemplo, com uma comissão de 50%, se 5 pessoas indicadas recarregarem R$10,00 cada, você receberá R$25,00.

*Indique mais e aumente seus ganhos!*`;

        await this.bot.sendMessage(chatId, text, { parse_mode: 'Markdown' });
    }

    async showProductAlerts(chatId, userId) {
        const products = await db.getAllProducts();
        
        const text = `🔔 *Alertas de Produtos*

Ative ou desative alertas para ser notificado quando um produto for reabastecido:`;

        const keyboard = { inline_keyboard: [] };
        
        products.forEach(product => {
            keyboard.inline_keyboard.push([{
                text: `${product.name} - ${product.stock > 0 ? '✅' : '❌'}`,
                callback_data: `alert_${product.id}`
            }]);
        });

        keyboard.inline_keyboard.push([{ text: '↩️ Voltar', callback_data: 'back_main' }]);

        await this.bot.sendMessage(chatId, text, {
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async createSampleProducts() {
        const sampleProducts = [
            { name: 'NETFLIX PREMIUM', description: 'Acesso completo Netflix Premium por 30 dias', price: 15.00, stock: 100 },
            { name: 'SPOTIFY PREMIUM', description: 'Spotify Premium por 30 dias', price: 8.00, stock: 50 },
            { name: 'DISNEY+ PREMIUM', description: 'Disney Plus Premium por 30 dias', price: 12.00, stock: 75 },
            { name: 'AMAZON PRIME', description: 'Amazon Prime Video por 30 dias', price: 10.00, stock: 60 }
        ];

        for (const product of sampleProducts) {
            await db.createProduct(product.name, product.description, product.price, product.stock);
        }
    }

    async updateUserRanking(userId, username, type, value) {
        try {
            await db.updateRanking(type, userId, username, value);
        } catch (error) {
            console.error('Erro ao atualizar ranking:', error);
        }
    }

    async initiateSearch(chatId, messageId) {
        const text = `🔍 *Pesquisar Serviços*

Digite o nome do produto que você está procurando:

Exemplo: Netflix, Spotify, Disney, etc.`;

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Voltar', callback_data: 'back_main' }]]
            }
        });
    }

    start() {
        console.log('🚀 Telegram Store Bot iniciado!');
        console.log('🤖 Bot:', this.bot.options.username);
    }
}

// Inicializar o bot
const telegramStoreBot = new TelegramStoreBot();
telegramStoreBot.start();

module.exports = TelegramStoreBot;