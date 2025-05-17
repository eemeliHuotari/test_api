from rest_framework import serializers
from .models import (
    Ingredient, FoodItem, FoodItemIngredient,
    WeeklyMealPlan, DailyMeal, User, UserIngredient
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class FoodItemIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )

    class Meta:
        model = FoodItemIngredient
        fields = ['id', 'food_item', 'ingredient', 'ingredient_id', 'quantity']


class FoodItemSerializer(serializers.ModelSerializer):
    ingredients = FoodItemIngredientSerializer(source="fooditemingredient_set", many=True, read_only=True)

    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'description', 'ingredients']


class DailyMealSerializer(serializers.ModelSerializer):
    lunch = FoodItemSerializer(read_only=True)
    lunch_id = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.all(), source='lunch', write_only=True
    )
    dinner = FoodItemSerializer(read_only=True)
    dinner_id = serializers.PrimaryKeyRelatedField(
        queryset=FoodItem.objects.all(), source='dinner', write_only=True
    )

    class Meta:
        model = DailyMeal
        fields = ['id', 'day', 'lunch', 'lunch_id', 'dinner', 'dinner_id']


class WeeklyMealPlanSerializer(serializers.ModelSerializer):
    daily_meals = DailyMealSerializer(many=True, read_only=True)

    class Meta:
        model = WeeklyMealPlan
        fields = ['id', 'start_date', 'daily_meals']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']


class UserIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    ingredient_id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient', write_only=True
    )

    class Meta:
        model = UserIngredient
        fields = ['id', 'user', 'ingredient', 'ingredient_id', 'quantity']
