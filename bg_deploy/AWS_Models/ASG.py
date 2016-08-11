import boto3

from bg_deploy.AWS_Models.ELB import ELB


class ASG(object):
    """
    Object representing a single ASG, extracting the information we use for manipulation
    This class makes heavy use of the @property decorator to query the API on every attribute lookup, ensuring
    no stale data will be present
    """
    def __init__(self, asg_name, profile):
        session = boto3.Session(profile_name=profile)
        self.boto_client = session.client('autoscaling')
        self.name = asg_name
        self.profile = profile

    def _get_desc(self):
        return self.boto_client.describe_auto_scaling_groups(AutoScalingGroupNames=[self.name])['AutoScalingGroups'][0]

    @property
    def instances(self):
        return self._get_desc()['Instances']

    @property
    def instance_count(self):
        return len((self._get_desc())['Instances'])

    @property
    def min_size(self):
        asg_description = self._get_desc()
        return asg_description['MinSize']

    @min_size.setter
    def min_size(self, value):
        self.boto_client.update_auto_scaling_group(AutoScalingGroupName=self.name, MinSize=value)
        # return (self._get_desc())['MinSize']

    @property
    def max_size(self):
        return (self._get_desc())['MaxSize']

    @max_size.setter
    def max_size(self, value):
        self.boto_client.update_auto_scaling_group(AutoScalingGroupName=self.name, MaxSize=value)
        # return (self._get_desc())['MaxSize']

    @property
    def desired_capacity(self):
        return (self._get_desc())['DesiredCapacity']

    @desired_capacity.setter
    def desired_capacity(self, value):
        self.boto_client.update_auto_scaling_group(AutoScalingGroupName=self.name, DesiredCapacity=value)

    @property
    def attached_loadbalancers_health(self):

        loadbalancer_list = []
        # Instantiate our load balancer class based on text output of API call, store ELB objects in list
        for loadbalancer in (self._get_desc())['LoadBalancerNames']:
            loadbalancer_list.append(ELB(loadbalancer, self.profile))

        # Create attribute structure to provide load balancer name, and whether all health check passed or not
        check_results = []
        for elb in loadbalancer_list:
            check_results.append({'Load_Balancer': elb.name, 'Healthy': elb.instance_health,
                                  'Instance_Count': elb.instance_count})

        return check_results

    @property
    def attached_loadbalancers(self):
        return (self._get_desc())['LoadBalancerNames']

    def attach_loadbalancers(self, loadbalancers):
        '''
        Attaches a list of load balancers from the ASG
        :param loadbalancers: list of load balancers
        :return:
        '''
        self.boto_client.attach_load_balancers(AutoScalingGroupName=self.name, LoadBalancerNames=loadbalancers)

    def detach_loadbalancers(self, loadbalancers):
        '''
        Detaches a list of load balancers from the ASG
        :param loadbalancers: list of load balancers
        :return:
        '''
        self.boto_client.detach_load_balancers(AutoScalingGroupName=self.name, LoadBalancerNames=loadbalancers)

    @property
    def launch_configuration(self):
        return (self._get_desc())['LaunchConfigurationName']

    @launch_configuration.setter
    def launch_configuration(self, value):
        self.boto_client.update_auto_scaling_group(AutoScalingGroupName=self.name, LaunchConfigurationName=value)

    def disable_scale_down(self):
        processes = ['ReplaceUnhealthy', 'AZRebalance', 'Terminate']
        self.boto_client.suspend_processes(AutoScalingGroupName=self.name, ScalingProcesses= processes)

    def enable_scale_down(self):
        processes = ['ReplaceUnhealthy', 'AZRebalance', 'Terminate']
        self.boto_client.resume_processes(AutoScalingGroupName=self.name, ScalingProcesses=processes)

