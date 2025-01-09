from django import forms
from django.contrib.auth.models import User
from . import models
from django.core.validators import RegexValidator


class CustomerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model=models.Customer
        fields = ['mobile','email']

class ProductForm(forms.ModelForm):
    class Meta:
        model=models.Product
        fields=['name','price','description','product_image',"quantity"]


#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile = forms.CharField(
        max_length=15, 
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Enter a valid phone number (e.g., +1234567890, 1234567890)."
            )
        ]
    )
    Address = forms.CharField(widget=forms.Textarea, max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status']

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))
