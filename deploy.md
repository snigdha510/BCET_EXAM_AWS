# Flask Deployment Steps

### Install all necessary stuff (python etc)

### Git Clone the Project Repository

nano wsgi.py
```
from pariksha import create_app
app = create_app()

if __name__ == "__main__":
    app.run()
```

source venv/bin/activate
pip3 install gunicorn

### Test The Deployment using Gunicorn
```
/home/ubuntu/BCET_EXAM_AWS/venv/bin/gunicorn --bind 0.0.0.0:2028 "wsgi:app"
```

### Gunicorn Config
sudo mkdir /var/log/gunicorn
gunicorn_conf.py
```
bind = '0.0.0.0:2028'
worker_class = 'sync'
loglevel = 'debug'
accesslog = '/var/log/gunicorn/access_log_pariksha'
acceslogformat ="%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s %(f)s %(a)s"
errorlog =  '/var/log/gunicorn/access_log_pariksha'
```

### Create the Systemd Service
sudo nano /etc/systemd/system/pariksha.service
```
[Unit]
Description=BCET ENV
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/BCET_EXAM_AWS
Environment="PATH=/home/ubuntu/BCET_EXAM_AWS/venv/bin"
ExecStart=/home/ubuntu/BCET_EXAM_AWS/venv/bin/gunicorn -c "/home/ubuntu/BCET_EXAM_AWS/gunicorn_conf.py" --workers 3 --bind unix:pariksha.sock -m 007 "wsgi:app"
[Install]
WantedBy=multi-user.target
```

```
sudo systemctl start pariksha
sudo systemctl enable pariksha
sudo systemctl status pariksha
```

### Edit the Nginx Configuration
sudo nano /etc/nginx/sites-available/default
```
server { 
	listen 2028; 
	server_name 52.66.152.129; `

	location / { 
		include proxy_params;
		proxy_pass http://unix:/home/ubuntu/BCET_EXAM_AWS/pariksha.sock; 
	} 
}
```
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl reload nginx 