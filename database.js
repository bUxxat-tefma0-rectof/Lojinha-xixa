const sqlite3 = require('sqlite3').verbose();
const path = require('path');
require('dotenv').config();

class Database {
    constructor() {
        this.db = new sqlite3.Database(process.env.DATABASE_PATH || './database.db');
        this.init();
    }

    init() {
        // Tabela de usuários
        this.db.run(`
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE,
                whatsapp_number TEXT,
                username TEXT,
                balance REAL DEFAULT 0.0,
                bonus REAL DEFAULT 0.0,
                affiliate_code TEXT UNIQUE,
                referrer_id INTEGER,
                commission_rate REAL DEFAULT 0.5,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                flood_count INTEGER DEFAULT 0,
                flood_timeout DATETIME
            )
        `);

        // Tabela de produtos
        this.db.run(`
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                category TEXT,
                image_url TEXT,
                active BOOLEAN DEFAULT 1,
                guarantee_days INTEGER DEFAULT 30,
                delivery_info TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Tabela de compras
        this.db.run(`
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending',
                purchase_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        `);

        // Tabela de transações PIX
        this.db.run(`
            CREATE TABLE IF NOT EXISTS pix_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                pix_key TEXT,
                qr_code TEXT,
                transaction_id TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                expires_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                paid_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        `);

        // Tabela de configurações do sistema
        this.db.run(`
            CREATE TABLE IF NOT EXISTS system_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // Tabela de rankings
        this.db.run(`
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT, -- 'purchases', 'recharges', 'gifts', 'balance'
                user_id INTEGER,
                username TEXT,
                value REAL,
                count INTEGER DEFAULT 1,
                month INTEGER,
                year INTEGER,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        `);

        // Tabela de alertas de produtos
        this.db.run(`
            CREATE TABLE IF NOT EXISTS product_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        `);

        // Tabela de gift cards
        this.db.run(`
            CREATE TABLE IF NOT EXISTS gift_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                amount REAL,
                used_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_at DATETIME,
                FOREIGN KEY (used_by) REFERENCES users (id)
            )
        `);

        // Inserir configurações padrão
        this.insertDefaultConfig();
    }

    insertDefaultConfig() {
        const configs = [
            ['store_name', 'JOÃOZINHO STORE BOT'],
            ['support_phone', '5544998312326'],
            ['support_name', 'JOÃO'],
            ['min_recharge', '1.00'],
            ['commission_rate', '0.50'],
            ['pix_expires_minutes', '30'],
            ['flood_timeout_seconds', '6'],
            ['max_flood_count', '3'],
            ['store_logo', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSltpwF6kTey6ImHK0Z76OBq2AmdNgMsS7irFzm7Xv4Ji9whMxq-eD6PO2Y&s=10'],
            ['whatsapp_group', 'https://chat.whatsapp.com/EAMz3pt1kPe9VPO9rK8ccF']
        ];

        configs.forEach(([key, value]) => {
            this.db.run(`INSERT OR IGNORE INTO system_config (key, value) VALUES (?, ?)`, [key, value]);
        });
    }

    // Métodos para usuários
    createUser(telegramId, username = null, whatsappNumber = null) {
        return new Promise((resolve, reject) => {
            const affiliateCode = this.generateAffiliateCode();
            this.db.run(
                `INSERT OR IGNORE INTO users (telegram_id, username, whatsapp_number, affiliate_code) VALUES (?, ?, ?, ?)`,
                [telegramId, username, whatsappNumber, affiliateCode],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });
    }

    getUserByTelegramId(telegramId) {
        return new Promise((resolve, reject) => {
            this.db.get(
                `SELECT * FROM users WHERE telegram_id = ?`,
                [telegramId],
                (err, row) => {
                    if (err) reject(err);
                    else resolve(row);
                }
            );
        });
    }

    updateUserBalance(userId, amount, operation = 'add') {
        return new Promise((resolve, reject) => {
            const sign = operation === 'add' ? '+' : '-';
            this.db.run(
                `UPDATE users SET balance = balance ${sign} ?, last_activity = CURRENT_TIMESTAMP WHERE id = ?`,
                [Math.abs(amount), userId],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.changes);
                }
            );
        });
    }

    // Métodos para produtos
    createProduct(name, description, price, stock = 0, category = 'premium') {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT INTO products (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)`,
                [name, description, price, stock, category],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });
    }

    getAllProducts() {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT * FROM products WHERE active = 1 ORDER BY name`,
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    getProductById(id) {
        return new Promise((resolve, reject) => {
            this.db.get(
                `SELECT * FROM products WHERE id = ?`,
                [id],
                (err, row) => {
                    if (err) reject(err);
                    else resolve(row);
                }
            );
        });
    }

    updateProductStock(productId, quantity, operation = 'subtract') {
        return new Promise((resolve, reject) => {
            const sign = operation === 'add' ? '+' : '-';
            this.db.run(
                `UPDATE products SET stock = stock ${sign} ? WHERE id = ?`,
                [Math.abs(quantity), productId],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.changes);
                }
            );
        });
    }

    // Métodos para transações PIX
    createPixTransaction(userId, amount) {
        return new Promise((resolve, reject) => {
            const transactionId = this.generateTransactionId();
            const pixKey = this.generatePixKey(amount, transactionId);
            const expiresAt = new Date(Date.now() + 30 * 60 * 1000); // 30 minutos

            this.db.run(
                `INSERT INTO pix_transactions (user_id, amount, pix_key, transaction_id, expires_at) VALUES (?, ?, ?, ?, ?)`,
                [userId, amount, pixKey, transactionId, expiresAt],
                function(err) {
                    if (err) reject(err);
                    else {
                        // Retornar a transação criada
                        resolve({
                            id: this.lastID,
                            transaction_id: transactionId,
                            pix_key: pixKey,
                            amount: amount,
                            expires_at: expiresAt
                        });
                    }
                }
            );
        });
    }

    // Métodos para compras
    createPurchase(userId, productId, amount) {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT INTO purchases (user_id, product_id, amount) VALUES (?, ?, ?)`,
                [userId, productId, amount],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });
    }

    getUserPurchases(userId) {
        return new Promise((resolve, reject) => {
            this.db.all(
                `SELECT p.*, pr.name as product_name FROM purchases p 
                 JOIN products pr ON p.product_id = pr.id 
                 WHERE p.user_id = ? ORDER BY p.created_at DESC`,
                [userId],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    // Métodos para ranking
    updateRanking(type, userId, username, value, month = null, year = null) {
        return new Promise((resolve, reject) => {
            const currentDate = new Date();
            const currentMonth = month || currentDate.getMonth() + 1;
            const currentYear = year || currentDate.getFullYear();

            this.db.run(
                `INSERT OR REPLACE INTO rankings (type, user_id, username, value, month, year) 
                 VALUES (?, ?, ?, ?, ?, ?)`,
                [type, userId, username, value, currentMonth, currentYear],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });
    }

    getRanking(type, month = null, year = null) {
        return new Promise((resolve, reject) => {
            const currentDate = new Date();
            const currentMonth = month || currentDate.getMonth() + 1;
            const currentYear = year || currentDate.getFullYear();

            this.db.all(
                `SELECT * FROM rankings WHERE type = ? AND month = ? AND year = ? 
                 ORDER BY value DESC, count DESC LIMIT 10`,
                [type, currentMonth, currentYear],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    // Métodos utilitários
    generateAffiliateCode() {
        return Math.random().toString(36).substr(2, 8).toUpperCase();
    }

    generateTransactionId() {
        return Date.now().toString() + Math.random().toString(36).substr(2, 5);
    }

    generatePixKey(amount, transactionId) {
        // Simular geração de chave PIX (substitua por integração real)
        const payload = `00020101021226830014BR.GOV.BCB.PIX2561qrcodespix.sejaefi.com.br/v2/${transactionId}5204000053039865802BR5905EFISA6008SAOPAULO62070503***6304E477`;
        return payload;
    }

    // Métodos para configurações
    getConfig(key) {
        return new Promise((resolve, reject) => {
            this.db.get(
                `SELECT value FROM system_config WHERE key = ?`,
                [key],
                (err, row) => {
                    if (err) reject(err);
                    else resolve(row ? row.value : null);
                }
            );
        });
    }

    setConfig(key, value) {
        return new Promise((resolve, reject) => {
            this.db.run(
                `INSERT OR REPLACE INTO system_config (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)`,
                [key, value],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.changes);
                }
            );
        });
    }

    // Método para fechar conexão
    close() {
        this.db.close();
    }
}

module.exports = new Database();