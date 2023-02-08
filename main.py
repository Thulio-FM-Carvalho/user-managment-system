from flask import Flask
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)


@app.route('/')
def index():
    return render_template('index.html', title="")


from user_routes import *
from admin_routes import *

if __name__ == "__main__":
    app.run(debug=True)
