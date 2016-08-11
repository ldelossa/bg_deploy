def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class DATA(object):
    def __init__(self):
        self.cur_state = 'Init'
        self.prev_state = None
        self.service_name = None
        self.canary = None
        self.canary_elb = None
        self.canary_timeout = None
        self.scaleup_timeout = None
        self.abort_message = None
        self.target_asg = None
        self.original_asg = None
        self.target_asg_org_configuration = None
        self.original_asg_org_configuration = None
        self.launch_config = None
        self.profile = None
        self.step = None
        self.step_interval = None
        self.expect_yes = False

