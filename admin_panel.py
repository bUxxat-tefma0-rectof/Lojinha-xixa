#!/usr/bin/env python3
"""
Painel de Administração Web para o JOÃOZINHO STORE BOT
Interface web para gerenciar produtos, usuários e configurações
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import json
from datetime import datetime
import config
from database import Database
from pix_generator import PixGenerator

# Configuração do Flask
app = Flask(__name__)
app.secret_key = 'joaozinho_store_bot_secret_key_2024'

# Configuração do Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicializa componentes
db = Database()
pix_generator = PixGenerator()

class AdminUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    if int(user_id) == config.ADMIN_ID:
        return AdminUser(user_id)
    return None

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        telegram_id = request.form.get('telegram_id')
        
        if int(telegram_id) == config.ADMIN_ID:
            user = AdminUser(telegram_id)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('ID de administrador inválido!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rotas principais
@app.route('/')
@login_required
def dashboard():
    """Dashboard principal"""
    try:
        # Estatísticas básicas
        stats = {
            'total_users': len(db.get_all_users()),
            'total_products': len(db.get_products()),
            'total_transactions': len(db.get_all_transactions()),
            'total_purchases': len(db.get_all_purchases()),
            'total_revenue': db.get_total_revenue()
        }
        
        # Produtos com estoque baixo
        low_stock_products = [p for p in db.get_products() if p['stock'] <= 5]
        
        # Transações pendentes
        pending_transactions = db.get_pending_transactions()
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             low_stock_products=low_stock_products,
                             pending_transactions=pending_transactions)
    
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {e}', 'error')
        return render_template('dashboard.html', stats={}, low_stock_products=[], pending_transactions=[])

@app.route('/products')
@login_required
def products():
    """Gerenciamento de produtos"""
    try:
        products_list = db.get_products()
        return render_template('products.html', products=products_list)
    except Exception as e:
        flash(f'Erro ao carregar produtos: {e}', 'error')
        return render_template('products.html', products=[])

@app.route('/users')
@login_required
def users():
    """Gerenciamento de usuários"""
    try:
        users_list = db.get_all_users()
        return render_template('users.html', users=users_list)
    except Exception as e:
        flash(f'Erro ao carregar usuários: {e}', 'error')
        return render_template('users.html', users=[])

@app.route('/transactions')
@login_required
def transactions():
    """Histórico de transações"""
    try:
        transactions_list = db.get_all_transactions()
        return render_template('transactions.html', transactions=transactions_list)
    except Exception as e:
        flash(f'Erro ao carregar transações: {e}', 'error')
        return render_template('transactions.html', transactions=[])

@app.route('/purchases')
@login_required
def purchases():
    """Histórico de compras"""
    try:
        purchases_list = db.get_all_purchases()
        return render_template('purchases.html', purchases=purchases_list)
    except Exception as e:
        flash(f'Erro ao carregar compras: {e}', 'error')
        return render_template('purchases.html', purchases=[])

@app.route('/settings')
@login_required
def settings():
    """Configurações do bot"""
    try:
        bot_config = db.get_bot_config()
        return render_template('settings.html', config=bot_config)
    except Exception as e:
        flash(f'Erro ao carregar configurações: {e}', 'error')
        return render_template('settings.html', config={})

# APIs para operações CRUD
@app.route('/api/products', methods=['POST'])
@login_required
def add_product():
    """Adiciona novo produto"""
    try:
        data = request.get_json()
        
        # Valida dados
        required_fields = ['name', 'price', 'description', 'stock', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Campo obrigatório: {field}'}), 400
        
        # Cria produto
        product_id = db.add_product(
            name=data['name'],
            price=float(data['price']),
            description=data['description'],
            stock=int(data['stock']),
            category=data['category']
        )
        
        return jsonify({'success': True, 'product_id': product_id})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    """Atualiza produto existente"""
    try:
        data = request.get_json()
        
        # Atualiza produto
        success = db.update_product(
            product_id=product_id,
            name=data.get('name'),
            price=float(data.get('price', 0)),
            description=data.get('description'),
            stock=int(data.get('stock', 0)),
            category=data.get('category'),
            is_active=data.get('is_active', True)
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Produto não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """Remove produto"""
    try:
        success = db.delete_product(product_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Produto não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>/balance', methods=['PUT'])
@login_required
def update_user_balance(user_id):
    """Atualiza saldo do usuário"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        operation = data.get('operation', 'set')
        
        db.update_user_balance(user_id, amount, operation)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings', methods=['PUT'])
@login_required
def update_settings():
    """Atualiza configurações do bot"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            db.update_bot_config(key, str(value))
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transactions/<int:transaction_id>/status', methods=['PUT'])
@login_required
def update_transaction_status(transaction_id):
    """Atualiza status da transação"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['pending', 'completed', 'expired', 'cancelled']:
            return jsonify({'success': False, 'error': 'Status inválido'}), 400
        
        success = db.update_transaction_status(transaction_id, status)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Transação não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Rotas de relatórios
@app.route('/reports')
@login_required
def reports():
    """Página de relatórios"""
    try:
        # Dados para relatórios
        monthly_sales = db.get_monthly_sales()
        top_products = db.get_top_products()
        user_rankings = db.get_user_rankings()
        
        return render_template('reports.html', 
                             monthly_sales=monthly_sales,
                             top_products=top_products,
                             user_rankings=user_rankings)
    
    except Exception as e:
        flash(f'Erro ao carregar relatórios: {e}', 'error')
        return render_template('reports.html', 
                             monthly_sales=[], 
                             top_products=[], 
                             user_rankings=[])

@app.route('/api/reports/sales')
@login_required
def api_sales_report():
    """API para relatório de vendas"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        sales_data = db.get_sales_report(start_date, end_date)
        
        return jsonify({'success': True, 'data': sales_data})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/users')
@login_required
def api_users_report():
    """API para relatório de usuários"""
    try:
        users_data = db.get_users_report()
        
        return jsonify({'success': True, 'data': users_data})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Rotas de sistema
@app.route('/system/backup')
@login_required
def system_backup():
    """Cria backup do banco de dados"""
    try:
        backup_file = db.create_backup()
        
        flash(f'Backup criado com sucesso: {backup_file}', 'success')
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f'Erro ao criar backup: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/system/restart')
@login_required
def system_restart():
    """Reinicia o bot"""
    try:
        # Aqui você implementaria a lógica de reinicialização
        flash('Comando de reinicialização enviado!', 'success')
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f'Erro ao reiniciar: {e}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/system/logs')
@login_required
def system_logs():
    """Visualiza logs do sistema"""
    try:
        log_file = 'bot.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()[-100:]  # Últimas 100 linhas
        else:
            logs = ['Arquivo de log não encontrado']
        
        return render_template('logs.html', logs=logs)
    
    except Exception as e:
        flash(f'Erro ao carregar logs: {e}', 'error')
        return render_template('logs.html', logs=[])

# Tratamento de erros
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Cria diretório de templates se não existir
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Cria templates básicos se não existirem
    create_basic_templates()
    
    print("🚀 Painel de Administração iniciado!")
    print(f"🌐 Acesse: http://localhost:5001")
    print(f"🔑 Login com ID: {config.ADMIN_ID}")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

def create_basic_templates():
    """Cria templates HTML básicos se não existirem"""
    templates_dir = 'templates'
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Template base
    base_template = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}JOÃOZINHO STORE BOT - Admin{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-robot"></i> JOÃOZINHO STORE BOT
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="{{ url_for('logout') }}">
                    <i class="fas fa-sign-out-alt"></i> Sair
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
    
    # Template de login
    login_template = '''{% extends "base.html" %}

{% block title %}Login - Admin{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="card-header text-center">
                <h4><i class="fas fa-robot"></i> Admin Login</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="telegram_id" class="form-label">ID do Telegram</label>
                        <input type="number" class="form-control" id="telegram_id" name="telegram_id" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-sign-in-alt"></i> Entrar
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Template do dashboard
    dashboard_template = '''{% extends "base.html" %}

{% block title %}Dashboard{% endblock %}

{% block content %}
<h2><i class="fas fa-tachometer-alt"></i> Dashboard</h2>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <h5 class="card-title">Usuários</h5>
                <h2>{{ stats.total_users or 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <h5 class="card-title">Produtos</h5>
                <h2>{{ stats.total_products or 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <h5 class="card-title">Transações</h5>
                <h2>{{ stats.total_transactions or 0 }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-warning text-white">
            <div class="card-body">
                <h5 class="card-title">Receita</h5>
                <h2>R$ {{ "%.2f"|format(stats.total_revenue or 0) }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-exclamation-triangle"></i> Estoque Baixo</h5>
            </div>
            <div class="card-body">
                {% if low_stock_products %}
                    <ul class="list-group list-group-flush">
                    {% for product in low_stock_products %}
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            {{ product.name }}
                            <span class="badge bg-danger rounded-pill">{{ product.stock }}</span>
                        </li>
                    {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted">Nenhum produto com estoque baixo.</p>
                {% endif %}
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5><i class="fas fa-clock"></i> Transações Pendentes</h5>
            </div>
            <div class="card-body">
                {% if pending_transactions %}
                    <ul class="list-group list-group-flush">
                    {% for transaction in pending_transactions %}
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            R$ {{ "%.2f"|format(transaction.amount) }}
                            <small class="text-muted">{{ transaction.created_at }}</small>
                        </li>
                    {% endfor %}
                    </ul>
                {% else %}
                    <p class="text-muted">Nenhuma transação pendente.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Cria os arquivos de template
    templates = {
        'base.html': base_template,
        'login.html': login_template,
        'dashboard.html': dashboard_template
    }
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Template criado: {filename}")