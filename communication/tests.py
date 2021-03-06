# coding: utf-8

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from auth.models import Learner
from communication.models import Ban, ChatMessage, CoursePostRel, Message, MessageStatus, Profanity, Post, PostComment,\
    PostCommentLike, Report, ReportResponse, SmsQueue
from communication.utils import contains_profanity, report_user_post, get_user_bans, get_replacement_content, \
    JunebugApi
from content.models import TestingQuestion
from core.models import Class, Participant
from organisation.models import Course, CourseModuleRel, Module, Organisation, School


def create_course(name="course name", **kwargs):
    return Course.objects.create(name=name, **kwargs)


def create_module(name, course, **kwargs):
    module = Module.objects.create(name=name, **kwargs)
    rel = CourseModuleRel.objects.create(course=course, module=module)
    module.save()
    rel.save()
    return module


def create_class(name, course, **kwargs):
    return Class.objects.create(name=name, course=course, **kwargs)


def create_organisation(name='organisation name', **kwargs):
    return Organisation.objects.create(name=name, **kwargs)


def create_school(name, organisation, **kwargs):
    return School.objects.create(
        name=name, organisation=organisation, **kwargs)


def create_learner(school, **kwargs):
    if 'country' not in kwargs:
        kwargs['country'] = '+27123456789'
    if 'grade' not in kwargs:
        kwargs['grade'] = 'Grade 11'
    if 'mobile' not in kwargs:
        kwargs['mobile'] = '+27123456789'
    if 'username' not in kwargs:
        kwargs['username'] = kwargs['mobile']
    return Learner.objects.create(school=school, **kwargs)


def create_participant(learner, classs, **kwargs):
    participant = Participant.objects.create(
        learner=learner, classs=classs, **kwargs)
    return participant


class TestMessage(TestCase):

    # As you write more tests you'll probably find that you'd want to
    # add these utility functions to a helper class that you can then
    # reuse in different test cases

    def create_course(self, name="course name", **kwargs):
        return Course.objects.create(name=name, **kwargs)

    def create_class(self, course, name='class name', **kwargs):
        return Class.objects.create(name=name, course=course, **kwargs)

    def create_user(self, mobile="+27123456789", country="country", **kwargs):
        model_class = get_user_model()
        return model_class.objects.create(
            mobile=mobile, country=country, **kwargs)

    def create_message(self, author, course, **kwargs):
        return Message.objects.create(author=author, course=course, **kwargs)

    def setUp(self):
        self.course = self.create_course()
        self.classs = self.create_class(self.course)
        self.user = self.create_user()

    def test_get_messages(self):
        # unused
        dt1 = datetime.now()
        dt2 = dt1 - timedelta(minutes=5)
        dt3 = dt2 - timedelta(minutes=5)
        dt4 = dt1 + timedelta(minutes=5)

        msg1 = self.create_message(
            self.user,
            self.course,
            name="msg1",
            publishdate=dt3
        )
        msg2 = self.create_message(
            self.user,
            self.course,
            name="msg2",
            publishdate=dt2
        )
        msg3 = self.create_message(
            self.user,
            self.course,
            name="msg3",
            publishdate=dt1
        )
        msg4 = self.create_message(
            self.user,
            self.course,
            name="msg4",
            publishdate=dt4
        )
        # should return the most recent two in descending order of publish date
        self.assertEqual(
            [msg3, msg2], Message.get_messages(self.user, self.course, 2))
        #should return 3, 4th is not published yet
        self.assertEqual(
            [msg3, msg2, msg1], Message.get_messages(self.user, self.course, 4))

    def test_unread_msg_count(self):
        msg = self.create_message(
            self.user,
            self.course,
            name="msg2",
            publishdate=datetime.now()
        )
        msg2 = self.create_message(
            self.user,
            self.course,
            name="msg3",
            publishdate=datetime.now()
        )
        # should return 2 unread messages
        self.assertEqual(
            2, Message.unread_message_count(self.user, self.course))

    def test_view_message(self):
        msg = self.create_message(
            self.user,
            self.course,
            name="msg2",
            publishdate=datetime.now()
        )

        _status = MessageStatus.objects.create(message=msg, user=self.user)

        # view status is False
        self.assertFalse(_status.view_status)

        msg.view_message(self.user)
        msg.save()

        _status = MessageStatus.objects.get(message=msg)

        # view status is True
        self.assertTrue(_status.view_status)

    def test_hide_message(self):
        msg = self.create_message(
            self.user,
            self.course,
            name="msg",
            publishdate=datetime.now()
        )

        hide_status = MessageStatus.objects.create(message=msg, user=self.user)

        # hide status is False
        self.assertFalse(hide_status.hidden_status)

        msg.hide_message(self.user)
        msg.save()

        hide_status = MessageStatus.objects.get(message=msg)
        # hide status is True
        self.assertTrue(hide_status.hidden_status)


class TestChatMessage(TestCase):
    def create_chat_message(self, content="", **kwargs):
        return ChatMessage.objects.create(content=content, **kwargs)

    def test_created_message(self):
        msg = self.create_chat_message(content="Ò")
        self.assertEqual(msg.content, 'Ò', "They are not equal")


class TestSmsQueue(TestCase):
    def create_smsqueue(self, **kwargs):
        return SmsQueue.objects.create(**kwargs)

    def test_created_smsqueue(self):
        sms_queue1 = self.create_smsqueue(msisdn="+27721472583", send_date=datetime.now(), message="Message")

        self.assertEqual(sms_queue1.message, "Message", "Message text not the same")


class TestReport(TestCase):
    def create_user(self, _mobile="+27123456789", _country="country", **kwargs):
        model_class = get_user_model()
        return model_class.objects.create(mobile=_mobile, country=_country, **kwargs)

    def create_course(self, _name="course name", **kwargs):
        return Course.objects.create(name=_name, **kwargs)

    def create_module(self, _course, _name="module name", **kwargs):
        module = Module.objects.create(name=_name, **kwargs)
        rel = CourseModuleRel.objects.create(course=_course, module=module)
        module.save()
        rel.save()
        return module

    def create_question(self, _module, _name="question name", _q_content="2+2", _a_content="4", **kwargs):
        return TestingQuestion.objects.create(name=_name, module=_module, question_content=_q_content,
                                              answer_content=_a_content, **kwargs)

    def setUp(self):
        self.user = self.create_user()
        self.course = self.create_course()
        self.module = self.create_module(self.course)
        self.question = self.create_question(self.module)

    def create_report(self, _issue, _fix, **kwargs):
        return Report.objects.create(user=self.user,
                                     question=self.question,
                                     issue=_issue,
                                     fix=_fix,
                                     **kwargs)

    def test_created_report(self):
        report = self.create_report("There is an error.", "The answer should be 10.")

        self.assertEquals(report.issue, "There is an error.", "They are not equal")
        self.assertEquals(report.fix, "The answer should be 10.", "They are not equal")
        self.assertEquals(report.question.name, "question name", "They are not equal")

        self.assertIsNone(report.response, "Response should be None")

        #create response to report
        report.create_response("Title", "Question updated.")

        self.assertIsNotNone(report.response, "Response doesn't exist")
        self.assertEquals(report.response.title, "Title", "They are not equal")
        self.assertEquals(report.response.content, "Question updated.", "They are not equal")


class TestReportResponse(TestCase):
    def create_report_response(self, _title, _content, **kwargs):
        return ReportResponse.objects.create(title=_title,
                                             content=_content,
                                             **kwargs)

    def test_created_report_response(self):
        response = self.create_report_response("title", "content")

        self.assertEquals(response.title, "title", "They are not equal")
        self.assertEquals(response.content, "content", "They are equal")


class TestBan(TestCase):
    def create_user(self, mobile="+27123456789", country="country", **kwargs):
        model_class = get_user_model()
        return model_class.objects.create(
            mobile=mobile, country=country, **kwargs)

    def create_chat_message(self, content="Test", **kwargs):
        return ChatMessage.objects.create(content=content, **kwargs)

    def create_ban(self, till_when):
        return Ban.objects.create(
            banned_user=self.user,
            banning_user=self.user2,
            when=datetime.now(),
            till_when=till_when,
            source_type=1,
            source_pk=1
        )

    def setUp(self):
        self.user = self.create_user()
        self.user2 = self.create_user(mobile='123123', username='123123')

    def test_ban_duration(self):
        today = datetime.now()
        today = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)
        b1tw = today
        b2tw = today + timedelta(days=2)

        ban1 = self.create_ban(b1tw)
        self.assertEquals(ban1.get_duration(), 1)
        ban1.delete()

        ban2 = self.create_ban(b2tw)
        self.assertEquals(ban2.get_duration(), 3)

    def test_report_user_post(self):
        chat = self.create_chat_message(author=self.user)
        report_user_post(obj=chat, banning_user=self.user2, num_days=1)
        self.assertEquals(chat.unmoderated_by.id, self.user2.pk)
        qs = get_user_bans(user=self.user)
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first().get_duration(), 1)

    def test_report_user_post_more_days(self):
        chat = self.create_chat_message(author=self.user)
        report_user_post(obj=chat, banning_user=self.user2, num_days=7)
        self.assertEquals(chat.unmoderated_by.id, self.user2.pk)
        qs = get_user_bans(user=self.user)
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first().get_duration(), 7)

    def test_multi_ban(self):
        chat = self.create_chat_message(author=self.user)
        report_user_post(obj=chat, banning_user=self.user2, num_days=1)
        report_user_post(obj=chat, banning_user=self.user2, num_days=1)
        report_user_post(obj=chat, banning_user=self.user2, num_days=1)
        cnt = Ban.objects.filter(banned_user=self.user).count()
        self.assertEquals(cnt, 1)
        report_user_post(obj=chat, banning_user=self.user2, num_days=3)
        cnt = Ban.objects.filter(banned_user=self.user).count()
        self.assertEquals(cnt, 2)

    def test_replacement_content_admin(self):
        exp_admin = 'This comment has been reported by a moderator and the user has ' \
                    'been banned from commenting for 5 days.'
        act = get_replacement_content(admin_ban=True, num_days=5)
        self.assertEquals(exp_admin, act)

        exp_admin = 'This comment has been reported by a moderator and the user has ' \
                    'been banned from commenting for 1 day.'
        act = get_replacement_content(admin_ban=True, num_days=1)
        self.assertEquals(exp_admin, act)

    def test_replacement_content_community(self):
        exp_com = 'This comment has been reported by the community and the user has ' \
                  'been banned from commenting for 7 days.'
        act = get_replacement_content(admin_ban=False, num_days=7)
        self.assertEquals(exp_com, act)

        exp_com = 'This comment has been reported by the community and the user has ' \
                  'been banned from commenting for 1 day.'
        act = get_replacement_content(admin_ban=False, num_days=1)
        self.assertEquals(exp_com, act)

    def test_replacement_content_profanity(self):
        exp_com = "This comment includes a banned word so has been removed."
        act = get_replacement_content(profanity=True)
        self.assertEquals(exp_com, act)


class TestProfanity(TestCase):
    def test_profanity(self):
        Profanity.objects.create(
            word='test'
        )

        self.assertEquals(contains_profanity('foo bar'), False)
        self.assertEquals(contains_profanity('test testees testing'), True)
        self.assertEquals(contains_profanity('Test testees testing'), True)
        self.assertEquals(contains_profanity('TeSt testees TesTing'), True)
        self.assertEquals(contains_profanity('test TesTees testing'), True)
        self.assertEquals(contains_profanity('test'), True)
        self.assertEquals(contains_profanity('test!'), True)
        self.assertEquals(contains_profanity('test, test'), True)
        self.assertEquals(contains_profanity(' test'), True)
        self.assertEquals(contains_profanity('\"test\"'), True)
        self.assertEquals(contains_profanity('test?'), True)
        self.assertEquals(contains_profanity(',test'), True)


class TestSms(TestCase):
    def test_send_sms(self):
        settings.__setattr__("JUNEBUG_FAKE", True)
        api = JunebugApi()
        sms, sent = api.send("+27715597770", "test", None, None)

        self.assertIsNotNone(sms)
        self.assertEquals(sent, True)
        self.assertEquals(sms.message, "test")


class TestLikes(TestCase):
    def setUp(self):
        self.organisation = Organisation.objects.get(name='One Plus')
        self.school = create_school('Death Dome', self.organisation)
        for i in xrange(5):
            create_learner(
                self.school,
                username="+2712345{0:04d}".format(i),
                mobile="+2712345{0:04d}".format(i),
                country="country",
                area="Test_Area",
                unique_token='abc{0:03d}'.format(i),
                unique_token_expiry=datetime.now() + timedelta(days=30),
                is_staff=True)
        self.learners = Learner.objects.all()
        self.course = create_course('Hunger Games')
        self.classs = create_class('District 12', self.course)
        self.participant = create_participant(
            self.learners[0], self.classs, datejoined=datetime(2014, 7, 18, 1, 1))
        self.post = Post.objects.create(name="Blog Post", publishdate=timezone.now())
        CoursePostRel.objects.create(course=self.course, post=self.post)

    def test_post_like(self):
        comment = PostComment.objects.create(author=self.learners[0], post=self.post, publishdate=timezone.now())
        self.assertEqual(PostCommentLike.objects.all().count(), 0)
        PostCommentLike.like(self.learners[0], comment)
        self.assertEqual(PostCommentLike.objects.all().count(), 1)

    def test_post_like_twice(self):
        comment = PostComment.objects.create(author=self.learners[0], post=self.post, publishdate=timezone.now())
        self.assertEqual(PostCommentLike.objects.all().count(), 0)
        PostCommentLike.like(self.learners[0], comment)
        self.assertEqual(PostCommentLike.objects.all().count(), 1)
        PostCommentLike.like(self.learners[0], comment)
        self.assertEqual(PostCommentLike.objects.all().count(), 1)

    def test_post_unlike(self):
        comment = PostComment.objects.create(author=self.learners[0], post=self.post, publishdate=timezone.now())
        self.assertEqual(PostCommentLike.objects.all().count(), 0)
        PostCommentLike.like(self.learners[0], comment)
        self.assertEqual(PostCommentLike.objects.all().count(), 1)
        PostCommentLike.unlike(self.learners[0], comment)
        self.assertEqual(PostCommentLike.objects.all().count(), 0)

    def test_post_like_count(self):
        comment = PostComment.objects.create(author=self.learners[0], post=self.post, publishdate=timezone.now())
        self.assertEqual(PostCommentLike.count_likes(comment), 0)
        PostCommentLike.like(self.learners[0], comment)
        self.assertEqual(PostCommentLike.count_likes(comment), 1)
        PostCommentLike.like(self.learners[1], comment)
        self.assertEqual(PostCommentLike.count_likes(comment), 2)
        PostCommentLike.unlike(self.learners[1], comment)
        self.assertEqual(PostCommentLike.count_likes(comment), 1)
