from django.urls import path, include
from rest_framework import routers

from app.views import UserViewSet, IngredientViewSet, FoodItemViewSet, FoodItemIngredientViewSet, WeeklyMealPlanViewSet, DailyMealViewSet, UserIngredientViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'food-items', FoodItemViewSet, basename='fooditem')
router.register(r'food-item-ingredients', FoodItemIngredientViewSet, basename='fooditemingredient')
router.register(r'weekly-plans', WeeklyMealPlanViewSet, basename='weeklymealplan')
router.register(r'daily-meals', DailyMealViewSet, basename='dailymeal')
router.register(r'user-ingredients', UserIngredientViewSet, basename='useringredient')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
