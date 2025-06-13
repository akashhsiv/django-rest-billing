# User Management API

A Django REST Framework API for user management with role-based access control.

## Features

- User registration and authentication (JWT)
- Role-based access control (Admin, Manager, Cashier, Customer)
- API documentation with Swagger/ReDoc
- Custom user model with email as username
- Secure password handling

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create admin user**
   ```bash
   python manage.py create_admin
   ```
   Default admin credentials:
   - Email: admin@example.com
   - Password: admin123

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- API Documentation: http://localhost:8000/swagger/
- Admin Interface: http://localhost:8000/admin/
- API Base URL: http://localhost:8000/api/

### Authentication

- `POST /api/auth/register/` - Register a new user (customer)
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/token/refresh/` - Refresh access token

### User Management (Admin)

- `GET /api/auth/users/` - List all users (Admin only)
- `GET /api/auth/users/{id}/` - Get user details (Admin only)
- `PATCH /api/auth/users/{id}/` - Update user (Admin only)
- `DELETE /api/auth/users/{id}/` - Delete user (Admin only)

### Cashier Management (Manager & Admin)

- `GET /api/auth/cashiers/` - List all cashiers (Manager+)
- `POST /api/auth/cashiers/` - Create new cashier (Manager+)

## Roles and Permissions

- **Admin**: Full access to all endpoints
- **Manager**: Can manage cashiers and view customers
- **Cashier**: Limited access to specific features
- **Customer**: Basic user with limited access

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Testing

Run the test suite with:

```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
