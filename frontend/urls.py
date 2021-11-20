from django.urls import path

from .views import *

app_name = 'frontend'

urlpatterns = [
    #HomeView
    path('', HomeView.as_view(), name='home'),

    #Accounts Login, Logout and Register
    path('login/', SigninView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name = 'logout'),
    path('register/',SignupView.as_view(), name = 'signup'),

    #Email Confirmations 
    path('resend/token/', SendTokenView.as_view(), name = 'send_token'),
    path('activate/(<uidb64>[0-9A-Za-z_\-]+)/(<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', activate, name='activate_account'),

    #Candidates Profile Detail updates
    path('candidate/<username>/', CandidateUpdateView.as_view(), name='candidate_update'),
    path('personaldetails/<int:pk>/', CandidateProfileDetailUpdateView.as_view(),  name='candidate_personal_detail_update'),
    
    # Candidate Photo Update
    path('candidate/photo/update/', CandidatePhotoUpdateView.as_view(), name='candidate_photo_update'),

    # Candidate CV Update and Download
    path('cv/edit/<username>/', CandidateEditCVTemplateView.as_view(), name='candidate_cv_update'),
    path('download/cv/', CandidateCVDownloadTemplateView.as_view(), name='candidate_cv_download'),
    # path('generate-cv/<int:pk>/', GenerateCVPDFView.as_view(), name="generate_cv_pdf"),

    # Candidate Education CRUD
    path('education/create/', CandidateEducationCreateView.as_view(), name='candidate_education_create'),
    path('education/<int:pk>/', CandidateEducationUpdateview.as_view(), name='candidate_education_update'),
    path('education/<int:pk>/delete/',CandidateEducationDeleteView.as_view(), name='candidate_education_delete'),
    path('aboutme/<int:pk>/', CandidateAboutMeUpdateView.as_view(), name='candidate_aboutme_update'),

    #Candidate Experience CRUD
    path('experience/<int:pk>/', CandidateExperienceUpdateView.as_view(),  name='candidate_experience_update'),
    path('experience/create/', CandidateExperienceCreateView.as_view(), name='candidate_experience_create'),
    path('experience/<int:pk>/delete/',CandidateExperienceDeleteView.as_view(), name = 'candidate_experience_delete'),


]