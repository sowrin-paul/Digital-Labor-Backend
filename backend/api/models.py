from django.db import models
from django.contrib.auth.models import AbstractUser

# ==================================== User model =================================
class User(AbstractUser):
    ROLE_CHOICES = [
        ("worker", "Worker"),
        ("customer", "Customer"),
    ]
    is_worker = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_worker:
            self.role = "worker"
            self.is_active = False
        elif self.is_customer:
            self.role = "customer"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

# ==================================== Worker model =================================
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField()
    experience =  models.PositiveIntegerField()
    location = models.TextField(max_length=100, blank=True, null=True)
    nid = models.CharField(max_length=20, blank=True, null=True)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

# ==================================== Job model =================================
class Job(models.Model):
    STATUS_CHOICE = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("completed", "Completed"),
    ]

    assigned_worker = models.ForeignKey(
        'Worker',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assigned_jobs',
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=255)
    location = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    urgency = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ==================================== Bid model =================================
class Bid(models.Model):
    STATUS_CHOICE = [
        ("selected", "Selected"),
        ("ignored", "Ignored"),
        ("not_selected", "Not Selected"),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="bids")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default="not_selected")
    def __str__(self):
        return f"{self.worker.user.username} -> {self.job.title}"

# ==================================== Payment model =================================
class Payment(models.Model):
    STATUS_CHOICE = [
        ("pending", "Pending"),
        ("completed", "Completed"),
    ]
    METHOD_CHOICE = [
        ("bkash", "BKash"),
        ("nagad", "Nagad"),
        ("rocket", "Rocket"),
        ("cash", "Cash"),
    ]

    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} - {self.method}"

# ==================================== Review model =================================
class Review(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="review")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.job.title}"
