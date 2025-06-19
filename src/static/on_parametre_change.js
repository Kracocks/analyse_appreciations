document
    .getElementById("modeles_choice")
    .addEventListener("change", (event) => {
        console.log(event)
        document
            .getElementById("parametre_form")
            .submit()
    })