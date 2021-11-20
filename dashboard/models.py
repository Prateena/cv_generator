from datetime import date, datetime
from urllib.parse import parse_qs, urlsplit

from django.apps import apps
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags

from .utils import *
from .validators import *

GENDER = (
    (1,'Male'),
    (2,'Female'),
    (3,'Others'),
)


CURRENTLY_WORKING_TYPE = (
    ('Yes','Yes'),
    ('No','No'),
)

def get_candidate(user):
    try:
        return user.candidate
    except:
        pass
    return None


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        auto_now=False,
    )
    updated_at = models.DateTimeField(
        auto_now_add=False,
        auto_now=True,
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        super().save()


class Skill(models.Model):
    name = models.CharField(max_length=254, unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name

class Candidate(User, DateTimeModel):
    gender = models.IntegerField(choices = GENDER,blank = False,null= True)
    dob = models.DateField(blank = False,null = True)
    is_verified = models.BooleanField(default = False)
    mobile_number = models.CharField(max_length=13,blank = False,null= True)
    address = models.CharField(max_length = 120,blank = False, null= True)
    skills = models.ManyToManyField(Skill,related_name='candidates')
    profile_image = models.FileField(null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['png','jpg','jpeg'])])
    about_me = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-id']
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"

    def __str__(self):
        return self.username

    @property
    def name(self):
        return "{0} {1} ".format(self.first_name,self.last_name)

    def get_photo(self):
        try:
            return self.profile_image.url
        except:
            return self.get_avatar()

    def get_avatar(self):
        url="https://ui-avatars.com/api/?background=0D8ABC&color=fff&name={0}+{1}&size=256".format(self.first_name,self.last_name)
        return url

    @property
    def get_skills(self):
        return self.skills.all

    @property
    def get_educations(self):
        return self.educational_qualifications.filter(deleted_at__isnull=True)


class EducationalQualification(DateTimeModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='educational_qualifications')
    degree = models.CharField(max_length=100)
    name_of_institute = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    started_year = models.CharField(max_length=10)
    passed_year = models.CharField(max_length=10)
    description = models.TextField()

    class Meta:
        verbose_name = "Educational Qualification"
        verbose_name_plural = "Educational Qualifications"
        ordering = ["-id"]

    def __str__(self):
        return self.candidate.username


class WorkExperience(DateTimeModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='work_experiences')
    job_title = models.CharField(max_length=250)
    organization = models.CharField(max_length=250)
    is_working = models.IntegerField(choices=CURRENTLY_WORKING_TYPE , null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experiences"
        ordering = ["-id"]

    def __str__(self):
        return self.candidate.username

    
class CurriculumVitae(DateTimeModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='cvs')
    cv_generated = models.FileField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.candidate.username