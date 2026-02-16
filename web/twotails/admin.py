from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from .models import (User, Role, Address, Supplier, Supply, SupplyItem, Delivery ,Category, Product,
                      DeliveryItem, Cart, CartItem, Order, OrderItem, Promotion, ProductPromotion)


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1
class CartInline(admin.TabularInline):
    model = Cart
    extra = 1
class OrderInline(admin.TabularInline):
    model = Order
    extra = 1
class SupplierInline(admin.StackedInline):
    model = Supplier
    extra = 1
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1  
class ProductPromotionInline(admin.TabularInline):
    model = ProductPromotion
    extra = 1
class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
class ProductPromotionInline(admin.TabularInline):
    model = ProductPromotion
    extra = 1
class SupplyItemInline(admin.TabularInline):
    model = SupplyItem
    extra = 1 



@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    model = Role
    list_display = ['id', 'name']
    list_display_links = ['name']
    search_fields = ['id', 'name']


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = [
        'id',
        'role_id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_active',
    ]
    list_display_links = ['username']
    list_filter = [
        'role_id',
        'is_staff',
        'is_active',
    ]
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]
    date_hierarchy = 'date_joined'

    inlines = [AddressInline, CartInline, OrderInline]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    model = Supplier
    list_display = ['name', 'email']
    list_display_links = ['name']
    #list_filter = []
    search_fields = ['name']

@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'date']
    list_filter = ['supplier', 'date']
    inlines = [SupplyItemInline]
    search_fields = ['supplier__name']
    date_hierarchy = 'date'

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    model = Delivery
    list_display = ['status', 'delivery_date', 'supplier_id']
    search_fields = ['supplier_id']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'manufacturer',
        'supplier',
        'purchase_price',
        'sale_price',
        'profit',
        'promotions_list'
    )
    list_display_links = ['name']
    list_filter = ('category', 'manufacturer', 'supplier', 'promotions')
    search_fields = ('name', 'description', 'manufacturer')
    readonly_fields = ('profit',)
    inlines = [ProductPromotionInline]
    ordering = ('name',)
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'manufacturer', 'supplier')
        }),
        ('Цены', {
            'fields': ('purchase_price', 'sale_price', 'profit')
        }),
        ('Акции', {
            'fields': (),
        }),
    )
    def profit(self, obj):
        return obj.sale_price - obj.purchase_price
    profit.short_description = 'Прибыль'
    def promotions_list(self, obj):
        return ", ".join([p.name for p in obj.promotions.all()])
    promotions_list.short_description = 'Акции'

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'updated_at', 'total_items')
    list_filter = ('status',)
    search_fields = ('user__username',)
    inlines = [CartItemInline]

    def total_items(self, obj):
        return sum(item.quantity for item in obj.cartitem_set.all())
    total_items.short_description = "Всего товаров"

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_amount', 'items_count')
    list_filter = ('status',)
    search_fields = ('user__username',)
    inlines = [OrderItemInline]

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent', 'is_active', 'start_date', 'end_date', 'active_status')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    inlines = [ProductPromotionInline]

    def active_status(self, obj):
        return "Активна" if obj.is_active else "Неактивна"
    active_status.short_description = "Статус"