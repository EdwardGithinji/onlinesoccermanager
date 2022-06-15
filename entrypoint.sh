#!/bin/sh
# wait-for-postgres.sh

set -e

cmd="$@"

python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.filter(email='admin@onlinesoccermanager.com').exists() or get_user_model().objects.create_superuser('admin@onlinesoccermanager.com', 'admin', 'user', 'purr55wad')"
exec ${cmd}
