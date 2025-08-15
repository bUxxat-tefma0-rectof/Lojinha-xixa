import os
from dotenv import load_dotenv

load_dotenv()

# Tokens dos bots
TELEGRAM_BOT_TOKEN = "8355155370:AAEF_mx0b0FxMkB7SQsFhv-asrSv0NeUbQA"
TELEGRAM_ADMIN_TOKEN = "8355155370:AAEF_mx0b0FxMkB7SQsFhv-asrSv0NeUbQA"

# CallMeBot API
CALLMEBOT_API_KEY = "8334846"
CALLMEBOT_PHONE = "554498312326"
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

# WhatsApp Business API (para funcionalidades avançadas)
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

# Configurações do bot
BOT_NAME = "JOÃOZINHO STORE BOT"
ADMIN_ID = 8206910765
MIN_RECHARGE = 1.00
MAX_RECHARGE = 1000.00
PIX_EXPIRATION_MINUTES = 30
AFFILIATE_COMMISSION = 0.50  # 50%

# Configurações de banco de dados
DATABASE_FILE = "store_bot.db"

# Configurações de notificação
SUPPORT_GROUP_LINK = "https://chat.whatsapp.com/EAMz3pt1kPe9VPO9rK8ccF?mode=ems_copy_t"

# Configurações de produtos padrão
DEFAULT_PRODUCTS = [
    {
        "name": "NETFLIX PREMIUM",
        "price": 10.00,
        "description": "Acesso premium ao Netflix",
        "stock": 100,
        "category": "streaming"
    },
    {
        "name": "DISNEY+ PREMIUM",
        "price": 8.00,
        "description": "Acesso premium ao Disney+",
        "stock": 50,
        "category": "streaming"
    },
    {
        "name": "HBO MAX",
        "price": 12.00,
        "description": "Acesso premium ao HBO Max",
        "stock": 75,
        "category": "streaming"
    },
    {
        "name": "SPOTIFY PREMIUM",
        "price": 5.00,
        "description": "Acesso premium ao Spotify",
        "stock": 200,
        "category": "música"
    }
]