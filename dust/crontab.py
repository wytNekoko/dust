from dust import create_app
from dust.logics.liquidation import *


def main():
    app = create_app()
    with app.app_context():
        liquidate()
        get_monthly_focus()


if __name__ == '__main__':
    main()

