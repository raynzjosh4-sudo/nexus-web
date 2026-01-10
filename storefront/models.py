from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='category_icons/') # For "Bags", "Watches" icons

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200) # e.g., "Regular Fit Linen-blend..."
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g., $189.00
    rating = models.FloatField(default=0.0) # e.g., 4.8
    review_count = models.IntegerField(default=0) # e.g., (342)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.name

