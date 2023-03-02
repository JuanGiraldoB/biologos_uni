var intervalId = null;

document.addEventListener("DOMContentLoaded", function () {
    var button = document.getElementById("procesar");
    button.addEventListener("click", function () {
        intervalId = setInterval(updateProgressBar, 100);
    });
});

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

            progressBar.style.width = progress * 50 + '%';
            console.log(progress, max, "hey")
            if (progress == max) {
                clearInterval(intervalId);
            }
        }
    };
    xhr.send();
}
