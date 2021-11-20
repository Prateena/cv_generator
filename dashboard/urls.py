from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns=[       
        path('', views.DashboardView.as_view(), name='index'),
        
        # accounts
        path('accounts/login/', views.LoginPageView.as_view(), name='login'),
        path('accounts/logout/', views.LogoutView.as_view(), name='logout'),

        # user crud
        path('users/', views.UserListView.as_view(), name='users-list'),
        path('users/create', views.UserCreateView.as_view(), name='users-create'),
        path('users/<int:pk>/update', views.UserUpdateView.as_view(), name='users-update'),
        path('users/<int:pk>/status', views.UserStatusView.as_view(), name='users-status'),

        #CVS CRUD
        path('cvs/', views.CurriculumVitaeListView.as_view(), name='cvs-list'),
        path('cv/<int:pk>/detail/', views.CurriculumVitaeDetailView.as_view(), name='cv-detail'),
]