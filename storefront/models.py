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


class ContactSubmission(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} <{self.email}>"


class SupportTicket(models.Model):
    user_id = models.UUIDField(null=True, blank=True)
    subject = models.CharField(max_length=255, default='App Support')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='open')
    priority = models.CharField(max_length=20, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.subject}"


class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender_id = models.UUIDField(null=True, blank=True)
    message = models.TextField()
    is_from_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message on {self.ticket_id} by {self.sender_id or 'anon'}"

