document.addEventListener("DOMContentLoaded", () => {
	let graph = document.getElementById("graph");

	let filename = document.getElementById("x");

	// Define the data for the graph
	let data = {
		x: times,
		y: frequencies,
		z: spectrogram,
		type: "heatmap",
		aspect: "auto",
		colorscale: "Rainbow",
		dragmode: "select",
	};

	// Define the layout for the graph
	let layout = {
		xaxis: { title: "Time (s)" },
		yaxis: { title: "Frequency (Hz)" },
		margin: { t: 60 },
		width: 800,
		height: 400,
		font: { size: 16 },
		dragmode: "select", // set the default dragmode to 'select'
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
		],
	};

	// Create the graph
	Plotly.newPlot("graph", [data], layout, {
		toImageButtonOptions: {
			filename: filename,
			width: 800,
			height: 600,
			format: "png",
		},
		// annotations: [],
	});

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
	graph.on("plotly_selected", function (data) {
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

		let labelCenter = "<etiqueta>";
		annotations.push(addLabel(centerX, centerY, labelCenter));

		// top left
		let labelTopLeft = `(${leftX.toFixed(2)} , ${topY.toFixed(2)})`;
		annotations.push(addLabel(leftX, topY, labelTopLeft));

		// bottom right
		let labelBottomRight = `(${rightX.toFixed(2)} , ${bottomY.toFixed(2)})`;
		annotations.push(addLabel(rightX, bottomY, labelBottomRight));

		Plotly.downloadImage("graph", {
			format: "png",
			width: 800,
			height: 600,
			filename: "newplot",
		});

		Plotly.relayout("graph", { annotations: annotations });
	});
});
