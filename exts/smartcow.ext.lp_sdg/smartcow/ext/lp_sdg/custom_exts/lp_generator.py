from PIL import Image, ImageDraw, ImageFont
from numpy.random import choice as np_random_choice
from numpy.random import randint as np_random_int
import numpy as np
import string
import random
import cv2
import re
import os


class IndianLicensePlateGenerator:
    # https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_India
    COLOR_COMBINATIONS = {
        "private": [(255, 255, 255), (0, 0, 0)],  # background, foreground
        "private_electric": [(0, 128, 0), (255, 255, 255)],
        "commercial": [(249, 190, 25), (0, 0, 0)],
        "commercial_rent": [(0, 0, 0), (249, 190, 25)],
        "commercial_electric": [(0, 128, 0), (249, 190, 25)],
        "external_affairs": [(100, 180, 245), (255, 255, 255)],
        "armed_forces": [(0, 0, 0), (255, 255, 255)],
        "unsold": [(255, 0, 0), (255, 255, 255)],
        "awaiting": [(249, 190, 25), (255, 0, 0)],
    }

    CAPITAL_LETTERS = np.array(list(string.ascii_uppercase))
    RTO_SERIES = np.array(
        list(string.ascii_uppercase.replace("O", "").replace("I", ""))
    )
    FILLERS = np.array([" ", "•", "-"])
    
    SPACERS_1 = np.array(["", " "])
    SPACERS_2 = np.array(["", " ", "  "])

    def __init__(self, regions_path="regions.txt", seed=None):
        """
        regions: State/UT + District code for license plate
        >> Example: ['AN01', 'AN02', 'AP01', 'AP02']
        """
        if not os.path.exists(regions_path):
            regions_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), regions_path
            )
        with open(regions_path) as f:
            self.REGIONS = np.array(f.read().strip().split("\n"))
        assert len(self.REGIONS), "Regions cannot be empty"

        self.FONT = {}

        # seed random generators
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_text(self, filler_prob=0.1, multiline=False):
        """
        https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_India
        License Plate Format For Indian region consits of 4 parts
        - The first two letters indicate the State or Union Territory to which the vehicle is registered.
        - The next two digit numbers are the sequential number of a district. Due to heavy volume of vehicle registration.
        - The third part consists of one, two or three letters or no letters at all. This shows the ongoing series of an RTO (Also as a counter of the number of vehicles registered) and/or vehicle classification.
          - Letters such as O and I are not used in RTO series in order to avoid confusion with digits 0 or 1.
        - The fourth part is a number from 1 to 9999, unique to each plate. A letter is prefixed when the 4 digit number runs out and then two letters and so on.
        """

        # randomly choose options for each of the parts
        region_district = np_random_choice(self.REGIONS)
        rto_series = (
            ""
            if len(region_district) > 4
            else "".join(np_random_choice(self.RTO_SERIES, np_random_int(0, 4)))
        )
        
        numeric_part = "".join([str(x) for x in np_random_int(0, 10, 4)])
        
        numeric_prefix = (
            ""
            if len(rto_series) != 0
            else "".join(np_random_choice(self.CAPITAL_LETTERS, 2))
        )

        if multiline:
            spacing = np_random_choice(self.SPACERS_1, p=[0.2, 0.8])
            lp = f"{region_district} {rto_series}{spacing}{numeric_prefix}{spacing}{numeric_part}"
            return re.sub(" +", " ", lp), " "
        else:
            # add whitespaces to accomodate license plate area
            lp = region_district + rto_series + numeric_prefix + numeric_part
            if (
                (not len(rto_series))
                or (not len(numeric_prefix))
                or (len(rto_series) + len(numeric_prefix) < 2)
            ):
                lp = f"{region_district[:2]} {region_district[2:]} {rto_series} {numeric_prefix} {numeric_part}"

            # remove redundant whitespaces and substitute with special characters
            assert filler_prob <= 0.5, "argument filler_prob should be <= 0.5"
            filler = np_random_choice(
                self.FILLERS, p=[1 - (2 * filler_prob), filler_prob, filler_prob]
            )
            lp = re.sub(" +", ("" if len(region_district) >= 6 else filler), lp)
            return lp, filler

    def generate_normal_map(self, gray_image, bluriness=0, sobel=0):
        # https://github.com/weixk2015/DeepSFM/blob/master/convert.py
        zy, zx = np.gradient(gray_image)

        if sobel:
            zx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=sobel)
            zy = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=sobel)

        normal = np.dstack((-zx, -zy, np.ones_like(gray_image)))
        n = np.linalg.norm(normal, axis=2)
        normal[:, :, 0] /= n
        normal[:, :, 1] /= n
        normal[:, :, 2] /= n
        normal += 1
        normal /= 2
        normal *= 255

        if bluriness:
            normal = cv2.GaussianBlur(normal, (bluriness, bluriness), 0)

        return normal.astype(np.uint8)

    def load_font(self, width, height, font_file, font_size, max_chars):
        # recursively load font file with decreasing font sizes to find an optimal size
        font = ImageFont.truetype(font_file, size=font_size)
        text_w, text_h = font.getsize("W" * (max_chars + 1))
        if (text_w > width) or (text_h > height):
            return self.load_font(width, height, font_file, font_size - 1, max_chars)
        return font

    def clear_font_cache(self):
        # useful for debugging
        self.FONT = {}

    def generate_image(
        self,
        width=675,
        height=170,
        font_file="CharlesWright-Bold.ttf",
        lp_types={"private": 0.5, "commercial": 0.5},
        bluriness=0,
        sobel=0,
        padding=12,
        linespace=0,
        multiline=False,
    ):
        """
        width: generated license plate width
        height: generated license plate height
        font_file: path to font file on disk
        lp_types: license plate types and their probability distributions
        bluriness: gaussian blur kernel size for normal maps
        sobel: sobel filter kernel size for normal maps
        padding: maximum text length in a line to calculate font_size, padding and font_size are inversly related
        linespace: Add vertical spacing between multiline texts
        """
        
        # standard dimension for 4 wheeler license plate
        # width = 675, height = 170
        
        # standard dimension for 2 wheeler license plate
        # width = 575, height = 270

        lp_type = np_random_choice(list(lp_types.keys()), p=list(lp_types.values()))
        bg_color, text_color = self.COLOR_COMBINATIONS[lp_type]

        # create a blank canvas and drawing object
        src = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(src)

        # cache font to avoid time consuming operation i.e., font size calculation
        font_key = f"{font_file}_{width}_{height}_{padding}_{linespace}_{multiline}"
        if not font_key in self.FONT:
            self.FONT[font_key] = self.load_font(
                width,
                height,
                font_file,
                font_size=max(width, height),
                max_chars=(padding-4) if multiline else padding,
            )
        font = self.FONT[font_key]

        # generate multi line license plate text
        if multiline:
            lp, filler = self.generate_text(multiline=True)
            region, lp = lp.split(" ", 1) if " " in lp else (lp[:4], lp[4:])
            text_w, text_h = font.getsize(region)
            spacing = np_random_choice(self.SPACERS_2, p=[0.2, 0.7, 0.1])

            # draw first line
            draw.text(
                (width // 2, (height // 2) - (text_h // 2) - linespace//2),
                f"{region[:2]}{spacing}{region[2:]}",
                align="center",
                fill=text_color,
                font=font,
                anchor="mm",
            )
            
            # draw second line
            draw.text(
                (width // 2, (height // 2) + (text_h // 2) + linespace//2),
                lp,
                align="center",
                fill=text_color,
                font=font,
                anchor="mm",
            )
            
            lp = region+"+"+lp

        else:
            # generate single line license plate text
            lp, filler = self.generate_text(filler_prob=0.1)
            draw.text(
                (width // 2, height // 2),
                lp,
                align="center",
                fill=text_color,
                font=font,
                anchor="mm",
            )
            
        # generate normal map
        normal_map = self.generate_normal_map(
            cv2.cvtColor(np.array(src), cv2.COLOR_RGB2GRAY),
            bluriness=bluriness,
            sobel=sobel,
        )
        normal_map = Image.fromarray(normal_map)
        
        # remove whitespaces from text
        lp = re.sub(filler + "+", "", lp)

        return lp, src, normal_map, lp_type, (bg_color, text_color)