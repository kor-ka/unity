import pykka

import interceptor


class ManagerActor(pykka.ThreadingActor):
    def __init__(self, ls):
        super(ManagerActor, self).__init__()
        self.interceptor = interceptor.InterceptorActor.start(self.actor_ref)
