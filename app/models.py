"""Models for meal planning application."""
from django.db import models
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    """Represents a raw ingredient (e.g., Tomato, Rice)."""
    name = models.CharField(max_length=64, unique=True)
    unit = models.CharField(max_length=32)  # e.g., grams, ml, pieces

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    """Represents a food recipe."""
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through="FoodItemIngredient")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodItemIngredient(models.Model):
    """Links a FoodItem to its ingredients with quantity."""
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])

    class Meta:
        unique_together = ("food_item", "ingredient")

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} {self.ingredient.name} in {self.food_item.name}"


class WeeklyMealPlan(models.Model):
    """Represents a meal plan for a given week."""
    start_date = models.DateField()  # Start of the week (e.g., Monday)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"Week of {self.start_date}"


class DailyMeal(models.Model):
    """Stores lunch and dinner for a day within a weekly plan."""
    DAY_CHOICES = [
        ("Mon", "Monday"),
        ("Tue", "Tuesday"),
        ("Wed", "Wednesday"),
        ("Thu", "Thursday"),
        ("Fri", "Friday"),
        ("Sat", "Saturday"),
        ("Sun", "Sunday"),
    ]

    weekly_plan = models.ForeignKey(WeeklyMealPlan, on_delete=models.CASCADE, related_name="daily_meals")
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    lunch = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, related_name="lunches")
    dinner = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, related_name="dinners")

    class Meta:
        unique_together = ("weekly_plan", "day")
        ordering = ["weekly_plan", "day"]

    def __str__(self):
        return f"{self.get_day_display()} (Lunch: {self.lunch}, Dinner: {self.dinner})"


class User(models.Model):
    """User who stores ingredient inventory."""
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserIngredient(models.Model):
    """Tracks what ingredients a user has and in what quantity."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])

    class Meta:
        unique_together = ("user", "ingredient")

    def __str__(self):
        return f"{self.user.name} has {self.quantity} {self.ingredient.unit} of {self.ingredient.name}"

class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Audio(models.Model):
    file = models.FileField(upload_to='audios/')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
