document.addEventListener("DOMContentLoaded", () => {
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
				// console.error("Error:", error);
			});
	}

	// function quitarEtiqueta(params) {
	// 	let annotations = document.getElementById("plot").layout.annotations;
	// 	console.log("here then?");
	// 	if (annotations && annotations.length > 0) {
	// 		annotations.pop();
	// 		annotations.pop();
	// 		annotations.pop();
	// 		console.log("here?");
	// 		Plotly.relayout("plot", { annotations: annotations }); // Update the plot
	// 	}
	// }

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
});
