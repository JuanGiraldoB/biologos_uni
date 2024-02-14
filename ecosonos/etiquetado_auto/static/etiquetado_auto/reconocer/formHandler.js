let intervalId;

// CSV
let formCSV = document.getElementById("form_cargar_csv");
formCSV.addEventListener("submit", handleSubmiSelectCSV);

function selectCSV() {
    let submitButton = document.getElementById("cargar_csv");

    let formData = new FormData(formCSV);
    formData.append("cargar_csv", submitButton.name);

    fetch("", {
        method: "POST",
        body: formData,
    })
    .then(async response => {
        if (response.ok) {
            return response.json();
        } else {
            const data = await response.json();
			return await Promise.reject(data);
        }
    })
    .then(jsonResponse => {
        let species = jsonResponse.cluster_names;
		hideDiv("div-seleccionar-csv");
		displayDiv("div-seleccionar-carpeta-principal");
        generateSpeciesName(species);
    })
    .catch(error => {
        console.error("Error during fetch:", error.error, error.status);
    });
}

function handleSubmiSelectCSV(event) {
    event.preventDefault();
    selectCSV();
}

// Main Folder
let formMainFolder = document.getElementById("cargar_carpeta");
formMainFolder.addEventListener("submit", handleSubmiSelectMainFolder);

function selectMainFolder() {
    let submitButton = document.getElementById("cargar");
    
    let formData = new FormData(formMainFolder);
    formData.append("cargar", submitButton.name);
    
    fetch("", {
        method: "POST",
        body: formData,
    })
    .then(async response => {
        if (response.ok) {
            return response.json();
        } else {
            const data = await response.json();
			return await Promise.reject(data);
        }
    })
    .then(jsonResponse => {
        let folders = jsonResponse.folders_details;
        let selectedClusters = jsonResponse.selected_cluster_names;
		hideDiv("div-seleccionar-carpeta-principal");
		displayDiv("div-seleccionar-carpeta-destino");
        generateSubfolderCheckboxList(folders);
        generateClusterList(selectedClusters);
        emptyDiv("div-seleccionar-especies");
    })
    .catch(error => {
        console.error("Error during fetch:", error.error, error.status);
    });
}

function handleSubmiSelectMainFolder(event) {
    event.preventDefault();
    selectMainFolder();
}

// Destination folder
let formDestinationFolder = document.getElementById("carpeta_destino");
formDestinationFolder.addEventListener("submit", handleSubmiSelectDestinationFolder);

function handleSubmiSelectDestinationFolder(event) {
    event.preventDefault();
    selectDestinationFolder();
}

function selectDestinationFolder() {
    let form = document.getElementById("carpeta_destino");
    let submitButton = document.getElementById("destino");

	let formData = new FormData(form);
	formData.append("destino", submitButton.name);

	fetch("", {
		method: "POST",
		body: formData,
	})
	.then(async response => {
		if (response.ok) {
			return response.json();
		} else {
			const data = await response.json();
			return await Promise.reject(data);
		}
	})
	.then(jsonResponse => {
        let folders = jsonResponse.folders;
		let destinationFolder = jsonResponse.destination_folder;
		hideDiv("div-seleccionar-carpeta-destino");
		emptyDiv("div-seleccionar-subcarpetas");
		generateSelectedFoldersList(folders, destinationFolder);
		displayDiv("div-procesar");
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}

// Process folders
let formProcessFolders = document.getElementById("form_procesar");
formProcessFolders.addEventListener("submit", handleSubmiSelectProcessFolders);

function handleSubmiSelectProcessFolders(event) {
    event.preventDefault();
    processFolders();
}

function processFolders() {
    let form = document.getElementById("form_procesar");
    let submitButton = document.getElementById("procesar_carpetas_reconocer");

	let formData = new FormData(form);
	formData.append("procesar_carpetas", submitButton.name);

	fetch("", {
		method: "POST",
		body: formData,
	})
	.then(async response => {
		if (response.ok) {
			return response.json();
		} else {
			const data = await response.json();
			return await Promise.reject(data);
		}
	})
	.then(jsonResponse => {
        displayDivProgressBar();
		hideDiv("div-procesar");
		displayDiv("div-opciones-radio");
        displayDiv("div-parar");
		displaySection("section-cluster-reconocer");
		displaySection("section-representativo-reconocer");
        intervalId = setInterval(() => updateProgressBar("reconocer", intervalId), 500);
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}

// Stop process
let formStopProcess = document.getElementById("form_parar");
formStopProcess.addEventListener("submit", handleSubmiStopProcess);

function handleSubmiStopProcess(event) {
    event.preventDefault();
    stopProcess();
}

function stopProcess() {
    let form = document.getElementById("form_parar");
    let submitButton = document.getElementById("parar_proceso");

	let formData = new FormData(form);
	formData.append("parar_proceso", submitButton.name);

	fetch("", {
		method: "POST",
		body: formData,
	})
	.then(async response => {
		if (response.ok) {
			return response.json();
		} else {
			const data = await response.json();
			return await Promise.reject(data);
		}
	})
	.then(jsonResponse => {
		clearInterval(intervalId);
		const spanValue = document.getElementById("value1");
		spanValue.innerHTML = "Cancelado";
		hideDiv("div-parar");
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}