from django.contrib import admin
from .models import Wallet, WalletTransactionHistory, TradingPair, Order, SpotTransactionHistory


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    pass
    # list_display = ('user', 'currency_symbol', 'amount')
    # search_fields = ('user', 'currency_symbol'),
    # list_filter = ('user',)
    # ordering = ('user',)


@admin.register(WalletTransactionHistory)
class WalletTransactionHistoryAdmin(admin.ModelAdmin):
    pass
    # list_display = ('transaction_type', 'amount')


@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    pass
    # list_display = ('base_currency', 'quote_currency')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass
    # list_display = ('user', 'order_type', 'order_kind', 'price', 'amount')
    # search_fields = ('user', 'order_type', 'order_kind'),
    # list_filter = ('user', 'order_type', 'order_kind')
    # ordering = ('user',)


@admin.register(SpotTransactionHistory)
class SpotTransactionHistoryAdmin(admin.ModelAdmin):
    pass
    # list_display = ('user', 'pair', 'transaction_type', 'amount', 'price', 'total', 'status', 'fee')
