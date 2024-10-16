import omni
from pxr import UsdShade, Sdf, UsdGeom, Gf

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
        "arm": [(190, 190, 190), (0, 0, 0)],  # background, foreground
        "arm_height": [(223, 226, 230), (0, 0, 0)],
        "arm_mil": [(0, 0, 0), (255, 255, 255)],
    }

    CAPITAL_LETTERS = np.array(list(string.ascii_uppercase))
    RTO_SERIES = np.array(list(string.ascii_uppercase.replace("O", "").replace("I", "")))
    FILLERS = np.array([" ", "•", "-"])

    SPACERS_1 = np.array(["", " "])
    SPACERS_2 = np.array(["", " ", "  "])

    def __init__(self, working_dir, arm_bg_material, arm_mil_bg_material, arm_height_bg_material, text_width, regions_path="regions.txt",
                 seed=None):
        """Entrypoint for LP-SDG extension"""
        self.working_dir = str(working_dir)
        self.arm_bg_material = arm_bg_material
        self.arm_mil_bg_material = arm_mil_bg_material
        self.arm_height_bg_material = arm_height_bg_material
        self.Vehicle_paths = []
        self.font_size_upscale = text_width // 100

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
        self.plate_image_names = []

        # seed random generators
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_text(self, lp_type, multiline=False):
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
        lp = ""
        if lp_type == "arm":
            first_part = "".join(np.random.choice(range(10), 2).astype(str))
            middle_part = "".join(np.random.choice(self.CAPITAL_LETTERS, 2))
            last_part = "".join(np.random.choice(range(10), 3).astype(str))
            lp = np.random.choice(
                [first_part + " " + middle_part + " " + last_part,
                 last_part + " " + middle_part + " " + first_part])
        elif lp_type == "arm_height":
            first_part = "".join(np.random.choice(range(10), 2).astype(str))
            middle_part = "".join(np.random.choice(self.CAPITAL_LETTERS, 2))
            last_part = "".join(np.random.choice(range(10), 3).astype(str))
            lp = np.random.choice(
                [first_part + " " + middle_part + " " + last_part,
                 last_part + " " + middle_part + " " + first_part])
        elif lp_type == "arm_mil":
            first_part = "ՊՆ"
            middle_part = "".join(np.random.choice(range(10), 4).astype(str))
            last_part = "".join(np.random.choice(["Տ", "Մ", "Շ"]))
            lp = first_part + middle_part + " " + last_part
        return lp

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
        # text_w, text_h = font.getsize("W" * (max_chars + 1))
        # if (text_w > width) or (text_h > height):
        #     return self.load_font(width, height, font_file, font_size - 1, max_chars)
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
            lp_types={"arm": 0.4, "arm_mil": 0.4, "arm_height": 0.2},
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
        if lp_type == "arm_height":
            width = 300
            height = 600
        src = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(src)
        if lp_type == "arm" or lp_type == "arm_height":
            font_file = "/usr/share/fonts/truetype/fe/FE.TTF"
        elif lp_type == "arm_mil":
            font_file = "/usr/share/fonts/truetype/arm/Nicolo-Regular.otf"
        # cache font to avoid time consuming operation i.e., font size calculation
        font_key = f"{font_file}_{width}_{height}_{padding}_{linespace}_{multiline}"
        if not font_key in self.FONT:
            custom_font_size = 20 * self.font_size_upscale
            custom_max_chars = 7
            if lp_type == "arm":
                custom_font_size = 18 * self.font_size_upscale
                custom_max_chars = 7
            if lp_type == "arm_height":
                custom_font_size = 15 * self.font_size_upscale
                custom_max_chars = 7
            elif lp_type == "arm_mil":
                custom_font_size = 20 * self.font_size_upscale
                custom_max_chars = 7
            self.FONT[font_key] = self.load_font(
                width,
                height,
                font_file,
                font_size=custom_font_size,
                max_chars=custom_max_chars,
            )
        font_regular = self.FONT[font_key]

        if lp_type == "arm_mil":
            lp = self.generate_text(lp_type)
            # Load fonts with different styles and sizes
            font_bold_small = self.load_font(
                width,
                height,
                font_file,
                font_size=16 * self.font_size_upscale,
                max_chars=2,
            )
            font_bold_large = self.load_font(
                width,
                height,
                font_file,
                font_size=20 * self.font_size_upscale,
                max_chars=4,
            )

            # Generate text parts
            lp_pn = "ՊՆ"
            lp_front_part, lp_last_part = lp.split()
            lp_numbers = lp_front_part.replace(lp_pn, "") + " "

            # Measure text widths
            bbox = font_bold_small.getbbox(lp_pn)
            lp_pn_width, lp_pn_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            bbox = font_bold_large.getbbox(lp_numbers)
            lp_numbers_width, lp_numbers_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            bbox = font_regular.getbbox(lp_last_part)
            lp_last_part_width, lp_last_part_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            total_width = lp_pn_width + lp_numbers_width + lp_last_part_width

            # Set the baseline position (y-coordinate will be the same for all parts)
            baseline_y = height // 2 + max(lp_pn_height, lp_numbers_height, lp_last_part_height) // 2

            # Calculate starting x position to center the text
            x_start = (width - total_width) // 2

            # Draw lp_pn, aligned to the baseline
            draw.text(
                (x_start, baseline_y),
                lp_pn,
                align="left",
                fill=text_color,
                font=font_bold_small,
                anchor="ls",  # Use "ls" anchor to align text on the baseline
            )

            # Update x position for the next part
            x_start += lp_pn_width

            # Draw lp_numbers, aligned to the baseline
            draw.text(
                (x_start, baseline_y),
                lp_numbers,
                align="left",
                fill=text_color,
                font=font_bold_large,
                anchor="ls",
            )

            # Update x position for the last part
            x_start += lp_numbers_width

            # Draw lp_last_part, aligned to the baseline
            draw.text(
                (x_start, baseline_y),
                lp_last_part,
                align="left",
                fill=text_color,
                font=font_regular,
                anchor="ls",
            )
        elif lp_type == "arm_height":
            lp = self.generate_text(lp_type)
            first_part, last_part = " ".join(lp.split()[:-1]), lp.split()[-1]

            # Get bounding box for the first and last part
            first_part_bbox = font_regular.getbbox(first_part)
            last_part_bbox = font_regular.getbbox(last_part)

            # Calculate the height for each part
            first_part_height = first_part_bbox[3] - first_part_bbox[1]
            last_part_height = last_part_bbox[3] - last_part_bbox[1]

            # Draw the first part in the center of the first line
            line_spacing = 10
            top_margin = 65
            total_height = first_part_height + last_part_height + line_spacing - top_margin

            # Draw the first part
            draw.text(
                (width // 2, height // 2 - total_height // 2),  # Position above center
                first_part,
                align="center",
                fill=text_color,
                font=font_regular,
                anchor="mm",
            )

            # Draw the last part with line spacing applied
            draw.text(
                (width // 2, height // 2 - total_height // 2 + first_part_height + line_spacing),
                # Position below first part
                last_part,
                align="center",
                fill=text_color,
                font=font_regular,
                anchor="mm",
            )

        else:
            # generate single line license plate text
            lp = self.generate_text(lp_type)
            draw.text(
                (width // 2, height // 2),
                lp,
                align="center",
                fill=text_color,
                font=font_regular,
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

    def set_size_position(self, stage, object_path, scale, position):
        prim = stage.GetPrimAtPath(object_path)
        if prim.IsA(UsdGeom.Xformable):
            xformable = UsdGeom.Xformable(prim)

            # Find the existing scale operation, or create it if it doesn't exist
            scale_ops = xformable.GetOrderedXformOps()
            scale_op = None
            for op in scale_ops:
                if op.GetOpType() == UsdGeom.XformOp.TypeScale:
                    scale_op = op
                    break
            if scale_op is None:
                scale_op = xformable.AddScaleOp()

            # Set the scale value
            scale_value = Gf.Vec3f(*scale)  # Modify the scale values as needed
            scale_op.Set(scale_value)

            # Find the existing translate operation, or create it if it doesn't exist
            translate_op = None
            for op in scale_ops:
                if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                    translate_op = op
                    break
            if translate_op is None:
                translate_op = xformable.AddTranslateOp()

            translation_value = Gf.Vec3f(*position)
            translate_op.Set(translation_value)

    def remove_dirt(self, stage, object_path):
        prim = stage.GetPrimAtPath(object_path)
        if prim and prim.IsValid():
            prim.GetStage().RemovePrim(object_path)

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
            image_name,
            bluriness=0,
            sobel=0,
            padding=12,
            linespace=0,
            multiline=False,
            show_lp_text=True,
    ):
        """Creates and binds the license plate images to the correct regions"""

        # print("Generating License Plates")
        image_name = "image" + str(int(image_name.split('.')[0]) % 10) + "_"
        save_path = os.path.join(os.path.dirname(save_path), image_name + os.path.basename(save_path))
        if image_name not in self.plate_image_names:
            if len(self.plate_image_names) == 5:
                del_image_name = self.plate_image_names[0]
                for i in range(len(self.Vehicle_paths)):
                    del_image_path = os.path.join(os.path.dirname(save_path), del_image_name + str(i)) + "_"
                    os.remove(del_image_path + "plate.png")
                    os.remove(del_image_path + "plate_normals.png")
                del self.plate_image_names[0]
            self.plate_image_names.append(image_name)
        lp_text, lp_type, (bg_color, text_color) = await self.generate_image(
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

        # print("License Plates Generated!")

        # Retrieval of vehicle and LP prims, bboxes
        lp_prim_f = vehicle_path + "/NumberPlateAsset_F/LP"
        bg_prim_f = vehicle_path + "/NumberPlateAsset_F/NumberPlate"
        holder_prim_f = vehicle_path + "/NumberPlateAsset_F/LP_Holder/LP_Holder_Long"
        scratches_prim_f = vehicle_path + "/NumberPlateAsset_F/Damage_Scratches"

        lp_prim_r = vehicle_path + "/NumberPlateAsset_R/LP"
        bg_prim_r = vehicle_path + "/NumberPlateAsset_R/NumberPlate"
        holder_prim_r = vehicle_path + "/NumberPlateAsset_R/LP_Holder/LP_Holder_Long"
        scratches_prim_r = vehicle_path + "/NumberPlateAsset_R/Damage_Scratches"

        plate_dirt_f_path = vehicle_path + "/NumberPlateAsset_F/Damage_Dirt"
        plate_dirt_r_path = vehicle_path + "/NumberPlateAsset_R/Damage_Dirt"

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

        if lp_type == "arm_mil":
            position_bg = (0, 2.69, 0)
            scale_bg = (10.96, 2.85, 2.7)
            position_lp = (0.05, 2.7, 0.001)
            scale_lp = (10.74, 2.5, 2.7)
            position_holder = (-5.1, 2.72, 1.35)
            scale_holder = (1, 3.1, 0.146)
            position_scratch = (0, 2.7, 0.005)
            scale_scratch = (10.96, 2.7, 2.7)
            material = self.arm_mil_bg_material
        elif lp_type == "arm_height":
            position_bg = (0, 2.6, 0.146)
            scale_bg = (8, 3.96, 2.54)
            position_lp = (1.04, 2.67, 0.07)
            scale_lp = (5.3, 3.52, 2.7)
            position_holder = (-3.8, 2.57, 1.5)
            scale_holder = (0.73, 5.1, 0.14)
            position_scratch = (0, 2.63, 0.015)
            scale_scratch = (7.26, 2.85, 2.7)
            material = self.arm_height_bg_material
        else:
            position_bg = (0, 2.69, 0)
            scale_bg = (10.96, 2.85, 2.7)
            position_lp = (0.9, 2.8, 0.001)
            scale_lp = (8.9, 2.2, 2.7)
            position_holder = (-5.1, 2.72, 1.35)
            scale_holder = (1, 3.1, 0.146)
            position_scratch = (0, 2.7, 0.005)
            scale_scratch = (10.96, 2.7, 2.7)
            material = self.arm_bg_material
        self.set_size_position(stage, object_path=bg_prim_f, scale=scale_bg, position=position_bg)
        self.set_size_position(stage, object_path=bg_prim_r, scale=scale_bg, position=position_bg)
        self.set_lp_bg(stage, object_path=bg_prim_f, material=material)
        self.set_lp_bg(stage, object_path=bg_prim_r, material=material)
        self.set_size_position(stage, object_path=lp_prim_f, scale=scale_lp, position=position_lp)
        self.set_size_position(stage, object_path=lp_prim_r, scale=scale_lp, position=position_lp)
        self.set_size_position(stage, object_path=holder_prim_f, scale=scale_holder, position=position_holder)
        self.set_size_position(stage, object_path=holder_prim_r, scale=scale_holder, position=position_holder)
        self.set_size_position(stage, object_path=scratches_prim_f, scale=scale_scratch, position=position_scratch)
        self.set_size_position(stage, object_path=scratches_prim_r, scale=scale_scratch, position=position_scratch)
        if vehicle_path not in self.Vehicle_paths:
            self.remove_dirt(stage, plate_dirt_f_path)
            self.remove_dirt(stage, plate_dirt_r_path)
            self.Vehicle_paths.append(vehicle_path)

        # if show_lp_text:
        #     print(f"License Plate Text: {lp_text}")

        return lp_text
