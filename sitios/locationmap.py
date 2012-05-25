# The development of this code was sponsored by MIG Internacional
# This code is released under the terms of the BSD license
# http://code.djangoproject.com/browser/django/trunk/LICENSE
# Feel free to use it at your whim/will/risk :D
# Contact info: Javier Rojas <jerojasro@gmail.com>

# -*- coding: utf-8 -*-

from django import forms

class LocationWidget(forms.widgets.Widget):
    def __init__(self, *args, **kw):
        super(LocationWidget, self).__init__(*args, **kw)
        self.inner_widget = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):

        lat, lng = float(37), float(-15)

        js = '''
                <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false&region=ES"></script>
		<script type="text/javascript">
		//<![CDATA[
		
			var map_%(name)s;
			var point;
			var geocoder;
                        var marker;

			function savePosition_%(name)s(point){
				var location = document.getElementById("id_%(name)s");
				location.value = point.lat().toFixed(6) + "," + point.lng().toFixed(6);
				map_%(name)s.panTo(point);
			}
			
			function saveAddress(address){
				var reverse_address = document.getElementById("id_direccion");
				
				var myAddress = address.split(",");
                                reverse_address.value = myAddress.slice(0, myAddress.length-2);
				//var accuracy = document.getElementById("accuracy");
				//accuracy.value = place.AddressDetails.Accuracy;
			}
			
			function addAddressToMap(results, status) {

                          if (status == google.maps.GeocoderStatus.OK){
                                map_%(name)s.setCenter(results[0].geometry.location);

				marker.setPosition(results[0].geometry.location);

				saveAddress(results[0].formatted_address);
				savePosition_%(name)s(marker.getPosition());
                          }
                          else{
                            document.getElementById("info_direccion").innerHTML = "Direcci&oacute;n no encontrada";
                          }
			}

			function showLocation(address) {
                            if(geocoder){
				geocoder.geocode({'address': address}, addAddressToMap);
                            }
			}
			
			function zoom(level){
				map_%(name)s.setZoom(level);
			}
		
			function load_%(name)s() {

                            var latlng = new google.maps.LatLng(citycenter[cod_ciudad][0], citycenter[cod_ciudad][1]);
                            var options = {
                              zoom: 13,
                              center: latlng,
                              mapTypeId: google.maps.MapTypeId.ROADMAP
                            };
                            map_%(name)s = new google.maps.Map(document.getElementById("map_%(name)s"), options);
                            geocoder = new google.maps.Geocoder();


                            point = new google.maps.LatLng(%(lat)f, %(lng)f);
                            marker = new google.maps.Marker({
                                position: point,
                                map: map_%(name)s,
                                draggable: true
                            });


                            google.maps.event.addListener(marker, "dragend", function() {
                                if (autodiscover){
                                    geocoder.geocode({'latLng': marker.getPosition()}, addAddressToMap);
                                }
                                else{
                                    point = marker.getPosition();
                                    savePosition_%(name)s(point);
                                }
                            });
			}
		//]]>
		</script>
        ''' % dict(name=name, lat=lat, lng=lng)
        html = self.inner_widget.render("%s" % name, "%f,%f" % (lat,lng), dict(id='id_%s' % name))
        html += "<div id=\"map_%s\" style=\"width: 450px; height: 400px\"></div>" % name
        return (js+html)


class LocationField(forms.Field):
    widget = LocationWidget

    def clean(self, value):
        a, b = value.split(',')
        lat, lng = float(a), float(b)
        return (lat, lng)
