from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from xpoarena.serializers import BoothSerializer, GamesSerializer, ThemeSerializer, BoothCustomizationSerializer
from .models import Booth, Game, Theme, BoothCustomization

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
        
        
@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])  
def update_game(request, title):
    if request.method == 'PATCH':
        data = request.data
        if not title:
            return Response({"error": "No game title provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            game_object = Game.objects.get(title=title)
        except Booth.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GamesSerializer(game_object, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        try:
            game_object = Game.objects.get(title=title)
        except Game.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)

        game_object.delete()
        return Response({"success": f"Booth {title} deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        
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

@api_view(['POST', 'GET'])
def theme(request):
    if request.method == 'POST':
        serializer = ThemeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        if 'name' in request.query_params:
            name = request.GET.get('name')
            object = Theme.objects.get(name=name)
            serializer = ThemeSerializer(object)
            return Response(serializer.data)
        elif 'id' in request.query_params:
            id = request.GET.get('id')
            object = Theme.objects.get(id=id)
            serializer = ThemeSerializer(object)
            return Response(serializer.data)

@api_view(['POST', 'GET'])
def customizedBooth(request):
    if request.method == 'POST':
        data = request.data
        serializer = BoothCustomizationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        if request.query_params:
            id = request.GET.get('id')
            object = BoothCustomization.objects.get(booth_id=id)
            serializer = BoothCustomizationSerializer(object)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        

@api_view(['PUT'])
def update_booth_customization(request, pk):
    try:
        booth_customization = BoothCustomization.objects.get(pk=pk)
    except BoothCustomization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = BoothCustomizationSerializer(booth_customization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)