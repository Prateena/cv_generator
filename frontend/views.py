from collections import OrderedDict
from io import BytesIO

from django.core.files import File
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.views.generic import View, TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from frontend.tasks import send_verification_email

from .mixins import *
from dashboard.models import * 
from .forms import *
from .tokens import account_activation_token
from .utils import render_to_pdf


#HomeView
class HomeView(TemplateView):
    template_name = 'frontend/layouts/home.html'

#Account Login View
class SigninView(FormView):        
    form_class =  SigninForm
    model = User    
    template_name = 'frontend/auth/login.html'
    success_url = reverse_lazy('frontend:home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        candidate = get_candidate(user)
        if user:
            if user.is_active and candidate is not None:
                if candidate.is_verified: 
                    login(self.request, user)
                    if self.request.GET.get('to') == 'profile':
                        return redirect('frontend:candidate_update',username=candidate.username)
                    else:
                        return render(self.request,'frontend/auth/login.html',{'message':'Please Check your email inbox for activation email','form':SigninForm})
        else:
            return render(self.request,'frontend/auth/login.html',{'message':'Please Check your username and password again and try to login','form':SigninForm})

    def form_invalid(self, form):
        if form.errors:
            return render(self.request, self.template_name,{"form":SigninForm, "errors":form.errors})
        return super().form_invalid(form)


#Account Logout View
class LogoutView(View):

    def get(self, request,*args,**kwargs):
        logout(request)
        return redirect('frontend:home')


#Account Register View
class SignupView(CreateView):
    form_class = CandidateSignupForm
    template_name = "frontend/auth/register.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidate_registration_form'] = context['form']
        return context

    def get_success_url(self):
        return render(self.request,'frontend/layouts/home.html', {'message':'Please Check your email inbox for activation email'})
    
    def form_valid(self,form):
        username = form.cleaned_data['username']
        password1 = form.cleaned_data['password1']
        form.instance.set_password(password1)
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        
        user = authenticate(self.request,username = username, password = password1)
        login(self.request,user,backend='django.contrib.auth.backends.ModelBackend')
        send_verification_email.delay(user_pk=user.pk)
        return render(self.request,'frontend/layouts/home.html', {'message':'Please Check your email inbox for activation email'})

    def form_invalid(self,form):
        if form.errors:
            return render(self.request, self.template_name, {"candidate_registration_form":CandidateSignupForm,'errors':form.errors})
        else:
            return super().form_invalid(form)



#Send token for account activation
class SendTokenView(View):
    def get(self, request, *args, **kwargs):
        send_verification_email.delay(user_pk=request.user.pk)
        return redirect('frontend:email_confirmation')
        


#Activation of account via activation email
def activate(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request,'frontend/layouts/home.html', {'message':'Please Check your email inbox for activation email'})
    if user.is_authenticated:
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            if get_candidate(user):
                user.candidate.is_verified = True
                user.candidate.save()            
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')           
                messages.success(request, 'Account Activation Successful!')            
                return redirect('frontend:candidate_update', username=user.username)
        else:
            return render(request, 'frontend/layouts/home.html', {'message':'Please Check your email inbox for activation email'})
    else:
        return render(request,'frontend/layouts/home.html',  {'message':'Please Check your email inbox for activation email'})



#Candidates Update View
class CandidateUpdateView(CandidateRequired403Mixin, UpdateView):
    model = Candidate
    template_name = 'frontend/candidates/profile_edit.html'
    form_class = CandidateCreateForm

    def get_object(self, *args, **kwargs):
        candidate = get_candidate(self.request.user)
        return candidate

    def get_success_url(self):
        return reverse_lazy('frontend:candidate_update',username=self.kwargs.get('username'))

    def form_invalid(self,form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return super().form_invalid(form)

    def form_valid(self,form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            return JsonResponse({'status':'ok'}, status=200)
        else:
            return response


#Candidates Photo Update View
class CandidatePhotoUpdateView(CandidateRequired403Mixin,CandidateRedirectMixin, UpdateView):
    template_name = 'frontend/candidates/candidate_photo_update.html'
    form_class = CandidatePhotoUpdateForm
    model = Candidate

    def get_object(self, *args, **kwargs):
        instance = get_candidate(self.request.user)
        return instance

    def get_success_url(self,*args,**kwargs):
          return reverse_lazy('frontend:candidate_cv_update',kwargs={'username':self.request.user.username})

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.is_ajax():
            return JsonResponse({}, status=200)
        return response
    
    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)


#Candidates Profile Detail Update View
class CandidateProfileDetailUpdateView(CandidateRequired403Mixin, GetCandidateMixin, CandidateRedirectMixin, UpdateView):
    model = Candidate
    form_class = CandidateProfileDetailCreateForm
    template_name = 'frontend/candidates/personal_detail_edit.html'

    def get_context_data(self, *args, **kwargs):
        context =  super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_personal_detail_update', kwargs={'pk':self.get_object().pk})
        return context

    def form_valid(self, form):
        print(form.data,32374902374)
        user = get_object_or_404(User,username=self.request.user.username)
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.save()
        form.save()
        response = super().form_valid(form)
        if self.request.is_ajax():
            return JsonResponse({}, status=200)
        return response

    def form_invalid(self, form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        return super().form_invalid(form)


#Candidate can edit their CV Templates
class CandidateEditCVTemplateView(CandidateRequired403Mixin, GetCandidateMixin, TemplateView):
    template_name = 'frontend/candidates/edit_cv.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['image_form'] = CandidatePhotoUpdateForm()
        return context


#Candidate can download their CV in their desired format
class CandidateCVDownloadTemplateView(CandidateRequired403Mixin, TemplateView):
    template_name = 'frontend/cvs/cv1.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        candidate = get_candidate(self.request.user)
        templates = OrderedDict()
        templates['1'] = 'cv1.html'
        
        samples = OrderedDict()
        samples['1'] = 'sample1.png'

        sample_id = request.GET.get('sample')
        template = templates.get(sample_id, 'cv1.html')
        self.template_name = 'frontend/cvs/' + template
        context = {'candidate': candidate}
        pdf = render_to_pdf(self.template_name, context)
        filename = "{}-cv.pdf".format(candidate.username)
        cv_obj = CurriculumVitae.objects.create(candidate=candidate)
        cv_obj.cv_generated.save(filename, File(BytesIO(pdf.content)))
        return render(request, self.template_name, context={'candidate':candidate, 'samples':samples, 'templates':templates})


class CandidateCompleteProfileUpdateView(CandidateRequired403Mixin,UpdateView):
    model = Candidate
    template_name = 'frontend/candidates/dashboard/profile_edit.html'
    form_class = CandidateProfileCompleteForm
    
    def get_success_url(self):
        # return reverse_lazy('frontend:candidate_update',username=self.kwargs.get('username'))
        return reverse_lazy('frontend:home')

    def get_object(self, *args, **kwargs):
        candidate = get_candidate(self.request.user)
        return candidate

    def form_invalid(self,form):
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return super().form_invalid(form)

    def form_valid(self,form):
        response = super().form_valid(form)
        print(form.data,34394734032)
        candidate = get_candidate(self.request.user)
        if self.request.is_ajax():
            return JsonResponse({'status':'ok'}, status=200)
        else:
            return response
            

class CandidateEducationCreateView(CandidateRequired403Mixin,AjaxResponse, CandidateCreateMixin, CreateView):
    model = EducationalQualification
    form_class = CandidateEducationCreateForm
    template_name = 'frontend/candidates/dashboard/education/education_create.html'

    def get_context_data(self, *args, **kwargs):
        context =  super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_education_create')
        return context

   
class CandidateEducationUpdateview(CandidateRequired403Mixin, GetObjectMixin, AjaxResponse, CandidateRedirectMixin, UpdateView):
    model = EducationalQualification
    form_class = CandidateEducationCreateForm
    template_name = 'frontend/candidates/dashboard/education/education_edit.html'

    def get_context_data(self, *args, **kwargs):
        context =  super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_education_update', kwargs={ 'pk':self.get_object().pk })
        return context


class CandidateEducationDeleteView(CandidateRequired403Mixin, GetObjectMixin, CandidateRedirectMixin, DeleteView):
    model = EducationalQualification
    template_name = 'frontend/candidates/dashboard/education/education_delete.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_education_delete', kwargs={'pk':self.get_object().pk})
        return context


class CandidateExperienceUpdateView(CandidateRequired403Mixin, GetObjectMixin, AjaxResponse, CandidateRedirectMixin, UpdateView):
    model = WorkExperience
    form_class = CandidateExperienceCreateForm
    template_name = 'frontend/candidates/dashboard/experience/experience_edit.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_experience_update', kwargs={'pk':self.get_object().pk })
        return context


class CandidateExperienceCreateView(CandidateRequired403Mixin,AjaxResponse, CreateView):
    model = WorkExperience
    form_class = CandidateExperienceCreateForm
    template_name = 'frontend/candidates/dashboard/experience/experience_create.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_experience_create')
        return context


class CandidateExperienceDeleteView(CandidateRequired403Mixin, GetObjectMixin, CandidateRedirectMixin, DeleteView):
    model = WorkExperience
    template_name = 'frontend/candidates/dashboard/experience/experience_delete.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_experience_delete', kwargs={'pk':self.get_object().pk})
        return context


class CandidateAboutMeUpdateView(CandidateRequired403Mixin, CandidateRedirectMixin, UpdateView):
    model = Candidate
    form_class = CandidateAboutMeCreateForm
    template_name = 'frontend/candidates/dashboard/aboutme/aboutme_edit.html'

    def get_object(self):
        return get_candidate(self.request.user)
        
    def get_context_data(self, *args, **kwargs):    
        context = super().get_context_data(*args, **kwargs)
        context['url'] = reverse_lazy('frontend:candidate_aboutme_update', kwargs={'pk':self.get_object().pk})
        return context



# class GenerateCVPDFView(View):

#     def get(self, request, *args, **kwargs):
#         obj_id = self.kwargs.get('pk')
#         candidate_obj = get_object_or_404(Candidate,pk=obj_id)
#         context = {'instance': candidate_obj}
#         pdf = render_to_pdf('frontend/cvs/cv1.html', context)
#         filename = "{}-cv.pdf" %(candidate_obj.username)
#         cv_obj = CurriculumVitae.objects.create(candidate=candidate_obj)
#         cv_obj.pdf.save(filename, File(BytesIO(pdf.content)))
#         return reverse_lazy('frontend:home')
