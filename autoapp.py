from dust import create_app
from dust.core import db
from dust.models.user_planet import *

app = create_app()

if __name__ == '__main__':
    app.run()
