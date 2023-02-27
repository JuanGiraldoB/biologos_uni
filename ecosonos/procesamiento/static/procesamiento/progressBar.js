var intervalId = null;

document.addEventListener("DOMContentLoaded", function () {
    var button = document.getElementById("procesar");
    button.addEventListener("click", function () {
        intervalId = setInterval(updateProgressBar, 1000);
    });
});

const hiddenButton = document.getElementById('prueba');

function updateProgressBar() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/preproceso/", true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            const progress = data['progress'];
            const max = data['max'];
            const progressBar = document.getElementById("progress-bar");

            progressBar.style.width = progress + 10 + '%';

            if (progress == max) {
                hiddenButton.style.display = "block";
                clearInterval(intervalId);
            }
        }
    };
    xhr.send();
}
