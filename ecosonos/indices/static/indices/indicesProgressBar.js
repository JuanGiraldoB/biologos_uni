let intervalId = null;

document.addEventListener("DOMContentLoaded", function () {
	let button = document.getElementById("procesar_carpetas");

	if (button) {
		intervalId = setInterval(updateProgressBar, 500);
	}
});

function updateProgressBar() {
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/indices/barra_progreso", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const porcentaje_completado = data["procentaje_completado"];

			const spanValue = document.getElementById("value1");
			spanValue.innerHTML = porcentaje_completado + "%";
			const barElement = document.querySelector(".bar");
			barElement.style.setProperty("--percentage", spanValue.textContent);

			console.log(porcentaje_completado);

			if (porcentaje_completado == 100) {
				spanValue.innerHTML = "Completado";
				clearInterval(intervalId);
				enableButtons();
			}
		}
	};
	xhr.send();
}

function enableButtons() {
	document.getElementById("cargar").disabled = false;
	// document.getElementById("destino").disabled = false;
	document.getElementById("procesar_carpetas").disabled = false;
	document.getElementById("mostrar-grafica").disabled = false;
	document.getElementById("cargar-csv").disabled = false;
}
