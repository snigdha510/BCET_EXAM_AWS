import os

class Config():
    SECRET_KEY = "7c9270027a164800f09e52vb828q1384523667f"
    #change if not using gmail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    #mail port info ends

    #add email and password 
    MAIL_USERNAME = "pariksha.contact@gmail.com"
    MAIL_PASSWORD = "pycavmail"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"

    def getBackendURL(self):
        MYIP = os.popen("dig +short txt ch whoami.cloudflare @1.0.0.1").read().replace('\n', '').replace('"', '')
        if(MYIP in ["52.66.152.129", "43.205.116.144"]):
            print(f"Using IP({MYIP})")
            return f"http://{MYIP}:2021"
        else:
            print('Unauthorized IP, using default pre-prod IP')
            return "http://52.66.152.129:2021"
        