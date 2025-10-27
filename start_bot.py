#!/usr/bin/env python3
"""
Script de Inicialização Principal do JOÃOZINHO STORE BOT
Coordena todos os componentes e inicia o sistema completo
"""

import os
import sys
import time
import signal
import logging
import threading
import asyncio
from datetime import datetime
import config
from database import Database
from telegram_bot import TelegramBot
from whatsapp_bot import WhatsAppBot
from pix_generator import PixGenerator
from notification_system import NotificationSystem
from backup_system import BackupSystem

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

class BotManager:
    def __init__(self):
        self.running = False
        self.components = {}
        self.threads = {}
        
        # Sinalizadores de parada
        self.stop_event = threading.Event()
        
        # Configura tratamento de sinais
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Trata sinais de parada"""
        logger.info(f"Sinal recebido: {signum}")
        self.stop()
    
    def initialize_components(self):
        """Inicializa todos os componentes do bot"""
        try:
            logger.info("🚀 Inicializando componentes do bot...")
            
            # Banco de dados
            logger.info("📊 Inicializando banco de dados...")
            self.components['database'] = Database()
            logger.info("✅ Banco de dados inicializado")
            
            # Gerador de PIX
            logger.info("💰 Inicializando gerador de PIX...")
            self.components['pix_generator'] = PixGenerator()
            logger.info("✅ Gerador de PIX inicializado")
            
            # Bot do WhatsApp
            logger.info("📱 Inicializando bot do WhatsApp...")
            self.components['whatsapp_bot'] = WhatsAppBot()
            logger.info("✅ Bot do WhatsApp inicializado")
            
            # Bot do Telegram
            logger.info("📨 Inicializando bot do Telegram...")
            self.components['telegram_bot'] = TelegramBot()
            logger.info("✅ Bot do Telegram inicializado")
            
            # Sistema de notificações
            logger.info("🔔 Inicializando sistema de notificações...")
            self.components['notification_system'] = NotificationSystem()
            self.components['notification_system'].set_bots(
                self.components['telegram_bot'],
                self.components['whatsapp_bot']
            )
            logger.info("✅ Sistema de notificações inicializado")
            
            # Sistema de backup
            logger.info("💾 Inicializando sistema de backup...")
            self.components['backup_system'] = BackupSystem()
            logger.info("✅ Sistema de backup inicializado")
            
            logger.info("🎉 Todos os componentes inicializados com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar componentes: {e}")
            return False
    
    def start_telegram_bot(self):
        """Inicia o bot do Telegram em thread separada"""
        try:
            logger.info("📨 Iniciando bot do Telegram...")
            
            def run_telegram():
                try:
                    self.components['telegram_bot'].run()
                except Exception as e:
                    logger.error(f"Erro no bot do Telegram: {e}")
            
            telegram_thread = threading.Thread(target=run_telegram, daemon=True)
            telegram_thread.start()
            self.threads['telegram'] = telegram_thread
            
            logger.info("✅ Bot do Telegram iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar bot do Telegram: {e}")
            return False
    
    def start_notification_system(self):
        """Inicia o sistema de notificações"""
        try:
            logger.info("🔔 Iniciando sistema de notificações...")
            
            async def run_notifications():
                try:
                    await self.components['notification_system'].start_notification_loop()
                except Exception as e:
                    logger.error(f"Erro no sistema de notificações: {e}")
            
            # Cria loop de eventos para notificações
            def run_notification_loop():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(run_notifications())
                loop.close()
            
            notification_thread = threading.Thread(target=run_notification_loop, daemon=True)
            notification_thread.start()
            self.threads['notifications'] = notification_thread
            
            logger.info("✅ Sistema de notificações iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema de notificações: {e}")
            return False
    
    def start_backup_system(self):
        """Inicia o sistema de backup automático"""
        try:
            logger.info("💾 Iniciando sistema de backup...")
            
            def run_backup_scheduler():
                try:
                    # Agenda backup diário
                    self.components['backup_system'].schedule_backup('full', 24)
                except Exception as e:
                    logger.error(f"Erro no sistema de backup: {e}")
            
            backup_thread = threading.Thread(target=run_backup_scheduler, daemon=True)
            backup_thread.start()
            self.threads['backup'] = backup_thread
            
            logger.info("✅ Sistema de backup iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema de backup: {e}")
            return False
    
    def start_pix_cleanup(self):
        """Inicia limpeza automática de PIXs expirados"""
        try:
            logger.info("🧹 Iniciando limpeza automática de PIXs...")
            
            def run_pix_cleanup():
                try:
                    while not self.stop_event.is_set():
                        self.components['pix_generator'].cleanup_expired_pix()
                        time.sleep(60)  # Verifica a cada minuto
                except Exception as e:
                    logger.error(f"Erro na limpeza de PIXs: {e}")
            
            cleanup_thread = threading.Thread(target=run_pix_cleanup, daemon=True)
            cleanup_thread.start()
            self.threads['pix_cleanup'] = cleanup_thread
            
            logger.info("✅ Limpeza automática de PIXs iniciada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar limpeza de PIXs: {e}")
            return False
    
    def start_health_monitor(self):
        """Inicia monitoramento de saúde do sistema"""
        try:
            logger.info("🏥 Iniciando monitoramento de saúde...")
            
            def run_health_monitor():
                try:
                    while not self.stop_event.is_set():
                        # Verifica saúde dos componentes
                        self._check_system_health()
                        time.sleep(300)  # Verifica a cada 5 minutos
                except Exception as e:
                    logger.error(f"Erro no monitoramento de saúde: {e}")
            
            health_thread = threading.Thread(target=run_health_monitor, daemon=True)
            health_thread.start()
            self.threads['health_monitor'] = health_thread
            
            logger.info("✅ Monitoramento de saúde iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar monitoramento de saúde: {e}")
            return False
    
    def _check_system_health(self):
        """Verifica saúde do sistema"""
        try:
            # Verifica se os threads estão rodando
            for name, thread in self.threads.items():
                if not thread.is_alive():
                    logger.warning(f"⚠️ Thread {name} não está rodando")
            
            # Verifica espaço em disco
            disk_usage = self._get_disk_usage()
            if disk_usage > 90:  # Mais de 90% de uso
                logger.warning(f"⚠️ Disco com pouco espaço: {disk_usage}%")
            
            # Verifica uso de memória
            memory_usage = self._get_memory_usage()
            if memory_usage > 80:  # Mais de 80% de uso
                logger.warning(f"⚠️ Memória com alto uso: {memory_usage}%")
            
            logger.info("🏥 Verificação de saúde concluída")
            
        except Exception as e:
            logger.error(f"Erro na verificação de saúde: {e}")
    
    def _get_disk_usage(self):
        """Obtém uso do disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            return (used / total) * 100
        except:
            return 0
    
    def _get_memory_usage(self):
        """Obtém uso da memória"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0
    
    def start(self):
        """Inicia o bot completo"""
        try:
            logger.info("🤖 JOÃOZINHO STORE BOT - Iniciando...")
            logger.info("=" * 50)
            
            # Inicializa componentes
            if not self.initialize_components():
                logger.error("❌ Falha ao inicializar componentes")
                return False
            
            # Inicia serviços
            services = [
                ('Telegram Bot', self.start_telegram_bot),
                ('Sistema de Notificações', self.start_notification_system),
                ('Sistema de Backup', self.start_backup_system),
                ('Limpeza de PIXs', self.start_pix_cleanup),
                ('Monitor de Saúde', self.start_health_monitor)
            ]
            
            for service_name, service_func in services:
                if not service_func():
                    logger.error(f"❌ Falha ao iniciar {service_name}")
                    return False
            
            self.running = True
            logger.info("🎉 Bot iniciado com sucesso!")
            logger.info("=" * 50)
            logger.info(f"📱 WhatsApp: {config.CALLMEBOT_PHONE}")
            logger.info(f"📨 Telegram: @{config.BOT_NAME}")
            logger.info(f"👑 Admin ID: {config.ADMIN_ID}")
            logger.info(f"💰 Min Recarga: R${config.MIN_RECHARGE}")
            logger.info(f"💰 Max Recarga: R${config.MAX_RECHARGE}")
            logger.info(f"⏰ PIX Expira em: {config.PIX_EXPIRATION_MINUTES} min")
            logger.info(f"👥 Comissão Afiliado: {config.AFFILIATE_COMMISSION * 100}%")
            logger.info("=" * 50)
            
            # Aguarda sinal de parada
            while self.running and not self.stop_event.is_set():
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro fatal ao iniciar bot: {e}")
            return False
    
    def stop(self):
        """Para o bot"""
        try:
            logger.info("🛑 Parando bot...")
            
            self.running = False
            self.stop_event.set()
            
            # Aguarda threads terminarem
            for name, thread in self.threads.items():
                if thread.is_alive():
                    logger.info(f"Parando thread: {name}")
                    thread.join(timeout=5)
            
            logger.info("✅ Bot parado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar bot: {e}")
    
    def get_status(self):
        """Retorna status do bot"""
        status = {
            'running': self.running,
            'components': {},
            'threads': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Status dos componentes
        for name, component in self.components.items():
            status['components'][name] = {
                'initialized': component is not None,
                'type': type(component).__name__
            }
        
        # Status dos threads
        for name, thread in self.threads.items():
            status['threads'][name] = {
                'alive': thread.is_alive(),
                'daemon': thread.daemon
            }
        
        return status

def main():
    """Função principal"""
    try:
        # Cria diretórios necessários
        directories = ['qr_codes', 'logs', 'backups', 'data']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Diretório criado: {directory}")
        
        # Inicializa e inicia o bot
        bot_manager = BotManager()
        
        if bot_manager.start():
            print("🎉 Bot iniciado com sucesso!")
            print("Pressione Ctrl+C para parar")
            
            # Aguarda indefinidamente
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Interrupção recebida, parando bot...")
                bot_manager.stop()
        else:
            print("❌ Falha ao iniciar bot")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()