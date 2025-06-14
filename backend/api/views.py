from django.contrib.auth import authenticate
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import User, Payment, Job, Worker, Review, Bid
from .serializers import RegisterSerializer, JobSerializer

def send_bid_notification(worker_email, job_title):
    send_mail(
        subject="Bid Selected",
        message=f"Your bid for the job '{job_title}' has been selected.",
        from_email="noreply@yourdomain.com",
        recipient_list=[worker_email],
        fail_silently=False,
    )
# ======================================== Registration API ==================================
class RegisterView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            if user.is_worker:
                return Response(
                    {
                        "success": True,
                        "statusCode": 201,
                        "message": "Registration successful. Your account will be activated after admin approval.",
                        "data": {
                            "id": str(user.id),
                            "name": user.get_username(),
                            "email": user.email,
                            "role": user.role,
                            "refresh": str(refresh),
                            "access": str(refresh.access_token)
                        }
                    }, status=status.HTTP_201_CREATED)
            return Response(
                {
                    "success": True,
                    "statusCode": 201,
                    "message": "User registered successfully.",
                    "data": {
                        "id": str(user.id),
                        "name": user.get_username(),
                        "email": user.email,
                        "role": user.role,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================ Login API ====================================
class LoginView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "success": True,
                        "statusCode": 200,
                        "message": "Login successful.",
                        "data": {
                            "id": str(user.id),
                            "name": user.get_username(),
                            "email": user.email,
                            "role": user.role,
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "Account is inactive."
                }, status=status.HTTP_403_FORBIDDEN)
        return Response(
            {
                "success": False,
                "statusCode": 401,
                "message": "Invalid credentials."
            }, status=status.HTTP_401_UNAUTHORIZED)

# ============================================ Job Posting API ====================================
class JobPostView(APIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_customer:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "Only customers can post jobs.",
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(
                {
                    "success": True,
                    "statusCode": 201,
                    "message": "Job successfully posted.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "success": False,
                "statusCode": 400,
                "message": "Invalid job data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Job.objects.all()
        customer_id = self.request.query_params.get('customer_id', None)
        status = self.request.query_params.get('status', None)
        location = self.request.query_params.get('location', None)
        min_budget = self.request.query_params.get('min_budget', None)
        max_budget = self.request.query_params.get('max_budget', None)

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        if status:
            queryset = queryset.filter(status=status)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_budget:
            queryset = queryset.filter(budget__gte=min_budget)
        if max_budget:
            queryset = queryset.filter(budget__lte=max_budget)

        return queryset

class JobUpdateView(APIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        job = get_object_or_404(Job, pk=pk, customer=request.user)
        serializer = JobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "statusCode": 200,
                    "message": "Job successfully updated.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "statusCode": 400,
                "message": "Invalid job data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class JobDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk, customer=request.user)
        job.delete()
        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Job successfully deleted.",
            },
            status=status.HTTP_200_OK
        )
# ============================================ Worker Assignment API ====================================
class AssignBidView(APIView):
    permission_classes = []
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        bid_id = request.data.get('bid_id')

        if not bid_id:
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "bid_id is required.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        bid = get_object_or_404(Bid, id=bid_id)
        job = bid.job

        if job.customer != request.user:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "You do not have permission to assign this job.",
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if job.assigned_worker:
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "This job has already been assigned.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.assigned_worker = bid.worker
        job.status = 'in-progress'
        job.save()

        bid.status = "selected"
        bid.save()
        Bid.objects.filter(job=job).exclude(id=bid_id).update(status="ignored")
        serialized_job = JobSerializer(job)

        send_bid_notification(bid.worker.email, job.title)

        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Job successfully assigned.",
                "data": serialized_job.data,
            },
            status=status.HTTP_200_OK
        )

