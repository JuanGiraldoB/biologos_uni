let sonotipo = document.getElementById("sonotipo");
let sonotipoDiv = document.getElementById("sonotipo_div");

let reconocer = document.getElementById("reconocer");
let reconocerDiv = document.getElementById("reconocer_div");

// document.addEventListener("DOMContentLoaded", function () {
// 	reconocerDiv.style.display = "none";
// 	sonotipoDiv.style.display = "none";
// });

sonotipo.addEventListener("click", () => {
	reconocerDiv.style.display = "none";
	sonotipoDiv.style.display = "block";
});

reconocer.addEventListener("click", () => {
	sonotipoDiv.style.display = "none";
	reconocerDiv.style.display = "block";
});
