"""
This module contains the views for the REST API.
"""

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer


class FoodItemIngredientViewSet(viewsets.ModelViewSet):
    queryset = FoodItemIngredient.objects.all()
    serializer_class = FoodItemIngredientSerializer


class WeeklyMealPlanViewSet(viewsets.ModelViewSet):
    queryset = WeeklyMealPlan.objects.all()
    serializer_class = WeeklyMealPlanSerializer


class DailyMealViewSet(viewsets.ModelViewSet):
    queryset = DailyMeal.objects.all()
    serializer_class = DailyMealSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserIngredientViewSet(viewsets.ModelViewSet):
    queryset = UserIngredient.objects.all()
    serializer_class = UserIngredientSerializer

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request, format=None):
        images = Image.objects.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

class AudioUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = AudioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request, format=None):
        audios = Audio.objects.all()
        serializer = AudioSerializer(audios, many=True)
        return Response(serializer.data)

class AudioRenameView(APIView):
    def put(self, request, pk, format=None):
        audio = get_object_or_404(Audio, pk=pk)
        new_name = request.data.get('name')
        if new_name:
            audio.name = new_name
            audio.save()
            serializer = AudioSerializer(audio)
            return Response(serializer.data)
        return Response({'error': 'Name not provided'}, status=400)
