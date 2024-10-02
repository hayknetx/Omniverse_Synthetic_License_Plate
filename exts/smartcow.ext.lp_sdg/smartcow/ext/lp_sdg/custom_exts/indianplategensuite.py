import omni
from pxr import UsdShade, Sdf

import os
import re
import string
import random
import glob
import asyncio

import cv2

import numpy as np
import pandas as pd

from PIL import Image, ImageDraw, ImageFont


class IndianLicensePlateGenerator:
    """
    A tool suite for developing synthetic license plates for simulation.
    """

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
    RTO_SERIES = np.array(list(string.ascii_uppercase.replace("O", "").replace("I", "")))
    FILLERS = np.array([" ", "•", "-"])

    SPACERS_1 = np.array(["", " "])
    SPACERS_2 = np.array(["", " ", "  "])

    def __init__(self, working_dir, white_bg_mat, yellow_bg_mat, regions_path="regions.txt", seed=None):
        """Entrypoint for LP-SDG extension"""
        self.working_dir = str(working_dir)
        self.white_bg_mat = white_bg_mat
        self.yellow_bg_mat = yellow_bg_mat

        """
        regions: State/UT + District code for license plate
        >> Example: ['AN01', 'AN02', 'AP01', 'AP02']
        """

        if not os.path.exists(regions_path):
            regions_path = os.path.join(self.working_dir, regions_path)
        with open(str(regions_path)) as f:
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
        region_district = np.random.choice(self.REGIONS)
        rto_series = (
            "" if len(region_district) > 4 else "".join(np.random.choice(self.RTO_SERIES, np.random.randint(0, 4)))
        )

        numeric_part = "".join([str(x) for x in np.random.randint(0, 10, 4)])

        numeric_prefix = "" if len(rto_series) != 0 else "".join(np.random.choice(self.CAPITAL_LETTERS, 2))

        if multiline:
            spacing = np.random.choice(self.SPACERS_1, p=[0.2, 0.8])
            lp = f"{region_district} {rto_series}{spacing}{numeric_prefix}{spacing}{numeric_part}"
            return re.sub(" +", " ", lp), " "
        else:
            # add whitespaces to accomodate license plate area
            lp = region_district + rto_series + numeric_prefix + numeric_part
            if (not len(rto_series)) or (not len(numeric_prefix)) or (len(rto_series) + len(numeric_prefix) < 2):
                lp = f"{region_district[:2]} {region_district[2:]} {rto_series} {numeric_prefix} {numeric_part}"

            # remove redundant whitespaces and substitute with special characters
            assert filler_prob <= 0.5, "argument filler_prob should be <= 0.5"
            filler = np.random.choice(self.FILLERS, p=[1 - (2 * filler_prob), filler_prob, filler_prob])
            lp = re.sub(" +", ("" if len(region_district) >= 6 else filler), lp)
            return lp, filler

    def generate_normal_map(self, img, save_path, bluriness=1, sobel=0):
        """Uses Sobel and Gaussian Blur effects to generate a normal map from given image information"""
        zy, zx = np.gradient(img)

        if sobel:
            zx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=sobel)
            zy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=sobel)

        normal = np.dstack((-zx, -zy, np.ones_like(img)))
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
        """recursively load font file with decreasing font sizes to find an optimal size"""
        font = ImageFont.truetype(font_file, size=font_size)
        text_w, text_h = font.getsize("W" * (max_chars + 1))
        if (text_w > width) or (text_h > height):
            return self.load_font(width, height, font_file, font_size - 1, max_chars)
        return font

    def clear_font_cache(self):
        """Helps debug font cache"""
        self.FONT = {}

    async def generate_image(
        self,
        save_path,
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
        save_path: the path to save the generated images
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

        lp_type = np.random.choice(list(lp_types.keys()), p=list(lp_types.values()))
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
                max_chars=(padding - 4) if multiline else padding,
            )
        font = self.FONT[font_key]

        # generate multi line license plate text
        if multiline:
            lp, filler = self.generate_text(multiline=True)
            region, lp = lp.split(" ", 1) if " " in lp else (lp[:4], lp[4:])
            text_w, text_h = font.getsize(region)
            spacing = np.random.choice(self.SPACERS_2, p=[0.2, 0.7, 0.1])

            # draw first line
            draw.text(
                (width // 2, (height // 2) - (text_h // 2) - linespace // 2),
                f"{region[:2]}{spacing}{region[2:]}",
                align="center",
                fill=text_color,
                font=font,
                anchor="mm",
            )

            # draw second line
            draw.text(
                (width // 2, (height // 2) + (text_h // 2) + linespace // 2),
                lp,
                align="center",
                fill=text_color,
                font=font,
                anchor="mm",
            )

            lp = region + "+" + lp

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
            save_path,
            bluriness=bluriness,
            sobel=sobel,
        )
        normal_map = Image.fromarray(normal_map)

        # Save OG License Plate img
        src.save(save_path + "plate.png", "PNG")

        # Save generated normal map
        normal_map.save(save_path + "plate_normals.png", "PNG")

        # remove whitespaces from text
        lp = re.sub(filler + "+", "", lp)

        return lp, lp_type, (bg_color, text_color)

    def assign_texture(self, stage, object_path, material, save_path):
        """Creates and binds the generated LP material to the LP asset"""
        mtl_prim = stage.GetPrimAtPath(material)

        # Set material inputs, these can be determined by looking at the .mdl file
        # or by selecting the Shader attached to the Material in the stage window and looking at the details panel
        omni.usd.create_material_input(
            mtl_prim,
            "diffuse_texture",
            save_path + "plate.png",
            Sdf.ValueTypeNames.Asset,
        )

        omni.usd.create_material_input(
            mtl_prim,
            "normalmap_texture",
            save_path + "plate_normals.png",
            Sdf.ValueTypeNames.Asset,
        )

        # Get the path to the prim
        prim = stage.GetPrimAtPath(object_path)

        # Bind the material to the prim
        prim_mat_shade = UsdShade.Material(mtl_prim)

        UsdShade.MaterialBindingAPI(prim).Bind(prim_mat_shade, UsdShade.Tokens.strongerThanDescendants)

    def set_lp_bg(self, stage, object_path, material):
        """Binds selected LP material to the select LP object"""
        mtl_prim = stage.GetPrimAtPath(material)

        # Get the path to the prim
        prim = stage.GetPrimAtPath(object_path)

        # Bind the material to the prim
        prim_mat_shade = UsdShade.Material(mtl_prim)

        UsdShade.MaterialBindingAPI(prim).Bind(prim_mat_shade, UsdShade.Tokens.strongerThanDescendants)

    async def make_lp(
        self,
        stage,
        vehicle_path,
        im_width,
        im_height,
        save_path,
        lp_types,
        font_file,
        bluriness=0,
        sobel=0,
        padding=12,
        linespace=0,
        multiline=False,
        show_lp_text=True,
    ):
        """Creates and binds the license plate images to the correct regions"""

        print("Generating License Plates")

        lp_text, lp_type, (bg_color, text_color) = await asyncio.ensure_future(
            self.generate_image(
                save_path,
                width=im_width,
                height=im_height,
                font_file=font_file,
                lp_types=lp_types,
                bluriness=bluriness,
                sobel=sobel,
                padding=padding,
                linespace=linespace,
                multiline=multiline,
            )
        )

        print("License Plates Generated!")

        # Retrieval of vehicle and LP prims, bboxes
        lp_prim_f = vehicle_path + "/NumberPlateAsset_F/LP"
        bg_prim_f = vehicle_path + "/NumberPlateAsset_F/NumberPlate"

        lp_prim_r = vehicle_path + "/NumberPlateAsset_R/LP"
        bg_prim_r = vehicle_path + "/NumberPlateAsset_R/NumberPlate"

        # Shared Materials Scope with an OmniPBR material assigned to it
        pbr_path = vehicle_path + "/Shared_Materials/OmniPBR"

        # CONNECT PLATEGENERATOR TO TEXTURE!!!!
        self.assign_texture(
            stage,
            lp_prim_f,
            pbr_path,
            os.path.join(self.working_dir, save_path),
        )

        self.assign_texture(
            stage,
            lp_prim_r,
            pbr_path,
            os.path.join(self.working_dir, save_path),
        )

        # TODO: EXPAND THIS WITH THE OTHER 'IND' LP COLOURS!
        if lp_type == "private":
            self.set_lp_bg(stage, object_path=bg_prim_f, material=self.white_bg_mat)
            self.set_lp_bg(stage, object_path=bg_prim_r, material=self.white_bg_mat)
            # print("Setting white material as background")
        elif lp_type == "commercial":
            self.set_lp_bg(stage, object_path=bg_prim_f, material=self.yellow_bg_mat)
            self.set_lp_bg(stage, object_path=bg_prim_r, material=self.yellow_bg_mat)
            # print("Setting yellow material as background")

        if show_lp_text:
            print(f"License Plate Text: {lp_text}")

        return lp_text
