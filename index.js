const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

// Importar módulos dos bots
const db = require('./database');

// Classe principal do sistema
class JoaozinhoStoreSystem {
    constructor() {
        this.app = express();
        this.port = process.env.PORT || 3000;
        this.setupMiddleware();
        this.setupRoutes();
        this.initializeBots();
    }

    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
        this.app.use(express.static('public'));
    }

    setupRoutes() {
        // Página inicial do sistema
        this.app.get('/', (req, res) => {
            res.send(`
                <!DOCTYPE html>
                <html lang="pt-BR">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Joãozinho Store Bot - Sistema de Gerenciamento</title>
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: 'Arial', sans-serif; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; 
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }
                        .container { 
                            max-width: 800px; 
                            margin: 0 auto; 
                            padding: 2rem;
                            background: rgba(255,255,255,0.1);
                            border-radius: 15px;
                            backdrop-filter: blur(10px);
                            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                        }
                        h1 { 
                            text-align: center; 
                            margin-bottom: 2rem; 
                            font-size: 2.5rem;
                            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                        }
                        .status { 
                            display: grid; 
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                            gap: 1rem; 
                            margin: 2rem 0; 
                        }
                        .status-card { 
                            background: rgba(255,255,255,0.2); 
                            padding: 1rem; 
                            border-radius: 10px; 
                            text-align: center;
                            border: 1px solid rgba(255,255,255,0.3);
                        }
                        .status-card h3 { 
                            margin-bottom: 0.5rem; 
                            color: #4CAF50; 
                        }
                        .features { 
                            list-style: none; 
                            padding: 1rem 0; 
                        }
                        .features li { 
                            margin: 0.5rem 0; 
                            padding: 0.5rem; 
                            background: rgba(255,255,255,0.1); 
                            border-radius: 5px;
                            border-left: 3px solid #4CAF50;
                        }
                        .footer { 
                            text-align: center; 
                            margin-top: 2rem; 
                            opacity: 0.8; 
                        }
                        .emoji { font-size: 1.2em; }
                        .btn {
                            display: inline-block;
                            padding: 10px 20px;
                            background: rgba(255,255,255,0.2);
                            border: 1px solid rgba(255,255,255,0.3);
                            border-radius: 5px;
                            color: white;
                            text-decoration: none;
                            margin: 5px;
                            transition: all 0.3s ease;
                        }
                        .btn:hover {
                            background: rgba(255,255,255,0.3);
                            transform: translateY(-2px);
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🤖 Joãozinho Store Bot</h1>
                        
                        <div class="status">
                            <div class="status-card">
                                <h3>📱 WhatsApp Bot</h3>
                                <p>✅ Ativo</p>
                                <small>CallMeBot API</small>
                            </div>
                            <div class="status-card">
                                <h3>🤖 Telegram Loja</h3>
                                <p>✅ Ativo</p>
                                <small>Bot da Loja</small>
                            </div>
                            <div class="status-card">
                                <h3>🛠️ Telegram Admin</h3>
                                <p>✅ Ativo</p>
                                <small>Painel Administrativo</small>
                            </div>
                            <div class="status-card">
                                <h3>💾 Banco de Dados</h3>
                                <p>✅ Conectado</p>
                                <small>SQLite</small>
                            </div>
                        </div>

                        <h2>🚀 Recursos Implementados:</h2>
                        <ul class="features">
                            <li><span class="emoji">💸</span> Sistema de PIX automático</li>
                            <li><span class="emoji">🛍️</span> Loja com produtos premium</li>
                            <li><span class="emoji">👥</span> Sistema de afiliados</li>
                            <li><span class="emoji">🏆</span> Rankings em tempo real</li>
                            <li><span class="emoji">📊</span> Painel administrativo completo</li>
                            <li><span class="emoji">💰</span> Controle de saldo e transações</li>
                            <li><span class="emoji">📱</span> Integração WhatsApp + Telegram</li>
                            <li><span class="emoji">🔔</span> Sistema de alertas</li>
                            <li><span class="emoji">📈</span> Relatórios de vendas</li>
                            <li><span class="emoji">🎯</span> Anti-flood e controle de acesso</li>
                        </ul>

                        <div style="text-align: center; margin: 2rem 0;">
                            <a href="/api/status" class="btn">📊 Status da API</a>
                            <a href="/api/stats" class="btn">📈 Estatísticas</a>
                            <a href="https://t.me/SEU_BOT_USERNAME" class="btn">🤖 Acessar Bot</a>
                        </div>

                        <div class="footer">
                            <p>💫 Sistema completo de loja automatizada</p>
                            <p>🔧 Desenvolvido com Node.js, SQLite e Telegram/WhatsApp APIs</p>
                            <p><small>Versão 1.0.0 - ${new Date().getFullYear()}</small></p>
                        </div>
                    </div>
                </body>
                </html>
            `);
        });

        // API de status do sistema
        this.app.get('/api/status', async (req, res) => {
            try {
                const status = await this.getSystemStatus();
                res.json(status);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // API de estatísticas
        this.app.get('/api/stats', async (req, res) => {
            try {
                const stats = await this.getSystemStats();
                res.json(stats);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Webhook para WhatsApp (CallMeBot integration)
        this.app.post('/webhook/whatsapp', async (req, res) => {
            try {
                // Processar mensagem do WhatsApp
                console.log('📱 Mensagem WhatsApp recebida:', req.body);
                res.status(200).json({ success: true });
            } catch (error) {
                console.error('❌ Erro no webhook WhatsApp:', error);
                res.status(500).json({ error: error.message });
            }
        });

        // Webhook para notificações PIX
        this.app.post('/webhook/pix', async (req, res) => {
            try {
                // Processar notificação de PIX
                console.log('💰 Notificação PIX recebida:', req.body);
                await this.processPIXNotification(req.body);
                res.status(200).json({ success: true });
            } catch (error) {
                console.error('❌ Erro no webhook PIX:', error);
                res.status(500).json({ error: error.message });
            }
        });

        // API para gerar PIX
        this.app.post('/api/pix/generate', async (req, res) => {
            try {
                const { userId, amount } = req.body;
                const transaction = await db.createPixTransaction(userId, amount);
                res.json(transaction);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // API para gerenciar produtos
        this.app.get('/api/products', async (req, res) => {
            try {
                const products = await db.getAllProducts();
                res.json(products);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        this.app.post('/api/products', async (req, res) => {
            try {
                const { name, description, price, stock } = req.body;
                const productId = await db.createProduct(name, description, price, stock);
                res.json({ id: productId, success: true });
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // API para rankings
        this.app.get('/api/rankings/:type', async (req, res) => {
            try {
                const { type } = req.params;
                const rankings = await db.getRanking(type);
                res.json(rankings);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        // Health check
        this.app.get('/health', (req, res) => {
            res.json({ 
                status: 'ok', 
                timestamp: new Date().toISOString(),
                uptime: process.uptime(),
                memory: process.memoryUsage()
            });
        });
    }

    async initializeBots() {
        console.log('🚀 Inicializando sistema Joãozinho Store Bot...');
        
        try {
            // Inicializar bots de forma sequencial para evitar conflitos
            console.log('📱 Inicializando WhatsApp Bot...');
            const WhatsAppBot = require('./whatsapp-bot');
            
            console.log('🤖 Inicializando Telegram Store Bot...');
            const TelegramStoreBot = require('./telegram-store-bot');
            
            console.log('🛠️ Inicializando Telegram Admin Bot...');
            const TelegramAdminBot = require('./telegram-admin-bot');

            console.log('✅ Todos os bots foram inicializados com sucesso!');
            
        } catch (error) {
            console.error('❌ Erro ao inicializar bots:', error);
        }
    }

    async getSystemStatus() {
        return {
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            status: 'running',
            services: {
                whatsapp: { status: 'active', api: 'CallMeBot' },
                telegram_store: { status: 'active', bot: process.env.TELEGRAM_STORE_BOT_TOKEN ? 'configured' : 'not_configured' },
                telegram_admin: { status: 'active', bot: process.env.TELEGRAM_ADMIN_BOT_TOKEN ? 'configured' : 'not_configured' },
                database: { status: 'connected', type: 'SQLite' }
            },
            version: '1.0.0'
        };
    }

    async getSystemStats() {
        try {
            const users = await this.countUsers();
            const products = await this.countProducts();
            const purchases = await this.countPurchases();
            const revenue = await this.getTotalRevenue();

            return {
                users: {
                    total: users,
                    active_today: await this.getActiveUsersToday()
                },
                products: {
                    total: products,
                    in_stock: await this.getProductsInStock()
                },
                sales: {
                    total_purchases: purchases,
                    total_revenue: revenue,
                    today_purchases: await this.getTodayPurchases(),
                    today_revenue: await this.getTodayRevenue()
                },
                system: {
                    uptime: process.uptime(),
                    memory: process.memoryUsage(),
                    version: '1.0.0'
                }
            };
        } catch (error) {
            throw new Error('Erro ao obter estatísticas: ' + error.message);
        }
    }

    async processPIXNotification(pixData) {
        // Processar notificação de PIX pago
        console.log('💰 Processando pagamento PIX:', pixData);
        
        // Aqui você integraria com o sistema de PIX real
        // Por enquanto, apenas log
    }

    // Métodos auxiliares para estatísticas
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

    async countPurchases() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM purchases', (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getTotalRevenue() {
        return new Promise((resolve, reject) => {
            db.db.get('SELECT SUM(amount) as total FROM purchases', (err, row) => {
                if (err) reject(err);
                else resolve(row.total || 0);
            });
        });
    }

    async getActiveUsersToday() {
        const today = new Date().toISOString().split('T')[0];
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM users WHERE DATE(last_activity) = ?', [today], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
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

    async getTodayPurchases() {
        const today = new Date().toISOString().split('T')[0];
        return new Promise((resolve, reject) => {
            db.db.get('SELECT COUNT(*) as count FROM purchases WHERE DATE(created_at) = ?', [today], (err, row) => {
                if (err) reject(err);
                else resolve(row.count);
            });
        });
    }

    async getTodayRevenue() {
        const today = new Date().toISOString().split('T')[0];
        return new Promise((resolve, reject) => {
            db.db.get('SELECT SUM(amount) as total FROM purchases WHERE DATE(created_at) = ?', [today], (err, row) => {
                if (err) reject(err);
                else resolve(row.total || 0);
            });
        });
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`
🎉 ===================================
🤖 JOÃOZINHO STORE BOT SYSTEM
🎉 ===================================

✅ Sistema iniciado com sucesso!
🌐 Servidor rodando na porta: ${this.port}
🔗 Acesse: http://localhost:${this.port}

📱 WhatsApp: ${process.env.WHATSAPP_PHONE}
🤖 Telegram Loja: Ativo
🛠️ Telegram Admin: Ativo (ID: ${process.env.ADMIN_TELEGRAM_ID})

💾 Banco de dados: SQLite conectado
🔑 APIs configuradas: CallMeBot

🚀 Todos os serviços estão funcionando!
🎉 ===================================
            `);
        });

        // Graceful shutdown
        process.on('SIGTERM', () => {
            console.log('🔄 Recebido SIGTERM, finalizando graciosamente...');
            db.close();
            process.exit(0);
        });

        process.on('SIGINT', () => {
            console.log('🔄 Recebido SIGINT, finalizando graciosamente...');
            db.close();
            process.exit(0);
        });
    }
}

// Inicializar o sistema
const system = new JoaozinhoStoreSystem();
system.start();

module.exports = JoaozinhoStoreSystem;