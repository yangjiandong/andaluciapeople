# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Tipo'
        db.create_table('sitios_tipo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('sitios', ['Tipo'])

        # Adding model 'Sitio'
        db.create_table('sitios_sitio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('direccion', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('zona', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ciudad', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('lng', self.gf('django.db.models.fields.FloatField')()),
            ('telefono', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('web', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('lastfm', self.gf('django.db.models.fields.IntegerField')(max_length=8, null=True, blank=True)),
            ('patrocinado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rank', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('num_votos', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('fecha', self.gf('django.db.models.fields.DateTimeField')()),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('cerrado', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('traslado', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('cambio_nombre', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
            ('incorrecto', self.gf('django.db.models.fields.NullBooleanField')(default=False, null=True, blank=True)),
        ))
        db.send_create_signal('sitios', ['Sitio'])

        # Adding unique constraint on 'Sitio', fields ['slug', 'ciudad']
        db.create_unique('sitios_sitio', ['slug', 'ciudad'])

        # Adding M2M table for field tipo on 'Sitio'
        db.create_table('sitios_sitio_tipo', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sitio', models.ForeignKey(orm['sitios.sitio'], null=False)),
            ('tipo', models.ForeignKey(orm['sitios.tipo'], null=False))
        ))
        db.create_unique('sitios_sitio_tipo', ['sitio_id', 'tipo_id'])

        # Adding model 'SitioPatrocinado'
        db.create_table('sitios_sitiopatrocinado', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sitio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Sitio'], unique=True)),
            ('descripcion', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('imagen', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('icono', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('precio', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('fecha_inicio', self.gf('django.db.models.fields.DateField')()),
            ('fecha_fin', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('sitios', ['SitioPatrocinado'])

        # Adding model 'SitioNochevieja'
        db.create_table('sitios_sitionochevieja', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sitio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Sitio'], unique=True)),
            ('precio', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('info', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('imagen', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('sitios', ['SitioNochevieja'])

        # Adding model 'Jerarquia'
        db.create_table('sitios_jerarquia', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32, db_index=True)),
        ))
        db.send_create_signal('sitios', ['Jerarquia'])

        # Adding model 'Etiqueta'
        db.create_table('sitios_etiqueta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32, db_index=True)),
            ('padre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Jerarquia'], null=True, blank=True)),
        ))
        db.send_create_signal('sitios', ['Etiqueta'])

        # Adding model 'ObjetoEtiquetado'
        db.create_table('sitios_objetoetiquetado', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Etiqueta'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('sitio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Sitio'])),
            ('fecha', self.gf('django.db.models.fields.DateTimeField')()),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('sitios', ['ObjetoEtiquetado'])

        # Adding unique constraint on 'ObjetoEtiquetado', fields ['tag', 'user', 'sitio']
        db.create_unique('sitios_objetoetiquetado', ['tag_id', 'user_id', 'sitio_id'])

        # Adding model 'Voto'
        db.create_table('sitios_voto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('sitio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Sitio'])),
            ('valoracion', self.gf('django.db.models.fields.FloatField')()),
            ('fecha', self.gf('django.db.models.fields.DateTimeField')()),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('sitios', ['Voto'])

        # Adding unique constraint on 'Voto', fields ['user', 'sitio']
        db.create_unique('sitios_voto', ['user_id', 'sitio_id'])

        # Adding model 'Comentario'
        db.create_table('sitios_comentario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('sitio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Sitio'])),
            ('mensaje', self.gf('django.db.models.fields.TextField')()),
            ('fecha', self.gf('django.db.models.fields.DateTimeField')()),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('sitios', ['Comentario'])

        # Adding model 'Foto'
        db.create_table('sitios_foto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('sitio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Sitio'])),
            ('foto', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('fecha', self.gf('django.db.models.fields.DateTimeField')()),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('flickr', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sitios', ['Foto'])

        # Adding model 'DatosUsuario'
        db.create_table('sitios_datosusuario', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], primary_key=True)),
            ('web', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('imagen', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('boletin', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sexo', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('nacimiento', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('notificaciones', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('idioma', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('puntos', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('sitios', ['DatosUsuario'])

        # Adding M2M table for field favoritos on 'DatosUsuario'
        db.create_table('sitios_datosusuario_favoritos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datosusuario', models.ForeignKey(orm['sitios.datosusuario'], null=False)),
            ('sitio', models.ForeignKey(orm['sitios.sitio'], null=False))
        ))
        db.create_unique('sitios_datosusuario_favoritos', ['datosusuario_id', 'sitio_id'])

        # Adding M2M table for field gustos on 'DatosUsuario'
        db.create_table('sitios_datosusuario_gustos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datosusuario', models.ForeignKey(orm['sitios.datosusuario'], null=False)),
            ('etiqueta', models.ForeignKey(orm['sitios.etiqueta'], null=False))
        ))
        db.create_unique('sitios_datosusuario_gustos', ['datosusuario_id', 'etiqueta_id'])

        # Adding model 'PesosTipoJerarquia'
        db.create_table('sitios_pesostipojerarquia', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('tipo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Tipo'])),
            ('jerarquia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sitios.Jerarquia'])),
            ('peso', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('sitios', ['PesosTipoJerarquia'])

        # Adding unique constraint on 'PesosTipoJerarquia', fields ['user', 'tipo', 'jerarquia']
        db.create_unique('sitios_pesostipojerarquia', ['user_id', 'tipo_id', 'jerarquia_id'])

        # Adding model 'Amigo'
        db.create_table('sitios_amigo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from', to=orm['auth.User'])),
            ('friend', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to', to=orm['auth.User'])),
        ))
        db.send_create_signal('sitios', ['Amigo'])

        # Adding unique constraint on 'Amigo', fields ['user', 'friend']
        db.create_unique('sitios_amigo', ['user_id', 'friend_id'])

        # Adding model 'Invitacion'
        db.create_table('sitios_invitacion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('enviada', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('codigo', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('aceptada', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sitios', ['Invitacion'])

        # Adding model 'Banner'
        db.create_table('sitios_banner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('img', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('alt', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('posicion', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('ciudad', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('activo', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sitios', ['Banner'])


    def backwards(self, orm):

        # Removing unique constraint on 'Amigo', fields ['user', 'friend']
        db.delete_unique('sitios_amigo', ['user_id', 'friend_id'])

        # Removing unique constraint on 'PesosTipoJerarquia', fields ['user', 'tipo', 'jerarquia']
        db.delete_unique('sitios_pesostipojerarquia', ['user_id', 'tipo_id', 'jerarquia_id'])

        # Removing unique constraint on 'Voto', fields ['user', 'sitio']
        db.delete_unique('sitios_voto', ['user_id', 'sitio_id'])

        # Removing unique constraint on 'ObjetoEtiquetado', fields ['tag', 'user', 'sitio']
        db.delete_unique('sitios_objetoetiquetado', ['tag_id', 'user_id', 'sitio_id'])

        # Removing unique constraint on 'Sitio', fields ['slug', 'ciudad']
        db.delete_unique('sitios_sitio', ['slug', 'ciudad'])

        # Deleting model 'Tipo'
        db.delete_table('sitios_tipo')

        # Deleting model 'Sitio'
        db.delete_table('sitios_sitio')

        # Removing M2M table for field tipo on 'Sitio'
        db.delete_table('sitios_sitio_tipo')

        # Deleting model 'SitioPatrocinado'
        db.delete_table('sitios_sitiopatrocinado')

        # Deleting model 'SitioNochevieja'
        db.delete_table('sitios_sitionochevieja')

        # Deleting model 'Jerarquia'
        db.delete_table('sitios_jerarquia')

        # Deleting model 'Etiqueta'
        db.delete_table('sitios_etiqueta')

        # Deleting model 'ObjetoEtiquetado'
        db.delete_table('sitios_objetoetiquetado')

        # Deleting model 'Voto'
        db.delete_table('sitios_voto')

        # Deleting model 'Comentario'
        db.delete_table('sitios_comentario')

        # Deleting model 'Foto'
        db.delete_table('sitios_foto')

        # Deleting model 'DatosUsuario'
        db.delete_table('sitios_datosusuario')

        # Removing M2M table for field favoritos on 'DatosUsuario'
        db.delete_table('sitios_datosusuario_favoritos')

        # Removing M2M table for field gustos on 'DatosUsuario'
        db.delete_table('sitios_datosusuario_gustos')

        # Deleting model 'PesosTipoJerarquia'
        db.delete_table('sitios_pesostipojerarquia')

        # Deleting model 'Amigo'
        db.delete_table('sitios_amigo')

        # Deleting model 'Invitacion'
        db.delete_table('sitios_invitacion')

        # Deleting model 'Banner'
        db.delete_table('sitios_banner')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sitios.amigo': {
            'Meta': {'unique_together': "(('user', 'friend'),)", 'object_name': 'Amigo'},
            'friend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from'", 'to': "orm['auth.User']"})
        },
        'sitios.banner': {
            'Meta': {'object_name': 'Banner'},
            'activo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'alt': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'ciudad': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'posicion': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'sitios.comentario': {
            'Meta': {'object_name': 'Comentario'},
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mensaje': ('django.db.models.fields.TextField', [], {}),
            'sitio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Sitio']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sitios.datosusuario': {
            'Meta': {'object_name': 'DatosUsuario'},
            'boletin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'favoritos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sitios.Sitio']", 'null': 'True', 'blank': 'True'}),
            'gustos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sitios.Etiqueta']", 'null': 'True', 'blank': 'True'}),
            'idioma': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'imagen': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'nacimiento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'notificaciones': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'puntos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'primary_key': 'True'}),
            'web': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'sitios.etiqueta': {
            'Meta': {'object_name': 'Etiqueta'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'padre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Jerarquia']", 'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'})
        },
        'sitios.foto': {
            'Meta': {'object_name': 'Foto'},
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'flickr': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'foto': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'sitio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Sitio']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sitios.invitacion': {
            'Meta': {'object_name': 'Invitacion'},
            'aceptada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'enviada': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'sitios.jerarquia': {
            'Meta': {'object_name': 'Jerarquia'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'})
        },
        'sitios.objetoetiquetado': {
            'Meta': {'unique_together': "(('tag', 'user', 'sitio'),)", 'object_name': 'ObjetoEtiquetado'},
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'sitio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Sitio']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Etiqueta']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sitios.pesostipojerarquia': {
            'Meta': {'unique_together': "(('user', 'tipo', 'jerarquia'),)", 'object_name': 'PesosTipoJerarquia'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jerarquia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Jerarquia']"}),
            'peso': ('django.db.models.fields.FloatField', [], {}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Tipo']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sitios.sitio': {
            'Meta': {'ordering': "('nombre',)", 'unique_together': "(('slug', 'ciudad'),)", 'object_name': 'Sitio'},
            'cambio_nombre': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'cerrado': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'ciudad': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incorrecto': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'lastfm': ('django.db.models.fields.IntegerField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lng': ('django.db.models.fields.FloatField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'num_votos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'patrocinado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rank': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'telefono': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sitios.Tipo']", 'symmetrical': 'False'}),
            'traslado': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'web': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zona': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sitios.sitionochevieja': {
            'Meta': {'object_name': 'SitioNochevieja'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagen': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'precio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sitio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Sitio']", 'unique': 'True'})
        },
        'sitios.sitiopatrocinado': {
            'Meta': {'ordering': "('sitio',)", 'object_name': 'SitioPatrocinado'},
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fecha_fin': ('django.db.models.fields.DateField', [], {}),
            'fecha_inicio': ('django.db.models.fields.DateField', [], {}),
            'icono': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagen': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'precio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sitio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Sitio']", 'unique': 'True'})
        },
        'sitios.tipo': {
            'Meta': {'ordering': "('tipo',)", 'object_name': 'Tipo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'sitios.voto': {
            'Meta': {'unique_together': "(('user', 'sitio'),)", 'object_name': 'Voto'},
            'fecha': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'sitio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sitios.Sitio']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'valoracion': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['sitios']
