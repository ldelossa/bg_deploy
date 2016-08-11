import boto3


class ELB(object):
    """
    Object representing a single ELB, extracting the information we use for manipulation
    This class makes heavy use of the @property decorator to query the API on every attribute lookup, ensuring
    no stale data will be present
    """
    def __init__(self, elb_name, profile):
        session = boto3.Session(profile_name=profile)
        self.boto_client = session.client('elb')
        self.name = elb_name
        self.profile = profile

    def _get_desc(self):
        return self.boto_client.describe_load_balancers(LoadBalancerNames=[self.name])['LoadBalancerDescriptions'][0]

    @property
    def instance_health(self):
        _checks = self.boto_client.describe_instance_health(LoadBalancerName=self.name)['InstanceStates']

        if any(status != "InService" for status in [code['State'] for code in _checks]):
            return False
        else:
            return True

    @property
    def instances(self):
        return self._get_desc()['Instances']

    @property
    def instance_count(self):
        return len(self._get_desc()['Instances'])
