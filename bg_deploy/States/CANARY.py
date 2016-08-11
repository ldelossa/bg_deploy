from bg_deploy.helper_functions import _input_loop
from bg_deploy.DATA import DATA
from bg_deploy.States.BASE import BASE
from bg_deploy.constants import *
from time import sleep
import logging

CANARY_ELB_FORMAT = '{service}-canary'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class CANARY(BASE):
    def __init__(self):
        self.data = DATA()
        log.info("=" * 38)
        log.info(LOGFT_STATE_ENTRY.format(state=self.data.cur_state))

    def launch_canary(self):

        # Set desired instance count on target ASG to one
        log.info(LOGFT_ASG_DESIRED.format(state=self.data.cur_state,
                                          type='target',
                                          ASG=self.data.target_asg.name,
                                          value=1))
        self.data.target_asg.max_size = 1
        self.data.target_asg.min_size = 0
        self.data.target_asg.desired_capacity = 1

        # Wait for asg instance count to be one
        while self.data.target_asg.instance_count < 1:
            log.info(LOGFT_ASG_INSTANCE_COUNT.format(state=self.data.cur_state,
                                                     type='target',
                                                     ASG=self.data.target_asg.name,
                                                     cur_instances=self.data.target_asg.instance_count,
                                                     des_instances=1))
            sleep(POLL_SLEEP)

        # Wait for elb to register new instances in ASG (common function implemented in base class)
        super(CANARY, self).determine_new_instances_in_elb(self.data.target_asg, state=self.data.cur_state)

        # Wait until healthy, state transition to abort if returns False
        if not super(CANARY, self).elb_health_check(ASG=self.data.target_asg,
                                                    threshold=self.data.scaleup_timeout,
                                                    state=self.data.cur_state):
            self.data.prev_state = 'Canary'
            self.data.cur_state = 'Abort'
            self.data.abort_message = 'Canary: ELB health check threshold expired'

            return

    def run(self):

        # If canary ELB specified; add only canary ELB; else add original ELBs
        if self.data.canary_elb:
            canary_elb = CANARY_ELB_FORMAT.format(service=self.data.service_name)
            log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.cur_state,
                                               allocation='attaching',
                                               ELB=canary_elb,
                                               type='target',
                                               ASG=self.data.target_asg.name))
            self.data.target_asg.attach_loadbalancers(canary_elb)
        else:
            target_elb = self.data.original_asg_org_configuration['LoadBalancerNames']
            log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.cur_state,
                                               allocation='attaching',
                                               ELB=target_elb,
                                               type='target',
                                               ASG=self.data.target_asg.name))
            self.data.target_asg.attach_loadbalancers(target_elb)

        # Launch canary
        self.launch_canary()

        # Wait for user input, unless --expect_yes flag specified
        log.info(LOGFT_CANARY_LIVE)
        if not self.data.expect_yes:
            if _input_loop('Proceed: Y/N '):
                # State transition to ScaleUp
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                     trans_state='Scaleup'))
                self.data.cur_state = 'ScaleUp'
                self.data.prev_state = 'Canary'
            else:
                # State transition to Abort
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                     trans_state='Abort'))
                self.data.cur_state = 'Abort'
                self.data.prev_state = 'Canary'
                self.data.abort_message = 'During Canary State, user chose not to proceed'
        else:
            # State transition to ScaleUp
            log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                   trans_state='Scaleup'))
            self.data.cur_state = 'ScaleUp'
            self.data.prev_state = 'Canary'



