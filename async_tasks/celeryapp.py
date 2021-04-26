from __future__ import absolute_import, unicode_literals

from celery import Celery

app = Celery('async_tasks')
app.config_from_object('async_tasks.celeryconfig')

if __name__ == '__main__':
    app.start()
