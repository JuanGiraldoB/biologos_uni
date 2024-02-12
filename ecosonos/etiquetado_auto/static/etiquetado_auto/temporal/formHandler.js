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
		emptyDiv("contedorImagenes")
		intervalId = setInterval(() => updateProgressBar("temporal"), 500);
    })
    .catch(error => {
        console.error("Error during fetch:", error.error, error.status);
    });
}

function handleSubmiSelectCSV(event) {
    event.preventDefault();
    selectCSV();
}