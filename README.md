# IT News Parser

A robust news parser for IT blogs (Habr, VC.ru, iXBT Live) with a FastAPI search engine and Streamlit dashboard.

## Features
- **Multi-source Parsing**: Habr, VC.ru, and iXBT Live.
- **Deduplication**: Avoids duplicate articles based on URL.
- **Language Detection**: Automatically detects RU/EN content.
- **Throttling**: Respectful of site limits.
- **Database Storage**: Uses PostgreSQL for persistent storage.
- **Search API**: FastAPI endpoint for searching articles by tags and dates.
- **Dashboard**: Visualizes trends and popular topics.
- **Dockerized**: Easy deployment with Docker Compose.

## System Architecture

### Database Schema
- **articles**: Main table storing title, url, published date, stats, etc.
- **authors**: Unique authors of the articles.
- **tags**: Topics/hubs associated with articles.
- **sources**: Source websites (Habr, VC.ru, etc.).
- **article_tags**: Junction table for many-to-many relationship between articles and tags.

### Components
- **Parser Service**: Periodically fetches new articles and saves them to the DB.
- **API Service**: Provides access to the data.
- **Dashboard Service**: UI for data analysis.

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the application
1. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Start all services:
   ```bash
   docker-compose up --build
   ```

The services will be available at:
- **FastAPI API**: http://localhost:8000
- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation (Swagger)**: http://localhost:8000/docs

## API Examples

### Search articles by tag
```bash
curl "http://localhost:8000/articles?tag=Python"
```

### Search articles by date range
```bash
curl "http://localhost:8000/articles?date_from=2024-01-01&date_to=2024-12-31"
```

### List all tags
```bash
curl "http://localhost:8000/tags"
```

## Testing
To run tests locally:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest
```
To check coverage:
```bash
coverage run -m pytest
coverage report
```
