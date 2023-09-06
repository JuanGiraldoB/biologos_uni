function show_files() {
	let xhr = new XMLHttpRequest();
	let formData = new FormData();
	formData.append("informacion", "informacion");

	xhr.open("POST", "/etiquetado-auto/espectrograma", true); // Replace with your actual GET URL
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const fileDetails = data.files_details;
			const clusters = data.clusters;
			const size = Object.keys(fileDetails).length;

			let checkboxClusterDiv = document.getElementById("checkbox_clusters");
			setupDivCheckbox(checkboxClusterDiv, clusters);

			let radioClusterDiv = document.getElementById("radio_clusters");
			// setupDivRadio(radioClusterDiv, clusters);

			let ulElement = document.getElementById("lista_audios");
			for (let i = 0; i < size; i++) {
				const fileDetail = fileDetails[i];
				const filePath = fileDetail.path;
				const fileName = fileDetail.basename;

				let liElement = document.createElement("li");
				let aElement = createA(filePath, fileName);

				liElement.appendChild(aElement);
				ulElement.appendChild(liElement);
			}
		}
	};
	xhr.send(formData);
}

function createA(path, basename) {
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
		xhr.open("POST", "/etiquetado-auto/espectrograma", true);

		// Set up the request headers
		xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

		// Set up the onload and onerror event handlers
		xhr.onload = function () {
			if (xhr.status === 200) {
				let response = JSON.parse(xhr.responseText);
				let graficaDiv = document.getElementById("grafica_div");
				graficaDiv.innerHTML = "";
				let iframe = document.createElement("iframe");

				// Fetch the HTML content from the URL
				fetch(response.plot_url)
					.then((response) => response.text())
					.then((htmlContent) => {
						iframe.srcdoc = htmlContent;
						iframe.style.width = "100%";
						iframe.style.height = "100%";
						console.log("yey");
					})
					.catch((error) => {
						console.error("Error fetching HTML content:", error);
					});
				graficaDiv.appendChild(iframe);
			} else {
				console.error("Request failed:", xhr.statusText);
			}
		};

		// Send the request
		xhr.send(formData);
	});

	return aElement;
}

function setupDivCheckbox(clustersDiv, clusters) {
	let clusterHeader = createHeader("Seleccione Clusters");
	clustersDiv.appendChild(clusterHeader);

	for (let i = 0; i < clusters.length; i++) {
		const cluster = clusters[i];
		let checkbox = createCheckBox(cluster);
		let label = createLabel(cluster);
		let div = createCheckboxDiv();

		div.appendChild(checkbox);
		div.appendChild(label);

		clustersDiv.appendChild(div);
	}
}

function setupDivRadio(representativoDiv, clusters) {
	let clusterHeader = createHeader("Seleccione elemento representativo");
	representativoDiv.appendChild(clusterHeader);

	for (let i = 0; i < clusters.length; i++) {
		const cluster = clusters[i];
		let radio = createRadio(cluster);
		let label = createLabel(cluster);
		let div = createRadioDiv();

		div.append(radio);
		div.append(label);

		representativoDiv.appendChild(div);
	}
}

function createHeader(content) {
	let clusterHeader = document.createElement("h3");
	clusterHeader.textContent = content;

	return clusterHeader;
}

function createCheckBox(value) {
	let checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.name = value;
	checkbox.value = value;
	checkbox.id = value;
	checkbox.checked = true;

	return checkbox;
}

function createRadio(value) {
	let radio = document.createElement("input");
	radio.type = "radio";
	radio.name = "representativo";
	radio.value = value;

	return radio;
}

function createLabel(name) {
	let label = document.createElement("label");
	label.for = name;
	label.textContent = name;

	return label;
}

function createCheckboxDiv() {
	let divCarpetasCargadas = document.createElement("div");
	divCarpetasCargadas.className = "carpetas-clusters";

	return divCarpetasCargadas;
}

function createRadioDiv() {
	let divCarpetasCargadas = document.createElement("div");
	// divCarpetasCargadas.className = "carpetas-clusters";

	return divCarpetasCargadas;
}
