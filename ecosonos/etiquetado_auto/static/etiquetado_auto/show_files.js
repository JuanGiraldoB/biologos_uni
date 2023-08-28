function show_files() {
	let xhr = new XMLHttpRequest();
	xhr.open("POST", "/etiquetado-auto/lista_audios", true); // Replace with your actual GET URL
	xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
			const data = JSON.parse(xhr.responseText);
			const fileDetails = data.files_details;
			const size = Object.keys(fileDetails).length;

			let ulElement = document.getElementById("lista_audios");
			for (let i = 0; i < size; i++) {
				const fileDetail = fileDetails[i];
				const filePath = fileDetail.path;
				const fileName = fileDetail.basename;

				let liElement = document.createElement("li");
				let aElement = createA(filePath, fileName);

				liElement.appendChild(aElement);
				ulElement.appendChild(liElement);
			}
		}
	};
	xhr.send();
}

function createA(path, basename) {
	let aElement = document.createElement("a");
	aElement.href = `/etiquetado/espectrograma/${encodeURIComponent(path)}`;
	aElement.textContent = basename;

	return aElement;
}
