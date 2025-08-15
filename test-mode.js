#!/usr/bin/env node

console.log('🧪 MODO DE TESTE - Joãozinho Store Bot\n');

// Configurar variáveis de ambiente para teste
process.env.WHATSAPP_PHONE = '5544998312326';
process.env.WHATSAPP_API_KEY = 'test_key';
process.env.TELEGRAM_STORE_BOT_TOKEN = 'test_store_token';
process.env.TELEGRAM_ADMIN_BOT_TOKEN = 'test_admin_token';
process.env.ADMIN_TELEGRAM_ID = '8206910765';
process.env.STORE_NAME = 'JOÃOZINHO STORE BOT (TESTE)';
process.env.PORT = '3000';

console.log('⚙️  Configurações de teste aplicadas');
console.log('📋 Variáveis configuradas:');
console.log('   - WHATSAPP_PHONE: ' + process.env.WHATSAPP_PHONE);
console.log('   - STORE_NAME: ' + process.env.STORE_NAME);
console.log('   - PORT: ' + process.env.PORT);
console.log('   - Demais variáveis: configuradas para teste\n');

try {
    console.log('💾 Inicializando banco de dados em modo teste...');
    const db = require('./database');
    console.log('✅ Banco de dados conectado');

    // Criar produtos de exemplo
    setTimeout(async () => {
        try {
            console.log('📦 Criando produtos de exemplo...');
            
            const produtos = [
                { name: 'NETFLIX PREMIUM', description: 'Acesso Netflix Premium por 30 dias', price: 15.00, stock: 100 },
                { name: 'SPOTIFY PREMIUM', description: 'Spotify Premium por 30 dias', price: 8.00, stock: 50 },
                { name: 'DISNEY+ PREMIUM', description: 'Disney Plus Premium por 30 dias', price: 12.00, stock: 75 },
                { name: 'AMAZON PRIME', description: 'Amazon Prime Video por 30 dias', price: 10.00, stock: 60 }
            ];

            for (const produto of produtos) {
                await db.createProduct(produto.name, produto.description, produto.price, produto.stock);
            }
            
            console.log('✅ Produtos de exemplo criados');
            
            // Criar usuário de teste
            console.log('👤 Criando usuário de teste...');
            await db.createUser('123456789', 'TestUser', '5544998312326');
            console.log('✅ Usuário de teste criado');
            
        } catch (error) {
            console.log('⚠️  Erro ao criar dados de exemplo:', error.message);
        }
    }, 2000);

    console.log('🌐 Iniciando servidor web em modo teste...');
    
    // Interceptar erros de bots e continuar
    const originalConsoleError = console.error;
    console.error = function(...args) {
        const message = args.join(' ');
        if (message.includes('TELEGRAM_TOKEN') || message.includes('401') || message.includes('Unauthorized')) {
            console.log('⚠️  Bot Telegram: Token inválido (esperado no modo teste)');
            return;
        }
        originalConsoleError.apply(console, args);
    };

    // Inicializar sistema principal
    require('./index');
    
    console.log('\n🎉 SISTEMA EM MODO TESTE INICIADO COM SUCESSO!');
    console.log('🌐 Acesse: http://localhost:3000');
    console.log('📱 WhatsApp: Simulado (não envia mensagens reais)');
    console.log('🤖 Telegram: Desabilitado (tokens de teste)');
    console.log('💾 Banco: SQLite local funcionando');
    console.log('🔧 APIs: Modo simulação ativo\n');
    
    console.log('💡 Para usar o sistema real:');
    console.log('1. Configure o arquivo .env com tokens reais');
    console.log('2. Execute: npm start\n');
    
} catch (error) {
    console.error('❌ Erro no modo teste:', error.message);
    console.log('\n🔧 Possíveis soluções:');
    console.log('1. Execute: npm install');
    console.log('2. Verifique se o Node.js está atualizado');
    console.log('3. Reporte o erro se persistir\n');
    process.exit(1);
}