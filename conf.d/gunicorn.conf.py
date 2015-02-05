#### Space Gunicorn configuration

# The IP / socket to bind to, by default will bind to all IP's on 10051
bind = '0.0.0.0:10051'

# Number of requests in backlog
backlog = 1024

# Workers
workers = 4
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

daemon = True
pidfile = '/var/run/space.pid'
umask = 0
user = None
group = None

errorlog = '/var/log/space/error.log'
loglevel = 'info'
accesslog = '/var/log/space/access.log'

proc_name = 'Space'

