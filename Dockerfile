# Use Python Alpine as base image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PROJECT_NAME=html2pdf \
    DJANGO_SUPERUSER_USERNAME=admin \
    DJANGO_SUPERUSER_EMAIL=admin@example.com \
    DJANGO_SUPERUSER_PASSWORD=changeme

# Install system dependencies required for WeasyPrint
RUN apk add --no-cache \
    # WeasyPrint dependencies
    pango \
    fontconfig \
    harfbuzz \
    msttcorefonts-installer \
    # Build dependencies
    gcc \
    musl-dev \
    python3-dev \
    pango-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    cairo-dev \
    # Install Microsoft TrueType fonts
    && update-ms-fonts \
    && fc-cache -f

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create media and temp directories
RUN mkdir -p media temp

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]