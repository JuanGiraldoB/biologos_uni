document.addEventListener("DOMContentLoaded", function () {
    // Add event listeners to the buttons
    document.getElementById("sonotipo").addEventListener("click", function () {
        navigateToUrl("/etiquetado-auto/sonotipo");
    });

    document.getElementById("reconocer").addEventListener("click", function () {
        navigateToUrl("/etiquetado-auto/reconocer");
    });

    document.getElementById("temporal").addEventListener("click", function () {
        navigateToUrl("/etiquetado-auto/temporal");
    });
});

function navigateToUrl(url) {
    window.location.href = url;
}