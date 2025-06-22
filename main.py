from flask import Flask
from flask_cors import CORS
from app import create_app


app = create_app()
app.config['SECRET_KEY'] = 'secret!'

host_addr = "0.0.0.0"
port_num = 8080

if __name__ == "__main__":              
    app.run(host=host_addr, port=port_num,debug=True)