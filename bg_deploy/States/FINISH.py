from bg_deploy.DATA import DATA
from bg_deploy.States.BASE import BASE
from bg_deploy.helper_functions import _input_loop
from bg_deploy.constants import *
from time import sleep
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FINISH(BASE):
    def __init__(self):
        self.data = DATA()
        log.info("=" * 38)
        log.info(LOGFT_STATE_ENTRY.format(state=self.data.cur_state))

    def run(self):

        # Remove ELBs from original ASG
        log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.cur_state,
                                           allocation='detaching',
                                           ELB=self.data.original_asg.attached_loadbalancers,
                                           type='original',
                                           ASG=self.data.original_asg.name))
        self.data.original_asg.detach_loadbalancers(self.data.original_asg.attached_loadbalancers)

        # Enable ScaleDown
        log.info(LOGFT_SCALEDOWN.format(state=self.data.cur_state,
                                        allocation='enabling',
                                        type='target',
                                        ASG=self.data.target_asg.name))
        self.data.target_asg.enable_scale_down()

        # Wait for user input
        print("Finish: ELB has been removed from Original ASG: ({}), Waiting for user input to continue. "
              "Next step is to terminate the instances!!".format(self.data.original_asg.name))
        if not self.data.expect_yes:
            if _input_loop('Proceed Y/N? '):
                log.info(LOGFT_ASG_DESIRED.format(state=self.data.cur_state,
                                                  type='original',
                                                  ASG=self.data.original_asg.name,
                                                  value=0))
                self.data.original_asg.min_size = 0
                self.data.original_asg.desired_capacity = 0
                while self.data.original_asg.instance_count != 0:
                    log.info(LOGFT_ASG_INSTANCE_COUNT.format(state=self.data.cur_state,
                                                         type='original',
                                                         ASG=self.data.target_asg.name,
                                                         cur_instances=self.data.original_asg.instance_count,
                                                         des_instances=0))
                    sleep(POLL_SLEEP)
            else:
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                   trans_state='Abort'))
                self.data.prev_state = 'Finish'
                self.data.cur_state = 'Abort'
                self.data.abort_message = 'Finish: User aborted finish state, ' \
                              'instances have not been terminated from original ASG'
        else:
            log.info(LOGFT_ASG_DESIRED.format(state=self.data.cur_state,
                                              type='original',
                                              ASG=self.data.original_asg.name,
                                              value=0))
            self.data.original_asg.min_size = 0
            self.data.original_asg.desired_capacity = 0
            while self.data.original_asg.instance_count != 0:
                log.info(LOGFT_ASG_INSTANCE_COUNT.format(state=self.data.cur_state,
                                                     type='original',
                                                     ASG=self.data.target_asg.name,
                                                     cur_instances=self.data.original_asg.instance_count,
                                                     des_instances=0))
                sleep(POLL_SLEEP)

