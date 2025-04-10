
from main import app

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///isbn_database.db'
    app.run(host='127.0.0.1', port=5000, debug=False)
