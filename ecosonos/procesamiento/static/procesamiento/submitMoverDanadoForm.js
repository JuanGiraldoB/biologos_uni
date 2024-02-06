document.addEventListener("DOMContentLoaded", function () {
	let form = document.getElementById("mover_danado_form");
	let submitButton = document.getElementById("mover_malos");

	form.addEventListener("submit", function (event) {
		event.preventDefault();
		let formData = new FormData(form);

		formData.append("mover_archivos", submitButton.value);

		let xhr = new XMLHttpRequest();
		xhr.open("POST", "", true);
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);
					let folder = response.folder;

					let pDanado = document.getElementById("p-danado");
					pDanado.style.display = "block";
					pDanado.textContent += folder;
				} else {
					let response = JSON.parse(xhr.responseText);
					console.error(response.error + " " + xhr.status);
				}
			}
		};

		xhr.send(formData);
	});
});
