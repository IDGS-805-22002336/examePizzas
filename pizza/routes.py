from flask import render_template, request, redirect, url_for
from . import pizza
from models import db, Cliente, Pizza, Pedido, DetallePedido
import forms
from datetime import datetime


@pizza.route('/listaPizza', methods=['GET', 'POST'])
def lista_pizza():

    form = forms.PizzaForm()
    pedidos = []
    mensaje= ""

    nombres_ingredientes = {
        '10_jamon': 'Jamón',
        '10_pina': 'Piña',
        '10_champi': 'Champiñones'
    }

    tamano_texto = {
        '40': 'Chica',
        '80': 'Mediana',
        '120': 'Grande'
    }


    if 'agregar' in request.form and form.validate_on_submit():

        fecha_actual = datetime.now().date()

        seleccionados = request.form.getlist('ingredientes')
        costo_ingredientes = len(seleccionados) * 10
        ingredientes_texto = [nombres_ingredientes[i] for i in seleccionados]

        precio_base = int(form.tamano.data)
        tamano_nombre = tamano_texto[form.tamano.data]

        cantidad = int(form.cantidad.data)

        subtotal = (precio_base + costo_ingredientes) * cantidad

        nuevo_cliente = Cliente(
            nombre=form.nombre.data,
            direccion=form.direccion.data,
            telefono=form.telefono.data
        )

        db.session.add(nuevo_cliente)
        db.session.commit()

        nueva_pizza = Pizza(
            tamano=tamano_nombre,
            ingredientes=", ".join(ingredientes_texto),
            precio=precio_base
        )

        db.session.add(nueva_pizza)
        db.session.commit()

        nuevo_pedido = Pedido(
            id_cliente=nuevo_cliente.id_cliente,
            fecha=fecha_actual,
            total=subtotal
        )

        db.session.add(nuevo_pedido)
        db.session.commit()

        detalle = DetallePedido(
            id_pedido=nuevo_pedido.id_pedido,
            id_pizza=nueva_pizza.id_pizza,
            cantidad=cantidad,
            subtotal=subtotal
        )

        db.session.add(detalle)
        db.session.commit()

        return redirect(url_for('pizza.lista_pizza'))


    if 'quitar' in request.form:

        pedido_id = request.form.get('pedido_id')

        if pedido_id:

            detalle = DetallePedido.query.filter_by(id_pedido=pedido_id).first()

            if detalle:
                db.session.delete(detalle)

            pedido = Pedido.query.get(pedido_id)

            if pedido:
                db.session.delete(pedido)

            db.session.commit()

        return redirect(url_for('pizza.lista_pizza'))
    
    if 'terminar' in request.form:

        total_pagar = 0

        lista_pedidos = Pedido.query.all()

        for p in lista_pedidos:
            total_pagar += p.total

        mensaje = "El total a pagar es: $" + str(total_pagar)

    lista_pedidos = Pedido.query.all()

    for p in lista_pedidos:

        cliente = Cliente.query.get(p.id_cliente)
        detalle = DetallePedido.query.filter_by(id_pedido=p.id_pedido).first()

        if detalle:

            pizza_obj = Pizza.query.get(detalle.id_pizza)

            pedidos.append({
                "id": p.id_pedido,
                "nombre": cliente.nombre,
                "direccion": cliente.direccion,
                "tamano": pizza_obj.tamano,
                "ingredientes": pizza_obj.ingredientes,
                "cantidad": detalle.cantidad,
                "total": p.total
            })
    
    ventas_fecha = []
    total_fecha = 0

    fecha_seleccionada = request.args.get("fecha")

    if fecha_seleccionada:

        pedidos_fecha = Pedido.query.filter_by(fecha=fecha_seleccionada).all()

        for p in pedidos_fecha:

            cliente = Cliente.query.get(p.id_cliente)

            ventas_fecha.append({
                "nombre": cliente.nombre,
                "total": p.total
            })
            
            total_fecha += p.total
        
        
        
    return render_template(
    'pizza/listaPizza.html',
    form=form,
    pedidos=pedidos,
    ventas_fecha=ventas_fecha,
    total_fecha=total_fecha,
    mensaje=mensaje
)