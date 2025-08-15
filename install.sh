#!/bin/bash

# JOÃOZINHO STORE BOT - Script de Instalação
# Este script instala todas as dependências necessárias para o bot

echo "🤖 JOÃOZINHO STORE BOT - Instalação Automática"
echo "================================================"

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
else
    echo "✅ Python 3 já está instalado"
fi

# Verifica se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instalando..."
    sudo apt install -y python3-pip
else
    echo "✅ pip3 já está instalado"
fi

# Cria ambiente virtual
echo "🔧 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Atualiza pip
echo "📦 Atualizando pip..."
pip install --upgrade pip

# Instala dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Cria diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p qr_codes
mkdir -p logs
mkdir -p data

# Configura permissões
echo "🔐 Configurando permissões..."
chmod +x main.py
chmod +x telegram_bot.py
chmod +x whatsapp_bot.py

# Cria arquivo de configuração se não existir
if [ ! -f .env ]; then
    echo "⚙️ Criando arquivo de configuração..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!"
fi

# Cria script de execução
echo "🚀 Criando script de execução..."
cat > run_bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF

chmod +x run_bot.sh

# Cria script de parada
echo "🛑 Criando script de parada..."
cat > stop_bot.sh << 'EOF'
#!/bin/bash
echo "Parando o bot..."
pkill -f "python main.py"
echo "Bot parado!"
EOF

chmod +x stop_bot.sh

# Cria serviço systemd (opcional)
echo "🔧 Criando serviço systemd..."
sudo tee /etc/systemd/system/joaozinho-bot.service > /dev/null << EOF
[Unit]
Description=JOÃOZINHO STORE BOT
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/run_bot.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarrega systemd
sudo systemctl daemon-reload

echo ""
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite o arquivo .env com suas configurações"
echo "2. Execute o bot com: ./run_bot.sh"
echo "3. Para parar: ./stop_bot.sh"
echo "4. Para executar como serviço: sudo systemctl start joaozinho-bot"
echo "5. Para executar automaticamente na inicialização: sudo systemctl enable joaozinho-bot"
echo ""
echo "📚 Documentação: README.md"
echo "🐛 Logs: logs/bot.log"
echo ""
echo "🤖 Bot pronto para uso!"