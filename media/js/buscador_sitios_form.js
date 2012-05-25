//$(document).ready(function() {
function load_buscador_sitios_form(){
	//$(function(){
	  //setAutoComplete("id_q", "results", "/"+ciudad+"/sitios.json/lookup/?query=");
	//});
	
	$('#ver_tags').bind('click', function(){
		$('#tag_list').slideToggle("slow");
		return false;
	});
	
	$('#tag_list a').each(function(){
		$(this).bind('click', function(){
			var texto_anterior = $('#id_q').val();
			if (texto_anterior.length == 0){
				$('#id_q').val($(this).text());
				$('#slug').html($(this).text());
			}
			else{
				$('#id_q').val(texto_anterior + ' ' + $(this).text());
				$('#slug').html(texto_anterior + ' ' + $(this).text());
			}
			return false;
		});
	});
	/*
	$('#buscador_sitios form').bind('submit', function(event){
		event.preventDefault();
		$.getJSON("/" + ciudad + "/sitios.json/?q=" + $('#id_q').val(), function(data){
			OnLocalSearch(data);		
		});
	});*/
	/*$.validator.addMethod('tag_regex', function(value, element) { 
	  return this.optional(element) || /^[a-zñA-ZÑ0-9\-\s]+$/.test(value); 
	}, 'Por favor, utiliza sólo caracteres alfanuméricos sin acentos en tus búsquedas');
	
	$('#buscador_sitios_form').validate({
		rules: {
			s: 'tag_regex'
		}
	});*/
	
	//$('#id_q').slug({slug: 'slug', hide: true});
	
	/*$('#buscador_sitios_form').bind('submit', function(event){
		event.preventDefault();
		$('#id_s').val($('#slug').text());
		this.submit();
	});*/
}
//});
