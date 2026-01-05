from django.contrib import admin
from .models import Instrument, InstrumentIntervalData, PortfolioHolding, InstrumentQuote, CompanyNews, Company, \
    EarningsReport, Dividend


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'type', 'exchange', 'is_active', 'company')
    search_fields = ('symbol', 'name', 'company')

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

class CompanyNewsInline(admin.TabularInline):
    model = CompanyNews.companies.through
    extra = 1
    verbose_name = "Company News"
    verbose_name_plural = "Company News"

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'sector', 'industry', 'website', 'latest_news')
    search_fields = ('name', 'ticker', 'sector', 'industry')
    list_filter = ('sector', 'industry')
    inlines = [CompanyNewsInline]
    readonly_fields = ('created_at', 'updated_at')

    def latest_news(self, obj):
        latest = obj.news.order_by('-published_at').first()
        return latest.headline if latest else "-"
    latest_news.short_description = "Latest News"


@admin.register(CompanyNews)
class CompanyNewsAdmin(admin.ModelAdmin):
    list_display = ('headline', 'get_companies', 'published_at', 'source')
    search_fields = ('headline', 'content', 'companies__name', 'source')
    list_filter = ('published_at', 'source')
    filter_horizontal = ('companies',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'published_at'

    def get_companies(self, obj):
        return ", ".join([c.name for c in obj.companies.all()])
    get_companies.short_description = "Companies"


@admin.register(EarningsReport)
class EarningsReportAdmin(admin.ModelAdmin):
    list_display = ("company", "fiscal_quarter", "fiscal_year", "report_date", "estimate_eps", "actual_eps")
    list_filter = ("company", "fiscal_quarter", "fiscal_year")
    search_fields = ("company__name", "company__ticker")
    ordering = ("report_date",)
    date_hierarchy = "report_date"


@admin.register(Dividend)
class DividendAdmin(admin.ModelAdmin):
    list_display = ("company", "ex_date", "payment_date", "dividend_amount", "currency")
    list_filter = ("company",)
    search_fields = ("company__name", "company__ticker")
    ordering = ("ex_date",)
    date_hierarchy = "ex_date"

