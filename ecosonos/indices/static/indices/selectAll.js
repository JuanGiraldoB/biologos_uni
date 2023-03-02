const selectAllBtn = document.getElementById("seleccionar-todos");
const checkboxes = document.getElementsByName("options");

selectAllBtn.addEventListener("click", function () {

    let value;

    if (this.name === 'false') {
        value = false;
        this.name = 'true';
    } else {
        value = true;
        this.name = 'false';
    }

    for (const checkbox of checkboxes) {
        console.log(value)
        checkbox.checked = value;
    }
});
