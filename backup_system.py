#!/usr/bin/env python3
"""
Sistema de Backup Automático para o JOÃOZINHO STORE BOT
Realiza backups do banco de dados e arquivos importantes
"""

import os
import shutil
import sqlite3
import zipfile
import json
from datetime import datetime, timedelta
import logging
import config
from database import Database

logger = logging.getLogger(__name__)

class BackupSystem:
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        self.db = Database()
        
        # Cria diretório de backup se não existir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_database_backup(self):
        """Cria backup do banco de dados"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"database_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Conecta ao banco original
            original_db = sqlite3.connect(config.DATABASE_FILE)
            
            # Cria backup
            backup_db = sqlite3.connect(backup_path)
            original_db.backup(backup_db)
            
            # Fecha conexões
            original_db.close()
            backup_db.close()
            
            logger.info(f"Backup do banco criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup do banco: {e}")
            return None
    
    def create_files_backup(self):
        """Cria backup dos arquivos importantes"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"files_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Lista de arquivos para backup
            important_files = [
                'config.py',
                'main.py',
                'telegram_bot.py',
                'whatsapp_bot.py',
                'database.py',
                'pix_generator.py',
                'notification_system.py',
                'admin_panel.py',
                'requirements.txt',
                'README.md',
                '.env'
            ]
            
            # Cria arquivo ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in important_files:
                    if os.path.exists(file_path):
                        zipf.write(file_path, file_path)
                        logger.info(f"Arquivo adicionado ao backup: {file_path}")
            
            logger.info(f"Backup de arquivos criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup de arquivos: {e}")
            return None
    
    def create_full_backup(self):
        """Cria backup completo (banco + arquivos)"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir_name = f"full_backup_{timestamp}"
            backup_dir_path = os.path.join(self.backup_dir, backup_dir_name)
            
            # Cria diretório do backup
            os.makedirs(backup_dir_path)
            
            # Backup do banco
            db_backup = self.create_database_backup()
            if db_backup:
                # Move para diretório do backup completo
                db_backup_name = os.path.basename(db_backup)
                shutil.move(db_backup, os.path.join(backup_dir_path, db_backup_name))
            
            # Backup de arquivos
            files_backup = self.create_files_backup()
            if files_backup:
                # Move para diretório do backup completo
                files_backup_name = os.path.basename(files_backup)
                shutil.move(files_backup, os.path.join(backup_dir_path, files_backup_name))
            
            # Cria arquivo de metadados
            metadata = {
                'backup_type': 'full',
                'created_at': datetime.now().isoformat(),
                'bot_version': '1.0.0',
                'database_file': db_backup_name if db_backup else None,
                'files_backup': files_backup_name if files_backup else None,
                'total_size': self._get_directory_size(backup_dir_path)
            }
            
            metadata_path = os.path.join(backup_dir_path, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Cria arquivo ZIP do backup completo
            full_backup_zip = f"{backup_dir_name}.zip"
            full_backup_path = os.path.join(self.backup_dir, full_backup_zip)
            
            with zipfile.ZipFile(full_backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(backup_dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, backup_dir_path)
                        zipf.write(file_path, arcname)
            
            # Remove diretório temporário
            shutil.rmtree(backup_dir_path)
            
            logger.info(f"Backup completo criado: {full_backup_path}")
            return full_backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup completo: {e}")
            return None
    
    def restore_database_backup(self, backup_path):
        """Restaura backup do banco de dados"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_path}")
            
            # Cria backup do banco atual antes de restaurar
            current_backup = self.create_database_backup()
            
            # Restaura backup
            backup_db = sqlite3.connect(backup_path)
            current_db = sqlite3.connect(config.DATABASE_FILE)
            
            backup_db.backup(current_db)
            
            # Fecha conexões
            backup_db.close()
            current_db.close()
            
            logger.info(f"Banco restaurado de: {backup_path}")
            logger.info(f"Backup do banco anterior salvo em: {current_backup}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                
                if os.path.isfile(file_path):
                    file_stat = os.stat(file_path)
                    file_size = file_stat.st_size
                    created_time = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    backup_info = {
                        'filename': filename,
                        'path': file_path,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'created_at': created_time,
                        'created_at_str': created_time.strftime('%d/%m/%Y %H:%M:%S'),
                        'type': self._get_backup_type(filename)
                    }
                    
                    backups.append(backup_info)
            
            # Ordena por data de criação (mais recente primeiro)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days=30):
        """Remove backups antigos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            removed_count = 0
            
            backups = self.list_backups()
            
            for backup in backups:
                if backup['created_at'] < cutoff_date:
                    try:
                        os.remove(backup['path'])
                        logger.info(f"Backup antigo removido: {backup['filename']}")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Erro ao remover backup {backup['filename']}: {e}")
            
            logger.info(f"Limpeza concluída: {removed_count} backups removidos")
            return removed_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza de backups: {e}")
            return 0
    
    def get_backup_stats(self):
        """Retorna estatísticas dos backups"""
        try:
            backups = self.list_backups()
            
            if not backups:
                return {
                    'total_backups': 0,
                    'total_size_mb': 0,
                    'oldest_backup': None,
                    'newest_backup': None,
                    'backup_types': {}
                }
            
            total_size = sum(backup['size'] for backup in backups)
            oldest_backup = min(backup['created_at'] for backup in backups)
            newest_backup = max(backup['created_at'] for backup in backups)
            
            # Conta tipos de backup
            backup_types = {}
            for backup in backups:
                backup_type = backup['type']
                backup_types[backup_type] = backup_types.get(backup_type, 0) + 1
            
            return {
                'total_backups': len(backups),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'oldest_backup': oldest_backup,
                'newest_backup': newest_backup,
                'backup_types': backup_types
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas dos backups: {e}")
            return {}
    
    def _get_backup_type(self, filename):
        """Determina o tipo de backup baseado no nome do arquivo"""
        if filename.startswith('database_backup_'):
            return 'database'
        elif filename.startswith('files_backup_'):
            return 'files'
        elif filename.startswith('full_backup_'):
            return 'full'
        else:
            return 'unknown'
    
    def _get_directory_size(self, directory):
        """Calcula tamanho total de um diretório"""
        total_size = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        
        return total_size
    
    def schedule_backup(self, backup_type='full', interval_hours=24):
        """Agenda backup automático"""
        try:
            import schedule
            import time
            
            if backup_type == 'database':
                schedule.every(interval_hours).hours.do(self.create_database_backup)
            elif backup_type == 'files':
                schedule.every(interval_hours).hours.do(self.create_files_backup)
            else:
                schedule.every(interval_hours).hours.do(self.create_full_backup)
            
            logger.info(f"Backup automático agendado: {backup_type} a cada {interval_hours} horas")
            
            # Executa agendador
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Verifica a cada hora
                
        except ImportError:
            logger.error("Biblioteca 'schedule' não instalada. Execute: pip install schedule")
        except Exception as e:
            logger.error(f"Erro no agendador de backup: {e}")

def main():
    """Função principal para testes"""
    backup_system = BackupSystem()
    
    print("🤖 Sistema de Backup - JOÃOZINHO STORE BOT")
    print("=" * 50)
    
    # Cria backup completo
    print("📦 Criando backup completo...")
    backup_path = backup_system.create_full_backup()
    
    if backup_path:
        print(f"✅ Backup criado: {backup_path}")
    else:
        print("❌ Erro ao criar backup")
        return
    
    # Lista backups
    print("\n📋 Listando backups disponíveis...")
    backups = backup_system.list_backups()
    
    for backup in backups:
        print(f"📁 {backup['filename']}")
        print(f"   Tipo: {backup['type']}")
        print(f"   Tamanho: {backup['size_mb']} MB")
        print(f"   Criado: {backup['created_at_str']}")
        print()
    
    # Estatísticas
    print("📊 Estatísticas dos backups...")
    stats = backup_system.get_backup_stats()
    
    print(f"Total de backups: {stats['total_backups']}")
    print(f"Tamanho total: {stats['total_size_mb']} MB")
    print(f"Tipos: {stats['backup_types']}")
    
    # Limpeza
    print("\n🧹 Limpando backups antigos (mais de 30 dias)...")
    removed_count = backup_system.cleanup_old_backups(30)
    print(f"Backups removidos: {removed_count}")

if __name__ == "__main__":
    main()