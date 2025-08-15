const axios = require('axios');
const express = require('express');
const db = require('./database');
const moment = require('moment');
require('dotenv').config();

class WhatsAppBot {
    constructor() {
        this.apiUrl = process.env.CALLMEBOT_API_URL;
        this.apiKey = process.env.WHATSAPP_API_KEY;
        this.phone = process.env.WHATSAPP_PHONE;
        this.userStates = new Map(); // Armazenar estados dos usuários
        this.floodControl = new Map(); // Controle de flood
        this.app = express();
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
    }

    setupRoutes() {
        // Webhook para receber mensagens (simular recebimento)
        this.app.post('/webhook/whatsapp', async (req, res) => {
            try {
                const { phone, message, name } = req.body;
                await this.handleMessage(phone, message, name);
                res.status(200).send('OK');
            } catch (error) {
                console.error('Erro no webhook:', error);
                res.status(500).send('Erro');
            }
        });

        this.app.listen(process.env.PORT || 3000, () => {
            console.log('🤖 WhatsApp Bot rodando na porta', process.env.PORT || 3000);
        });
    }

    async sendMessage(phone, message) {
        try {
            const encodedMessage = encodeURIComponent(message);
            const url = `${this.apiUrl}?phone=${phone}&text=${encodedMessage}&apikey=${this.apiKey}`;
            
            const response = await axios.get(url);
            console.log('✅ Mensagem enviada para', phone);
            return response.data;
        } catch (error) {
            console.error('❌ Erro ao enviar mensagem:', error.message);
            throw error;
        }
    }

    async handleMessage(phone, message, name = 'Usuário') {
        // Controle de flood
        if (this.checkFlood(phone)) {
            return await this.sendFloodWarning(phone);
        }

        const cleanPhone = phone.replace(/\D/g, '');
        let user = await this.getOrCreateUser(cleanPhone, name);
        
        const userState = this.userStates.get(cleanPhone) || 'main_menu';
        
        // Comandos específicos
        if (message.toLowerCase() === 'stop') {
            return await this.sendMessage(phone, '⏸️ Bot pausado. Envie "Resume" para reativar.');
        }
        
        if (message.toLowerCase() === 'resume') {
            return await this.sendMessage(phone, '▶️ Bot reativado! Bem-vindo de volta!');
        }

        // Processar mensagem baseado no estado
        switch (userState) {
            case 'main_menu':
                await this.handleMainMenu(phone, message, user);
                break;
            case 'adding_balance':
                await this.handleAddingBalance(phone, message, user);
                break;
            case 'custom_amount':
                await this.handleCustomAmount(phone, message, user);
                break;
            case 'converting_bonus':
                await this.handleConvertingBonus(phone, message, user);
                break;
            default:
                await this.handleMainMenu(phone, message, user);
        }
    }

    async handleMainMenu(phone, message, user) {
        if (message === '1' || message.toLowerCase().includes('start') || message === '/start') {
            await this.sendWelcomeMessage(phone, user);
        } else if (message === '💸' || message.toLowerCase().includes('adicionar saldo')) {
            await this.showBalanceMenu(phone, user);
        } else if (message === '🛍️' || message.toLowerCase().includes('assinaturas premium')) {
            await this.showPremiumSubscriptions(phone, user);
        } else if (message === '💼' || message.toLowerCase().includes('area do associado')) {
            await this.showAssociateArea(phone, user);
        } else if (message === '🆘' || message.toLowerCase().includes('contato do suporte')) {
            await this.showSupport(phone, user);
        } else {
            await this.sendWelcomeMessage(phone, user);
        }
    }

    async sendWelcomeMessage(phone, user) {
        const storeName = await db.getConfig('store_name') || 'JOÃOZINHO STORE BOT';
        const message = `🤖 *${storeName}*

🥇Nosso bot permite que você encontre diversos produtos e serviços, oferecendo um ótimo custo-beneficio na hora de comprar, assim você encontrará o item desejado pelo menor preço.

ℹ️ *Seus Dados:*
💠 *Número:* ${phone}
💸 *Saldo Atual:* R$ ${user.balance.toFixed(2)}

Selecione uma opção:

💸 *Adicionar Saldo*
🛍️ *Assinaturas Premium*
💼 *Area do Associado*
🆘 *Contato do Suporte*

_Envie o emoji ou palavra-chave da opção desejada._`;

        await this.sendMessage(phone, message);
    }

    async showBalanceMenu(phone, user) {
        const message = `💸 *MENU DE OPÇÃO DE PIX* 💸

Escolha um dos valores disponíveis para recarregar sua conta ou selecione "Digite outro valor" para inserir um valor personalizado.

💠 *PIX R$ 5,00*
💠 *PIX R$ 10,00*
💠 *PIX R$ 20,00*
💠 *DIGITE OUTRO VALOR*

_Envie o valor desejado (ex: 5, 10, 20) ou "outro" para valor customizado._`;

        await this.sendMessage(phone, message);
        this.userStates.set(phone.replace(/\D/g, ''), 'adding_balance');
    }

    async handleAddingBalance(phone, message, user) {
        const cleanPhone = phone.replace(/\D/g, '');
        let amount = 0;

        if (message === '5' || message.toLowerCase().includes('5')) {
            amount = 5.00;
        } else if (message === '10' || message.toLowerCase().includes('10')) {
            amount = 10.00;
        } else if (message === '20' || message.toLowerCase().includes('20')) {
            amount = 20.00;
        } else if (message.toLowerCase().includes('outro') || message.toLowerCase().includes('digite')) {
            await this.requestCustomAmount(phone);
            return;
        } else if (!isNaN(parseFloat(message))) {
            amount = parseFloat(message);
            if (amount < 1) {
                await this.sendMessage(phone, '❌ Valor mínimo para recarga é R$ 1,00. Tente novamente.');
                return;
            }
        } else {
            await this.sendMessage(phone, '❌ Valor inválido. Envie um número válido ou escolha uma das opções.');
            return;
        }

        await this.generatePix(phone, user, amount);
        this.userStates.set(cleanPhone, 'main_menu');
    }

    async requestCustomAmount(phone) {
        const message = `💰 *Digite o valor desejado para recarga:*

🔻 Valor mínimo: R$ 1,00

_Envie apenas o número (exemplo: 15.50)_`;

        await this.sendMessage(phone, message);
        this.userStates.set(phone.replace(/\D/g, ''), 'custom_amount');
    }

    async handleCustomAmount(phone, message, user) {
        const cleanPhone = phone.replace(/\D/g, '');
        const amount = parseFloat(message);

        if (isNaN(amount) || amount < 1) {
            await this.sendMessage(phone, '❌ Valor inválido. Digite um valor mínimo de R$ 1,00');
            return;
        }

        await this.generatePix(phone, user, amount);
        this.userStates.set(cleanPhone, 'main_menu');
    }

    async generatePix(phone, user, amount) {
        try {
            await this.sendMessage(phone, '*⏳ Gerando PIX...*\n\nAguarde um momento! 💰');

            const transaction = await db.createPixTransaction(user.id, amount);
            const expiresAt = moment(transaction.expires_at).format('DD/MM/YYYY [às] HH:mm:ss');

            const pixMessage = `*💰 ADICIONAR SALDO COM PIX AUTOMÁTICO 💠*

⚠️ Você está prestes a adicionar saldo ao bot!

Escaneie o *QR Code* ou utilize o *código PIX* enviado abaixo.

O PIX expira em *30 minutos*, pague dentro do prazo.

O saldo será creditado em até *1 minuto* após o pagamento.

*⚠️ ADICIONE APENAS O QUE FOR USAR!*
_Não realizamos reembolsos._

━━━━━━━━❪❃❫━━━━━━━━

*🆔 ID da Compra:* ${transaction.transaction_id}
*💰 Valor:* R$ ${amount.toFixed(2)}
*📅 Vencimento:* ${expiresAt}

━━━━━━━━❪❃❫━━━━━━━━

*🔑 O código PIX foi enviado abaixo para facilitar o pagamento!*

\`\`\`${transaction.pix_key}\`\`\`

_Clique no código acima para copiar._`;

            await this.sendMessage(phone, pixMessage);

            // Simular verificação de pagamento (em produção, usar webhook real)
            setTimeout(async () => {
                await this.simulatePaymentCheck(phone, user, transaction, amount);
            }, 30000); // Simular pagamento em 30 segundos

        } catch (error) {
            console.error('Erro ao gerar PIX:', error);
            await this.sendMessage(phone, '❌ Erro ao gerar PIX. Tente novamente.');
        }
    }

    async simulatePaymentCheck(phone, user, transaction, amount) {
        // Simular aprovação automática para demonstração
        const random = Math.random();
        if (random > 0.3) { // 70% de chance de "pagamento"
            await db.updateUserBalance(user.id, amount, 'add');
            await this.sendMessage(phone, `✅ *Pagamento Confirmado!*\n\n💰 R$ ${amount.toFixed(2)} foram adicionados ao seu saldo!\n\nSaldo atual: R$ ${(user.balance + amount).toFixed(2)}`);
        } else {
            await this.sendMessage(phone, `*⚠️ Solicitação Negada!*\n\nDesculpe, sua recarga falhou porque o *PIX não foi pago dentro do prazo*. ⏳❌`);
        }
    }

    async showPremiumSubscriptions(phone, user) {
        const products = await db.getAllProducts();
        let message = `🥇 Somos a solução para o mercado digital, disponibilizando um bot moderno que permite que o cliente receba pelo produto / serviço desejado. Tudo isso com praticidade e segurança.

🏦 *Carteira:*
💠 *Número:* ${phone}
💰 *Saldo Atual:* R$ ${user.balance.toFixed(2)}

*📱 PRODUTOS DISPONÍVEIS:*\n`;

        if (products.length === 0) {
            // Criar produtos exemplo se não existirem
            await this.createSampleProducts();
            const sampleProducts = await db.getAllProducts();
            sampleProducts.forEach((product, index) => {
                message += `\n${index + 1}. *${product.name.toUpperCase()}* - R$ ${product.price.toFixed(2)}`;
            });
        } else {
            products.forEach((product, index) => {
                message += `\n${index + 1}. *${product.name.toUpperCase()}* - R$ ${product.price.toFixed(2)}`;
            });
        }

        message += `\n\n_Envie o número do produto que deseja comprar._`;

        await this.sendMessage(phone, message);
        this.userStates.set(phone.replace(/\D/g, ''), 'selecting_product');
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

    async showAssociateArea(phone, user) {
        const message = `🗒️ *SUA CONTA*

👤 *Nome:* ${user.username || 'Usuário'}
🆔 *Telegram ID:* ${user.telegram_id || 'N/A'}
📞 *Número:* ${phone}

📢 *Indicador:* ${user.affiliate_code}
*Cargo:* Cliente
*Saldo:* R$ ${user.balance.toFixed(2)}
*Bônus:* R$ ${user.bonus.toFixed(2)}

*Opções disponíveis:*
🛍️ *Minhas Compras*
💰 *Resgatar Saldo*

_Envie "compras" para ver histórico ou "resgatar" para converter bônus._`;

        await this.sendMessage(phone, message);
    }

    async showSupport(phone, user) {
        const supportName = await db.getConfig('support_name') || 'JOÃO';
        const supportPhone = await db.getConfig('support_phone') || '5544998312326';

        const message = `*👤 CONTATO DO SUPORTE 👤*

*⚠️ Este é o número do responsável ou suporte deste bot.*

*⚠️ Dúvidas sobre o material vendido?* Entre em contato apenas com este número!

*${supportName}* - ${supportPhone}

_Para falar diretamente com o suporte, clique no link:_
https://wa.me/${supportPhone}`;

        await this.sendMessage(phone, message);
    }

    checkFlood(phone) {
        const cleanPhone = phone.replace(/\D/g, '');
        const now = Date.now();
        const floodData = this.floodControl.get(cleanPhone) || { count: 0, lastMessage: 0 };

        if (now - floodData.lastMessage < 6000) { // 6 segundos
            floodData.count++;
            if (floodData.count >= 3) {
                floodData.timeout = now + (6000 * floodData.count); // Timeout acumulativo
                this.floodControl.set(cleanPhone, floodData);
                return true;
            }
        } else {
            floodData.count = 0;
        }

        floodData.lastMessage = now;
        this.floodControl.set(cleanPhone, floodData);
        return false;
    }

    async sendFloodWarning(phone) {
        const cleanPhone = phone.replace(/\D/g, '');
        const floodData = this.floodControl.get(cleanPhone);
        const timeoutSeconds = Math.ceil((floodData.timeout - Date.now()) / 1000);

        const message = `*⚠️ Atenção!*

Pare de floodar! Suas solicitações serão ignoradas pelos próximos *${timeoutSeconds} segundos* (acumulativo). ⏳`;

        await this.sendMessage(phone, message);
    }

    async getOrCreateUser(phone, name) {
        try {
            let user = await db.getUserByTelegramId(phone);
            if (!user) {
                await db.createUser(phone, name, phone);
                user = await db.getUserByTelegramId(phone);
            }
            return user;
        } catch (error) {
            console.error('Erro ao buscar/criar usuário:', error);
            throw error;
        }
    }

    // Método para iniciar o bot
    start() {
        console.log('🚀 WhatsApp Bot iniciado!');
        console.log('📱 Número:', this.phone);
        console.log('🔑 API Key configurada');
    }
}

// Inicializar o bot
const whatsappBot = new WhatsAppBot();
whatsappBot.start();

module.exports = WhatsAppBot;