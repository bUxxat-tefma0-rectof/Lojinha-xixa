import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import config

class Database:
    def __init__(self, db_file: str = config.DATABASE_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                whatsapp_number TEXT,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                balance REAL DEFAULT 0.0,
                bonus REAL DEFAULT 0.0,
                affiliate_code TEXT UNIQUE,
                referred_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                stock INTEGER DEFAULT 0,
                category TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                pix_code TEXT,
                pix_expiration TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabela de compras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                delivery_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivered_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Tabela de configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de notificações de estoque
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Inserir produtos padrão se não existirem
        self.insert_default_products()
        self.insert_default_config()
    
    def insert_default_products(self):
        """Insere produtos padrão no banco de dados"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        for product in config.DEFAULT_PRODUCTS:
            cursor.execute('''
                INSERT OR IGNORE INTO products (name, price, description, stock, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (product['name'], product['price'], product['description'], product['stock'], product['category']))
        
        conn.commit()
        conn.close()
    
    def insert_default_config(self):
        """Insere configurações padrão do bot"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        default_config = {
            'bot_name': config.BOT_NAME,
            'support_phone': config.CALLMEBOT_PHONE,
            'support_group_link': config.SUPPORT_GROUP_LINK,
            'min_recharge': str(config.MIN_RECHARGE),
            'max_recharge': str(config.MAX_RECHARGE),
            'pix_expiration': str(config.PIX_EXPIRATION_MINUTES),
            'affiliate_commission': str(config.AFFILIATE_COMMISSION)
        }
        
        for key, value in default_config.items():
            cursor.execute('''
                INSERT OR REPLACE INTO bot_config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> Dict:
        """Obtém ou cria um usuário"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Verifica se o usuário existe
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        
        if user:
            # Atualiza última atividade
            cursor.execute('''
                UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                WHERE telegram_id = ?
            ''', (telegram_id,))
            
            user_dict = {
                'id': user[0], 'telegram_id': user[1], 'whatsapp_number': user[2],
                'username': user[3], 'first_name': user[4], 'last_name': user[5],
                'balance': user[6], 'bonus': user[7], 'affiliate_code': user[8],
                'referred_by': user[9], 'created_at': user[10], 'last_activity': user[11]
            }
        else:
            # Cria novo usuário
            affiliate_code = self.generate_affiliate_code()
            cursor.execute('''
                INSERT INTO users (telegram_id, username, first_name, last_name, affiliate_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, username, first_name, last_name, affiliate_code))
            
            user_id = cursor.lastrowid
            user_dict = {
                'id': user_id, 'telegram_id': telegram_id, 'whatsapp_number': None,
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'balance': 0.0, 'bonus': 0.0, 'affiliate_code': affiliate_code,
                'referred_by': None, 'created_at': datetime.now(), 'last_activity': datetime.now()
            }
        
        conn.commit()
        conn.close()
        return user_dict
    
    def generate_affiliate_code(self) -> str:
        """Gera um código de afiliado único"""
        import random
        import string
        
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE affiliate_code = ?', (code,))
            if not cursor.fetchone():
                conn.close()
                return code
            conn.close()
    
    def get_user_balance(self, telegram_id: int) -> float:
        """Obtém o saldo do usuário"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM users WHERE telegram_id = ?', (telegram_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0
    
    def update_user_balance(self, telegram_id: int, amount: float, operation: str = 'add'):
        """Atualiza o saldo do usuário"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if operation == 'add':
            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE telegram_id = ?
            ''', (amount, telegram_id))
        elif operation == 'subtract':
            cursor.execute('''
                UPDATE users SET balance = balance - ? WHERE telegram_id = ?
            ''', (amount, telegram_id))
        elif operation == 'set':
            cursor.execute('''
                UPDATE users SET balance = ? WHERE telegram_id = ?
            ''', (amount, telegram_id))
        
        conn.commit()
        conn.close()
    
    def get_products(self, category: str = None) -> List[Dict]:
        """Obtém lista de produtos"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT * FROM products WHERE category = ? AND is_active = 1', (category,))
        else:
            cursor.execute('SELECT * FROM products WHERE is_active = 1')
        
        products = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': p[0], 'name': p[1], 'price': p[2], 'description': p[3],
                'stock': p[4], 'category': p[5], 'is_active': p[6], 'created_at': p[7]
            }
            for p in products
        ]
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        """Obtém um produto específico"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        conn.close()
        
        if product:
            return {
                'id': product[0], 'name': product[1], 'price': product[2],
                'description': product[3], 'stock': product[4], 'category': product[5],
                'is_active': product[6], 'created_at': product[7]
            }
        return None
    
    def create_transaction(self, user_id: int, type: str, amount: float, description: str = None) -> int:
        """Cria uma nova transação"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (user_id, type, amount, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, type, amount, description))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id
    
    def create_purchase(self, user_id: int, product_id: int, amount: float) -> int:
        """Cria uma nova compra"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO purchases (user_id, product_id, amount)
            VALUES (?, ?, ?)
        ''', (user_id, product_id, amount))
        
        purchase_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return purchase_id
    
    def get_user_transactions(self, telegram_id: int, limit: int = 50) -> List[Dict]:
        """Obtém transações do usuário"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.* FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE u.telegram_id = ?
            ORDER BY t.created_at DESC
            LIMIT ?
        ''', (telegram_id, limit))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': t[0], 'user_id': t[1], 'type': t[2], 'amount': t[3],
                'description': t[4], 'status': t[5], 'pix_code': t[6],
                'pix_expiration': t[7], 'created_at': t[8], 'completed_at': t[9]
            }
            for t in transactions
        ]
    
    def get_user_purchases(self, telegram_id: int, limit: int = 50) -> List[Dict]:
        """Obtém compras do usuário"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, pr.name as product_name FROM purchases p
            JOIN users u ON p.user_id = u.id
            JOIN products pr ON p.product_id = pr.id
            WHERE u.telegram_id = ?
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (telegram_id, limit))
        
        purchases = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': p[0], 'user_id': p[1], 'product_id': p[2], 'amount': p[3],
                'status': p[4], 'delivery_info': p[5], 'created_at': p[6],
                'delivered_at': p[7], 'product_name': p[8]
            }
            for p in purchases
        ]
    
    def get_ranking_data(self, ranking_type: str, limit: int = 10) -> List[Dict]:
        """Obtém dados para rankings"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if ranking_type == 'recargas':
            cursor.execute('''
                SELECT u.first_name, u.username, SUM(t.amount) as total
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE t.type = 'recharge' AND t.status = 'completed'
                AND t.created_at >= datetime('now', 'start of month')
                GROUP BY u.id
                ORDER BY total DESC
                LIMIT ?
            ''', (limit,))
        elif ranking_type == 'compras':
            cursor.execute('''
                SELECT u.first_name, u.username, COUNT(p.id) as total
                FROM purchases p
                JOIN users u ON p.user_id = u.id
                WHERE p.status = 'delivered'
                AND p.created_at >= datetime('now', 'start of month')
                GROUP BY u.id
                ORDER BY total DESC
                LIMIT ?
            ''', (limit,))
        elif ranking_type == 'gift_card':
            cursor.execute('''
                SELECT u.first_name, u.username, SUM(t.amount) as total
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE t.type = 'gift_card' AND t.status = 'completed'
                GROUP BY u.id
                ORDER BY total DESC
                LIMIT ?
            ''', (limit,))
        elif ranking_type == 'saldo':
            cursor.execute('''
                SELECT first_name, username, balance
                FROM users
                ORDER BY balance DESC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        if ranking_type == 'recargas' or ranking_type == 'gift_card':
            return [{'name': r[0] or r[1], 'total': r[2]} for r in results]
        elif ranking_type == 'compras':
            return [{'name': r[0] or r[1], 'total': r[2]} for r in results]
        elif ranking_type == 'saldo':
            return [{'name': r[0] or r[1], 'balance': r[2]} for r in results]
        
        return []
    
    def get_bot_config(self, key: str = None) -> Dict:
        """Obtém configurações do bot"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if key:
            cursor.execute('SELECT key, value FROM bot_config WHERE key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return {result[0]: result[1]} if result else {}
        else:
            cursor.execute('SELECT key, value FROM bot_config')
            results = cursor.fetchall()
            conn.close()
            return {r[0]: r[1] for r in results}
    
    def update_bot_config(self, key: str, value: str):
        """Atualiza configuração do bot"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def search_products(self, query: str) -> List[Dict]:
        """Pesquisa produtos por nome"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM products 
            WHERE name LIKE ? AND is_active = 1
            ORDER BY name
        ''', (f'%{query}%',))
        
        products = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': p[0], 'name': p[1], 'price': p[2], 'description': p[3],
                'stock': p[4], 'category': p[5], 'is_active': p[6], 'created_at': p[7]
            }
            for p in products
        ]