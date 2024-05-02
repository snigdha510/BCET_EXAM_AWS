from pariksha import create_app,db

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print('DB Created')
        db.create_all()