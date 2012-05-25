	maxWidth = 300;
	minWidth = 55;	
	lastBlock.css('width', maxWidth+"px");
	
	$("ul.menu_user li a").hover(function(){
		$(lastBlock).animate({width: minWidth+"px"}, { queue:false, duration:400 });
		$(this).animate({width: maxWidth+"px"}, { queue:false, duration:400});
		lastBlock = this;
	});
