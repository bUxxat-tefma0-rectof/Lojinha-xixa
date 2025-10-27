#!/usr/bin/env python3
"""
JOÃOZINHO STORE BOT
Bot completo para WhatsApp e Telegram com sistema de vendas e administração
"""

import asyncio
import logging
import threading
import time
from flask import Flask, request, jsonify
from telegram_bot import TelegramBot
from whatsapp_bot import WhatsAppBot
from database import Database
from pix_generator import PixGenerator
import config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Inicializa Flask para webhooks
app = Flask(__name__)

# Inicializa bots
telegram_bot = None
whatsapp_bot = None
database = None
pix_generator = None

def initialize_bots():
    """Inicializa todos os bots e serviços"""
    global telegram_bot, whatsapp_bot, database, pix_generator
    
    try:
        logger.info("Inicializando banco de dados...")
        database = Database()
        
        logger.info("Inicializando gerador de PIX...")
        pix_generator = PixGenerator()
        
        logger.info("Inicializando bot do WhatsApp...")
        whatsapp_bot = WhatsAppBot()
        
        logger.info("Inicializando bot do Telegram...")
        telegram_bot = TelegramBot()
        
        logger.info("Todos os bots inicializados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar bots: {e}")
        raise

def start_telegram_bot():
    """Inicia o bot do Telegram em thread separada"""
    try:
        logger.info("Iniciando bot do Telegram...")
        telegram_bot.run()
    except Exception as e:
        logger.error(f"Erro no bot do Telegram: {e}")

def start_whatsapp_webhook():
    """Inicia o servidor webhook para WhatsApp"""
    try:
        logger.info("Iniciando servidor webhook para WhatsApp...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Erro no servidor webhook: {e}")

def start_pix_cleanup():
    """Inicia limpeza automática de PIXs expirados"""
    try:
        logger.info("Iniciando limpeza automática de PIXs...")
        while True:
            try:
                if pix_generator:
                    pix_generator.cleanup_expired_pix()
                time.sleep(60)  # Verifica a cada minuto
            except Exception as e:
                logger.error(f"Erro na limpeza automática: {e}")
                time.sleep(300)  # Espera 5 minutos em caso de erro
    except Exception as e:
        logger.error(f"Erro fatal na limpeza automática: {e}")

# Rotas do webhook para WhatsApp
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Webhook para receber mensagens do WhatsApp"""
    try:
        data = request.get_json()
        logger.info(f"Webhook recebido: {data}")
        
        # Processa dados do webhook (implementar conforme sua API)
        if data and 'entry' in data:
            for entry in data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change.get('value') and 'messages' in change['value']:
                            for message in change['value']['messages']:
                                await process_whatsapp_message(message)
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook/whatsapp', methods=['GET'])
def whatsapp_verify():
    """Verificação do webhook do WhatsApp"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == 'your_verify_token':
        logger.info("Webhook verificado com sucesso!")
        return challenge
    else:
        logger.warning("Falha na verificação do webhook")
        return 'Forbidden', 403

async def process_whatsapp_message(message):
    """Processa mensagem recebida do WhatsApp"""
    try:
        if 'from' in message and 'text' in message:
            phone = message['from']
            text = message['text']['body']
            user_name = message.get('sender', {}).get('name', 'Usuário')
            
            logger.info(f"Mensagem recebida de {phone}: {text}")
            
            # Processa mensagem
            if whatsapp_bot:
                whatsapp_bot.handle_message(phone, text, user_name)
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem do WhatsApp: {e}")

# Rotas para CallMeBot (alternativa ao webhook)
@app.route('/callmebot', methods=['POST'])
def callmebot_webhook():
    """Webhook alternativo para CallMeBot"""
    try:
        data = request.get_json()
        logger.info(f"CallMeBot webhook: {data}")
        
        if data and 'message' in data:
            phone = data.get('phone', '')
            message = data.get('message', '')
            user_name = data.get('name', 'Usuário')
            
            if phone and message:
                # Processa mensagem
                if whatsapp_bot:
                    whatsapp_bot.handle_message(phone, message, user_name)
        
        return jsonify({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Erro no webhook CallMeBot: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Rotas de administração
@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    """Estatísticas do bot (apenas para administradores)"""
    try:
        if not database:
            return jsonify({'error': 'Database não inicializado'}), 500
        
        # Estatísticas básicas
        stats = {
            'total_users': 0,
            'total_products': 0,
            'total_transactions': 0,
            'total_purchases': 0
        }
        
        # Aqui você implementaria as consultas ao banco
        # Por enquanto retorna dados simulados
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/config', methods=['GET', 'POST'])
def admin_config():
    """Configurações do bot (apenas para administradores)"""
    try:
        if not database:
            return jsonify({'error': 'Database não inicializado'}), 500
        
        if request.method == 'GET':
            # Retorna configurações atuais
            config_data = database.get_bot_config()
            return jsonify(config_data)
        
        elif request.method == 'POST':
            # Atualiza configurações
            data = request.get_json()
            
            for key, value in data.items():
                database.update_bot_config(key, str(value))
            
            return jsonify({'status': 'success', 'message': 'Configurações atualizadas'})
    
    except Exception as e:
        logger.error(f"Erro ao gerenciar configurações: {e}")
        return jsonify({'error': str(e)}), 500

# Rota de saúde
@app.route('/health', methods=['GET'])
def health_check():
    """Verificação de saúde do sistema"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'telegram_bot': telegram_bot is not None,
            'whatsapp_bot': whatsapp_bot is not None,
            'database': database is not None,
            'pix_generator': pix_generator is not None
        }
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

def main():
    """Função principal"""
    try:
        logger.info("Iniciando JOÃOZINHO STORE BOT...")
        
        # Inicializa bots
        initialize_bots()
        
        # Inicia threads para diferentes serviços
        threads = []
        
        # Thread para bot do Telegram
        telegram_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        threads.append(telegram_thread)
        telegram_thread.start()
        
        # Thread para limpeza automática de PIX
        cleanup_thread = threading.Thread(target=start_pix_cleanup, daemon=True)
        threads.append(cleanup_thread)
        cleanup_thread.start()
        
        # Thread para servidor webhook (opcional)
        if config.WHATSAPP_ACCESS_TOKEN:  # Só inicia se tiver token do WhatsApp Business
            webhook_thread = threading.Thread(target=start_whatsapp_webhook, daemon=True)
            threads.append(webhook_thread)
            webhook_thread.start()
        
        logger.info("Bot iniciado com sucesso!")
        logger.info(f"Bot do Telegram: @{config.BOT_NAME}")
        logger.info(f"Bot do WhatsApp: {config.CALLMEBOT_PHONE}")
        logger.info(f"Admin ID: {config.ADMIN_ID}")
        
        # Aguarda threads terminarem
        for thread in threads:
            thread.join()
        
    except KeyboardInterrupt:
        logger.info("Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        raise

if __name__ == "__main__":
    main()