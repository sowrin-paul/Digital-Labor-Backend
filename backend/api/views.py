from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import User, Payment, Job, Worker, Review
from .serializers import RegisterSerializer

class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            if user.is_worker:
                return Response(
                    {
                        "message": "Registration successful. Your account will be activated after admin approval.",
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {
                    "message": "User registered successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)