//<![CDATA[
// Our global state
var gLocalSearch;
var gMap;
var gInfoWindow;
var gSelectedResults = [];
var gCurrentResults = [];
var gSearchForm;
// Create our "tiny" marker icon
var gYellowIcon = new google.maps.MarkerImage( "http://labs.google.com/ridefinder/images/mm_20_yellow.png", 
	new google.maps.Size(12, 20), new google.maps.Point(0, 0), new google.maps.Point(6, 20));
var gRedIcon = new google.maps.MarkerImage( "http://labs.google.com/ridefinder/images/mm_20_red.png", 
	new google.maps.Size(12, 20), new google.maps.Point(0, 0), new google.maps.Point(6, 20));
var gSmallShadow = new google.maps.MarkerImage( "http://labs.google.com/ridefinder/images/mm_20_shadow.png", 
	new google.maps.Size(22, 20), new google.maps.Point(0, 0), new google.maps.Point(6, 20));
// Set up the map and the local searcher.
function loadMap(options) 
{	
	if (typeof options=='undefined'){
		options = {};
	}
	
	var gOptions = {
	  zoom: typeof options.zoom=='undefined' ? 13 : options.zoom,
	  mapTypeId: typeof options.mapTypeId=='undefined' ? google.maps.MapTypeId.ROADMAP : options.mapTypeId,
	  panControl: typeof options.panControl=='undefined' ? true : options.panControl,
	  zoomControl: typeof options.zoomControl=='undefined' ? true : options.zoomControl,
	  mapTypeControl: typeof options.mapTypeControl=='undefined' ? true : options.mapTypeControl,
	  scaleControl: typeof options.scaleControl=='undefined' ? false : options.scaleControl,
	  streetViewControl: typeof options.streetViewControl=='undefined' ? true : options.streetViewControl,
	};
	
	//console.log(gOptions);
	
    // Initialize the map with default UI.
    gMap = new google.maps.Map(document.getElementById("map"), 
    {
        center : new google.maps.LatLng(citycenter[cod_ciudad][0], citycenter[cod_ciudad][1]), 
        zoom : gOptions.zoom, 
        mapTypeId : gOptions.mapTypeId,
		panControl: gOptions.panControl,
		zoomControl: gOptions.zoomControl,
		mapTypeControl: gOptions.mapTypeControl,
		scaleControl: gOptions.scaleControl,
		streetViewControl: gOptions.streetViewControl        
    });
    // Create one InfoWindow to open when a marker is clicked.
    gInfoWindow = new google.maps.InfoWindow;
    google.maps.event.addListener(gInfoWindow, 'closeclick', function () 
    {
        unselectMarkers();
    });
}
function unselectMarkers() 
{
    for (var i = 0; i < gCurrentResults.length; i++) {
        gCurrentResults[i].unselect();
    }
}
function localSearch(query, has_node, page){
	
	var url_json = "/" + ciudad + "/sitios.json/?q=" + query;
	if (typeof page != "undefined") {
    	url_json += "&amp;page=" + page;
  	}
	$.getJSON(url_json, function(data, responseCode) {
		OnLocalSearch(data.results, has_node);
		
		//pagination
		if(data.pagination){
			var url_frame = "/" + ciudad + "/iframe/?q=" + query;
			var html_pag = '';
			if (data.pagination.has_previous == "True"){
				html_pag  += '<a href="'+url_frame+'&amp;page='+data.pagination.previous_page+'" title="Anteriores">&laquo;</a> ';
			}
			html_pag += 'Página '+ data.pagination.page +' de '+ data.pagination.total_pages;
			if (data.pagination.has_next == "True"){
				html_pag  += ' <a href="'+url_frame+'&amp;page='+data.pagination.next_page+'" title="Siguientes">&raquo;</a>';
			}
			$("#pages").html(html_pag);
		}
	});
}
function randomSearch(max_elements, has_node){
	var url_json = "/" + ciudad + "/sitios.json/random/"+ max_elements +"/";
	$.getJSON(url_json, function(data, responseCode) {
		OnLocalSearch(data, has_node);
	});
}
// Called when Local Search results are returned, we clear the old
// results and load the new ones.
function OnLocalSearch(results, has_node) 
{
	if (typeof has_node == "undefined") {
    	has_node = true;
  	}
	
	//console.log(results);
    if (!results) {
        return;
    }
    var gBounds = new google.maps.LatLngBounds();
    // Clear the map
    for (var i = 0; i < gCurrentResults.length; i++) {
        gCurrentResults[i].marker().setMap(null);
    }
    // Close the infowindow
    gInfoWindow.close();
    gCurrentResults = [];
    for (var i = 0; i < results.length; i++) 
    {
        var local_result = new LocalResult(results[i], has_node);
        gCurrentResults.push(local_result);
        var position = local_result.marker().getPosition();
        gBounds.extend(position);
    }
    if (gCurrentResults.length > 0) {
        gMap.fitBounds(gBounds); // fit the map to the markers
    }
}
function LocalResult(result, has_node) 
{
    var me = this;
    me.has_node_ = has_node;
    me.result_ = result;
    me.marker_ = me.marker();
    if (me.has_node_){
    	me.resultNode_ = me.node();
	    google.maps.event.addDomListener(me.resultNode_, 'mouseover', function () 
	    {
	        // Highlight the marker and result icon when the result is
	        // mouseovered.  Do not remove any other highlighting at this time.
	        me.highlight(true);
	    });
	    google.maps.event.addDomListener(me.resultNode_, 'mouseout', function () 
	    {
	        // Remove highlighting unless this marker is selected (the info
	        // window is open).
	        if (!me.selected_) {
	            me.highlight(false);
	        }
	    });
	    google.maps.event.addDomListener(me.resultNode_, 'click', function () 
	    {
	        me.select();
	    });
	    google.maps.event.addDomListener(document.getElementById('link_' + me.result_.id), 'click', function (e) 
	    {
	    	e.preventDefault();
	        me.select();
	    });
    }
}
LocalResult.prototype.node = function () 
{
    if (this.resultNode_) {
        return this.resultNode_;
    }
   	return document.getElementById('result_' + this.result_.id);
    
}
// Returns the GMap marker for this result, creating it with the given
// icon if it has not already been created.
LocalResult.prototype.marker = function () 
{
    var me = this;
 	//console.log("lat="+me.result_.lat);   
    if (me.marker_) {
        return me.marker_;
    }
    me.marker_ = new google.maps.Marker(
    {
        position : new google.maps.LatLng(parseFloat(me.result_.lat), parseFloat(me.result_.lng)), 
        icon : gYellowIcon, shadow : gSmallShadow, map : gMap
    });
    google.maps.event.addListener(me.marker_, "click", function () 
    {
        me.select();
    });
    //console.log(me.marker_);
    return me.marker_;
};
// Unselect any selected markers and then highlight this result and
// display the info window on it.
LocalResult.prototype.select = function () 
{
    unselectMarkers();
    this.selected_ = true;
    this.highlight(true);
    gInfoWindow.setContent(this.info());
    gInfoWindow.open(gMap, this.marker());
    gMap.panTo(this.marker().getPosition());
};
LocalResult.prototype.isSelected = function () 
{
    return this.selected_;
};
// Remove any highlighting on this result.
LocalResult.prototype.unselect = function () 
{
    this.selected_ = false;
    this.highlight(false);
};
// Returns the HTML we display for a result before it has been "saved"
LocalResult.prototype.info = function () 
{
    if (this.result_.info) {
        return this.result_.info;
    }
    return this.infoWindowHtml();
}
LocalResult.prototype.highlight = function (highlight) 
{
    this.marker().setOptions({
        icon : highlight ? gRedIcon : gYellowIcon
    });
    if (this.has_node_){
    	this.node().className = "sitio" + (highlight ? " red" : "");
    }
}
LocalResult.prototype.infoWindowHtml = function () 
{
	var input = this.result_;
    var html = '<div class="vcard">';
    if (input.patrocinado > 0)
    {
        html += '<img src="' + input.logo + '" alt="" align="left" width="50px" height="50px" style="padding: 3px"/>';
    }
    var target = '_parent';
    if (!this.has_node_){
    	target = '_blank';
    }
    html += '<span class="adr">' + '<a class="url fn org" href="/' + ciudad + '/sitio/' + input.slug + '" target="'+target+'">' + input.nombre + '</a><br/>';
    for (var i = 0; i < input.tipos.length; i++) {
        html += '<span class="type">' + input.tipos[i] + '</span> ';
    }
    html += '<br/>';
    if (input.direccion.length > 0) {
        html += '<span class="street-address">' + input.direccion + '</span><br/>';
    }
    html += '<span class="locality">' + input.zona + '</span> ' + '(<span class="region">' + input.ciudad + '</span>)<br/>';
    if (input.telefono != null && input.telefono != "None") {
        html += '<span class="tel">' + input.telefono + '</span><br/>';
    }
    html += '</span>';
    if (input.comentarios > 1)
    {
        html += '<span class="reviews"><img src="/media/icons/balloon.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="'+target+'">' + input.comentarios + ' opiniones</a></span><br/>';
    }
    else
    {
        html += '<span class="reviews"><img src="/media/icons/balloon.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="'+target+'">Deja tu opinión</a></span><br/>';
    }
    if (input.fotos > 1)
    {
        html += '<span class="photos"><img src="/media/icons/image.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="'+target+'">' + input.fotos + ' fotos</a></span><br/>';
    }
    else
    {
        html += '<span class="photos"><img src="/media/icons/image.png" alt="" /> <a href="/' + ciudad + '/sitio/' + input.slug + '" target="'+target+'">Sube tus fotos</a></span><br/>';
    }
    //html += '<a class="neighbours" href="javascript:" onclick="buscar_sitios_cercanos(\'' + input.slug + '\'); return false;">Mostrar sitios cercanos &raquo;</a><br/>';
    html += '<div align="right"><a href="/' + ciudad + '/sitio/' + input.slug + '" target="'+target+'">Visitar ficha &raquo;</a></div>'; 
    html += '</div>';
    return html;
}
//]]>