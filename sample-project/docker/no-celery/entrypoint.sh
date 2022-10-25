echo "Setting up server..."

python manage.py migrate
echo "- Migrations complete"
python manage.py createsuperuser --noinput || true
echo "- Superuser ready"
python manage.py collectstatic --noinput
echo "- Static files collected"

echo "Starting server..."
python manage.py runserver 0.0.0.0:80 --noreload