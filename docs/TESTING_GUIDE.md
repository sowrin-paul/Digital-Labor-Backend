# Digital Labor Backend - Testing Guide

## Table of Contents

- [Testing Overview](#testing-overview)
- [Test Structure](#test-structure)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [API Testing](#api-testing)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [Test Data Management](#test-data-management)
- [Continuous Integration](#continuous-integration)
- [Test Coverage](#test-coverage)

## Testing Overview

This guide covers comprehensive testing strategies for the Digital Labor Backend application. The testing suite includes unit tests, integration tests, API tests, and performance tests to ensure the application's reliability and security.

### Testing Framework

The application uses Django's built-in testing framework, which is based on Python's `unittest` module, along with additional tools:

- **Django TestCase**: For database-dependent tests
- **Django APITestCase**: For API endpoint testing
- **Factory Boy**: For test data generation
- **Coverage.py**: For test coverage analysis
- **pytest-django**: Alternative test runner (optional)

## Test Structure

```
backend/
├── api/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_serializers.py
│   │   ├── test_utils.py
│   │   ├── test_authentication.py
│   │   └── factories.py
│   └── tests.py  # Default Django test file
├── manage.py
└── requirements-test.txt
```

### Test Configuration

Create `backend/settings/test.py`:

```python
from .base import *

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Disable email sending in tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable CSRF for API tests
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'rest_framework.authentication.SessionAuthentication',
]

# Use weak password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
}

# Test media files
MEDIA_ROOT = '/tmp/test_media/'
```

## Unit Tests

### Model Tests

Create `api/tests/test_models.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from decimal import Decimal
from api.models import User, Worker, Job, Bid, Payment, Review, WorkerWallet

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.customer_data = {
            'username': 'customer1',
            'email': 'customer@example.com',
            'password': 'testpass123',
            'is_customer': True,
            'is_worker': False
        }
        self.worker_data = {
            'username': 'worker1',
            'email': 'worker@example.com',
            'password': 'testpass123',
            'is_customer': False,
            'is_worker': True
        }

    def test_create_customer_user(self):
        user = User.objects.create_user(**self.customer_data)
        self.assertEqual(user.username, 'customer1')
        self.assertEqual(user.role, 'customer')
        self.assertTrue(user.is_customer)
        self.assertFalse(user.is_worker)
        self.assertTrue(user.is_active)

    def test_create_worker_user(self):
        user = User.objects.create_user(**self.worker_data)
        self.assertEqual(user.username, 'worker1')
        self.assertEqual(user.role, 'worker')
        self.assertFalse(user.is_customer)
        self.assertTrue(user.is_worker)
        self.assertFalse(user.is_active)  # Workers start inactive

    def test_user_str_method(self):
        user = User.objects.create_user(**self.customer_data)
        self.assertEqual(str(user), 'customer1')

class WorkerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='worker1',
            email='worker@example.com',
            password='testpass123',
            is_worker=True
        )

    def test_create_worker(self):
        worker = Worker.objects.create(
            user=self.user,
            skills='Python, Django, React',
            experience=3,
            location='Dhaka, Bangladesh'
        )
        self.assertEqual(worker.user, self.user)
        self.assertEqual(worker.skills, 'Python, Django, React')
        self.assertEqual(worker.experience, 3)
        self.assertFalse(worker.verified)

    def test_worker_str_method(self):
        worker = Worker.objects.create(
            user=self.user,
            skills='Python',
            experience=1
        )
        self.assertEqual(str(worker), 'worker1')

class JobModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )

    def test_create_job(self):
        job = Job.objects.create(
            customer=self.customer,
            title='Website Development',
            description='Need a website',
            location='Remote',
            budget=Decimal('50000.00'),
            urgency=2
        )
        self.assertEqual(job.customer, self.customer)
        self.assertEqual(job.title, 'Website Development')
        self.assertEqual(job.status, 'open')
        self.assertIsNone(job.assigned_worker)

    def test_job_str_method(self):
        job = Job.objects.create(
            customer=self.customer,
            title='Test Job',
            description='Test description',
            location='Test location',
            budget=Decimal('1000.00')
        )
        self.assertEqual(str(job), 'Test Job')

class BidModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.worker_user = User.objects.create_user(
            username='worker1',
            email='worker@example.com',
            password='testpass123',
            is_worker=True
        )
        self.worker = Worker.objects.create(
            user=self.worker_user,
            skills='Python',
            experience=2
        )
        self.job = Job.objects.create(
            customer=self.customer,
            title='Test Job',
            description='Test description',
            location='Test location',
            budget=Decimal('50000.00')
        )

    def test_create_bid(self):
        bid = Bid.objects.create(
            worker=self.worker,
            job=self.job,
            bid_amount=Decimal('45000.00')
        )
        self.assertEqual(bid.worker, self.worker)
        self.assertEqual(bid.job, self.job)
        self.assertEqual(bid.bid_amount, Decimal('45000.00'))
        self.assertEqual(bid.status, 'not_selected')

    def test_bid_str_method(self):
        bid = Bid.objects.create(
            worker=self.worker,
            job=self.job,
            bid_amount=Decimal('45000.00')
        )
        self.assertEqual(str(bid), 'worker1 -> Test Job')

class PaymentModelTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.job = Job.objects.create(
            customer=self.customer,
            title='Test Job',
            description='Test description',
            location='Test location',
            budget=Decimal('50000.00')
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            job=self.job,
            amount=Decimal('45000.00'),
            method='bkash'
        )
        self.assertEqual(payment.job, self.job)
        self.assertEqual(payment.amount, Decimal('45000.00'))
        self.assertEqual(payment.method, 'bkash')
        self.assertEqual(payment.status, 'pending')

    def test_payment_str_method(self):
        payment = Payment.objects.create(
            job=self.job,
            amount=Decimal('45000.00'),
            method='bkash'
        )
        self.assertEqual(str(payment), 'Test Job - bkash')
```

### Utility Tests

Create `api/tests/test_utils.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch, Mock
from api.models import User, Worker, Job, Payment, WorkerWallet
from api.utils import release_funds, send_payment_notification

User = get_user_model()

class UtilsTest(TestCase):
    def setUp(self):
        # Create customer
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        # Create worker
        self.worker_user = User.objects.create_user(
            username='worker1',
            email='worker@example.com',
            password='testpass123',
            is_worker=True
        )
        self.worker = Worker.objects.create(
            user=self.worker_user,
            skills='Python',
            experience=2
        )
        self.wallet = WorkerWallet.objects.create(
            worker=self.worker,
            balance=Decimal('0.00')
        )
        
        # Create job
        self.job = Job.objects.create(
            customer=self.customer,
            title='Test Job',
            description='Test description',
            location='Test location',
            budget=Decimal('50000.00'),
            assigned_worker=self.worker
        )
        
        # Create payment
        self.payment = Payment.objects.create(
            job=self.job,
            amount=Decimal('45000.00'),
            method='bkash',
            status='pending'
        )

    def test_release_funds_success(self):
        initial_balance = self.wallet.balance
        release_funds(self.payment)
        
        # Refresh from database
        self.wallet.refresh_from_db()
        self.payment.refresh_from_db()
        
        # Check if funds were released
        self.assertEqual(
            self.wallet.balance, 
            initial_balance + self.payment.amount
        )
        self.assertEqual(self.payment.status, 'completed')

    def test_release_funds_already_completed(self):
        self.payment.status = 'completed'
        self.payment.save()
        
        with self.assertRaises(Exception) as context:
            release_funds(self.payment)
        
        self.assertIn('Payment already released', str(context.exception))

    @patch('api.utils.send_mail')
    def test_send_payment_notification_success(self, mock_send_mail):
        mock_send_mail.return_value = True
        
        send_payment_notification(
            customer_email='customer@example.com',
            worker_email='worker@example.com',
            job_title='Test Job',
            amount=Decimal('45000.00')
        )
        
        # Verify send_mail was called twice (customer and worker)
        self.assertEqual(mock_send_mail.call_count, 2)

    @patch('api.utils.send_mail')
    def test_send_payment_notification_failure(self, mock_send_mail):
        mock_send_mail.side_effect = Exception('Email service down')
        
        # Should not raise exception, just print error
        send_payment_notification(
            customer_email='customer@example.com',
            worker_email='worker@example.com',
            job_title='Test Job',
            amount=Decimal('45000.00')
        )
        
        self.assertEqual(mock_send_mail.call_count, 1)
```

## Integration Tests

### API Tests

Create `api/tests/test_views.py`:

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from api.models import User, Worker, Job, Bid, Payment

User = get_user_model()

class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.customer_data = {
            'username': 'customer1',
            'email': 'customer@example.com',
            'password': 'testpass123',
            'confirmPassword': 'testpass123',
            'is_customer': True,
            'is_worker': False
        }

    def test_register_customer_success(self):
        response = self.client.post(self.register_url, self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['role'], 'customer')

    def test_register_password_mismatch(self):
        data = self.customer_data.copy()
        data['confirmPassword'] = 'wrongpassword'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        # First register a user
        user = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        
        login_data = {
            'username': 'customer1',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])

    def test_login_invalid_credentials(self):
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class JobAPITest(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.worker_user = User.objects.create_user(
            username='worker1',
            email='worker@example.com',
            password='testpass123',
            is_worker=True,
            is_active=True
        )
        self.worker = Worker.objects.create(
            user=self.worker_user,
            skills='Python',
            experience=2,
            verified=True
        )
        
        self.job_list_url = reverse('job-list')
        self.job_create_url = reverse('job-create')

    def test_list_jobs_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_jobs_unauthenticated(self):
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_job_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        job_data = {
            'title': 'Website Development',
            'description': 'Need a responsive website',
            'location': 'Remote',
            'budget': 50000.00,
            'urgency': 2
        }
        response = self.client.post(self.job_create_url, job_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Website Development')

    def test_create_job_as_worker_forbidden(self):
        self.client.force_authenticate(user=self.worker_user)
        job_data = {
            'title': 'Website Development',
            'description': 'Need a responsive website',
            'location': 'Remote',
            'budget': 50000.00,
            'urgency': 2
        }
        response = self.client.post(self.job_create_url, job_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class BiddingAPITest(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.worker_user = User.objects.create_user(
            username='worker1',
            email='worker@example.com',
            password='testpass123',
            is_worker=True,
            is_active=True
        )
        self.worker = Worker.objects.create(
            user=self.worker_user,
            skills='Python',
            experience=2,
            verified=True
        )
        self.job = Job.objects.create(
            customer=self.customer,
            title='Test Job',
            description='Test description',
            location='Remote',
            budget=Decimal('50000.00')
        )
        
        self.bid_url = reverse('worker-bid')

    def test_submit_bid_as_worker(self):
        self.client.force_authenticate(user=self.worker_user)
        bid_data = {
            'job': self.job.id,
            'bid_amount': 45000.00
        }
        response = self.client.post(self.bid_url, bid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submit_bid_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer)
        bid_data = {
            'job': self.job.id,
            'bid_amount': 45000.00
        }
        response = self.client.post(self.bid_url, bid_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_duplicate_bid(self):
        # First bid
        self.client.force_authenticate(user=self.worker_user)
        bid_data = {
            'job': self.job.id,
            'bid_amount': 45000.00
        }
        response1 = self.client.post(self.bid_url, bid_data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Duplicate bid
        response2 = self.client.post(self.bid_url, bid_data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

class PaymentAPITest(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            is_customer=True
        )
        self.worker_user = User.objects.create_user(
            username='worker1',
            email='worker@example.com',
            password='testpass123',
            is_worker=True,
            is_active=True
        )
        self.worker = Worker.objects.create(
            user=self.worker_user,
            skills='Python',
            experience=2,
            verified=True
        )
        self.job = Job.objects.create(
            customer=self.customer,
            title='Test Job',
            description='Test description',
            location='Remote',
            budget=Decimal('50000.00'),
            assigned_worker=self.worker,
            status='closed'
        )
        
        self.payment_url = reverse('payment-create')

    def test_create_payment_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        payment_data = {
            'job': self.job.id,
            'amount': 45000.00,
            'method': 'bkash'
        }
        response = self.client.post(self.payment_url, payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_payment_invalid_method(self):
        self.client.force_authenticate(user=self.customer)
        payment_data = {
            'job': self.job.id,
            'amount': 45000.00,
            'method': 'invalid_method'
        }
        response = self.client.post(self.payment_url, payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

## API Testing

### Test Factories

Create `api/tests/factories.py` for generating test data:

```python
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from decimal import Decimal
from api.models import User, Worker, Job, Bid, Payment, Review

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class CustomerFactory(UserFactory):
    is_customer = True
    is_worker = False
    role = 'customer'
    is_active = True

class WorkerUserFactory(UserFactory):
    is_customer = False
    is_worker = True
    role = 'worker'
    is_active = True

class WorkerFactory(DjangoModelFactory):
    class Meta:
        model = Worker

    user = factory.SubFactory(WorkerUserFactory)
    skills = factory.Faker('text', max_nb_chars=200)
    experience = factory.Faker('random_int', min=0, max=20)
    location = factory.Faker('city')
    verified = True

class JobFactory(DjangoModelFactory):
    class Meta:
        model = Job

    customer = factory.SubFactory(CustomerFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=250)
    location = factory.Faker('city')
    budget = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    urgency = factory.Faker('random_int', min=1, max=5)
    status = 'open'

class BidFactory(DjangoModelFactory):
    class Meta:
        model = Bid

    worker = factory.SubFactory(WorkerFactory)
    job = factory.SubFactory(JobFactory)
    bid_amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    status = 'not_selected'

class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    job = factory.SubFactory(JobFactory)
    amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    method = factory.Faker('random_element', elements=('bkash', 'nagad', 'rocket', 'cash'))
    status = 'pending'
```

### Using Factories in Tests

```python
from django.test import TestCase
from api.tests.factories import CustomerFactory, WorkerFactory, JobFactory, BidFactory

class FactoryTest(TestCase):
    def test_create_customer_with_factory(self):
        customer = CustomerFactory()
        self.assertTrue(customer.is_customer)
        self.assertFalse(customer.is_worker)

    def test_create_job_with_bids(self):
        job = JobFactory()
        worker1 = WorkerFactory()
        worker2 = WorkerFactory()
        
        bid1 = BidFactory(job=job, worker=worker1, bid_amount=45000)
        bid2 = BidFactory(job=job, worker=worker2, bid_amount=40000)
        
        self.assertEqual(job.bids.count(), 2)
        self.assertEqual(bid1.job, job)
        self.assertEqual(bid2.job, job)
```

## Performance Testing

### Load Testing with Locust

Create `tests/locustfile.py`:

```python
from locust import HttpUser, task, between
import json

class DigitalLaborUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Register and login
        self.register_and_login()
    
    def register_and_login(self):
        # Register a customer
        register_data = {
            "username": f"customer_{self.environment.runner.user_count}",
            "email": f"customer_{self.environment.runner.user_count}@example.com",
            "password": "testpass123",
            "confirmPassword": "testpass123",
            "is_customer": True,
            "is_worker": False
        }
        
        response = self.client.post("/api/register/", json=register_data)
        if response.status_code == 201:
            data = response.json()
            self.access_token = data['data']['access']
            self.headers = {'Authorization': f'Bearer {self.access_token}'}
    
    @task(3)
    def list_jobs(self):
        self.client.get("/api/jobs/", headers=self.headers)
    
    @task(1)
    def create_job(self):
        job_data = {
            "title": "Test Job",
            "description": "This is a test job",
            "location": "Remote",
            "budget": 50000.00,
            "urgency": 2
        }
        self.client.post("/api/jobs/create/", json=job_data, headers=self.headers)
    
    @task(2)
    def view_job_bids(self):
        self.client.get("/api/customer/jobs/bids/", headers=self.headers)
```

Run load tests:
```bash
locust -f tests/locustfile.py --host=http://localhost:8000
```

### Database Performance Tests

```python
from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import override_settings
from api.tests.factories import JobFactory, BidFactory
from api.models import Job

class DatabasePerformanceTest(TestCase):
    def test_job_list_query_count(self):
        # Create test data
        jobs = JobFactory.create_batch(50)
        for job in jobs[:25]:
            BidFactory.create_batch(5, job=job)
        
        with self.assertNumQueries(2):  # Should use select_related/prefetch_related
            list(Job.objects.select_related('customer', 'assigned_worker')
                             .prefetch_related('bids__worker__user'))

    def test_large_dataset_performance(self):
        # Create large dataset
        jobs = JobFactory.create_batch(1000)
        
        # Measure query time
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_job WHERE status = 'open'")
            result = cursor.fetchone()
        
        self.assertIsNotNone(result)
```

## Security Testing

### Authentication Security Tests

```python
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.tests.factories import CustomerFactory, WorkerFactory

class SecurityTest(APITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.worker_user = WorkerFactory().user
        
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        protected_urls = [
            reverse('job-create'),
            reverse('worker-bid'),
            reverse('payment-create'),
        ]
        
        for url in protected_urls:
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_role_based_access_control(self):
        """Test that users can only access endpoints appropriate to their role"""
        
        # Customer trying to submit bid (should fail)
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(reverse('worker-bid'), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Worker trying to create job (should fail)
        self.client.force_authenticate(user=self.worker_user)
        response = self.client.post(reverse('job-create'), {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_jwt_token_expiration(self):
        """Test JWT token expiration handling"""
        # This would require mocking time or using expired tokens
        pass
    
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        weak_passwords = [
            '123',
            'password',
            '12345678',
            'qwerty'
        ]
        
        for weak_password in weak_passwords:
            register_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': weak_password,
                'confirmPassword': weak_password,
                'is_customer': True,
                'is_worker': False
            }
            response = self.client.post(reverse('register'), register_data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

### Input Validation Tests

```python
class InputValidationTest(APITestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.client.force_authenticate(user=self.customer)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        malicious_inputs = [
            "'; DROP TABLE api_job; --",
            "1' OR '1'='1",
            "admin'/*",
            "'; INSERT INTO api_job (title) VALUES ('hacked'); --"
        ]
        
        for malicious_input in malicious_inputs:
            job_data = {
                'title': malicious_input,
                'description': 'Test description',
                'location': 'Test location',
                'budget': 1000.00,
                'urgency': 1
            }
            response = self.client.post(reverse('job-create'), job_data)
            # Should either create job safely or reject input
            self.assertIn(response.status_code, [200, 201, 400])
    
    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        xss_inputs = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//",
        ]
        
        for xss_input in xss_inputs:
            job_data = {
                'title': xss_input,
                'description': 'Test description',
                'location': 'Test location',
                'budget': 1000.00,
                'urgency': 1
            }
            response = self.client.post(reverse('job-create'), job_data)
            if response.status_code in [200, 201]:
                # If job was created, verify XSS was properly escaped
                job_id = response.data.get('id')
                job_response = self.client.get(reverse('job-list'))
                self.assertNotIn('<script>', str(job_response.content))
```

## Test Data Management

### Test Database Setup

```python
# conftest.py for pytest
import pytest
from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup():
    """Custom database setup for tests"""
    from django.conf import settings
    from django.test.utils import setup_test_environment, teardown_test_environment
    
    setup_test_environment()
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
    
    call_command('migrate', '--run-syncdb')

@pytest.fixture
def sample_data():
    """Fixture to create sample test data"""
    from api.tests.factories import CustomerFactory, WorkerFactory, JobFactory
    
    customers = CustomerFactory.create_batch(3)
    workers = WorkerFactory.create_batch(5)
    jobs = JobFactory.create_batch(10)
    
    return {
        'customers': customers,
        'workers': workers,
        'jobs': jobs
    }
```

### Test Data Cleanup

```python
from django.test import TransactionTestCase
from django.core.management import call_command

class CleanupMixin:
    """Mixin to ensure proper test data cleanup"""
    
    def setUp(self):
        super().setUp()
        self.created_objects = []
    
    def tearDown(self):
        # Clean up any created objects
        for obj in reversed(self.created_objects):
            try:
                obj.delete()
            except:
                pass
        super().tearDown()
    
    def track_object(self, obj):
        """Track object for cleanup"""
        self.created_objects.append(obj)
        return obj
```

## Continuous Integration

### GitHub Actions Configuration

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_digitallabor
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements-test.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_digitallabor
      run: |
        cd backend
        python manage.py test --settings=backend.settings.test
    
    - name: Generate coverage report
      run: |
        cd backend
        coverage run --source='.' manage.py test --settings=backend.settings.test
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./backend/coverage.xml
```

## Test Coverage

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = .
omit = 
    */migrations/*
    */venv/*
    */env/*
    */tests/*
    manage.py
    */settings/*
    */wsgi.py
    */asgi.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

### Running Coverage Tests

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test --settings=backend.settings.test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html

# Generate XML coverage report (for CI)
coverage xml
```

### Coverage Targets

Aim for the following coverage targets:

- **Overall Coverage**: 90%+
- **Models**: 95%+
- **Views**: 85%+
- **Utils**: 90%+
- **Serializers**: 80%+

### Running All Tests

```bash
# Run all tests
python manage.py test --settings=backend.settings.test

# Run specific test file
python manage.py test api.tests.test_models --settings=backend.settings.test

# Run with verbose output
python manage.py test --verbosity=2 --settings=backend.settings.test

# Run tests in parallel
python manage.py test --parallel --settings=backend.settings.test

# Run only failed tests
python manage.py test --failfast --settings=backend.settings.test
```

This comprehensive testing guide ensures that the Digital Labor Backend application is thoroughly tested at all levels, from unit tests to integration tests, security tests, and performance tests. Regular testing helps maintain code quality and prevents regressions.
