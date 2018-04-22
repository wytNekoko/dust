from dust import create_app
from dust.core import db
from dust.models.user_planet import User, Planet, Team, BuildRecord, Suggestion

app = create_app()

if __name__ == '__main__':
    app.run()
