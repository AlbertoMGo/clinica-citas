from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///citas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de datos
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sucursal = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    medico = db.Column(db.String(100), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)

# Crear la base de datos
with app.app_context():
    db.create_all()

# Datos para el formulario
sucursales = ['Centro', 'Norte', 'Sur']
tipos = ['Psicológica', 'Médica', 'Odontológica']
medicos_por_tipo_sucursal = {
    'Centro': {
        'Psicológica': ['Dra. Ana López', 'Dr. Mario Gómez'],
        'Médica': ['Dr. Juan Pérez', 'Dra. Carmen Díaz'],
        'Odontológica': ['Dra. Julia Ramos', 'Dr. Pedro Solano']
    },
    'Norte': {
        'Psicológica': ['Dra. Laura Méndez', 'Dr. Tomás Herrera'],
        'Médica': ['Dr. Luis Estrada', 'Dra. Teresa Morales'],
        'Odontológica': ['Dra. Miriam Guzmán', 'Dr. Hugo Varela']
    },
    'Sur': {
        'Psicológica': ['Dra. Paula Reyes', 'Dr. Iván Serrano'],
        'Médica': ['Dr. Enrique Silva', 'Dra. Mónica Lozano'],
        'Odontológica': ['Dra. Beatriz Cuevas', 'Dr. Samuel Ortega']
    }
}

@app.route('/')
def index():
    return render_template('formulario.html', sucursales=sucursales, tipos=tipos)

@app.route('/get_medicos')
def get_medicos():
    sucursal = request.args.get('sucursal')
    tipo = request.args.get('tipo')
    medicos = medicos_por_tipo_sucursal.get(sucursal, {}).get(tipo, [])
    return jsonify(medicos)

@app.route('/get_ocupados')
def get_ocupados():
    sucursal = request.args.get('sucursal')
    medico = request.args.get('medico')
    fecha = request.args.get('fecha')

    if not (sucursal and medico and fecha):
        return jsonify([])

    # Convertir la fecha a datetime sin hora
    try:
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    except ValueError:
        return jsonify([])

    citas = Cita.query.filter_by(sucursal=sucursal, medico=medico).all()
    ocupados = [
        cita.fecha_hora.strftime('%H:%M')
        for cita in citas
        if cita.fecha_hora.date() == fecha_dt
    ]
    return jsonify(ocupados)

@app.route('/agendar', methods=['POST'])
def agendar():
    nombre = request.form['nombre']
    sucursal = request.form['sucursal']
    tipo = request.form['tipo']
    medico = request.form['medico']
    fecha = request.form['fecha']
    hora = request.form['hora']
    fecha_hora = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')

    # Validar si ya existe una cita para ese médico en ese momento
    cita_existente = Cita.query.filter_by(
        medico=medico,
        sucursal=sucursal,
        fecha_hora=fecha_hora
    ).first()

    if cita_existente:
        flash('Ya existe una cita para ese médico en esa fecha y hora. Por favor elige otro horario.', 'error')
        return redirect(url_for('index'))

    nueva_cita = Cita(
        nombre=nombre,
        sucursal=sucursal,
        tipo=tipo,
        medico=medico,
        fecha_hora=fecha_hora
    )
    db.session.add(nueva_cita)
    db.session.commit()

    flash('Cita agendada exitosamente.', 'success')
    return redirect(url_for('index'))

@app.route('/agenda')
def agenda():
    citas = Cita.query.all()
    eventos = [
        {
            'title': f"{cita.tipo} - {cita.medico}",
            'start': cita.fecha_hora.isoformat()
        }
        for cita in citas
    ]
    return render_template('agenda.html', eventos=eventos, sucursales=sucursales)

if __name__ == '__main__':
    app.run(debug=True)
