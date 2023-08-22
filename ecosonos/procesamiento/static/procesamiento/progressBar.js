let intervalId = null;

function updateProgressBar() {
	let xhr = new XMLHttpRequest();

	xhr.open("POST", "/preproceso/barra_progreso", true);
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

			if (porcentaje_completado == 100) {
				console.log("completado");
				clearInterval(intervalId);
			}
		}
	};
	xhr.send();
}
