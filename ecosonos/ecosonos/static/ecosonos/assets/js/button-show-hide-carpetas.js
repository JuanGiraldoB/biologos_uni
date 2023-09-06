jQuery(function ($) {
	$("#swapFire").on("click", function () {
		var $el = $(this),
			textNode = this.lastChild;
		$el
			.find("span")
			.toggleClass("glyphicon-folder-close glyphicon-folder-open");
		textNode.nodeValue =
			($el.hasClass("showFire") ? "Deseleccionar" : "Seleccionar") +
			" Carpetas ";
		$el.toggleClass("showFire");
	});
});

document.addEventListener("DOMContentLoaded", function () {
	const selectAllBtn = document.getElementById("swapFire");

	if (selectAllBtn) {
		const checkboxes = document.getElementsByName("carpetas");

		selectAllBtn.addEventListener("click", function () {
			let value;

			if (this.name === "false") {
				value = false;
				this.name = "true";
			} else {
				value = true;
				this.name = "false";
			}

			for (const checkbox of checkboxes) {
				checkbox.checked = value;
			}
		});
	}
});
