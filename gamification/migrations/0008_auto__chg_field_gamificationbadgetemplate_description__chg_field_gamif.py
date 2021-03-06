# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'GamificationBadgeTemplate.description'
        db.alter_column(u'gamification_gamificationbadgetemplate', 'description', self.gf('django.db.models.fields.CharField')(max_length=500))

        # Changing field 'GamificationBadgeTemplate.name'
        db.alter_column(u'gamification_gamificationbadgetemplate', 'name', self.gf('django.db.models.fields.CharField')(max_length=500, unique=True, null=True))

        # Changing field 'GamificationScenario.description'
        db.alter_column(u'gamification_gamificationscenario', 'description', self.gf('django.db.models.fields.CharField')(max_length=500))

        # Changing field 'GamificationScenario.event'
        db.alter_column(u'gamification_gamificationscenario', 'event', self.gf('django.db.models.fields.CharField')(max_length=500))

        # Changing field 'GamificationScenario.name'
        db.alter_column(u'gamification_gamificationscenario', 'name', self.gf('django.db.models.fields.CharField')(max_length=500, unique=True, null=True))

        # Changing field 'GamificationPointBonus.name'
        db.alter_column(u'gamification_gamificationpointbonus', 'name', self.gf('django.db.models.fields.CharField')(max_length=500, unique=True, null=True))

        # Changing field 'GamificationPointBonus.description'
        db.alter_column(u'gamification_gamificationpointbonus', 'description', self.gf('django.db.models.fields.CharField')(max_length=500))

    def backwards(self, orm):

        # Changing field 'GamificationBadgeTemplate.description'
        db.alter_column(u'gamification_gamificationbadgetemplate', 'description', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'GamificationBadgeTemplate.name'
        db.alter_column(u'gamification_gamificationbadgetemplate', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True))

        # Changing field 'GamificationScenario.description'
        db.alter_column(u'gamification_gamificationscenario', 'description', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'GamificationScenario.event'
        db.alter_column(u'gamification_gamificationscenario', 'event', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'GamificationScenario.name'
        db.alter_column(u'gamification_gamificationscenario', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True))

        # Changing field 'GamificationPointBonus.name'
        db.alter_column(u'gamification_gamificationpointbonus', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True))

        # Changing field 'GamificationPointBonus.description'
        db.alter_column(u'gamification_gamificationpointbonus', 'description', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        u'gamification.gamificationbadgetemplate': {
            'Meta': {'object_name': 'GamificationBadgeTemplate'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'})
        },
        u'gamification.gamificationpointbonus': {
            'Meta': {'object_name': 'GamificationPointBonus'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'value': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'gamification.gamificationscenario': {
            'Meta': {'object_name': 'GamificationScenario'},
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationBadgeTemplate']", 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Course']", 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Module']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationPointBonus']", 'null': 'True', 'blank': 'True'})
        },
        u'organisation.course': {
            'Meta': {'object_name': 'Course'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'organisation.module': {
            'Meta': {'object_name': 'Module'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Course']", 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True'})
        }
    }

    complete_apps = ['gamification']