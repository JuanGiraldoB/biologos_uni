let sonotipo = document.getElementById("sonotipo");
let sonotipoDiv = document.getElementById("sonotipo_div");

let reconocer = document.getElementById("reconocer");
let reconocerDiv = document.getElementById("reconocer_div");

let temporal = document.getElementById("temporal");
let temporalDiv = document.getElementById("temporal_div");

// document.addEventListener("DOMContentLoaded", function () {
// 	reconocerDiv.style.display = "none";
// 	sonotipoDiv.style.display = "none";
// });

sonotipo.addEventListener("click", () => {
	// Show
	sonotipoDiv.style.display = "block";

	// Hide
	reconocerDiv.style.display = "none";
	temporalDiv.style.display = "none";
});

reconocer.addEventListener("click", () => {
	// Show
	reconocerDiv.style.display = "block";

	// Hide
	sonotipoDiv.style.display = "none";
	temporalDiv.style.display = "none";
});

temporal.addEventListener("click", () => {
	// Show
	temporalDiv.style.display = "block";

	// Hide
	sonotipoDiv.style.display = "none";
	reconocerDiv.style.display = "none";
});
