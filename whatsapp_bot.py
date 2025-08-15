import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config
from database import Database
from pix_generator import PixGenerator

class WhatsAppBot:
    def __init__(self):
        self.db = Database()
        self.pix_generator = PixGenerator()
        self.api_key = config.CALLMEBOT_API_KEY
        self.phone = config.CALLMEBOT_PHONE
        self.api_url = config.CALLMEBOT_URL
        
        # Cache de usuários ativos
        self.active_users = {}
        self.user_states = {}
        self.flood_protection = {}
    
    def send_message(self, phone: str, message: str) -> bool:
        """Envia mensagem via CallMeBot API"""
        try:
            url = f"{self.api_url}?phone={phone}&text={message}&apikey={self.api_key}"
            response = requests.get(url)
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return False
    
    def send_photo(self, phone: str, photo_path: str, caption: str = "") -> bool:
        """Envia foto via CallMeBot API"""
        try:
            url = f"{self.api_url}?phone={phone}&photo={photo_path}&caption={caption}&apikey={self.api_key}"
            response = requests.get(url)
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar foto: {e}")
            return False
    
    def handle_message(self, phone: str, message: str, user_name: str = None):
        """Processa mensagem recebida"""
        # Verifica flood protection
        if self._is_flooding(phone):
            self.send_message(phone, "*⚠️ Atenção!*\n\nPare de floodar! Suas solicitações serão ignoradas pelos próximos *6 segundos* (acumulativo). ⏳")
            return
        
        # Processa comando ou mensagem
        if message.startswith('/'):
            self._handle_command(phone, message, user_name)
        else:
            self._handle_text_message(phone, message, user_name)
    
    def _handle_command(self, phone: str, command: str, user_name: str):
        """Processa comandos"""
        cmd_parts = command.split()
        cmd = cmd_parts[0].lower()
        
        if cmd == '/start':
            self._show_main_menu(phone, user_name)
        elif cmd == '/pix':
            if len(cmd_parts) > 1:
                try:
                    amount = float(cmd_parts[1])
                    self._handle_pix_command(phone, amount, user_name)
                except ValueError:
                    self.send_message(phone, "Você enviou em um formato incorreto. Envie /pix e o valor que deseja...\nExemplo:\n/pix 10\n/pix 6.26")
            else:
                self.send_message(phone, "Você enviou em um formato incorreto. Envie /pix e o valor que deseja...\nExemplo:\n/pix 10\n/pix 6.26")
        elif cmd == '/historico':
            self._show_purchase_history(phone, user_name)
        elif cmd == '/afiliados':
            self._show_affiliate_info(phone, user_name)
        elif cmd == '/id':
            self._show_user_id(phone, user_name)
        elif cmd == '/ranking':
            self._show_ranking_menu(phone, user_name)
        elif cmd == '/alertas':
            self._show_alerts_menu(phone, user_name)
        else:
            self.send_message(phone, "Comando não reconhecido. Use /start para ver o menu principal.")
    
    def _handle_text_message(self, phone: str, message: str, user_name: str):
        """Processa mensagens de texto"""
        # Verifica estado do usuário
        user_state = self.user_states.get(phone, {})
        
        if user_state.get('waiting_for_amount'):
            self._handle_recharge_amount(phone, message, user_name)
        elif user_state.get('waiting_for_support_number'):
            self._handle_support_number(phone, message, user_name)
        else:
            # Mensagem não reconhecida
            self.send_message(phone, "Use /start para acessar o menu principal ou digite um comando válido.")
    
    def _show_main_menu(self, phone: str, user_name: str):
        """Mostra menu principal"""
        # Obtém ou cria usuário
        user = self._get_or_create_user(phone, user_name)
        
        # Obtém configurações do bot
        bot_config = self.db.get_bot_config()
        
        message = f"""🥇{bot_config.get('bot_name', config.BOT_NAME)}

🥇Descubra como nosso bot pode transformar sua experiência de compras!
Ele facilita a busca por diversos produtos e serviços, garantindo que você encontre o que precisa com o melhor preço e excelente custo-benefício.
Importante: Não realizamos reembolsos em dinheiro. O suporte estará disponível por até 48 horas após a entrega das informações, com reembolso em créditos no bot, se necessário.

👥Grupo De Clientes:
{config.SUPPORT_GROUP_LINK}

👨‍💻 Link De Suporte:
{bot_config.get('support_phone', config.CALLMEBOT_PHONE)}

ℹ️Seus Dados:
🆔ID: {user['affiliate_code']}
💸Saldo Atual: R${user['balance']:.2f}
🪪Usuário: {user_name or 'Usuário'}

https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSltpwF6kTey6ImHK0Z76OBq2AmdNgMsS7irFzm7Xv4Ji9whMxq-eD6PO2Y&s=10

💎  Logins | Contas Premium
🪪 PERFIL        💰RECARGA 
                   🎖️ Ranking
👩‍💻 Suporte.       ℹ️ Informações 
       🔎 Pesquisar Serviços"""
        
        self.send_message(phone, message)
    
    def _show_products_menu(self, phone: str, user_name: str):
        """Mostra menu de produtos"""
        products = self.db.get_products()
        user = self._get_or_create_user(phone, user_name)
        
        message = f"""🎟️ Logins Premium | Acesso Exclusivo

🏦 Carteira
💸 Saldo Atual: R${user['balance']:.2f}

Produtos disponíveis:"""
        
        for product in products:
            message += f"\n\n{product['name']} - R${product['price']:.2f}"
            message += f"\nEstoque: {product['stock']}"
        
        message += "\n\nDigite o nome do produto que deseja comprar ou use /start para voltar ao menu principal."
        
        self.send_message(phone, message)
    
    def _show_product_details(self, phone: str, product_name: str, user_name: str):
        """Mostra detalhes do produto"""
        products = self.db.search_products(product_name)
        user = self._get_or_create_user(phone, user_name)
        
        if not products:
            self.send_message(phone, f"Produto '{product_name}' não encontrado. Use /start para ver todos os produtos.")
            return
        
        product = products[0]  # Primeiro produto encontrado
        
        message = f"""⚜️ACESSO: {product['name']} ⚜️

💵 Preço: R${product['price']:.2f}
💼 Saldo Atual: R${user['balance']:.2f}
📥 Estoque Disponível: {product['stock']}

🗒️ Descrição: {product['description']}

Aviso Importante:
O acesso é disponibilizado na hora. Não atendemos ligações nem ouvimos mensagens de áudio; pedimos que aguarde sua vez.
Informamos que não realizamos reembolsos via Pix, apenas em créditos no bot, correspondendo aos dias restantes até o vencimento.
Agradecemos pela compreensão e desejamos boas compras!

♻️ Garantia: 30 dias

Para comprar, digite: COMPRAR {product['name']}"""
        
        self.send_message(phone, message)
    
    def _handle_purchase_request(self, phone: str, product_name: str, user_name: str):
        """Processa solicitação de compra"""
        products = self.db.search_products(product_name)
        user = self._get_or_create_user(phone, user_name)
        
        if not products:
            self.send_message(phone, "Produto não encontrado.")
            return
        
        product = products[0]
        
        # Verifica saldo
        if user['balance'] < product['price']:
            missing = product['price'] - user['balance']
            message = f"""*❌ Saldo Insuficiente!*

Seu saldo atual não é suficiente para concluir esta compra. Faça uma *recarga* e tente novamente! 💰

Faltam: R${missing:.2f}
Seu saldo: R${user['balance']:.2f}"""
            
            self.send_message(phone, message)
            return
        
        # Verifica estoque
        if product['stock'] <= 0:
            self.send_message(phone, "Produto sem estoque no momento. Tente novamente mais tarde.")
            return
        
        # Processa compra
        self._process_purchase(phone, product, user, user_name)
    
    def _process_purchase(self, phone: str, product: Dict, user: Dict, user_name: str):
        """Processa a compra do produto"""
        # Cria compra no banco
        purchase_id = self.db.create_purchase(
            user_id=user['id'],
            product_id=product['id'],
            amount=product['price']
        )
        
        # Deduz saldo
        self.db.update_user_balance(user['telegram_id'], product['price'], 'subtract')
        
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
        
        self.send_message(phone, message)
    
    def _generate_delivery_info(self, product: Dict) -> str:
        """Gera informações de entrega do produto"""
        # Simula geração de credenciais
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
    
    def _show_recharge_menu(self, phone: str, user_name: str):
        """Mostra menu de recarga"""
        user = self._get_or_create_user(phone, user_name)
        bot_config = self.db.get_bot_config()
        
        message = f"""💼| ID da Carteira: {user['affiliate_code']}
💵| Saldo Disponível: R${user['balance']:.2f}

💡Selecione uma opção para recarregar:

Para recarregar via PIX, digite o valor desejado (mínimo R${bot_config.get('min_recharge', '1.00'})).

Exemplo: 10.50"""
        
        # Define estado de espera por valor
        self.user_states[phone] = {'waiting_for_amount': True}
        
        self.send_message(phone, message)
    
    def _handle_recharge_amount(self, phone: str, amount_str: str, user_name: str):
        """Processa valor de recarga"""
        try:
            amount = float(amount_str)
            bot_config = self.db.get_bot_config()
            min_amount = float(bot_config.get('min_recharge', '1.00'))
            max_amount = float(bot_config.get('max_recharge', '1000.00'))
            
            if amount < min_amount:
                self.send_message(phone, f"Valor mínimo para recarga é R${min_amount:.2f}")
                return
            
            if amount > max_amount:
                self.send_message(phone, f"Valor máximo para recarga é R${max_amount:.2f}")
                return
            
            # Gera PIX
            user = self._get_or_create_user(phone, user_name)
            pix_result = self.pix_generator.generate_pix(amount, user['id'])
            
            if pix_result['success']:
                self._send_pix_payment(phone, pix_result, user_name)
            else:
                self.send_message(phone, f"Erro ao gerar PIX: {pix_result['error']}")
            
            # Limpa estado
            self.user_states[phone] = {}
            
        except ValueError:
            self.send_message(phone, "Valor inválido. Digite apenas números (ex: 10.50)")
    
    def _send_pix_payment(self, phone: str, pix_result: Dict, user_name: str):
        """Envia informações de pagamento PIX"""
        message = f"""Gerando pagamento...

💰 Comprar Saldo com Pix Automático:

⏱️ Expira em: {pix_result['expiration_formatted']}
💵 Valor: R${pix_result['amount']:.2f}
✨ ID da Recarga: {pix_result['transaction_id']}

🗞️ Atenção: Este código é válido para apenas um único pagamento.
Se você utilizá-lo mais de uma vez, o saldo adicional será perdido sem direito a reembolso.

💎 Pix Copia e Cola:

{pix_result['pix_code']}

💡 Dica: Clique no código acima para copiar.

🇧🇷 Após o pagamento, seu saldo será liberado instantaneamente.

⏰ Aguardando Pagamento"""
        
        self.send_message(phone, message)
        
        # Envia QR Code se disponível
        if pix_result['qr_code']:
            self.send_photo(phone, pix_result['qr_code'], "QR Code para pagamento PIX")
    
    def _show_profile(self, phone: str, user_name: str):
        """Mostra perfil do usuário"""
        user = self._get_or_create_user(phone, user_name)
        
        message = f"""🙋‍♂️ Meu perfil

🔎 Veja aqui os detalhes da sua conta:

-👤 Informações:
🆔 ID da Carteira: {user['affiliate_code']}
💰 Saldo Atual: R${user['balance']:.2f}

📊 Suas movimentações:
—🛒 Comprar Realizadas: {len(self.db.get_user_purchases(user['telegram_id']))}
—💠 Pix Inseridos: {len([t for t in self.db.get_user_transactions(user['telegram_id']) if t['type'] == 'recharge'])}
—🎁 Gifts Resgatados: R${user['bonus']:.2f}

Para ver histórico detalhado, digite: HISTORICO"""
        
        self.send_message(phone, message)
    
    def _show_purchase_history(self, phone: str, user_name: str):
        """Mostra histórico de compras"""
        user = self._get_or_create_user(phone, user_name)
        purchases = self.db.get_user_purchases(user['telegram_id'])
        transactions = self.db.get_user_transactions(user['telegram_id'])
        
        # Gera arquivo de histórico
        history_file = self._generate_history_file(user, purchases, transactions)
        
        message = "📋 Histórico de compras gerado com sucesso!"
        self.send_message(phone, message)
        
        # Aqui você enviaria o arquivo (CallMeBot não suporta envio de arquivos)
        # Em uma implementação real, você usaria WhatsApp Business API
    
    def _generate_history_file(self, user: Dict, purchases: List, transactions: List) -> str:
        """Gera arquivo de histórico"""
        filename = f"historico_{user['affiliate_code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
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
    
    def _show_ranking_menu(self, phone: str, user_name: str):
        """Mostra menu de rankings"""
        message = """🏆 Ranking dos serviços mais vendidos (deste mês)

1°) Premiere (tela) 🥇Com 66 pedidos
2°) Globoplay+canais (tela) 🥈Com 66 pedidos
3°) Prime video (tela) 🥉Com 63 pedidos
4°) Disney+star premium (tela) - Com 40 pedidos
5°) Iptv premium (mensal) - Com 34 pedidos
6°) Max (tela) - Com 28 pedidos
7°) Youtube premium (convite) - Com 25 pedidos
8°) Netflix premium (tela) - Com 22 pedidos
9°) Globoplay+canais+telecine (tela) - Com 20 pedidos
10°) Grupos vips +30 links +18 (acesso) - Com 19 pedidos

Para ver outros rankings, digite:
- RECARGAS (usuários que mais recarregaram)
- COMPRAS (usuários que mais compraram)
- GIFT CARD (usuários que mais resgataram)
- SALDO (usuários com mais saldo)"""
        
        self.send_message(phone, message)
    
    def _show_affiliate_info(self, phone: str, user_name: str):
        """Mostra informações de afiliado"""
        user = self._get_or_create_user(phone, user_name)
        bot_config = self.db.get_bot_config()
        
        affiliate_link = f"https://t.me/{config.BOT_NAME.lower().replace(' ', '')}?start={user['affiliate_code']}"
        
        message = f"""ℹ️ Status:
📊 Comissão por Indicação: {float(bot_config.get('affiliate_commission', '0.5')) * 100}%
👥 Total de Afiliados: 0
🔗 Link para Indicar: {affiliate_link}

Como Funciona?
Copie seu link de indicação e envie para outras pessoas.
Cada vez que alguém indicado por você fizer uma recarga no bot, você receberá uma porcentagem desse valor!
Por exemplo, com uma comissão de {float(bot_config.get('affiliate_commission', '0.5')) * 100}%, se 5 pessoas indicadas recarregarem R$10,00 cada, você receberá R${5 * 10 * float(bot_config.get('affiliate_commission', '0.5')):.2f}.
Indique mais e aumente seus ganhos!"""
        
        self.send_message(phone, message)
    
    def _show_user_id(self, phone: str, user_name: str):
        """Mostra ID do usuário"""
        user = self._get_or_create_user(phone, user_name)
        
        message = f"🆔 Seu id é: {user['affiliate_code']}"
        self.send_message(phone, message)
    
    def _show_alerts_menu(self, phone: str, user_name: str):
        """Mostra menu de alertas"""
        products = self.db.get_products()
        
        message = "🔔 Configurar Alertas de Estoque\n\n"
        message += "Selecione os produtos para receber notificações quando o estoque for reabastecido:\n\n"
        
        for product in products:
            message += f"✅ {product['name']} - Estoque: {product['stock']}\n"
        
        message += "\nPara ativar/desativar alertas, digite: ALERTA [nome do produto]"
        
        self.send_message(phone, message)
    
    def _get_or_create_user(self, phone: str, user_name: str) -> Dict:
        """Obtém ou cria usuário baseado no número do WhatsApp"""
        # Busca usuário por número do WhatsApp
        conn = self.db.db_file
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE whatsapp_number = ?', (phone,))
        user = cursor.fetchone()
        
        if user:
            user_dict = {
                'id': user[0], 'telegram_id': user[1], 'whatsapp_number': user[2],
                'username': user[3], 'first_name': user[4], 'last_name': user[5],
                'balance': user[6], 'bonus': user[7], 'affiliate_code': user[8],
                'referred_by': user[9], 'created_at': user[10], 'last_activity': user[11]
            }
        else:
            # Cria novo usuário
            affiliate_code = self.db.generate_affiliate_code()
            cursor.execute('''
                INSERT INTO users (whatsapp_number, first_name, affiliate_code)
                VALUES (?, ?, ?)
            ''', (phone, user_name, affiliate_code))
            
            user_id = cursor.lastrowid
            user_dict = {
                'id': user_id, 'telegram_id': None, 'whatsapp_number': phone,
                'username': None, 'first_name': user_name, 'last_name': None,
                'balance': 0.0, 'bonus': 0.0, 'affiliate_code': affiliate_code,
                'referred_by': None, 'created_at': datetime.now(), 'last_activity': datetime.now()
            }
        
        conn.commit()
        conn.close()
        return user_dict
    
    def _is_flooding(self, phone: str) -> bool:
        """Verifica se usuário está fazendo flood"""
        now = time.time()
        
        if phone not in self.flood_protection:
            self.flood_protection[phone] = {'count': 0, 'last_reset': now}
        
        # Reseta contador a cada 6 segundos
        if now - self.flood_protection[phone]['last_reset'] > 6:
            self.flood_protection[phone] = {'count': 0, 'last_reset': now}
        
        self.flood_protection[phone]['count'] += 1
        
        # Permite no máximo 3 mensagens em 6 segundos
        return self.flood_protection[phone]['count'] > 3
    
    def cleanup_expired_pix(self):
        """Limpa PIXs expirados e notifica usuários"""
        expired_pix = self.pix_generator.get_expired_pix()
        
        for pix in expired_pix:
            if pix['telegram_id']:
                # Notifica usuário do Telegram
                message = f"""*⚠️ Solicitação Negada!*

Desculpe, sua recarga falhou porque o *PIX não foi pago dentro do prazo*. ⏳❌"""
                
                # Aqui você enviaria para o Telegram (implementar separadamente)
                pass
        
        # Limpa PIXs expirados
        self.pix_generator.cleanup_expired_pix()
    
    def start_auto_cleanup(self):
        """Inicia limpeza automática de PIXs expirados"""
        import threading
        import time
        
        def cleanup_loop():
            while True:
                try:
                    self.cleanup_expired_pix()
                    time.sleep(60)  # Verifica a cada minuto
                except Exception as e:
                    print(f"Erro na limpeza automática: {e}")
                    time.sleep(300)  # Espera 5 minutos em caso de erro
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()