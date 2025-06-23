import sys
import os
sys.path.append(os.path.abspath("."))

from app import create_app

app = create_app()
app.config['SECRET_KEY'] = 'secret!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
