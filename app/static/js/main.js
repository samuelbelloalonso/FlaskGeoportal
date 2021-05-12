var ultimoComponente = ''
var ultimoActivo = ''

var estiloActivo2 = {
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

var estiloActivo = {
    "color": "#ea04f9",
    "weight": 5,
    "opacity": 1
};





function dibujaGeojson(geojson, estilo) {
    if (geojson.length == 0) { return }

    mapaPintado = L.geoJSON(geojson, {
        style: estilo
    }).addTo(map)

    return mapaPintado._leaflet_id
    // layertramo = mapaPintadoPoint._leaflet_id

}


function borrarGeojson(geojson) {
    //borrado de la layer anterior con global var para que no se borre

    map.eachLayer(function (layer) {
        if (layer._leaflet_id == geojson) {
            map.removeLayer(layer)
        }
    })

}



function centrarMapa(tramo, zoom) {
    var requiredArea = L.geoJson(tramo).getBounds();
    var cord = tramo[0].geometry.coordinates;
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


function pedir_componente_geojson(id, activoid) {
    $.ajax({
        url: "/activoycomponenteGeojson", data: {
            id_componente:
                id,
            id_activo:
                activoid
        }, type: "GET", dataType: "json", success: function (response) {
            borrarGeojson(ultimoActivo)
            borrarGeojson(ultimoComponente)
            ultimoActivo = dibujaGeojson(response["activos"], estiloActivo2)
            ultimoComponente = dibujaGeojson(response["componentes"], estiloComponente)
            centrarMapa(response["componentes"], 19)
        }
    });
}




function aConsultasComponentes(id) {
    $.get(`/consultasComponentes?activo=${id}`, function (response) {
        $('#injectTarget').html(response)
    });
}

function renderFormResults(response) {
    var len = Object.keys(response.tramos).length;
    $("#tablaResultadosActivos > tbody").empty()
    for (i = 0; i < len; i++) {
        var aux = response.tramos[i];
        //tr inicia una fila nueva
        html = `<tr class="idEstrada">` +
            `<td>${i + 1}</td>` +
            `<td>${aux.id}</td>` +
            `<td>${aux.nombre_activo}</td>` +
            `<td>${aux.id_tramo}</td>` +
            `<td class="td">` +
            '<input type="radio" name="tramo" onclick="sendcheckboxes()" value="' + aux.id + '" ">' +
            `</td>` +
            '<td class="td">' +
            `<input type="button" class="btn btn-primary" onclick="vercomponentes(${aux.id})" value="Ver asociados">` +
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


function vercomponentes(id) {
    $("button").prop("disabled", true)
    $.get(`/consultasComponentes?activo=${id}`, function (response) {
        $("#injectTarget").html(response);
        $("#divResultados").hide();
        $("#divAcciones").scrollTop(0).show();
        $("button").prop("disabled", false)
    });
}



function ajaxRenderizado() {
    $.ajax({
        url: "/consultasTramos2",
        data: $("form").serialize(),
        type: "POST",
        dataType: "json",
        success: renderFormResults
    })
}


function sendcheckboxes() {
    //formar lista de id con los que tienen el check activado
    var checked = []
    var id_checkbox = ''
    $("input[name='tramo']:checked").each(function () {
        checked.push(parseInt($(this).val()));
        id_checkbox = parseInt($(this).val())
    });

    $.ajax({
        url: "/activosGeojson",
        data: {
            id_tramo: id_checkbox,
        },
        type: "GET",
        dataType: "json",
        success: function (response) {
            borrarGeojson(ultimoActivo)
            borrarGeojson(ultimoComponente)
            ultimoActivo = dibujaGeojson(response, estiloActivo2) // dibuja el tramo especifico  
            centrarMapa(response, 12)
        }
    });

}

function escondeDetallesMuestraTabla() {
    $("#divResultados").show();
    $("#divAcciones").hide();
}

//Función para renderizar el resultado de la peticion ajax
//devuelve la consulta
//borra la tabla y la reescribe
function renderFormResults(response) {
    var len = Object.keys(response.tramos).length;
    $("#tablaResultadosActivos > tbody").empty()
    for (i = 0; i < len; i++) {
        var aux = response.tramos[i];
        //tr inicia una fila nueva
        html = `<tr class="idEstrada">` +
            `<td>${i + 1}</td>` +
            `<td>${aux.id}</td>` +
            `<td>${aux.nombre_activo}</td>` +
            `<td>${aux.id_tramo}</td>` +
            `<td class="td">` +
            '<input type="radio" name="tramo" onclick="sendcheckboxes()" value="' + aux.id + '" ">' +
            `</td>` +
            '<td class="td">' +
            `<input type="button" class="btn btn-primary" onclick="vercomponentes(${aux.id})" value="Ver asociados">` +
            '</td>' +
            '</tr>';
        $("#tablaResultadosActivos > tbody").append(html);
    }
    $("#divAcciones").hide();
    $("#divResultados").scrollTop(0).show();
}


//peticion ajax mandandole el tramo del que queremos obtener informacion
$(function infoTramo() {
    //click en enviar
    $("#ajaxTrigger_form").click(function () {
        $.ajax({
            url: "/geoportal",
            data: $("form").serialize(),
            type: "POST",
            dataType: "json",
            success: renderFormResults
        });
    });
});


function aConsultasComponentes(id) {
    $.get(`/consultasComponentes?activo=${id}`, function (response) {
        $('#injectTarget').html(response)
    });
}

//peticion ajax mandandole el tramo del que queremos obtener informacion
$(function () {
    //click en enviar
    $("#ajaxTrigger_form").click(function () {
        $.ajax({
            url: "/geoportal",
            data: $("form").serialize(),
            type: "POST",
            dataType: "json",
            success: renderFormResults
        });
    });
});


