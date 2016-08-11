# BG_Deploy

A script which automates the blue\green deployment process. The script uses a finite state machine which transitions through deployment states.

#### Installation
Make sure you have python3 and pip3 installed on your workstation.
Run the following command:

```
sudo pip3.4 install --extra-index-url https://devpi.longtailvideo.com/root/ltv/+simple/ bg_deploy
```

You should now have the bg_deploy binary in your path.

#### Usage
```
usage: ['--service_name', 'livestream', '--scaleup_timeout', '120', '--profile', 'stg', '--step', '3', '--canary', '-y', '--help']
       [-h] --service_name SERVICE_NAME [--launch_config LAUNCH_CONFIG]
       [--canary] [--canary_elb] [--canary_timeout CANARY_TIMEOUT]
       [--scaleup_timeout SCALEUP_TIMEOUT] --profile PROFILE [--step STEP]
       [--step_interval STEP_INTERVAL] [--expect_yes]

optional arguments:
  -h, --help            show this help message and exit
  --service_name SERVICE_NAME, -s SERVICE_NAME
                        The service name you're deploying.
  --launch_config LAUNCH_CONFIG, -l LAUNCH_CONFIG
                        Optional launch configuration you'd like applied to
                        the target ASG.
  --canary, -c          Canary stage will take place
  --canary_elb, -ce     Canary ELB will be used,this ELB should be configured
                        already
  --canary_timeout CANARY_TIMEOUT, -ct CANARY_TIMEOUT
                        Timeout threshold for canary stage's ELB health check
                        in seconds
  --scaleup_timeout SCALEUP_TIMEOUT, -st SCALEUP_TIMEOUT
                        Timeout threshold for scaleup stage's ELB health check
                        in seconds
  --profile PROFILE, -p PROFILE
                        The profile\env to use specified inside your aws
                        credentials file
  --step STEP, -sp STEP
                        The number of instances to deploy during each stagger
                        deploy step
  --step_interval STEP_INTERVAL, -si STEP_INTERVAL
                        The number of seconds between stagger deployment steps
  --expect_yes, -y      Automatically proceed on all steps
```

Specifying a launch configuration will apply this launch configuration to the target ASG.

Both canary_timeout and scaleup_timeout are defaulted to 300 seconds.

Specifying a canary ELB will attach a specific (already created and configured) ELB for canary testing.

Specifying a step performs a stagger deploy

Specifying a step_interval controls the pausing between stagger deploy steps. Defaults to 60 seconds





Example command line:

```
❯python3.4 bg_deploy --service_name livestream --canary_timeout 120 --scaleup_timeout 120 --canary --canary_timeout 120 --profile stg   
```

This script expects you to have a .aws/credentials file present in your home directory. For more information please see: http://docs.aws.amazon.com/java-sdk/latest/developer-guide/credentials.html and reference the credential file section. 

#### Flow Diagram explaining the states

![](docs/BG_deploy.png?raw=true "BG Deploy Flow Diagram")
