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


class Product(models.Model):
    name = models.CharField(max_length=40)
    product_image = models.ImageField(upload_to="product_image/", null=True, blank=True)
    price = models.PositiveIntegerField()
    description = models.CharField(max_length=4000)
    quantity = models.IntegerField(default=1)

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
