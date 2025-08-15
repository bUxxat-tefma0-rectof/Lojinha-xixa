#!/usr/bin/env node

console.log('🚀 Iniciando sistema Joãozinho Store Bot...\n');

// Verificar se as variáveis de ambiente estão configuradas
const requiredEnvVars = [
    'WHATSAPP_PHONE',
    'WHATSAPP_API_KEY',
    'TELEGRAM_STORE_BOT_TOKEN',
    'TELEGRAM_ADMIN_BOT_TOKEN',
    'ADMIN_TELEGRAM_ID'
];

console.log('📋 Verificando configurações...');

let missingVars = [];
requiredEnvVars.forEach(varName => {
    if (!process.env[varName]) {
        missingVars.push(varName);
    }
});

if (missingVars.length > 0) {
    console.log('⚠️  Algumas variáveis de ambiente não estão configuradas:');
    missingVars.forEach(varName => {
        console.log(`   - ${varName}`);
    });
    console.log('\n💡 Configure essas variáveis no arquivo .env antes de continuar.\n');
    
    // Mostrar exemplo do .env
    console.log('📝 Exemplo de configuração (.env):');
    console.log(`
WHATSAPP_PHONE=5544998312326
WHATSAPP_API_KEY=sua_api_key_aqui
TELEGRAM_STORE_BOT_TOKEN=seu_token_bot_loja
TELEGRAM_ADMIN_BOT_TOKEN=seu_token_bot_admin
ADMIN_TELEGRAM_ID=seu_id_telegram
    `);
    
    console.log('⚡ Para testar sem configuração real, execute: node test-mode.js\n');
    process.exit(1);
}

console.log('✅ Configurações OK');

try {
    console.log('💾 Inicializando banco de dados...');
    const db = require('./database');
    console.log('✅ Banco de dados conectado');

    console.log('📱 Inicializando sistema principal...');
    require('./index');
    
} catch (error) {
    console.error('❌ Erro ao inicializar sistema:', error.message);
    console.log('\n🔧 Dicas para resolver:');
    console.log('1. Verifique se todas as dependências estão instaladas: npm install');
    console.log('2. Verifique se o arquivo .env está configurado corretamente');
    console.log('3. Verifique os tokens dos bots Telegram');
    console.log('4. Para modo de teste: node test-mode.js\n');
    process.exit(1);
}