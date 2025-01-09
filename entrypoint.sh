#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Creating superuser..."
python manage.py createsuperuser --noinput || true

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000