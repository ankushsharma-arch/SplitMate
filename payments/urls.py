from django.urls import path
from .views import PaymentCreateView, PaymentListView, GroupSummaryView

urlpatterns = [
    path('', PaymentCreateView.as_view()),
    path('group/<int:group_id>/', PaymentListView.as_view()),
    path('group/<int:group_id>/summary/', GroupSummaryView.as_view()),
]
