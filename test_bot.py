#!/usr/bin/env python3
"""
Script de teste para o JOÃOZINHO STORE BOT
Testa todas as funcionalidades principais do bot
"""

import sys
import os
import sqlite3
from datetime import datetime
import config
from database import Database
from pix_generator import PixGenerator

def test_database():
    """Testa funcionalidades do banco de dados"""
    print("🧪 Testando banco de dados...")
    
    try:
        # Inicializa banco
        db = Database()
        print("✅ Banco de dados inicializado com sucesso")
        
        # Testa criação de usuário
        user = db.get_or_create_user(
            telegram_id=123456789,
            username="test_user",
            first_name="Teste",
            last_name="Usuário"
        )
        print(f"✅ Usuário criado: {user['affiliate_code']}")
        
        # Testa busca de produtos
        products = db.get_products()
        print(f"✅ Produtos encontrados: {len(products)}")
        
        # Testa configurações
        bot_config = db.get_bot_config()
        print(f"✅ Configurações carregadas: {len(bot_config)} itens")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def test_pix_generator():
    """Testa funcionalidades do gerador de PIX"""
    print("\n🧪 Testando gerador de PIX...")
    
    try:
        # Inicializa gerador
        pix_gen = PixGenerator()
        print("✅ Gerador de PIX inicializado")
        
        # Testa geração de PIX
        pix_result = pix_gen.generate_pix(10.00, 1)
        
        if pix_result['success']:
            print(f"✅ PIX gerado: {pix_result['pix_code'][:50]}...")
            print(f"✅ QR Code: {pix_result['qr_code']}")
            print(f"✅ Expira em: {pix_result['expiration_formatted']}")
        else:
            print(f"❌ Erro ao gerar PIX: {pix_result['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no gerador de PIX: {e}")
        return False

def test_config():
    """Testa configurações do bot"""
    print("\n🧪 Testando configurações...")
    
    try:
        print(f"✅ Nome do bot: {config.BOT_NAME}")
        print(f"✅ Admin ID: {config.ADMIN_ID}")
        print(f"✅ Token Telegram: {config.TELEGRAM_BOT_TOKEN[:20]}...")
        print(f"✅ CallMeBot API Key: {config.CALLMEBOT_API_KEY}")
        print(f"✅ CallMeBot Phone: {config.CALLMEBOT_PHONE}")
        print(f"✅ Min Recharge: R${config.MIN_RECHARGE}")
        print(f"✅ Max Recharge: R${config.MAX_RECHARGE}")
        print(f"✅ PIX Expiration: {config.PIX_EXPIRATION_MINUTES} minutos")
        print(f"✅ Affiliate Commission: {config.AFFILIATE_COMMISSION * 100}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_dependencies():
    """Testa se todas as dependências estão instaladas"""
    print("\n🧪 Testando dependências...")
    
    required_packages = [
        'telegram',
        'requests',
        'qrcode',
        'PIL',
        'aiohttp',
        'flask'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NÃO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def test_file_structure():
    """Testa estrutura de arquivos"""
    print("\n🧪 Testando estrutura de arquivos...")
    
    required_files = [
        'main.py',
        'telegram_bot.py',
        'whatsapp_bot.py',
        'database.py',
        'pix_generator.py',
        'config.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - NÃO ENCONTRADO")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    return True

def test_directories():
    """Testa criação de diretórios necessários"""
    print("\n🧪 Testando diretórios...")
    
    required_dirs = [
        'qr_codes',
        'logs',
        'data'
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Diretório criado: {directory}")
        else:
            print(f"✅ Diretório existe: {directory}")

def run_integration_test():
    """Executa teste de integração"""
    print("\n🧪 Executando teste de integração...")
    
    try:
        # Testa fluxo completo de usuário
        db = Database()
        
        # Cria usuário
        user = db.get_or_create_user(
            telegram_id=999999999,
            username="integration_test",
            first_name="Integration",
            last_name="Test"
        )
        
        # Adiciona saldo
        db.update_user_balance(user['telegram_id'], 50.00, 'add')
        
        # Busca produtos
        products = db.get_products()
        if products:
            product = products[0]
            
            # Cria transação
            transaction_id = db.create_transaction(
                user_id=user['id'],
                type='recharge',
                amount=25.00,
                description='Teste de integração'
            )
            
            # Cria compra
            purchase_id = db.create_purchase(
                user_id=user['id'],
                product_id=product['id'],
                amount=product['price']
            )
            
            print(f"✅ Usuário criado: {user['affiliate_code']}")
            print(f"✅ Saldo adicionado: R$50,00")
            print(f"✅ Transação criada: {transaction_id}")
            print(f"✅ Compra criada: {purchase_id}")
            
            return True
        else:
            print("❌ Nenhum produto encontrado para teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🤖 JOÃOZINHO STORE BOT - TESTE COMPLETO")
    print("=" * 50)
    
    tests = [
        ("Estrutura de arquivos", test_file_structure),
        ("Dependências", test_dependencies),
        ("Configurações", test_config),
        ("Banco de dados", test_database),
        ("Gerador de PIX", test_pix_generator),
        ("Diretórios", test_directories),
        ("Teste de integração", run_integration_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  Teste '{test_name}' falhou")
        except Exception as e:
            print(f"❌ Erro no teste '{test_name}': {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO DOS TESTES: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O bot está pronto para uso.")
        print("\n📋 Para iniciar o bot:")
        print("1. Configure o arquivo .env com suas credenciais")
        print("2. Execute: python main.py")
        print("3. Ou use: ./run_bot.sh (após executar install.sh)")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        print("\n🔧 Para resolver problemas:")
        print("1. Execute: pip install -r requirements.txt")
        print("2. Verifique se todos os arquivos estão presentes")
        print("3. Confirme as configurações em config.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)