//google.load("maps", "2");

var map;
var tooltip;
var initialLocation;
var cityLocation = new google.maps.LatLng(citycenter[cod_ciudad][0], citycenter[cod_ciudad][1]);
//var progressbar;

function initialize_map() {
    var myOptions = {
      zoom: 13,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map"), myOptions);
    
    // Try W3C Geolocation (Preferred)
	if(navigator.geolocation) {
	    navigator.geolocation.getCurrentPosition(function(position) {
	      initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
	      map.setCenter(initialLocation);
	    }, function() {
	      initialLocation = cityLocation;
	      map.setCenter(initialLocation);
	    });
	// Try Google Gears Geolocation
	} else if (google.gears) {
	    var geo = google.gears.factory.create('beta.geolocation');
	    geo.getCurrentPosition(function(position) {
	      initialLocation = new google.maps.LatLng(position.latitude,position.longitude);
	      map.setCenter(initialLocation);
	    }, function() {
	      initialLocation = cityLocation;
	      map.setCenter(initialLocation);
	    });
	// Browser doesn't support Geolocation
	} else {
	    initialLocation = cityLocation;
	    map.setCenter(initialLocation);
	}
	
	
    if(busqueda.length>0){
		buscar(busqueda);
	}
	else{
		//Mostrar sitios aleatorios y patrocinados
		mostrar_aleatorios_y_patrocinados(20);
	}
    
  }

function initialize_old () {	
	if (GBrowserIsCompatible()) {

		map = new google.maps.Map2(document.getElementById("map"));
		map.setCenter(new google.maps.LatLng(citycenter[cod_ciudad][0], citycenter[cod_ciudad][1]), 13);
	    
	    // Barra de cargando
	    //var progressbarOptions = {width: 150, loadstring: 'Cargando...'};
		//progressbar = new ProgressbarControl(map, progressbarOptions);
				
		// Control del mapa
		map.addControl(new GHierarchicalMapTypeControl());
		map.addControl(new GOverviewMapControl(new GSize(150, 150)));
		map.addControl(new GLargeMapControl());
		
		// Consejo
		/*var consejo = document.createElement("div");
		document.getElementById("map").appendChild(consejo);
		consejo.innerHTML = 'Haz clic en el mapa para obtener sitios cercanos a esa posición [<a id="cerrar_consejo" href="#">cerrar</a>]';
		consejo.setAttribute("class", "sin_resultados");
		consejo.setAttribute("id", "consejo");
		
		$('#cerrar_consejo').bind('click', function(){
			$('#consejo').slideUp('fast');
			return false;
		});*/
		
		// Icono (mejora: función para crear diferentes iconos)
		/*icon = new GIcon();
		icon.image = "http://labs.google.com/ridefinder/images/mm_20_red.png";
		icon.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
		icon.iconSize = new GSize(12, 20);
		icon.shadowSize = new GSize(22, 20);
		icon.iconAnchor = new GPoint(6, 20);
		icon.infoWindowAnchor = new GPoint(5, 1);*/
		
		tooltip = document.createElement("div");
		document.getElementById("map").appendChild(tooltip);
		tooltip.style.visibility="hidden";
      
		if(busqueda.length>0){
			buscar(busqueda);
		}
		else{
			//Mostrar sitios aleatorios y patrocinados
			mostrar_aleatorios_y_patrocinados(20);
		}
		
        GEvent.addListener(map, "click", function(overlay, point){
          if (point) {
           map.getInfoWindow().hide();
		   map.clearOverlays();
           marker = new GMarker(point);
           map.addOverlay(marker);
           map.panTo(point);
           //$('lat').value = point.lat();
           //$('lng').value = point.lng();
           marker.openInfoWindowHtml('<a class="neighbours" href="javascript:" onclick="buscar_sitios_cercanos_coordenadas(\'' + point.lat() + '\', \'' + point.lng() + '\'); return false;">Mostrar sitios cercanos &raquo;</a>');
          }
		}); //endListener

	} else {
		alert("Sorry, your browser cannot handle the true power of Google Maps");
	}
}

function formatTabOne (input) {
			
	var html 	 = '<div class="vcard">';
	
	if (input.patrocinado>0)
		html += '<img src="'+input.logo+'" alt="" align="left" width="50px" height="50px" style="padding: 3px"/>';
		
	html		 += '<span class="adr">'
				 + '<a class="url fn org" href="/' + ciudad + '/sitio/' + input.slug + '" target="_parent">' + input.nombre + '</a><br/>';
	
	for(var i=0; i<input.tipos.length; i++){
		html += '<span class="type">' + input.tipos[i] + '</span>';
	}
	
	html += '<br/>';
	
	if(input.direccion.length>0)			 
		html	+= '<span class="street-address">' + input.direccion + '</span><br/>';

		html	+= '<span class="locality">' + input.zona + '</span> '
				 + '(<span class="region">' + LISTA_CIUDADES[input.ciudad-1] + '</span>)<br/>';
	
	if(input.telefono!=null)			 
		html	+= '<span class="tel">' + input.telefono + '</span><br/>';
	
	html	+= '</span>';
	
	if(input.comentarios > 1)
		html	+= '<span class="reviews"><img src="/media/icons/balloon.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="_parent">' + input.comentarios + ' opiniones</a></span><br/>';
	else
		html	+= '<span class="reviews"><img src="/media/icons/balloon.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="_parent">Deja tu opinión</a></span><br/>';

	if(input.fotos > 1)
		html	+= '<span class="photos"><img src="/media/icons/image.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="_parent">' + input.fotos + ' fotos</a></span><br/>';
	else
		html	+= '<span class="photos"><img src="/media/icons/image.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="_parent">Sube tus fotos</a></span><br/>';

	html += '<a class="neighbours" href="javascript:" onclick="buscar_sitios_cercanos(\'' + input.slug + '\'); return false;">Mostrar sitios cercanos &raquo;</a><br/>'
		 + '<div align="right"><a href="/' + ciudad + '/sitio/' + input.slug + '" target="_parent">Visitar ficha &raquo;</a></div>'
		 + '</div>';

	return html;			
}

function showTooltip(marker) {
	tooltip.innerHTML = marker.tooltip;
	var point=map.getCurrentMapType().getProjection().fromLatLngToPixel(map.getBounds().getSouthWest(),map.getZoom());
	var offset=map.getCurrentMapType().getProjection().fromLatLngToPixel(marker.getPoint(),map.getZoom());
	var anchor=marker.getIcon().iconAnchor;
	var width=marker.getIcon().iconSize.width;
	var pos = new GControlPosition(G_ANCHOR_BOTTOM_LEFT, new GSize(offset.x - point.x - anchor.x + width,- offset.y + point.y +anchor.y)); 
	pos.apply(tooltip);
	tooltip.style.visibility="visible";
}
      
function createMarker(input) {
	
	
	var point = new google.maps.LatLng(input.lat, input.lng);
	/*var iconOptions = {};
	var icon;
	
	if (input.patrocinado>0){
		
		icon = new GIcon();
		icon.image = "/media/icons/google-maps-icons/"+input.icono;
		icon.iconSize = new GSize(32, 37);
		icon.iconAnchor = new GPoint(16, 32);
		icon.infoWindowAnchor = new GPoint(16, 0);

	}
	else{
			
		iconOptions.width = 22;
		iconOptions.height = 22;
		iconOptions.primaryColor = "#FF0000FF";
		iconOptions.cornerColor = "#FB8F8FFF";
		iconOptions.strokeColor = "#000000FF";
		icon = MapIconMaker.createMarkerIcon(iconOptions);
		
	}*/
	
	var marker = new google.maps.Marker({
        position: point, 
        map: map,
        title: input.nombre
    });   
	
	
	/*var marker = new GMarker(point, icon);
	marker.tooltip = '<div class="tooltip">'+input.nombre+'</div>';
	
	GEvent.addListener(marker, "click", function() {
		marker.openInfoWindowHtml(formatTabOne(input));
	});
	GEvent.addListener(marker,"mouseover", function() {
		showTooltip(marker);
	});        
	GEvent.addListener(marker,"mouseout", function() {
		tooltip.style.visibility="hidden"
	});*/
	return marker;
}

function parseJson (jsonData) {
	
	if(jsonData==null || jsonData.length==0){
		//No se han encontrado resultados
		var sin_resultados = document.createElement("div");
		document.getElementById("map").appendChild(sin_resultados);
		sin_resultados.innerHTML = 'No se han encontrado resultados<br/><a href="/' + ciudad + '/sitio/add/">Añade un nuevo sitio &raquo;</a>';
		sin_resultados.setAttribute("class", "sin_resultados");
		return false;
	}
		
	//progressbar.start(jsonData.length);
	var bounds = new google.maps.LatLngBounds();
	for (var i = 0; i < jsonData.results.length; i++) {
		var marker = createMarker(jsonData.results[i]);
		bounds.extend(marker);
		//map.addOverlay(marker);
		//progressbar.updateLoader(1);
	}
	
	//progressbar.remove();
	
	/*if(jsonData.length == 1) {
		map.setCenter(point, zoom); 
	}
	else{*/
		map.fitBounds(bounds);
		/*map.setZoom(map.getBoundsZoomLevel(bounds));
		var clat = (bounds.getNorthEast().lat() + bounds.getSouthWest().lat()) /2;
		var clng = (bounds.getNorthEast().lng() + bounds.getSouthWest().lng()) /2;
		map.setCenter(new GLatLng(clat,clng));*/
	//}
					
}

function buscar(s) {
	
	//map.getInfoWindow().hide();
	//map.clearOverlays();
	
	$.getJSON("/" + ciudad + "/sitios.json/?q=" + s, function(data, responseCode) { 
		parseJson(data);
	});
}

function buscar_sitios_cercanos(slug) {
	
	map.getInfoWindow().hide();
	map.clearOverlays();
	
	GDownloadUrl("/" + ciudad + "/sitio/" + slug + "/cercanos.json/", function(data, responseCode) { 
		parseJson(data);
	});
}

function buscar_sitios_cercanos_coordenadas(lat, lng) {
	
	map.getInfoWindow().hide();
	map.clearOverlays();
	
	GDownloadUrl("/" + ciudad + "/sitios.json/lat/" + lat + "/lng/" + lng + "/", function(data, responseCode) { 
		parseJson(data);
	});
}

function mostrar_aleatorios_y_patrocinados(num) {
	
	map.getInfoWindow().hide();
	map.clearOverlays();
	
	GDownloadUrl("/" + ciudad + "/sitios.json/random/" + num + "/", function(data, responseCode) { 
		parseJson(data);
	});
}

//google.setOnLoadCallback(initialize);
