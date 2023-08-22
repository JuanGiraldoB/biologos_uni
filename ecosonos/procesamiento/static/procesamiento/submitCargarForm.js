document.addEventListener("DOMContentLoaded", function () {
	let form = document.getElementById("cargar_carpeta");
	let estadisticasCheckbox = document.getElementById("estadisticas");
	let submitButton = document.getElementById("cargar");

	form.addEventListener("submit", function (event) {
		event.preventDefault();
		let formData = new FormData(form);

		formData.append("estadisticas", estadisticasCheckbox.checked);
		formData.append("cargar", submitButton.name);

		let xhr = new XMLHttpRequest();
		xhr.open("POST", "", true);
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);
					console.log(response);
				} else {
					let response = JSON.parse(xhr.responseText);
					console.error(response.error + " " + xhr.status);
				}
			}
		};

		xhr.send(formData);
	});
});
