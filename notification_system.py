import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config
from database import Database
from telegram_bot import TelegramBot
from whatsapp_bot import WhatsAppBot

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self):
        self.db = Database()
        self.telegram_bot = None
        self.whatsapp_bot = None
        self.notification_queue = []
        
    def set_bots(self, telegram_bot: TelegramBot, whatsapp_bot: WhatsAppBot):
        """Define as instâncias dos bots"""
        self.telegram_bot = telegram_bot
        self.whatsapp_bot = whatsapp_bot
    
    async def check_stock_notifications(self):
        """Verifica e envia notificações de estoque"""
        try:
            # Busca produtos com estoque baixo
            products = self.db.get_products()
            low_stock_products = [p for p in products if p['stock'] <= 5]
            
            if low_stock_products:
                # Notifica administradores
                await self._notify_admins_stock_low(low_stock_products)
                
                # Notifica usuários que ativaram alertas
                await self._notify_users_stock_alerts(low_stock_products)
                
        except Exception as e:
            logger.error(f"Erro ao verificar notificações de estoque: {e}")
    
    async def check_payment_notifications(self):
        """Verifica e envia notificações de pagamento"""
        try:
            # Busca transações pendentes
            pending_transactions = self._get_pending_transactions()
            
            for transaction in pending_transactions:
                # Verifica se está próximo de expirar
                if self._is_near_expiration(transaction):
                    await self._notify_payment_expiring(transaction)
                
                # Verifica se expirou
                if self._is_expired(transaction):
                    await self._notify_payment_expired(transaction)
                    
        except Exception as e:
            logger.error(f"Erro ao verificar notificações de pagamento: {e}")
    
    async def check_delivery_notifications(self):
        """Verifica e envia notificações de entrega"""
        try:
            # Busca compras pendentes de entrega
            pending_deliveries = self._get_pending_deliveries()
            
            for delivery in pending_deliveries:
                # Verifica se está atrasado
                if self._is_delivery_delayed(delivery):
                    await self._notify_delivery_delayed(delivery)
                    
        except Exception as e:
            logger.error(f"Erro ao verificar notificações de entrega: {e}")
    
    async def _notify_admins_stock_low(self, products: List[Dict]):
        """Notifica administradores sobre estoque baixo"""
        if not self.telegram_bot:
            return
            
        try:
            message = "🚨 *ALERTA DE ESTOQUE BAIXO!*\n\n"
            message += "Os seguintes produtos estão com estoque baixo:\n\n"
            
            for product in products:
                message += f"📦 {product['name']}\n"
                message += f"   Estoque atual: {product['stock']}\n"
                message += f"   Categoria: {product['category']}\n\n"
            
            message += "⚠️ Abasteça o estoque o quanto antes!"
            
            # Envia para todos os administradores
            admin_ids = [config.ADMIN_ID]  # Adicione outros IDs de admin aqui
            
            for admin_id in admin_ids:
                try:
                    await self.telegram_bot.application.bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Erro ao notificar admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Erro ao notificar admins sobre estoque: {e}")
    
    async def _notify_users_stock_alerts(self, products: List[Dict]):
        """Notifica usuários sobre produtos em estoque"""
        try:
            # Busca usuários que ativaram alertas para estes produtos
            for product in products:
                users_with_alerts = self._get_users_with_stock_alerts(product['id'])
                
                for user in users_with_alerts:
                    try:
                        message = f"🔔 *PRODUTO EM ESTOQUE!*\n\n"
                        message += f"🎟️ {product['name']}\n"
                        message += f"💰 Preço: R${product['price']:.2f}\n"
                        message += f"📥 Estoque: {product['stock']}\n\n"
                        message += "Use /start para comprar agora!"
                        
                        if user['telegram_id']:
                            await self.telegram_bot.application.bot.send_message(
                                chat_id=user['telegram_id'],
                                text=message,
                                parse_mode='Markdown'
                            )
                        
                        if user['whatsapp_number'] and self.whatsapp_bot:
                            self.whatsapp_bot.send_message(
                                user['whatsapp_number'],
                                message
                            )
                            
                    except Exception as e:
                        logger.error(f"Erro ao notificar usuário {user['id']}: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao notificar usuários sobre estoque: {e}")
    
    async def _notify_payment_expiring(self, transaction: Dict):
        """Notifica sobre pagamento próximo de expirar"""
        try:
            user = self._get_user_by_id(transaction['user_id'])
            if not user:
                return
            
            message = "⏰ *PAGAMENTO EXPIRANDO EM BREVE!*\n\n"
            message += f"💰 Valor: R${transaction['amount']:.2f}\n"
            message += f"📅 Expira em: {transaction['pix_expiration']}\n\n"
            message += "⚠️ Complete o pagamento antes que expire!"
            
            if user['telegram_id']:
                await self.telegram_bot.application.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=message,
                    parse_mode='Markdown'
                )
            
            if user['whatsapp_number'] and self.whatsapp_bot:
                self.whatsapp_bot.send_message(
                    user['whatsapp_number'],
                    message
                )
                
        except Exception as e:
            logger.error(f"Erro ao notificar sobre pagamento expirando: {e}")
    
    async def _notify_payment_expired(self, transaction: Dict):
        """Notifica sobre pagamento expirado"""
        try:
            user = self._get_user_by_id(transaction['user_id'])
            if not user:
                return
            
            message = "*⚠️ Solicitação Negada!*\n\n"
            message += "Desculpe, sua recarga falhou porque o *PIX não foi pago dentro do prazo*. ⏳❌"
            
            if user['telegram_id']:
                await self.telegram_bot.application.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=message,
                    parse_mode='Markdown'
                )
            
            if user['whatsapp_number'] and self.whatsapp_bot:
                self.whatsapp_bot.send_message(
                    user['whatsapp_number'],
                    message
                )
                
        except Exception as e:
            logger.error(f"Erro ao notificar sobre pagamento expirado: {e}")
    
    async def _notify_delivery_delayed(self, delivery: Dict):
        """Notifica sobre entrega atrasada"""
        try:
            user = self._get_user_by_id(delivery['user_id'])
            if not user:
                return
            
            message = "⏰ *ENTREGA ATRASADA*\n\n"
            message += f"📦 Produto: {delivery['product_name']}\n"
            message += f"📅 Pedido em: {delivery['created_at']}\n\n"
            message += "Estamos processando sua entrega. Em caso de dúvidas, entre em contato com o suporte."
            
            if user['telegram_id']:
                await self.telegram_bot.application.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=message,
                    parse_mode='Markdown'
                )
            
            if user['whatsapp_number'] and self.whatsapp_bot:
                self.whatsapp_bot.send_message(
                    user['whatsapp_number'],
                    message
                )
                
        except Exception as e:
            logger.error(f"Erro ao notificar sobre entrega atrasada: {e}")
    
    def _get_pending_transactions(self) -> List[Dict]:
        """Busca transações pendentes"""
        try:
            conn = self.db.db_file
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM transactions 
                WHERE status = 'pending' 
                AND pix_code IS NOT NULL
                AND pix_expiration IS NOT NULL
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': r[0], 'user_id': r[1], 'type': r[2],
                    'amount': r[3], 'description': r[4], 'status': r[5],
                    'pix_code': r[6], 'pix_expiration': r[7],
                    'created_at': r[8], 'completed_at': r[9]
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar transações pendentes: {e}")
            return []
    
    def _get_pending_deliveries(self) -> List[Dict]:
        """Busca entregas pendentes"""
        try:
            conn = self.db.db_file
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, pr.name as product_name FROM purchases p
                JOIN products pr ON p.product_id = pr.id
                WHERE p.status = 'pending'
                AND p.created_at < datetime('now', '-24 hours')
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': r[0], 'user_id': r[1], 'product_id': r[2],
                    'amount': r[3], 'status': r[4], 'delivery_info': r[5],
                    'created_at': r[6], 'delivered_at': r[7],
                    'product_name': r[8]
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar entregas pendentes: {e}")
            return []
    
    def _get_users_with_stock_alerts(self, product_id: int) -> List[Dict]:
        """Busca usuários com alertas de estoque ativos"""
        try:
            conn = self.db.db_file
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.* FROM users u
                JOIN stock_notifications sn ON u.id = sn.user_id
                WHERE sn.product_id = ? AND sn.is_active = 1
            ''', (product_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': r[0], 'telegram_id': r[1], 'whatsapp_number': r[2],
                    'username': r[3], 'first_name': r[4], 'last_name': r[5],
                    'balance': r[6], 'bonus': r[7], 'affiliate_code': r[8],
                    'referred_by': r[9], 'created_at': r[10], 'last_activity': r[11]
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuários com alertas: {e}")
            return []
    
    def _get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        try:
            conn = self.db.db_file
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0], 'telegram_id': result[1], 'whatsapp_number': result[2],
                    'username': result[3], 'first_name': result[4], 'last_name': result[5],
                    'balance': result[6], 'bonus': result[7], 'affiliate_code': result[8],
                    'referred_by': result[9], 'created_at': result[10], 'last_activity': result[11]
                }
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar usuário: {e}")
            return None
    
    def _is_near_expiration(self, transaction: Dict) -> bool:
        """Verifica se transação está próxima de expirar (5 minutos)"""
        try:
            expiration = datetime.fromisoformat(transaction['pix_expiration'])
            now = datetime.now()
            time_left = expiration - now
            
            return timedelta(minutes=0) < time_left <= timedelta(minutes=5)
            
        except Exception as e:
            logger.error(f"Erro ao verificar expiração: {e}")
            return False
    
    def _is_expired(self, transaction: Dict) -> bool:
        """Verifica se transação expirou"""
        try:
            expiration = datetime.fromisoformat(transaction['pix_expiration'])
            now = datetime.now()
            
            return now > expiration
            
        except Exception as e:
            logger.error(f"Erro ao verificar expiração: {e}")
            return False
    
    def _is_delivery_delayed(self, delivery: Dict) -> bool:
        """Verifica se entrega está atrasada (mais de 24 horas)"""
        try:
            created_at = datetime.fromisoformat(delivery['created_at'])
            now = datetime.now()
            time_passed = now - created_at
            
            return time_passed > timedelta(hours=24)
            
        except Exception as e:
            logger.error(f"Erro ao verificar atraso de entrega: {e}")
            return False
    
    async def start_notification_loop(self):
        """Inicia loop de notificações"""
        logger.info("Sistema de notificações iniciado")
        
        while True:
            try:
                # Verifica notificações de estoque
                await self.check_stock_notifications()
                
                # Verifica notificações de pagamento
                await self.check_payment_notifications()
                
                # Verifica notificações de entrega
                await self.check_delivery_notifications()
                
                # Aguarda 5 minutos antes da próxima verificação
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Erro no loop de notificações: {e}")
                await asyncio.sleep(60)  # Aguarda 1 minuto em caso de erro