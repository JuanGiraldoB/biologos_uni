// Main Folder
let formMainFolder = document.getElementById("cargar_carpeta");
formMainFolder.addEventListener("submit", handleSubmiSelecttMainFolder);

function selectMainFolder() {
    let estadisticasCheckbox = document.getElementById("estadisticas");
    let submitButton = document.getElementById("cargar");

    let formData = new FormData(formMainFolder);
    formData.append("estadisticas", estadisticasCheckbox.checked);
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

        let statistics = jsonResponse.statistics;
        let folders = jsonResponse.folders_details;

        hideDivMainFolder();
        displayDivDestinationFolder();
        generateSubfolderCheckboxList(statistics, folders);
    })
    .catch(error => {
        console.error("Error during fetch:", error.error, error.status);
    });
}

function handleSubmiSelecttMainFolder(event) {
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
		hideDivDestinationFolder();
		emptyDiv("div-seleccionar-subcarpetas");
		generateSelectedFoldersList(folders, destinationFolder);
        displayDivProcess();
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
        intervalId = setInterval(updateProgressBar, 500);
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}