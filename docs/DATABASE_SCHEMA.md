# Digital Labor Backend - Database Schema Documentation

## Overview

This document describes the database schema for the Digital Labor Backend application. The system uses Django's ORM with SQLite for development (easily configurable for PostgreSQL/MySQL in production).

## Entity Relationship Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      User       │    │     Worker      │    │   WorkerWallet  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │◄──►│ id (PK)         │◄──►│ id (PK)         │
│ username        │    │ user_id (FK)    │    │ worker_id (FK)  │
│ email           │    │ skills          │    │ balance         │
│ password        │    │ experience      │    └─────────────────┘
│ is_worker       │    │ location        │
│ is_customer     │    │ nid             │
│ role            │    │ verified        │
│ profile_picture │    │ profile_picture │
│ is_active       │    └─────────────────┘
│ date_joined     │
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Job        │    │      Bid        │    │    Payment      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │◄──►│ id (PK)         │    │ id (PK)         │
│ customer_id(FK) │    │ worker_id (FK)  │    │ job_id (FK)     │
│ assigned_worker │    │ job_id (FK)     │◄──►│ amount          │
│ title           │    │ bid_amount      │    │ method          │
│ description     │    │ status          │    │ status          │
│ location        │    │ timestamp       │    │ created_at      │
│ budget          │    └─────────────────┘    └─────────────────┘
│ urgency         │
│ status          │    ┌─────────────────┐
│ created_at      │◄──►│     Review      │
└─────────────────┘    ├─────────────────┤
                       │ id (PK)         │
                       │ job_id (FK)     │
                       │ reviewer_id(FK) │
                       │ reviewee_id(FK) │
                       │ review_type     │
                       │ rating          │
                       │ comment         │
                       │ created_at      │
                       └─────────────────┘
```

## Table Schemas

### User Table

Custom user model extending Django's AbstractUser.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing user ID |
| username | CharField(150) | UNIQUE, NOT NULL | Unique username |
| email | EmailField(254) | NOT NULL | User email address |
| password | CharField(128) | NOT NULL | Hashed password |
| first_name | CharField(150) | NULLABLE | User's first name |
| last_name | CharField(150) | NULLABLE | User's last name |
| is_worker | BooleanField | DEFAULT False | Indicates if user is a worker |
| is_customer | BooleanField | DEFAULT False | Indicates if user is a customer |
| role | CharField(20) | CHOICES, NULLABLE | User role ('worker' or 'customer') |
| profile_picture | ImageField | NULLABLE | Path to user's profile picture |
| is_active | BooleanField | DEFAULT True | Account activation status |
| is_staff | BooleanField | DEFAULT False | Staff status |
| is_superuser | BooleanField | DEFAULT False | Superuser status |
| date_joined | DateTimeField | AUTO_NOW_ADD | Account creation timestamp |
| last_login | DateTimeField | NULLABLE | Last login timestamp |

**Constraints:**
- Username must be unique
- Either is_worker or is_customer must be True (enforced in serializer)
- Workers are set to is_active=False by default (requires admin approval)

### Worker Table

Extended profile information for workers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing worker ID |
| user_id | OneToOneField | FOREIGN KEY, NOT NULL | Reference to User table |
| skills | TextField | NOT NULL | Worker's skills description |
| experience | PositiveIntegerField | NOT NULL | Years of experience |
| location | TextField(100) | NULLABLE | Worker's location |
| nid | CharField(20) | NULLABLE | National ID for verification |
| verified | BooleanField | DEFAULT False | Admin verification status |
| profile_picture | ImageField | NULLABLE | Worker-specific profile picture |

**Relationships:**
- One-to-One with User (user_id)
- One-to-One with WorkerWallet
- One-to-Many with Bid
- One-to-Many with Job (as assigned_worker)

### Job Table

Job postings created by customers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing job ID |
| customer_id | ForeignKey | NOT NULL | Reference to User (customer) |
| assigned_worker_id | ForeignKey | NULLABLE | Reference to Worker |
| title | CharField(100) | NOT NULL | Job title |
| description | TextField(255) | NOT NULL | Job description |
| location | CharField(100) | NOT NULL | Job location |
| budget | DecimalField(10,2) | NOT NULL | Job budget |
| urgency | PositiveSmallIntegerField | DEFAULT 1 | Urgency level (1-5) |
| status | CharField(20) | CHOICES, DEFAULT 'open' | Job status |
| created_at | DateTimeField | AUTO_NOW_ADD | Job creation timestamp |

**Status Choices:**
- 'open': Available for bidding
- 'closed': Assigned to a worker
- 'completed': Work finished and paid

**Relationships:**
- Many-to-One with User (customer)
- Many-to-One with Worker (assigned_worker)
- One-to-Many with Bid
- One-to-One with Payment
- One-to-Many with Review

### Bid Table

Bids submitted by workers for jobs.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing bid ID |
| worker_id | ForeignKey | NOT NULL | Reference to Worker |
| job_id | ForeignKey | NOT NULL | Reference to Job |
| bid_amount | DecimalField(10,2) | NOT NULL | Proposed bid amount |
| status | CharField(20) | CHOICES, DEFAULT 'not_selected' | Bid status |
| timestamp | DateTimeField | AUTO_NOW_ADD | Bid submission time |

**Status Choices:**
- 'selected': Bid accepted by customer
- 'ignored': Bid ignored by customer
- 'not_selected': Pending review (default)

**Relationships:**
- Many-to-One with Worker
- Many-to-One with Job

**Constraints:**
- Unique constraint on (worker_id, job_id) to prevent duplicate bids

### Payment Table

Payment information for completed jobs.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing payment ID |
| job_id | OneToOneField | FOREIGN KEY, NOT NULL | Reference to Job |
| amount | DecimalField(10,2) | NOT NULL | Payment amount |
| method | CharField(20) | CHOICES, NOT NULL | Payment method |
| status | CharField(20) | CHOICES, DEFAULT 'pending' | Payment status |
| created_at | DateTimeField | AUTO_NOW_ADD | Payment creation time |

**Method Choices:**
- 'bkash': bKash mobile banking
- 'nagad': Nagad mobile banking
- 'rocket': Rocket mobile banking
- 'cash': Cash payment

**Status Choices:**
- 'pending': Payment initiated but not completed
- 'completed': Payment processed and released

**Relationships:**
- One-to-One with Job

### WorkerWallet Table

Wallet system for worker payments.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing wallet ID |
| worker_id | OneToOneField | FOREIGN KEY, NOT NULL | Reference to Worker |
| balance | DecimalField(10,2) | DEFAULT 0.0 | Current wallet balance |

**Relationships:**
- One-to-One with Worker

### Review Table

Review system for jobs between customers and workers.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PRIMARY KEY | Auto-incrementing review ID |
| job_id | ForeignKey | NOT NULL | Reference to Job |
| reviewer_id | ForeignKey | NOT NULL | User giving the review |
| reviewee_id | ForeignKey | NOT NULL | User receiving the review |
| review_type | CharField(20) | CHOICES, DEFAULT 'worker' | Type of review |
| rating | PositiveSmallIntegerField | NOT NULL | Rating (1-5) |
| comment | TextField | NULLABLE | Review comment |
| created_at | DateTimeField | AUTO_NOW_ADD | Review creation time |

**Review Type Choices:**
- 'worker': Customer reviewing worker
- 'customer': Worker reviewing customer

**Relationships:**
- Many-to-One with Job
- Many-to-One with User (reviewer)
- Many-to-One with User (reviewee)

**Constraints:**
- Rating must be between 1 and 5
- Unique constraint on (job_id, reviewer_id, review_type) to prevent duplicate reviews

## Database Indexes

The following indexes are recommended for optimal performance:

### Primary Indexes (Automatic)
- All primary keys are automatically indexed

### Foreign Key Indexes (Automatic)
- All foreign key fields are automatically indexed

### Recommended Additional Indexes

```sql
-- User table
CREATE INDEX idx_user_role ON api_user(role);
CREATE INDEX idx_user_is_active ON api_user(is_active);

-- Job table
CREATE INDEX idx_job_status ON api_job(status);
CREATE INDEX idx_job_created_at ON api_job(created_at);
CREATE INDEX idx_job_budget ON api_job(budget);

-- Bid table
CREATE INDEX idx_bid_status ON api_bid(status);
CREATE INDEX idx_bid_timestamp ON api_bid(timestamp);
CREATE INDEX idx_bid_amount ON api_bid(bid_amount);

-- Payment table
CREATE INDEX idx_payment_status ON api_payment(status);
CREATE INDEX idx_payment_method ON api_payment(method);

-- Review table
CREATE INDEX idx_review_rating ON api_review(rating);
CREATE INDEX idx_review_type ON api_review(review_type);
```

## Data Validation Rules

### User Model
- Username: 1-150 characters, alphanumeric and @/./+/-/_ only
- Email: Valid email format
- Password: Django's built-in password validators
- Role: Must be 'worker' or 'customer'

### Worker Model
- Experience: Must be positive integer
- NID: 20 characters maximum
- Skills: Required field, cannot be empty

### Job Model
- Title: 1-100 characters
- Description: 1-255 characters
- Budget: Positive decimal, max 10 digits with 2 decimal places
- Urgency: 1-5 integer range

### Bid Model
- Bid Amount: Positive decimal, max 10 digits with 2 decimal places
- Must be for open jobs only

### Payment Model
- Amount: Positive decimal, max 10 digits with 2 decimal places
- Method: Must be one of the predefined choices

### Review Model
- Rating: Integer between 1 and 5
- Comment: Optional text field

## Migration History

The application includes several migrations:

1. **0001_initial.py**: Initial database schema
2. **0002_alter_payment_method.py**: Updated payment method choices
3. **0003_user_role.py**: Added role field to User model
4. **0004_alter_user_is_customer_alter_user_is_worker.py**: Modified user type fields
5. **0005_job_assigned_worker_alter_user_is_customer_and_more.py**: Added job assignment
6. **0006_bid_status.py**: Added bid status field
7. **0007_user_profile_picture_worker_profile_picture.py**: Added profile pictures
8. **0008_alter_worker_verified_workerwallet.py**: Added worker verification and wallet
9. **0009_alter_payment_status.py**: Updated payment status choices
10. **0010_review_review_type_review_reviewee_alter_review_job_and_more.py**: Enhanced review system

## Backup and Maintenance

### Regular Maintenance Tasks

1. **Database Cleanup**:
   - Remove old inactive user accounts
   - Archive completed jobs older than 1 year
   - Clean up orphaned media files

2. **Performance Monitoring**:
   - Monitor query performance
   - Check index usage
   - Analyze slow queries

3. **Data Integrity**:
   - Validate foreign key relationships
   - Check for orphaned records
   - Verify wallet balance consistency

### Backup Strategy

For production environments:

1. **Daily Backups**: Full database backup
2. **Weekly Backups**: Archive to long-term storage
3. **Transaction Log Backups**: Every 15 minutes (for supported databases)
4. **Media Files**: Daily backup of uploaded files

## Security Considerations

1. **Data Encryption**:
   - Passwords are hashed using Django's PBKDF2 algorithm
   - Consider encrypting sensitive fields like NID

2. **Access Control**:
   - Database access restricted to application user
   - No direct database access for end users
   - Admin interface access limited to superusers

3. **Data Privacy**:
   - Personal information (NID, email) should be handled according to privacy laws
   - Implement data anonymization for analytics
   - Consider GDPR compliance for EU users

4. **Audit Trail**:
   - All models include creation timestamps
   - Consider adding update timestamps and user tracking
   - Log important business events (payments, reviews, etc.)

## Performance Optimization

### Query Optimization

1. **Use select_related() and prefetch_related()**:
   ```python
   # Get jobs with assigned workers
   jobs = Job.objects.select_related('assigned_worker__user')
   
   # Get user with all bids
   user = User.objects.prefetch_related('worker__bids')
   ```

2. **Database Connection Pooling**:
   - Configure connection pooling for production
   - Use persistent connections where appropriate

3. **Caching Strategy**:
   - Cache frequently accessed data (user profiles, job listings)
   - Use Redis for session storage and caching
   - Implement query result caching

### Scaling Considerations

1. **Read Replicas**: For read-heavy workloads
2. **Database Sharding**: Partition data by user or geographic region
3. **Archive Strategy**: Move old data to separate archive database
4. **Media Storage**: Use cloud storage (AWS S3, etc.) for file uploads
