from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Worker, User, Job, Payment, Bid, Review

admin.site.register(User, UserAdmin)
admin.site.register(Worker)
admin.site.register(Job)
admin.site.register(Bid)
admin.site.register(Payment)
admin.site.register(Review)