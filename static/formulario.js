document.addEventListener('DOMContentLoaded', function () {
    const sucursalSelect = document.getElementById('sucursal');
    const tipoSelect = document.getElementById('tipo');
    const medicoSelect = document.getElementById('medico');
    const fechaHoraInput = document.getElementById('fecha_hora');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('formularioCita');

    const medicos = {
        Centro: {
            Psicológica: ['Dra. Ana Morales', 'Dr. Luis Sánchez'],
            Médica: ['Dra. Teresa Gómez', 'Dr. Juan Pérez'],
            Odontológica: ['Dra. Clara Torres', 'Dr. Emilio Díaz']
        },
        Norte: {
            Psicológica: ['Dra. Carolina Ruiz', 'Dr. Marco Hernández'],
            Médica: ['Dra. Gabriela Márquez', 'Dr. Rafael Estrada'],
            Odontológica: ['Dra. Andrea León', 'Dr. Tomás Fuentes']
        },
        Sur: {
            Psicológica: ['Dra. Isabel Rivas', 'Dr. Pablo Quintana'],
            Médica: ['Dra. Fernanda Soto', 'Dr. Miguel Ortega'],
            Odontológica: ['Dra. Patricia Flores', 'Dr. Andrés Velasco']
        }
    };

    function actualizarMedicos() {
        const sucursal = sucursalSelect.value;
        const tipo = tipoSelect.value;
        medicoSelect.innerHTML = '<option value="" disabled selected>Selecciona un profesional</option>';

        if (sucursal && tipo && medicos[sucursal] && medicos[sucursal][tipo]) {
            medicos[sucursal][tipo].forEach(function (medico) {
                const option = document.createElement('option');
                option.value = medico;
                option.textContent = medico;
                medicoSelect.appendChild(option);
            });
        }
    }

    sucursalSelect.addEventListener('change', actualizarMedicos);
    tipoSelect.addEventListener('change', actualizarMedicos);

    function validarFormulario() {
        const nombre = document.getElementById('nombre').value.trim();
        const correo = document.getElementById('correo').value.trim();
        const telefono = document.getElementById('telefono').value.trim();
        const sucursal = sucursalSelect.value;
        const tipo = tipoSelect.value;
        const medico = medicoSelect.value;
        const fechaHora = fechaHoraInput.value;

        const ahora = new Date();
        const fechaSeleccionada = new Date(fechaHora);

        const diferenciaMinutos = (fechaSeleccionada - ahora) / (1000 * 60);

        if (
            nombre && correo && telefono && sucursal &&
            tipo && medico && fechaHora &&
            diferenciaMinutos >= 60
        ) {
            submitBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
        }
    }

    document.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('input', validarFormulario);
        el.addEventListener('change', validarFormulario);
    });

    // Validación en envío para prevenir duplicados
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        const response = await fetch('/verificar_cita', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.existe) {
            alert('Ya existe una cita con esos datos. Por favor elige otro horario.');
        } else {
            form.submit();
        }
    });
});
