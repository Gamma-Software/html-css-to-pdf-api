# PDF Converter API

A Django REST API that converts HTML/CSS/images to PDF using WeasyPrint.

## Setup

1. Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start the development server:

```bash
python manage.py runserver
```

## API Usage

### Convert HTML to PDF

**Endpoint:** `POST /api/convert/`

**Request:**

- Content-Type: `multipart/form-data`
- Body:
  - `file`: ZIP file containing:
    - `index.html` (required)
    - CSS files (optional)
    - Images (optional)

**Response:**

- Success: PDF file (application/pdf)
- Error: JSON with error message

**Example using curl:**

```bash
curl -X POST -F "file=@your-archive.zip" http://localhost:8000/api/convert/ --output converted.pdf
```

## Notes

- The ZIP file must contain an `index.html` file at any level in its directory structure
- All assets (CSS, images) should be referenced using relative paths in the HTML
- The API will return the PDF file directly in the response
