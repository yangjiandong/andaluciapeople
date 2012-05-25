function getHTTPObject(box_id)
/* Merci à http://openweb.eu.org/articles/objet_xmlhttprequest */
{
  var xmlhttp = false;

  /* Compilation conditionnelle d'IE */
  /*@cc_on
  @if (@_jscript_version >= 5)
     try
     {
        xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
     }
     catch (e)
     {
        try
        {
           xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        catch (E)
        {
           xmlhttp = false;
        }
     }
  @else
     xmlhttp = false;
  @end @*/

  /* on essaie de créer l'objet si ce n'est pas déjà fait */
  if (!xmlhttp && typeof XMLHttpRequest != 'undefined')
  {
     try
     {
        xmlhttp = new XMLHttpRequest();
     }
     catch (e)
     {
        xmlhttp = false;
     }
  }

  if (xmlhttp)
  {
     /* on définit ce qui doit se passer quand la page répondra */
     xmlhttp.onreadystatechange=function()
     {
        if (xmlhttp.readyState == 4) /* 4 : état "complete" */
        {
           if (xmlhttp.status == 200) /* 200 : code HTTP pour OK */
           {
              /* Traitement de la réponse. */
              update_display(xmlhttp.responseText,box_id);
           }
        }
     }
  }
  return xmlhttp;
}

function update_display(response,box_id) {
  /* alert('ok');
  alert(box_id); */
  box=document.getElementById(box_id);
  box.innerHTML=response;
  }

function cleanup(box_id) {
  document.getElementById(box_id).innerHTML="";
  }

function load_data(url,box_id) {
  /* Création de l'objet : */
  var xmlhttp = getHTTPObject(box_id); 
  /* Préparation d'une requête asynchrone de type GET : */
  xmlhttp.open("GET", url,true); 
  /* Effectue la requête : */
  xmlhttp.send(null); 
  }


