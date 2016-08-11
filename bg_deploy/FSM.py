from bg_deploy.DATA import DATA
from bg_deploy.States.INIT import INIT
from bg_deploy.States.CANARY import CANARY
from bg_deploy.States.SCALEUP import SCALEUP
from bg_deploy.States.FINISH import FINISH
from bg_deploy.States.ABORT import ABORT


ASG_BLUE_FORMAT = '{service}-blue'
ASG_GREEN_FORMAT = '{service}-green'


class FSM(object):
    def __init__(self,
                 service_name,
                 canary=False,
                 canary_elb=False,
                 launch_config=None,
                 canary_timeout=None,
                 scaleup_timeout=120,
                 profile=None,
                 step=None,
                 step_interval=20,
                 expect_yes=False):
        """
        Finite state machine for deploying to B\G ASGs
        :param service_name: String, representing the service being deployed
        :param canary: Bool, whether the canary state is required
        """
        self.data = DATA()
        self.data.cur_state = 'Init'
        self.data.prev_state = None
        self.data.service_name = service_name
        self.data.canary = canary
        self.data.canary_elb = canary_elb
        self.data.canary_timeout = canary_timeout
        self.data.scaleup_timeout = scaleup_timeout
        self.data.abort_message = None
        self.data.target_asg = None
        self.data.target_asg_org_configuration = None
        self.data.original_asg = None
        self.data.original_asg_org_configuration = None
        self.data.launch_config = launch_config
        self.data.profile = profile
        self.data.step = step
        self.data.step_interval = step_interval
        self.data.expect_yes = expect_yes



    def init_handler(self):
        init = INIT()
        init.run()

        return

    def canary_handler(self):
        canary = CANARY()
        canary.run()

        return

    def scaleup_handler(self):
        scaleup = SCALEUP()
        scaleup.run()

        return

    def finish_handler(self):
        finish = FINISH()
        finish.run()

        return

    def abort_handler(self):
        abort = ABORT()
        abort.run()

        return

    def run(self):
        if self.data.cur_state == 'Init':
            self.init_handler()
        if self.data.cur_state == 'Canary':
            self.canary_handler()
        if self.data.cur_state == 'ScaleUp':
            self.scaleup_handler()
        if self.data.cur_state == 'Finish':
            self.finish_handler()
        if self.data.cur_state == 'Abort':
            self.abort_handler()

