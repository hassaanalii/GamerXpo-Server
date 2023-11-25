from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from xpoarena.serializers import BoothSerializer
from .models import Booth

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])  

def booth(request):
    if request.method == 'GET':
        if request.query_params:
            name = request.GET.get('name')
            object = Booth.objects.get(name=name)
            serializer = BoothSerializer(object)
            return Response(serializer.data)
        else:
            objects = Booth.objects.all()
            serializer = BoothSerializer(objects, many=True)
            return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data
        serializer = BoothSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
        