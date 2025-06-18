from pyexpat.errors import messages
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from .models import Worker, User, Job, Payment, Bid, Review
from .utils import release_funds

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_worker", "is_customer", "is_staff",)
    list_filter = ("is_worker", "is_customer", "is_staff",)
    search_fields = ("username", "email",)
    actions = ['suspend_users', 'activate_users', 'approve_workers']

    def suspend_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} user(s) suspended.')

    # def activate_users(self, request, queryset):
    #     queryset.update(is_active=True)
    #     self.message_user(request, f'{queryset.count()} user(s) re-activated.')

    def approve_workers(self, request, queryset):
        workers = queryset.filter(is_worker=True, is_active=False)
        count = workers.update(is_active=True)
        self.message_user(request, f"{count} worker(s) approved.")

    approve_workers.short_description = "Approve selected workers"
    suspend_users.short_description = "Suspend selected users"
    # activate_users.short_description = "Activate selected users"

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("user", "location", "verified", "experience",)
    list_filter = ("verified", "location",)
    search_fields = ("user__username", "location",)
    actions = ["verify_workers"]

    def verify_worker(self, request, queryset):
        updated = queryset.update(verified=True)
        self.message_user(request, f"{updated} workers marked as verified.")
    verify_worker.short_description = "Mark selected worker as verified."

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "customer", "location", "budget", "status", "created_at",)
    list_filter = ("status", "location",)
    search_fields = ("title", "customer__username", "location",)
    date_hierarchy = "created_at"
    actions = ['print_popular_jobs']

    def print_popular_jobs(self, request, queryset):
        popular = queryset.values('title').annotate(count=Count('id')).order_by('-count')[:5]
        for job in popular:
            self.message_user(request, f"{job['title']}: {job['count']} postings")
    print_popular_jobs.short_description = "Show Top 5 Popular Job Titles"

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("job", "worker", "bid_amount", "timestamp",)
    list_filter = ("timestamp",)
    search_fields = ("worker__user__username", "job__title",)

    def most_hired_workers(self, request, queryset):
        top_workers = queryset.values('worker__user__username') \
                               .annotate(count=Count('id')) \
                               .order_by('-count')[:5]
        for worker in top_workers:
            self.message_user(request, f"{worker['worker__user__username']} - {worker['count']} jobs")
    most_hired_workers.short_description = "Show Top 5 Most Hired Workers"

@admin.register(Review)
class Review(admin.ModelAdmin):
    list_display = ('job', 'reviewer', 'rating', 'created_at',)
    list_filter = ('rating',)
    search_fields = ('reviewer__username', 'job__title',)
    date_hierarchy = 'created_at'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('job', 'amount', 'method', 'status', 'created_at')
    list_filter = ('status', 'method')
    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        updated = 0
        for payment in queryset:
            if payment.status != 'completed':
                payment.status = 'completed'
                payment.save()
                # Update job status
                job = payment.job
                job.status = 'completed'
                job.save()
                updated += 1
        self.message_user(request, f'{updated} payment(s) marked as completed and jobs updated.')
    mark_as_completed.short_description = "Mark selected payments as completed"

    def release_payment(modeladmin, request, queryset):
        for payment in queryset:
            try:
                release_funds(payment)
            except Exception as e:
                modeladmin.message_user(request, f"Error: {e}", level=messages.ERROR)

    release_payment.short_description = "Release escrow to worker"
