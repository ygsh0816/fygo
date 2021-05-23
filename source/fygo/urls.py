"""fygo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from transactions import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('get-all-users/', views.UsersListView.as_view(), name="users-list"),
    path('create-transaction/', views.CreateTransactionView.as_view(), name="create-transaction"),
    path('get-transactions/', views.TransactionsListView.as_view(), name="get-transactions"),
    path('get-operations/<int:user_id>/', views.UserOperationsListView.as_view(), name="get-operations"),
    path('withdraw/<int:pk>/', views.UserWithdrawalCreateView.as_view(), name="withdraw"),
    path('get-my-balance/<int:user_id>/', views.GetUserBalanceDetailView.as_view(), name="get-balance"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
