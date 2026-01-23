from django.contrib import admin
from .models import Fund, FundHolding, FundSubscription


class FundHoldingInline(admin.TabularInline):
    model = FundHolding
    extra = 1
    readonly_fields = []
    fields = ['instrument', 'weight_percent']


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator_portfolio', 'is_active', 'total_units', 'nav_per_unit', 'created_at']
    list_filter = ['is_active', 'creator_portfolio']
    search_fields = ['name', 'creator_portfolio__name']
    inlines = [FundHoldingInline]
    readonly_fields = ['total_units', 'nav_per_unit', 'created_at', 'updated_at']



@admin.register(FundSubscription)
class FundSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber_portfolio', 'fund', 'units', 'invested_amount', 'created_at']
    list_filter = ['fund', 'subscriber_portfolio']
    search_fields = ['fund__name', 'subscriber_portfolio__name']
    readonly_fields = ['units', 'invested_amount', 'created_at', 'updated_at']
