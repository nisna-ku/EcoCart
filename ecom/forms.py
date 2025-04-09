from django import forms
from django.contrib.auth.models import User
from . import models


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
        fields=['address','mobile','profile_pic']

class BusinessUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Make email mandatory

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        widgets = {
            'password': forms.PasswordInput()
        }

class BusinessForm(forms.ModelForm):
    class Meta:
        model = models.Business
        fields = ['business_name', 'description', 'business_logo', 'website','sustainability_score']



from ecom.models import Product,ProductCategory


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['category']



class ProductForm(forms.ModelForm):

    materials_footprint = forms.DecimalField(required=False)
    production_footprint = forms.DecimalField(required=False)
    packaging_footprint = forms.DecimalField(required=False)
    transportation_footprint = forms.DecimalField(required=False)
    disposal_footprint = forms.DecimalField(required=False)
    materials_source = forms.CharField(required=False)
    production_method = forms.CharField(required=False)
    disposal_instructions = forms.CharField(required=False)

    class Meta:
        model = Product

        fields = ['name','product_image','price','description','category','stock_quantity','materials_footprint','production_footprint','packaging_footprint','transportation_footprint','disposal_footprint','materials_source','production_method','disposal_instructions','certification_details']





#address of shipment
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status']

from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your feedback...'})
        }


#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))



class ProductSustainabilityForm(forms.ModelForm):
    class Meta:
        model = models.ProductSustainabilityData
        fields = '__all__'
        exclude = ('product', 'last_updated')

class CarbonOffsetForm(forms.ModelForm):
    class Meta:
        model = models.CarbonOffsetPurchase
        fields = ['project', 'amount']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'})
        }