import threading

from arch import arch_model
from arch.univariate import HARX
from arch.univariate.base import ARCHModelResult

from controller.injector import Injector

GARCH = 'GARCH'
LINES = "=" * 100


class _CountdownLatch:
    def __init__(self, count):
        self.count = count
        self._event = threading.Event()

    def countdown(self):
        with threading.Lock():
            self.count -= 1
            if self.count == 0:
                self._event.set()

    def wait(self):
        self._event.wait()


class Analyzer:
    __ANALYZABLE_MODELS = [GARCH]

    def __init__(self, loader: Injector, vol=GARCH, p=1, q=1, col='Log Return'):
        if loader is None:
            raise RuntimeError('loader cannot be none')

        self.__loader = loader
        self.__cache = {}
        if vol not in Analyzer.__ANALYZABLE_MODELS:
            raise RuntimeError(f'model not in {Analyzer.__ANALYZABLE_MODELS}')
        self.__actual_models: list[HARX] = []
        self.actual_results: list[ARCHModelResult] = []
        self.__setup_models(vol, p, q, col)

    def worker(self, latch: _CountdownLatch, thread_id, model: HARX):
        print(f'thread {thread_id} start')
        self.actual_results[thread_id] = model.fit()
        print(f'thread {thread_id} done')
        latch.countdown()
        pass

    def fit(self):
        size = len(self.__actual_models)
        latch = _CountdownLatch(size)
        threads = []

        for index in range(size):
            t = threading.Thread(target=self.worker, args=(latch, index, self.__actual_models[index]))
            threads.append(t)
            t.start()

        latch.wait()

    def summary(self):

        for i in range(len(self.actual_results)):
            print(LINES)
            print(f'\tsummary for {self.__loader.indexes[i].i_name}')
            print(LINES)
            print(self.actual_results[i].summary())

    def __setup_models(self, vol, p, q, col):
        for index in self.__loader.indexes:
            self.__actual_models.append(
                arch_model(
                    index.daily_info[col], vol=vol,
                    p=p, q=q
                )
            )
            self.actual_results.append(None)
        pass
