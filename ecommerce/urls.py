"""

Developed By : sumit kumar
facebook : fb.com/sumit.luv
Youtube :youtube.com/lazycoders


"""
from django.contrib import admin
from django.urls import path
from ecom import views
from django.contrib.auth.views import LoginView,LogoutView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name='home'),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    path('logout/', views.LogoutView,name='logout'),
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view,name='contactus'),
    path('search', views.search_view,name='search'),
    path('send-feedback', views.send_feedback_view,name='send-feedback'),
    path('view-feedback', views.view_feedback_view,name='view-feedback'),

    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='ecom/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('admin-logout/', views.admin_logout_view, name='admin-logout'),

    path('view-customer', views.view_customer_view,name='view-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),

    path('admin-products', views.admin_products_view,name='admin-products'),
    # path('delete-product/<int:pk>', views.delete_product_view,name='delete-product'),
    # path('update-product/<int:pk>', views.update_product_view,name='update-product'),

    path('admin-view-booking', views.admin_view_booking_view,name='admin-view-booking'),
    path('delete-order/<int:pk>', views.delete_order_view,name='delete-order'),
    path('update-order/<int:pk>', views.update_order_view,name='update-order'),

    path('dashboard/verify-business/', views.admin_verify_business_view, name='admin_verify_business'),    
    path('ecom-admin/verify-business/<int:business_id>/', views.verify_business, name='verify_business'),
    path('ecom-admin/reject-business/<int:business_id>/', views.reject_business, name='reject_business'),




    path('customersignup', views.customer_signup_view,name='customersignup'),
    path('customerlogin', LoginView.as_view(template_name='ecom/customerlogin.html'),name='customerlogin'),
    path('customer-home', views.customer_home_view,name='customer-home'),
    # path('my-order', views.my_order_view2,name='my-order'),
    path('my-profile', views.my_profile_view,name='my-profile'),
    path('edit-profile', views.edit_profile_view,name='edit-profile'),
    path('product/<int:product_id>/feedback/', views.add_feedback, name='add-feedback'),
    path('products/', views.product_list, name='product-list'),
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),


    path('add-to-cart/<int:pk>', views.add_to_cart_view,name='add-to-cart'),
    path('cart', views.cart_view,name='cart'),
    path('increase-quantity/<int:pk>', views.increase_quantity_view, name='increase-quantity'),
    path('decrease-quantity/<int:pk>', views.decrease_quantity_view, name='decrease-quantity'),

    path('remove-from-cart/<int:pk>', views.remove_from_cart_view,name='remove-from-cart'),
    path('customer-address/', views.customer_address_view, name='customer-address'),
    path('create-order/', views.update_order_view, name='create-order'),
    path('initiate-payment/', views.initiate_payment_view, name='initiate-payment'),
    path('payment-success/', views.payment_success_view, name='payment-success'),
    path('orders/', views.order_list_view, name='order-list'),

    # path('my-orders/', views.my_order_view, name='my-orders'),
    path('order-details/<int:order_id>/', views.order_details_view, name='order-details'),

    path('businessclick', views.businessclick_view, name='businessclick'),
    path('businesslogin', views.BusinessLoginView.as_view(), name='businesslogin'),
    path('business-logout', views.business_logout_view, name='business-logout'),
    path('business-register', views.business_registration_view, name='business-register'),
    
    path('businesslogin', LoginView.as_view(template_name='ecom/businesslogin.html'), name='businesslogin'),
    path('business-dashboard', views.business_dashboard_view, name='business-dashboard'),
    path('business-products', views.business_products_view, name='business-products'),
    path('business-add-product', views.BusinessAddProductView.as_view(), name='business-add-product'),
    path('business-delete-product/<int:pk>', views.business_delete_product_view, name='business-delete-product'),
    path('business-update-product/<int:pk>',views.BussinesUpdateProductView.as_view(), name='business-update-product'),
    path('business-view-orders', views.business_view_orders_view, name='business-view-orders'),
    path("update-order-status/", views.update_order_status, name="update_order_status"),
    path('business-update-order/<int:pk>', views.business_update_order_view, name='business-update-order'),
    path('business-view-feedback', views.business_view_feedback_view, name='business-view-feedback'),
    path('view-business/', views.view_business_view, name='view-business'),


    # Sustainability URLs
    path('product/<int:pk>/sustainability/', views.product_sustainability_view, name='product-sustainability'),
    path('carbon-dashboard/', views.carbon_dashboard_view, name='carbon-dashboard'),
    path('offset-carbon/', views.offset_carbon_view, name='offset-carbon'),
    
    # Updated Business URLs
    # path('business/products/add/', views.business_add_product_view, name='business-add-product'),
    
    
    
    
    ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

