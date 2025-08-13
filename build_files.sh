#!/bin/bash
# Install requirements
pip install -r requirements.txt
# Collect static files (for Django admin and DRF)
python manage.py collectstatic --noinput