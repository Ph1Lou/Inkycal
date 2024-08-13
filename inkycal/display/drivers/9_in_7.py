"""
9.7" driver class
Copyright by aceinnolab
"""
import os
from subprocess import run

from inkycal.settings import Settings

# Display resolution
EPD_WIDTH = 1200
EPD_HEIGHT = 825

settings = Settings()


class EPD:

    def __init__(self):
        """9.7" epaper class"""
        pass

    def init(self):
        pass

    def display(self, command):
        """displays an image"""
        try:
            run_command = command.split()
            run(run_command)
        except:
            print("oops, something didn't work right :/")

    def getbuffer(self, image):
        """ad-hoc"""
        image = image.rotate(90, expand=True)
        image.convert("RGB").save(os.path.join(settings.IMAGE_FOLDER, "canvas.bmp"), "BMP")
        command = f'sudo {settings.PARALLEL_DRIVER_PATH}/epd -{settings.VCOM} 0 {os.path.join(settings.IMAGE_FOLDER, "canvas.bmp")}'
        print(command)
        return command

    def sleep(self):
        pass
