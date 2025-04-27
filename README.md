# Together - A Relationship Communication App

![Web Container CI](https://github.com/user/together/workflows/Web%20CI/badge.svg)
![API Container CI](https://github.com/user/together/workflows/API%20CI/badge.svg)
![AI Container CI](https://github.com/user/together/workflows/AI%20CI/badge.svg)
![DB Container CI](https://github.com/user/together/workflows/DB%20CI/badge.svg)

Together is a full-stack web application designed to help couples maintain and strengthen their relationships through structured communication tools, insights, and shared activities. The application uses a multi-container microservice architecture with Flask backends, MongoDB database, and a real-time AI analytics service.

## Features

- **Secure Messaging**: Send real-time and scheduled messages to your partner
- **Shared Calendar**: Coordinate events and activities together
- **Relationship Insights**: AI-powered analysis of communication patterns
- **Real-time Metrics**: Track conversation sentiment and response patterns
- **Virtual Pet**: A virtual pet that grows as your relationship strengthens
- **Smart Reminders**: Automatic detection of important dates from conversations

## Container Images

- Web Frontend: [docker.io/togetherapp/web-container](https://hub.docker.com/r/togetherapp/web-container)
- API Service: [docker.io/togetherapp/api-container](https://hub.docker.com/r/togetherapp/api-container)
- AI Service: [docker.io/togetherapp/ai-container](https://hub.docker.com/r/togetherapp/ai-container)
- MongoDB Database: [docker.io/togetherapp/db-container](https://hub.docker.com/r/togetherapp/db-container)

## Team

- [Developer 1](https://github.com/developer1)
- [Developer 2](https://github.com/developer2)
- [Developer 3](https://github.com/developer3)

## Architecture

The application is composed of four main services:

1. **Web Container** (Port 3000): Flask frontend that serves the UI and communicates with the API
2. **API Container** (Port 5001): Core service handling authentication, messages, calendar, etc.
3. **AI Container** (Port 5002): AI analysis service with Socket.IO for real-time metrics
4. **Database Container** (Port 27017): MongoDB database storing all application data

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js (optional, for development only)

## Quick Start

1. Clone the repository
   ```bash
   git clone https://github.com/user/together.git
   cd together
   ```

2. Create environment files (see Configuration section)

3. Start the application using Docker Compose
   ```bash
   docker-compose up -d
   ```

4. Access the application at `http://localhost:3000`

## Configuration

### Environment Variables

Before starting the application, you need to set up the following environment variables. Create a `.env` file in the project root directory:

```
# General settings
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=jwt-secret-key

# MongoDB connection
MONGO_URI=mongodb://db:27017/together

# Email settings (required for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=together-app@example.com

# Service URLs
API_URL=http://api:5001/api
AI_URL=http://ai-service:5002/api/ai
AI_SOCKET_URL=http://localhost:5002
```

### Example Configuration Files

Samples of all required configuration files are included in the repository as `.example` files. Simply copy these files and remove the `.example` extension:

```bash
cp .env.example .env
```

## Database Setup

The MongoDB database is automatically initialized when the container starts. Sample users are created:

- Email: test@example.com, Password: password123
- Email: partner@example.com, Password: password123

You can modify the initial database setup by editing `db-container/init-mongo.js`.

## Manual Setup (Without Docker)

If you prefer to run the services without Docker:

### Web Container
```bash
cd web-container
pip install -r requirements.txt
python app.py
```

### API Container
```bash
cd api-container
pip install -r requirements.txt
python run.py
```

### AI Container
```bash
cd ai-container
pip install -r requirements.txt
python run.py
```

### Database
Install MongoDB and run:
```bash
mongod --dbpath=/path/to/data
```
Then initialize the database with:
```bash
mongo < db-container/init-mongo.js
```

## Project Structure

```
SWE5/
├── web-container/           # Frontend Flask application
│   ├── app.py               # Main application file
│   ├── requirements.txt     # Python dependencies
│   ├── static/              # CSS, JS, and images
│   └── templates/           # HTML templates
├── api-container/           # API service
│   ├── app/                 # Application modules
│   │   ├── routes/          # API endpoints
│   │   └── email_utils.py   # Email functions
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Entry point
├── ai-container/            # AI analytics service
│   ├── app/                 # Application modules
│   │   ├── models/          # AI models
│   │   ├── routes.py        # API endpoints
│   │   └── socket_events.py # Real-time events
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Entry point
├── db-container/            # Database service
│   ├── init-mongo.js        # DB initialization script
│   └── Dockerfile           # MongoDB container setup
└── docker-compose.yml       # Docker Compose configuration
```

## Development

### Adding New Features

1. Create a feature branch:
   ```bash
   git checkout -b feature/new-feature
   ```

2. Make your changes

3. Run tests:
   ```bash
   # In each service directory
   pytest
   ```

4. Submit a pull request

### Environment Variables for Development

During development, you may want to use different environment variables:

```
FLASK_ENV=development
DEBUG=True
```

## Troubleshooting

### Container Communication Issues

If containers cannot communicate:
1. Check network settings in `docker-compose.yml`
2. Ensure all containers are on the same network (`app-network`)
3. Verify service names match the hostnames used in configuration

### Database Connection Issues

If the application cannot connect to the database:
1. Make sure MongoDB is running
2. Check the MongoDB connection string
3. Verify database initialization completed successfully

### Email Notification Issues

If email notifications are not working:
1. Make sure email credentials are correct
2. For Gmail, use an App Password instead of regular password
3. Check SMTP server settings and port

## License

This project is licensed under the MIT License - see the LICENSE file for details.
