# Together - A Relationship Communication App


![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Enabled-blue?logo=docker)
![Flask](https://img.shields.io/badge/Backend-Flask-blue?logo=flask)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-green?logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-yellow?logo=opensourceinitiative)
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![CI](https://img.shields.io/badge/CI%20Build-Passing-success?logo=github)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen?logo=github)


Together is a full-stack web application designed to help couples maintain and strengthen their relationships through structured communication tools and shared activities. The application uses a multi-container microservice architecture with Flask backends and MongoDB database.

## Features

- **Dashboard**: Personalized home page with upcoming events and recent messages
- **Secure Messaging**: Send real-time and scheduled messages to your partner
- **Shared Calendar**: Coordinate events and activities together
- **Partner Connection**: Simple system to connect with your significant other
- **Relationship Insights**: AI-powered analysis of communication patterns
- **Daily Questions**: Answer daily prompts to share with your partner
- **Settings Management**: Customize notifications and account preferences

## Container Images

- [Web Frontend](https://hub.docker.com/r/ericzzy/together-web)
- [API Service](https://hub.docker.com/r/ericzzy/together-api)
- [MongoDB Database](https://hub.docker.com/r/ericzzy/together-db)

## Team

- [ChenJun Hsu](https://github.com/Junpapadiamond)
- [Eric Zhao](https://github.com/Ericzzy675)
- [Jiangbo Shen](https://github.com/js-montgomery)
- [Jess Liang](https://github.com/jess-liang322)

## 🏗️ Architecture

The application is composed of four main services:

1. **Web Container** (Port 3000): Flask frontend that serves the UI and communicates with the API
2. **API Container** (Port 5001): Core service handling authentication, messages, calendar, etc.
4. **Database Container** (Port 27017): MongoDB database storing all application data

## 📋 Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. Clone the repository
   ```bash
   git clone https://github.com/software-students-spring2025/5-final-team-ez-squad-5-0
   cd 5-final-team-ez-squad-5-0
   ```

2. Create environment files (see Configuration section)

3. Start the application using Docker Compose
   ```bash
   docker compose up --build
   ```

4. Access the application at `http://localhost:3000`

## ⚙️ Configuration

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
```

### Example Configuration Files

Samples of all required configuration files are included in the repository as `.example` files. Simply copy these files and remove the `.example` extension:

```bash
cp .env.example .env
```

## 🗄️ Database Setup

The MongoDB database is automatically initialized when the container starts. Sample users are created:

- Email: test@example.com, Password: password123
- Email: partner@example.com, Password: password123

You can modify the initial database setup by editing `db-container/init-mongo.js`.

## 🛠️ Manual Setup (Without Docker)

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

## 📁 Project Structure

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
│   ├── workers/             # Background workers
│   │   └── message_worker.py # Handles scheduled messages
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Entry point
├── ai-container/            # AI analytics service
│   ├── app/                 # Application modules
│   │   ├── models/          # Analytics models
│   │   ├── routes.py        # API endpoints
│   │   └── utils/           # Utility functions
│   ├── requirements.txt     # Python dependencies
│   └── run.py               # Entry point
├── db-container/            # Database service
│   ├── init-mongo.js        # DB initialization script
│   └── Dockerfile           # MongoDB container setup
└── docker-compose.yml       # Docker Compose configuration
```

## 🔑 Key Features Explained

### Scheduled Messages
Send messages to your partner that will be delivered at a specific time. Perfect for anniversaries, birthdays, or just to surprise your partner.

### Relationship Insights
The AI container analyzes your communication patterns and provides insights to help strengthen your relationship. View metrics like message frequency, response times, and sentiment analysis.

### Real-time Updates
The application uses Socket.IO to provide real-time updates for communication analytics.

## 🐞 Troubleshooting

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

## 📱 API Documentation

The API endpoints are organized into several categories:

- `/api/auth/*` - Authentication and user management
- `/api/messages/*` - Message sending and retrieval
- `/api/calendar/*` - Calendar event management
- `/api/ai/*` - AI insights and analytics

For detailed API documentation, refer to the API documentation in the project wiki.

## 🧪 Testing

To run tests for the various containers:

```bash
# Web container tests
cd web-container
pytest

# API container tests
cd api-container
pytest

# AI container tests
cd ai-container
pytest
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
