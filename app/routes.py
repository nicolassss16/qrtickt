from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Event, Ticket
from uuid import uuid4
import qrcode
import base64
from io import BytesIO

main = Blueprint('main', __name__)

# Home o index
@main.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

# Ruta para el checkout - formulario de pago
@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        event_id = request.form['event_id']
        quantity = request.form['quantity']

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            flash('Cantidad inválida.', 'error')
            return redirect(url_for('main.index'))

        event = Event.query.get(event_id)
        if not event:
            flash('Evento no encontrado.', 'error')
            return redirect(url_for('main.index'))

        return render_template('checkout.html', name=name, event=event, quantity=quantity)
    else:
        return redirect(url_for('main.index'))

# Ruta para confirmar el pago y generar tickets
@main.route('/pago_confirmado', methods=['POST'])
def pago_confirmado():
    name = request.form['name']
    event_id = request.form['event_id']
    quantity = request.form['quantity']
    payment_method = request.form['payment_method']

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        flash('Cantidad inválida.', 'error')
        return redirect(url_for('main.index'))

    event = Event.query.get(event_id)
    if not event:
        flash('Evento no encontrado.', 'error')
        return redirect(url_for('main.index'))

    transaction_id = str(uuid4())

    tickets_created = []
    for _ in range(quantity):
        ticket_code = str(uuid4())
        qr = qrcode.QRCode()
        qr.add_data(ticket_code)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        ticket = Ticket(
            name=name,
            event_id=event.id,
            quantity=1,
            qr_code=qr_code_base64,
            ticket_code=ticket_code,
            transaction_id=transaction_id,
            payment_method=payment_method
        )
        db.session.add(ticket)
        tickets_created.append(ticket)

    db.session.commit()
    flash(f'Pago realizado correctamente con método: {payment_method}', 'success')

    return redirect(url_for('main.confirmacion_compra', transaction_id=transaction_id))

# Confirmación de compra, muestra los tickets de la transacción
@main.route('/confirmacion_compra/<string:transaction_id>')
def confirmacion_compra(transaction_id):
    tickets = Ticket.query.filter_by(transaction_id=transaction_id).all()
    if not tickets:
        flash('No se encontraron tickets para esta transacción.', 'error')
        return redirect(url_for('main.index'))
    return render_template('ticket_multiple.html', tickets=tickets)

# Vista individual de ticket
@main.route('/ticket/<ticket_code>')
def ticket(ticket_code):
    ticket = Ticket.query.filter_by(ticket_code=ticket_code).first_or_404()
    return render_template('ticket.html', ticket=ticket)

# API para verificar ticket vía QR
@main.route('/api/verificar_ticket', methods=['POST'])
def api_verificar_ticket():
    data = request.get_json()
    qr_data = data.get('ticket_id')
    ticket = Ticket.query.filter_by(ticket_code=qr_data).first()

    if not ticket:
        return jsonify({'status': 'error', 'message': '❌ Ticket no encontrado'})

    ticket_details = {
        'ticket_code': ticket.ticket_code,
        'buyer_name': ticket.name,
        'event_name': ticket.event.name,
        'usado': ticket.usado
    }

    if ticket.usado:
        return jsonify({
            'status': 'warning',
            'message': '⚠️ Ticket ya fue usado',
            'ticket_info': ticket_details
        })

    ticket.usado = True
    db.session.commit()

    return jsonify({
        'status': 'ok',
        'message': f'✅ Ticket válido. Bienvenido {ticket.name}!',
        'ticket_info': ticket_details
    })

# Página para escanear QR
@main.route('/verificar')
def verificar_qr():
    return render_template('verificar.html')

# -----------------------
# Rutas de administración
# -----------------------

@main.route('/admin/')
@main.route('/admin/page/<int:page>')
@login_required
def admin(page=1):
    events = Event.query.all()
    tickets_paginated = Ticket.query.order_by(Ticket.id.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin.html', events=events, tickets_paginated=tickets_paginated)

@main.route('/admin/add_event', methods=['POST'])
@login_required
def add_event():
    name = request.form.get('name')
    if not name or name.strip() == '':
        flash('El nombre del evento no puede estar vacío.', 'error')
    else:
        event = Event(name=name.strip())
        db.session.add(event)
        db.session.commit()
        flash(f'Evento "{event.name}" agregado correctamente.', 'success')
    return redirect(url_for('main.admin'))

@main.route('/admin/event/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Elimina tickets asociados por cascada (si configurado)
    Ticket.query.filter_by(event_id=event.id).delete()
    db.session.delete(event)
    db.session.commit()
    flash(f'Evento "{event.name}" y todos sus tickets han sido eliminados.', 'success')
    return redirect(url_for('main.admin'))

@main.route('/admin/ticket/delete/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash(f'Ticket para {ticket.name} eliminado.', 'success')
    return redirect(url_for('main.admin'))

@main.route('/admin/ticket/toggle_status/<int:ticket_id>', methods=['POST'])
@login_required
def toggle_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.usado = not ticket.usado
    db.session.commit()
    status = "marcado como Usado" if ticket.usado else "marcado como No Usado"
    flash(f'Ticket de {ticket.name} {status}.', 'success')
    return redirect(url_for('main.admin'))
