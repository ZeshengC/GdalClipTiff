from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from quickstart.serializers import UserSerializer, GroupSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from GdalClip import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
@api_view(['GET','POST'])
def Clip(request):
    if request.method == 'POST':
        inputTiffs = request.data["intif"]
        for tif in inputTiffs:
            main(request.data["inshp"],tif,request.data["outtif"])
            return Response({"message": tif + " has been clipped"})
        
         
    
