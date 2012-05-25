function load_index() {
  load_data("/messaging/","messaging");
  }

function load_contacts() {
  load_data("/messaging/contacts/","messaging_contacts");
  }

function pop_contacts(mode) {
  var main=document.getElementById("messaging_contacts");
  if (mode=="off") {
    main.style.height="auto";
    load_index(); 
    }
  else {
    load_contacts();
    update_display('<a href="javascript:pop_contacts('+"'off'"+')"><img class="icon" src="/site_media/icons/group.gif" title="Contacts" alt="Contacts" /></a>','messaging_contacts_icon');
    }
  }

function add_contact(contact_id) {
  load_data('/messaging/contacts/'+contact_id+'/add/','messaging_contacts');
  }

function remove_contact(contact_id) {
  load_data('/messaging/contacts/'+contact_id+'/remove/','messaging_contacts')
  }

function load_msg_list(mode) {
  var img='<img class="icon" src="/site_media/messaging/icons/pm.gif" alt="" title="Messages" />';
  var url_close_msg='<a href="javascript:load_msg_list('+"'off'"+')">'+img+'</a>';
  var url_open_msg='<a href="javascript:load_msg_list('+"'on'"+')">'+img+'</a>';
  if (mode=='on') {
    var url='/messaging/load_msgs_list/';
    load_data(url,'messaging_contacts');
    update_display(url_close_msg,'messages_icon');
    load_nummsg();
    }
  else {
    load_index();
    }
  }

function send_pm(userid) {
  var url="/messaging/send_pm/"+userid+'/';
  load_data(url,'messaging_contacts');
  load_nummsg();
  }

function delete_pm(pmid,noload) {
   var url="/messaging/delete_message/"+pmid+'/';
   load_data(url,'messaging_contacts');
   if (noload==undefined) {
     load_nummsg();
     load_msg_list('on');
     }
  /* else {
    alert(noload);
    }*/
  }

function post_pm(userid,pm) {
   url="/messaging/post_pm/"+userid+"/?pm="+pm;
   load_data(url,'messaging');
  }

function load_nummsg() {
   url='/messaging/load_num_msgs/';
   load_data(url,'messaging_num_msgs');
  }

function read_pm(pmid) {
   url='/messaging/read_pm/'+pmid+'/';
   load_data(url,'messaging_contacts');
   load_nummsg();
  }

function read_first_pm() {
   url='/messaging/read_first_pm/';
   load_data(url,'messaging_contacts');
   load_nummsg();
  }
