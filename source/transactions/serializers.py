# pylint: disable=line-too-long
# pylint: disable=unused-argument
from django.forms import model_to_dict
from rest_framework import serializers
from .models import Transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .constant import *
from .exceptions import CustomException
from django.conf import settings

User = get_user_model()


class AllTransactionSerializer(serializers.ModelSerializer):
    """
    All Transactions Serializer
    """

    class Meta:
        model = Transaction
        fields = ['user', 'transaction_id', 'transaction_amount', 'wallet_amount', 'create_date']

    def to_representation(self, instance):
        result = super(AllTransactionSerializer,
                       self).to_representation(instance)
        result['username'] = instance.user.username
        transaction_types = list(Transaction.TRANSACTION_TYPES)
        result['transaction_type'] = list(filter(lambda x: instance.transaction_type in x, transaction_types))[0][1]
        return result


class CreateTransactionSerializer(serializers.ModelSerializer):
    """CreateTransactionSerializer"""

    def __init__(self, *args, **kwargs):
        super(CreateTransactionSerializer, self).__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            self.user_id = self.request.data['user']

    class Meta(object):
        """meta information for Create Board"""
        model = Transaction
        fields = ['user', 'transaction_type', 'transaction_id', 'transaction_amount']
        extra_kwargs = {'wallet_amount': {'read_only': True, 'required': False}}

    def validate(self, validated_data):
        """
        Validate data
        """
        if not User.objects.filter(pk=self.user_id).exists():
            raise CustomException(USER_NOT_EXIST, "User", status.HTTP_400_BAD_REQUEST)

        if not validated_data['transaction_amount']:
            raise CustomException(INVALID_TRANSACTION_AMOUNT, "transaction_amount", status.HTTP_406_NOT_ACCEPTABLE)

        user = validated_data['user']
        if validated_data['transaction_amount'] < 0:
            if not user.transaction_user.select_related().exists():
                raise CustomException(INVALID_TRANSACTION_AMOUNT, "transaction_amount", status.HTTP_406_NOT_ACCEPTABLE)

        if user.transaction_user.select_related().exists():
            wallet_amount = user.transaction_user.select_related().order_by('-create_date')[0].wallet_amount
            if abs(validated_data['transaction_amount']) > wallet_amount:
                raise CustomException(INSUFFICIENT_FUNDS_TO_REFUND, "transaction_amount",
                                      status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return validated_data
        else:
            return validated_data

    def create(self, validated_data):
        """
        Create Data
        """
        user = validated_data['user']
        if user.transaction_user.select_related().exists():
            validated_data['wallet_amount'] = user.transaction_user.select_related().order_by('-create_date')[
                                                  0].wallet_amount + validated_data['transaction_amount']
        else:
            validated_data['wallet_amount'] = validated_data['transaction_amount']
        instance = Transaction.objects.create(**validated_data)
        return instance


class GetAllUsersSerializer(serializers.ModelSerializer):
    """
    All User Serializer
    """

    def __init__(self, *args, **kwargs):
        super(GetAllUsersSerializer, self).__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']
            self.user_id = self.request.user.id

    class Meta(object):
        """
        meta for user
        """
        model = User
        fields = ('id', 'firstname', 'lastname', 'username')


class CreateWithdrawalSerializer(serializers.ModelSerializer):
    """
    Create Withdrawal Serializer
    """

    def __init__(self, *args, **kwargs):
        super(CreateWithdrawalSerializer, self).__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    class Meta(object):
        """meta information for Create Board"""
        model = Transaction
        fields = ['transaction_amount', 'wallet_amount']
        extra_kwargs = {'wallet_amount': {'read_only': True, 'required': False}}

    def validate(self, validated_data):
        """
        Validate data
        """
        user_id = int(self.request.path.split('/')[2])
        try:
            user = User.objects.get(pk=user_id)
            validated_data['user'] = user
        except ObjectDoesNotExist:
            raise CustomException(USER_NOT_EXIST, "User", status.HTTP_400_BAD_REQUEST)

        if not validated_data['transaction_amount']:
            raise CustomException(INVALID_TRANSACTION_AMOUNT, "transaction_amount", status.HTTP_406_NOT_ACCEPTABLE)

        if validated_data['transaction_amount']:
            if not user.transaction_user.select_related().exists():
                raise CustomException(NOTHING_TO_WITHDRAW, "transaction_amount", status.HTTP_406_NOT_ACCEPTABLE)

        if user.transaction_user.select_related().exists():
            wallet_amount = user.transaction_user.select_related().order_by('-create_date')[0].wallet_amount
            if abs(validated_data['transaction_amount']) > wallet_amount:
                raise CustomException(NOTHING_TO_WITHDRAW, "transaction_amount",
                                      status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return validated_data
        else:
            return validated_data

    def create(self, validated_data):
        validated_data['wallet_amount'] = \
            validated_data['user'].transaction_user.select_related().order_by('-create_date')[
                0].wallet_amount - validated_data['transaction_amount']
        validated_data['transaction_type'] = 3
        instance = Transaction.objects.create(**validated_data)
        return instance


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    email = serializers.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        self.created = False
        super(RegisterUserSerializer, self).__init__(*args, **kwargs)
        context = kwargs.get('context', None)
        if context:
            self.request = kwargs['context']['request']

    class Meta(object):
        """meta information for user registration serializer"""
        model = get_user_model()
        fields = ('email', 'password', 'firstname', 'lastname')

        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def validate_email(self, email_value):
        """meta information for validating email"""
        try:
            get_user_model().objects.get(email__iexact=email_value)
            raise ValidationError(ALREADY_REGISTER_USER)
        except get_user_model().DoesNotExist:
            return email_value

    def validate_password(self, password_value):
        """ validates password """
        if password_value and (len(password_value) < settings.VALIDATE_PASSWORD_MIN_LEN):
            raise serializers.ValidationError(PASSWORD_CHARACTER_LENGTH_API)
        return password_value

    def create(self, validated_data):
        instance = get_user_model().objects.create(**validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        self.created = True
        return instance

    @property
    def data(self):
        if self.created:
            user = model_to_dict(self.instance)
            response = {
                'message': USER_REGISTERED_SUCCESSFULLY, 'extras': user}
        else:
            response = {'message': USER_NOT_EXIST,
                        'status': settings.HTTP_API_ERROR}
        return response
