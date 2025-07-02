document
    .getElementById("eleve_choice")
    .addEventListener("change", (event) => {
        console.log(event)
        document
            .getElementById("eleve_form")
            .submit()
    })