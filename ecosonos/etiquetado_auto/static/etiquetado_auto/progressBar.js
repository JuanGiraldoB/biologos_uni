let intervalId = null;

function updateProgressBar(type) {
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/etiquetado-auto/barra_progreso", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

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
				if (type == "temporal") {
					getPlots();
				} else {
					show_files(type);
				}
			}
		}
	};
	xhr.send();
}
