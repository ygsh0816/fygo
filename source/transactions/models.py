# pylint: disable=line-too-long
# pylint: disable=unused-argument
import itertools
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)
from django.utils.text import slugify


class UserManager(BaseUserManager):
    """
    User Custom Manager
    """

    def create_user(self, email=None, password=None):
        """
        Create User
        """
        if not email:
            raise ValueError('User must have a email address')
        user = self.model(email=self.normalize_email(email))
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Create Superuser
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    If no need to use UserGroups/Permissions then remove PermissionsMixin
    """
    email = models.EmailField('Email Address', unique=True)
    firstname = models.CharField('First Name', max_length=20, db_index=True)
    lastname = models.CharField('Last Name', max_length=20, db_index=True)
    username = models.SlugField(max_length=254, unique=True, blank=True)
    is_staff = models.BooleanField('Staff member', default=False)
    is_active = models.BooleanField('Active', default=True)
    is_superuser = models.BooleanField('Is a Super user', default=False)
    create_date = models.DateTimeField('Joined Time', auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def get_full_name(self):
        return '{0} {1}'.format(self.firstname, self.lastname)

    def __str__(self):
        return '{0} {1}'.format(self.firstname, self.lastname)

    def get_short_name(self):
        return '{0}'.format(self.firstname)

    @staticmethod
    def create_username(firstname, lastname, email, seperator='-'):
        """ Create Username """
        username = None
        lenslug = 210
        if firstname:
            username = firstname + ' ' + lastname
        else:
            username = email
        if not len(username) > 210:
            lenslug = len(username)
        username = slugify(username)[0:lenslug]
        temp_username = username
        for itrvalue in itertools.count(1):
            if not User.objects.filter(username__iexact=username).exists():
                break
            username = "%s%s%d" % (slugify(temp_username), seperator, itrvalue)
        return username

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """
        Save Model
        """
        if not self.username:
            self.username = User.create_username(
                self.firstname, self.lastname, self.email)
        self.is_active = True
        return super(User, self).save(force_insert=False,
                                      force_update=False,
                                      using=None,
                                      update_fields=None)

    USERNAME_FIELD = 'email'

    class Meta(object):
        """ User Class Meta """
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        app_label = 'transactions'


class Transaction(models.Model):
    """
    Transaction Model
    """
    REFUND = 1
    PURCHASE = 2
    WITHDRAWAL = 3

    TRANSACTION_TYPES = {
        (REFUND, 'REFUND'),
        (PURCHASE, 'PURCHASE'),
        (WITHDRAWAL, 'WITHDRAWAL')
    }
    user = models.ForeignKey(User, related_name='transaction_user', on_delete=models.CASCADE)
    transaction_type = models.SmallIntegerField(choices=TRANSACTION_TYPES)
    transaction_amount = models.IntegerField()
    wallet_amount = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['create_date']
