from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.urls import reverse_lazy
from django.shortcuts import render

from .forms import *
from dashboard.models import *


class GetCandidateMixin(object):
     def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['candidate'] = get_candidate(self.request.user) 
        print(get_candidate(self.request.user),389437389478379345435)
        return context

class CandidateRedirectMixin(object):
     def get_success_url(self,*args,**kwargs):
          return reverse_lazy('frontend:candidate_cv_update',kwargs={'username':self.request.user.username})

class CandidateCreateMixin(object):

     def form_valid(self,form):
          form.instance.candidate_id = get_candidate(self.request.user).pk
          response = super().form_valid(form)
          if self.request.is_ajax():
               return JsonResponse({}, status=200)
          return response

     def form_invalid(self,form):
          if self.request.is_ajax():
               return JsonResponse(form.errors, status=400)
          return HttpResponseRedirect(self.get_success_url())

     def get_success_url(self,*args,**kwargs):
          return reverse_lazy('frontend:candidate_cv_update',kwargs={'username':self.request.user.username})

class CandidateRequired403Mixin(LoginRequiredMixin):
     def dispatch(self,request,*args,**kwargs):
          candidate = get_candidate(self.request.user)
          if candidate is None:
               raise PermissionDenied
          if not candidate.is_verified:
               return render(self.request,'frontend/layouts/home.html', {'message':'You have not confirmed your email yet. Please check your inbox for email verification'})
          return super().dispatch(request,*args,**kwargs)


class AjaxResponse(object):
     def form_valid(self, form):
        form.instance.candidate_id = get_candidate(self.request.user).pk
        response = super().form_valid(form)
        if self.request.is_ajax():
            return JsonResponse({}, status=200)
        return response

     def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)

     def get_success_url(self,*args,**kwargs):
          return reverse_lazy('frontend:candidate_cv_update',kwargs={'username':self.request.user.username})


class GetObjectMixin(object):
     def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(candidate=get_candidate(self.request.user))
        return super().get_object(queryset=queryset)