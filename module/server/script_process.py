# This Python file uses the following encoding: utf-8
# @author runhey
# 脚本进程
# github https://github.com/runhey
import multiprocessing
# from multiprocessing import Process, Queue
from enum import Enum

from module.logger import logger

from module.server.script_websocket import ScriptWSManager

class ScriptState(int, Enum):
    INACTIVE = 1
    RUNNING = 2
    WARNING = 3
    UPDATING = 4

class ScriptProcess(ScriptWSManager):

    def __init__(self, config_name: str) -> None:
        super().__init__()
        self.config_name = config_name  # config_name
        self.log_pipe_out, self.log_pipe_in = multiprocessing.Pipe(False)
        self.state_queue = multiprocessing.Queue()
        self.state: ScriptState = ScriptState.INACTIVE
        self._process = multiprocessing.Process(target=self.func,
                                                args=(self.state_queue, self.log_pipe_in,),
                                                name=self.config_name,
                                                daemon=True)




    def start(self):
        if self._process is None:
            logger.warning(f'Script {self.config_name} is not initialized')
            return
        if self._process.is_alive():
            logger.warning(f'Script {self.config_name} is already running and first stop it')
            self.stop()
        self._process.start()
        self.state = ScriptState.RUNNING

    def stop(self):
        if self._process is None:
            logger.warning(f'Script {self.config_name} is not initialized')
            return
        if not self._process.is_alive():
            logger.warning(f'Script {self.config_name} is not running')
            return
        self._process.terminate()
        self.state = ScriptState.INACTIVE




    def func(self, state_queue, log_pipe_in):
        self.start_log(log_pipe_in)
        try:
            from script import Script
            script = Script(config_name=self.config_name)
            script.state_queue = state_queue
            # script.loop()
            # 脚本启动
            from time import sleep
            logger.info(f'Script {self.config_name} start')
            sleep(5)
            logger.info(f'Script {self.config_name} end')
            exit(0)
            raise Exception('test')
        except SystemExit as e:
            logger.info(f'Script {self.config_name} exit')
            self.state = ScriptState.WARNING
        except Exception as e:
            logger.exception(f'Run script {self.config_name} error')
            logger.error(f'Error: {e}')
            raise

    def start_log(self, log_pipe_in) -> None:
        try:
            from module.logger import set_file_logger, set_func_logger
            set_file_logger(name=self.config_name)
            set_func_logger(log_pipe_in.send)
        except Exception as e:
            logger.exception(f'Start log error')
            logger.error(f'Error: {e}')
            raise


    async def broadcast_state_log(self):
        try:
            state = self.state_queue.get_nowait()
            if not state:
                pass
            await self.broadcast_state(state)
        except Exception as e:
            pass



if __name__ == '__main__':
    p = ScriptProcess('oas1')
    p.start()
    from time import sleep
    sleep(10)
    logger.info(p._process.exitcode)


