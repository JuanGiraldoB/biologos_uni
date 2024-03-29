// Create tags

function generatePlotList(plots, indices){
	let divPlot = document.getElementById("div-graficas");
	removeAllChildElements(divPlot);
	
	for (let i = 0; i < plots.length; i++) {
		const plot_url = plots[i];
		const index = indices[i];
		
		fetch(plot_url)
		.then((response) => response.text())
		.then((htmlContent) => {
				const ul = createUlPlot();
				const iframe = createIframePlot(htmlContent);
				const header = createHeaderPlot(index);
				const li = createLiPlot(index);
				const button = createButtonPlot(index);
				const spanIcon = createSpanPlotIcon();
				const spanText = createSpanPlotText(index);
				
				button.appendChild(spanIcon);
				button.appendChild(spanText);
				li.appendChild(iframe);

				ul.appendChild(header);
				ul.appendChild(li);
				ul.appendChild(button);
				divPlot.appendChild(ul);
			})
			.catch((error) => {
				console.error("Error fetching HTML content:", error);
			});
			
	}
}

function createUlPlot(){
	let ul = document.createElement("ul");
	ul.id = "ul-graficas";
	ul.className = "lista-graficas";
	return ul;
}

function createHeaderPlot(text){
	let header = document.createElement("h2");
	header.className = "titulo-graficas";
	header.textContent = "Gráfica para el índice " + text;
	return header;
}

function createIframePlot(htmlContent){
	let iframe = document.createElement("iframe");
	iframe.srcdoc = htmlContent;
	iframe.style.width = "100%";
	iframe.style.height = "400px";
	return iframe;
}

function createLiPlot(text){
	let li = document.createElement("li");
	li.className = "item-graficas";
	li.id = "grafica-" + text;
	return li;
}

function createButtonPlot(text){
	let button = document.createElement("button");
	button.id = "btn-" + text;
	button.className = "btn btn-primary showFire1";
	button.onclick = () => {toggleVisibility(text);}
	return button;
}

function createSpanPlotIcon(){
	let span = document.createElement("span");
	span.className = "glyphicon glyphicon-eye-close";
	return span;
}

function createSpanPlotText(text){
	let span = document.createElement("span");
	span.id = "text-" + text;
	span.innerText = "Ocultar Gráfica";
	return span
}







function generateSpeciesName(species){
	let outerDiv = document.getElementById("div-seleccionar-especies");
	let n = species.length;

	const headerText = "Seleccionar especies";
	const headerType = "h1";
	const header = createHeader(headerType, headerText);

	outerDiv.appendChild(header);

	for (let i = 0; i < n; i++) {
		const specie = species[i];
		let innerDiv = createDiv("carpetas-cargadas");
		let checkbox = createCheckBox(specie, "clusters_names");
		let checkboxLabel = createCheckBoxLabel(specie, "clusters_names");
		innerDiv.appendChild(checkbox);
		innerDiv.appendChild(checkboxLabel);
		outerDiv.appendChild(innerDiv);
		outerDiv.className = "";
	}
}









function generateSubfolderCheckboxList(folders){
	let outerDiv = document.getElementById("div-seleccionar-subcarpetas");
	let n = folders.length;

	const headerText = "Seleccionar subcarpetas a procesar";
	const headerType = "h1";
	const header = createHeader(headerType, headerText);

	outerDiv.appendChild(header);

	for (let i = 0; i < n; i++) {
		const folder = folders[i];
		let innerDiv = createDiv("carpetas-cargadas");
		let checkbox = createCheckBox(folder.folder_path, "carpetas");
		let checkboxLabel = createCheckBoxLabel(folder.folder_name, "carpetas");
		innerDiv.appendChild(checkbox);
		innerDiv.appendChild(checkboxLabel);
		outerDiv.appendChild(innerDiv);
		outerDiv.className = "";
	}
}

function generateClusterList(clusters){
	document.getElementById("h1-clusters-seleccionados").style.display = "block";
	let ul = document.getElementById("ul-clusters-seleccionados");
	let n = clusters.length;

	for (let i = 0; i < n; i++) {
		const cluster = clusters[i];
		let label = createLabel(cluster);
		let li = createLi();

		li.appendChild(label);
		ul.appendChild(li);
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

function createCheckBox(value, name) {
	let checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.name = name;
	checkbox.value = value;
	checkbox.checked = true;

	return checkbox;
}

function createCheckBoxLabel(text, name) {
	let label = document.createElement("label");
	label.htmlFor = name;
	label.textContent = text;

	return label;
}

function createLabel(text){
	let label = document.createElement("label");
	label.textContent = text;
	return label;
}

function createLi() {
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
function displayDiv(id){
	document.getElementById(id).style.display = "block";
}

function hideDiv(id){
	document.getElementById(id).style.display = "none";
}

function displaySection(id){
	document.getElementById(id).style.display = "block";
}

function hideSection(id){
	document.getElementById(id).style.display = "none";
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
	document.getElementById(id).innerHTML = ""
}

function toggleVisibility(indice) {
	let grafica = document.getElementById("grafica-" + indice);
	let btn = document.getElementById("btn-" + indice);
	let text = document.getElementById("text-" + indice);
	let span = btn.querySelector("span");

	if (grafica.style.display === "none") {
		grafica.style.display = "block";
		text.innerText = "Ocultar Gráfica";
		span.className = "glyphicon glyphicon-eye-close";
	} else {
		grafica.style.display = "none";
		text.innerText = "Mostrar Gráfica";
		span.className = "glyphicon glyphicon-eye-open";
	}
}

function removeAllChildElements(tag) {
	while (tag.firstChild) {
		tag.removeChild(tag.firstChild);
	}
}