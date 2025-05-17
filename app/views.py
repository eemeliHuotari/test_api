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