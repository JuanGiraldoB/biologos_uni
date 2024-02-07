// global vars
// let ruta, frequencies, times, spectrogram;


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
		let mainFolder = jsonResponse.selected_folder;
        hideDivMainFolder();
        displayDivDestinationFolder();
		generateFolderHeader("Carpeta principal seleccionada: " + mainFolder);
		
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
        let destinationFolder = jsonResponse.selected_destination_folder;
		let files = jsonResponse.files_details;
		hideDivDestinationFolder();
		generateFolderHeader("Carpeta destino seleccionada: " + destinationFolder);
		generateFileList(files);
	})
	.catch(error => {
		console.error("Error during fetch:", error.error, error.status);
	});
}
