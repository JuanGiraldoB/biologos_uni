let intervalId = null;
document.addEventListener("DOMContentLoaded", function () {
    let button = document.getElementById("procesar");
    button.addEventListener("click", function () {
        console.log("dasdas")
        intervalId = setInterval(updateProgressBar, 1000);
    });
});


function updateProgressBar() {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/indices/", true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            const progress = data['progress'];
            const max = data['max'];
            const progressBar = document.getElementById("progress-bar");

            progressBar.style.width = progress * 10 + '%';
            console.log(progress, max)
            if (progress == max) {
                clearInterval(intervalId);
            }
        }
    };
    xhr.send();
}
