from django.contrib import admin
from .models import Wallet, WalletTransactionHistory, TradingPair, Order, SpotTransactionHistory


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency_symbol', 'amount')
    search_fields = ('user', 'currency_symbol'),
    list_filter = ('user',)
    date_hierarchy = 'user'
    ordering = ('user',)


@admin.register(WalletTransactionHistory)
class WalletTransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'futures',)


@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'quote_currency')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_type', 'order_kind', 'price', 'amount')
    search_fields = ('user', 'order_type', 'order_kind'),
    list_filter = ('user', 'order_type', 'order_kind')
    date_hierarchy = 'user'
    ordering = ('user',)


@admin.register(SpotTransactionHistory)
class SpotTransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'pair', 'transaction_type', 'amount', 'price', 'total', 'status', 'fee')
