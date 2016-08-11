
LOGFT_ASG_DESIRED = '{state}: Setting {type} ASG: ({ASG}) desired to {value}'

LOGFT_ASG_INSTANCE_COUNT = '{state}: Waiting for {type} ASG: ({ASG}) ' \
                           'instance count to change. Current: {cur_instances} Desired: {des_instances}'

LOGFT_ELB_HEALTH_WAITING = '{state}: Waiting for ELB(s): {ELBs} health check to pass. Threshold: {threshold} remaining.'

LOGFT_ELB_ALLOCATE = '{state}: {allocation} ELB : {ELB} to {type} ({ASG})'

LOGFT_LC_ALLOCATE = '{state}: {allocation} Launch Configuration: ({LC}) to {type} ({ASG})'

LOGFT_ELB_REGISTERING = '{state}: Waiting for ELB: ({ELB}) to register the following instances {instances}'

LOGFT_ELB_REGISTERED = '{state}: ELB: ({ELB}) registered the following instances {instances}'

LOGFT_STATE_TRANSITION = '{state}: Finished, transitioning to {trans_state}'

LOGFT_ABORT = 'Abort: Aborted from previous state {prev_state} \n' \
              'Abort: Aborted for the following reason: \n  {abort_msg}'

LOGFT_CANARY_LIVE = 'Canary: Canary is now live, please proceed with manual testing'

LOGFT_DETERMINE_ASG = '{state}: Target ASG Found: ({target_asg}). Original ASG Found ({org_asg})'

LOGFT_SCALEDOWN = '{state}: {allocation} scale down on {type} ({ASG})'

LOGFT_STATE_ENTRY = '{state}: Entering {state} state.'

POLL_SLEEP = 15
