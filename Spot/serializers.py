from rest_framework import serializers
from .models import Currency, TradingPair, Order, Wallet, WalletTransactionHistory, SpotTransactionHistory


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class WalletTransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransactionHistory
        fields = '__all__'


class TradingPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingPair
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class SpotTransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotTransactionHistory
        fields = '__all__'
