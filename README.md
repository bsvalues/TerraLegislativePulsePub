# Benton County Assessor AI Platform

An AI-powered platform for the Benton County Assessor's office that focuses on legislative tracking, bill analysis, and property assessment impact evaluation.

## Features

### Legislative Tracking

The platform integrates with multiple data sources to track legislation that may impact property assessments:

- **Washington State Legislature RSS Feed** - Direct updates from WA state legislature
- **OpenStates API** - Comprehensive view of bills across 50 states
- **LegiScan API** - Detailed bill information and status tracking
- **Local Documents** - Relevant County-specific documentation

### AI-Powered Analysis

Leveraging Anthropic Claude, the platform provides:

- **Bill Summarization** - Concise summaries of complex legislative text
- **Impact Assessment** - Analysis of how bills affect property assessments
- **Entity Extraction** - Identification of key entities and stakeholders
- **Property Class Analysis** - Targeted analysis for specific property types

### Property Assessment Tools

- **Data Validation Agent** - Ensures property data meets Washington state standards
- **Valuation Agent** - Multiple approaches to property valuation
- **Property Impact Analysis** - Track how legislative changes affect property values

## System Architecture

The platform uses a multi-agent architecture with a Master Control Program (MCP) that coordinates specialized agents:

- **Data Validation Agent** - Validates property data according to state standards
- **Valuation Agent** - Calculates property values using multiple methodologies
- **Property Impact Agent** - Analyzes legislative impact on property assessments
- **User Interaction Agent** - Handles user queries and provides assistance

## API Documentation

The platform provides several API endpoints for interacting with its capabilities:

### AI Subsystem API

- `GET /ai/status` - Check AI system status
- `POST /ai/property-impact` - Analyze legislation impact on property assessments
- `POST /ai/analyze` - Analyze bill for key insights
- `POST /ai/summarize` - Generate bill summary
- `POST /ai/extract-entities` - Extract entities from bill text
- `POST /ai/categorize` - Categorize bill into relevant topics
- `POST /ai/impact-assessment` - Assess general bill impact

### Bill Tracking API

- `GET /bills/tracked` - Get all tracked bills
- `GET /bills/search` - Search bills by query
- `GET /bills/analyze/{bill_id}` - Analyze specific bill
- `GET /bills/relevant` - Find bills relevant to search query
- `GET /bills/summarize/{bill_id}` - Generate summary of tracked bill
- `GET /bills/extract-entities/{bill_id}` - Extract entities from tracked bill

## Configuration

### Environment Variables

The platform requires the following environment variables:

- `DATABASE_URL` - PostgreSQL database connection string
- `ANTHROPIC_API_KEY` - API key for Anthropic Claude
- `LEGISCAN_API_KEY` - API key for LegiScan (optional)
- `OPENSTATES_API_KEY` - API key for OpenStates (optional)
- `SESSION_SECRET` - Secret key for session management

### API Keys

API keys can be managed through the settings page in the web interface. The platform will function with degraded capabilities if certain API keys are not provided:

- **Anthropic API Key** - Required for AI analysis features
- **LegiScan API Key** - Optional, enhances bill tracking
- **OpenStates API Key** - Optional, enhances bill tracking

## Development

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Initialize the database: `flask db upgrade`
5. Run the application: `gunicorn --bind 0.0.0.0:5000 main:app`

### Technology Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL
- **AI**: Anthropic Claude
- **Scheduler**: Schedule library for background tasks

## License

This project is licensed under the MIT License - see the LICENSE file for details.