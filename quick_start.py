#!/usr/bin/env python3
"""
Script de Inicialização Rápida do JOÃOZINHO STORE BOT
Inicia o bot de forma simples e rápida
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou superior é necessário!")
        print(f"Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("📦 Verificando dependências...")
    
    required_packages = [
        'telegram',
        'requests',
        'qrcode',
        'PIL',
        'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NÃO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Instalando dependências...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            print("Execute manualmente: pip install -r requirements.txt")
            return False
    
    return True

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    print("📁 Verificando arquivos...")
    
    required_files = [
        'start_bot.py',
        'telegram_bot.py',
        'whatsapp_bot.py',
        'database.py',
        'pix_generator.py',
        'config.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NÃO ENCONTRADO")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("📂 Criando diretórios...")
    
    directories = ['qr_codes', 'logs', 'backups', 'data']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Criado: {directory}")
        else:
            print(f"   ✅ Existe: {directory}")

def check_config():
    """Verifica configurações básicas"""
    print("⚙️ Verificando configurações...")
    
    try:
        import config
        
        # Verifica configurações essenciais
        essential_configs = [
            ('BOT_NAME', config.BOT_NAME),
            ('ADMIN_ID', config.ADMIN_ID),
            ('TELEGRAM_BOT_TOKEN', config.TELEGRAM_BOT_TOKEN),
            ('CALLMEBOT_API_KEY', config.CALLMEBOT_API_KEY),
            ('CALLMEBOT_PHONE', config.CALLMEBOT_PHONE)
        ]
        
        for config_name, config_value in essential_configs:
            if config_value:
                print(f"   ✅ {config_name}: {str(config_value)[:20]}...")
            else:
                print(f"   ❌ {config_name}: NÃO CONFIGURADO")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar configurações: {e}")
        return False

def start_bot():
    """Inicia o bot"""
    print("🚀 Iniciando o bot...")
    
    try:
        # Inicia o bot em processo separado
        process = subprocess.Popen([sys.executable, "start_bot.py"])
        
        print("✅ Bot iniciado com sucesso!")
        print(f"📱 WhatsApp: {config.CALLMEBOT_PHONE}")
        print(f"📨 Telegram: @{config.BOT_NAME}")
        print(f"👑 Admin ID: {config.ADMIN_ID}")
        print("\n🔄 Bot rodando em segundo plano...")
        print("📝 Logs salvos em: bot.log")
        print("🛑 Para parar: Ctrl+C")
        
        # Aguarda processo
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando bot...")
            process.terminate()
            process.wait()
            print("✅ Bot parado!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")
        return False

def start_admin_panel():
    """Inicia o painel de administração"""
    print("🔧 Iniciando painel de administração...")
    
    try:
        # Inicia painel em processo separado
        process = subprocess.Popen([sys.executable, "admin_panel.py"])
        
        print("✅ Painel de administração iniciado!")
        print("🌐 Acesse: http://localhost:5001")
        print(f"🔑 Login com ID: {config.ADMIN_ID}")
        print("\n🔄 Painel rodando em segundo plano...")
        print("🛑 Para parar: Ctrl+C")
        
        # Aguarda processo
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Parando painel...")
            process.terminate()
            process.wait()
            print("✅ Painel parado!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao iniciar painel: {e}")
        return False

def run_tests():
    """Executa testes básicos"""
    print("🧪 Executando testes básicos...")
    
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Testes passaram!")
            return True
        else:
            print("❌ Testes falharam!")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False

def show_menu():
    """Mostra menu de opções"""
    print("\n🤖 JOÃOZINHO STORE BOT - MENU PRINCIPAL")
    print("=" * 50)
    print("1. 🚀 Iniciar Bot")
    print("2. 🔧 Painel de Administração")
    print("3. 🧪 Executar Testes")
    print("4. 📊 Ver Status")
    print("5. 📝 Ver Logs")
    print("6. 🔄 Reiniciar Bot")
    print("7. 🛑 Parar Bot")
    print("8. 📖 Ver Documentação")
    print("9. 🚪 Sair")
    print("=" * 50)

def get_user_choice():
    """Obtém escolha do usuário"""
    while True:
        try:
            choice = input("\nEscolha uma opção (1-9): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return choice
            else:
                print("❌ Opção inválida. Digite 1-9.")
        except KeyboardInterrupt:
            print("\n\n🛑 Saindo...")
            sys.exit(0)

def show_status():
    """Mostra status do sistema"""
    print("📊 STATUS DO SISTEMA")
    print("-" * 30)
    
    # Verifica processos
    try:
        bot_process = subprocess.run(["pgrep", "-f", "start_bot.py"], 
                                   capture_output=True, text=True)
        admin_process = subprocess.run(["pgrep", "-f", "admin_panel.py"], 
                                     capture_output=True, text=True)
        
        print(f"🤖 Bot: {'🟢 Rodando' if bot_process.returncode == 0 else '🔴 Parado'}")
        print(f"🔧 Painel Admin: {'🟢 Rodando' if admin_process.returncode == 0 else '🔴 Parado'}")
        
        # Verifica arquivos de log
        if os.path.exists('bot.log'):
            log_size = os.path.getsize('bot.log')
            print(f"📝 Log: 🟢 {log_size} bytes")
        else:
            print("📝 Log: 🔴 Não encontrado")
        
        # Verifica banco de dados
        if os.path.exists('store_bot.db'):
            db_size = os.path.getsize('store_bot.db')
            print(f"📊 Banco: 🟢 {db_size} bytes")
        else:
            print("📊 Banco: 🔴 Não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def show_logs():
    """Mostra logs recentes"""
    print("📝 LOGS RECENTES")
    print("-" * 30)
    
    try:
        if os.path.exists('bot.log'):
            with open('bot.log', 'r') as f:
                lines = f.readlines()
                # Mostra últimas 20 linhas
                for line in lines[-20:]:
                    print(line.rstrip())
        else:
            print("❌ Arquivo de log não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao ler logs: {e}")

def main():
    """Função principal"""
    print("🤖 JOÃOZINHO STORE BOT - INICIALIZAÇÃO RÁPIDA")
    print("=" * 60)
    
    # Verificações iniciais
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_files():
        sys.exit(1)
    
    create_directories()
    
    if not check_config():
        print("\n❌ Configure o arquivo config.py antes de continuar!")
        sys.exit(1)
    
    print("\n✅ Sistema verificado e pronto!")
    
    # Menu principal
    while True:
        show_menu()
        choice = get_user_choice()
        
        if choice == '1':
            start_bot()
        elif choice == '2':
            start_admin_panel()
        elif choice == '3':
            run_tests()
        elif choice == '4':
            show_status()
        elif choice == '5':
            show_logs()
        elif choice == '6':
            print("🔄 Reiniciando bot...")
            # Implementar reinicialização
            print("⚠️  Funcionalidade em desenvolvimento")
        elif choice == '7':
            print("🛑 Parando bot...")
            # Implementar parada
            print("⚠️  Funcionalidade em desenvolvimento")
        elif choice == '8':
            print("📖 Documentação:")
            print("   - README.md: Instruções completas")
            print("   - demo.py: Demonstração das funcionalidades")
            print("   - test_bot.py: Testes do sistema")
        elif choice == '9':
            print("👋 Saindo...")
            break
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Programa interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)