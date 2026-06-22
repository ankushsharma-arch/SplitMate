from django.urls import path
from .views import ExpenseCreateView, ExpenseListView, ExpenseDetailView, SettleUpView

urlpatterns = [
    path('', ExpenseCreateView.as_view()),
    path('group/<int:group_id>/', ExpenseListView.as_view()),
    path('<int:pk>/', ExpenseDetailView.as_view()),
    path('group/<int:group_id>/settle-up/', SettleUpView.as_view()),
]
