from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, LoginView, AssignBidView, JobPostView, JobListView, JobDeleteView, JobUpdateView, WorkerBidView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('jobs/', JobListView.as_view(), name='job-list'),
    path('jobs/<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    path('jobs/<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('jobs/create/', JobPostView.as_view(), name='job-create'),
    path('jobs/assign_bid/', AssignBidView.as_view(), name='assign-worker'),
    path('worker/bid/', WorkerBidView.as_view(), name='worker-bid'),
]