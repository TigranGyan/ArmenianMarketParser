# Armenian Market Parser

[![CI](https://github.com/yourusername/ArmenianMarketParser/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/ArmenianMarketParser/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced price aggregator and tracker for Armenian supermarkets. Track price history, search across stores, and find the best deals for your groceries.

## 🚀 Key Features

- **Multi-store Search**: Full-text search across various Armenian supermarkets powered by Elasticsearch.
- **Price History**: Track how prices change over time with Type 2 SCD (Slowly Changing Dimension) implementation.
- **Automated Scraping**: Asynchronous scrapers for real-time data collection.
- **Shopping Lists**: Create and manage your grocery lists with live price updates.
- **Modern UI**: Clean and responsive React-based frontend.

## 🛠 Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Database**: PostgreSQL 15, Redis 7 (Celery Broker)
- **Search**: Elasticsearch 8
- **Frontend**: React, Vite, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose, Nginx

## 🏗 Architecture

The project follows a microservices-based, event-driven architecture:
- `core-api`: FastAPI service handling user requests, auth, and search.
- `scraper`: Celery-based workers that fetch data from supermarket websites.
- `price_worker`: Processes scraped data, manages price history in PostgreSQL, and indexes data into Elasticsearch.
- `database`: PostgreSQL schema for relational data.
- `elasticsearch`: High-performance search engine.

## 🚦 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ArmenianMarketParser.git
   cd ArmenianMarketParser
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start the application**:
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- Frontend: `http://localhost`
- API Documentation: `http://localhost:8000/docs`

## ⚙️ Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `SECRET_KEY` | JWT signing key (Crucial for production) | `auto-generated in dev` |
| `ELASTICSEARCH_URL` | Elasticsearch connection string | `http://elasticsearch:9200` |
| `ENV` | Environment (development/production) | `development` |

## 🧪 Testing & Quality

### Backend
Run tests locally:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/core-api:$(pwd)/scraper:$(pwd)/price_worker
DATABASE_URL=sqlite:///:memory: pytest tests/
```

Quality checks:
```bash
ruff check .
black --check .
mypy .
bandit -r core-api scraper price_worker
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for:
- New store scrapers
- UI/UX improvements
- Bug fixes and optimizations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
