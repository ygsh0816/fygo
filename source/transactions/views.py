# pylint: disable=line-too-long
# pylint: disable=unused-argument
from .serializers import AllTransactionSerializer, CreateTransactionSerializer, CreateWithdrawalSerializer, \
    RegisterUserSerializer
from .models import Transaction
from .serializers import GetAllUsersSerializer
from collections import OrderedDict
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

User = get_user_model()


class APIPagination(PageNumberPagination):
    """ API Pagination """
    page_size = settings.API_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class UsersListView(generics.ListAPIView):
    """
    Get User List
    """
    queryset = User.objects.all()
    pagination_class = APIPagination
    serializer_class = GetAllUsersSerializer


class RegisterUserView(generics.CreateAPIView):
    """
    Register a new user
    """
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer


class CreateTransactionView(generics.CreateAPIView):
    """
    Create a new transaction
    """
    queryset = Transaction.objects.all()
    serializer_class = CreateTransactionSerializer


class TransactionsListView(generics.ListAPIView):
    """
    Get Transactions List
    """
    queryset = Transaction.objects.all()
    pagination_class = APIPagination
    serializer_class = AllTransactionSerializer


class UserOperationsListView(generics.ListAPIView):
    """
    Get User Operations List
    """
    queryset = Transaction.objects.all()
    pagination_class = APIPagination
    serializer_class = AllTransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.kwargs['user_id']).order_by('-create_date')
        return queryset


class UserWithdrawalCreateView(generics.CreateAPIView):
    """
    User withdrawal view
    """
    queryset = Transaction.objects.all()
    serializer_class = CreateWithdrawalSerializer


class GetUserBalanceDetailView(generics.RetrieveAPIView):
    """
    Get Current User balance view
    """
    queryset = Transaction.objects.all()
    serializer_class = AllTransactionSerializer

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.kwargs['user_id']).order_by('-create_date')[:1]
        return queryset
