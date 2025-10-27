import qrcode
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
import config
from database import Database

class PixGenerator:
    def __init__(self):
        self.db = Database()
        self.pix_api_url = "https://api.pix.com.br/v1"  # API fictícia para exemplo
    
    def generate_pix(self, amount: float, user_id: int) -> Dict:
        """Gera um novo PIX para pagamento"""
        try:
            # Gera código PIX único
            pix_code = self._generate_pix_code()
            
            # Cria QR Code
            qr_code = self._generate_qr_code(pix_code)
            
            # Calcula expiração
            expiration = datetime.now() + timedelta(minutes=config.PIX_EXPIRATION_MINUTES)
            
            # Salva transação no banco
            transaction_id = self.db.create_transaction(
                user_id=user_id,
                type='recharge',
                amount=amount,
                description=f'Recarga PIX R$ {amount:.2f}'
            )
            
            # Atualiza transação com código PIX
            self._update_transaction_pix(transaction_id, pix_code, expiration)
            
            return {
                'success': True,
                'pix_code': pix_code,
                'qr_code': qr_code,
                'amount': amount,
                'expiration': expiration,
                'transaction_id': transaction_id,
                'expiration_formatted': expiration.strftime('%d/%m/%Y às %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_pix_code(self) -> str:
        """Gera código PIX único"""
        import random
        import string
        
        # Gera código PIX no formato padrão
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        
        return f"00020101021226830014BR.GOV.BCB.PIX2561qrcodespix.sejaefi.com.br/v2/{random_part}5204000053039865802BR5905EFISA6008SAOPAULO62070503***6304E477"
    
    def _generate_qr_code(self, pix_code: str) -> str:
        """Gera QR Code para o PIX"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(pix_code)
            qr.make(fit=True)
            
            # Salva QR Code como imagem
            img = qr.make_image(fill_color="black", back_color="white")
            filename = f"qr_codes/pix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # Cria diretório se não existir
            import os
            os.makedirs("qr_codes", exist_ok=True)
            
            img.save(filename)
            return filename
            
        except Exception as e:
            print(f"Erro ao gerar QR Code: {e}")
            return ""
    
    def _update_transaction_pix(self, transaction_id: int, pix_code: str, expiration: datetime):
        """Atualiza transação com código PIX e expiração"""
        conn = self.db.db_file
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE transactions 
            SET pix_code = ?, pix_expiration = ?
            WHERE id = ?
        ''', (pix_code, expiration, transaction_id))
        
        conn.commit()
        conn.close()
    
    def check_pix_payment(self, pix_code: str) -> Dict:
        """Verifica se o PIX foi pago"""
        try:
            # Aqui você implementaria a verificação real com a API do seu provedor PIX
            # Por enquanto, simulamos uma verificação
            
            # Busca transação pelo código PIX
            transaction = self._get_transaction_by_pix(pix_code)
            
            if not transaction:
                return {'success': False, 'error': 'Transação não encontrada'}
            
            # Verifica se expirou
            if datetime.now() > transaction['pix_expiration']:
                return {'success': False, 'error': 'PIX expirado'}
            
            # Simula verificação de pagamento (substitua pela API real)
            payment_status = self._check_payment_with_provider(pix_code)
            
            if payment_status['paid']:
                # Marca transação como paga
                self._mark_transaction_paid(transaction['id'])
                
                # Adiciona saldo ao usuário
                self.db.update_user_balance(
                    transaction['user_id'], 
                    transaction['amount'], 
                    'add'
                )
                
                return {
                    'success': True,
                    'paid': True,
                    'amount': transaction['amount'],
                    'user_id': transaction['user_id']
                }
            else:
                return {
                    'success': True,
                    'paid': False,
                    'amount': transaction['amount']
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_transaction_by_pix(self, pix_code: str) -> Optional[Dict]:
        """Busca transação pelo código PIX"""
        conn = self.db.db_file
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, u.telegram_id FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.pix_code = ?
        ''', (pix_code,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0], 'user_id': result[1], 'type': result[2],
                'amount': result[3], 'description': result[4], 'status': result[5],
                'pix_code': result[6], 'pix_expiration': result[7],
                'created_at': result[8], 'completed_at': result[9],
                'telegram_id': result[10]
            }
        return None
    
    def _check_payment_with_provider(self, pix_code: str) -> Dict:
        """Verifica pagamento com provedor PIX (implementar com API real)"""
        # Aqui você implementaria a verificação real
        # Por enquanto, simulamos baseado em um critério simples
        
        # Simula verificação baseada no timestamp do código
        import time
        timestamp = int(time.time())
        
        # Simula que PIXs com timestamp par são pagos (apenas para teste)
        return {'paid': timestamp % 2 == 0}
    
    def _mark_transaction_paid(self, transaction_id: int):
        """Marca transação como paga"""
        conn = self.db.db_file
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE transactions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (transaction_id,))
        
        conn.commit()
        conn.close()
    
    def get_expired_pix(self) -> list:
        """Retorna lista de PIXs expirados"""
        conn = self.db.db_file
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, u.telegram_id FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.status = 'pending' 
            AND t.pix_expiration < CURRENT_TIMESTAMP
            AND t.pix_code IS NOT NULL
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0], 'user_id': r[1], 'type': r[2],
                'amount': r[3], 'description': r[4], 'status': r[5],
                'pix_code': r[6], 'pix_expiration': r[7],
                'created_at': r[8], 'completed_at': r[9],
                'telegram_id': r[10]
            }
            for r in results
        ]
    
    def cleanup_expired_pix(self):
        """Limpa PIXs expirados"""
        expired_pix = self.get_expired_pix()
        
        for pix in expired_pix:
            # Marca como expirado
            conn = self.db.db_file
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE transactions 
                SET status = 'expired'
                WHERE id = ?
            ''', (pix['id'],))
            
            conn.commit()
            conn.close()
            
            # Remove arquivo de QR Code se existir
            try:
                import os
                qr_file = f"qr_codes/pix_{pix['created_at'].strftime('%Y%m%d_%H%M%S')}.png"
                if os.path.exists(qr_file):
                    os.remove(qr_file)
            except:
                pass