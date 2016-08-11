import argparse
from bg_deploy.FSM import FSM
from bg_deploy.DATA import DATA
import logging
import sys

logger = logging.getLogger('bg_deploy')
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setLevel(logging.DEBUG)
logger.addHandler(out_hdlr)
logger.setLevel(logging.DEBUG)

def main(args):
    # parse arguments
    parser = argparse.ArgumentParser(args)
    parser.add_argument("--service_name", "-s",
                        type=str,
                        help="The service name you're deploying.",
                        required=True)

    parser.add_argument("--launch_config", "-l",
                        type=str,
                        help="Optional launch configuration you'd like applied to the target ASG.",
                        default= None)

    parser.add_argument("--canary", "-c",
                        help="Canary stage will take place",
                        action='store_true')

    parser.add_argument("--canary_elb", "-ce",
                        help="Canary ELB will be used,this ELB should be configured already",
                        action='store_true')

    parser.add_argument("--canary_timeout", '-ct',
                        type=int,
                        help="Timeout threshold for canary stage's ELB health check in seconds",
                        default=300)

    parser.add_argument("--scaleup_timeout", '-st',
                        type=int,
                        help="Timeout threshold for scaleup stage's ELB health check in seconds",
                        default=300)

    parser.add_argument("--profile", '-p',
                        type=str,
                        help="The profile\env to use specified inside your aws credentials file",
                        required=True)

    parser.add_argument("--step", "-sp",
                        help="The number of instances to deploy during each stagger deploy step",
                        type=int,
                        default=0)

    parser.add_argument("--step_interval", "-si",
                        help="The number of seconds between stagger deployment steps",
                        type=int,
                        default=60)

    parser.add_argument("--expect_yes", "-y",
                        help="Automatically proceed on all steps",
                        action='store_true',)

    args = parser.parse_args()

    # begin FSM
    fsm = FSM(service_name=args.service_name,
              canary_timeout=args.canary_timeout,
              canary_elb=args.canary_elb,
              canary=args.canary,
              scaleup_timeout=args.scaleup_timeout,
              profile=args.profile,
              launch_config=args.launch_config,
              step=args.step,
              step_interval=args.step_interval,
              expect_yes=args.expect_yes)

    fsm.run()

