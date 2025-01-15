# Use Python Alpine as base image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PROJECT_NAME=html2pdf \
    DJANGO_SUPERUSER_USERNAME=admin \
    DJANGO_SUPERUSER_EMAIL=admin@example.com \
    DJANGO_SUPERUSER_PASSWORD=changeme

    # Install system dependencies for Pillow and Chromium
RUN apt-get update -y && apt-get install -y \
    chromium \
    python3-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    build-essential \
# Install system dependencies required for WeasyPrint
    libpango1.0-0 \
    fontconfig \
    libharfbuzz0b \
    # Build dependencies
    gcc \
    libc6-dev \
    python3-dev \
    libpango1.0-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    tk-dev \
    tcl-dev \
    libcairo2-dev \
    # Install Microsoft TrueType fonts
    && fc-cache -f

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy project files
COPY . .

# Install /app/html2image-lib
WORKDIR /app/lib/html2image
RUN poetry install
RUN poetry build
RUN pip install dist/*.whl

RUN echo 'export CHROMIUM_FLAGS="$CHROMIUM_FLAGS --no-sandbox"' >> /etc/chromium.d/default-flags

WORKDIR /app

# Create media and temp directories
RUN mkdir -p media temp

# Create static directories
RUN mkdir -p /app/static /app/staticfiles

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
