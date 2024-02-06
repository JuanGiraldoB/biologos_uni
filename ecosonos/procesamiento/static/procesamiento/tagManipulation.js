// Create tags

function generateSubfolderCheckboxList(statistics, folders){
	let outerDiv = document.getElementById("div-seleccionar-subcarpetas");
	let n = folders.length;

	const headerText = "Seleccionar subcarpetas a procesar";
	const headerType = "h1";
	const header = createHeader(headerType, headerText);

	outerDiv.appendChild(header);

	for (let i = 0; i < n; i++) {
		const folder = folders[i];
		let innerDiv = createDiv("carpetas-cargadas");
		let checkbox = createCheckBox(folder.folder_path);
		let checkboxLabel = createCheckBoxLabel(folder, statistics);
		
		innerDiv.appendChild(checkbox);
		innerDiv.appendChild(checkboxLabel);
		outerDiv.appendChild(innerDiv);
		outerDiv.className = "";
	}
}

function generateSelectedFoldersList(folders, destinationFolder){
	document.getElementById("titulo-carpetas-procesar").style.display = "block";
	document.getElementById("nombre-carpeta-destino-seleccionada").innerText = "Carpeta destino: " + destinationFolder;
	let ul = document.getElementById("lista-nombre-carpetas-procesar");

	for (let i = 0; i < folders.length; i++) {
		const folder = folders[i];
		let label = createLabel(folder);
		let li = createLi();

		li.appendChild(label);
		ul.appendChild(li);
	}
}

function createDiv(className){
	let div = document.createElement("div");
	div.className = className;
	return div;
}

function createCheckBox(folderPath) {
	let checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.name = "carpetas";
	checkbox.value = folderPath;
	checkbox.checked = true;

	return checkbox;
}

function createCheckBoxLabel(folder, statistics) {
	let label = document.createElement("label");
	label.htmlFor = "carpetas";

	if (statistics) {
		label.textContent = `${folder.folder_name} - Numero de Archivos: ${folder.number_of_files} - Rango de duracion: ${folder.range_of_lengths} - Rango de fechas: ${folder.range_of_dates}`;
	} else {
		label.textContent = folder.folder_name;
	}

	return label;
}

function createLabel(folder){
	let label = document.createElement("label");
	label.textContent = folder;
	return label;
}

function createLi(label) {
	let li = document.createElement("li");
	// li.textContent = label;
	return li;
}

function createHeader(type, text) {
	let processingHeader = document.createElement(type);
	processingHeader.textContent = text;

	return processingHeader;
}

// Hide Show Tags
function hideDivMainFolder() {
	document.getElementById("div-seleccionar-carpeta-principal").style.display = "none";
}

function displayDivDestinationFolder() {
	document.getElementById("div-seleccionar-carpeta-destino").style.display = "block";
}

function displayDivProcess() {
	document.getElementById("div-procesar").style.display = "block";
}

function hideDivProcess() {
	document.getElementById("div-procesar").style.display = "none";
}

function displayDivProgressBar() {
	document.getElementById("div-barra-progreso").style.display = "block";
	const spanValue = document.getElementById("value1");
	spanValue.innerHTML = 0 + "%";
	const barElement = document.querySelector(".bar");
	barElement.style.setProperty("--percentage", spanValue.textContent);
}

function hideDivDestinationFolder() {
	document.getElementById("div-seleccionar-carpeta-destino").style.display = "none";
}

function emptyDiv(id){
	document.getElementById("div-seleccionar-subcarpetas").innerHTML = ""
}


function getSelectedCheckboxes() {
    // Get all checkboxes with the name "carpeta"
    const checkboxes = document.querySelectorAll('input[name="carpetas"]:checked');

    // Extract the values of the selected checkboxes
    const selectedValues = Array.from(checkboxes).map(checkbox => checkbox.value);

    return selectedValues;
}