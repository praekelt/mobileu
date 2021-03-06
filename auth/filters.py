from datetime import datetime, timedelta
from django.db.models import Count
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from organisation.models import Course
from core.models import Participant, ParticipantQuestionAnswer, Class


def today():
    return datetime.now()


class CourseFilter(admin.SimpleListFilter):
    title = _('Course')
    parameter_name = 'id'

    def lookups(self, request, model_admin):
        return Course.objects.all().values_list('id', 'name')

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(participant__classs__course_id=self.value())


class ClassFilter(admin.SimpleListFilter):
    title = _('Class')
    parameter_name = 'cid'

    def lookups(self, request, model_admin):
        return Class.objects.all().values_list('id', 'name')

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(participant__classs_id=self.value())


class AirtimeFilter(admin.SimpleListFilter):
    title = _('Airtime')
    parameter_name = 'name'

    @staticmethod
    def get_date_range():
        date = today()
        start = date - timedelta(days=date.weekday(), weeks=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        return [start, end]

    def get_learner_ids(self):
        participants = ParticipantQuestionAnswer.objects.filter(
            answerdate__range=self.get_date_range(),
            correct=True
        ).values('participant').annotate(Count('participant'))

        filtered_participants = participants.filter(
            participant__count__gte=12
        ).values('participant')

        return Participant.objects.filter(
            id__in=filtered_participants
        ).values_list('learner', flat=True)

    def lookups(self, request, model_admin):
        return [('airtime_award', _('12 to 15 questions correct'))]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        else:
            if self.value() == 'airtime_award':
                learners = self.get_learner_ids()
                return queryset.filter(id__in=learners)
            else:
                return queryset
