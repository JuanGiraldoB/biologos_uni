let intervalIdProgressBar;
let waitTime = 1000;

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
		displayDivProgressBar();
		emptyDiv("contedorImagenes");
        hideDiv("div-seleccionar-csv");
        displayDiv("div-parar");
		intervalIdProgressBar = setInterval(() => updateProgressBar("temporal", intervalIdProgressBar, waitTime), waitTime);
    })
    .catch(error => {
        console.error("Error during fetch:", error.error, error.status);
    });
}

function handleSubmiSelectCSV(event) {
    event.preventDefault();
    selectCSV();
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
		displayDiv("div-seleccionar-csv");
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