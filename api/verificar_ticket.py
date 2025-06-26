@main.route('/api/verificar_ticket', methods=['POST'])
def api_verificar_ticket():
    data = request.get_json()
    qr_data = data.get('ticket_id')

    ticket = Ticket.query.filter_by(ticket_code=qr_data).first()

    if not ticket:
        return jsonify({'status': 'error', 'message': '❌ Ticket no encontrado'})

    # Datos del ticket
    ticket_details = {
        'ticket_code': ticket.ticket_code,
        'buyer_name': ticket.name,
        'event_name': ticket.event.name if ticket.event else 'Desconocido',
        'usado': ticket.usado,
        'payment_method': ticket.payment_method or 'No especificado'
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

