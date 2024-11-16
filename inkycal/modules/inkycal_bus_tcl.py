
from inkycal.modules.template import inkycal_module
from inkycal.custom import *
import requests
from datetime import datetime
# Show less logging for request module
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def extract_time(item):
    raw_datetime = item.get("date_time")
    if raw_datetime:
        dt = datetime.strptime(raw_datetime, "%Y%m%dT%H%M%S")
        return dt.strftime("%Hh%M")
    return None

def get_prochaines_horaires(ligne, arret):

    url = "https://carte.tcl.fr/api/schedules"
    params = {
        "stop": "stop_point:tcl:SP:" + arret,
        "route": "route:tcl:" + ligne
    }
    headers = {
        "Referer": "https://carte.tcl.fr/"
    }

    try:
        response = requests.get(url,
                                params=params,
                                headers=headers)

        if response.status_code == 200:
            return list(filter(None, map(extract_time, response.json())))
        else:
            print(f"Erreur {response.status_code}: {response.text}")

    except requests.RequestException as e:
        print(f"Une erreur est survenue : {e}")


class BusTCL(inkycal_module):

    name = "TCl API"

    def __init__(self, config):

        super().__init__(config)

        config = config['config']

        self.stops = config['stops']
        self.lines = config['lines']

        if len(self.stops) != len(self.lines):
            raise Exception("les tailles des listes des lignes et des arrets sont differentes")

        # give an OK message
        logger.debug(f'{__name__} loaded')

    def generate_image(self):
        """Generate image for this module"""

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        im_size = im_width, im_height
        logger.debug(f'image size: {im_width} x {im_height} px')

        # Create an image for black pixels and one for coloured pixels
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Check if internet is available
        if internet_available():
            logger.debug('Connection test passed')
        else:
            logger.error("Network not reachable. Please check your connection.")
            raise NetworkNotReachableError


        # Set some parameters for formatting feeds
        line_spacing = 5
        text_bbox = self.font.getbbox("hg")
        line_height = text_bbox[3] + line_spacing
        line_width = im_width
        max_lines = (im_height // (line_height + line_spacing))

        logger.debug(f"max_lines: {max_lines}")

        # Calculate padding from top so the lines look centralised
        spacing_top = int(im_height % line_height / 2)

        # Calculate line_positions
        line_positions = [
            (0, spacing_top + _ * line_height) for _ in range(max_lines)]

        logger.debug(f'line positions: {line_positions}')

        horaires = [
            ', '.join(get_prochaines_horaires(self.lines[_], self.stops[_]))
            for _ in range(len(self.lines))
        ]

        lines = [
            self.lines[_].split('-')[0] + ' : '
            for _ in range(len(self.lines))
        ]

        logger.debug(f"horaires: {horaires}")

        # Write the horaires on the image
        for _ in range(len(horaires)):
            if _ + 1 > max_lines:
                logger.error('Ran out of lines for this horaires :/')
                break
            write(
                im_colour,
                line_positions[_],
                (line_width, line_height),
                lines[_],
                font=self.font,
                alignment='left',
            )
            write(im_black, (int(self.font.getlength(lines[_])), line_positions[_][1]), (line_width, line_height),
                  horaires[_], font=self.font, alignment='left')

        # Return images for black and colour channels
        return im_black, im_colour