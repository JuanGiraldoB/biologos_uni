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

    if (value){
        selectAllBtn.value = "Deseeleccionar todos los índices";
    }else{
        selectAllBtn.value = "Seleccionar todos los índices";
    }

    for (const checkbox of checkboxes) {
        checkbox.checked = value;
    }
});
