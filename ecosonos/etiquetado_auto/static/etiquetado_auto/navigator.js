document.addEventListener("DOMContentLoaded", function () {
    // Add event listeners to the buttons
    document.getElementById("sonotipo").addEventListener("click", function () {
        navigateToUrl("/etiquetado-auto/sonotipo#opciones");
    });

    document.getElementById("reconocer").addEventListener("click", function () {
        navigateToUrl("/etiquetado-auto/reconocer#opciones");
    });

    document.getElementById("temporal").addEventListener("click", function () {
        navigateToUrl("/etiquetado-auto/temporal#opciones");
    });
});

function navigateToUrl(url) {
    window.location.href = url;
}