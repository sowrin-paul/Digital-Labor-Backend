# Digital Labor Backend

A Django REST API backend for a digital labor marketplace platform that connects customers with skilled workers for various jobs and services.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [API Endpoints](#api-endpoints)
- [Models](#models)
- [Authentication](#authentication)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)

## Overview

Digital Labor Backend is a comprehensive platform that facilitates connections between customers who need services and skilled workers who can provide them. The platform supports job posting, bidding, worker verification, payment processing, and review systems.

## Features

### Core Features
- **User Management**: Separate registration and authentication for customers and workers
- **Job Management**: Create, update, delete, and browse job listings
- **Bidding System**: Workers can bid on jobs, customers can select bids
- **Worker Verification**: Admin approval process for worker accounts
- **Payment Processing**: Secure payment handling with multiple payment methods
- **Review System**: Bidirectional reviews between customers and workers
- **Wallet System**: Worker wallet for receiving payments
- **Email Notifications**: Automated notifications for important events

### User Roles
- **Customer**: Can post jobs, select bids, make payments, and review workers
- **Worker**: Can bid on jobs, update profiles, receive payments, and review customers
- **Admin**: Can verify workers and manage the platform

## Technology Stack

- **Backend Framework**: Django 5.2.2
- **API Framework**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens) with SimpleJWT
- **Database**: SQLite (development) - easily configurable for PostgreSQL/MySQL
- **Email**: Django email backend with SMTP support
- **File Upload**: Django file handling for profile pictures
- **CORS**: django-cors-headers for cross-origin requests

## Project Structure

```
Digital-Labor-Backend/
├── backend/
│   ├── manage.py
│   ├── db.sqlite3
│   ├── api/                    # Main API application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API views
│   │   ├── serializers.py     # Data serializers
│   │   ├── urls.py            # URL routing
│   │   ├── utils.py           # Utility functions
│   │   └── migrations/        # Database migrations
│   ├── backend/               # Django project settings
│   │   ├── settings.py        # Project configuration
│   │   ├── urls.py            # Main URL configuration
│   │   └── wsgi.py            # WSGI configuration
│   └── env/                   # Virtual environment
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Digital-Labor-Backend
   ```

2. **Create and activate virtual environment**
   ```bash
   cd backend
   python -m venv env
   
   # On Windows
   env\Scripts\activate
   
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
   ```

4. **Configure environment variables**
   Update `backend/settings.py` with your email configuration:
   ```python
   EMAIL_HOST_USER = 'your_email@example.com'
   EMAIL_HOST_PASSWORD = 'your_email_password'
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Register new user (customer/worker) |
| POST | `/api/login/` | User login |
| POST | `/api/token/` | Obtain JWT token |
| POST | `/api/token/refresh/` | Refresh JWT token |

### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs/` | List all jobs |
| POST | `/api/jobs/create/` | Create new job (customer only) |
| PUT | `/api/jobs/<id>/update/` | Update job (customer only) |
| DELETE | `/api/jobs/<id>/delete/` | Delete job (customer only) |
| POST | `/api/jobs/assign_bid/` | Assign worker to job |
| POST | `/api/jobs/unassign_worker/` | Unassign worker from job |

### Workers & Bidding
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/worker/bid/` | Submit bid on job |
| GET | `/api/worker/job_list/` | Get assigned jobs for worker |
| PUT | `/api/worker/profile/update/` | Update worker profile |
| GET | `/api/customer/jobs/bids/` | Get bids for customer's jobs |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payments/` | Create payment |
| PUT | `/api/jobs/<job_id>/` | Mark job as completed and process payment |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/<job_id>/review_worker/` | Customer reviews worker |
| POST | `/api/jobs/<job_id>/review_customer/` | Worker reviews customer |

## Models

### User Model
Extended Django's AbstractUser with additional fields:
- `is_worker`: Boolean field indicating if user is a worker
- `is_customer`: Boolean field indicating if user is a customer
- `role`: Character field for user role ("worker" or "customer")
- `profile_picture`: Image field for user profile picture

### Worker Model
- `user`: OneToOne relationship with User
- `skills`: Text field for worker skills
- `experience`: Integer field for years of experience
- `location`: Text field for worker location
- `nid`: National ID for verification
- `verified`: Boolean field for admin verification status
- `profile_picture`: Worker-specific profile picture

### Job Model
- `customer`: Foreign key to User (job creator)
- `assigned_worker`: Foreign key to Worker (assigned worker)
- `title`: Job title
- `description`: Job description
- `location`: Job location
- `budget`: Decimal field for job budget
- `urgency`: Integer field for urgency level
- `status`: Choice field ("open", "closed", "completed")

### Bid Model
- `worker`: Foreign key to Worker
- `job`: Foreign key to Job
- `bid_amount`: Decimal field for bid amount
- `status`: Choice field ("selected", "ignored", "not_selected")
- `timestamp`: Auto-generated timestamp

### Payment Model
- `job`: OneToOne relationship with Job
- `amount`: Payment amount
- `method`: Payment method ("bkash", "nagad", "rocket", "cash")
- `status`: Payment status ("pending", "completed")

### Review Model
- `job`: Foreign key to Job
- `reviewer`: User giving the review
- `reviewee`: User receiving the review
- `review_type`: Type of review ("worker" or "customer")
- `rating`: Integer rating
- `comment`: Text comment

### WorkerWallet Model
- `worker`: OneToOne relationship with Worker
- `balance`: Decimal field for wallet balance

## Authentication

The API uses JWT (JSON Web Token) authentication:

1. **Registration**: Users register as either customers or workers
2. **Worker Verification**: Worker accounts require admin approval (`is_active=False` initially)
3. **Login**: Returns access and refresh tokens
4. **Token Usage**: Include access token in Authorization header: `Bearer <token>`
5. **Token Refresh**: Use refresh token to get new access token

### Token Configuration
- Access token lifetime: 360 minutes (6 hours)
- Refresh token lifetime: 1 day

## Usage Examples

### Register a Customer
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "customer1",
    "email": "customer@example.com",
    "password": "strongpassword123",
    "confirmPassword": "strongpassword123",
    "is_customer": true,
    "is_worker": false
  }'
```

### Create a Job
```bash
curl -X POST http://localhost:8000/api/jobs/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "title": "Website Development",
    "description": "Need a responsive website for my business",
    "location": "Dhaka, Bangladesh",
    "budget": 50000.00,
    "urgency": 2
  }'
```

### Submit a Bid
```bash
curl -X POST http://localhost:8000/api/worker/bid/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "job": 1,
    "bid_amount": 45000.00
  }'
```

### Make a Payment
```bash
curl -X POST http://localhost:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "job": 1,
    "amount": 45000.00,
    "method": "bkash"
  }'
```

## Key Features Explained

### Worker Verification System
- Workers register but remain inactive until admin approval
- Verified workers can bid on jobs and receive payments
- Verification can be based on NID and other credentials

### Bidding and Assignment Process
1. Customer posts a job
2. Workers submit bids with their proposed amounts
3. Customer reviews bids and selects a worker
4. System assigns the worker to the job
5. Job status changes from "open" to "closed"

### Payment and Wallet System
- Customers make payments for completed jobs
- Payments are held until job completion
- Upon job completion, funds are released to worker's wallet
- Support for multiple payment methods (bKash, Nagad, Rocket, Cash)

### Review System
- Bidirectional reviews between customers and workers
- Reviews include ratings (1-5) and optional comments
- Reviews are tied to specific jobs for context

### Email Notifications
- Automated notifications for bid selection
- Payment completion notifications
- Configurable SMTP settings for email delivery

## Configuration

### Email Settings
Configure email settings in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@example.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

### CORS Settings
Configure allowed origins for cross-origin requests in `settings.py`.

### Database Configuration
The project uses SQLite by default. For production, configure PostgreSQL or MySQL in `settings.py`.

## Security Considerations

1. **Secret Key**: Change the SECRET_KEY in production
2. **Debug Mode**: Set DEBUG=False in production
3. **Allowed Hosts**: Configure ALLOWED_HOSTS for production
4. **Email Credentials**: Use environment variables for email credentials
5. **Database**: Use a robust database system in production
6. **HTTPS**: Use HTTPS in production for secure token transmission

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Support

For support and questions, please create an issue in the repository or contact the development team.

---

**Note**: This is a development version. For production deployment, ensure proper security configurations, environment variables, and database setup.