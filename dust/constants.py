class Status:
    """常用状态常量"""
    DEFAULT = 0
    UNSHELVED = 99


class Feedback:
    ADVICE = 0
    COOPERATION = 1
    OTHERS = 2


class Notify:
    BUILD = 0
    SPY = 1


NotifyContent = {
    Notify.BUILD: '{0} times remained to build planets today.',
    Notify.SPY: 'The email of {0}\'s captain is {1}.'
}