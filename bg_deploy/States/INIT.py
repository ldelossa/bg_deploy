from bg_deploy.AWS_Models.ASG import ASG
from bg_deploy.DATA import DATA
from bg_deploy.States.BASE import BASE
from bg_deploy.constants import *
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Constants for ASG names
ASG_BLUE_FORMAT = '{service}-blue'
ASG_GREEN_FORMAT = '{service}-green'


class INIT(BASE):
    def __init__(self):
        self.data = DATA()
        log.info("=" * 38)
        log.info(LOGFT_STATE_ENTRY.format(state=self.data.cur_state))

    def determine_asg(self):

        asg1 = ASG_BLUE_FORMAT.format(service=self.data.service_name)
        asg2 = ASG_GREEN_FORMAT.format(service=self.data.service_name)

        asg1 = ASG(asg1, self.data.profile)
        asg2 = ASG(asg2, self.data.profile)

        target, original = sorted([asg1, asg2], key=lambda asg: asg.instance_count)

        if target.instance_count == 0 and original.instance_count > 0:
            log.info(LOGFT_DETERMINE_ASG.format(state=self.data.cur_state,
                                                target_asg=target.name,
                                                org_asg=original.name))
            self.data.target_asg, self.data.original_asg = target, original
            return True
        else:
            return False

    def run(self):

        # Obtain target and orignal ASG, will return false if cannot determine
        results = self.determine_asg()

        if not results:
            # State transition condition
            self.data.cur_state = 'Abort'
            self.data.prev_state = 'Init'
            self.data.abort_message = 'Failed during INIT state. Could not determine' \
                                      'which ASG is target'
            return

        # Disable Scale Down
        log.info(LOGFT_SCALEDOWN.format(state=self.data.cur_state,
                                        allocation='disabling',
                                        type='target',
                                        ASG=self.data.target_asg.name))
        self.data.target_asg.disable_scale_down()

        # If target ASG is attached to ELB, remove
        if len(self.data.target_asg.attached_loadbalancers) > 0:
            log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.cur_state,
                                               allocation='detaching',
                                               ELB=self.data.target_asg.attached_loadbalancers,
                                               type='target',
                                               ASG=self.data.target_asg.name))
            self.data.target_asg.detach_loadbalancers(self.data.target_asg.attached_loadbalancers)

        # Store original configuration state or original ASG
        self.data.original_asg_org_configuration = self.data.original_asg._get_desc()

        # If launch configuration is specified, apply to target ASG
        if self.data.launch_config:
            log.info(LOGFT_LC_ALLOCATE.format(state=self.data.cur_state,
                                              allocation='attaching',
                                              type='target',
                                              LC=self.data.launch_config,
                                              ASG=self.data.target_asg.name))
            self.data.target_asg.launch_configuration = self.data.launch_config

        # State transition decision
        if self.data.canary:
            log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                   trans_state='Canary'))
            self.data.cur_state = 'Canary'
            self.data.prev_state = 'Init'
        else:
            log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                   trans_state='ScaleUp'))
            self.data.cur_state = 'ScaleUp'
            self.data.prev_state = 'Init'

        return



