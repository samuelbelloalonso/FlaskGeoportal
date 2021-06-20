var ultimoComponente = ''
var ultimoActivo = ''

var estiloActivo = {
    "color": "#ea04f9",
    "weight": 5,
    "opacity": 1
};

var estiloComponente = {
    "color": "#1864ff",
    "weight": 5,
    "opacity": 1
};

var tramo1Style = {
    "color": "#8E44AD",
    "weight": 5,
    "opacity": 1
};

var tramo2Style = {
    "color": "#173B4E ",
    "weight": 5,
    "opacity": 1
};



function dibujaGeojson(geojson, estilo) {
    if (geojson.length == 0) { return }

    mapaPintado = L.geoJSON(geojson, {
        style: estilo
    }).addTo(map)

    return mapaPintado._leaflet_id
}


function borrarGeojson(geojson) {
    //borrado de la layer anterior con global var para que no se borre

    map.eachLayer(function (layer) {
        if (layer._leaflet_id == geojson) {
            map.removeLayer(layer)
        }
    })

}



function centrarMapa(geojson, zoom) {
    var requiredArea = L.geoJson(geojson).getBounds();
    var cord = geojson[0].geometry.coordinates;
    if (Array.isArray(cord[0])) {
        map.setView(cord[0][0][1].reverse(), zoom);
    }

    else {
        map.setView(cord.reverse(), zoom);
    }
}



function verKpisConMediciones(idComponente, idActivo) {
    $("button").prop("disabled", true)
    $.get(`/consultasKpisConMediciones?componente=${idComponente}&activo=${idActivo}`, function (response) {
        $("#injectTarget").html(response);
        $("#divResultados").hide();
        $("#divAcciones").scrollTop(0).show();
        $("button").prop("disabled", false)
    });
}


function pedir_componente_geojson(idcomponente, idactivo) {
    $.ajax({
        url: "/activoycomponenteGeojson", data: {
            id_componente:
                idcomponente,
            id_activo:
                idactivo
        }, type: "GET", dataType: "json", success: function (response) {
            borrarGeojson(ultimoActivo)
            borrarGeojson(ultimoComponente)
            ultimoActivo = dibujaGeojson(response["activos"], estiloActivo)
            ultimoComponente = dibujaGeojson(response["componentes"], estiloComponente)
            centrarMapa(response["componentes"], 19)
        }
    });
}



function llenarTablaActivos(response) {
    var len = Object.keys(response.tramos).length;
    $("#tablaResultadosActivos > tbody").empty()
    for (i = 0; i < len; i++) {
        var aux = response.tramos[i];
        //tr inicia una fila nueva
        $("#mensajeNavegacion").text("Está viendo los activos asociados al tramo " + response.tramoNombre)
        html = `<tr class="idEstrada">` +
            `<td>${i + 1}</td>` +
            `<td>${aux.id}</td>` +
            `<td>${aux.nombre_activo}</td>` +
            `<td>${aux.id_tramo}</td>` +
            `<td class="td">` +
            '<input type="radio" name="tramo" onclick="dibujaYCentraActivo(' + aux.id + ')" value="' + aux.id + '" ">' +
            `</td>` +
            '<td class="td">' +
            `<input type="button" class="btn bg-secondary text-white" onclick="vercomponentes(${aux.id})" value="Ver asociados">` +
            '</td>' +
            '</tr>';
        $("#tablaResultadosActivos > tbody").append(html);
    }
    $("#divAcciones").hide();
    $("#divResultados").scrollTop(0).show();
}

function escondeDetallesMuestraTabla() {
    $("#divResultados").show();
    $("#divAcciones").hide();
}


function vercomponentes(idactivo) {
    $("button").prop("disabled", true)
    $.get(`/consultasComponentes?activo=${idactivo}`, function (response) {
        $("#injectTarget").html(response);
        $("#divResultados").hide();
        $("#divAcciones").scrollTop(0).show();
        $("button").prop("disabled", false)
    });
}


function dibujaYCentraActivo(idtramo) {
    $.ajax({
        url: "/activosGeojson",
        data: {
            // id_tramo: id_checkbox,
            id_tramo: idtramo
        },
        type: "GET",
        dataType: "json",
        success: function (response) {
            borrarGeojson(ultimoActivo)
            borrarGeojson(ultimoComponente)
            ultimoActivo = dibujaGeojson(response, estiloActivo) // dibuja el tramo especifico  
            centrarMapa(response, 12)
        }
    });
}

//peticion ajax mandandole el tramo del que queremos obtener informacion

function verActivosDeTramo() {
    $.ajax({
        url: "/geoportal",
        data: $("form").serialize(),
        type: "POST",
        dataType: "json",
        success: llenarTablaActivos
    });
}

function enviarAccionComponente() {
    $.ajax({
        url: "/decisiones",
        data: $("form").serialize(),
        method: "POST",
        success: function () {
            self.close()
        }
    })
}


function abreAcciones(idcomponente) {
    //equivalente a pasarle la ruta por /, llamo a la funcion en vez de eso
    //window.open(URL, name, specs, replace)
    window.open('/decisiones?componenteid=' + idcomponente, '', 'width=800,height=500')
}

function resetMapZoom() {
    map.setView([42.7674234, -7.8984065], 7.5)
}

