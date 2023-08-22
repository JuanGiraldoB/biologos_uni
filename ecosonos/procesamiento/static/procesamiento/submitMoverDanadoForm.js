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
		xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);
				} else {
					let response = JSON.parse(xhr.responseText);
					console.error(response.error + " " + xhr.status);
				}
			}
		};

		xhr.send(formData);
	});
});
