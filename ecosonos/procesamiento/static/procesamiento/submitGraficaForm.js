document.addEventListener("DOMContentLoaded", function () {
	let form = document.getElementById("grafica_form");
	let submitButton = document.getElementById("mostrar_grafica");

	form.addEventListener("submit", function (event) {
		event.preventDefault();
		let formData = new FormData(form);

		formData.append("mostrar_grafica", submitButton.name);

		let xhr = new XMLHttpRequest();
		xhr.open("POST", "", true);
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);
					let graficaDiv = document.getElementById("grafica_div");
					// Plotly.newPlot(graficaDiv, parsedFig);
					graficaDiv.innerHTML = response.plot;
					console.log(response.plot);
				} else {
					let response = JSON.parse(xhr.responseText);
					console.error(response.error + " " + xhr.status);
				}
			}
		};

		xhr.send(formData);
	});
});
