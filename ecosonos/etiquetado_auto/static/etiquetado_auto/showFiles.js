function show_files(type) {
	let xhr = new XMLHttpRequest();
	let formData = new FormData();
	formData.append("informacion", "informacion");

	xhr.open("POST", "/etiquetado-auto/plots", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const fileDetails = data.files_details;
			const clusters = data.clusters;
			const size = Object.keys(fileDetails).length;

			let checkboxClusterDiv;
			let radioClusterForm;
			let ulElement;

			if (type === "sonotipo") {
				checkboxClusterDiv = document.getElementById(
					"checkbox_clusters_sonotipo"
				);
				radioClusterForm = document.getElementById("radio_clusters_sonotipo");
				ulElement = document.getElementById("lista_audios_sonotipo");
			} else {
				checkboxClusterDiv = document.getElementById(
					"checkbox_clusters_reconocer"
				);
				radioClusterForm = document.getElementById("radio_clusters_reconocer");
				ulElement = document.getElementById("lista_audios_reconocer");
			}

			setupDivCheckbox(checkboxClusterDiv, clusters);
			setupFormRadio(radioClusterForm, clusters, type);

			for (let i = 0; i < size; i++) {
				const fileDetail = fileDetails[i];
				const filePath = fileDetail.path;
				const fileName = fileDetail.basename;

				let liElement = document.createElement("li");
				let aElement = createA(filePath, fileName, type);

				liElement.appendChild(aElement);
				ulElement.appendChild(liElement);
			}
		}
	};
	xhr.send(formData);
}

function createA(path, basename, type) {
	let aElement = document.createElement("a");
	aElement.href = "#"; // Set a placeholder link
	aElement.textContent = basename;

	aElement.addEventListener("click", function (event) {
		event.preventDefault(); // Prevent the default link behavior

		// Create a FormData object and append the data
		let formData = new FormData();
		formData.append("path", path);

		//Get the checked checkboxes
		let checkedCheckboxes = document.querySelectorAll(
			"input[type='checkbox']:checked"
		);
		checkedCheckboxes.forEach((checkbox) => {
			formData.append("selected_clusters", checkbox.value);
		});

		// Create a new XMLHttpRequest object
		let xhr = new XMLHttpRequest();
		xhr.open("POST", "/etiquetado-auto/plots", true);

		// Set up the request headers
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

		// Set up the onload and onerror event handlers
		xhr.onload = function () {
			if (xhr.status === 200) {
				let response = JSON.parse(xhr.responseText);

				let clusterDiv;
				if (type === "sonotipo") {
					clusterDiv = document.getElementById("cluster_sonotipo_div");
				} else {
					clusterDiv = document.getElementById("cluster_reconocer_div");
				}

				clusterDiv.innerHTML = "";
				let iframe = document.createElement("iframe");

				// Fetch the HTML content from the URL
				fetch(response.plot_url)
					.then((response) => response.text())
					.then((htmlContent) => {
						iframe.srcdoc = htmlContent;
						iframe.style.width = "100%";
						iframe.style.height = "100%";
					})
					.catch((error) => {
						console.error("Error fetching HTML content:", error);
					});
				clusterDiv.appendChild(iframe);
			} else {
				console.error("Request failed:", xhr.statusText);
			}
		};

		xhr.send(formData);
	});

	return aElement;
}

function setupDivCheckbox(clustersDiv, clusters) {
	let clusterHeader = createHeaderFiles("Seleccione Clusters");
	clustersDiv.appendChild(clusterHeader);

	for (let i = 0; i < clusters.length; i++) {
		const cluster = clusters[i];
		let checkbox = createCheckBoxSowFiles(cluster);
		let label = createLabelFiles(cluster, false);
		let div = createCheckboxSowFilesDiv();

		div.appendChild(checkbox);
		div.appendChild(label);

		clustersDiv.appendChild(div);
	}
}

function setupFormRadio(representativoDiv, clusters, type) {
	let clusterHeader = createHeaderFiles("Seleccione elemento representativo");
	representativoDiv.appendChild(clusterHeader);

	for (let i = 0; i < clusters.length; i++) {
		const cluster = clusters[i];
		let label = createLabelFiles(cluster, true);
		let radio = createRadio(cluster, type);
		let iTag = createI();

		label.appendChild(radio);
		label.appendChild(iTag);

		representativoDiv.appendChild(label);
	}
}

function createHeaderFiles(content) {
	let clusterHeader = document.createElement("h3");
	clusterHeader.textContent = content;

	return clusterHeader;
}

function createCheckBoxSowFiles(value) {
	let checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.name = value;
	checkbox.value = value;
	checkbox.id = value;
	checkbox.checked = true;

	return checkbox;
}

function createRadio(value, type) {
	let radio = document.createElement("input");
	radio.type = "radio";
	radio.name = "representativo";
	radio.value = value;
	radio.onclick = () => {
		submitForm(value, type);
	};

	return radio;
}

function createLabelFiles(name, isRadio) {
	let label = document.createElement("label");
	label.for = name;
	label.textContent = name;

	if (isRadio) {
		label.className = "content-input";
	}

	return label;
}

function createI() {
	return document.createElement("i");
}

function createCheckboxSowFilesDiv() {
	let divCarpetasCargadas = document.createElement("div");
	divCarpetasCargadas.className = "carpetas-clusters";

	return divCarpetasCargadas;
}

function createRadioDiv() {
	let divCarpetasCargadas = document.createElement("div");

	return divCarpetasCargadas;
}

function submitForm(selectedValue, type) {
	let form;
	let representativoDiv;

	if (type === "sonotipo") {
		form = document.getElementById("radio_clusters_sonotipo");
		representativoDiv = document.getElementById("representativo_sonotipo_div");
	} else {
		form = document.getElementById("radio_clusters_reconocer");
		representativoDiv = document.getElementById("representativo_reconocer_div");
	}

	let formData = new FormData(form);

	// Add the selected radio value to the form data
	formData.append("representativo", selectedValue);

	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/etiquetado-auto/plots", true);
	xhr.onreadystatechange = function () {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				let response = JSON.parse(xhr.responseText);
				representativoDiv.innerHTML = "";
				let iframe = document.createElement("iframe");

				// Fetch the HTML content from the URL
				fetch(response.plot_url)
					.then((response) => response.text())
					.then((htmlContent) => {
						iframe.srcdoc = htmlContent;
						iframe.style.width = "100%";
						iframe.style.height = "100%";
					})
					.catch((error) => {
						console.error("Error fetching HTML content:", error);
					});
				representativoDiv.appendChild(iframe);
			} else {
				console.error("XHR request failed.");
			}
		}
	};
	xhr.send(formData);
}
