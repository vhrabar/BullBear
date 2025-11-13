from django.contrib import admin
from .models import Instrument, InstrumentIntervalData, PortfolioHolding, InstrumentQuote


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

@admin.register(InstrumentQuote)
class InstrumentQuoteAdmin(admin.ModelAdmin):
    list_display = (
        "instrument",
        "bid_price",
        "ask_price",
        "last_price",
        "exchange",
        "market_state",
        "timestamp",
        "updated_at",
    )

    list_filter = ("exchange", "market_state", "currency")

    search_fields = ("instrument",)

    ordering = ("-timestamp",)

    readonly_fields = ("updated_at", "timestamp")

    fieldsets = (
        ("Instrument", {
            "fields": ("instrument", "exchange", "currency")
        }),
        ("Prices", {
            "fields": ("bid_price", "bid_size", "ask_price", "ask_size", "last_price")
        }),
        ("Market Meta", {
            "fields": ("market_state", "daily_change", "daily_change_percent")
        }),
        ("Timestamps", {
            "fields": ("timestamp", "updated_at")
        }),
    )