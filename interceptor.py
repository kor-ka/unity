import pykka
import subprocess


class InterceptorActor(pykka.ThreadingActor):
    def __init__(self, manager):
        super(InterceptorActor, self).__init__()
        self.manager = manager

    def on_keyword(self):
        print("hi there")
        args = []
        args.insert(0, 'aplay')
        args.insert(1, "../kw.waw")
        p = subprocess.Popen(args)
        p.wait()

    def on_receive(self, message):
        if message["command"] == "kw":
            self.on_keyword()
