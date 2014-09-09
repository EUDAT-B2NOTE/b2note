from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User, Group
from query.models import Ontologies
from rest_framework import viewsets
from b2noteapi.serializers import UserSerializer, GroupSerializer, OntologySerializer
from rest_framework import permissions



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.IsAdminUser,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class OntologiesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Ontologies.objects.all()
    serializer_class = OntologySerializer

