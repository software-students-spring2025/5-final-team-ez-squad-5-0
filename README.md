# Together - A Relationship Communication App


![API Container CI/CD](https://github.com/software-students-spring2025/5-final-team-ez-squad-5-0/actions/workflows/api-container-ci-cd.yml/badge.svg)
![Web Container CI/CD](https://github.com/software-students-spring2025/5-final-team-ez-squad-5-0/actions/workflows/web-container-ci-cd.yml/badge.svg)
![Lint](https://github.com/software-students-spring2025/5-final-team-ez-squad-5-0/actions/workflows/lint.yml/badge.svg)
![Event Logger](https://github.com/software-students-spring2025/5-final-team-ez-squad-5-0/actions/workflows/event-logger.yml/badge.svg)




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

## Team

- [ChenJun Hsu](https://github.com/Junpapadiamond)
- [Eric Zhao](https://github.com/Ericzzy675)
- [Jiangbo Shen](https://github.com/js-montgomery)
- [Jess Liang](https://github.com/jess-liang322)

## Architecture

The application is composed of four main services:

1. **Web Container** (Port 3000): Flask frontend that serves the UI and communicates with the API
2. **API Container** (Port 5001): Core service handling authentication, messages, calendar, etc.
4. **Database Container** (Port 27017): MongoDB database storing all application data

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. Clone the repository
   ```bash
   git clone https://github.com/software-students-spring2025/5-final-team-ez-squad-5-0
   cd 5-final-team-ez-squad-5-0
   ```

2. Environment Setup:
   - All necessary environment variables are already configured in `docker-compose.yml`, so no separate `.env` file is needed to run this project.

3. Start the application using Docker Compose
   ```bash
   docker compose up --build
   ```

4. Access the application at `http://localhost:3000`

## Configuration

The environment variables required for this project are already defined in the `docker-compose.yml` file for each service.  
You do not need to create a separate `.env` file to run the system.

For reference, here are the main environment variables used:

### API Service (`together-api`) and Message Worker (`together-message-worker`)
- `FLASK_APP=run.py`
- `FLASK_ENV=development`
- `MONGO_URI=mongodb://db:27017/together`
- `SECRET_KEY=dev-secret-key`
- `JWT_SECRET_KEY=jwt-secret-key`
- `MAIL_SERVER=smtp.gmail.com`
- `MAIL_PORT=587`
- `MAIL_USE_TLS=True`
- `MAIL_USERNAME=your-email@gmail.com`
- `MAIL_PASSWORD=your-app-password`
- `MAIL_DEFAULT_SENDER=together-app@example.com`

### Web Frontend (`together-web`)
- `API_URL=http://api:5001/api`
- `SECRET_KEY=web-secret-key`
- `FLASK_ENV=development`

### Notes
- You can modify any environment variable by editing the `docker-compose.yml` file before starting the services.

## Database Setup

The MongoDB database is automatically initialized when the container starts. Sample users are created:

- Email: test@example.com, Password: password123
- Email: partner@example.com, Password: password123

You can modify the initial database setup by editing `db-container/init-mongo.js`.


## Project Structure

```
5-final-team-ez-squad-5-0/
├── web-container/            # Frontend Flask application
│   ├── app.py                # Main application file
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Web container setup
│   ├── tests/                # Tests for the flask routes
│   ├── static/               # CSS, JS, and images
│   └── templates/            # HTML templates
├── api-container/            # API service
│   ├── app/                  # Application modules
│   │   ├── routes/           # API endpoints
│   │   ├── __init__.py       # Initialize the package
│   │   └── email_utils.py    # Email functions
│   ├── workers/              # Background workers
│   │   └── message_worker.py # Handles scheduled messages
│   ├── tests/                # Tests for API endpoints
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # API container setup
│   ├── Dockerfile.worker     # Worker API setup
│   └── run.py                # Entry point
├── db-container/             # Database service
│   ├── init-mongo.js         # DB initialization script
│   ├── mongo-setup.sh        # Setup MongoDB
│   └── Dockerfile            # MongoDB container setup
└── docker-compose.yml        # Docker Compose configuration
```



## 🧪 Testing

To run tests for the various containers:

```bash
# Web container tests
cd web-container
pytest tests/test_app.y --cov=app

# API container tests
cd api-container
pytest tests/ --cov=app
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
