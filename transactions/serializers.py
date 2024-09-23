from rest_framework import serializers
from .models import User, Transaction, TransactionParticipant

# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'balance']

# Сериализатор для участников транзакции
class TransactionParticipantSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # Изменяем на user_id
    share = serializers.DecimalField(max_digits=5, decimal_places=2)

# Сериализатор для транзакции
class TransactionSerializer(serializers.ModelSerializer):
    senders = TransactionParticipantSerializer(many=True)
    receivers = TransactionParticipantSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ['transaction_id', 'total_amount', 'senders', 'receivers']

