def release_funds(payment):
    if payment.status != 'pending':
        raise Exception("Payment already released or invalid.")

    worker_wallet = WorkerWallet.objects.get(worker=payment.job.assigned_worker)
    worker_wallet.balance += payment.amount
    worker_wallet.save()

    payment.status = 'completed'
    payment.save()
