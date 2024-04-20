bind = '0.0.0.0:2028'
worker_class = 'sync'
loglevel = 'debug'
accesslog = '/var/log/gunicorn/access_log_pariksha'
acceslogformat ="%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog =  '/var/log/gunicorn/access_log_pariksha'