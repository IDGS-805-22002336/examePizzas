from flask import render_template, request, redirect, url_for, session
from . import pizza
from models import db, Cliente, Pizza, Pedido, DetallePedido
import forms
from datetime import datetime


@pizza.route('/listaPizza', methods=['GET', 'POST'])
def lista_pizza():

    form = forms.PizzaForm()
    pedidos = []
    mensaje = ""

    if 'pedidos_temp' not in session:
        session['pedidos_temp'] = []
    pedidos_temp = session.get('pedidos_temp', [])

    nombres_ingredientes = {
        '10_jamon': 'Jamon',
        '10_pina': 'Piña',
        '10_champi': 'Champiñones'
    }

    tamano_texto = {
        '40': 'Chica',
        '80': 'Mediana',
        '120': 'Grande'
    }

    if request.method == "POST":

        if 'agregar' in request.form and form.validate_on_submit():

            seleccionados = request.form.getlist('ingredientes')
            costo_ingredientes = len(seleccionados) * 10

            ingredientes_texto = []
            for i in seleccionados:
                ingredientes_texto.append(nombres_ingredientes[i])

            precio_base = int(form.tamano.data)
            tamano_nombre = tamano_texto[form.tamano.data]

            cantidad = int(form.cantidad.data)

            subtotal = (precio_base + costo_ingredientes) * cantidad

            pedido_temp = {
                "nombre": form.nombre.data,
                "direccion": form.direccion.data,
                "telefono": form.telefono.data,
                "tamano": tamano_nombre,
                "ingredientes": ", ".join(ingredientes_texto),
                "cantidad": cantidad,
                "total": subtotal
            }

            pedidos_temp = session.get('pedidos_temp', [])
            pedidos_temp.append(pedido_temp)

            session['pedidos_temp'] = pedidos_temp

            return redirect(url_for('pizza.lista_pizza'))
        
        if 'quitar' in request.form:
            indice = request.form.get("pedido_id")

            if indice:
                indice = int(indice)
                pedidos_temp = session.get('pedidos_temp', [])

                nueva_lista = []  

                i = 0
                while i < len(pedidos_temp):
                    if i != indice:  
                        nueva_lista.append(pedidos_temp[i])
                    i += 1

                session['pedidos_temp'] = nueva_lista

            return redirect(url_for('pizza.lista_pizza'))
        
        if 'terminar' in request.form:

            pedidos_temp = session.get('pedidos_temp', [])
            total_pagar = 0

            for p in pedidos_temp:

                cliente = Cliente(
                    nombre=p["nombre"],
                    direccion=p["direccion"],
                    telefono=p["telefono"]
                )

                db.session.add(cliente)
                db.session.commit()

                pizza = Pizza(
                    tamano=p["tamano"],
                    ingredientes=p["ingredientes"],
                    precio=p["total"]
                )

                db.session.add(pizza)
                db.session.commit()

                pedido = Pedido(
                    id_cliente=cliente.id_cliente,
                    fecha=datetime.now().date(),
                    total=p["total"]
                )

                db.session.add(pedido)
                db.session.commit()

                detalle = DetallePedido(
                    id_pedido=pedido.id_pedido,
                    id_pizza=pizza.id_pizza,
                    cantidad=p["cantidad"],
                    subtotal=p["total"]
                )

                db.session.add(detalle)
                db.session.commit()

                total_pagar += p["total"]

            session['pedidos_temp'] = []

            mensaje = "Pedido realizado. Total a pagar: $" + str(total_pagar)

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
    pedidos_temp=pedidos_temp,
    ventas_fecha=ventas_fecha,
    total_fecha=total_fecha,
    mensaje=mensaje
)