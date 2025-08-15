const axios = require('axios');
const crypto = require('crypto');
const moment = require('moment');
const db = require('./database');
require('dotenv').config();

class PIXIntegration {
    constructor() {
        this.provider = process.env.PIX_PROVIDER || 'EAFI';
        this.merchantId = process.env.PIX_MERCHANT_ID || 'EFISA';
        this.merchantCity = process.env.PIX_MERCHANT_CITY || 'SAOPAULO';
        this.apiKey = process.env.PIX_API_KEY;
        this.webhookSecret = process.env.PIX_WEBHOOK_SECRET;
        this.baseURL = process.env.PIX_API_URL || 'https://api.pix-provider.com';
    }

    // Gerar chave PIX dinâmica
    async generateDynamicPIX(amount, description, expirationMinutes = 30) {
        try {
            const transactionId = this.generateTransactionId();
            const expiresAt = moment().add(expirationMinutes, 'minutes');

            // Payload PIX segundo padrão BR Code
            const pixPayload = this.generateBRCode({
                merchantName: process.env.STORE_NAME || 'JOÃOZINHO STORE',
                merchantCity: this.merchantCity,
                txid: transactionId,
                amount: amount,
                description: description || 'Recarga de saldo'
            });

            // Para provedores reais, fazer chamada para API
            if (this.apiKey && this.baseURL) {
                const response = await this.callProviderAPI({
                    method: 'POST',
                    endpoint: '/pix/cob',
                    data: {
                        calendario: {
                            expiracao: expirationMinutes * 60 // em segundos
                        },
                        devedor: {
                            nome: 'Cliente'
                        },
                        valor: {
                            original: amount.toFixed(2)
                        },
                        chave: process.env.PIX_KEY, // Sua chave PIX
                        solicitacaoPagador: description,
                        txid: transactionId
                    }
                });

                if (response.success) {
                    return {
                        transaction_id: transactionId,
                        pix_key: response.data.pixCopiaECola || pixPayload,
                        qr_code: response.data.qrcode || this.generateQRCode(pixPayload),
                        amount: amount,
                        expires_at: expiresAt.toDate(),
                        provider_data: response.data
                    };
                }
            }

            // Fallback para simulação
            return {
                transaction_id: transactionId,
                pix_key: pixPayload,
                qr_code: this.generateQRCode(pixPayload),
                amount: amount,
                expires_at: expiresAt.toDate(),
                provider_data: null
            };

        } catch (error) {
            console.error('Erro ao gerar PIX:', error);
            throw new Error('Falha ao gerar PIX');
        }
    }

    // Gerar BR Code (padrão PIX)
    generateBRCode(data) {
        const payload = [
            '00020126', // Payload Format Indicator
            '830014BR.GOV.BCB.PIX', // Merchant Account Information
            `2561qrcodespix.sejaefi.com.br/v2/${data.txid}`, // Dynamic QR Code URL
            '5204000', // Merchant Category Code
            '5303986', // Transaction Currency (BRL)
            `54${String(data.amount.toFixed(2)).padStart(2, '0')}${data.amount.toFixed(2)}`, // Transaction Amount
            '5802BR', // Country Code
            `59${String(data.merchantName).padStart(2, '0')}${data.merchantName}`, // Merchant Name
            `60${String(data.merchantCity).padStart(2, '0')}${data.merchantCity}`, // Merchant City
            `62070503${data.txid.substring(0, 25)}`, // Additional Data Field
            '6304' // CRC16 placeholder
        ].join('');

        // Calcular CRC16
        const crc = this.calculateCRC16(payload);
        return payload + crc;
    }

    // Calcular CRC16 para BR Code
    calculateCRC16(payload) {
        const polynomial = 0x1021;
        let crc = 0xFFFF;

        for (let i = 0; i < payload.length; i++) {
            crc ^= (payload.charCodeAt(i) << 8);
            for (let j = 0; j < 8; j++) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ polynomial;
                } else {
                    crc <<= 1;
                }
                crc &= 0xFFFF;
            }
        }

        return crc.toString(16).toUpperCase().padStart(4, '0');
    }

    // Gerar QR Code (simulado - use biblioteca real em produção)
    generateQRCode(pixPayload) {
        // Em produção, use qrcode lib: qrcode.toDataURL(pixPayload)
        return `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
    }

    // Gerar ID único de transação
    generateTransactionId() {
        return Date.now().toString() + crypto.randomBytes(4).toString('hex').toUpperCase();
    }

    // Verificar status de pagamento
    async checkPaymentStatus(transactionId) {
        try {
            if (this.apiKey && this.baseURL) {
                const response = await this.callProviderAPI({
                    method: 'GET',
                    endpoint: `/pix/cob/${transactionId}`,
                    data: null
                });

                if (response.success) {
                    return {
                        status: response.data.status, // ATIVA, CONCLUIDA, REMOVIDA_PELO_USUARIO_RECEBEDOR, REMOVIDA_PELO_PSP
                        paid: response.data.status === 'CONCLUIDA',
                        amount: response.data.valor?.original ? parseFloat(response.data.valor.original) : null,
                        paid_at: response.data.pix?.[0]?.horario || null
                    };
                }
            }

            // Fallback: verificar no banco local
            return await this.checkLocalPaymentStatus(transactionId);

        } catch (error) {
            console.error('Erro ao verificar status PIX:', error);
            return { status: 'error', paid: false };
        }
    }

    // Verificar status local (fallback)
    async checkLocalPaymentStatus(transactionId) {
        return new Promise((resolve, reject) => {
            db.db.get(
                'SELECT * FROM pix_transactions WHERE transaction_id = ?',
                [transactionId],
                (err, row) => {
                    if (err) {
                        reject(err);
                    } else if (!row) {
                        resolve({ status: 'not_found', paid: false });
                    } else {
                        resolve({
                            status: row.status,
                            paid: row.status === 'paid',
                            amount: row.amount,
                            paid_at: row.paid_at
                        });
                    }
                }
            );
        });
    }

    // Processar webhook de confirmação
    async processWebhook(webhookData, signature) {
        try {
            // Verificar assinatura do webhook
            if (!this.verifyWebhookSignature(webhookData, signature)) {
                throw new Error('Assinatura inválida');
            }

            const { txid, status, valor, pix } = webhookData;

            // Processar diferentes tipos de evento
            switch (status) {
                case 'CONCLUIDA':
                    await this.confirmPayment(txid, {
                        amount: parseFloat(valor.original),
                        paid_at: pix[0]?.horario || new Date(),
                        payer: pix[0]?.pagador || null
                    });
                    break;

                case 'REMOVIDA_PELO_USUARIO_RECEBEDOR':
                case 'REMOVIDA_PELO_PSP':
                    await this.cancelPayment(txid);
                    break;

                default:
                    console.log('Status PIX não processado:', status);
            }

            return { success: true, processed: true };

        } catch (error) {
            console.error('Erro ao processar webhook PIX:', error);
            return { success: false, error: error.message };
        }
    }

    // Confirmar pagamento
    async confirmPayment(transactionId, paymentData) {
        try {
            // Atualizar status no banco
            await new Promise((resolve, reject) => {
                db.db.run(
                    `UPDATE pix_transactions 
                     SET status = 'paid', paid_at = ? 
                     WHERE transaction_id = ?`,
                    [paymentData.paid_at, transactionId],
                    function(err) {
                        if (err) reject(err);
                        else resolve(this.changes);
                    }
                );
            });

            // Buscar dados da transação
            const transaction = await new Promise((resolve, reject) => {
                db.db.get(
                    'SELECT * FROM pix_transactions WHERE transaction_id = ?',
                    [transactionId],
                    (err, row) => {
                        if (err) reject(err);
                        else resolve(row);
                    }
                );
            });

            if (transaction) {
                // Adicionar saldo ao usuário
                await db.updateUserBalance(transaction.user_id, transaction.amount, 'add');

                // Atualizar ranking
                const user = await new Promise((resolve, reject) => {
                    db.db.get(
                        'SELECT * FROM users WHERE id = ?',
                        [transaction.user_id],
                        (err, row) => {
                            if (err) reject(err);
                            else resolve(row);
                        }
                    );
                });

                if (user) {
                    await db.updateRanking('recharges', user.id, user.username, transaction.amount);
                }

                // Notificar usuário (implementar notificação)
                await this.notifyPaymentConfirmed(transaction, user);

                console.log(`✅ Pagamento confirmado: ${transactionId} - R$ ${transaction.amount}`);
            }

        } catch (error) {
            console.error('Erro ao confirmar pagamento:', error);
            throw error;
        }
    }

    // Cancelar pagamento
    async cancelPayment(transactionId) {
        try {
            await new Promise((resolve, reject) => {
                db.db.run(
                    `UPDATE pix_transactions 
                     SET status = 'cancelled' 
                     WHERE transaction_id = ?`,
                    [transactionId],
                    function(err) {
                        if (err) reject(err);
                        else resolve(this.changes);
                    }
                );
            });

            console.log(`❌ Pagamento cancelado: ${transactionId}`);

        } catch (error) {
            console.error('Erro ao cancelar pagamento:', error);
            throw error;
        }
    }

    // Verificar assinatura do webhook
    verifyWebhookSignature(data, signature) {
        if (!this.webhookSecret || !signature) {
            return true; // Temporário para desenvolvimento
        }

        const expectedSignature = crypto
            .createHmac('sha256', this.webhookSecret)
            .update(JSON.stringify(data))
            .digest('hex');

        return crypto.timingSafeEqual(
            Buffer.from(signature, 'hex'),
            Buffer.from(expectedSignature, 'hex')
        );
    }

    // Notificar usuário sobre pagamento confirmado
    async notifyPaymentConfirmed(transaction, user) {
        // Implementar notificação via bot
        console.log(`📢 Notificar usuário ${user.telegram_id}: Pagamento R$ ${transaction.amount} confirmado`);
    }

    // Chamar API do provedor PIX
    async callProviderAPI({ method, endpoint, data }) {
        try {
            const config = {
                method: method,
                url: `${this.baseURL}${endpoint}`,
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            };

            if (data) {
                config.data = data;
            }

            const response = await axios(config);
            return { success: true, data: response.data };

        } catch (error) {
            console.error('Erro na API do provedor PIX:', error.response?.data || error.message);
            return { success: false, error: error.response?.data || error.message };
        }
    }

    // Listar transações pendentes
    async getPendingTransactions() {
        return new Promise((resolve, reject) => {
            db.db.all(
                `SELECT * FROM pix_transactions 
                 WHERE status = 'pending' AND expires_at > datetime('now')`,
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows);
                }
            );
        });
    }

    // Verificar transações expiradas
    async checkExpiredTransactions() {
        try {
            const expiredTransactions = await new Promise((resolve, reject) => {
                db.db.all(
                    `SELECT * FROM pix_transactions 
                     WHERE status = 'pending' AND expires_at <= datetime('now')`,
                    (err, rows) => {
                        if (err) reject(err);
                        else resolve(rows);
                    }
                );
            });

            for (const transaction of expiredTransactions) {
                await new Promise((resolve, reject) => {
                    db.db.run(
                        `UPDATE pix_transactions 
                         SET status = 'expired' 
                         WHERE id = ?`,
                        [transaction.id],
                        function(err) {
                            if (err) reject(err);
                            else resolve(this.changes);
                        }
                    );
                });

                console.log(`⏰ Transação expirada: ${transaction.transaction_id}`);
            }

            return expiredTransactions.length;

        } catch (error) {
            console.error('Erro ao verificar transações expiradas:', error);
            return 0;
        }
    }

    // Iniciar monitoramento automático
    startMonitoring() {
        // Verificar transações expiradas a cada 5 minutos
        setInterval(async () => {
            await this.checkExpiredTransactions();
        }, 5 * 60 * 1000);

        // Verificar status de transações pendentes a cada 30 segundos
        setInterval(async () => {
            const pendingTransactions = await this.getPendingTransactions();
            for (const transaction of pendingTransactions) {
                const status = await this.checkPaymentStatus(transaction.transaction_id);
                if (status.paid) {
                    await this.confirmPayment(transaction.transaction_id, status);
                }
            }
        }, 30 * 1000);

        console.log('🔄 Monitoramento PIX iniciado');
    }

    // Relatório de transações
    async getTransactionReport(startDate, endDate) {
        return new Promise((resolve, reject) => {
            db.db.all(
                `SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as total_paid,
                    SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_count,
                    SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) as expired_count,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count
                 FROM pix_transactions 
                 WHERE created_at BETWEEN ? AND ?`,
                [startDate, endDate],
                (err, rows) => {
                    if (err) reject(err);
                    else resolve(rows[0]);
                }
            );
        });
    }
}

module.exports = new PIXIntegration();