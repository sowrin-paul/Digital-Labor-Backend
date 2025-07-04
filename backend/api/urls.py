from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, LoginView, AssignWorkerView, JobPostView, JobListView, JobDeleteView, JobUpdateView, WorkerBidView, JobBidListView, WorkerProfileUpdateView, UnassignWorkerView, WorkerJobListView, PaymentCreateView,  JobPaymentStatusView, CustomerReviewWorkerView, WorkerReviewCustomerView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    path('jobs/<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('jobs/create/', JobPostView.as_view(), name='job-create'),
    path('jobs/assign_bid/', AssignWorkerView.as_view(), name='assign-worker'),
    path('jobs/unassign_worker/', UnassignWorkerView.as_view(), name='unassign-worker'),
    path('worker/bid/', WorkerBidView.as_view(), name='worker-bid'),
    path('worker/job_list/', WorkerJobListView.as_view(), name='job-list-worker'),
    path('customer/jobs/bids/', JobBidListView.as_view(), name='job-bid-list'),
    path('worker/profile/update/', WorkerProfileUpdateView.as_view(), name='worker-profile-update'),
    path('payments/', PaymentCreateView.as_view(), name='payment-create'),
    path('jobs/<int:job_id>/', JobPaymentStatusView.as_view(), name='mark-job-completed'),
    path('jobs/<int:job_id>/review_worker/', CustomerReviewWorkerView.as_view(), name='review-worker'),
    path('jobs/<int:job_id>/review_customer/', WorkerReviewCustomerView.as_view(), name='review-customer'),
]