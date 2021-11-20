
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from dashboard.models import CurriculumVitae

from .serializers import CVSerializer
from .permission import IsSuperUser

class CVListAPIView(ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsSuperUser]
    serializer_class = CVSerializer
    queryset = CurriculumVitae.objects.filter(deleted_at__isnull=True)
    pagination_class = PageNumberPagination
    

    def get_queryset(self):
        queryset = super().get_queryset()

        if 'skill' in self.request.GET and self.request.GET.get('skill', '').strip() != '':
            queryset = queryset.filter(candidate__skills__name__icontains=self.request.GET.get('skill'))

        return queryset