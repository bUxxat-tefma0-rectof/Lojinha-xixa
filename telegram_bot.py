import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
import config
from database import Database
from pix_generator import PixGenerator
from whatsapp_bot import WhatsAppBot
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.db = Database()
        self.pix_generator = PixGenerator()
        self.whatsapp_bot = WhatsAppBot()
        self.admin_id = config.ADMIN_ID
        
        # Estados dos usuários
        self.user_states = {}
        self.admin_states = {}
        
        # Inicializa bot
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers do bot"""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("pix", self.pix_command))
        self.application.add_handler(CommandHandler("historico", self.historico_command))
        self.application.add_handler(CommandHandler("afiliados", self.afiliados_command))
        self.application.add_handler(CommandHandler("id", self.id_command))
        self.application.add_handler(CommandHandler("ranking", self.ranking_command))
        self.application.add_handler(CommandHandler("alertas", self.alertas_command))
        
        # Comandos de administração
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Callbacks de botões inline
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Mensagens de texto
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Obtém configurações do bot
        bot_config = self.db.get_bot_config()
        
        # Cria teclado inline
        keyboard = [
            [
                InlineKeyboardButton("💎 Logins | Contas Premium", callback_data="products"),
                InlineKeyboardButton("🪪 PERFIL", callback_data="profile")
            ],
            [
                InlineKeyboardButton("💰 RECARGA", callback_data="recharge"),
                InlineKeyboardButton("🎖️ Ranking", callback_data="ranking")
            ],
            [
                InlineKeyboardButton("👩‍💻 Suporte", callback_data="support"),
                InlineKeyboardButton("ℹ️ Informações", callback_data="info")
            ],
            [
                InlineKeyboardButton("🔎 Pesquisar Serviços", callback_data="search")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Mensagem principal
        message = f"""🥇{bot_config.get('bot_name', config.BOT_NAME)}

🥇Descubra como nosso bot pode transformar sua experiência de compras!
Ele facilita a busca por diversos produtos e serviços, garantindo que você encontre o que precisa com o melhor preço e excelente custo-benefício.
Importante: Não realizamos reembolsos em dinheiro. O suporte estará disponível por até 48 horas após a entrega das informações, com reembolso em créditos no bot, se necessário.

👥Grupo De Clientes:
{config.SUPPORT_GROUP_LINK}

👨‍💻 Link De Suporte:
{bot_config.get('support_phone', config.CALLMEBOT_PHONE)}

ℹ️Seus Dados:
🆔ID: {user_data['affiliate_code']}
💸Saldo Atual: R${user_data['balance']:.2f}
🪪Usuário: {user.first_name or 'Usuário'}

https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSltpwF6kTey6ImHK0Z76OBq2AmdNgMsS7irFzm7Xv4Ji9whMxq-eD6PO2Y&s=10"""
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def pix_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /pix"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "Você enviou em um formato incorreto. Envie /pix e o valor que deseja...\nExemplo:\n/pix 10\n/pix 6.26"
            )
            return
        
        try:
            amount = float(context.args[0])
            await self._handle_pix_recharge(update, context, amount)
        except ValueError:
            await update.message.reply_text(
                "Você enviou em um formato incorreto. Envie /pix e o valor que deseja...\nExemplo:\n/pix 10\n/pix 6.26"
            )
    
    async def _handle_pix_recharge(self, update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
        """Processa recarga PIX"""
        user = update.effective_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Verifica limites
        bot_config = self.db.get_bot_config()
        min_amount = float(bot_config.get('min_recharge', '1.00'))
        max_amount = float(bot_config.get('max_recharge', '1000.00'))
        
        if amount < min_amount:
            await update.message.reply_text(f"Valor mínimo para recarga é R${min_amount:.2f}")
            return
        
        if amount > max_amount:
            await update.message.reply_text(f"Valor máximo para recarga é R${max_amount:.2f}")
            return
        
        # Gera PIX
        pix_result = self.pix_generator.generate_pix(amount, user_data['id'])
        
        if pix_result['success']:
            await self._send_pix_payment(update, context, pix_result)
        else:
            await update.message.reply_text(f"Erro ao gerar PIX: {pix_result['error']}")
    
    async def _send_pix_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, pix_result: Dict):
        """Envia informações de pagamento PIX"""
        message = f"""*⏳ Gerando PIX...*

Aguarde um momento! 💰

*💰 ADICIONAR SALDO COM PIX AUTOMÁTICO 💠*

⚠️ Você está prestes a adicionar saldo ao bot!

Escaneie o *QR Code* acima ou utilize o *código PIX* enviado abaixo.

O PIX expira em *30 minutos*, pague dentro do prazo.

O saldo será creditado em até *1 minuto* após o pagamento.

*⚠️ ADICIONE APENAS O QUE FOR USAR!*
_Não realizamos reembolsos._

━━━━━━━━❪❃❫━━━━━━━━

*🆔 ID da Compra:*
*💰 Valor:* R${pix_result['amount']:.2f}
*📅 Vencimento:* {pix_result['expiration_formatted']}

━━━━━━━━❪❃❫━━━━━━━━

*🔑 O código PIX foi enviado abaixo para facilitar o pagamento!*

`{pix_result['pix_code']}`"""
        
        # Envia mensagem principal
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        # Envia QR Code se disponível
        if pix_result['qr_code']:
            with open(pix_result['qr_code'], 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="QR Code para pagamento PIX"
                )
    
    async def historico_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /historico"""
        user = update.effective_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        purchases = self.db.get_user_purchases(user.id)
        transactions = self.db.get_user_transactions(user.id)
        
        # Gera arquivo de histórico
        history_file = self._generate_history_file(user_data, purchases, transactions)
        
        # Envia arquivo
        with open(history_file, 'rb') as doc:
            await update.message.reply_document(
                document=doc,
                filename=f"historico_{user_data['affiliate_code']}.txt",
                caption="📋 Seu histórico detalhado de compras e transações"
            )
    
    async def afiliados_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /afiliados"""
        user = update.effective_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        bot_config = self.db.get_bot_config()
        affiliate_link = f"https://t.me/{config.BOT_NAME.lower().replace(' ', '')}?start={user_data['affiliate_code']}"
        
        message = f"""ℹ️ Status:
📊 Comissão por Indicação: {float(bot_config.get('affiliate_commission', '0.5')) * 100}%
👥 Total de Afiliados: 0
🔗 Link para Indicar: {affiliate_link}

Como Funciona?
Copie seu link de indicação e envie para outras pessoas.
Cada vez que alguém indicado por você fizer uma recarga no bot, você receberá uma porcentagem desse valor!
Por exemplo, com uma comissão de {float(bot_config.get('affiliate_commission', '0.5')) * 100}%, se 5 pessoas indicadas recarregarem R$10,00 cada, você receberá R${5 * 10 * float(bot_config.get('affiliate_commission', '0.5')):.2f}.
Indique mais e aumente seus ganhos!"""
        
        await update.message.reply_text(message)
    
    async def id_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /id"""
        user = update.effective_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        await update.message.reply_text(f"🆔 Seu id é: {user_data['affiliate_code']}")
    
    async def ranking_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ranking"""
        keyboard = [
            [
                InlineKeyboardButton("🏆 Serviços", callback_data="ranking_services"),
                InlineKeyboardButton("💰 Recargas", callback_data="ranking_recharges")
            ],
            [
                InlineKeyboardButton("🛒 Compras", callback_data="ranking_purchases"),
                InlineKeyboardButton("🎁 Gift Card", callback_data="ranking_gifts")
            ],
            [
                InlineKeyboardButton("💵 Saldo", callback_data="ranking_balance"),
                InlineKeyboardButton("↩️ Voltar", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🏆 Escolha o tipo de ranking que deseja visualizar:",
            reply_markup=reply_markup
        )
    
    async def alertas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /alertas"""
        products = self.db.get_products()
        
        message = "🔔 Configurar Alertas de Estoque\n\n"
        message += "Selecione os produtos para receber notificações quando o estoque for reabastecido:\n\n"
        
        keyboard = []
        for product in products:
            keyboard.append([
                InlineKeyboardButton(
                    f"✅ {product['name']} - Estoque: {product['stock']}",
                    callback_data=f"alert_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ Voltar", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando de administração"""
        user = update.effective_user
        
        if user.id != self.admin_id:
            await update.message.reply_text("❌ Acesso negado. Apenas administradores podem usar este comando.")
            return
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Adicionar Produto", callback_data="admin_add_product"),
                InlineKeyboardButton("✏️ Editar Produto", callback_data="admin_edit_product")
            ],
            [
                InlineKeyboardButton("⚙️ Configurações", callback_data="admin_config"),
                InlineKeyboardButton("📊 Estatísticas", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("👥 Gerenciar Usuários", callback_data="admin_users"),
                InlineKeyboardButton("💰 Gerenciar Saldos", callback_data="admin_balances")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 Painel de Administração\n\nEscolha uma opção:",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa callbacks dos botões inline"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "products":
            await self._show_products_menu(query)
        elif data == "profile":
            await self._show_profile(query)
        elif data == "recharge":
            await self._show_recharge_menu(query)
        elif data == "ranking":
            await self._show_ranking_menu(query)
        elif data == "support":
            await self._show_support(query)
        elif data == "info":
            await self._show_info(query)
        elif data == "search":
            await self._show_search(query)
        elif data.startswith("ranking_"):
            await self._show_ranking(query, data.split("_")[1])
        elif data.startswith("product_"):
            await self._show_product_details(query, data.split("_")[1])
        elif data.startswith("buy_"):
            await self._handle_purchase(query, data.split("_")[1])
        elif data.startswith("admin_"):
            await self._handle_admin_action(query, data.split("_")[1])
        elif data == "main_menu":
            await self._show_main_menu(query)
    
    async def _show_products_menu(self, query):
        """Mostra menu de produtos"""
        products = self.db.get_products()
        user = query.from_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        message = f"""🎟️ Logins Premium | Acesso Exclusivo

🏦 Carteira
💸 Saldo Atual: R${user_data['balance']:.2f}

Produtos disponíveis:"""
        
        keyboard = []
        for product in products:
            keyboard.append([
                InlineKeyboardButton(
                    f"{product['name']} - R${product['price']:.2f}",
                    callback_data=f"product_{product['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("↩️ Voltar", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    async def _show_product_details(self, query, product_id: str):
        """Mostra detalhes do produto"""
        product = self.db.get_product(int(product_id))
        user = query.from_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if not product:
            await query.edit_message_text("❌ Produto não encontrado.")
            return
        
        message = f"""⚜️ACESSO: {product['name']} ⚜️

💵 Preço: R${product['price']:.2f}
💼 Saldo Atual: R${user_data['balance']:.2f}
📥 Estoque Disponível: {product['stock']}

🗒️ Descrição: {product['description']}

Aviso Importante:
O acesso é disponibilizado na hora. Não atendemos ligações nem ouvimos mensagens de áudio; pedimos que aguarde sua vez.
Informamos que não realizamos reembolsos via Pix, apenas em créditos no bot, correspondendo aos dias restantes até o vencimento.
Agradecemos pela compreensão e desejamos boas compras!

♻️ Garantia: 30 dias"""
        
        keyboard = [
            [
                InlineKeyboardButton("🛒 Comprar", callback_data=f"buy_{product_id}"),
                InlineKeyboardButton("↩️ Voltar", callback_data="products")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    async def _handle_purchase(self, query, product_id: str):
        """Processa compra do produto"""
        product = self.db.get_product(int(product_id))
        user = query.from_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if not product:
            await query.edit_message_text("❌ Produto não encontrado.")
            return
        
        # Verifica saldo
        if user_data['balance'] < product['price']:
            missing = product['price'] - user_data['balance']
            message = f"""*❌ Saldo Insuficiente!*

Seu saldo atual não é suficiente para concluir esta compra. Faça uma *recarga* e tente novamente! 💰

Faltam: R${missing:.2f}
Seu saldo: R${user_data['balance']:.2f}"""
            
            keyboard = [
                InlineKeyboardButton("💰 Recarregar", callback_data="recharge"),
                InlineKeyboardButton("↩️ Voltar", callback_data="products")
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Verifica estoque
        if product['stock'] <= 0:
            await query.edit_message_text("❌ Produto sem estoque no momento. Tente novamente mais tarde.")
            return
        
        # Processa compra
        await self._process_purchase(query, product, user_data)
    
    async def _process_purchase(self, query, product: Dict, user_data: Dict):
        """Processa a compra do produto"""
        # Cria compra no banco
        purchase_id = self.db.create_purchase(
            user_id=user_data['id'],
            product_id=product['id'],
            amount=product['price']
        )
        
        # Deduz saldo
        self.db.update_user_balance(user_data['telegram_id'], product['price'], 'subtract')
        
        # Gera informações de entrega
        delivery_info = self._generate_delivery_info(product)
        
        # Atualiza compra com informações de entrega
        self._update_purchase_delivery(purchase_id, delivery_info)
        
        # Envia confirmação
        message = f"""✅ *Compra realizada com sucesso!*

🎟️ Produto: {product['name']}
💰 Valor: R${product['price']:.2f}
🆔 ID da Compra: {purchase_id}

📦 *Informações de Entrega:*
{delivery_info}

⏰ Prazo de entrega: até 24 horas
♻️ Garantia: 30 dias

Obrigado pela compra! 🎉"""
        
        keyboard = [
            [InlineKeyboardButton("🛍️ Minhas Compras", callback_data="profile")],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    def _generate_delivery_info(self, product: Dict) -> str:
        """Gera informações de entrega do produto"""
        import random
        import string
        
        email = f"user{random.randint(1000, 9999)}@example.com"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        return f"""📧 Email: {email}
🔑 Senha: {password}
📱 App: {product['name']} (disponível na App Store e Play Store)"""
    
    def _update_purchase_delivery(self, purchase_id: int, delivery_info: str):
        """Atualiza compra com informações de entrega"""
        conn = self.db.db_file
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE purchases 
            SET delivery_info = ?, status = 'delivered', delivered_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (delivery_info, purchase_id))
        
        conn.commit()
        conn.close()
    
    def _generate_history_file(self, user_data: Dict, purchases: List, transactions: List) -> str:
        """Gera arquivo de histórico"""
        filename = f"historico_{user_data['affiliate_code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"HISTORICO DETALHADO\n")
            f.write(f"@{config.BOT_NAME.lower().replace(' ', '')}\n")
            f.write("_" * 40 + "\n\n")
            
            f.write("COMPRAS:\n")
            f.write("_" * 40 + "\n")
            for purchase in purchases:
                f.write(f"Produto: {purchase['product_name']}\n")
                f.write(f"Valor: R${purchase['amount']:.2f}\n")
                f.write(f"Data: {purchase['created_at']}\n")
                f.write(f"Status: {purchase['status']}\n")
                f.write("-" * 20 + "\n")
            
            f.write("\nPAGAMENTOS:\n")
            f.write("_" * 40 + "\n")
            for transaction in transactions:
                f.write(f"Tipo: {transaction['type']}\n")
                f.write(f"Valor: R${transaction['amount']:.2f}\n")
                f.write(f"Data: {transaction['created_at']}\n")
                f.write(f"Status: {transaction['status']}\n")
                f.write("-" * 20 + "\n")
        
        return filename
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de texto"""
        user = update.effective_user
        message_text = update.message.text
        
        # Verifica se é administrador
        if user.id == self.admin_id and message_text.startswith("ADMIN:"):
            await self._handle_admin_text(update, context, message_text)
            return
        
        # Processa mensagens normais
        if message_text.upper().startswith("COMPRAR "):
            product_name = message_text[8:]  # Remove "COMPRAR "
            await self._handle_purchase_request(update, context, product_name)
        elif message_text.upper() == "HISTORICO":
            await self.historico_command(update, context)
        elif message_text.upper() == "PERFIL":
            await self._show_profile_text(update, context)
        elif message_text.upper() == "RECARGA":
            await self._show_recharge_menu_text(update, context)
        else:
            # Verifica se é resposta a alguma pergunta do bot
            user_state = self.user_states.get(user.id, {})
            if user_state.get('waiting_for_amount'):
                await self._handle_recharge_amount_text(update, context, message_text)
            else:
                await update.message.reply_text(
                    "Use /start para acessar o menu principal ou digite um comando válido."
                )
    
    async def _handle_purchase_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, product_name: str):
        """Processa solicitação de compra por texto"""
        products = self.db.search_products(product_name)
        user = update.effective_user
        user_data = self.db.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if not products:
            await update.message.reply_text(f"Produto '{product_name}' não encontrado. Use /start para ver todos os produtos.")
            return
        
        product = products[0]
        
        # Verifica saldo
        if user_data['balance'] < product['price']:
            missing = product['price'] - user_data['balance']
            message = f"""*❌ Saldo Insuficiente!*

Seu saldo atual não é suficiente para concluir esta compra. Faça uma *recarga* e tente novamente! 💰

Faltam: R${missing:.2f}
Seu saldo: R${user_data['balance']:.2f}"""
            
            keyboard = [
                InlineKeyboardButton("💰 Recarregar", callback_data="recharge"),
                InlineKeyboardButton("↩️ Voltar", callback_data="products")
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Verifica estoque
        if product['stock'] <= 0:
            await update.message.reply_text("Produto sem estoque no momento. Tente novamente mais tarde.")
            return
        
        # Processa compra
        await self._process_purchase_text(update, context, product, user_data)
    
    async def _process_purchase_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, product: Dict, user_data: Dict):
        """Processa compra por texto"""
        # Cria compra no banco
        purchase_id = self.db.create_purchase(
            user_id=user_data['id'],
            product_id=product['id'],
            amount=product['price']
        )
        
        # Deduz saldo
        self.db.update_user_balance(user_data['telegram_id'], product['price'], 'subtract')
        
        # Gera informações de entrega
        delivery_info = self._generate_delivery_info(product)
        
        # Atualiza compra com informações de entrega
        self._update_purchase_delivery(purchase_id, delivery_info)
        
        # Envia confirmação
        message = f"""✅ *Compra realizada com sucesso!*

🎟️ Produto: {product['name']}
💰 Valor: R${product['price']:.2f}
🆔 ID da Compra: {purchase_id}

📦 *Informações de Entrega:*
{delivery_info}

⏰ Prazo de entrega: até 24 horas
♻️ Garantia: 30 dias

Obrigado pela compra! 🎉"""
        
        keyboard = [
            [InlineKeyboardButton("🛍️ Minhas Compras", callback_data="profile")],
            [InlineKeyboardButton("🏠 Menu Principal", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    def run(self):
        """Executa o bot"""
        print(f"Bot iniciado: @{config.BOT_NAME}")
        self.application.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()