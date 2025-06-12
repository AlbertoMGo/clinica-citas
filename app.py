from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/citas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de citas
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    sucursal = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    medico = db.Column(db.String(100), nullable=False)
    fecha_hora = db.Column(db.String(100), nullable=False)

# Diccionario de médicos por sucursal y tipo
medicos = {
    "Centro": {
        "Psicológica": ["Dra. Ana López", "Dr. Luis Torres"],
        "Médica": ["Dra. Claudia Pérez", "Dr. Juan Méndez"],
        "Odontológica": ["Dra. Elena Flores", "Dr. Marcos Herrera"]
    },
    "Norte": {
        "Psicológica": ["Dra. Laura Sánchez", "Dr. Pablo Ortega"],
        "Médica": ["Dra. Daniela Ruiz", "Dr. Miguel Chávez"],
        "Odontológica": ["Dra. Teresa Vega", "Dr. Andrés Campos"]
    },
    "Sur": {
        "Psicológica": ["Dra. Silvia Gómez", "Dr. Ernesto Ríos"],
        "Médica": ["Dra. Beatriz Soto", "Dr. Alfredo León"],
        "Odontológica": ["Dra. Lorena Ibáñez", "Dr. Tomás Fernández"]
    }
}

@app.route('/')
def formulario():
    return render_template(
        'formulario.html',
        sucursales=medicos.keys(),
        tipos=["Psicológica", "Médica", "Odontológica"],
        medicos=medicos
    )

@app.route('/submit', methods=['POST'])
def submit():
    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form['telefono']
    sucursal = request.form['sucursal']
    tipo = request.form['tipo']
    medico = request.form['medico']
    fecha_hora_str = request.form['fecha_hora']

    # Validación: formato de fecha
    try:
        fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash("Formato de fecha y hora inválido.", "error")
        return redirect(url_for('formulario'))

    # Validación: mínimo 1 hora de anticipación
    if fecha_hora < datetime.now() + timedelta(hours=1):
        flash("Las citas deben agendarse con al menos una hora de anticipación.", "error")
        return redirect(url_for('formulario'))

    # Validación: cita duplicada
    if Cita.query.filter_by(medico=medico, fecha_hora=fecha_hora_str).first():
        flash("Ya existe una cita con este médico en ese horario.", "error")
        return redirect(url_for('formulario'))

    nueva_cita = Cita(
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        sucursal=sucursal,
        tipo=tipo,
        medico=medico,
        fecha_hora=fecha_hora_str
    )
    db.session.add(nueva_cita)
    db.session.commit()
    flash("Cita agendada correctamente.", "success")
    return redirect(url_for('formulario'))

@app.route('/agenda')
def agenda():
    citas = Cita.query.all()
    eventos = [
        {
            "title": f"{cita.nombre} ({cita.tipo})",
            "start": cita.fecha_hora,
            "extendedProps": {
                "sucursal": cita.sucursal,
                "tipo": cita.tipo
            }
        }
        for cita in citas
    ]
    return render_template('agenda.html', eventos=eventos)

@app.route('/horarios_ocupados')
def horarios_ocupados():
    medico = request.args.get('medico')
    citas = Cita.query.filter_by(medico=medico).all()
    horarios = [cita.fecha_hora for cita in citas]
    return jsonify(horarios)

if __name__ == '__main__':
    os.makedirs('instance', exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
