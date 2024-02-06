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
        let indices = jsonResponse.indices;
        let folders = jsonResponse.folders_details;
        hideDivMainFolder();
        hideDivCsv();
        displayDivDestinationFolder();
        generateIndexList(indices);
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
        console.log(jsonResponse)
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
        hideDivProcess();
        intervalId = setInterval(updateProgressBar, 500);
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}

// Show plot
let formDisplayPlot = document.getElementById("form_grafica");
formDisplayPlot.addEventListener("submit", handleSubmiDisplayPlot);


function handleSubmiDisplayPlot(event) {
    event.preventDefault();
    displayPlot();
}

function displayPlot() {
    let form = document.getElementById("form_grafica");
    let submitButton = document.getElementById("mostrar-grafica");
    
	let formData = new FormData(form);
	formData.append("mostrar-grafica", submitButton.name);
    
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
        let plots = jsonResponse.plots_urls;
        let indices = jsonResponse.indices;
        
        generatePlotList(plots, indices);
	})
	.catch(error => {
        console.error("Error during fetch:", error.error, error.status);
	});
}

// CSV
let formCSV = document.getElementById("form-csv");
formCSV.addEventListener("submit", handleSubmiCSV);

function handleSubmiCSV(event) {
    event.preventDefault();
    loadCSV();
}

function loadCSV() {
    let form = document.getElementById("form_grafica");
    let submitButton = document.getElementById("cargar-csv");
    
	let formData = new FormData(form);
	formData.append("cargar-csv", submitButton.name);
    
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
        let plots = jsonResponse.plots_urls;
        let indices = jsonResponse.indices;

        hideDivMainFolder();
        hideDivDestinationFolder();
        hideDivProcess();
        generateIndexList(indices);
        generatePlotList(plots, indices);
	})
	.catch(error => {
        console.error("Error during fetch:", error.error, error.status);
	});
}
