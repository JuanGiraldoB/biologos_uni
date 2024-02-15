let intervalIdProgressBar;
let waitTime = 1000;

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
		hideDiv("div-seleccionar-carpeta-principal");
		displayDiv("div-seleccionar-carpeta-destino");
        generateSubfolderCheckboxList(folders);
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
    let submitButton = document.getElementById("procesar_carpetas");

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
		displaySection("section-cluster-sonotipo");
		displaySection("section-representativo-sonotipo");
        intervalIdProgressBar = setInterval(() => updateProgressBar("sonotipo", intervalIdProgressBar, waitTime), waitTime);
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
		clearInterval(intervalIdProgressBar);
		hideDiv("div-parar");
		setTimeout(() => {
			const spanValue = document.getElementById("value1");
			spanValue.innerHTML = "Cancelado";
		}, waitTime*2.5);
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}