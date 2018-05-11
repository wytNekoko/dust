from dust import create_app
from dust.logics.liquidation import *
from dust.logics.cal_builders_num import cal_builders


def monthly_liquidate():
    app = create_app()
    with app.app_context():
        liquidate()
        get_monthly_focus()


def get_builders_num():
    app = create_app()
    with app.app_context():
        cal_builders()


if __name__ == '__main__':
    get_builders_num()

