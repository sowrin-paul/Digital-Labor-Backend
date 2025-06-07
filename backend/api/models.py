from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_worker = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField()
    experience =  models.PositiveIntegerField()
    location = models.TextField(max_length=100, blank=True, null=True)
    nid = models.CharField(max_length=20, blank=True, null=True)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Job(models.Model):
    STATUS_CHOICE = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("completed", "Completed"),
    ]

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

class Bid(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="bids")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.user.username} -> {self.job.title}"

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

class Review(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="review")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.job.title}"
