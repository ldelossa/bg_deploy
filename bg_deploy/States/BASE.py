import logging
from datetime import datetime, timedelta
from time import sleep

from bg_deploy.AWS_Models.ELB import ELB
from bg_deploy.constants import *

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BASE(object):

    def _determine_elb_health(self, ASG):
        results = ASG.attached_loadbalancers_health
        return all(code['Healthy'] for code in results)

    def determine_new_instances_in_elb(self, ASG, state):

        ASG_Instances = [record['InstanceId'] for record in ASG.instances]

        for LB in ASG.attached_loadbalancers:
            elb = ELB(LB, ASG.profile)

            while True:

                elb_instances = [InstanceId['InstanceId'] for InstanceId in elb.instances]
                difference_list = [i for i in elb_instances if i in ASG_Instances]
                waiting_list = [i for i in ASG_Instances if i not in elb_instances]

                sleep(POLL_SLEEP)

                if sorted(difference_list) == sorted(ASG_Instances):
                    log.info(LOGFT_ELB_REGISTERED.format(state=state,
                                                         ELB=elb.name,
                                                         instances=difference_list))
                    break

                log.info(LOGFT_ELB_REGISTERING.format(state=state,
                                                      ELB=elb.name,
                                                      instances=waiting_list))

    def elb_health_check(self, ASG, threshold, state):
        """
        Takes in a threshold, sets a timer which will return false is expires.
        :param ASG: An ASG Object
        :param threshold: int representing timeout threshold
        :param state: current state of fsm (for logging purposes)
        :return:
        """
        now = datetime.now()
        while not self._determine_elb_health(ASG):
            if datetime.now() <= now + timedelta(0, threshold):
                expire_delta = (now + timedelta(0, threshold) - datetime.now())
                log.info(LOGFT_ELB_HEALTH_WAITING.format(state=state,
                                                         ELBs=ASG.attached_loadbalancers,
                                                         threshold=expire_delta))
                sleep(POLL_SLEEP)
            else:
                return False
        return True
