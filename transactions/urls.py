from django.urls import path
from .views import UserCreateView, TransactionCreateView, BalanceView

urlpatterns = [
    path('users/create/', UserCreateView.as_view(), name='create_user'),
    path('transactions/create/', TransactionCreateView.as_view(), name='create_transaction'),
    path('users/balance/<int:user_id>/', BalanceView.as_view(), name='get_balance'),
]
