import os, sys, tempfile, subprocess, threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from pathlib import Path
root=Path(__file__).resolve().parent.parent
os.chdir(root)
sys.path.insert(0, str(root))
with tempfile.TemporaryDirectory() as tmp:
    os.environ.update(DJANGO_DEBUG='true',DJANGO_SETTINGS_MODULE='config.settings',DATABASE_PATH=f'{tmp}/race.sqlite3',DJANGO_ALLOWED_HOSTS='testserver')
    subprocess.run([str(root/'.venv/bin/python'),'manage.py','migrate','--noinput'],check=True,stdout=subprocess.DEVNULL)
    import django
    django.setup()
    from django.test import Client
    from django.db import close_old_connections
    from django.contrib.auth.models import User
    from studio.forms import SetupForm
    barrier=threading.Barrier(2)
    original=SetupForm.is_valid
    def validated(form):
        result=original(form)
        barrier.wait(timeout=10)
        return result
    def create(name):
        close_old_connections()
        try:
            return Client().post('/setup/',{'username':name,'password1':'RainbowStrong-5384!','password2':'RainbowStrong-5384!'}).status_code
        finally:
            close_old_connections()
    with patch.object(SetupForm,'is_valid',validated), ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(create,['First','Second']))
    assert sorted(results)==[302,403],results
    assert User.objects.filter(is_superuser=True).count()==1
    print('PASS: simultaneous setup requests produce one admin, responses',results)
