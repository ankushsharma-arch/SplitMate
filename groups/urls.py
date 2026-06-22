from django.urls import path
from .views import GroupListCreateView, GroupDetailView, GroupMemberView, BalancesView

urlpatterns = [
    path('', GroupListCreateView.as_view()),
    path('<int:pk>/', GroupDetailView.as_view()),
    path('<int:pk>/members/', GroupMemberView.as_view()),
    path('<int:pk>/balances/', BalancesView.as_view()),
]
