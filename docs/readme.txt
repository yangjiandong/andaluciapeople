django andaluciapeople
======================

2012.05.28
----------

   1. html dl tag

   <dl>
   <dt>Coffee</dt>
    <dd>- black hot drink</dd>
   <dt>Milk</dt>
    <dd>- white cold drink</dd>
   </dl>

   show:
Coffee
     - black hot drink
Milk
     - white cold drink

   2. 登录页面不出现

   (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'base_login.html'}),
   Site matching query does not exist

   https://groups.google.com/group/django-users/browse_thread/thread/6e0e6404596b1917/3959031e3d5f9709
   检查后台django_site记录，调整settings.SITE_ID

2012.05.25
----------

   1. http://andaluciapeople.com/

   http://andaluciapeople.com/media/releases/


   -- END