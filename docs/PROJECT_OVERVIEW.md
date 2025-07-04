# Digital Labor Backend

A comprehensive Django REST API backend for a digital labor marketplace platform that connects customers with skilled workers for various jobs and services.

## 📚 Documentation

This project includes comprehensive documentation:

- **[README.md](README.md)** - Main project overview and quick start guide
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API endpoint reference
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Database design and relationships
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing strategies

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Digital-Labor-Backend
   ```

2. **Setup virtual environment**
   ```bash
   cd backend
   python -m venv env
   
   # Windows
   env\Scripts\activate
   
   # macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## 🏗️ Architecture Overview

### Core Features
- **User Management**: Separate customer and worker accounts with role-based access
- **Job Management**: CRUD operations for job postings with status tracking
- **Bidding System**: Workers can bid on jobs, customers can select winners
- **Payment Processing**: Secure payment handling with multiple methods
- **Review System**: Bidirectional reviews between customers and workers
- **Wallet System**: Worker payment management
- **Email Notifications**: Automated notifications for key events

### Technology Stack
- **Framework**: Django 5.2.2 with Django REST Framework
- **Authentication**: JWT tokens with SimpleJWT
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **File Storage**: Local files (dev) / AWS S3 (prod)
- **Email**: SMTP with configurable backends

## 📱 API Endpoints

### Authentication
```
POST /api/register/     - User registration
POST /api/login/        - User login
POST /api/token/        - Obtain JWT token
POST /api/token/refresh/ - Refresh JWT token
```

### Jobs
```
GET    /api/jobs/              - List all jobs
POST   /api/jobs/create/       - Create new job
PUT    /api/jobs/<id>/update/  - Update job
DELETE /api/jobs/<id>/delete/  - Delete job
```

### Bidding & Assignment
```
POST /api/worker/bid/           - Submit bid
POST /api/jobs/assign_bid/      - Assign worker to job
GET  /api/customer/jobs/bids/   - View job bids
```

### Payments & Reviews
```
POST /api/payments/                        - Create payment
POST /api/jobs/<id>/review_worker/         - Review worker
POST /api/jobs/<id>/review_customer/       - Review customer
```

## 🗄️ Database Schema

### Core Models
- **User**: Extended Django user with customer/worker roles
- **Worker**: Extended worker profile with skills and verification
- **Job**: Job postings with budget, location, and status
- **Bid**: Worker bids on jobs with amounts and status
- **Payment**: Payment processing with multiple methods
- **Review**: Bidirectional review system
- **WorkerWallet**: Payment management for workers

### Key Relationships
- Users can be customers, workers, or both
- Jobs belong to customers and can be assigned to workers
- Bids connect workers to jobs with proposed amounts
- Payments are tied to completed jobs
- Reviews are bidirectional between job participants

## 🔐 Security Features

- JWT token-based authentication
- Role-based access control
- Password strength validation
- CORS protection
- SQL injection protection
- XSS protection
- HTTPS enforcement (production)

## 📊 Monitoring & Analytics

- Comprehensive logging
- Error tracking with Sentry (optional)
- Performance monitoring
- Database query optimization
- Test coverage reporting

## 🧪 Testing

The project includes comprehensive testing:

- **Unit Tests**: Model and utility function tests
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication and authorization tests
- **Performance Tests**: Load testing with Locust
- **Coverage**: 90%+ test coverage target

Run tests:
```bash
python manage.py test --settings=backend.settings.test
```

## 🚀 Deployment

### Development
- SQLite database
- Local file storage
- Debug mode enabled
- Development CORS settings

### Production Options
1. **Traditional VPS**: Nginx + Gunicorn + PostgreSQL
2. **Docker**: Containerized deployment with docker-compose
3. **Cloud Platforms**: Heroku, AWS, DigitalOcean

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run code formatting
black .
isort .

# Run linting
flake8 .

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🗺️ Roadmap

### Version 1.1
- [ ] Real-time notifications with WebSockets
- [ ] Advanced search and filtering
- [ ] File attachments for jobs
- [ ] Multi-language support

### Version 1.2
- [ ] Mobile app API enhancements
- [ ] Payment gateway integrations
- [ ] Advanced analytics dashboard
- [ ] Automated testing pipeline

### Version 2.0
- [ ] Microservices architecture
- [ ] GraphQL API
- [ ] Machine learning job matching
- [ ] Video call integration

## 📈 Performance

- **Response Time**: < 200ms for most API endpoints
- **Throughput**: Supports 1000+ concurrent users
- **Database**: Optimized queries with proper indexing
- **Caching**: Redis caching for frequently accessed data
- **CDN**: Static file delivery via CDN

---

**Digital Labor Backend** - Connecting talent with opportunity through technology.

For detailed information, please refer to the comprehensive documentation in the `/docs` folder.
