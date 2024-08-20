from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=20, decimal_places=8)

    def __str__(self):
        return self.name


class Wallet(models.Model):
    wid = ShortUUIDField(unique=True, length=10, max_length=20, prefix="wal", alphabet="abcdefgh12345")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_symbol = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    def get_currency_info(self):
        return CurrencyApi.get_currency(self.currency_symbol)

    def __str__(self):
        return f"{self.user.username} - {self.currency_symbol}: {self.amount}"

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.amount += amount
        self.save()
        self.create_transaction('deposit', amount)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.amount < amount:
            raise ValueError("Insufficient funds.")
        self.amount -= amount
        self.save()
        self.create_transaction('withdraw', amount)

    def transfer(self, futures, amount):
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if self.amount < amount:
            raise ValueError("Insufficient funds.")
        self.amount -= amount
        futures.amount += amount
        self.save()
        futures.save()
        self.create_transaction('transfer', amount, futures)

    def create_transaction(self, transaction_type, amount, futures=None):
        WalletTransactionHistory.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=amount,
            futures=futures,
        )


class WalletTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
        ('transfer', 'Transfer'),
    )

    origin_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    destination_wallet = models.ForeignKey(Wallet, null=True, blank=True, related_name='received_transactions',
                                           on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("The transaction amount must be positive.")

        if self.transaction_type in ['withdraw', 'transfer']:
            if self.origin_wallet.amount < self.amount:
                raise ValidationError("Insufficient funds in the wallet.")

        if self.transaction_type == 'transfer' and not self.destination_wallet:
            raise ValidationError("Recipient wallet must be specified for transfer.")

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.origin_wallet.user.username} {self.transaction_type} {self.amount} on {self.created_at}"


class TradingPair(models.Model):
    base_currency = models.CharField(max_length=10)
    quote_currency = models.CharField(max_length=10)

    def get_currency_price(self):
        symbol = f"{self.base_currency}{self.quote_currency}"
        currency_info = CurrencyApi.get_currency(symbol)
        if currency_info:
            return currency_info["price"]
        else:
            return None

    def __str__(self):
        currency_price = self.get_currency_price()
        if currency_price:
            return f"{self.base_currency}/{self.quote_currency} - Current Price: {currency_price}"
        else:
            return f"{self.base_currency}/{self.quote_currency} - Price not available"


class Order(models.Model):
    ORDER_TYPE_CHOICES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    ORDER_KIND_CHOICES = (
        ('market', 'Market Order'),
        ('limit', 'Limit Order'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE_CHOICES)
    order_kind = models.CharField(max_length=7, choices=ORDER_KIND_CHOICES, default='market')
    price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)  # قیمت سفارش
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=8)  # مقدار سفارش
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.order_type} {self.amount} {self.pair}"


class SpotTransactionHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    total = models.DecimalField(max_digits=20, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=50, null=True, blank=True)  # شناسه سفارش
    status = models.CharField(max_length=20, default='completed')  # وضعیت تراکنش
    fee = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)  # کارمزد

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.amount} {self.pair} @ {self.price}"
