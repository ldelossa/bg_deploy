from bg_deploy.DATA import DATA
from bg_deploy.States.BASE import BASE
from bg_deploy.constants import LOGFT_ABORT, LOGFT_STATE_ENTRY
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ABORT(BASE):
    def __init__(self):
        self.data = DATA()
        log.info("=" * 38)
        log.info(LOGFT_STATE_ENTRY.format(state=self.data.cur_state))

    def run(self):
        log.info(LOGFT_ABORT.format(prev_state=self.data.prev_state,
                                    abort_msg=self.data.abort_message))
        input("ABORT: Please investigate issues and press any key to exit...")