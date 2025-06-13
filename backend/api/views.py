from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User, Payment, Job, Worker, Review, Bid
from .serializers import RegisterSerializer, JobSerializer

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

        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Job successfully assigned.",
                "data": {
                    "job_id": job.id,
                    "job_title": job.title,
                    "assigned_worker": bid.worker.user.username,
                    "status": job.status,
                },
            },
            status=status.HTTP_200_OK
        )

