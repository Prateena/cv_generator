from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import  reverse_lazy
from django.views.generic import View, TemplateView, FormView, ListView, CreateView, UpdateView
from django.db.models import Count

from .forms import (
    LoginForm, 
    UserForm
)
from .mixins import SuperAdminRequiredMixin
from .models import * 

User = get_user_model()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/layouts/home.html"


# Login Logout Views
class LoginPageView(FormView):
    form_class = LoginForm
    template_name = "dashboard/auth/login.html"

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        # Remember me
        if self.request.POST.get('remember', None) == None:
            self.request.session.set_expiry(0)

        login(self.request, user)

        if 'next' in self.request.GET:
            return redirect(self.request.GET.get('next'))
        return redirect('dashboard:index')
        

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('dashboard:login')


# User CRUD
class UserListView(SuperAdminRequiredMixin, ListView):
    model = User
    template_name = "dashboard/users/list.html"
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().annotate(cv_count=Count('candidate__cvs', distinct=True)).exclude(username=self.request.user)


class UserCreateView(SuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    form_class= UserForm
    success_message = "User Created Successfully"
    success_url = reverse_lazy('dashboard:users-list')
    template_name = "dashboard/users/form.html"
    

class UserUpdateView(SuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = UserForm
    model = User
    success_message = "User Updated Successfully"
    success_url = reverse_lazy('dashboard:users-list')
    template_name = "dashboard/users/form.html"


class UserStatusView(SuperAdminRequiredMixin, SuccessMessageMixin, View):
    model = User
    success_message = "User's Status Has Been Changed"
    success_url = reverse_lazy('dashboard:users-list')

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')
        if user_id:
            account = User.objects.filter(id=user_id).first()
            account.is_active = not account.is_active
            account.save(update_fields=['is_active'])
        return redirect(self.success_url)


class CurriculumVitaeListView(SuperAdminRequiredMixin, ListView):
    model = CurriculumVitae
    template_name = "dashboard/cvs/list.html"
    paginate_by = 100

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class CurriculumVitaeDetailView(SuperAdminRequiredMixin, ListView):
    model = CurriculumVitae
    template_name = "dashboard/cvs/detail.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['candidate'] = get_candidate(self.request.user) 
        return context

    
