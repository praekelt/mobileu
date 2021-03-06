# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UnprocessedSchools'
        db.create_table(u'core_unprocessedschools', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('learner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Learner'], null=True)),
            ('province', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('suggested_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('is_completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['UnprocessedSchools'])


    def backwards(self, orm):
        # Deleting model 'UnprocessedSchools'
        db.delete_table(u'core_unprocessedschools')


    models = {
        u'auth.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'optin_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'optin_sms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pass_reset_token': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'pass_reset_token_expiry': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'unique_token': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'unique_token_expiry': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.learner': {
            'Meta': {'object_name': 'Learner', '_ormbases': [u'auth.CustomUser']},
            u'customuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.CustomUser']", 'unique': 'True', 'primary_key': 'True'}),
            'enrolled': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'blank': 'True'}),
            'grade': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'last_active_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_maths_result': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.School']", 'null': 'True'}),
            'welcome_message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communication.Sms']", 'null': 'True', 'blank': 'True'}),
            'welcome_message_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.teacher': {
            'Meta': {'object_name': 'Teacher', '_ormbases': [u'auth.CustomUser']},
            u'customuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.CustomUser']", 'unique': 'True', 'primary_key': 'True'}),
            'last_active_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.School']", 'null': 'True'}),
            'welcome_message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communication.Sms']", 'null': 'True', 'blank': 'True'}),
            'welcome_message_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'communication.sms': {
            'Meta': {'object_name': 'Sms'},
            'date_sent': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'msisdn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'respond_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'responded': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'response': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['communication.SmsQueue']", 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        u'communication.smsqueue': {
            'Meta': {'object_name': 'SmsQueue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'msisdn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'send_date': ('django.db.models.fields.DateTimeField', [], {}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'content.testingquestion': {
            'Meta': {'ordering': "['name']", 'object_name': 'TestingQuestion'},
            'answer_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Module']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Auto Generated'", 'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'question_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'textbook_link': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'content.testingquestionoption': {
            'Meta': {'object_name': 'TestingQuestionOption'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'correct': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Auto Generated'", 'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.TestingQuestion']", 'null': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.badgeawardlog': {
            'Meta': {'object_name': 'BadgeAwardLog'},
            'award_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant_badge_rel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.ParticipantBadgeTemplateRel']", 'null': 'True'})
        },
        u'core.class': {
            'Meta': {'object_name': 'Class'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Course']", 'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'enddate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'startdate': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'core.participant': {
            'Meta': {'object_name': 'Participant'},
            'badgetemplate': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['gamification.GamificationBadgeTemplate']", 'symmetrical': 'False', 'through': u"orm['core.ParticipantBadgeTemplateRel']", 'blank': 'True'}),
            'classs': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Class']"}),
            'datejoined': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'learner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Learner']"}),
            'pointbonus': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['gamification.GamificationPointBonus']", 'symmetrical': 'False', 'through': u"orm['core.ParticipantPointBonusRel']", 'blank': 'True'}),
            'points': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'core.participantbadgetemplaterel': {
            'Meta': {'object_name': 'ParticipantBadgeTemplateRel'},
            'awardcount': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'awarddate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 10, 13, 0, 0)', 'null': 'True'}),
            'badgetemplate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationBadgeTemplate']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Participant']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationScenario']"})
        },
        u'core.participantpointbonusrel': {
            'Meta': {'object_name': 'ParticipantPointBonusRel'},
            'awarddate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 10, 13, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Participant']"}),
            'pointbonus': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationPointBonus']"}),
            'scenario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationScenario']"})
        },
        u'core.participantquestionanswer': {
            'Meta': {'object_name': 'ParticipantQuestionAnswer'},
            'answerdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 10, 13, 0, 0)', 'null': 'True', 'db_index': 'True'}),
            'correct': ('django.db.models.fields.BooleanField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option_selected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.TestingQuestionOption']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Participant']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.TestingQuestion']"})
        },
        u'core.participantredoquestionanswer': {
            'Meta': {'object_name': 'ParticipantRedoQuestionAnswer'},
            'answerdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2016, 10, 13, 0, 0)', 'null': 'True'}),
            'correct': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option_selected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.TestingQuestionOption']"}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Participant']"}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['content.TestingQuestion']"})
        },
        u'core.setting': {
            'Meta': {'object_name': 'Setting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'value': ('django.db.models.fields.TextField', [], {'max_length': '100'})
        },
        u'core.teacherclass': {
            'Meta': {'object_name': 'TeacherClass'},
            'classs': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Class']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Teacher']"})
        },
        u'core.unprocessedschools': {
            'Meta': {'object_name': 'UnprocessedSchools'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'learner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Learner']", 'null': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'suggested_name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'gamification.gamificationbadgetemplate': {
            'Meta': {'object_name': 'GamificationBadgeTemplate'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'award_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationBadgeTemplate']", 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Course']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Module']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gamification.GamificationPointBonus']", 'null': 'True', 'blank': 'True'})
        },
        u'organisation.course': {
            'Meta': {'object_name': 'Course'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'question_order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'organisation.coursemodulerel': {
            'Meta': {'object_name': 'CourseModuleRel'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Course']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Module']"})
        },
        u'organisation.module': {
            'Meta': {'object_name': 'Module'},
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'modules'", 'symmetrical': 'False', 'through': u"orm['organisation.CourseModuleRel']", 'to': u"orm['organisation.Course']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'module_link': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'organisation.organisation': {
            'Meta': {'object_name': 'Organisation'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'organisation.school': {
            'Meta': {'object_name': 'School'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True', 'null': 'True'}),
            'open_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['organisation.Organisation']", 'null': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['core']