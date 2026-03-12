from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectMultipleField, IntegerField
from wtforms import validators, widgets
from wtforms.validators import DataRequired

class PizzaForm(FlaskForm):
    id=IntegerField('id')
    nombre = StringField("Nombre completo", [
        validators.DataRequired(message="El campo es requerido"),
        validators.Length(min=3, max=170, message="Ingrese el valor valido")
    ])

    direccion = StringField("Direccion", [
        validators.DataRequired(message="El campo es requerido"),
        validators.Length(min=3, max=170, message="Ingrese el valor valido")
    ])

    telefono = StringField("Telefono", [
        validators.DataRequired(message="El campo es requerido"),
        validators.Length(min=1, max=13, message="Ingrese el valor valido"),
        validators.Regexp('^[0-9]+$', message="Solo se permiten numeros")
    ])

    tamano = RadioField(
        "Tamaño de la pizza",
        choices=[
            ('40', 'Chica'),
            ('80', 'Mediana'),
            ('120', 'Grande')
        ],
        default='Chica'
    )

    ingredientes = SelectMultipleField(
        "Ingredientes",
        choices=[
            ('10_jamon', 'Jamon'),
            ('10_pina', 'Piña'),
            ('10_champi', 'Champiñones')
        ],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
    )

    cantidad = IntegerField("Número de pizzas", [
    validators.NumberRange(min=1, message="Ingrese un valor válido")
    ])
