function updateProgressBar(type, intervalIdProgressBar, waitTime) {
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/etiquetado-auto/barra_progreso", true);
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
				clearInterval(intervalIdProgressBar);
				setTimeout(() => {
					spanValue.innerHTML = "Completado";
					if (type == "temporal") {
						getPlots();
					} else {
						intervalIdCsvState = setInterval(() => getCsvState(type, intervalIdCsvState), waitTime);
					}
				}, waitTime*2.5);
			}
			
		}
	};
	xhr.send();
}

function getCsvState(type, intervalIdCsvState, waitTime) {
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/etiquetado-auto/csv_cargado", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const csvCargado = data["csv_cargado"];

			console.log(csvCargado);

			if (csvCargado) {
				clearInterval(intervalIdCsvState);
				setTimeout(() => {
					show_files(type);
				}, waitTime*2.5); // Wait for 1000 milliseconds (1 second)
			}
			
		}
	};
	xhr.send();
}
