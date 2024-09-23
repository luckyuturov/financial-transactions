from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Transaction, TransactionParticipant
from .serializers import UserSerializer, TransactionSerializer
from django.db import transaction as db_transaction
from decimal import Decimal

# Создание пользователя
class UserCreateView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Создание транзакции
class TransactionCreateView(APIView):
    @db_transaction.atomic
    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            # Создаем новую транзакцию
            transaction_instance = Transaction.objects.create(
                transaction_id=serializer.validated_data['transaction_id'],
                total_amount=Decimal(serializer.validated_data['total_amount'])
            )

            # Распределение долей отправителей
            total_sender_share = sum([Decimal(sender['share']) for sender in request.data['senders']])
            for sender_data in request.data['senders']:
                user = User.objects.get(id=sender_data['id'])
                sender_share_amount = (Decimal(sender_data['share']) / total_sender_share) * Decimal(transaction_instance.total_amount)
                
                # Проверяем баланс отправителя
                if user.balance < sender_share_amount:
                    return Response({"error": f"Insufficient funds for user {user.id}"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Уменьшаем баланс отправителя
                user.balance -= sender_share_amount
                user.save()

                # Сохраняем данные отправителя в участниках транзакции
                TransactionParticipant.objects.create(
                    transaction=transaction_instance,
                    user=user,
                    share=sender_data['share'],
                    amount=sender_share_amount
                )

            # Распределение долей получателей
            total_receiver_share = sum([Decimal(receiver['share']) for receiver in request.data['receivers']])
            for receiver_data in request.data['receivers']:
                user = User.objects.get(id=receiver_data['id'])
                receiver_share_amount = (Decimal(receiver_data['share']) / total_receiver_share) * Decimal(transaction_instance.total_amount)
                
                # Увеличиваем баланс получателя
                user.balance += receiver_share_amount
                user.save()

                # Сохраняем данные получателя в участниках транзакции
                TransactionParticipant.objects.create(
                    transaction=transaction_instance,
                    user=user,
                    share=receiver_data['share'],
                    amount=receiver_share_amount
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Получение баланса пользователя
class BalanceView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)
