"""Django admin configuration."""
from django.contrib import admin

from .models import User, Ingredient, FoodItem, FoodItemIngredient, WeeklyMealPlan, DailyMeal, UserIngredient

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(User)
admin.site.register(FoodItem)
admin.site.register(FoodItemIngredient)
admin.site.register(WeeklyMealPlan)
admin.site.register(DailyMeal)
admin.site.register(UserIngredient)
