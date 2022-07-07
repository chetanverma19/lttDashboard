from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action


from ltt_dashboard import response

# Create your views here.


class JobViewSet(viewsets.GenericViewSet):
    queryset = ''

    @action(detail=False, methods=['get'], url_path='test')
    def get_test_response(self, request, *args, **kwargs):
        return response.Ok(status=status.HTTP_408_REQUEST_TIMEOUT)