// Create tags

function generateFileList(files){
	let ul = document.getElementById("ul-lista-archivos");

	files.forEach(file => {
		const a = createAElement(file);
		const li = createLi();
		
		li.appendChild(a);
		ul.appendChild(li);
	});
}

function createAElement(file){
	let urlPath =  `/etiquetado/espectrograma/${file.path}`
	const a = document.createElement("a");
	a.href = urlPath;
	a.textContent = file.basename;
	a.addEventListener('click', (event) => {
		event.preventDefault();

		fetch(urlPath)
			.then(async response => {
				if(response.ok) {
					return response.json();
				}
			})
			.then(jsonResponse => {
				let name = jsonResponse.nombre;
				let ruta = jsonResponse.ruta;
				let frequencies = jsonResponse.frequencies;
				let times = jsonResponse.times;
				let spectrogram = jsonResponse.spectrogram;

				document.getElementById("section-espectrograma").style.display = "block";
				document.getElementById("espectrograma-h1").textContent = "Espectrograma de " + name;


				function reproducir_sonido(ruta, etiqueta, x0, x1, y0, y1) {
					let csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
				
					fetch(`/etiquetado/espectrograma/reproducir/${ruta}`, {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
							"X-CSRFToken": csrfToken,
						},
						body: JSON.stringify({
							etiqueta: etiqueta,
							x0: x0,
							x1: x1,
							y0: y0,
							y1: y1,
						}),
					})
						.then((response) => {
							if (!response.ok) {
								throw new Error("Network response was not ok");
							}
							return response.json();
						})
						.then((data) => {
							console.log("Success:", data);
						})
						.catch((error) => {
							console.error("Error:", error);
						});
				}
				let plot = document.getElementById("plot");

				// Define the data for the plot
				let data = {
					x: times,
					y: frequencies,
					z: spectrogram,
					type: "heatmap",
					aspect: "auto",
					colorscale: "Rainbow",
					dragmode: "select",
				};

				// let lockIcon = {
				// 	width: 1000,
				// 	height: 1000,
				// 	path: "M320 768h512v192q0 106 -75 181t-181 75t-181 -75t-75 -181v-192zM1152 672v-576q0 -40 -28 -68t-68 -28h-960q-40 0 -68 28t-28 68v576q0 40 28 68t68 28h32v192q0 184 132 316t316 132t316 -132t132 -316v-192h32q40 0 68 -28t28 -68z",
				// 	transform: "matrix(0.75 0 0 -0.75 0 1000)",
				// };

				// let modeBarButtons = [
				// 	[
				// 		{
				// 			name: "Borrar ultima etiqueta",
				// 			icon: lockIcon,
				// 			click: () => {
				// 				quitarEtiqueta();
				// 			},
				// 		},
				// 	],
				// ];

				// Define the layout for the plot
				let layout = {
					xaxis: { title: "Tiempo (s)" },
					yaxis: { title: "Frecuencia (Hz)" },
					margin: { t: 60 },
					width: 800,
					height: 400,
					font: { size: 16 },
					dragmode: "select",
					updatemenus: [
						{
							buttons: [
								{
									args: [{ dragmode: "select" }],
									label: "Select",
									method: "relayout",
								},
							],
							direction: "left",
							pad: { r: 10, t: 10 },
							showactive: true,
							type: "buttons",
							x: 0.1,
							xanchor: "left",
							y: 1.1,
							yanchor: "top",
						},
						{
							buttons: [
								{
									args: ["colorscale", "Rainbow"],
									label: "Rainbow",
									method: "restyle",
								},
								{
									args: ["colorscale", "Blues"],
									label: "Blues",
									method: "restyle",
								},
								{
									args: ["colorscale", "Reds"],
									label: "Reds",
									method: "restyle",
								},
								{
									args: ["colorscale", "Viridis"],
									label: "Viridis",
									method: "restyle",
								},
								{
									args: ["colorscale", "Greens"],
									label: "Greens",
									method: "restyle",
								},
								{
									args: ["colorscale", "Earth"],
									label: "Earth",
									method: "restyle",
								},
							],
							direction: "down",
							pad: { r: 10, t: 10 },
							showactive: true,
							type: "dropdown",
							x: 0.25,
							xanchor: "left",
							y: 1.1,
							yanchor: "top",
						},
					],
				};

				// Create the plot
				Plotly.newPlot("plot", [data], layout);

				const addLabel = (x, y, label) => {
					return {
						x: x,
						y: y,
						xref: "x",
						yref: "y",
						text: label,
						showarrow: false,
						font: { size: 12, color: "white" },
					};
				};

				// Add the callback function to the plotly_selected event
				plot.on("plotly_selected", function (data) {
					console.log(data);
					let range = data.range;
					// X
					let leftX = range.x[0];
					let rightX = range.x[1];

					// Y
					let bottomY = range.y[0];
					let topY = range.y[1];
					console.log(data.range);

					annotations = layout.annotations || [];
					//  Calculate center point
					let centerX = (range.x[0] + range.x[1]) / 2;
					let centerY = (range.y[0] + range.y[1]) / 2;

					let etiqueta = document.getElementById("etiqueta");
					let labelCenter = etiqueta.value;
					annotations.push(addLabel(centerX, centerY, labelCenter));

					// top left
					let labelTopLeft = `(${leftX.toFixed(2)} , ${topY.toFixed(2)})`;
					annotations.push(addLabel(leftX, topY, labelTopLeft));

					// bottom right
					let labelBottomRight = `(${rightX.toFixed(2)} , ${bottomY.toFixed(2)})`;
					annotations.push(addLabel(rightX, bottomY, labelBottomRight));

					Plotly.relayout("plot", { annotations: annotations });
					reproducir_sonido(
						ruta,
						labelCenter,
						parseInt(leftX),
						parseInt(rightX),
						bottomY,
						topY
					);
				});
			})
	})
	return a;
}


function generateFolderHeader(text){
	let div = document.getElementById("selected-folders");
	const header1 = createHeader("h1", text)
	div.appendChild(header1);
}

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
		let checkbox = createCheckBox(folder.folder_path);
		let checkboxLabel = createCheckBoxLabel(folder.folder_name);
		innerDiv.appendChild(checkbox);
		innerDiv.appendChild(checkboxLabel);
		outerDiv.appendChild(innerDiv);
		outerDiv.className = "";
	}
}

function generateIndexList(indices){
	document.getElementById("h1-indices-seleccionados").style.display = "block";
	let ul = document.getElementById("ul-indices-seleccionados");
	let n = indices.length;

	for (let i = 0; i < n; i++) {
		const index = indices[i];
		let label = createLabel(index);
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

function createCheckBox(value) {
	let checkbox = document.createElement("input");
	checkbox.type = "checkbox";
	checkbox.name = "carpetas";
	checkbox.value = value;
	checkbox.checked = true;

	return checkbox;
}

function createCheckBoxLabel(text) {
	let label = document.createElement("label");
	label.htmlFor = "carpetas";
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

function hideDivCsv() {
	document.getElementById("div-mostrar-csv").style.display = "none";
}

function displayDivCsv() {
	document.getElementById("div-mostrar-csv").style.display = "block";
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