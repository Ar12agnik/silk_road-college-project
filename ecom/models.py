from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to="profile_pic/CustomerProfilePic/", null=True, blank=True,default='profile_pic/CustomerProfilePic/default_pic.jpg'
    )
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    email = models.EmailField(default="abc@example.com")

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name


# class Product(models.Model):
#     name = models.CharField(max_length=40)
#     product_image = models.ImageField(upload_to="product_image/", null=True, blank=True)
#     price = models.PositiveIntegerField()
#     description = models.CharField(max_length=4000)
#     quantity = models.IntegerField(default=1)
#     category = models.CharField(max_length=1000,default="None")
#     @property
#     def avg_raiting(self):
#         reviews = self.review_set.all()
#         if reviews.exists():
#             return round(sum(review.raiting for review in reviews) / reviews.count(), 2)
#         return 0  # Default value if no reviews exist

#     def __str__(self):
#         return self.name
class Product(models.Model):
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to="product_image/", null=True, blank=True)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=4000)
    quantity = models.IntegerField(default=1)
    category = models.CharField(max_length=1000, default="None")
    avg_raiting = models.FloatField(default=0.0)  # New field to store average rating

    def update_avg_raiting(self):
        reviews = self.review_set.all()
        if reviews.exists():
            self.avg_raiting = round(sum(review.raiting for review in reviews) / reviews.count(), 2)
        else:
            self.avg_raiting = 0.0
        self.save()  # Save the updated rating to the database

    def __str__(self):
        return self.name

class Orders(models.Model):
    STATUS = (
        ("Pending", "Pending"),
        ("Order Confirmed", "Order Confirmed"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
    )
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, null=True)
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    mobile = models.CharField(max_length=20, null=True)
    order_date = models.DateField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)
    quantity = models.IntegerField(default=1)
    razorpay_payment_id = models.CharField(max_length=100, null=True,blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True,blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True,blank=True)


class Feedback(models.Model):
    name = models.CharField(max_length=40)
    feedback = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    prod_details = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField(default=1)
    customer_details = models.ForeignKey(Customer, on_delete=models.CASCADE)
class returnorder(models.Model):
    Pname=models.CharField(max_length=200)
    Cphone=models.CharField(max_length=20)
    dop=models.DateField()
    user_name=models.CharField(max_length=100)
class review(models.Model):
    Product = models.ForeignKey("Product", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raiting = models.IntegerField()
    comments = models.CharField(max_length=5000, default=None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the review first
        self.Product.update_avg_raiting()  # Update product's average rating

    def delete(self, *args, **kwargs):
        product = self.Product
        super().delete(*args, **kwargs)  # Delete the review first
        product.update_avg_raiting()  # Update product's average rating after deletion
    def __str__(self):
        return "review for "+self.Product.name+" by "+self.user.username
    
