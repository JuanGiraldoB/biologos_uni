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
					let iframe = document.createElement("iframe");

					// Fetch the HTML content from the URL
					fetch(response.fig_url)
						.then((response) => response.text())
						.then((htmlContent) => {
							iframe.srcdoc = htmlContent;
							iframe.style.width = "100%";
							iframe.style.height = "400px";
						})
						.catch((error) => {
							console.error("Error fetching HTML content:", error);
						});

					graficaDiv.appendChild(iframe);
				} else {
					let response = JSON.parse(xhr.responseText);
					console.error(response.error + " " + xhr.status);
				}
			}
		};

		xhr.send(formData);
	});
});
