from django.contrib import admin
from .models import Instrument, InstrumentIntervalData, PortfolioHolding

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'type', 'exchange', 'is_active')
    search_fields = ('symbol', 'name')

@admin.register(InstrumentIntervalData)
class InstrumentIntervalDataAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'start_time', 'close_price', 'volume')
    list_filter = ('instrument',)

@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'instrument', 'quantity', 'average_price')
    list_filter = ('portfolio',)
