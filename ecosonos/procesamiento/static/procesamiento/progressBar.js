let intervalId = null;

document.addEventListener("DOMContentLoaded", function () {
    let button = document.getElementById("procesando");

    if (button) {
        intervalId = setInterval(updateProgressBar, 500);
    }

});

function updateProgressBar() {
    let xhr = new XMLHttpRequest();

    xhr.open("POST", "/preproceso/barra_progreso", true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            const progress = data['progreso'];
            const max = data['max'];
            const div = document.getElementById("progreso_completado");

            div.innerHTML = `${progress}/${max}`

            console.log(`${progress}/${max}`)

            if (progress == "terminado") {
                clearInterval(intervalId);
            }
        }
    };
    xhr.send();
}
