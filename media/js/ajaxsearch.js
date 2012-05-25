/* software_license
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
# 
# Creado por Fco. Javier Pérez Pacheco
# javielinux@gmail.com
# http://www.javielinux.com/
#
# Modificado por Manuel Martín Salvador
# draxus@granadapeople.com
# http://www.granadapeople.com
*/

function respondtoclick(event){
	buscar(document.getElementById('livesearch').value);
}

function AjaxSearch(pos, sep, type) {
	this.container = document.createElement("div");
	this.bottom = "5px";
	this.left = "65px";
	this.position = "absolute";
	this.width = "250px";
	this.textAlign = "left";
	this.color = "#000000";
	this.backgroundColor = "#ffffff";
	this.font = "Arial";
	this.size = "12px";
	this.border = "1px solid black";	
	this.position = pos;
	this.separate = sep;
	this.type = type;
	
	var form = document.createElement("form");
	form.id = "form_busqueda";
	form.setAttribute("method", "get");
	form.setAttribute("action", "#");
	form.setAttribute("onsubmit", "buscar(document.getElementById('livesearch').value); return false;");

	var input = document.createElement("input");
	input.id = "livesearch";
	input.type = "text";
	input.value = busqueda;
	form.appendChild(input);

	var boton = document.createElement("input");
	boton.id = "boton_buscar";
	boton.type = "submit";
	boton.value = "buscar";
	form.appendChild(boton);
	
	this.container.appendChild(form);
	
	//var resultados = document.createElement("div");
	//resultados.id = "sidebar";
	//resultados.className = "autosuggest";
	//resultados.style.visibility = "hidden";
	
	//this.container.appendChild(resultados);
}

AjaxSearch.prototype = new GControl();

AjaxSearch.prototype.setTextDecoration = function(t) { this.textDecoration = t; }
AjaxSearch.prototype.setColor = function(t) { this.color = t; }
AjaxSearch.prototype.setBackgroundColor = function(t) { this.backgroundColor = t; }
AjaxSearch.prototype.setFont = function(t) { this.font = t; }
AjaxSearch.prototype.setSize = function(t) { this.size = t; }
AjaxSearch.prototype.setBorder = function(t) { this.border = t; }
AjaxSearch.prototype.setPadding = function(t) { this.padding = t; }
AjaxSearch.prototype.setMargin = function(t) { this.margin = t; }
AjaxSearch.prototype.setTextAlign = function(t) { this.textAlign = t; }
AjaxSearch.prototype.setWidth = function(t) { this.width = t; }
AjaxSearch.prototype.setCursor = function(t) { this.cursor = t; }

AjaxSearch.prototype.initialize = function(map) {

	map.getContainer().appendChild(this.container);
	return this.container;

}

AjaxSearch.prototype.addButton = function(txt, funct) {

	var buttonDiv;
	if (this.type=="horizontal") {
		buttonDiv = document.createElement("span");
	} else {
		buttonDiv = document.createElement("div");
	}
	this.setButtonStyle(buttonDiv);
	this.container.appendChild(buttonDiv);
	buttonDiv.appendChild(document.createTextNode(txt));
	GEvent.addDomListener(buttonDiv, "click", function() {
		eval(funct);
	});

}

AjaxSearch.prototype.addImageButton = function(src, funct) {

	var buttonDiv;
	if (this.type=="horizontal") {
		buttonDiv = document.createElement("span");
	} else {
		buttonDiv = document.createElement("div");
	}

	var buttonImg = document.createElement("img");
	buttonImg.setAttribute('src',src);
	buttonImg.style.cursor = this.cursor;
	
	buttonDiv.appendChild(buttonImg);
	
	this.container.appendChild(buttonDiv);
	GEvent.addDomListener(buttonDiv, "click", function() {
		eval(funct);
	});

}

AjaxSearch.prototype.getDefaultPosition = function() {
	return new GControlPosition(this.position, new GSize(this.separate, this.separate));
}


AjaxSearch.prototype.setButtonStyle = function(button) {
	button.style.textDecoration = this.textDecoration;
	button.style.color = this.color;
	button.style.backgroundColor = this.backgroundColor;
	button.style.fontFamily = this.font;
	button.style.fontSize = this.size;
	button.style.border = this.border;
	button.style.padding = this.padding;
	button.style.margin = this.margin;
	button.style.textAlign = this.textAlign;
	button.style.width = this.width;
	button.style.cursor = this.cursor;
}
