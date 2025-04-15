from django.shortcuts import render,redirect,reverse,get_object_or_404
import razorpay
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login,logout
from django.contrib.auth.forms import UserCreationForm
from ecom.forms import ProductForm
# from ecom.forms import ProductForm

RAZORPAY_KEY_ID = 'rzp_test_Sjy6Si9Hn24pDd'
RAZORPAY_KEY_SECRET = '3nGtAZUZpwQz9DrxG4Q3WRYk'




def home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})
    


#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

def LogoutView(request):
    logout(request) 
    return redirect('/')  

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')


def admin_dashboard_view(request):
    # Counting different models
    customercount = models.Customer.objects.count()
    productcount = models.Product.objects.count()
    ordercount = models.Orders.objects.count()
    businesscount = models.Business.objects.count()  # Count Business users
    print('==============',customercount)

    # Fetching recent orders
    orders = models.Orders.objects.all()
    ordered_products = []
    ordered_bys = []

    for order in orders:
        order_items = order.get_items()  # Fetch related OrderItem entries
        products = [item.product for item in order_items]  # Extract products

        ordered_products.append(products)  # Store list of products
        ordered_bys.append(order.customer)  # Store customer info

    context = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'businesscount': businesscount,  # Adding business count to context
        'data': zip(ordered_products, ordered_bys, orders),
    }

    return render(request, 'ecom/admin_dashboard.html', context)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'ecom/admin_update_customer.html',context=mydict)




# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


# # admin add product by clicking on floating button
# @login_required(login_url='adminlogin')
# def admin_add_product_view(request):
#     productForm=forms.ProductForm()
#     if request.method=='POST':
#         productForm=forms.ProductForm(request.POST, request.FILES)
#         if productForm.is_valid():
#             productForm.save()
#         return HttpResponseRedirect('admin-products')
#     return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


# @login_required(login_url='adminlogin')
# def delete_product_view(request,pk):
#     product=models.Product.objects.get(id=pk)
#     product.delete()
#     return redirect('admin-products')

def admin_logout_view(request):
    logout(request)
    return redirect('/')  



@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import models

@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders = models.Orders.objects.all()
    order_data = []

    for order in orders:
        # Get all order items related to this order
        order_items = models.OrderItem.objects.filter(order=order)
        products = [item.product for item in order_items]  # Extract product from OrderItem
        
        order_data.append({
            'order': order,
            'products': products,
            'customer': order.customer
        })

    return render(request, 'ecom/admin_view_booking.html', {'order_data': order_data})




@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})


@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def admin_verify_business_view(request):
    pending_businesses = models.Business.objects.filter(verification_status='Pending')
    return render(request, 'ecom/admin_verify_business.html', {'pending_businesses': pending_businesses})

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def verify_business(request, business_id):
    business = get_object_or_404(models.Business, id=business_id)
    business.verification_status = 'Verified'
    business.save()
    return redirect('admin_verify_business')

@login_required(login_url='adminlogin')
@user_passes_test(lambda u: u.is_superuser)
def reject_business(request, business_id):
    business = get_object_or_404(models.Business, id=business_id)
    business.verification_status = 'Rejected'
    business.save()
    return redirect('admin_verify_business')

#---------------------------------------------------------------------------------
#------------------------ BUSINESS  RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------


def businessclick_view(request):
    if request.user.is_authenticated:
        return redirect('business-dashboard')
    return render(request, 'ecom/businessclick.html')

from django.contrib.auth.views import LoginView

class BusinessLoginView(LoginView):
    template_name = 'ecom/businesslogin.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if not hasattr(user, 'business'):
            messages.error(self.request, "This account is not registered as a business")
            return self.form_invalid(form)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('business-dashboard')

def business_logout_view(request):
    logout(request)
    return redirect('businessclick')

def business_registration_view(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        business_form = forms.BusinessForm(request.POST, request.FILES)
        
        if user_form.is_valid() and business_form.is_valid():
            user = user_form.save()
            
            # Create business profile
            business = business_form.save(commit=False)
            business.user = user
            business.save()
            
            # Login the user
            login(request, user)
            return redirect('business-dashboard')
    else:
        user_form = UserCreationForm()
        business_form = forms.BusinessForm()
    
    return render(request, 'ecom/business_registration.html', {
        'user_form': user_form,
        'business_form': business_form
    })

@login_required(login_url='businesslogin')
def business_dashboard_view(request):
    business = request.user.business
    products = models.Product.objects.filter(seller=request.user)  # Get all products by this business
    customercount = models.Customer.objects.all().count()

    # Get all orders related to the business's products
    orders = models.Orders.objects.filter(orderitem__product__in=products).distinct()

    context = {
        'business': business,
        'productcount': products.count(),
        'ordercount': orders.count(),
        'recent_orders': orders.order_by('-order_date')[:5],
        'customercount':customercount
    }
    return render(request, 'ecom/business_dashboard.html', context)






from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Product
from .forms import ProductForm

# Decorator for class-based views
def class_view_decorator(function_decorator):
    """Helper to apply function-based decorators to CBVs."""
    def decorator(ViewClass):
        ViewClass.dispatch = method_decorator(function_decorator)(ViewClass.dispatch)
        return ViewClass
    return decorator

# Function to calculate carbon footprint
from decimal import Decimal  # Ensure safe decimal calculations




@class_view_decorator(login_required(login_url='businesslogin'))
class BusinessAddProductView(View):
    template_name = 'ecom/business_add_product.html'

    form_class = ProductForm

    def get(self, request,*args,**kwargs):

        form_instance = self.form_class()

        return render(request,self.template_name,{'form':form_instance})
        

    def post(self, request,*args,**Kwargs):

        form_instance = self.form_class(request.POST,files=request.FILES)

        if form_instance.is_valid():

            data = form_instance.save(commit=False)

            total_footprint = sum([
            data.materials_footprint or Decimal(0),
            data.production_footprint or Decimal(0),
            data.packaging_footprint or Decimal(0),
            data.transportation_footprint or Decimal(0),
            data.disposal_footprint or Decimal(0),
            ])

        
            data.seller = request.user  # Assign logged-in user
            data.carbon_footprint = total_footprint
            data.sustainability_score = max(0, round((1 - (total_footprint / 1000)) * 100, 2))
  # Example score logic
            data.save()

            return redirect('business-products')  # Redirect to product list
        
        return render(request, self.template_name, {'form':form_instance})

@class_view_decorator(login_required(login_url='businesslogin'))
class BussinesUpdateProductView(View):
    template_name = 'ecom/business_update_product.html'
    form_class = ProductForm

    def get(self,request,*args,**kwargs):

        id = kwargs.get('pk')
        product_obj = Product.objects.get(id=id,seller=request.user)
        product_instance = self.form_class(instance=product_obj)

        return render(request,self.template_name,{'form':product_instance})
    
    def post(self,request,*args,**kwargs):

        id = kwargs.get('pk')
        product_obj = Product.objects.get(id=id,seller=request.user)
        form = self.form_class(request.POST,request.FILES,instance=product_obj)
        if form.is_valid():

            form.save()

            return redirect('business-products')
        
        return render(request,self.template_name,{'form':form})

        



        



@login_required(login_url='businesslogin')
def business_products_view(request):
    products = models.Product.objects.filter(seller=request.user)
    return render(request, 'ecom/business_products.html', {'products': products})









@login_required(login_url='businesslogin')
def business_delete_product_view(request, pk):
    product = get_object_or_404(models.Product, id=pk, seller=request.user)
    product.delete()
    return redirect('business-products')





# Business Order Views
@login_required(login_url='businesslogin')
def business_view_orders_view(request):
    # Get products owned by this business
    business_products = models.Product.objects.filter(seller=request.user)

    # Get all orders that contain any of the business's products
    business_orders = models.Orders.objects.filter(orderitem__product__in=business_products).distinct()

    return render(request, 'ecom/business_view_orders.html', {'orders': business_orders})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from ecom import models  # Adjust import based on your project structure

@login_required(login_url='businesslogin')
def update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("new_status")

        if not order_id or not new_status:
            return JsonResponse({"success": False, "error": "Missing order ID or status."})

        # Get order and ensure the seller owns the product in the order
        order = get_object_or_404(models.Orders, id=order_id)

        # Ensure the seller has at least one product in this order
        seller_products = models.Product.objects.filter(seller=request.user)
        if not order.orderitem_set.filter(product__in=seller_products).exists():
            return JsonResponse({"success": False, "error": "Unauthorized access to this order."})

        # Update status
        order.status = new_status
        order.save()

        return JsonResponse({"success": True, "new_status": new_status, "message": "Order status updated successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request method."})





@login_required(login_url='businesslogin')
def business_update_order_view(request, pk):
    order = get_object_or_404(models.Orders, id=pk, product__seller=request.user)
    if request.method == 'POST':
        orderForm = forms.OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('business-view-orders')
    else:
        orderForm = forms.OrderForm(instance=order)
    return render(request, 'ecom/business_update_order.html', {'orderForm': orderForm})

# Business Feedback Views
@login_required(login_url='businesslogin')
def business_view_feedback_view(request):
    # Get feedback for products belonging to this business
    business_feedback = models.Feedback.objects.filter(product__seller=request.user).order_by('-date')
    return render(request, 'ecom/business_view_feedback.html', {'feedbacks': business_feedback})


@login_required(login_url='adminlogin')
def view_business_view(request):
    # Use select_related to optimize fetching related User data
    business_users = models.Business.objects.select_related('user').all()
    return render(request, 'ecom/view_Business.html', {'business_users': business_users})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    query = request.GET.get('query', '')  # Use get to avoid KeyError
    products = models.Product.objects.filter(name__icontains=query) if query else []

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    word = f"Searched Result for: '{query}'" if query else "No search term entered."

    context = {
        'products': products,
        'word': word,
        'product_count_in_cart': product_count_in_cart
    }

    return render(request, 'ecom/product_list.html', context)



# any one can add product to cart, no need of signin
from django.shortcuts import render, redirect
from django.contrib import messages
from ecom.models import Product, Cart
from django.contrib.sessions.models import Session

@login_required(login_url='customerlogin')
def add_to_cart_view(request, pk):
    product = Product.objects.get(id=pk)
    
    # Get or create the session key
    if not request.session.session_key:
        request.session.save()
    
    session_key = request.session.session_key

    # Check if the product is already in the cart
    cart_item, created = Cart.objects.get_or_create(session_key=session_key, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart successfully!')
    
    return redirect('cart')  # Redirect to cart page

@login_required(login_url='customerlogin')

def increase_quantity_view(request, pk):
    session_key = request.session.session_key
    if not session_key:
        return redirect('cart')  # Redirect if session is missing

    cart_item = Cart.objects.filter(session_key=session_key, product_id=pk).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')
@login_required(login_url='customerlogin')

def decrease_quantity_view(request, pk):
    session_key = request.session.session_key
    if not session_key:
        return redirect('cart')

    cart_item = Cart.objects.filter(session_key=session_key, product_id=pk).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart')

from django.shortcuts import render
from ecom.models import Product, Cart

from django.shortcuts import render
from ecom.models import Product, Cart

@login_required(login_url='customerlogin')
def cart_view(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = Cart.objects.filter(session_key=session_key)

    total = sum(item.total_price() for item in cart_items)

    return render(request, 'ecom/cart.html', {'cart_items': cart_items, 'total': total})


@login_required(login_url='customerlogin')

def remove_from_cart_view(request, pk):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_item = Cart.objects.filter(session_key=session_key, product_id=pk).first()

    if cart_item:
        cart_item.delete()  # Completely remove item from cart

    return redirect('cart')


@login_required(login_url='customerlogin')

def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})



def product_list(request):
    products = Product.objects.all()  # Fetch all products

    context = {
        'products': products
    }
    return render(request, 'ecom/product_list.html', context)

from django.shortcuts import render, get_object_or_404
from ecom.models import Product, Feedback

from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from .models import Product, Feedback  # Import your models

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    feedbacks = Feedback.objects.filter(product=product)  # Fetch related feedbacks

    # Calculate expected delivery date (current date + 5 days)
    expected_delivery_date = datetime.now().date() + timedelta(days=5)

    context = {
        'product': product,
        'feedbacks': feedbacks,
        'expected_delivery_date': expected_delivery_date,
    }
    return render(request, 'ecom/product_detail.html', context)





from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings 
from django.contrib.auth.decorators import login_required
from ecom import models, forms  

@login_required(login_url='customerlogin')
def customer_address_view(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = models.Cart.objects.filter(session_key=session_key)
    product_in_cart = cart_items.exists()
    product_count_in_cart = cart_items.count()

    addressForm = forms.AddressForm()
    stock_errors = []

    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        shipping_method = request.POST.get('shipping_method', 'standard')

        # ✅ Check stock before validating form
        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                stock_errors.append(
                    f"Only {item.product.stock_quantity} left in stock for '{item.product.name}'."
                )

        if stock_errors:
            # ✅ Return with error if stock issues found
            return render(request, 'ecom/customer_address.html', {
                'addressForm': addressForm,
                'product_in_cart': product_in_cart,
                'product_count_in_cart': product_count_in_cart,
                'stock_errors': stock_errors
            })

        if addressForm.is_valid():
            # ✅ Store address details in session
            request.session['order_details'] = {
                'email': addressForm.cleaned_data['Email'],
                'mobile': addressForm.cleaned_data['Mobile'],
                'address': addressForm.cleaned_data['Address'],
                'shipping_method': shipping_method
            }

            # ✅ Redirect to Razorpay payment
            return redirect('initiate-payment')

    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': product_count_in_cart
    })

from decimal import Decimal
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from ecom import models

@login_required(login_url='customerlogin')
def initiate_payment_view(request):
    session_key = request.session.session_key
    if not session_key or 'order_details' not in request.session:
        return redirect('cart')  # 🚨 Redirect if session expired

    try:
        customer = models.Customer.objects.get(user=request.user)
    except models.Customer.DoesNotExist:
        return redirect('error_page')  # 🚨 Handle missing customer case

    cart_items = models.Cart.objects.filter(session_key=session_key)
    if not cart_items.exists():
        return redirect('cart')

    # ✅ Fetch order details from session
    order_data = request.session['order_details']
    shipping_method = order_data.get('shipping_method', 'standard')

    # ✅ Define Shipping Carbon Offsets
    SHIPPING_CARBON_OFFSETS = {
        'standard': 2.00,
        'express': 5.00,
        'eco': 0.50
    }
    shipping_carbon_offset = Decimal(SHIPPING_CARBON_OFFSETS.get(shipping_method, 2.00))

    # ✅ Calculate Order Totals
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    total_product_footprint = sum(item.product.carbon_footprint * item.quantity for item in cart_items)
    total_carbon_footprint = total_product_footprint + shipping_carbon_offset

    # ✅ Create Razorpay Order
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": int(total_amount * 100),  # Convert to paise
            "currency": "INR",
            "payment_capture": "1"
        })
    except razorpay.errors.BadRequestError:
        return redirect('error_page')  # 🚨 Handle Razorpay error

    # ✅ Save Order in Database (with Pending status)
    order = models.Orders.objects.create(
        customer=customer,
        status='Pending',
        email=order_data['email'],
        mobile=order_data['mobile'],
        address=order_data['address'],
        total_amount=total_amount,
        shipping_method=shipping_method,
        shipping_carbon_offset=shipping_carbon_offset,
        total_carbon_footprint=total_carbon_footprint,
        razorpay_order_id=razorpay_order['id']  # ✅ Store Razorpay Order ID
    )

    # ✅ Store Order ID in Session for Verification
    request.session['order_id'] = order.id

    return render(request, 'ecom/payment.html', {
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'total_amount': total_amount,
        'cart_items': cart_items
    })

from django.http import JsonResponse


import razorpay
import logging
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ecom import models

logger = logging.getLogger(__name__)

@login_required(login_url='customerlogin')
def payment_success_view(request):
    if request.method != "POST":
        return redirect('cart')  # 🚨 Prevent direct GET request

    if 'order_id' not in request.session:
        return redirect('cart')

    order_id = request.session['order_id']
    order = models.Orders.objects.get(id=order_id)

    # Get payment details from Razorpay response (✅ POST instead of GET)
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    if not razorpay_payment_id or not razorpay_signature:
        logger.error("❌ Missing Payment ID or Signature")
        return JsonResponse({'error': 'Missing Payment ID or Signature'}, status=400)

    # ✅ Verify payment with Razorpay
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    params_dict = {
        'razorpay_order_id': order.razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    try:
        razorpay_client.utility.verify_payment_signature(params_dict)  # ✅ Signature Verification
        logger.info(f"✅ Payment Verified! Order ID: {order.razorpay_order_id}")

        # ✅ Update order status
        order.status = 'Confirmed'
        order.is_paid=True
        order.payment_id = razorpay_payment_id
        order.save()

        send_payment_email(order)

        

        # ✅ Move cart items to order
        cart_items = models.Cart.objects.filter(session_key=request.session.session_key)
        for item in cart_items:
            models.OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                carbon_footprint=item.product.carbon_footprint * item.quantity
            )

            # update stock quantity
            item.product.stock_quantity -= item.quantity
            item.product.save()

        # ✅ Clear cart and session
        cart_items.delete()
        request.session.pop('order_details', None)
        request.session.pop('order_id', None)

        return render(request, 'ecom/payment_success.html', {'order': order})

    except razorpay.errors.SignatureVerificationError:
        logger.error("❌ Razorpay Signature Verification Failed!")
        order.status = 'Failed'
        order.save()
        return JsonResponse({'error': 'Payment verification failed'}, status=400)

    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        return JsonResponse({'error': 'Something went wrong!'}, status=500)

def send_payment_email(order): 
           

        subject = "Payment Successful - Your Order Confirmation"
        message = f"""
        Hi {order.customer},

        Your payment of ₹{order.total_amount} has been received.

        Order ID: {order.id}

        Payment Method: Razorpay

        Your item will receive in 3-4 Business Days 

        Thank you for shopping with us!

        Regards,
        Anughar ks
        Marketing team,Store Team
        """
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [order.email],  
            fail_silently=False,
        )        
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ecom import models  

@login_required(login_url='customerlogin')
def order_list_view(request):
    try:
        customer = models.Customer.objects.get(user=request.user)
    except models.Customer.DoesNotExist:
        return redirect('error_page')  # Handle missing customer gracefully

    # Get all orders for the logged-in user
    orders = models.Orders.objects.filter(customer=customer).order_by('-id')

    # Define order tracking progress values
    STATUS_PROGRESS = {
        'Pending': 25,
        'Confirmed': 50,
        'Shipped': 75,
        'Delivered': 100,
    }

    # Attach progress to orders
    for order in orders:
        order.progress = STATUS_PROGRESS.get(order.status, 10)  # Default to 10% if unknown

    return render(request, 'ecom/order_list.html', {'orders': orders})
    
    
def order_details_view(request, order_id):
    order = models.Orders.objects.get(id=order_id)
    order_items = models.OrderItem.objects.filter(order=order)

    # Define tracking stages
    tracking_stages = ['Pending', 'Confirmed', 'Shipped', 'Delivered']
    
    # Calculate progress percentage safely
    if order.status in tracking_stages:
        progress_index = tracking_stages.index(order.status) + 1
        progress_percentage = int((progress_index / len(tracking_stages)) * 100)  # Ensure integer
    else:
        progress_percentage = 0  # Default if status is unknown

        print(order_items)

    return render(request, 'ecom/order_details.html', {
        'order': order,
        'order_items': order_items,
        'progress_percentage': progress_percentage  # ✅ Ensure it's always an integer
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Feedback, Product
from .forms import FeedbackForm

from django.shortcuts import render, get_object_or_404, redirect
from ecom.models import Product, Feedback  # Ensure Feedback model is imported
from ecom.forms import FeedbackForm

def add_feedback(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.name = request.user  # Ensure request.user is valid
            feedback.product = product  
            
            print(f"Saving feedback for product {product.id} by {request.user}")

            try:
                feedback.save()
                print("Feedback saved successfully!")
                return redirect('home')  
            except Exception as e:
                print(f"Error saving feedback: {e}")

        else:
            print("Form is not valid:", form.errors)  # Print form errors

    else:
        form = FeedbackForm(initial={'product': product})

    return render(request, 'ecom/add_feedback.html', {'form': form, 'product': product})

    






@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)



#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form':sub})




# Sustainability Views
@login_required
def product_sustainability_view(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    sustainability_data = get_object_or_404(models.ProductSustainabilityData, product=product)
    return render(request, 'ecom/product_sustainability.html', {
        'product': product,
        'sustainability_data': sustainability_data
    })

@login_required
def carbon_dashboard_view(request):
    footprint_data = models.UserCarbonFootprint.objects.filter(user=request.user).order_by('-month')
    offsets = models.CarbonOffsetPurchase.objects.filter(user=request.user)
    return render(request, 'ecom/carbon_dashboard.html', {
        'footprint_data': footprint_data,
        'offsets': offsets
    })

@login_required
def offset_carbon_view(request):
    if request.method == 'POST':
        form = forms.CarbonOffsetForm(request.POST)
        if form.is_valid():
            offset = form.save(commit=False)
            offset.user = request.user
            offset.save()
            return redirect('carbon-dashboard')
    else:
        form = forms.CarbonOffsetForm()
    return render(request, 'ecom/carbon_offset.html', {'form': form})

