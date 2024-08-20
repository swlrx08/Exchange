from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('', views.WalletVeiwSetApiView)
router.register('', views.WalletTransactionHistoryVeiwSetApiView)
router.register('', views.TradingPairVeiwSetApiView)
router.register('', views.OrderVeiwSetApiView)
router.register('', views.SpotTransactionHistoryVeiwSetApiView)

urlpatterns = [
    path('viewset/', include(router.urls)),
]
