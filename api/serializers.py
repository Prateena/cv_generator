from rest_framework import serializers
from django.urls import  reverse

from django.contrib.auth import models

from dashboard.models import Candidate, CurriculumVitae


class CandidateSerializer(serializers.ModelSerializer):
    skills = serializers.StringRelatedField(many=True)

    class Meta:
        model = Candidate
        fields = ['id', 'email', 'first_name', 'last_name', 'dob', 'mobile_number', 'gender', 'skills']

class CVSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer()
    cv_url = serializers.SerializerMethodField()

    class Meta:
        model = CurriculumVitae
        fields = ['candidate', 'cv_url']

    def get_cv_url(self, obj):
        # return reverse('frontend:candidate_cv_download',kwargs={'candidate':obj.candidate})
        return 'Not Implemented'