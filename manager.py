import pykka

import interceptor
import keyword_listener


class ManagerActor(pykka.ThreadingActor):
    def __init__(self):
        super(ManagerActor, self).__init__()
        self.interceptor = interceptor.InterceptorActor.start(self.actor_ref)
        self.listener = keyword_listener.KeywordActor.start(self.actor_ref, self.interceptor)

    def on_start(self):
        pass

    def on_receive(self, message):
        pass
