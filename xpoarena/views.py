from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from xpoarena.serializers import BoothSerializer, GamesSerializer
from .models import Booth, Game

@api_view(['GET', 'POST', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])  

def booth(request):
    if request.method == 'GET':
        if request.query_params:
            id = request.GET.get('id')
            object = Booth.objects.get(id=id)
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


@api_view(['GET', 'POST', 'PATCH'])
@parser_classes([MultiPartParser, FormParser])  
def update_booth(request, booth_id):
    if request.method == 'PATCH':
        data = request.data
        if not booth_id:
            return Response({"error": "No booth ID provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            booth_object = Booth.objects.get(id=booth_id)
        except Booth.DoesNotExist:
            return Response({"error": "Booth not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BoothSerializer(booth_object, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
@api_view(['GET', 'POST'])
def games(request):
    if request.method == 'GET':
        if request.query_params:
            id = request.GET.get('id', None)
            title = request.GET.get('title', None)

            if id is not None:
                objects = Game.objects.filter(booth_id = id)
                serializer = GamesSerializer(objects, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            if title is not None:
                object = Game.objects.get(title=title)
                serializer = GamesSerializer(object)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            objects = Game.objects.all()
            serializer = GamesSerializer(objects, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data
        serializer = GamesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

