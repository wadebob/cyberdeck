import asyncio
import fcntl
import os
import pty
import shlex
import struct
import termios

import pyte
from rich.text import Text
from textual import events
from textual.app import App
from textual.widget import Widget

import time
import sys
picdir = os.path.join('/home/wade/RaspberryPi_JetsonNano/python/examples/pic')
libdir = os.path.join('/home/wade/RaspberryPi_JetsonNano/python/examples/lib')

from waveshare_epd import epd2in9_V2

epd = epd2in9_V2.EPD()
time_image = Image.new('1', (epd.height, epd.width), 255)
time_draw = ImageDraw.Draw(time_image)

def clearScreen():
    epd.init()
    epd.Clear(0xFF)

def splashScreen():
    Himage = Image.open(os.path.join(picdir, 'koala.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)
    epd.Clear(0xFF)
    epd.display_Base(epd.getbuffer(time_image))

if os.path.exists(libdir):
    sys.path.append(libdir)


class PyteDisplay:
    def __init__(self, lines):
        self.lines = lines

    def __rich_console__(self, console, options):
        for line in self.lines:
            yield line


class Terminal(Widget, can_focus=True):
    def __init__(self, send_queue, recv_queue, ncol, nrow):
        self.ctrl_keys = {
            "left": "\u001b[D",
            "right": "\u001b[C",
            "up": "\u001b[A",
            "down": "\u001b[B",
        }
        self.recv_queue = recv_queue
        self.send_queue = send_queue
        self.nrow = nrow
        self.ncol = ncol
        self._display = PyteDisplay([Text()])
        self._screen = pyte.Screen(self.ncol, self.nrow)
        self.stream = pyte.Stream(self._screen)
        asyncio.create_task(self.recv())
        asyncio.create_task(self.monitor_terminal())  # New line to start monitoring terminal
        super().__init__()
        self.focus()
        


    def render(self):
        return self._display
    
    def update_line(self,index):
        Tlines = [line.renderables[0].text for line in self._display.lines]
        time_draw.rectangle((0, 0+ (16*index), 296, 16+(16*index)), fill = 255)
        time_draw.text(0, 0+ (16*index), Tlines[index], fill = 0)
        newimage = time_image.crop([0, 0+ (16*index), 296, 16+(16*index)])
        time_image.paste(newimage, (0, 0+ (16*index)))  
        epd.display_Partial(epd.getbuffer(time_image))


        

    async def on_key(self, event: events.Key) -> None:
        char = self.ctrl_keys.get(event.key) or event.character
        await self.send_queue.put(["stdin", char])

    async def recv(self):
        while True:
            message = await self.recv_queue.get()
            cmd = message[0]
            if cmd == "setup":
                await self.send_queue.put(["set_size", self.nrow, self.ncol, 567, 573])
            elif cmd == "stdout":
                chars = message[1]
                self.stream.feed(chars)
                lines = []
                for i, line in enumerate(self._screen.display):
                    text = Text.from_ansi(line)
                    x = self._screen.cursor.x
                    if i == self._screen.cursor.y and x < len(text):
                        cursor = text[x]
                        cursor.stylize("reverse")
                        new_text = text[:x]
                        new_text.append(cursor)
                        new_text.append(text[x + 1:])
                        text = new_text
                    lines.append(text)
                self._display = PyteDisplay(lines)
                self.refresh()

    async def monitor_terminal(self):
        prev_content = [line.renderables[0].text for line in self._display.lines]
        while True:
            await asyncio.sleep(0.1)  # Adjust interval as needed
            current_content = [line.renderables[0].text for line in self._display.lines]
            for prev_line, current_line in zip(prev_content, current_content):
                if prev_line != current_line:
                    self.update_line(current_content.index(current_line))
            prev_content = current_content


class TerminalEmulator(App):

    def __init__(self, ncol, nrow):
        self.ncol = ncol
        self.nrow = nrow
        self.data_or_disconnect = None
        self.fd = self.open_terminal()
        self.p_out = os.fdopen(self.fd, "w+b", 0)
        self.recv_queue = asyncio.Queue()
        self.send_queue = asyncio.Queue()
        self.event = asyncio.Event()
        super().__init__()

    def compose(self):
        asyncio.create_task(self._run())
        asyncio.create_task(self._send_data())
        yield Terminal(self.recv_queue, self.send_queue, self.ncol, self.nrow)

    def open_terminal(self):
        pid, fd = pty.fork()
        if pid == 0:
            argv = shlex.split("bash")
            env = dict(TERM="linux", LC_ALL="en_GB.UTF-8", COLUMNS=str(self.ncol), LINES=str(self.nrow))
            os.execvpe(argv[0], argv, env)
        return fd

    async def _run(self):
        loop = asyncio.get_running_loop()

        def on_output():
            try:
                self.data_or_disconnect = self.p_out.read(65536).decode()
                self.event.set()
            except Exception:
                loop.remove_reader(self.p_out)
                self.data_or_disconnect = None
                self.event.set()

        loop.add_reader(self.p_out, on_output)
        await self.send_queue.put(["setup", {}])
        while True:
            msg = await self.recv_queue.get()
            if msg[0] == "stdin":
                self.p_out.write(msg[1].encode())
            elif msg[0] == "set_size":
                winsize = struct.pack("HH", msg[1], msg[2])
                fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    async def _send_data(self):
        while True:
            await self.event.wait()
            self.event.clear()
            if self.data_or_disconnect is None:
                await self.send_queue.put(["disconnect", 1])
            else:
                await self.send_queue.put(["stdout", self.data_or_disconnect])


if __name__ == "__main__":
    clearScreen()
    splashScreen()
    
    app = TerminalEmulator(80, 5)
    app.run()
