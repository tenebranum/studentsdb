from ..models import Student, MonthJournal
from ..util import paginate, get_current_group
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from calendar import monthrange,weekday,day_abbr

from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.http import JsonResponse
import logging
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



class JournalView(TemplateView):
	template_name = 'students/journal.html'


	#@method_decorator(login_required)
	#def dispatch(self,*args,**kwargs):
	#	super(JournalView,self).dispatch(*args,**kwargs)


	def get_context_data(self,**kwargs):
		context = super(JournalView,self).get_context_data(**kwargs)


		if self.request.GET.get('month'):
			month = datetime.strptime(self.request.GET['month'], "%Y-%m-%d").date()

		else:
			today = datetime.today()
			month = date(today.year,today.month,1)


		next_month = month + relativedelta(months=1)
		prev_month = month - relativedelta(months=1)
		context['prev_month'] = prev_month.strftime('%Y-%m-%d')
		context['next_month'] = next_month.strftime('%Y-%m-%d')
		context['year'] = month.year
		context['cur_month'] = month.strftime('%Y-%m-%d')
		context['month_verbose'] = month.strftime('%B')

		
		number_of_days = monthrange(month.year,month.month)[1]

		context['month_header'] = [
		{'day':d,'verbose':day_abbr[weekday(month.year,month.month,d)][:3]}
		for d in range (1,number_of_days+1)]

		if kwargs['pk']:
			queryset=[Student.objects.get(pk=kwargs['pk'])]
		else:
			current_group = get_current_group(self.request)
			if current_group:
				queryset = Student.objects.filter(student_group=current_group).order_by('last_name')
			else:
				queryset = Student.objects.order_by('last_name')
		update_url = reverse('visitation')

		students = []
		for student in queryset:
			try:
				journal = MonthJournal.objects.get(student=student,date=month)
			except Exception:
				journal = None


			days = []
			for day in range(1,number_of_days+1):
				days.append({
					'day':day,
					'present':journal and getattr(journal,'present_day%d' %day, False) or False,#journal.days[day-1] or False,
					'date':date(month.year,month.month,day).strftime('%Y-%m-%d'),})

			students.append({
				'full_name':u'%s %s' % (student.last_name, student.first_name ),
				'days':days,
				'id':student.id,
				'update_url':update_url,})

		context = paginate(students,3,self.request,context,var_name='students')

		return context

	

	def post(self,request,*args,**kwargs):
		data = request.POST

		current_date = datetime.strptime(data['date'],'%Y-%m-%d').date()
		month = date(current_date.year,current_date.month,1)
		present = data['present'] and True or False
		student = Student.objects.get(pk=data['pk'])


		journal = MonthJournal.objects.get_or_create(student = student, date = month)[0]
		#journal.days[current_date.day-1] = present
		setattr(journal,'present_day%d' %current_date.day,present)
		journal.save()



		return JsonResponse({'status':'success'})