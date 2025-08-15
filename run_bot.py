#!/usr/bin/env python3
"""
Script simples para executar o JOÃOZINHO STORE BOT
"""

import os
import sys
import time
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🤖 JOÃOZINHO STORE BOT - Iniciando...")
    
    try:
        # Importar componentes
        from start_bot import BotManager
        
        # Criar e iniciar o bot
        bot_manager = BotManager()
        bot_manager.start()
        
        print("✅ Bot iniciado com sucesso!")
        print("📱 Telegram Bot: Ativo")
        print("📱 WhatsApp Bot: Ativo")
        print("🌐 Admin Panel: Ativo")
        print("💾 Banco de dados: Ativo")
        print("💰 PIX Generator: Ativo")
        
        # Manter rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando bot...")
            bot_manager.stop()
            print("✅ Bot parado com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())