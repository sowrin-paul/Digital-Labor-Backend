# Digital Labor Backend - API Documentation

## Table of Contents

- [Authentication](#authentication)
- [User Registration & Login](#user-registration--login)
- [Job Management](#job-management)
- [Worker Operations](#worker-operations)
- [Bidding System](#bidding-system)
- [Payment Processing](#payment-processing)
- [Review System](#review-system)
- [Error Handling](#error-handling)
- [Response Formats](#response-formats)

## Authentication

The API uses JWT (JSON Web Token) authentication. All authenticated endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Endpoints

#### Obtain Token
- **URL**: `/api/token/`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- **Success Response**:
  ```json
  {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```

#### Refresh Token
- **URL**: `/api/token/refresh/`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```

## User Registration & Login

### Register User
- **URL**: `/api/register/`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "confirmPassword": "SecurePass123",
    "is_worker": false,
    "is_customer": true,
    "profile_picture": null
  }
  ```
- **Success Response** (201):
  ```json
  {
    "success": true,
    "statusCode": 201,
    "message": "User registered successfully.",
    "data": {
      "id": "1",
      "name": "john_doe",
      "email": "john@example.com",
      "role": "customer",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
  ```

### Login User
- **URL**: `/api/login/`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username": "john_doe",
    "password": "SecurePass123"
  }
  ```
- **Success Response** (200):
  ```json
  {
    "success": true,
    "statusCode": 200,
    "message": "Login successful.",
    "data": {
      "id": "1",
      "name": "john_doe",
      "email": "john@example.com",
      "role": "customer",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
  ```

## Job Management

### List All Jobs
- **URL**: `/api/jobs/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response** (200):
  ```json
  [
    {
      "id": 1,
      "title": "Website Development",
      "description": "Need a responsive website for my business",
      "location": "Dhaka, Bangladesh",
      "budget": "50000.00",
      "status": "open",
      "assigned_worker": null
    }
  ]
  ```

### Create Job
- **URL**: `/api/jobs/create/`
- **Method**: `POST`
- **Auth Required**: Yes (Customer only)
- **Body**:
  ```json
  {
    "title": "Mobile App Development",
    "description": "Create a mobile app for iOS and Android",
    "location": "Remote",
    "budget": 75000.00,
    "urgency": 3
  }
  ```
- **Success Response** (201):
  ```json
  {
    "id": 2,
    "title": "Mobile App Development",
    "description": "Create a mobile app for iOS and Android",
    "location": "Remote",
    "budget": "75000.00",
    "status": "open",
    "assigned_worker": null
  }
  ```

### Update Job
- **URL**: `/api/jobs/<id>/update/`
- **Method**: `PUT`
- **Auth Required**: Yes (Job owner only)
- **Body**:
  ```json
  {
    "title": "Updated Job Title",
    "description": "Updated description",
    "budget": 60000.00
  }
  ```

### Delete Job
- **URL**: `/api/jobs/<id>/delete/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Job owner only)
- **Success Response** (204): No content

## Worker Operations

### Update Worker Profile
- **URL**: `/api/worker/profile/update/`
- **Method**: `PUT`
- **Auth Required**: Yes (Worker only)
- **Body**:
  ```json
  {
    "skills": "Python, Django, React, Node.js",
    "experience": 3,
    "location": "Dhaka, Bangladesh",
    "nid": "1234567890123"
  }
  ```

### Get Worker's Assigned Jobs
- **URL**: `/api/worker/job_list/`
- **Method**: `GET`
- **Auth Required**: Yes (Worker only)
- **Success Response** (200):
  ```json
  [
    {
      "id": 1,
      "title": "Website Development",
      "description": "Need a responsive website",
      "location": "Dhaka",
      "budget": "50000.00",
      "status": "closed",
      "assigned_worker": {
        "id": 1,
        "username": "worker1",
        "skills": "Python, Django",
        "experience": 3,
        "location": "Dhaka"
      }
    }
  ]
  ```

## Bidding System

### Submit Bid
- **URL**: `/api/worker/bid/`
- **Method**: `POST`
- **Auth Required**: Yes (Worker only)
- **Body**:
  ```json
  {
    "job": 1,
    "bid_amount": 45000.00
  }
  ```
- **Success Response** (201):
  ```json
  {
    "success": true,
    "message": "Bid submitted successfully",
    "bid_id": 1
  }
  ```

### Get Job Bids (Customer)
- **URL**: `/api/customer/jobs/bids/`
- **Method**: `GET`
- **Auth Required**: Yes (Customer only)
- **Success Response** (200):
  ```json
  [
    {
      "job_id": 1,
      "job_title": "Website Development",
      "bids": [
        {
          "id": 1,
          "worker": {
            "username": "worker1",
            "skills": "Python, Django",
            "experience": 3
          },
          "bid_amount": "45000.00",
          "status": "not_selected",
          "timestamp": "2025-01-01T10:00:00Z"
        }
      ]
    }
  ]
  ```

### Assign Worker to Job
- **URL**: `/api/jobs/assign_bid/`
- **Method**: `POST`
- **Auth Required**: Yes (Customer only)
- **Body**:
  ```json
  {
    "bid_id": 1
  }
  ```
- **Success Response** (200):
  ```json
  {
    "success": true,
    "message": "Worker assigned successfully",
    "job_id": 1,
    "worker_id": 1
  }
  ```

### Unassign Worker from Job
- **URL**: `/api/jobs/unassign_worker/`
- **Method**: `POST`
- **Auth Required**: Yes (Customer only)
- **Body**:
  ```json
  {
    "job_id": 1
  }
  ```

## Payment Processing

### Create Payment
- **URL**: `/api/payments/`
- **Method**: `POST`
- **Auth Required**: Yes (Customer only)
- **Body**:
  ```json
  {
    "job": 1,
    "amount": 45000.00,
    "method": "bkash"
  }
  ```
- **Success Response** (201):
  ```json
  {
    "job": 1,
    "amount": "45000.00",
    "method": "bkash",
    "status": "pending"
  }
  ```

### Mark Job as Completed
- **URL**: `/api/jobs/<job_id>/`
- **Method**: `PUT`
- **Auth Required**: Yes (Customer only)
- **Body**:
  ```json
  {
    "status": "completed"
  }
  ```
- **Success Response** (200):
  ```json
  {
    "success": true,
    "message": "Job marked as completed and payment released",
    "job_id": 1
  }
  ```

## Review System

### Customer Reviews Worker
- **URL**: `/api/jobs/<job_id>/review_worker/`
- **Method**: `POST`
- **Auth Required**: Yes (Customer only)
- **Body**:
  ```json
  {
    "rating": 5,
    "comment": "Excellent work! Very professional and delivered on time."
  }
  ```
- **Success Response** (201):
  ```json
  {
    "success": true,
    "message": "Review submitted successfully",
    "review_id": 1
  }
  ```

### Worker Reviews Customer
- **URL**: `/api/jobs/<job_id>/review_customer/`
- **Method**: `POST`
- **Auth Required**: Yes (Worker only)
- **Body**:
  ```json
  {
    "rating": 4,
    "comment": "Good customer, clear requirements and prompt payment."
  }
  ```

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "error": "Error description",
  "details": {
    "field": ["Field-specific error message"]
  }
}
```

### Example Error Responses

#### Validation Error (400)
```json
{
  "password": ["Passwords do not match."],
  "email": ["This field is required."]
}
```

#### Authentication Error (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### Permission Error (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

## Response Formats

### Successful Registration/Login Response
```json
{
  "success": true,
  "statusCode": 200,
  "message": "Operation successful",
  "data": {
    "id": "user_id",
    "name": "username",
    "email": "user@example.com",
    "role": "customer|worker",
    "refresh": "refresh_token",
    "access": "access_token"
  }
}
```

### Job Response Format
```json
{
  "id": 1,
  "title": "Job Title",
  "description": "Job description",
  "location": "Job location",
  "budget": "50000.00",
  "status": "open|closed|completed",
  "assigned_worker": {
    "id": 1,
    "username": "worker_username",
    "skills": "Worker skills",
    "experience": 3,
    "location": "Worker location"
  }
}
```

### Payment Methods
- `bkash`: bKash mobile banking
- `nagad`: Nagad mobile banking
- `rocket`: Rocket mobile banking
- `cash`: Cash payment

### Job Status Values
- `open`: Job is available for bidding
- `closed`: Job has been assigned to a worker
- `completed`: Job has been completed and payment processed

### Bid Status Values
- `selected`: Bid has been selected by the customer
- `ignored`: Bid has been ignored by the customer
- `not_selected`: Bid is pending review (default status)

### Review Types
- `worker`: Customer reviewing a worker
- `customer`: Worker reviewing a customer

## Rate Limiting

Currently, there are no rate limiting restrictions, but it's recommended to implement them in production:

- Authentication endpoints: 5 requests per minute
- Job creation: 10 requests per hour
- Bid submission: 20 requests per hour

## Pagination

For endpoints that return lists (like jobs), pagination can be implemented using query parameters:

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

Example: `/api/jobs/?page=2&limit=10`
