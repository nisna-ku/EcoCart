from django.contrib import admin
from .models import Customer,Product,Orders,Feedback,Business,ProductSustainabilityData,UserCarbonFootprint,ProductCategory
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Customer, CustomerAdmin)

class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Product, ProductAdmin)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Orders, OrderAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)

class CategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(ProductCategory, CategoryAdmin)
# Register your models here.


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'verification_status', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('business_name', 'user__username')
    actions = ['verify_businesses']

    def verify_businesses(self, request, queryset):
        queryset.update(verification_status='Verified')
    verify_businesses.short_description = "Mark selected businesses as verified"

@admin.register(ProductSustainabilityData)
class ProductSustainabilityAdmin(admin.ModelAdmin):
    list_display = ('product', 'total_carbon_footprint', 'last_updated')
    search_fields = ('product__name',)

@admin.register(UserCarbonFootprint)
class CarbonFootprintAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'net_carbon_footprint')
    list_filter = ('month',)