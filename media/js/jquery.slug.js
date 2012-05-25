//
//	jQuery Slug Generation Plugin by Perry Trinier (perrytrinier@gmail.com)
//  Licensed under the GPL: http://www.gnu.org/copyleft/gpl.html

jQuery.fn.slug = function(options) {
	var settings = {
		slug: 'slug', // Class used for slug destination input and span. The span is created on $(document).ready() 
		hide: true	 // Boolean - By default the slug input field is hidden, set to false to show the input field and hide the span. 
	};
	
	if(options) {
		jQuery.extend(settings, options);
	}
	
	$this = $(this);

	$(document).ready( function() {
		if (settings.hide) {
			$('input.' + settings.slug).after("<span class="+settings.slug+"></span>");
			$('input.' + settings.slug).hide();
		}
	});
	
	makeSlug = function() {
			var slugcontent = $this.val();
			var slugcontent_hyphens = slugcontent.replace(/\s/g,'+');
			var finishedslug = slugcontent_hyphens.replace(/[^a-záéíóúñA-ZÁÉÍÓÚÑ0-9\-\+]/g,'');
			finishedslug = finishedslug.replace(/á/g,'a');
			finishedslug = finishedslug.replace(/é/g,'e');
			finishedslug = finishedslug.replace(/í/g,'i');
			finishedslug = finishedslug.replace(/ó/g,'o');
			finishedslug = finishedslug.replace(/ú/g,'u');
			finishedslug = finishedslug.replace(/ñ/g,'n');
			$('input.' + settings.slug).val(finishedslug.toLowerCase());
			$('span.' + settings.slug).text(finishedslug.toLowerCase());

		}
		
	$(this).keyup(makeSlug);
		
	return $this;
};
