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

    // Evenement quand on clique sur un élément de la légende
    var graphique = document.getElementById('bargraph');

    graphique.on('plotly_legendclick', function(data){
        console.log(data)
        const curveNumber = data.curveNumber;
        const curve = data.fullData[curveNumber];
        const group = curve.legendgroup;
        annotations = data.fullLayout.annotations
    
        console.log(curve);
    
        let curvesToUpdate = [];
    
        data.fullData.forEach((trace, index) => {
            if (trace.legendgroup === group) {
                curvesToUpdate.push(index);
            }
        });
    
        var updateStyle;
        var updateLayout = { annotations: annotations };
    
        if (curve.visible === true) {
            updateStyle = { 'visible': 'legendonly' };
    
            // Ajout des annotations masquées
            if (curve.customdata && curve.customdata.length) {
                for (let i = 0; i < curve.customdata.length; i++) {
                    let couleur = curve.line.color;
                    let x = curve.x[i];
                    let y = curve.y[i];
                    updateLayout.annotations.forEach((elem) => {
                        if (elem.x == x && elem.y == y && elem.bgcolor == couleur) {
                            index_annotation_suppr = updateLayout.annotations.indexOf(elem);
                            if (index_annotation_suppr > -1) {
                                updateLayout.annotations.splice(index_annotation_suppr, 1);
                            }
                        }
                    });
                }
            }
        } else {
            updateStyle = { 'visible': true };
    
            // Ajout des annotations visibles
            if (curve.customdata && curve.customdata.length) {
                for (let i = 0; i < curve.customdata.length; i++) {
                    let text = curve.customdata[i];
                    let couleur = curve.line.color;
                    if (text != null) {
                        text = text.replace(/(.{1,32})(\s+|$)/g, '$1</br>');
                        text = '</br>' + text
                        updateLayout.annotations.push({
                            x: curve.x[i],
                            y: curve.y[i],
                            xref: "x",
                            yref: "y",
                            text: text,
                            clicktoshow: "onoff",
                            showarrow: true,
                            visible: false,
                            font: {
                                family: "Courier New, monospace",
                                size: 11,
                                color: "#ffffff"
                            },
                            align: "center",
                            arrowhead: 4,
                            arrowsize: 1,
                            arrowwidth: 2,
                            arrowcolor: "#636363",
                            ax: 0,
                            ay: -30,
                            bordercolor: "#c7c7c7",
                            borderwidth: 2,
                            borderpad: 4,
                            bgcolor: couleur,
                            opacity: 0.8
                        });
                    }
                }
            }
        }
    
        Plotly.restyle('bargraph', updateStyle, curvesToUpdate);
    
        Plotly.relayout('bargraph', updateLayout);
    
        return false;
    });
    
});