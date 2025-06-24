from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from .models import db, Event, Ticket, User
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
import qrcode
from io import BytesIO
import base64
from uuid import uuid4
from . import login_manager

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Sesión iniciada correctamente', 'success')
            return redirect(url_for('main.admin'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('main.index'))

@main.route('/admin')
@login_required
def admin():
    events = Event.query.all()
    tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    return render_template('admin.html', events=events, tickets=tickets)

@main.route('/admin/add_event', methods=['POST'])
@login_required
def add_event():
    name = request.form['name']
    if name:
        event = Event(name=name)
        db.session.add(event)
        db.session.commit()
        flash('Evento agregado correctamente!', 'success')
    else:
        flash('El nombre del evento es obligatorio', 'error')
    return redirect(url_for('main.admin'))

@main.route('/purchase', methods=['POST'])
def purchase_ticket():
    name = request.form['name']
    event_id = request.form['event']
    quantity = request.form['quantity']

    if not name or not event_id or not quantity:
        flash('Todos los campos son obligatorios', 'error')
        return redirect(url_for('main.index'))

    # Corregir la redirección para pasar los datos como query parameters al GET
    # de checkout_simulado si este maneja GET.
    # Como tu checkout_simulado ya maneja GET y toma args, esto funciona.
    return redirect(url_for('main.checkout_simulado', name=name, event_id=event_id, quantity=quantity))

@main.route('/checkout_simulado', methods=['GET', 'POST'])
def checkout_simulado():
    # Si se llega por POST (desde un formulario de checkout, no desde /purchase)
    if request.method == 'POST':
        name = request.form.get('name')
        event_id = request.form.get('event')
        quantity = request.form.get('quantity')
    # Si se llega por GET (desde la redirección de /purchase)
    else: # request.method == 'GET'
        name = request.args.get('name')
        event_id = request.args.get('event_id')
        quantity = request.args.get('quantity')

    if not name or not event_id or not quantity:
        flash('Datos incompletos para el checkout.', 'error')
        return redirect(url_for('main.index'))

    # Aquí el render_template es correcto para mostrar el formulario de pago
    return render_template('checkout.html', name=name, event_id=event_id, quantity=quantity)


@main.route('/pago_confirmado', methods=['POST'])
def pago_confirmado():
    name = request.form['name']
    event_id = request.form['event_id']
    quantity = request.form['quantity']
    payment_method = request.form['payment_method']

    # Convertir quantity a entero
    try:
        quantity = int(quantity)
    except ValueError:
        flash('Cantidad inválida.', 'error')
        return redirect(url_for('main.index'))

    # --- INICIO DE CAMBIOS PARA EL PATRÓN PRG ---

    # 1. Generar un ID único para esta transacción/compra
    transaction_id = str(uuid4())

    tickets_created = [] # Para almacenar los tickets creados en esta transacción
    for _ in range(quantity):
        ticket_code = str(uuid4()) # Cada ticket sigue teniendo su propio UUID
        qr = qrcode.QRCode()
        qr.add_data(ticket_code)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        ticket = Ticket(
            name=name,
            event_id=event_id,
            quantity=1, # Siempre 1 ticket por este objeto de ticket
            qr_code=qr_code_base64,
            ticket_code=ticket_code,
            transaction_id=transaction_id # Asignar el ID de transacción a cada ticket
        )
        db.session.add(ticket)
        tickets_created.append(ticket) # Añadir a la lista para referencia

    db.session.commit()
    flash(f'Pago realizado correctamente con método: {payment_method}', 'success')

    # 2. REDIRECCIONAR a una nueva URL de GET para mostrar los tickets
    # Pasar el transaction_id para que la nueva ruta pueda recuperar los tickets
    return redirect(url_for('main.confirmacion_compra', transaction_id=transaction_id))

# --- NUEVA RUTA PARA MOSTRAR LA CONFIRMACIÓN Y LOS TICKETS (MÉTODO GET) ---
@main.route('/confirmacion_compra/<string:transaction_id>', methods=['GET'])
def confirmacion_compra(transaction_id):
    # Recuperar los tickets usando el transaction_id
    tickets = Ticket.query.filter_by(transaction_id=transaction_id).all()

    if not tickets:
        flash('No se encontraron tickets para esta transacción.', 'error')
        return redirect(url_for('main.index'))

    # Renderizar la plantilla con los tickets recuperados
    return render_template('ticket_multiple.html', tickets=tickets)

# --- FIN DE CAMBIOS PARA EL PATRÓN PRG ---

@main.route('/ticket/<ticket_code>')
def ticket(ticket_code):
    ticket = Ticket.query.filter_by(ticket_code=ticket_code).first_or_404()
    return render_template('ticket.html', ticket=ticket)

@main.route('/api/verificar_ticket', methods=['POST'])
def api_verificar_ticket():
    data = request.get_json()
    qr_data = data.get('ticket_id')
    ticket = Ticket.query.filter_by(ticket_code=qr_data).first()
    if not ticket:
        return jsonify({'status': 'error', 'message': '❌ Ticket no encontrado'})
    if ticket.usado:
        return jsonify({'status': 'error', 'message': '⚠️ Ticket ya fue usado'})
    ticket.usado = True
    db.session.commit()
    return jsonify({'status': 'ok', 'message': f'✅ Ticket válido. Bienvenido {ticket.name}!'})

@main.route('/verificar')
def verificar_qr():
    return render_template('verificar.html')
