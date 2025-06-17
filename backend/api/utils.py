from django.core.mail import send_mail

def release_funds(payment):
    if payment.status != 'pending':
        raise Exception("Payment already released or invalid.")

    worker_wallet = WorkerWallet.objects.get(worker=payment.job.assigned_worker)
    worker_wallet.balance += payment.amount
    worker_wallet.save()

    payment.status = 'completed'
    payment.save()

def send_payment_notification(customer_email, worker_email, job_title, amount):
    try:
        # Notify the customer
        send_mail(
            subject="Payment Completed",
            message=f"Your payment of {amount} for the job '{job_title}' has been successfully completed.",
            from_email="noreply@yourdomain.com",
            recipient_list=[customer_email],
            fail_silently=False,
        )

        # Notify the worker
        send_mail(
            subject="Payment Received",
            message=f"You have received a payment of {amount} for the job '{job_title}'.",
            from_email="noreply@yourdomain.com",
            recipient_list=[worker_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send payment notification: {e}")