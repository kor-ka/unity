import pykka

import interceptor


class ManagerActor(pykka.ThreadingActor):
    def __init__(self, mic):
        super(ManagerActor, self).__init__()
        self.interceptor = interceptor.InterceptorActor.start(self.actor_ref, mic)

    def on_start(self):
        pass

    def on_receive(self, message):
        if message["command"] == "kw":
            self.interceptor.tell(message)
