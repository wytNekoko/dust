from dust import create_app
from dust.logics.liquidation import *
from dust.logics.cal_builders_num import cal_builders
from dust.logics.github_contributors import *


def monthly_liquidate():
    app = create_app()
    with app.app_context():
        liquidate()
        get_monthly_focus()


def get_builders_num():
    app = create_app()
    with app.app_context():
        cal_builders()


def github_plan():
    app = create_app('dust.config.TestConfig')
    with app.app_context():
        get_rank()
        github_score()
        cal_gift()


if __name__ == '__main__':
    github_plan()

