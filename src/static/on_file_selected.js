document
    .getElementById("recent_files_choice")
    .addEventListener("change", (event) => {
        console.log(event)
        document
            .getElementById("recent_file_form")
            .submit()
    })