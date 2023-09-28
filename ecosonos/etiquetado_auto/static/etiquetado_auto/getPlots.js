function getPlots() {
	let xhr = new XMLHttpRequest();
	let formData = new FormData();

	formData.append("graficas", "graficas");
	xhr.open("POST", "/etiquetado-auto/plots", true);
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const imgUrls = data.img_urls;

			const container = document.getElementById("contedorImagenes");

			// Loop through the image URLs and create img elements
			imgUrls.forEach((url) => {
				const img = document.createElement("img");
				img.src = url;
				container.appendChild(img);
			});
		}
	};
	xhr.send(formData);
}
