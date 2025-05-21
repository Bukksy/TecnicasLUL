let pagina = 1;

const contenedorCartas = document.getElementById('contenedor-cartas');
const btnVerMas = document.getElementById('btn-ver-mas');
const spinner = document.getElementById('loading-spinner');
const filtroTipo = document.getElementById('filtro-tipo');
const buscador = document.getElementById('buscador-cartas');
const cartasCargadas = document.getElementById('cartas-cargadas');
const paginaActual = document.getElementById('pagina-actual');

function cargarCartasFiltradas() {
    const tipo = filtroTipo.value;
    const nombre = buscador.value;

    pagina = 1; 
    btnVerMas.style.display = 'inline-block';
    btnVerMas.disabled = true;
    btnVerMas.innerText = 'Cargando...';
    spinner.style.display = 'inline-block';

    fetch(`cartas-onepiece/cargar-mas/?page=1&tipo=${encodeURIComponent(tipo)}&nombre=${encodeURIComponent(nombre)}`)
        .then(response => response.json())
        .then(data => {
            contenedorCartas.innerHTML = data.cartas_html;
            cartasCargadas.textContent = document.querySelectorAll('#contenedor-cartas .carta-item').length;
            paginaActual.textContent = '1';

            if (data.has_next) {
                btnVerMas.style.display = 'inline-block';
                btnVerMas.disabled = false;
                btnVerMas.innerText = 'Ver más';
                pagina = 2;
            } else {
                btnVerMas.style.display = 'none';
            }
        })
        .catch(() => {
            alert('Error cargando cartas. Intenta de nuevo.');
            btnVerMas.disabled = false;
            btnVerMas.innerText = 'Ver más';
        })
        .finally(() => {
            spinner.style.display = 'none';
        });
}

btnVerMas.addEventListener('click', () => {
    btnVerMas.disabled = true;
    btnVerMas.innerText = 'Cargando...';
    spinner.style.display = 'inline-block';

    const tipo = filtroTipo.value;
    const nombre = buscador.value;

    fetch(`cartas-onepiece/cargar-mas/?page=${pagina}&tipo=${encodeURIComponent(tipo)}&nombre=${encodeURIComponent(nombre)}`)
        .then(response => response.json())
        .then(data => {
            contenedorCartas.insertAdjacentHTML('beforeend', data.cartas_html);
            cartasCargadas.textContent = document.querySelectorAll('#contenedor-cartas .carta-item').length;
            paginaActual.textContent = pagina;

            if (data.has_next) {
                pagina += 1;
                btnVerMas.disabled = false;
                btnVerMas.innerText = 'Ver más';
            } else {
                btnVerMas.style.display = 'none';
            }
        })
        .catch(() => {
            alert('Error cargando más cartas.');
            btnVerMas.disabled = false;
            btnVerMas.innerText = 'Ver más';
        })
        .finally(() => {
            spinner.style.display = 'none';
        });
});

filtroTipo.addEventListener('change', cargarCartasFiltradas);
buscador.addEventListener('input', () => {
    // Pequeño debounce para no hacer fetch a cada tecla en tiempo real
    clearTimeout(buscarTimeout);
    buscarTimeout = setTimeout(cargarCartasFiltradas, 400);
});

let buscarTimeout;
