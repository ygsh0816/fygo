from .models import Transaction, User
from django.contrib import admin, messages as flash_messages
from django.contrib.admin.views import main
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.forms import (AdminPasswordChangeForm,
                                       UserChangeForm)
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf.urls import url
from django.utils.html import escape
from django.utils.encoding import force_text
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.core.exceptions import PermissionDenied
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class TransactionAdmin(admin.ModelAdmin):
    actions = None
    verbose_name = "User Transactions"

    list_select_related = True

    list_display = ['user', 'transaction_type', 'transaction_id', 'transaction_amount', 'wallet_amount', 'create_date']

    list_display_links = ['user']
    search_fields = ['user', 'transaction_type', 'transaction_id']

    list_filter = ['transaction_type']

    ordering = ('-create_date',)

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def get_actions(self, request):
        return []


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom Admin class for Custom user model
    """

    def __init__(self, *args, **kwargs):
        super(CustomUserAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''

    change_user_password_template = None

    form = UserChangeForm

    change_password_form = AdminPasswordChangeForm

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {
            'fields': ('firstname', 'lastname')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )

    readonly_fields = ['username']

    list_select_related = True

    list_display = ['email', 'firstname', 'lastname',
                    'username', 'is_active']

    list_display_links = ['email', 'firstname', 'lastname', 'username']

    actions = ['make_active', 'make_inactive']

    search_fields = ['email', 'firstname', 'lastname', 'username', 'id']

    list_filter = ['is_active']

    ordering = ('-id',)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(CustomUserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(CustomUserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        return [
                   url(r'^(.+)/password/$', self.admin_site.admin_view(self.user_change_password),
                       name='auth_user_password_change'),
               ] + super(CustomUserAdmin, self).get_urls()

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(CustomUserAdmin, self).lookup_allowed(lookup, value)

    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):
        # It's an error for a user to have add permission but NOT change
        # permission for users. If we allowed such users to add users, they
        # could create superusers, which would mean they would essentially have
        # the permission to change users. To avoid the problem entirely, we
        # disallow users from adding users if they don't have change
        # permission.
        if not self.has_change_permission(request):
            # Raise Http404 in debug mode so that the user gets a helpful
            # error message.
            raise PermissionDenied
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {'auto_populated_fields': (),
                    'username_help_text': username_field.help_text, }
        extra_context.update(defaults)
        return super(CustomUserAdmin, self).add_view(request, form_url,
                                                     extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, user_id, form_url=''):
        """ User Change Password """
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, unquote(user_id))
        if user is None:
            message = 'User does not exist.'
            raise Http404(message % {'name': force_text(self.model._meta.verbose_name),
                                     'key': escape(id), })
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(
                    request, form, None)
                self.log_change(request, user, change_message)
                msg = 'Password successfully changed.'
                flash_messages.success(request, msg)
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})
        context = {
            'title': 'Change password',
            'adminForm': admin_form,
            'form_url': form_url,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(request,
                                self.change_user_password_template or
                                'admin/auth/user/change_password.html',
                                context)

    def get_actions(self, request):
        """ To remove user deleted action """
        actions = super(CustomUserAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def make_active(self, request, queryset):
        """make_active from action"""
        queryset.update(is_active=True)

    make_active.short_description = "Make selected users as Active"

    def make_inactive(self, request, queryset):
        """make_inactive from action"""
        queryset.update(is_active=False)

    make_inactive.short_description = "Make selected users as Inactive"

    def get_queryset(self, request):
        """ Return Only App User """
        return User.objects.filter(is_superuser=False)

    def has_add_permission(self, request):
        """ Denied add permissions """
        return True


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(User, CustomUserAdmin)
