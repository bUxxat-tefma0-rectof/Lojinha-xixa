#!/usr/bin/env python3
"""
Script de Demonstração do JOÃOZINHO STORE BOT
Mostra todas as funcionalidades principais do bot
"""

import time
import sys
from datetime import datetime
import config
from database import Database
from pix_generator import PixGenerator
from whatsapp_bot import WhatsAppBot

def print_header():
    """Imprime cabeçalho da demonstração"""
    print("🤖 JOÃOZINHO STORE BOT - DEMONSTRAÇÃO")
    print("=" * 60)
    print("Este script demonstra todas as funcionalidades do bot")
    print("=" * 60)
    print()

def demo_database():
    """Demonstra funcionalidades do banco de dados"""
    print("📊 DEMONSTRAÇÃO DO BANCO DE DADOS")
    print("-" * 40)
    
    try:
        # Inicializa banco
        db = Database()
        print("✅ Banco de dados inicializado")
        
        # Cria usuário de teste
        user = db.get_or_create_user(
            telegram_id=999999999,
            username="demo_user",
            first_name="Usuário",
            last_name="Demonstração"
        )
        print(f"✅ Usuário criado: {user['affiliate_code']}")
        
        # Lista produtos
        products = db.get_products()
        print(f"✅ Produtos encontrados: {len(products)}")
        
        for product in products:
            print(f"   📦 {product['name']} - R${product['price']:.2f}")
        
        # Configurações
        bot_config = db.get_bot_config()
        print(f"✅ Configurações carregadas: {len(bot_config)} itens")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def demo_pix_generator():
    """Demonstra funcionalidades do gerador de PIX"""
    print("💰 DEMONSTRAÇÃO DO GERADOR DE PIX")
    print("-" * 40)
    
    try:
        # Inicializa gerador
        pix_gen = PixGenerator()
        print("✅ Gerador de PIX inicializado")
        
        # Gera PIX de teste
        pix_result = pix_gen.generate_pix(25.00, 1)
        
        if pix_result['success']:
            print(f"✅ PIX gerado com sucesso!")
            print(f"   💰 Valor: R${pix_result['amount']:.2f}")
            print(f"   🆔 ID: {pix_result['transaction_id']}")
            print(f"   ⏰ Expira: {pix_result['expiration_formatted']}")
            print(f"   📱 QR Code: {pix_result['qr_code']}")
        else:
            print(f"❌ Erro ao gerar PIX: {pix_result['error']}")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erro no gerador de PIX: {e}")
        return False

def demo_whatsapp_bot():
    """Demonstra funcionalidades do bot do WhatsApp"""
    print("📱 DEMONSTRAÇÃO DO BOT DO WHATSAPP")
    print("-" * 40)
    
    try:
        # Inicializa bot
        whatsapp_bot = WhatsAppBot()
        print("✅ Bot do WhatsApp inicializado")
        
        # Mostra configurações
        print(f"   📞 Número: {whatsapp_bot.phone}")
        print(f"   🔑 API Key: {whatsapp_bot.api_key}")
        print(f"   🌐 URL: {whatsapp_bot.api_url}")
        
        # Simula envio de mensagem
        print("   📤 Testando envio de mensagem...")
        # whatsapp_bot.send_message("5544999999999", "Teste do bot de demonstração")
        print("   ✅ Mensagem enviada (simulado)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erro no bot do WhatsApp: {e}")
        return False

def demo_config():
    """Demonstra configurações do bot"""
    print("⚙️ DEMONSTRAÇÃO DAS CONFIGURAÇÕES")
    print("-" * 40)
    
    try:
        print(f"🤖 Nome do Bot: {config.BOT_NAME}")
        print(f"👑 Admin ID: {config.ADMIN_ID}")
        print(f"📱 WhatsApp: {config.CALLMEBOT_PHONE}")
        print(f"🔑 API Key: {config.CALLMEBOT_API_KEY}")
        print(f"💰 Min Recarga: R${config.MIN_RECHARGE}")
        print(f"💰 Max Recarga: R${config.MAX_RECHARGE}")
        print(f"⏰ PIX Expira em: {config.PIX_EXPIRATION_MINUTES} min")
        print(f"👥 Comissão Afiliado: {config.AFFILIATE_COMMISSION * 100}%")
        print(f"📊 Banco: {config.DATABASE_FILE}")
        print(f"🔗 Grupo Suporte: {config.SUPPORT_GROUP_LINK}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def demo_features():
    """Demonstra funcionalidades principais"""
    print("🚀 DEMONSTRAÇÃO DAS FUNCIONALIDADES")
    print("-" * 40)
    
    features = [
        "✅ Sistema de usuários com IDs únicos",
        "✅ Cadastro automático de usuários",
        "✅ Sistema de saldo e recargas",
        "✅ Geração automática de PIX",
        "✅ QR Code para pagamentos",
        "✅ Validação automática de pagamentos",
        "✅ Catálogo de produtos",
        "✅ Sistema de estoque",
        "✅ Processamento de compras",
        "✅ Entrega automática de produtos",
        "✅ Sistema de afiliados",
        "✅ Rankings e estatísticas",
        "✅ Histórico de transações",
        "✅ Sistema de notificações",
        "✅ Backup automático",
        "✅ Painel de administração web",
        "✅ Bot do Telegram completo",
        "✅ Bot do WhatsApp via CallMeBot",
        "✅ Sistema de flood protection",
        "✅ Logs detalhados",
        "✅ Monitoramento de saúde",
        "✅ Configurações editáveis"
    ]
    
    for feature in features:
        print(f"   {feature}")
        time.sleep(0.1)  # Pequena pausa para efeito visual
    
    print()

def demo_commands():
    """Demonstra comandos disponíveis"""
    print("⌨️ COMANDOS DISPONÍVEIS")
    print("-" * 40)
    
    commands = [
        ("/start", "Menu principal do bot"),
        ("/pix [valor]", "Gera PIX para recarga"),
        ("/historico", "Histórico de compras"),
        ("/afiliados", "Informações de afiliado"),
        ("/id", "Seu ID único"),
        ("/ranking", "Rankings diversos"),
        ("/alertas", "Configurar alertas"),
        ("/admin", "Painel de administração"),
        ("COMPRAR [produto]", "Comprar produto específico"),
        ("HISTORICO", "Ver histórico"),
        ("PERFIL", "Ver perfil"),
        ("RECARGA", "Fazer recarga")
    ]
    
    for command, description in commands:
        print(f"   {command:<20} - {description}")
    
    print()

def demo_products():
    """Demonstra produtos disponíveis"""
    print("🛍️ PRODUTOS DISPONÍVEIS")
    print("-" * 40)
    
    try:
        db = Database()
        products = db.get_products()
        
        for product in products:
            print(f"   🎟️ {product['name']}")
            print(f"      💰 Preço: R${product['price']:.2f}")
            print(f"      📥 Estoque: {product['stock']}")
            print(f"      📝 {product['description']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar produtos: {e}")
        return False

def demo_installation():
    """Demonstra processo de instalação"""
    print("📦 PROCESSO DE INSTALAÇÃO")
    print("-" * 40)
    
    steps = [
        "1. Clone o repositório",
        "2. Instale as dependências: pip install -r requirements.txt",
        "3. Configure o arquivo .env com suas credenciais",
        "4. Execute: python start_bot.py",
        "5. Ou use o script de instalação: ./install.sh"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print()

def demo_usage():
    """Demonstra como usar o bot"""
    print("📖 COMO USAR O BOT")
    print("-" * 40)
    
    usage_steps = [
        "1. Inicie o bot com /start",
        "2. Navegue pelos menus usando os botões",
        "3. Faça recargas via PIX",
        "4. Compre produtos digitais",
        "5. Receba acesso instantâneo",
        "6. Use comandos para funcionalidades específicas"
    ]
    
    for step in usage_steps:
        print(f"   {step}")
    
    print()

def demo_admin():
    """Demonstra funcionalidades de administração"""
    print("🔧 FUNCIONALIDADES DE ADMINISTRAÇÃO")
    print("-" * 40)
    
    admin_features = [
        "✅ Painel web em http://localhost:5001",
        "✅ Login com ID do Telegram",
        "✅ Gerenciamento de produtos",
        "✅ Gerenciamento de usuários",
        "✅ Configurações do bot",
        "✅ Estatísticas e relatórios",
        "✅ Sistema de backup",
        "✅ Monitoramento em tempo real",
        "✅ Logs do sistema",
        "✅ Reinicialização remota"
    ]
    
    for feature in admin_features:
        print(f"   {feature}")
        time.sleep(0.1)
    
    print()

def run_demo():
    """Executa demonstração completa"""
    print_header()
    
    demos = [
        ("Configurações", demo_config),
        ("Banco de Dados", demo_database),
        ("Gerador de PIX", demo_pix_generator),
        ("Bot do WhatsApp", demo_whatsapp_bot),
        ("Funcionalidades", demo_features),
        ("Comandos", demo_commands),
        ("Produtos", demo_products),
        ("Instalação", demo_installation),
        ("Como Usar", demo_usage),
        ("Administração", demo_admin)
    ]
    
    success_count = 0
    total_demos = len(demos)
    
    for demo_name, demo_func in demos:
        print(f"🔄 Executando: {demo_name}")
        if demo_func():
            success_count += 1
            print(f"✅ {demo_name} - SUCESSO")
        else:
            print(f"❌ {demo_name} - FALHOU")
        
        print()
        time.sleep(1)  # Pausa entre demonstrações
    
    # Resultado final
    print("=" * 60)
    print("📊 RESULTADO DA DEMONSTRAÇÃO")
    print("=" * 60)
    print(f"✅ Sucessos: {success_count}")
    print(f"❌ Falhas: {total_demos - success_count}")
    print(f"📈 Taxa de Sucesso: {(success_count/total_demos)*100:.1f}%")
    
    if success_count == total_demos:
        print("\n🎉 TODAS AS DEMONSTRAÇÕES PASSARAM!")
        print("O bot está funcionando perfeitamente!")
    else:
        print(f"\n⚠️ {total_demos - success_count} DEMONSTRAÇÕES FALHARAM")
        print("Verifique os erros acima antes de usar o bot")
    
    print("\n🚀 Para iniciar o bot:")
    print("   python start_bot.py")
    print("\n🔧 Para painel de administração:")
    print("   python admin_panel.py")
    print("\n🧪 Para executar testes:")
    print("   python test_bot.py")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n🛑 Demonstração interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal na demonstração: {e}")
        sys.exit(1)