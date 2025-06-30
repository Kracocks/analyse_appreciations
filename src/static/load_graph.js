var graphique = document.getElementById("bargraph");
var progress = document.getElementById("progress");

// Lecteur d'évenement pour mettre a jour la barre de chargement
var source = new EventSource("/progress");
source.onmessage = function(event) {
    graphique.style.display = "none";
    progress.style.display = "block";

    var data = JSON.parse(event.data)

    console.log(event)
    $('.progress-bar').css('width', data.progression+'%').attr('aria-valuenow', data.progression);
    $('.progress-bar-label').text(data.progression+'%');

    console.log(data.progression)

    if(data.progression == 100){
        graphique.style.display = "block";
        progress.style.display = "none";
        source.close()
    }
}

// Génération du graphique quand un fichier est sélectionné
fetch('/get-graph')
.then(r => r.json())
.then(data => {
    var graphs = JSON.parse(data.graph);

    var graphique_div = document.getElementById("bargraph");
    var progress_div = document.getElementById("progress");
    if (graphique_div.style.display == "none") {
        graphique_div.style.display = "block";
        progress_div.style.display = "none";
    }
    Plotly.plot('bargraph', graphs, {}, {editable: true});

    // Evenement quand on clique sur un point
    var graphique = document.getElementById('bargraph');
    var selected_text = '';
});