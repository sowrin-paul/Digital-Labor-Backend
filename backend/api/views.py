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
    try:
        send_mail(
            subject="Bid Selected",
            message=f"Your bid for the job '{job_title}' has been selected.",
            from_email="noreply@yourdomain.com",
            recipient_list=[worker_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")

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
                Worker.objects.create(user=user, skills="", experience=0, location="")
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

        title = request.data.get('title')
        description = request.data.get('description')
        if Job.objects.filter(title=title, description=description, customer=request.user).exists():
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "Cannot post duplicate job.",
                },
                status=status.HTTP_400_BAD_REQUEST
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

# to see the list of jobs
class JobListView(generics.ListAPIView):
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

# update job informations
class JobUpdateView(APIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if not request.user.is_customer:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "Only customers can update jobs.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

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

# delete a job
class JobDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        if not request.user.is_customer:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "Only customers can delete jobs.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

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

# ============================================ Worker bidding API ====================================
class WorkerBidView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # post request to the sever for worker to bid
    def post(self, request):
        job_id = request.data.get('job_id')
        bid_amount = request.data.get('bid_amount')
        # print("worker bid view is accessed.")
        if not job_id or not bid_amount:
            return Response({
                    "success": False,
                    "statusCode": 400,
                    "message": "job_id and bid_amount are required.",
                },
                status=status.HTTP_400_BAD_REQUEST)

        job = get_object_or_404(Job, id=job_id)
        # print("worker bid view is accessed.")
        if job.status != 'open':
            return Response({
                    "success": False,
                    "statusCode": 400,
                    "message": "You can only bid on open jobs.",
                },
                status=status.HTTP_400_BAD_REQUEST)

        if job.customer == request.user:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "You cannot bid on your own job.",
                },
                status=status.HTTP_403_FORBIDDEN)

        # worker instance
        worker = get_object_or_404(Worker, user=request.user)

        # same worker can not bid for second time
        if Bid.objects.filter(worker=worker, job=job).exists():
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "You have already placed a bid for this job.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # response get from the server for successful bidding
        bid = Bid.objects.create(worker=worker, job=job, bid_amount=bid_amount)

        return Response(
            {
                "success": True,
                "statusCode": 201,
                "message": "Bid successfully submitted.",
                "data": {
                    "bid_id": bid.id,
                    "job_id": job.id,
                    "job_title": job.title,
                    "bid_amount": bid.bid_amount,
                    "status": bid.status,
                },
            },
            status=status.HTTP_201_CREATED)

# ============================================ Worker assign API ====================================
class AssignWorkerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    # worker assignment to the job
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

        # only customers can assign the worker
        if job.customer != request.user:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "You do not have permission to assign this job.",
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # if job is assigned to any worker
        if job.assigned_worker:
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "This job has already been assigned.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # if the job is already assigned
        if job.assigned_worker:
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "This job has already been assigned.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # if the job is in progress
        job.assigned_worker = bid.worker
        job.status = 'in-progress'
        job.save()

        # if the bid is selected
        bid.status = "selected"
        bid.save()
        Bid.objects.filter(job=job).exclude(id=bid_id).update(status="ignored")
        serialized_job = JobSerializer(job)

        # an email notification will send to the worker email if his bid is accepted
        send_bid_notification(bid.worker.user.email, job.title)

        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Job successfully assigned.",
                "data": serialized_job.data,
            },
            status=status.HTTP_200_OK
        )

# ========================================== Bid list view ====================================
class JobBidListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_customer:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "Only customers can view bid counts for their jobs.",
                },
                status=status.HTTP_403_FORBIDDEN)

        jobs = Job.objects.filter(customer=request.user) # job bid filtering for each customer
        job_bids = [
            {
                "job_id": job.id,
                "job_title": job.title,
                "bid_count": job.bids.count(),
                "bids": [
                    {
                        "bid_id": bid.id,
                        "bid_amount": bid.bid_amount,
                        "worker": {
                            "worker_id": bid.worker.id,
                            "username": bid.worker.user.username,
                            "skills": bid.worker.skills,
                            "experience": bid.worker.experience,
                            "location": bid.worker.location,
                        },
                    }
                    for bid in job.bids.all()
                ],
            }
            for job in jobs
        ]
        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Bid counts retrieved successfully.",
                "data": job_bids,
            },
            status=status.HTTP_200_OK,)

# =========================================== Worker Profile update view ======================================
class WorkerProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        if not request.user.is_worker:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "Only workers can update their profile.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        worker = get_object_or_404(Worker, user=request.user)
        data = request.data

        # worker profile fields that can be updated
        worker.skills = data.get("skills", worker.skills)
        worker.experience = data.get("experience", worker.experience)
        worker.location = data.get("location", worker.location)
        worker.nid = data.get("nid", worker.nid)
        worker.profile_picture = data.get("profile_picture", worker.profile_picture)
        worker.save()

        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Worker profile updated successfully.",
                "data": {
                    "worker_id": worker.id,
                    "username": worker.user.username,
                    "skills": worker.skills,
                    "experience": worker.experience,
                    "location": worker.location,
                    "nid": worker.nid,
                },
            },
            status=status.HTTP_200_OK,
        )

# ============================================== Unassign worker ======================================
class UnassignWorkerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        job_id = request.data.get('job_id')

        # Validate job_id
        if not job_id:
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "job_id is required.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the job
        job = get_object_or_404(Job, id=job_id)

        # Ensure only the customer who created the job can unassign workers
        if job.customer != request.user:
            return Response(
                {
                    "success": False,
                    "statusCode": 403,
                    "message": "You do not have permission to unassign workers from this job.",
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if the job has an assigned worker
        if not job.assigned_worker:
            return Response(
                {
                    "success": False,
                    "statusCode": 400,
                    "message": "No worker is assigned to this job.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Unassign the worker and update the job status
        job.assigned_worker = None
        job.status = 'open'  # Reset the job status to "open"
        job.save()

        return Response(
            {
                "success": True,
                "statusCode": 200,
                "message": "Worker successfully unassigned from the job.",
                "data": {
                    "job_id": job.id,
                    "job_title": job.title,
                    "status": job.status,
                },
            },
            status=status.HTTP_200_OK
        )