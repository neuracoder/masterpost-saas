# Masterpost.io Backend API

FastAPI backend for batch image processing service targeting e-commerce platforms.

## Features

- **Multi-format Image Upload**: Support for JPG, PNG, WebP, BMP, TIFF
- **Batch Processing**: Handle 100+ images simultaneously
- **E-commerce Pipelines**:
  - Amazon Compliant (1000x1000px, white background)
  - Instagram Ready (1080x1080px, color enhanced)
  - eBay Optimized (1600x1600px, high resolution)
- **Real-time Progress Tracking**
- **ZIP Download** of processed images
- **Supabase Integration** for data persistence

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup

Copy your `.env` file from the parent directory or create one with:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

### 3. Run the Server

```bash
# Development
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Upload Images
```http
POST /api/v1/upload
Content-Type: multipart/form-data

# Returns job_id for tracking
```

### Process Images
```http
POST /api/v1/process
Content-Type: application/json

{
  "job_id": "uuid",
  "pipeline": "amazon|instagram|ebay",
  "settings": {
    "quality": 95,
    "saturation": 1.3,
    "contrast": 1.1
  }
}
```

### Check Status
```http
GET /api/v1/status/{job_id}

# Returns progress percentage and status
```

### Download Results
```http
GET /api/v1/download/{job_id}

# Downloads ZIP file with processed images
```

## Pipeline Details

### Amazon Pipeline
- **Size**: 1000x1000px
- **Background**: Pure white
- **Features**: Background removal, product centering, quality optimization
- **Coverage**: 85% product coverage requirement

### Instagram Pipeline
- **Size**: 1080x1080px
- **Format**: Perfect square
- **Features**: Color boost, contrast enhancement, social media optimization
- **Enhancement**: Saturation +30%, Contrast +20%

### eBay Pipeline
- **Size**: 1600x1600px
- **Quality**: High resolution for zoom
- **Features**: Detail enhancement, noise reduction, professional padding
- **Optimization**: Sharpness +30%, detail preservation

## Configuration

### Image Processing Settings

```python
# Default sizes
AMAZON_SIZE = (1000, 1000)
INSTAGRAM_SIZE = (1080, 1080)
EBAY_SIZE = (1600, 1600)

# Quality settings
JPEG_QUALITY = 95
PNG_COMPRESSION = 6

# Upload limits
MAX_FILE_SIZE = 50MB
MAX_FILES_PER_JOB = 500
```

### Custom Pipeline Settings

```json
{
  "quality": 95,
  "padding_percent": 5,
  "remove_background": true,
  "saturation": 1.3,
  "contrast": 1.1,
  "brightness": 1.0,
  "sharpness": 1.1
}
```

## Architecture

```
/backend
├── app/
│   ├── main.py              # FastAPI application
│   ├── routers/             # API route handlers
│   │   ├── upload.py        # File upload endpoints
│   │   ├── process.py       # Processing endpoints
│   │   └── download.py      # Download endpoints
│   └── core/                # Core configuration
│       ├── config.py        # Settings and configuration
│       └── security.py      # Authentication and security
├── processing/              # Image processing logic
│   ├── image_processor.py   # Core image operations
│   ├── pipelines.py         # Platform-specific pipelines
│   └── batch_handler.py     # Queue and batch processing
└── models/                  # Data models
    ├── schemas.py           # Pydantic models
    └── database.py          # Supabase integration
```

## Database Schema

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_files INTEGER NOT NULL,
    processed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    pipeline VARCHAR(50),
    settings JSONB DEFAULT '{}',
    files JSONB DEFAULT '[]',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
flake8 .
```

### Docker (Optional)
```bash
docker build -t masterpost-api .
docker run -p 8000:8000 masterpost-api
```

## Production Deployment

1. **Environment Variables**: Set all required env vars
2. **Redis**: For production queue management
3. **File Storage**: Consider cloud storage for uploads/processed files
4. **Monitoring**: Add logging and health checks
5. **Scale**: Use multiple workers with load balancer

## Error Handling

The API returns standardized error responses:

```json
{
  "error": "error_type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Security

- JWT-based authentication
- File type validation
- Size limits enforcement
- Input sanitization
- Rate limiting (recommended for production)

## Support

For issues or questions, check the API documentation at `/docs` or contact the development team.