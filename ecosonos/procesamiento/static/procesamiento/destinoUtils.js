// submitForm.js
document.addEventListener("DOMContentLoaded", function () {
	let form = document.getElementById("carpeta_destino");
	let submitButton = document.getElementById("destino");

	form.addEventListener("submit", function (event) {
		event.preventDefault();
		let formData = new FormData(form);

		formData.append("destino", submitButton.name);

		let xhr = new XMLHttpRequest();
		xhr.open("POST", "", true); // URL to your view
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);

					let seleccionarCarpetasForm = document.getElementById(
						"seleccionar_carpetas"
					);

					let csrfTokenInput = seleccionarCarpetasForm.querySelector(
						'input[name="csrfmiddlewaretoken"]'
					);

					seleccionarCarpetasForm.innerHTML = "";
					seleccionarCarpetasForm.append(csrfTokenInput);

					let statistics = response.statistics;
					let folders_details = response.folders_details;

					for (let i = 0; i < folders_details.length; i++) {
						const folderDetail = folders_details[i];

						// Create checkbox
						let checkbox = createCheckBox(folderDetail.folder_path);

						// Create checkbox's label
						let label = createCheckBoxLabel(folderDetail, statistics);

						// Create div
						let divCarpetasCargadas = createCheckboxDiv();
						divCarpetasCargadas.appendChild(checkbox);
						divCarpetasCargadas.appendChild(label);

						// Append to div to form
						seleccionarCarpetasForm.append(divCarpetasCargadas);
					}

					let submit = createSubmit();

					seleccionarCarpetasForm.addEventListener("submit", (event) => {
						event.preventDefault();
						intervalId = setInterval(updateProgressBar, 1000);

						let formData = new FormData(seleccionarCarpetasForm);
						formData.append("procesar_carpetas", submit.name);

						let xhr = new XMLHttpRequest();
						xhr.open("POST", "", true);
						xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
						xhr.setRequestHeader("X-CSRFToken", "{{ csrf_token }}");

						xhr.onreadystatechange = function () {
							if (xhr.readyState === XMLHttpRequest.DONE) {
								if (xhr.status === 200) {
									// Create header
									let processingHeader = createHeader();
									seleccionarCarpetasForm.insertBefore(
										processingHeader,
										submit
									);

									// Create ul element
									let ulElement = document.createElement("ul");

									// Iterate through checkboxes
									let checkboxes = seleccionarCarpetasForm.querySelectorAll(
										'input[type="checkbox"]'
									);
									checkboxes.forEach((checkbox) => {
										let label = checkbox.nextElementSibling; // Get associated label
										if (checkbox.checked) {
											let liElement = createLi(label); // Create a new li element
											ulElement.appendChild(liElement);
										}
										// Remove the checkbox and label
										checkbox.remove();
										label.remove();
									});

									// Insert the ul element before the submit button
									seleccionarCarpetasForm.insertBefore(ulElement, submit);
								} else {
									console.error("error: " + xhr.status);
								}
							}
						};
						xhr.send(formData);
					});

					seleccionarCarpetasForm.append(submit);
				} else {
					let response = JSON.parse(xhr.responseText);
					console.error(response.error + " " + xhr.status);
				}
			}
		};

		xhr.send(formData);
	});
});

function createCheckBox(value) {
	let checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.name = "carpetas";
	checkbox.value = value;
	checkbox.checked = true;

	return checkbox;
}

function createCheckBoxLabel(folderDetail, statistics) {
	let label = document.createElement("label");
	label.for = "carpetas";

	if (statistics) {
		label.textContent = `${folderDetail.folder_name} - Numero de Archivos: ${folderDetail.number_of_files} - Rango de duracion: ${folderDetail.range_of_lengths} - Rango de fechas: ${folderDetail.range_of_dates}`;
	} else {
		label.textContent = folderDetail.folder_name;
	}

	return label;
}

function createCheckboxDiv() {
	let divCarpetasCargadas = document.createElement("div");
	divCarpetasCargadas.className = "carpetas-cargadas";

	return divCarpetasCargadas;
}

function createSubmit() {
	let submit = document.createElement("input");
	submit.type = "submit";
	submit.value = "Procesar";
	submit.id = "procesar_carpetas";
	submit.name = "procesar_carpetas";

	return submit;
}

function createHeader() {
	let processingHeader = document.createElement("h4");
	processingHeader.textContent = "Procesando";

	return processingHeader;
}

function createLi(label) {
	let liElement = document.createElement("li");
	liElement.textContent = label.textContent;

	return liElement;
}
