from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import WalletSerializer, WalletTransactionHistorySerializer, TradingPairSerializer, OrderSerializer, \
    SpotTransactionHistorySerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from .models import Wallet, WalletTransactionHistory, TradingPair, Order, SpotTransactionHistory


class WalletVeiwSetApiView(ModelViewSet):
    queryset = Wallet.objects.order_by('-wid').all()
    serializer_class = WalletSerializer


class WalletTransactionHistoryVeiwSetApiView(ModelViewSet):
    queryset = WalletTransactionHistory.objects.order_by('-wtid').all()
    serializer_class = WalletTransactionHistorySerializer


class TradingPairVeiwSetApiView(ModelViewSet):
    queryset = TradingPair.objects.all()
    serializer_class = TradingPairSerializer


class OrderVeiwSetApiView(ModelViewSet):
    queryset = Order.objects.order_by('-oid').all()
    serializer_class = OrderSerializer


class SpotTransactionHistoryVeiwSetApiView(ModelViewSet):
    queryset = SpotTransactionHistory.objects.order_by('-tid').all()
    serializer_class = SpotTransactionHistorySerializer
