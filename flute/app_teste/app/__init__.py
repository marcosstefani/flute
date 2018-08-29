from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask( __name__ )
app.config.from_object( 'config.dev' )
db = SQLAlchemy( app )

@app.route( '/' )
def index():
    return render_template( 'home.html' )

@app.errorhandler( 403 )
def forbidden( error ):
    return render_template('error.html', number= 403, title=' Forbidden'), 403

@app.errorhandler( 404 )
def page_not_found( error ):
    return render_template('error.html', number= 404, title=' Page Not Found'), 404

@app.errorhandler( 500 )
def internal_server_error( error ):
    return render_template('error.html', number= 500, title=' Internal Server Error'), 500

db.create_all()