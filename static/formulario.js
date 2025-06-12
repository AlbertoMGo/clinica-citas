document.addEventListener("DOMContentLoaded", function () {
    const sucursalSelect = document.getElementById("sucursal");
    const tipoSelect = document.getElementById("tipo");
    const medicoSelect = document.getElementById("medico");
    const fechaHoraSelect = document.getElementById("fecha_hora");
    const form = document.getElementById("formulario");
    const enviarBtn = document.getElementById("enviar");

    // Cargar sucursales y tipos
    const sucursales = [...new Set(medicos.map(m => m.sucursal))];
    sucursales.forEach(s => {
        const option = new Option(s, s);
        sucursalSelect.appendChild(option);
    });

    const tipos = [...new Set(medicos.map(m => m.tipo))];
    tipos.forEach(t => {
        const option = new Option(t, t);
        tipoSelect.appendChild(option);
    });

    function cargarMedicos() {
        medicoSelect.innerHTML = "";
        const filtro = medicos.filter(m =>
            m.sucursal === sucursalSelect.value && m.tipo === tipoSelect.value
        );
        filtro.forEach(m => {
            const option = new Option(m.nombre, m.nombre);
            medicoSelect.appendChild(option);
        });
        cargarHorarios();
    }

    async function cargarHorarios() {
        fechaHoraSelect.innerHTML = "";
        const hoy = new Date();
        const dia = hoy.toISOString().split("T")[0];

        for (let hora = 7; hora < 20; hora++) {
            for (let min of [0, 30]) {
                const fecha = new Date();
                fecha.setHours(hora, min, 0, 0);

                if (fecha < new Date(Date.now() + 60 * 60 * 1000)) continue;

                const fechaISO = fecha.toISOString().slice(0, 16);
                const fechaTexto = fecha.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                });

                const disponible = await fetch(`/verificar_horario?medico=${medicoSelect.value}&fecha_hora=${fechaISO}`)
                    .then(res => res.json());

                if (disponible.disponible) {
                    const option = new Option(`${dia} ${fechaTexto}`, fechaISO);
                    fechaHoraSelect.appendChild(option);
                }
            }
        }
    }

    sucursalSelect.addEventListener("change", cargarMedicos);
    tipoSelect.addEventListener("change", cargarMedicos);
    medicoSelect.addEventListener("change", cargarHorarios);

    // Activar botón solo si todos los campos están llenos
    form.addEventListener("input", function () {
        const inputs = form.querySelectorAll("input, select");
        const todosLlenos = Array.from(inputs).every(i => i.value.trim() !== "");
        enviarBtn.disabled = !todosLlenos;
    });
});
