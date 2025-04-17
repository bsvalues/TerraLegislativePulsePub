# Benton County Assessor AI Platform

A sophisticated AI-driven legislative tracking platform designed to simplify complex regulatory analysis for Benton County property stakeholders.

## 🌟 Features

- **Advanced Bill Search & Analysis Engine**: Intelligently search and analyze legislative bills from multiple sources
- **Multi-Source Legislative Tracking**: Track bills from Washington Legislature, OpenStates, LegiScan, and local documents
- **AI-Enhanced Bill Comprehension**: Understand complex legislative language with AI-powered summaries
- **Property Impact Assessment**: Analyze how legislative changes affect property assessments
- **Data Validation**: Validate property data according to Washington State standards
- **Property Valuation**: Calculate property values using multiple approaches

## 📋 Key Components

- **Legislative Trackers**: Services that fetch bills from various sources
- **Bill Analysis Service**: AI-powered service that analyzes the impact of bills on property assessments
- **Data Validation Agent**: Validates property data according to Washington State standards
- **Property Impact Agent**: Analyzes how legislative changes affect property assessments
- **User Interaction Agent**: Provides a natural language interface for assessor staff

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Required API keys (optional):
  - ANTHROPIC_API_KEY for AI-powered analysis
  - LEGISCAN_API_KEY for LegiScan integration
  - OPENSTATES_API_KEY for OpenStates integration

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/benton-county-assessor-ai.git
   cd benton-county-assessor-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/benton_assessor"
   export SESSION_SECRET="your_secret_key"
   export FLASK_DEBUG=True
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Add sample data (optional):
   ```bash
   python add_sample_properties.py
   python add_sample_bills.py
   ```

6. Create an admin user:
   ```bash
   python create_admin_user.py admin@example.com admin password
   ```

7. Run the application:
   ```bash
   python main.py
   ```

## 🏛️ Architecture

The application follows a modular architecture:

- **Web Interface**: Flask-based web application
- **Legislative Tracking**: Services that fetch bills from various sources
- **AI Analysis**: AI-powered services that analyze legislative text
- **Database**: PostgreSQL database for storing bills, properties, and assessments
- **Agent System**: AI agents that perform specific tasks (validation, analysis, etc.)

## 📊 Database Schema

The application uses the following database models:

- **User**: Stores user information
- **Property**: Stores property information
- **Assessment**: Stores property assessment information
- **LegislativeUpdate**: Stores legislative bill information
- **AuditLog**: Logs user actions for audit purposes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔒 Security

- Passwords are hashed using werkzeug.security
- Session management uses Flask-Login
- CSRF protection is enabled

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.