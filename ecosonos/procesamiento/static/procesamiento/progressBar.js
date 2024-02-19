function updateProgressBar(intervalIdProgressBar, waitTime) {
	let xhr = new XMLHttpRequest();

	xhr.open("POST", "/preproceso/barra_progreso", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const porcentaje_completado = data["procentaje_completado"];

			const spanValue = document.getElementById("value1");
			spanValue.innerHTML = porcentaje_completado + "%";
			const barElement = document.querySelector(".bar");
			barElement.style.setProperty("--percentage", spanValue.textContent);

			if (porcentaje_completado == 100) {
				clearInterval(intervalIdProgressBar);
				setTimeout(() => {
					spanValue.innerHTML = "Completado - Guardando datos en CSV";
					intervalIdCsvState = setInterval(() => getCsvState(intervalIdCsvState), waitTime);
				}, waitTime*2.5);
			}
		}
	};
	xhr.send();
}

function getCsvState(intervalIdCsvState, waitTime) {
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/preproceso/csv_cargado", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const csvCargado = data["csv_cargado"];

			if (csvCargado) {
				clearInterval(intervalIdCsvState);
				setTimeout(() => {
					enableButtons();
				}, waitTime*2.5);
			}
			
		}
	};
	xhr.send();
}

function enableButtons() {
	document.getElementById("div-mover-mostrar").style.display = "block";
}
