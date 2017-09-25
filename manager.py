import pykka

import interceptor


class ManagerActor(pykka.ThreadingActor):
    def __init__(self):
        super(ManagerActor, self).__init__()
        self.interceptor = interceptor.InterceptorActor.start(self.actor_ref)

    def on_receive(self, message):
        self.interceptor.tell(message)