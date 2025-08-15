const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
require('dotenv').config();

class VoiceCallSystem {
    constructor() {
        this.callAPI = process.env.VOICE_CALL_API || 'https://api.voice-provider.com';
        this.callAPIKey = process.env.VOICE_CALL_API_KEY;
        this.ttsAPI = process.env.TTS_API || 'https://api.elevenlabs.io/v1';
        this.ttsAPIKey = process.env.TTS_API_KEY;
        this.voiceId = process.env.VOICE_ID || 'default';
        this.callQueue = [];
        this.activeCallbacks = new Map();
        this.setupVoiceTemplates();
    }

    setupVoiceTemplates() {
        this.voiceTemplates = {
            welcome: `Olá! Aqui é o suporte automático da ${process.env.STORE_NAME || 'Joãozinho Store'}. 
                     Como posso ajudá-lo hoje? Você pode me perguntar sobre nossos produtos, 
                     como fazer recargas, ou qualquer dúvida sobre nossa loja.`,
            
            products: `Temos diversos produtos premium disponíveis, incluindo Netflix, Spotify, 
                      Disney Plus, Amazon Prime e muitos outros. Todos com garantia e suporte. 
                      Qual produto você gostaria de saber mais?`,
            
            recharge: `Para fazer uma recarga, você pode usar nosso bot no Telegram ou WhatsApp. 
                      Aceitamos PIX com confirmação automática. O valor mínimo é R$ 1,00 e 
                      o saldo é liberado instantaneamente após o pagamento.`,
            
            support: `Nossa equipe de suporte está disponível 24 horas. Você pode entrar em 
                     contato pelo WhatsApp, Telegram ou através deste sistema de ligação. 
                     Estamos aqui para ajudar!`,
            
            goodbye: `Obrigado por entrar em contato conosco! Se precisar de mais alguma coisa, 
                     não hesite em nos procurar. Tenha um ótimo dia!`,

            error: `Desculpe, não consegui entender sua pergunta. Você pode repetir ou 
                   perguntar de forma diferente? Estou aqui para ajudar com produtos, 
                   recargas e suporte.`
        };
    }

    // Iniciar ligação automática
    async initiateCall(phoneNumber, callType = 'support', userData = {}) {
        try {
            console.log(`📞 Iniciando ligação para ${phoneNumber} - Tipo: ${callType}`);

            // Gerar áudio de boas-vindas
            const welcomeAudio = await this.generateTTS(this.voiceTemplates.welcome);
            
            // Configurar chamada
            const callConfig = {
                to: phoneNumber,
                from: process.env.SUPPORT_PHONE,
                audioUrl: welcomeAudio,
                callType: callType,
                userData: userData,
                webhook: `${process.env.BASE_URL}/webhook/voice-call`,
                timeout: 300 // 5 minutos
            };

            // Fazer chamada usando API de voz
            const callResult = await this.makeVoiceCall(callConfig);

            if (callResult.success) {
                this.activeCallbacks.set(callResult.callId, {
                    phone: phoneNumber,
                    type: callType,
                    userData: userData,
                    startTime: new Date(),
                    status: 'active'
                });

                console.log(`✅ Ligação iniciada: ${callResult.callId}`);
                return { success: true, callId: callResult.callId };
            } else {
                console.error(`❌ Falha ao iniciar ligação: ${callResult.error}`);
                return { success: false, error: callResult.error };
            }

        } catch (error) {
            console.error('Erro ao iniciar ligação:', error);
            return { success: false, error: error.message };
        }
    }

    // Fazer chamada usando API de voz
    async makeVoiceCall(config) {
        try {
            if (!this.callAPIKey) {
                // Simular chamada para desenvolvimento
                return this.simulateVoiceCall(config);
            }

            const response = await axios.post(`${this.callAPI}/calls`, {
                to: config.to,
                from: config.from,
                audio_url: config.audioUrl,
                webhook_url: config.webhook,
                timeout: config.timeout
            }, {
                headers: {
                    'Authorization': `Bearer ${this.callAPIKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return {
                success: true,
                callId: response.data.call_id || this.generateCallId(),
                data: response.data
            };

        } catch (error) {
            console.error('Erro na API de chamadas:', error.response?.data || error.message);
            return {
                success: false,
                error: error.response?.data?.message || error.message
            };
        }
    }

    // Simular chamada para desenvolvimento
    async simulateVoiceCall(config) {
        const callId = this.generateCallId();
        
        // Simular tempo de chamada
        setTimeout(() => {
            this.processVoiceWebhook({
                call_id: callId,
                status: 'answered',
                duration: 0
            });
        }, 2000);

        // Simular conversação
        setTimeout(() => {
            this.processVoiceWebhook({
                call_id: callId,
                status: 'completed',
                duration: 120,
                transcript: 'Usuário perguntou sobre produtos Netflix'
            });
        }, 10000);

        return { success: true, callId: callId };
    }

    // Gerar áudio usando TTS (Text-to-Speech)
    async generateTTS(text, voiceSettings = {}) {
        try {
            if (!this.ttsAPIKey) {
                // Retornar URL fictícia para desenvolvimento
                return `${process.env.BASE_URL}/audio/tts_${Date.now()}.mp3`;
            }

            const response = await axios.post(
                `${this.ttsAPI}/text-to-speech/${this.voiceId}`,
                {
                    text: text,
                    model_id: "eleven_multilingual_v2",
                    voice_settings: {
                        stability: voiceSettings.stability || 0.5,
                        similarity_boost: voiceSettings.similarity_boost || 0.8,
                        style: voiceSettings.style || 0.0,
                        use_speaker_boost: voiceSettings.use_speaker_boost || true
                    }
                },
                {
                    headers: {
                        'Accept': 'audio/mpeg',
                        'Content-Type': 'application/json',
                        'xi-api-key': this.ttsAPIKey
                    },
                    responseType: 'stream'
                }
            );

            // Salvar áudio
            const audioPath = path.join(__dirname, 'temp', `tts_${Date.now()}.mp3`);
            const writer = fs.createWriteStream(audioPath);
            response.data.pipe(writer);

            return new Promise((resolve, reject) => {
                writer.on('finish', () => {
                    // Upload para CDN ou retornar URL local
                    const audioUrl = `${process.env.BASE_URL}/audio/${path.basename(audioPath)}`;
                    resolve(audioUrl);
                });
                writer.on('error', reject);
            });

        } catch (error) {
            console.error('Erro ao gerar TTS:', error);
            return null;
        }
    }

    // Processar webhook de chamada de voz
    async processVoiceWebhook(webhookData) {
        try {
            const { call_id, status, transcript, duration, user_input } = webhookData;
            const callData = this.activeCallbacks.get(call_id);

            if (!callData) {
                console.log('Chamada não encontrada:', call_id);
                return { success: false, error: 'Call not found' };
            }

            console.log(`📞 Webhook de voz - Status: ${status} - Call ID: ${call_id}`);

            switch (status) {
                case 'answered':
                    await this.handleCallAnswered(call_id, callData);
                    break;

                case 'speech_detected':
                    await this.handleUserSpeech(call_id, callData, transcript || user_input);
                    break;

                case 'no_input':
                    await this.handleNoInput(call_id, callData);
                    break;

                case 'completed':
                case 'hung_up':
                    await this.handleCallCompleted(call_id, callData, duration);
                    break;

                case 'failed':
                    await this.handleCallFailed(call_id, callData);
                    break;

                default:
                    console.log('Status de chamada não reconhecido:', status);
            }

            return { success: true, processed: true };

        } catch (error) {
            console.error('Erro ao processar webhook de voz:', error);
            return { success: false, error: error.message };
        }
    }

    // Lidar com chamada atendida
    async handleCallAnswered(callId, callData) {
        console.log(`✅ Chamada atendida: ${callId}`);
        
        // Atualizar status
        callData.status = 'answered';
        callData.answeredAt = new Date();
        
        // Opcional: reproduzir menu de opções
        const menuAudio = await this.generateTTS(
            "Para produtos premium, diga 'produtos'. Para recargas, diga 'recarga'. Para suporte, diga 'suporte'."
        );
        
        if (menuAudio) {
            await this.playAudioInCall(callId, menuAudio);
        }
    }

    // Lidar com fala do usuário
    async handleUserSpeech(callId, callData, transcript) {
        console.log(`🎤 Usuário falou: "${transcript}"`);
        
        // Analisar intent da fala
        const intent = this.analyzeUserIntent(transcript);
        let responseText = '';

        switch (intent) {
            case 'products':
                responseText = this.voiceTemplates.products;
                break;
            case 'recharge':
                responseText = this.voiceTemplates.recharge;
                break;
            case 'support':
                responseText = this.voiceTemplates.support;
                break;
            case 'goodbye':
                responseText = this.voiceTemplates.goodbye;
                // Programar encerramento da chamada
                setTimeout(() => this.endCall(callId), 3000);
                break;
            default:
                responseText = this.voiceTemplates.error;
        }

        // Gerar e reproduzir resposta
        const responseAudio = await this.generateTTS(responseText);
        if (responseAudio) {
            await this.playAudioInCall(callId, responseAudio);
        }

        // Salvar interação
        this.saveCallInteraction(callId, transcript, responseText, intent);
    }

    // Analisar intenção do usuário
    analyzeUserIntent(transcript) {
        const text = transcript.toLowerCase();
        
        if (text.includes('produto') || text.includes('netflix') || text.includes('spotify')) {
            return 'products';
        } else if (text.includes('recarga') || text.includes('saldo') || text.includes('pix')) {
            return 'recharge';
        } else if (text.includes('suporte') || text.includes('ajuda') || text.includes('problema')) {
            return 'support';
        } else if (text.includes('tchau') || text.includes('obrigad') || text.includes('desligar')) {
            return 'goodbye';
        } else {
            return 'unknown';
        }
    }

    // Lidar com ausência de input
    async handleNoInput(callId, callData) {
        console.log(`⏳ Sem input do usuário: ${callId}`);
        
        const promptAudio = await this.generateTTS(
            "Você ainda está aí? Como posso ajudá-lo? Diga 'produtos', 'recarga' ou 'suporte'."
        );
        
        if (promptAudio) {
            await this.playAudioInCall(callId, promptAudio);
        }
    }

    // Lidar com chamada completada
    async handleCallCompleted(callId, callData, duration) {
        console.log(`📞 Chamada finalizada: ${callId} - Duração: ${duration}s`);
        
        // Atualizar dados da chamada
        callData.status = 'completed';
        callData.endTime = new Date();
        callData.duration = duration;
        
        // Salvar log da chamada
        await this.saveCallLog(callId, callData);
        
        // Remover da lista ativa
        this.activeCallbacks.delete(callId);
        
        // Opcional: enviar follow-up via WhatsApp/Telegram
        await this.sendFollowUpMessage(callData);
    }

    // Lidar com falha na chamada
    async handleCallFailed(callId, callData) {
        console.log(`❌ Falha na chamada: ${callId}`);
        
        callData.status = 'failed';
        callData.endTime = new Date();
        
        await this.saveCallLog(callId, callData);
        this.activeCallbacks.delete(callId);
        
        // Opcional: reagendar chamada ou enviar mensagem
        await this.handleCallFailure(callData);
    }

    // Reproduzir áudio durante a chamada
    async playAudioInCall(callId, audioUrl) {
        try {
            if (!this.callAPIKey) {
                console.log(`🔊 Simulando reprodução de áudio: ${audioUrl}`);
                return { success: true };
            }

            const response = await axios.post(`${this.callAPI}/calls/${callId}/play`, {
                audio_url: audioUrl
            }, {
                headers: {
                    'Authorization': `Bearer ${this.callAPIKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return { success: true, data: response.data };

        } catch (error) {
            console.error('Erro ao reproduzir áudio:', error);
            return { success: false, error: error.message };
        }
    }

    // Encerrar chamada
    async endCall(callId) {
        try {
            if (!this.callAPIKey) {
                console.log(`📞 Simulando encerramento da chamada: ${callId}`);
                return { success: true };
            }

            const response = await axios.post(`${this.callAPI}/calls/${callId}/hangup`, {}, {
                headers: {
                    'Authorization': `Bearer ${this.callAPIKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return { success: true, data: response.data };

        } catch (error) {
            console.error('Erro ao encerrar chamada:', error);
            return { success: false, error: error.message };
        }
    }

    // Salvar interação da chamada
    saveCallInteraction(callId, userInput, botResponse, intent) {
        const interaction = {
            call_id: callId,
            timestamp: new Date(),
            user_input: userInput,
            bot_response: botResponse,
            intent: intent
        };

        // Salvar no banco ou arquivo de log
        console.log('💾 Interação salva:', interaction);
    }

    // Salvar log completo da chamada
    async saveCallLog(callId, callData) {
        const logData = {
            call_id: callId,
            phone: callData.phone,
            type: callData.type,
            status: callData.status,
            start_time: callData.startTime,
            end_time: callData.endTime,
            duration: callData.duration,
            answered_at: callData.answeredAt,
            user_data: callData.userData
        };

        // Salvar no banco de dados
        console.log('📋 Log da chamada salvo:', logData);
    }

    // Enviar mensagem de follow-up
    async sendFollowUpMessage(callData) {
        const message = `Obrigado por falar conosco! Se precisar de mais alguma coisa, estamos sempre disponíveis no WhatsApp e Telegram. 😊`;
        
        // Enviar via WhatsApp ou Telegram
        console.log(`📱 Follow-up enviado para ${callData.phone}: ${message}`);
    }

    // Lidar com falhas de chamada
    async handleCallFailure(callData) {
        console.log(`🔄 Tratando falha de chamada para ${callData.phone}`);
        
        // Opcional: reagendar para outro horário
        // Opcional: enviar mensagem explicando a falha
    }

    // Gerar ID único para chamada
    generateCallId() {
        return 'call_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Processar fila de chamadas
    async processCallQueue() {
        if (this.callQueue.length === 0) return;

        const nextCall = this.callQueue.shift();
        await this.initiateCall(nextCall.phone, nextCall.type, nextCall.userData);
    }

    // Adicionar chamada à fila
    queueCall(phoneNumber, callType = 'support', userData = {}) {
        this.callQueue.push({
            phone: phoneNumber,
            type: callType,
            userData: userData,
            queuedAt: new Date()
        });

        console.log(`📞 Chamada adicionada à fila: ${phoneNumber}`);
    }

    // Iniciar processamento automático da fila
    startQueueProcessor() {
        setInterval(async () => {
            if (this.callQueue.length > 0 && this.activeCallbacks.size < 5) {
                await this.processCallQueue();
            }
        }, 30000); // Processar a cada 30 segundos

        console.log('🔄 Processador de fila de chamadas iniciado');
    }

    // Obter estatísticas de chamadas
    getCallStats() {
        return {
            activeCallbacks: this.activeCallbacks.size,
            queueLength: this.callQueue.length,
            totalCalls: this.activeCallbacks.size + this.callQueue.length
        };
    }

    // Inicializar sistema
    start() {
        console.log('📞 Sistema de chamadas de voz iniciado');
        this.startQueueProcessor();
        
        // Criar diretório temp se não existir
        const tempDir = path.join(__dirname, 'temp');
        if (!fs.existsSync(tempDir)) {
            fs.mkdirSync(tempDir, { recursive: true });
        }
    }
}

module.exports = new VoiceCallSystem();