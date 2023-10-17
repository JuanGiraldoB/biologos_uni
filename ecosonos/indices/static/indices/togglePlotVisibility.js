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
