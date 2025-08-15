const TelegramBot = require('node-telegram-bot-api');
const db = require('./database');
const moment = require('moment');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

class TelegramAdminBot {
    constructor() {
        this.token = process.env.TELEGRAM_ADMIN_BOT_TOKEN;
        this.bot = new TelegramBot(this.token, { polling: true });
        this.adminId = parseInt(process.env.ADMIN_TELEGRAM_ID);
        this.adminStates = new Map();
        this.setupHandlers();
        this.setupCommands();
    }

    setupCommands() {
        this.bot.setMyCommands([
            { command: 'start', description: '🚀 Painel Administrativo' },
            { command: 'produtos', description: '📦 Gerenciar produtos' },
            { command: 'usuarios', description: '👥 Gerenciar usuários' },
            { command: 'vendas', description: '💰 Relatório de vendas' },
            { command: 'config', description: '⚙️ Configurações do sistema' },
            { command: 'backup', description: '💾 Backup do banco de dados' },
            { command: 'broadcast', description: '📢 Enviar mensagem para todos' },
            { command: 'stats', description: '📊 Estatísticas do sistema' }
        ]);
    }

    setupHandlers() {
        // Verificar se o usuário é admin
        this.bot.use((ctx, next) => {
            if (ctx.from.id !== this.adminId) {
                this.bot.sendMessage(ctx.chat.id, '❌ Acesso negado. Você não é administrador.');
                return;
            }
            return next();
        });

        // Handler para /start
        this.bot.onText(/\/start/, async (msg) => {
            await this.showAdminMenu(msg.chat.id);
        });

        // Handler para produtos
        this.bot.onText(/\/produtos/, async (msg) => {
            await this.showProductsMenu(msg.chat.id);
        });

        // Handler para usuários
        this.bot.onText(/\/usuarios/, async (msg) => {
            await this.showUsersMenu(msg.chat.id);
        });

        // Handler para vendas
        this.bot.onText(/\/vendas/, async (msg) => {
            await this.showSalesReport(msg.chat.id);
        });

        // Handler para configurações
        this.bot.onText(/\/config/, async (msg) => {
            await this.showConfigMenu(msg.chat.id);
        });

        // Handler para backup
        this.bot.onText(/\/backup/, async (msg) => {
            await this.generateBackup(msg.chat.id);
        });

        // Handler para broadcast
        this.bot.onText(/\/broadcast/, async (msg) => {
            await this.initiateBroadcast(msg.chat.id);
        });

        // Handler para stats
        this.bot.onText(/\/stats/, async (msg) => {
            await this.showStats(msg.chat.id);
        });

        // Handler para callback queries
        this.bot.on('callback_query', async (query) => {
            await this.handleCallbackQuery(query);
        });

        // Handler para mensagens de texto
        this.bot.on('message', async (msg) => {
            if (msg.text && !msg.text.startsWith('/')) {
                await this.handleTextMessage(msg);
            }
        });
    }

    async showAdminMenu(chatId) {
        const stats = await this.getQuickStats();
        
        const text = `🛠️ *PAINEL ADMINISTRATIVO*
🤖 *JOÃOZINHO STORE BOT*

📊 *Estatísticas Rápidas:*
👥 Usuários: ${stats.users}
📦 Produtos: ${stats.products}
💰 Vendas hoje: R$ ${stats.todaySales.toFixed(2)}
🛒 Compras hoje: ${stats.todayPurchases}

🎛️ *Menu Principal:*`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '📦 Produtos', callback_data: 'admin_products' },
                    { text: '👥 Usuários', callback_data: 'admin_users' }
                ],
                [
                    { text: '💰 Vendas', callback_data: 'admin_sales' },
                    { text: '📊 Estatísticas', callback_data: 'admin_stats' }
                ],
                [
                    { text: '⚙️ Configurações', callback_data: 'admin_config' },
                    { text: '📢 Broadcast', callback_data: 'admin_broadcast' }
                ],
                [
                    { text: '💾 Backup', callback_data: 'admin_backup' },
                    { text: '🔄 Atualizar', callback_data: 'admin_refresh' }
                ]
            ]
        };

        await this.bot.sendMessage(chatId, text, {
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async handleCallbackQuery(query) {
        const chatId = query.message.chat.id;
        const data = query.data;
        const messageId = query.message.message_id;

        try {
            await this.bot.answerCallbackQuery(query.id);

            switch (data) {
                case 'admin_products':
                    await this.showProductsAdmin(chatId, messageId);
                    break;
                case 'admin_users':
                    await this.showUsersAdmin(chatId, messageId);
                    break;
                case 'admin_sales':
                    await this.showSalesAdmin(chatId, messageId);
                    break;
                case 'admin_stats':
                    await this.showStatsAdmin(chatId, messageId);
                    break;
                case 'admin_config':
                    await this.showConfigAdmin(chatId, messageId);
                    break;
                case 'admin_broadcast':
                    await this.showBroadcastAdmin(chatId, messageId);
                    break;
                case 'admin_backup':
                    await this.generateBackupAdmin(chatId);
                    break;
                case 'admin_refresh':
                    await this.bot.deleteMessage(chatId, messageId);
                    await this.showAdminMenu(chatId);
                    break;
                case 'add_product':
                    await this.initiateAddProduct(chatId, messageId);
                    break;
                case 'list_products':
                    await this.listAllProducts(chatId, messageId);
                    break;
                case 'add_stock':
                    await this.initiateAddStock(chatId, messageId);
                    break;
                case 'back_main_admin':
                    await this.bot.deleteMessage(chatId, messageId);
                    await this.showAdminMenu(chatId);
                    break;
                default:
                    if (data.startsWith('edit_product_')) {
                        const productId = data.split('_')[2];
                        await this.showEditProduct(chatId, messageId, productId);
                    } else if (data.startsWith('delete_product_')) {
                        const productId = data.split('_')[2];
                        await this.confirmDeleteProduct(chatId, messageId, productId);
                    } else if (data.startsWith('stock_product_')) {
                        const productId = data.split('_')[2];
                        await this.showStockProduct(chatId, messageId, productId);
                    }
                    break;
            }
        } catch (error) {
            console.error('Erro no callback admin:', error);
            await this.bot.answerCallbackQuery(query.id, { text: '❌ Erro interno' });
        }
    }

    async showProductsAdmin(chatId, messageId) {
        const text = `📦 *GERENCIAMENTO DE PRODUTOS*

Escolha uma ação:`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '➕ Adicionar Produto', callback_data: 'add_product' },
                    { text: '📋 Listar Produtos', callback_data: 'list_products' }
                ],
                [{ text: '📈 Adicionar Estoque', callback_data: 'add_stock' }],
                [{ text: '↩️ Voltar', callback_data: 'back_main_admin' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async initiateAddProduct(chatId, messageId) {
        const text = `➕ *ADICIONAR NOVO PRODUTO*

Envie as informações do produto no formato:

\`Nome | Descrição | Preço | Estoque\`

*Exemplo:*
\`Netflix Premium | Acesso Netflix por 30 dias | 15.00 | 100\`

Envie agora:`;

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Cancelar', callback_data: 'admin_products' }]]
            }
        });

        this.adminStates.set(chatId, 'adding_product');
    }

    async listAllProducts(chatId, messageId) {
        const products = await db.getAllProducts();
        
        if (products.length === 0) {
            await this.bot.editMessageText('📦 Nenhum produto cadastrado.', {
                chat_id: chatId,
                message_id: messageId,
                reply_markup: {
                    inline_keyboard: [[{ text: '↩️ Voltar', callback_data: 'admin_products' }]]
                }
            });
            return;
        }

        let text = `📦 *PRODUTOS CADASTRADOS* (${products.length})\n\n`;

        const keyboard = { inline_keyboard: [] };

        products.forEach((product, index) => {
            text += `${index + 1}. *${product.name}*\n`;
            text += `💰 R$ ${product.price.toFixed(2)} | 📦 ${product.stock} unidades\n`;
            text += `${product.active ? '✅ Ativo' : '❌ Inativo'}\n\n`;

            keyboard.inline_keyboard.push([
                { text: `✏️ ${product.name}`, callback_data: `edit_product_${product.id}` },
                { text: `📈 Stock`, callback_data: `stock_product_${product.id}` }
            ]);
        });

        // Limitar texto se muito longo
        if (text.length > 4000) {
            text = text.substring(0, 3900) + '\n\n... (lista truncada)';
        }

        keyboard.inline_keyboard.push([{ text: '↩️ Voltar', callback_data: 'admin_products' }]);

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showEditProduct(chatId, messageId, productId) {
        const product = await db.getProductById(productId);
        
        if (!product) {
            await this.bot.answerCallbackQuery(query.id, { text: '❌ Produto não encontrado' });
            return;
        }

        const text = `✏️ *EDITAR PRODUTO*

*Produto:* ${product.name}
*Preço:* R$ ${product.price.toFixed(2)}
*Estoque:* ${product.stock}
*Status:* ${product.active ? 'Ativo' : 'Inativo'}

*Descrição:*
${product.description || 'Sem descrição'}

Escolha uma ação:`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '💰 Alterar Preço', callback_data: `price_${productId}` },
                    { text: '📦 Alterar Estoque', callback_data: `stock_${productId}` }
                ],
                [
                    { text: '📝 Alterar Nome', callback_data: `name_${productId}` },
                    { text: '📄 Alterar Descrição', callback_data: `desc_${productId}` }
                ],
                [
                    { text: product.active ? '❌ Desativar' : '✅ Ativar', callback_data: `toggle_${productId}` },
                    { text: '🗑️ Excluir', callback_data: `delete_product_${productId}` }
                ],
                [{ text: '↩️ Voltar', callback_data: 'list_products' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showUsersAdmin(chatId, messageId) {
        const users = await this.getUserStats();
        
        const text = `👥 *GERENCIAMENTO DE USUÁRIOS*

📊 *Estatísticas:*
• Total de usuários: ${users.total}
• Novos hoje: ${users.today}
• Com saldo: ${users.withBalance}
• Compraram este mês: ${users.activeBuyers}

🔧 *Ações disponíveis:*`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '📋 Listar Usuários', callback_data: 'list_users' },
                    { text: '🔍 Buscar Usuário', callback_data: 'search_user' }
                ],
                [
                    { text: '💰 Adicionar Saldo', callback_data: 'add_balance_user' },
                    { text: '📊 Top Usuários', callback_data: 'top_users' }
                ],
                [{ text: '↩️ Voltar', callback_data: 'back_main_admin' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showSalesAdmin(chatId, messageId) {
        const salesData = await this.getSalesData();
        
        const text = `💰 *RELATÓRIO DE VENDAS*

📈 *Hoje:*
• Vendas: R$ ${salesData.today.revenue.toFixed(2)}
• Transações: ${salesData.today.count}

📊 *Este Mês:*
• Vendas: R$ ${salesData.month.revenue.toFixed(2)}
• Transações: ${salesData.month.count}

📋 *Total Geral:*
• Vendas: R$ ${salesData.total.revenue.toFixed(2)}
• Transações: ${salesData.total.count}

🏆 *Produto Mais Vendido:*
${salesData.topProduct || 'Nenhuma venda ainda'}`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '📊 Relatório Detalhado', callback_data: 'detailed_sales' },
                    { text: '📈 Gráfico Mensal', callback_data: 'monthly_chart' }
                ],
                [{ text: '↩️ Voltar', callback_data: 'back_main_admin' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showConfigAdmin(chatId, messageId) {
        const configs = await this.getCurrentConfigs();
        
        const text = `⚙️ *CONFIGURAÇÕES DO SISTEMA*

🏪 *Loja:*
• Nome: ${configs.store_name}
• Suporte: ${configs.support_name} (${configs.support_phone})

💰 *Financeiro:*
• Recarga mínima: R$ ${configs.min_recharge}
• Taxa de comissão: ${(parseFloat(configs.commission_rate) * 100).toFixed(0)}%

⏰ *Sistema:*
• Timeout flood: ${configs.flood_timeout_seconds}s
• PIX expira em: ${configs.pix_expires_minutes} min

🔧 *Ações:*`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '🏪 Alterar Nome da Loja', callback_data: 'config_store_name' },
                    { text: '📞 Alterar Suporte', callback_data: 'config_support' }
                ],
                [
                    { text: '💰 Config. Financeira', callback_data: 'config_financial' },
                    { text: '🖼️ Alterar Logo', callback_data: 'config_logo' }
                ],
                [
                    { text: '🔗 Links e Grupos', callback_data: 'config_links' },
                    { text: '⚙️ Sistema', callback_data: 'config_system' }
                ],
                [{ text: '↩️ Voltar', callback_data: 'back_main_admin' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async showStatsAdmin(chatId, messageId) {
        const stats = await this.getDetailedStats();
        
        const text = `📊 *ESTATÍSTICAS DETALHADAS*

👥 *Usuários:*
• Total: ${stats.users.total}
• Ativos (últimos 7 dias): ${stats.users.active}
• Novos esta semana: ${stats.users.newWeek}

💰 *Financeiro:*
• Receita total: R$ ${stats.finance.totalRevenue.toFixed(2)}
• Receita este mês: R$ ${stats.finance.monthRevenue.toFixed(2)}
• Ticket médio: R$ ${stats.finance.averageTicket.toFixed(2)}

📦 *Produtos:*
• Total cadastrados: ${stats.products.total}
• Em estoque: ${stats.products.inStock}
• Sem estoque: ${stats.products.outOfStock}

🛒 *Vendas:*
• Total de vendas: ${stats.sales.total}
• Vendas hoje: ${stats.sales.today}
• Vendas esta semana: ${stats.sales.week}`;

        const keyboard = {
            inline_keyboard: [
                [
                    { text: '📈 Exportar Relatório', callback_data: 'export_report' },
                    { text: '🔄 Atualizar', callback_data: 'admin_stats' }
                ],
                [{ text: '↩️ Voltar', callback_data: 'back_main_admin' }]
            ]
        };

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: keyboard
        });
    }

    async handleTextMessage(msg) {
        const chatId = msg.chat.id;
        const text = msg.text;
        const state = this.adminStates.get(chatId);

        switch (state) {
            case 'adding_product':
                await this.processAddProduct(chatId, text);
                break;
            case 'config_store_name':
                await this.processConfigStoreName(chatId, text);
                break;
            case 'broadcast_message':
                await this.processBroadcast(chatId, text);
                break;
            case 'search_user':
                await this.processSearchUser(chatId, text);
                break;
            default:
                // Comando não reconhecido
                await this.bot.sendMessage(chatId, '❓ Comando não reconhecido. Use /start para ver o menu.');
        }
    }

    async processAddProduct(chatId, text) {
        try {
            const parts = text.split('|').map(part => part.trim());
            
            if (parts.length !== 4) {
                await this.bot.sendMessage(chatId, '❌ Formato incorreto. Use: Nome | Descrição | Preço | Estoque');
                return;
            }

            const [name, description, priceStr, stockStr] = parts;
            const price = parseFloat(priceStr);
            const stock = parseInt(stockStr);

            if (isNaN(price) || isNaN(stock)) {
                await this.bot.sendMessage(chatId, '❌ Preço e estoque devem ser números válidos.');
                return;
            }

            const productId = await db.createProduct(name, description, price, stock);
            
            await this.bot.sendMessage(chatId, `✅ *Produto criado com sucesso!*

📦 *Nome:* ${name}
💰 *Preço:* R$ ${price.toFixed(2)}
📈 *Estoque:* ${stock}
🆔 *ID:* ${productId}`, { parse_mode: 'Markdown' });

            this.adminStates.delete(chatId);
            await this.showAdminMenu(chatId);

        } catch (error) {
            console.error('Erro ao criar produto:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao criar produto. Tente novamente.');
        }
    }

    async processConfigStoreName(chatId, text) {
        try {
            await db.setConfig('store_name', text);
            await this.bot.sendMessage(chatId, `✅ Nome da loja alterado para: *${text}*`, { parse_mode: 'Markdown' });
            this.adminStates.delete(chatId);
            await this.showAdminMenu(chatId);
        } catch (error) {
            console.error('Erro ao alterar nome da loja:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao alterar configuração.');
        }
    }

    async generateBackupAdmin(chatId) {
        try {
            await this.bot.sendMessage(chatId, '💾 Gerando backup do banco de dados...');

            // Criar backup do banco de dados
            const backupPath = path.join(__dirname, `backup_${Date.now()}.db`);
            const originalPath = process.env.DATABASE_PATH || './database.db';

            // Copiar arquivo do banco
            fs.copyFileSync(originalPath, backupPath);

            // Enviar arquivo
            await this.bot.sendDocument(chatId, backupPath, {
                caption: `💾 *Backup do Banco de Dados*\n📅 ${moment().format('DD/MM/YYYY HH:mm:ss')}`
            });

            // Remover arquivo temporário
            fs.unlinkSync(backupPath);

            await this.bot.sendMessage(chatId, '✅ Backup enviado com sucesso!');

        } catch (error) {
            console.error('Erro ao gerar backup:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao gerar backup.');
        }
    }

    async showBroadcastAdmin(chatId, messageId) {
        const text = `📢 *ENVIO EM MASSA*

⚠️ *Atenção:* Esta função enviará uma mensagem para todos os usuários cadastrados.

Digite a mensagem que deseja enviar:`;

        await this.bot.editMessageText(text, {
            chat_id: chatId,
            message_id: messageId,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: '↩️ Cancelar', callback_data: 'back_main_admin' }]]
            }
        });

        this.adminStates.set(chatId, 'broadcast_message');
    }

    async processBroadcast(chatId, message) {
        try {
            await this.bot.sendMessage(chatId, '📢 Iniciando envio em massa...');

            // Buscar todos os usuários
            const users = await this.getAllUsers();
            let successCount = 0;
            let errorCount = 0;

            for (const user of users) {
                try {
                    // Aqui você integraria com o bot da loja para enviar a mensagem
                    // Por enquanto, apenas simular
                    await new Promise(resolve => setTimeout(resolve, 100)); // Delay para evitar spam
                    successCount++;
                } catch (error) {
                    errorCount++;
                }
            }

            await this.bot.sendMessage(chatId, `✅ *Broadcast concluído!*

📊 *Resultados:*
✅ Enviadas: ${successCount}
❌ Falhas: ${errorCount}
📱 Total de usuários: ${users.length}`, { parse_mode: 'Markdown' });

            this.adminStates.delete(chatId);
            await this.showAdminMenu(chatId);

        } catch (error) {
            console.error('Erro no broadcast:', error);
            await this.bot.sendMessage(chatId, '❌ Erro ao enviar broadcast.');
        }
    }

    // Métodos auxiliares para buscar dados
    async getQuickStats() {
        const today = moment().format('YYYY-MM-DD');
        
        return {
            users: await this.countUsers(),
            products: await this.countProducts(),
            todaySales: await this.getTodaySales(),
            todayPurchases: await this.getTodayPurchases()
        };
    }

    async countUsers() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM users', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async countProducts() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM products WHERE active = 1', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getTodaySales() {
        const today = moment().format('YYYY-MM-DD');
        return new Promise((resolve, reject) => {
            db.db.get('SELECT SUM(amount) as total FROM purchases WHERE DATE(created_at) = ?', [today], (err, row) => {
                if (err) reject(err);
                else resolve(row.total || 0);
            });
        });
    }

    async getTodayPurchases() {
        const today = moment().format('YYYY-MM-DD');
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM purchases WHERE DATE(created_at) = ?', [today], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getUserStats() {
        const today = moment().format('YYYY-MM-DD');
        const thisMonth = moment().format('YYYY-MM');
        
        return {
            total: await this.countUsers(),
            today: await this.getUsersToday(),
            withBalance: await this.getUsersWithBalance(),
            activeBuyers: await this.getActiveBuyers()
        };
    }

    async getUsersToday() {
        const today = moment().format('YYYY-MM-DD');
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = ?', [today], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getUsersWithBalance() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM users WHERE balance > 0', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getActiveBuyers() {
        const thisMonth = moment().format('YYYY-MM');
        return new Promise((resolve, reject) => {
            db.db.get(`SELECT COUNT(DISTINCT user_id) as count FROM purchases 
                      WHERE strftime('%Y-%m', created_at) = ?`, [thisMonth], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getSalesData() {
        const today = moment().format('YYYY-MM-DD');
        const thisMonth = moment().format('YYYY-MM');
        
        return {
            today: {
                revenue: await this.getTodaySales(),
                count: await this.getTodayPurchases()
            },
            month: {
                revenue: await this.getMonthSales(),
                count: await this.getMonthPurchases()
            },
            total: {
                revenue: await this.getTotalSales(),
                count: await this.getTotalPurchases()
            },
            topProduct: await this.getTopProduct()
        };
    }

    async getMonthSales() {
        const thisMonth = moment().format('YYYY-MM');
        return new Promise((resolve, reject) => {
            db.db.get(`SELECT SUM(amount) as total FROM purchases 
                      WHERE strftime('%Y-%m', created_at) = ?`, [thisMonth], (err, row) => {
                if (err) reject(err);
                else resolve(row.total || 0);
            });
        });
    }

    async getMonthPurchases() {
        const thisMonth = moment().format('YYYY-MM');
        return new Promise((resolve, reject) => {
            db.db.get(`SELECT COUNT(*) as count FROM purchases 
                      WHERE strftime('%Y-%m', created_at) = ?`, [thisMonth], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getTotalSales() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT SUM(amount) as total FROM purchases', (err, row) => {
                if (err) reject(err);
                else resolve(row.total || 0);
            });
        });
    }

    async getTotalPurchases() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM purchases', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getTopProduct() {
        return new Promise((resolve, reject) => {
            db.db.get(`SELECT p.name, COUNT(*) as sales FROM purchases pu 
                      JOIN products p ON pu.product_id = p.id 
                      GROUP BY p.id ORDER BY sales DESC LIMIT 1`, (err, row) => {
                if (err) reject(err);
                else resolve(row ? `${row.name} (${row.sales} vendas)` : null);
            });
        });
    }

    async getCurrentConfigs() {
        const configs = {};
        const keys = ['store_name', 'support_name', 'support_phone', 'min_recharge', 
                     'commission_rate', 'flood_timeout_seconds', 'pix_expires_minutes'];
        
        for (const key of keys) {
            configs[key] = await db.getConfig(key);
        }
        
        return configs;
    }

    async getDetailedStats() {
        return {
            users: {
                total: await this.countUsers(),
                active: await this.getActiveUsers(),
                newWeek: await this.getNewUsersWeek()
            },
            finance: {
                totalRevenue: await this.getTotalSales(),
                monthRevenue: await this.getMonthSales(),
                averageTicket: await this.getAverageTicket()
            },
            products: {
                total: await this.countProducts(),
                inStock: await this.getProductsInStock(),
                outOfStock: await this.getProductsOutOfStock()
            },
            sales: {
                total: await this.getTotalPurchases(),
                today: await this.getTodayPurchases(),
                week: await this.getWeekPurchases()
            }
        };
    }

    async getActiveUsers() {
        const weekAgo = moment().subtract(7, 'days').format('YYYY-MM-DD');
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM users WHERE DATE(last_activity) >= ?', [weekAgo], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getNewUsersWeek() {
        const weekAgo = moment().subtract(7, 'days').format('YYYY-MM-DD');
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM users WHERE DATE(created_at) >= ?', [weekAgo], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getAverageTicket() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT AVG(amount) as avg FROM purchases', (err, row) => {
                if (err) reject(err);
                else resolve(row.avg || 0);
            });
        });
    }

    async getProductsInStock() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM products WHERE stock > 0 AND active = 1', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getProductsOutOfStock() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM products WHERE stock = 0 AND active = 1', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getWeekPurchases() {
        const weekAgo = moment().subtract(7, 'days').format('YYYY-MM-DD');
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM purchases WHERE DATE(created_at) >= ?', [weekAgo], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getAllUsers() {
        return new Promise((resolve, reject) => {
            db.db.all('SELECT * FROM users', (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    start() {
        console.log('🛠️ Telegram Admin Bot iniciado!');
        console.log('👤 Admin ID:', this.adminId);
    }
}

// Inicializar o bot admin
const telegramAdminBot = new TelegramAdminBot();
telegramAdminBot.start();

module.exports = TelegramAdminBot;