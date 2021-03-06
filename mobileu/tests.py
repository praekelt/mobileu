# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test.client import Client
from django.utils import timezone
from utils import format_option, format_content
from communication.models import ChatMessage, Discussion, PostComment, ChatGroup, Post, CoursePostRel
from organisation.models import Course, Organisation
from auth.models import CustomUser
from datetime import datetime, timedelta
import math
from mock import Mock, patch, mock_open, call, ANY, DEFAULT
import mobileu.teacher_report as teacher_report
from mobileu.tasks import grade_up_body
from core.models import Class, Teacher, TeacherClass, TestingQuestion, TestingQuestionOption, Learner, Participant, \
    ParticipantQuestionAnswer
from organisation.models import Course, CourseModuleRel, Module, School
from settings import GRADE_10_COURSE_NAME, GRADE_11_COURSE_NAME, GRADE_12_COURSE_NAME


def create_course(name="course name", **kwargs):
    return Course.objects.create(name=name, **kwargs)


def create_class(name, course, **kwargs):
    return Class.objects.create(name=name, course=course, **kwargs)


def create_module(name, course, **kwargs):
    module = Module.objects.create(name=name, **kwargs)
    rel = CourseModuleRel.objects.create(course=course, module=module)
    module.save()
    rel.save()
    return module


def create_organisation(name='organisation name', **kwargs):
    return Organisation.objects.create(name=name, **kwargs)


def create_test_question(name, module, **kwargs):
    return TestingQuestion.objects.create(name=name, module=module, **kwargs)


def create_test_question_option(name, question, correct=True):
    return TestingQuestionOption.objects.create(
        name=name, question=question, correct=correct)


def create_school(name, organisation, **kwargs):
    return School.objects.create(
        name=name,
        organisation=organisation,
        **kwargs)


def create_learner(school, **kwargs):
    return Learner.objects.create(school=school, **kwargs)


def create_participant(learner, classs, datejoined=timezone.now(), **kwargs):
    return Participant.objects.create(
        learner=learner,
        classs=classs,
        datejoined=datejoined,
        **kwargs)


class TestContent(TestCase):

    def test_strip_p_tags(self):
        content = "<p><b>Test</b></p>"
        result = format_content(content)
        self.assertEquals(result, "<div><b>Test</b><br/></div>")

    def test_align_image_only(self):
        content = "<img/>"
        result = format_option(content)
        self.assertEquals(result, u'<img style="vertical-align:middle"/>')

    def test_format_option_text_only(self):
        content = "Test"
        result = format_option(content)
        self.assertEquals(result, u'Test')

    def test_format_option_text_and_image(self):
        content = "<b>Test</b><img/>"
        result = format_option(content)
        self.assertEquals(result, u'<b>Test</b><img style='
                                  u'"vertical-align:middle"/>')

    def test_format_option_double_image(self):
        content = "<img/><img/>"
        result = format_option(content)
        self.assertEquals(result, u'<img style="vertical-align:middle"/>'
                                  u'<img style="vertical-align:middle"/>')

    def test_format_option(self):
        content = "<b>Test</b><p></p><img/>"
        output = format_option(content)
        self.assertEquals(output, u'<b>Test</b><br/><img style="'
                                  u'vertical-align:middle"/>')

    def test_format_content(self):
        content = '<img style="width:300px"/>'
        result = format_content(content)
        self.assertEquals(result, u'<div><img style="width:100%;'
                                  u'vertical-align:middle"/></div>')

    def test_already_format_content(self):
        content = '<img style="width:100%"/>'
        result = format_content(content)
        self.assertEquals(result, u'<div><img style="width:100%;'
                                  u'vertical-align:middle"/></div>')

    def test_format_content_small_image(self):
        content = '<img style="width:60px"/>'
        result = format_content(content)
        self.assertEquals(result, u'<div><img style="width:60px;'
                                  u'vertical-align:middle"/></div>')

    def test_filters_empty(self):
        content = ""
        output = format_content(content)
        self.assertEquals(output, u'<div></div>')

    def test_filters_empty_option(self):
        content = ""
        output = format_option(content)
        self.assertEquals(output, u'')

    def test_unicode_input(self):
        content = u'Zoë'
        output = format_option(content)
        self.assertEquals(output, u'Zoë')


class TestPublishViews(TestCase):

    def create_user(self, mobile="+27123456789", country="country", **kwargs):
        model_class = get_user_model()
        return model_class.objects.create(
            mobile=mobile, country=country, **kwargs)

    def create_chatgroup(self, name='TestGroup', description='TestGroup'):
        return ChatGroup.objects.create(
            name=name,
            description=description
        )

    def create_chatmessage(self, content):
        return ChatMessage.objects.create(
            chatgroup=self.chatgroup,
            author=self.user,
            content=content,
            publishdate=datetime.now()
        )

    def create_discussion(self, content, name='Test', description='Test'):
        return Discussion.objects.create(
            name=name,
            description=description,
            content=content,
            author=self.user,
            publishdate=datetime.now()
        )

    def create_course(self, name='Test', description='Test', slug='Test'):
        return Course.objects.create(
            name=name,
            description=description,
            slug=slug
        )

    def create_post(self, content, name='Test', description='Test'):
        post = Post.objects.create(
            name=name,
            description=description,
            content=content,
            publishdate=datetime.now()
        )
        CoursePostRel.objects.create(course=self.course, post=post)

        return post

    def create_postcomment(self, post, content):
        return PostComment.objects.create(
            post=post,
            content=content,
            author=self.user,
            publishdate=datetime.now()
        )

    def setUp(self):
        self.user = self.create_user()
        self.chatgroup = self.create_chatgroup()
        self.course = self.create_course()
        self.post = self.create_post('Test Test Test Test')
        self.admin_user_password = 'mypassword'
        self.admin_user = CustomUser.objects.create_superuser(
            username='asdf33',
            email='asdf33@example.com',
            password=self.admin_user_password,
            mobile='+27111111133')

    def test_chatmessage_publish_unpublish(self):
        cm = self.create_chatmessage('Test Test test')

        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        base_url = '/admin/communication/chatmessage/publish/'

        url = base_url + '10000'
        resp = c.get(url)
        self.assertContains(resp, 'Can''t find record')

        url = base_url + str(cm.pk)
        resp = c.get(url)
        self.assertContains(resp, 'ChatMessage has been published')

        cm = ChatMessage.objects.get(pk=cm.pk)
        self.assertEquals(cm.moderated, True)

        base_url = '/admin/communication/chatmessage/unpublish/'
        url = base_url + '10000'
        resp = c.get(url)
        self.assertContains(resp, 'Can''t find record')

        url = base_url + str(cm.pk)
        resp = c.get(url)
        self.assertContains(resp, 'ChatMessage has been unpublished')

        cm = ChatMessage.objects.get(pk=cm.pk)
        self.assertEquals(cm.moderated, False)
        self.assertEquals(cm.unmoderated_by.username, self.admin_user.username)
        self.assertIsNotNone(cm.unmoderated_date)

    def test_discussion_publish_unpublish(self):
        d = self.create_discussion('Test Test test')

        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        base_url = '/admin/communication/discussion/publish/'

        url = base_url + '10000'
        resp = c.get(url)
        self.assertContains(resp, 'Can''t find record')

        url = base_url + str(d.pk)
        resp = c.get(url)
        self.assertContains(resp, 'Discussion has been published')

        d = Discussion.objects.get(pk=d.pk)
        self.assertEquals(d.moderated, True)

        base_url = '/admin/communication/discussion/unpublish/'
        url = base_url + '10000'
        resp = c.get(url)
        self.assertContains(resp, 'Can''t find record')

        url = base_url + str(d.pk)
        resp = c.get(url)
        self.assertContains(resp, 'Discussion has been unpublished')

        d = Discussion.objects.get(pk=d.pk)
        self.assertEquals(d.moderated, False)
        self.assertEquals(d.unmoderated_by.username, self.admin_user.username)
        self.assertIsNotNone(d.unmoderated_date)

    def test_postcomment_publish_unpublish(self):
        pc = self.create_postcomment(self.post, 'Test Test test')

        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        base_url = '/admin/communication/postcomment/publish/'

        url = base_url + '10000'
        resp = c.get(url)
        self.assertContains(resp, 'Can''t find record')

        url = base_url + str(pc.pk)
        resp = c.get(url)
        self.assertContains(resp, 'PostComment has been published')

        pc = PostComment.objects.get(pk=pc.pk)
        self.assertEquals(pc.moderated, True)

        base_url = '/admin/communication/postcomment/unpublish/'
        url = base_url + '10000'
        resp = c.get(url)
        self.assertContains(resp, 'Can''t find record')

        url = base_url + str(pc.pk)
        resp = c.get(url)
        self.assertContains(resp, 'PostComment has been unpublished')

        pc = PostComment.objects.get(pk=pc.pk)
        self.assertEquals(pc.moderated, False)
        self.assertEquals(pc.unmoderated_by.username, self.admin_user.username)
        self.assertIsNotNone(pc.unmoderated_date)


class AdminSiteTests(TestCase):

    def setUp(self):
        self.admin_user_password = 'mypassword'
        self.admin_user = CustomUser.objects.create_superuser(
            username='asdf33',
            email='asdf33@example.com',
            password=self.admin_user_password,
            mobile='+27111111133')

    def admin_page_test_helper(self, c, url):
        resp = c.get(url)
        self.assertEquals(resp.status_code, 200)

    def test_auth_admin_pages_render(self):
        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        self.admin_page_test_helper(c, "/admin/")

        self.admin_page_test_helper(c, "/admin/auth/")
        self.admin_page_test_helper(c, "/admin/auth/coursemanager/")
        self.admin_page_test_helper(c, "/admin/auth/coursemanager/add/")
        self.admin_page_test_helper(c, "/admin/auth/coursementor/")
        self.admin_page_test_helper(c, "/admin/auth/coursementor/add/")
        self.admin_page_test_helper(c, "/admin/auth/group/")
        self.admin_page_test_helper(c, "/admin/auth/group/add/")
        self.admin_page_test_helper(c, "/admin/auth/learner/")
        self.admin_page_test_helper(c, "/admin/auth/learner/add/")
        self.admin_page_test_helper(c, "/admin/auth/teacher/")
        self.admin_page_test_helper(c, "/admin/auth/teacher/add/")
        self.admin_page_test_helper(c, "/admin/auth/schoolmanager/")
        self.admin_page_test_helper(c, "/admin/auth/schoolmanager/add/")
        self.admin_page_test_helper(c, "/admin/auth/systemadministrator/")
        self.admin_page_test_helper(c, "/admin/auth/systemadministrator/add/")

    def test_communication_admin_pages_render(self):
        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        self.admin_page_test_helper(c, "/admin/communication/")
        self.admin_page_test_helper(c, "/admin/communication/ban/")
        self.admin_page_test_helper(c, "/admin/communication/ban/add/")
        self.admin_page_test_helper(c, "/admin/communication/chatgroup/")
        self.admin_page_test_helper(c, "/admin/communication/chatgroup/add/")
        self.admin_page_test_helper(c, "/admin/communication/chatmessage/")
        self.admin_page_test_helper(c, "/admin/communication/chatmessage/add/")
        self.admin_page_test_helper(c, "/admin/communication/discussion/")
        self.admin_page_test_helper(c, "/admin/communication/discussion/add/")
        self.admin_page_test_helper(c, "/admin/communication/message/")
        self.admin_page_test_helper(c, "/admin/communication/message/add/")
        self.admin_page_test_helper(c, "/admin/communication/moderation/")
        self.admin_page_test_helper(c, "/admin/communication/postcomment/")
        self.admin_page_test_helper(c, "/admin/communication/postcomment/add/")
        self.admin_page_test_helper(c, "/admin/communication/post/")
        self.admin_page_test_helper(c, "/admin/communication/post/add/")
        self.admin_page_test_helper(c, "/admin/communication/smsqueue/")
        self.admin_page_test_helper(c, "/admin/communication/smsqueue/add/")
        self.admin_page_test_helper(c, "/admin/communication/reportresponse/")
        self.admin_page_test_helper(c, "/admin/communication/reportresponse/add/")
        self.admin_page_test_helper(c, "/admin/communication/report/")
        self.admin_page_test_helper(c, "/admin/communication/report/add/")
        self.admin_page_test_helper(c, "/admin/communication/sms/")
        self.admin_page_test_helper(c, "/admin/communication/sms/add/")

    def test_content_admin_pages_render(self):
        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        self.admin_page_test_helper(c, "/admin/content/")
        self.admin_page_test_helper(c, "/admin/content/definition/")
        self.admin_page_test_helper(c, "/admin/content/definition/add/")
        self.admin_page_test_helper(c, "/admin/content/eventparticipantrel/")
        self.admin_page_test_helper(c, "/admin/content/eventparticipantrel/add/")
        self.admin_page_test_helper(c, "/admin/content/eventquestionanswer/")
        self.admin_page_test_helper(c, "/admin/content/eventquestionanswer/add/")
        self.admin_page_test_helper(c, "/admin/content/eventquestionrel/")
        self.admin_page_test_helper(c, "/admin/content/eventquestionrel/add/")
        self.admin_page_test_helper(c, "/admin/content/event/")
        self.admin_page_test_helper(c, "/admin/content/event/add/")
        self.admin_page_test_helper(c, "/admin/content/goldeneggrewardlog/")
        self.admin_page_test_helper(c, "/admin/content/goldeneggrewardlog/add/")
        self.admin_page_test_helper(c, "/admin/content/goldenegg/")
        self.admin_page_test_helper(c, "/admin/content/goldenegg/add/")
        self.admin_page_test_helper(c, "/admin/content/learningchapter/")
        self.admin_page_test_helper(c, "/admin/content/learningchapter/add/")
        self.admin_page_test_helper(c, "/admin/content/mathml/")
        self.admin_page_test_helper(c, "/admin/content/mathml/add/")
        self.admin_page_test_helper(c, "/admin/content/testingquestionoption/")
        self.admin_page_test_helper(c, "/admin/content/testingquestionoption/add/")
        self.admin_page_test_helper(c, "/admin/content/sumit/")
        self.admin_page_test_helper(c, "/admin/content/sumit/add/")
        self.admin_page_test_helper(c, "/admin/content/sumitlevel/")
        self.admin_page_test_helper(c, "/admin/content/testingquestion/")
        self.admin_page_test_helper(c, "/admin/content/testingquestion/add/")
        self.admin_page_test_helper(c, "/admin/content/testingquestiondifficulty/")
        self.admin_page_test_helper(c, "/admin/content/testingquestiondifficulty/add/")

    def test_core_admin_pages_render(self):
        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        self.admin_page_test_helper(c, "/admin/core/")
        self.admin_page_test_helper(c, "/admin/core/class/")
        self.admin_page_test_helper(c, "/admin/core/class/add/")
        self.admin_page_test_helper(c, "/admin/core/participantquestionanswer/")
        self.admin_page_test_helper(c, "/admin/core/participantquestionanswer/add/")
        self.admin_page_test_helper(c, "/admin/core/participant/")
        self.admin_page_test_helper(c, "/admin/core/participant/add/")
        self.admin_page_test_helper(c, "/admin/core/setting/")
        self.admin_page_test_helper(c, "/admin/core/setting/add/")
        self.admin_page_test_helper(c, "/admin/core/badgeawardlog/")

    def test_gamification_admin_pages_render(self):
        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        self.admin_page_test_helper(c, "/admin/gamification/")
        self.admin_page_test_helper(c, "/admin/gamification/gamificationbadgetemplate/")
        self.admin_page_test_helper(c, "/admin/gamification/gamificationbadgetemplate/add/")
        self.admin_page_test_helper(c, "/admin/gamification/gamificationpointbonus/")
        self.admin_page_test_helper(c, "/admin/gamification/gamificationpointbonus/add/")
        self.admin_page_test_helper(c, "/admin/gamification/gamificationscenario/")
        self.admin_page_test_helper(c, "/admin/gamification/gamificationscenario/add/")

    def test_organisation_admin_pages_render(self):
        c = Client()
        c.login(username=self.admin_user.username, password=self.admin_user_password)

        self.admin_page_test_helper(c, "/admin/organisation/")
        self.admin_page_test_helper(c, "/admin/organisation/course/")
        self.admin_page_test_helper(c, "/admin/organisation/course/add/")
        self.admin_page_test_helper(c, "/admin/organisation/module/")
        self.admin_page_test_helper(c, "/admin/organisation/module/add/")
        self.admin_page_test_helper(c, "/admin/organisation/organisation/")
        self.admin_page_test_helper(c, "/admin/organisation/organisation/add/")
        self.admin_page_test_helper(c, "/admin/organisation/school/")
        self.admin_page_test_helper(c, "/admin/organisation/school/add/")


class TestTeacherReport(TestCase):
    def generate_questions(self, module, num_questions, num_options):
        questions = []
        options = []
        for i in range(num_questions):
            q = TestingQuestion.objects.create(name='Q%d' % (i,),
                                               order=i,
                                               module=module,
                                               question_content='This is Q%d' % (i,),
                                               difficulty=TestingQuestion.DIFF_EASY,
                                               state=TestingQuestion.PUBLISHED)
            questions.append(q)
            for j in range(num_options):
                o = TestingQuestionOption.objects.create(
                    question=q,
                    name='Q%dA%d' % (i, j),
                    order=j,
                    content='This is Q%dA%d' % (i, j),
                    correct=True if j == 0 else False)
                options.append(o)
        return {'questions': questions, 'options': options}

    def generate_participant(self, school, classs, first_name='Anon', last_name='Ymous',
                             username='5556667777', mobile='5556667777', datejoined=datetime.now()):
        learner = Learner.objects.create(first_name=first_name, last_name=last_name,
                                         username=username, mobile=mobile, school=school)
        participant = Participant.objects.create(learner=learner,
                                                 classs=classs,
                                                 datejoined=datejoined)
        return participant

    def generate_class(self, course_name='Test_Course', module_name='Test_Module',
                       school_name='Test_School', class_name='Test_Class'):
        try:
            course = Course.objects.get(name=course_name)
        except Course.DoesNotExist:
            course = Course.objects.create(name=course_name)
        try:
            module = Module.objects.get(name=module_name)
        except Module.DoesNotExist:
            module = Module.objects.create(name=module_name)
        try:
            rel = CourseModuleRel.objects.get(course=course, module=module)
        except CourseModuleRel.DoesNotExist:
            rel = CourseModuleRel.objects.create(course=course, module=module)
        try:
            school = School.objects.get(name=school_name)
        except School.DoesNotExist:
            school = School.objects.create(name=school_name)
        try:
            classs = Class.objects.get(name=class_name, course=course)
        except Class.DoesNotExist:
            classs = Class.objects.create(name=class_name, course=course)
        return {'course': course, 'module': module, 'school': school, 'class': classs}

    def answer_questions_roundrobin(self, participant, questions, num_options, lastmonth):
        num_correct = 0
        for i in range(len(questions)):
            q = questions[i]
            selected_option = TestingQuestionOption.objects.get(question=q, order=i % num_options)
            if selected_option.correct:
                num_correct += 1
            qr = ParticipantQuestionAnswer.objects.create(
                participant=participant,
                question=q,
                option_selected=selected_option,
                correct=selected_option.correct,
                answerdate=lastmonth+timedelta(hours=i/3*24))
        return num_correct

    def test_safe_sheet_name(self):
        normal = teacher_report.make_safe_sheet_name('ThisIsMyName')
        self.assertEqual(
            normal,
            'ThisIsMyName',
            'Long name should be truncated to "ThisIsMyName", got %s' % (normal,))
        truncated = teacher_report.make_safe_sheet_name('ThisIsAReallyLongSheetNameThatNeverSeemsToEnd')
        self.assertEqual(
            truncated,
            'ThisIsAReallyLongSheetNameThatN',
            'Long name should be truncated to "ThisIsAReallyLongSheetNameThatN", got %s' % (truncated,))

    def test_get_teacher_list(self):
        self.assertListEqual(list(teacher_report.get_teacher_list()), list(), 'Teacher list not empty')
        class_details = self.generate_class()
        teacher = Teacher.objects.create(first_name='Anon', last_name='Ymousteach',
                                         username='Iamafunteacher', mobile='1234567890',
                                         school=class_details['school'], email='aymous@school.com')
        teach_class = TeacherClass.objects.create(classs=class_details['class'], teacher=teacher)
        teach_list = teacher_report.get_teacher_list()
        self.assertListEqual(list(teach_list), [teacher.pk],
                             'Teacher list should contain one item, got %s' % (teach_list,))
        teacher2 = Teacher.objects.create(first_name='Anon', last_name='Ymousity',
                                          username='Iamafunteachertoo', mobile='9876543210',
                                          school=class_details['school'], email='anonmouse@school.com')
        teach_class2 = TeacherClass.objects.create(classs=class_details['class'], teacher=teacher2)
        teach_list = teacher_report.get_teacher_list()
        self.assertListEqual(sorted(list(teach_list)), sorted([teacher.pk, teacher2.pk]),
                             'Teacher list should contain two items, got %s' % (teach_list,))

    def test_process_participant(self):
        today = datetime.now()
        lastmonth = (today.replace(day=1) - timedelta(days=-1)).replace(day=1)
        class_details = self.generate_class()
        participant = self.generate_participant(school=class_details['school'], classs=class_details['class'],
                                                datejoined=today-timedelta(days=14))
        num_questions = 15
        num_options = 2
        q_and_a = self.generate_questions(class_details['module'], num_questions, num_options)
        num_correct = self.answer_questions_roundrobin(participant, q_and_a['questions'], num_options, lastmonth)
        processed = teacher_report.process_participant(participant, lastmonth)
        self.assertEqual(processed[0], 'Anon')
        self.assertEqual(processed[1], num_questions)
        self.assertAlmostEqual(processed[2], math.floor(100*num_correct/num_questions), 0)
        self.assertEqual(processed[3], num_questions)
        self.assertAlmostEqual(processed[4], math.floor(100*num_correct/num_questions), 0)

    def test_process_module(self):
        today = datetime.today()
        lastmonth = (today.replace(day=1) - timedelta(days=-1)).replace(day=1)
        num_learners = 10
        class_details = self.generate_class()
        participants = []
        for i in range(num_learners):
            mobile = '08251232%02d' % i
            participant = self.generate_participant(school=class_details['school'], classs=class_details['class'],
                                                    first_name='Anon%d' % (i,), username=mobile, mobile=mobile,
                                                    datejoined=today-timedelta(days=14))
            participants.append(participant)
        num_questions = 15
        num_options = 2
        q_and_a = self.generate_questions(class_details['module'], num_questions, num_options)
        num_correct = 0
        for p in participants:
            num_correct += self.answer_questions_roundrobin(p, q_and_a['questions'], num_options, lastmonth)
        correct_percentage = 100 * num_correct/num_learners/num_questions
        processed = teacher_report.process_module(class_details['module'], lastmonth)
        self.assertTupleEqual(processed, (class_details['module'].name, correct_percentage, correct_percentage))

    def test_write_class_list(self):
        learners_per_class = 10
        num_questions = 15
        class_report_name = 'Test_Class_Report'
        class_list = []
        current_class = Mock()
        current_class.name.return_value = 'Test_Class'
        for i in range(learners_per_class):
            correct_percent = i * 100 / learners_per_class
            class_list.append(['Learner %d' % (i,), num_questions, correct_percent, num_questions, correct_percent])
        failed_reports = []
        fake_open = mock_open()
        with patch('__builtin__.open', fake_open, create=True):
            teacher_report.write_class_list(class_report_name, class_list, current_class, failed_reports)
        self.assertListEqual(fake_open.call_args_list,
                             [call('Test_Class_Report.csv', 'wb'), call('Test_Class_Report.xls', 'w+b')],
                             'Didn\'t open both *.csv and *.xls files for report')
        self.assertGreater(
            fake_open().write.call_count,
            learners_per_class + 1,
            msg='Number of writes too low, should be more than %d, got %d' % (learners_per_class + 1,
                                                                              fake_open().write.call_count))
        csv_writes = fake_open().write.call_args_list[1:learners_per_class + 1]
        for i in range(learners_per_class):
            correct_percent = i * 100 / learners_per_class
            self.assertRegexpMatches(
                csv_writes[i][0][0],
                'Learner %d,%d,%d,%d,%d' % (i, num_questions, correct_percent, num_questions, correct_percent))

    def test_write_module_list(self):
        num_modules = 10
        module_report_name = 'Test_Module_Report'
        module_list = []
        current_class = Mock()
        current_class.name.return_value = 'Test_Class'
        for i in range(num_modules):
            correct_percent = i * 100 / num_modules
            module_list.append(['Module %d' % (i,), correct_percent, correct_percent + 1])
        failed_reports = []
        fake_open = mock_open()
        with patch('__builtin__.open', fake_open, create=True):
            teacher_report.write_module_list(module_report_name, current_class, module_list, failed_reports)
        self.assertListEqual(fake_open.call_args_list,
                             [call('Test_Module_Report.csv', 'wb'), call('Test_Module_Report.xls', 'w+b')],
                             'Didn\'t open both *.csv and *.xls files for report')
        self.assertGreater(
            fake_open().write.call_count,
            num_modules + 1,
            msg='Number of writes too low, should be more than %d, got %d' % (num_modules + 1,
                                                                              fake_open().write.call_count))
        csv_writes = fake_open().write.call_args_list[1:num_modules + 1]
        for i in range(num_modules):
            correct_percent = i * 100 / num_modules
            self.assertRegexpMatches(csv_writes[i][0][0],
                                     'Module %d,%d,%d' % (i, correct_percent, correct_percent + 1))

    @patch('mobileu.teacher_report.log', autospec=True)
    @patch('mobileu.teacher_report.EmailMessage', autospec=True)
    def test_email_teacher(self, fake_mail, fake_log):
        subject = 'Teacher report mails'
        message = 'Here are your teacher reports'
        from_email = 'local@dig-it.me'
        current_teacher = {'id': 1, 'email': 'teach@school.com', 'username': 'teach'}
        all_teachers_list = []
        failed_email_reports = []

        # test normal mailing
        new_teacher_obj = {'id': 1,
                           'email': 'teach@school.com',
                           'csv_class_reports': ['Class report 1.csv'],
                           'csv_module_reports': ['Module report 1.csv'],
                           'xls_class_reports': ['Class report 1.xls'],
                           'xls_module_reports': ['Module report 1.xls']}
        all_teachers_list.append(new_teacher_obj)
        teacher_report.email_teacher(subject, message, from_email, current_teacher,
                                     all_teachers_list, failed_email_reports)
        self.assertEqual(fake_mail().attach_file.call_count, 4)
        self.assertTrue(fake_mail().send.called)

        # test failed file attachment
        fake_mail.reset_mock()
        fake_log.reset_mock()
        fake_mail().attach_file.side_effect = Exception
        teacher_report.email_teacher(subject, message, from_email, current_teacher,
                                     all_teachers_list, failed_email_reports)
        fake_log.assert_has_calls([
            call(ANY, False), call(ANY, False), call(ANY, False), call(ANY, False)
        ])
        fake_mail().attach_file.side_effect = None

        # test failed sending
        fake_mail.reset_mock()
        fake_log.reset_mock()
        fake_mail().send.side_effect = Exception
        teacher_report.email_teacher(subject, message, from_email, current_teacher,
                                     all_teachers_list, failed_email_reports)
        fake_log.assert_has_calls([call(ANY, False)])
        self.assertEqual(len(failed_email_reports), 1)
        self.assertEqual(failed_email_reports[0][0], current_teacher['username'])
        self.assertEqual(failed_email_reports[0][1], current_teacher['email'])
        fake_mail().send.side_effect = None

        # test multiple non-matching teachers
        fake_mail.reset_mock()
        fake_log.reset_mock()
        failed_email_reports = []
        all_teachers_list.insert(0, {'id': 2})
        all_teachers_list.insert(0, {'id': 3})
        all_teachers_list.append({'id': 4})
        teacher_report.email_teacher(subject, message, from_email, current_teacher,
                                     all_teachers_list, failed_email_reports)
        self.assertEqual(fake_mail().attach_file.call_count, 4)
        self.assertTrue(fake_mail().send.called)
        fake_log.assert_called_once_with(ANY, current_teacher["email"])

    def test_send_teacher_reports_body(self):
        num_classes = 3
        teachers_per_class = 5
        learners_per_class = 10
        questions_answered = 15
        classes = []
        teachers = []
        participants = []
        for i in range(num_classes):
            class_details = self.generate_class(class_name='Class%d' % i)
            classes.append(class_details)
            for j in range(teachers_per_class):
                teacher = teacher = Teacher.objects.create(first_name='C%dTeacher%d' % (i, j,),
                                                           last_name='C%dMcLastnamey%d' % (i, j,),
                                                           username='c%dteacher%d' % (i, j,),
                                                           mobile='12345%03d%03d' % (i, j,),
                                                           school=class_details['school'],
                                                           email='c%dteacher%d@school.com' % (i, j))
                teach_class = TeacherClass.objects.create(classs=class_details['class'], teacher=teacher)
                teachers.append(teacher)
            for j in range(learners_per_class):
                participant = self.generate_participant(class_details['school'],
                                                        class_details['class'],
                                                        first_name='C%dLearner%d' % (i, j,),
                                                        last_name='C%dMcLastnamey%d' % (i, j,),
                                                        username='54321%03d%03d' % (i, j,),
                                                        mobile='54321%03d%03d' % (i, j,))
                participants.append(participant)

        modules = list(Module.objects.all())

        def mock_get_teacher_list():
            return [teacher.id for teacher in teachers]

        mock_process_participant_list = [
            (participants[i].learner.first_name,
             math.floor(questions_answered * i / len(participants)),
             math.floor(100 * i / len(participants)),
             math.floor(questions_answered * i / len(participants)),
             math.floor(100 * i / len(participants)))
            for i in range(len(participants))]
        module_idx = 0

        def mock_process_module_list(*args, **kwargs):
            result = (modules[module_idx].name,
                      math.floor(100 * module_idx / len(modules)),
                      math.floor(100 * module_idx / len(modules)))
            self.module_idx = (module_idx + 1) % len(modules)
            return result

        def mock_email_teachers_fail_some(subject, message, from_email, teacher, all_teachers_list, failed_emails):
            if (teacher['id'] % num_classes) == 0:
                failed_emails.append((teacher['username'], teacher['email'], 'Failed %s' % (teacher['username'],)))

        def reset_mocks(patches):
            self.module_idx = 0
            for _, value in patches.items():
                value.reset_mock()
            patches['process_participant'].side_effect = iter(mock_process_participant_list)

        with patch.multiple('mobileu.teacher_report',
                            autospec=True,
                            create=True,
                            settings=DEFAULT,
                            mail_managers=DEFAULT,
                            log=DEFAULT,
                            process_participant=DEFAULT,
                            process_module=DEFAULT,
                            get_teacher_list=DEFAULT,
                            write_class_list=DEFAULT,
                            write_module_list=DEFAULT,
                            email_teacher=DEFAULT) as patches:
            patches['settings'].MEDIA_ROOT = '/MROOT/'
            patches['get_teacher_list'].return_value = mock_get_teacher_list()
            patches['process_participant'].side_effect = iter(mock_process_participant_list)
            patches['process_module'].side_effect = mock_process_module_list
            failed_teachers = [teacher.username for teacher in teachers if ((teacher.id % num_classes) == 0)]

            # test basic case
            teacher_report.send_teacher_reports_body()
            self.assertEqual(patches['email_teacher'].call_count, num_classes*teachers_per_class)

            # test teacher e-mails failed
            reset_mocks(patches)
            patches['email_teacher'].side_effect = mock_email_teachers_fail_some
            teacher_report.send_teacher_reports_body()
            self.assertEqual(patches['mail_managers'].call_count, 1)
            fail_teach_args, fail_teach_kwargs = patches['mail_managers'].call_args
            for teacher in failed_teachers:
                self.assertRegexpMatches(fail_teach_args[1], '%s' % (teacher,))

            # test managers e-mail failed
            reset_mocks(patches)
            patches['mail_managers'].side_effect = Exception
            teacher_report.send_teacher_reports_body()
            failed_teachers = [teacher.username for teacher in teachers if ((teacher.id % num_classes) == 0)]
            self.assertEqual(patches['mail_managers'].call_count, 1)
            patches['log'].assert_has_calls([call('Sending failed emails email'), call(ANY, False)])


class TestGradeUp(TestCase):
    def setUp(self):
        gr10_course = create_course(GRADE_10_COURSE_NAME)
        gr11_course = create_course(GRADE_11_COURSE_NAME)
        gr12_course = create_course(GRADE_12_COURSE_NAME)
        self.module = create_module('module name', gr10_course)
        self.classs = create_class('class name', gr10_course)
        self.organisation = create_organisation()
        self.school = create_school('school name', self.organisation)

    def test_grade_up(self):
        learner = create_learner(school=self.school, grade=Learner.GR_10)
        participant = create_participant(learner, self.classs)
        self.assertEqual(Learner.objects.filter(grade=Learner.GR_10).count(), 1)
        self.assertEqual(Learner.objects.filter(grade=Learner.GR_11).count(), 0)
        self.assertEqual(Learner.objects.filter(grade=Learner.GR_12).count(), 0)

        # test whether learner moves up correctly from Gr 10
        grade_up_body()
        gr_10_count = Learner.objects.filter(grade=Learner.GR_10).count()
        self.assertEqual(gr_10_count, 0, 'Should have 0 Gr 10 learners, got %d' % (gr_10_count,))
        gr_11_count = Learner.objects.filter(grade=Learner.GR_11).count()
        self.assertEqual(gr_11_count, 1, 'Should have 1 Gr 11 learners, got %d' % (gr_11_count,))
        gr_12_count = Learner.objects.filter(grade=Learner.GR_12).count()
        self.assertEqual(gr_12_count, 0, 'Should have 0 Gr 12 learners, got %d' % (gr_10_count,))
        grad_count = Learner.objects.filter(grade=Learner.GR_GRAD).count()
        self.assertEqual(grad_count, 0, 'Should have 0 graduates, got %d' % (grad_count,))
        old_participant = Participant.objects.get(id=participant.id)
        self.assertFalse(old_participant.is_active, "Old participant should be inactive")

        # test whether learner moves up correctly from Gr 11
        grade_up_body()
        gr_10_count = Learner.objects.filter(grade=Learner.GR_10).count()
        self.assertEqual(gr_10_count, 0, 'Should have 0 Gr 10 learners, got %d' % (gr_10_count,))
        gr_11_count = Learner.objects.filter(grade=Learner.GR_11).count()
        self.assertEqual(gr_11_count, 0, 'Should have 0 Gr 11 learners, got %d' % (gr_11_count,))
        gr_12_count = Learner.objects.filter(grade=Learner.GR_12).count()
        self.assertEqual(gr_12_count, 1, 'Should have 1 Gr 12 learners, got %d' % (gr_12_count,))
        grad_count = Learner.objects.filter(grade=Learner.GR_GRAD).count()
        self.assertEqual(grad_count, 0, 'Should have 0 graduates, got %d' % (grad_count,))

        # test whether number of active participants is correct
        old_partcipant_count = Participant.objects.filter(is_active=True, learner__grade=Learner.GR_10).count()
        self.assertEqual(old_partcipant_count, 0, 'Should have 0 active participants, got %d' % (old_partcipant_count,))
        new_partcipant_count = Participant.objects.filter(is_active=True, learner__grade=Learner.GR_12).count()
        self.assertEqual(new_partcipant_count, 1, 'Should have 1 active participant, got %d' % (new_partcipant_count,))

        # test whether learner moves up correctly from Gr 12
        grade_up_body()
        gr_10_count = Learner.objects.filter(grade=Learner.GR_10).count()
        self.assertEqual(gr_10_count, 0, 'Should have 0 Gr 10 learners, got %d' % (gr_10_count,))
        gr_11_count = Learner.objects.filter(grade=Learner.GR_11).count()
        self.assertEqual(gr_11_count, 0, 'Should have 0 Gr 11 learners, got %d' % (gr_11_count,))
        gr_12_count = Learner.objects.filter(grade=Learner.GR_12).count()
        self.assertEqual(gr_12_count, 0, 'Should have 0 Gr 12 learners, got %d' % (gr_12_count,))
        grad_count = Learner.objects.filter(grade=Learner.GR_GRAD).count()
        self.assertEqual(grad_count, 1, 'Should have 1 graduates, got %d' % (grad_count,))
