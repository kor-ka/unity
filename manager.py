import pykka

import interceptor


class ManagerActor(pykka.ThreadingActor):
    def __init__(self, mic):
        super(ManagerActor, self).__init__()
        self.interceptor = interceptor.InterceptorActor.start(self.actor_ref, mic)

    def on_receive(self, message):
        self.interceptor.tell(message)
