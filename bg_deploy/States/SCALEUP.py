from bg_deploy.States.BASE import BASE
from bg_deploy.DATA import DATA
from bg_deploy.constants import *
from time import sleep
import logging


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SCALEUP(BASE):
    def __init__(self):
        self.data = DATA()
        log.info("=" * 38)
        log.info(LOGFT_STATE_ENTRY.format(state=self.data.cur_state))

    def scale_up(self, ASG, desired, step, interval):

        # Init step index, used to keep track of the value used for AWS api calls
        if step > desired:
            si = desired
        else:
            si = step

        # Increase ASG count to si, wait while ASG instance count increases, check ELB
        log.info(LOGFT_ASG_DESIRED.format(state=self.data.cur_state,
                                          type='target',
                                          ASG=self.data.target_asg.name,
                                          value=si))
        ASG.desired_capacity = si

        while ASG.instance_count < si:
            log.info(LOGFT_ASG_INSTANCE_COUNT.format(state=self.data.cur_state,
                                                     type='target',
                                                     ASG=self.data.target_asg.name,
                                                     cur_instances=ASG.instance_count,
                                                     des_instances=si))
            sleep(POLL_SLEEP)

        # Wait for elb to register new instances in ASG (common function implemented in base class)
        super(SCALEUP, self).determine_new_instances_in_elb(ASG, self.data.cur_state)

        # Wait until healthy, returns false if failed
        if not super(SCALEUP, self).elb_health_check(ASG, self.data.scaleup_timeout, 'ScaleUp'):
            return False

        sleep(interval)

        if step > desired:
            desired -= desired
        else:
            desired -= step

        while desired >= step:
            si += step

            log.info(LOGFT_ASG_DESIRED.format(state=self.data.cur_state,
                                              type='target',
                                              ASG=self.data.target_asg.name,
                                              value=si))
            ASG.desired_capacity = si

            while ASG.instance_count < si:
                log.info(LOGFT_ASG_INSTANCE_COUNT.format(state=self.data.cur_state,
                                                         type='target',
                                                         ASG=self.data.target_asg.name,
                                                         cur_instances=ASG.instance_count,
                                                         des_instances=si))
                sleep(POLL_SLEEP)

            super(SCALEUP, self).determine_new_instances_in_elb(ASG, self.data.cur_state)

            if not super(SCALEUP, self).elb_health_check(ASG, self.data.scaleup_timeout, 'ScaleUp'):
                return False

            sleep(interval)
            desired -= step

        if desired == 0:
            return True

        elif desired > 0:
            # Add remaining desire value to step index to obtain final desired value
            log.info(LOGFT_ASG_DESIRED.format(state=self.data.cur_state,
                                              type='target',
                                              ASG=self.data.target_asg.name,
                                              value=si + desired))

            ASG.desired_capacity = (si + desired)

            while ASG.instance_count < si:
                log.info(LOGFT_ASG_INSTANCE_COUNT.format(state=self.data.cur_state,
                                                         type='target',
                                                         ASG=self.data.target_asg.name,
                                                         cur_instances=self.data.target_asg.instance_count,
                                                         des_instances=si + desired))
                sleep(interval)

            super(SCALEUP, self).determine_new_instances_in_elb(ASG, state=self.data.cur_state)

            if not super(SCALEUP, self).elb_health_check(ASG, self.data.scaleup_timeout, 'ScaleUp'):
                return False

            return True

    def run(self):
        # Set target ASG's max to original ASG's max
        self.data.target_asg.max_size = self.data.original_asg_org_configuration['MaxSize']

        # If canary_elb set, remove canary elb, and add original, else check target attached ELB matches Original
        if self.data.canary_elb:
            log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.curstate,
                                               allocation='detaching',
                                               ELB=self.data.target_asg.attached_loadbalancers,
                                               type='target',
                                               ASG=self.data.target_asg.name))
            self.data.target_asg.detach_loadbalancers(self.data.target_asg.attached_loadbalancers)

            log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.curstate,
                                               allocation='attaching',
                                               ELB=self.data.original_asg_org_configuration['LoadBalancerNames'],
                                               type='target',
                                               ASG=self.data.target_asg.name))
            self.data.target_asg.attached_loadbalancers(self.data.original_asg_org_configuration['LoadBalancerNames'])

        elif sorted(self.data.target_asg.attached_loadbalancers) != sorted(self.data.original_asg_org_configuration['LoadBalancerNames']):
            log.info(LOGFT_ELB_ALLOCATE.format(state=self.data.cur_state,
                                               allocation='attaching',
                                               ELB=self.data.original_asg_org_configuration['LoadBalancerNames'],
                                               type='target',
                                               ASG=self.data.target_asg.name))
            self.data.target_asg.attach_loadbalancers(self.data.original_asg_org_configuration['LoadBalancerNames'])

        # If step argument not defined
        if self.data.step is None or self.data.step == 0:

            self.data.step_interval = 0

            if not self.scale_up(self.data.target_asg,
                                 desired=self.data.original_asg.desired_capacity,
                                 step=self.data.original_asg.desired_capacity,
                                 interval=self.data.step_interval):

                # State transition to Abort
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                       trans_state='Abort'))

                self.data.prev_state = 'ScaleUp'
                self.data.cur_state = 'Abort'
                self.data.abort_message = 'ScaleUp: There has been an issue during scaling.'

            else:
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                       trans_state='Finish'))
                self.data.prev_state = 'ScaleUp'
                self.data.cur_state = 'Finish'
        # If step argument is defined
        elif self.data.step > 0:

            if self.data.step_interval is None:
                self.data.step_interval = 0

            if not self.scale_up(self.data.target_asg,
                                 desired=self.data.original_asg.desired_capacity,
                                 step=self.data.step,
                                 interval=self.data.step_interval):

                # State transition to Abort
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                       trans_state='Abort'))
                self.data.prev_state = 'ScaleUp'
                self.data.cur_state = 'Abort'
                self.data.abort_message = 'ScaleUp: There has been an issue during scaling.'

            else:
                log.info(LOGFT_STATE_TRANSITION.format(state=self.data.cur_state,
                                                       trans_state='Finish'))
                self.data.prev_state = 'ScaleUp'
                self.data.cur_state = 'Finish'

