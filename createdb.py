from pariksha import create_app,db
with app.app_context():
    print('DB Created')
    db.create_all()