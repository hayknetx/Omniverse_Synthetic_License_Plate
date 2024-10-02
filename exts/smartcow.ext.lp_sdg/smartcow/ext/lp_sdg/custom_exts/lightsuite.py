import omni
import asyncio
from pxr import UsdLux


class LightSuite:
    """
    A set of tools designed to manipulate lights, intensity, and finer aspects thereof.
    """

    def create_light(
        self,
        primName,
        primType="DistantLight",
        angle=1.0,
        intensity=3000,
        height=1.0,
        length=1.0,
        color=(1.0, 1.0, 1.0),
        enableColorTemp=False,
        colorTemp=6500.0,
        diffuse=1.0,
        specular=1.0,
    ):

        # Light Reference: https://docs.omniverse.nvidia.com/py/kit/docs/api/pxr.html?highlight=physics
        # Adjustable parameters via command call
        omni.kit.commands.execute(
            "CreatePrim",
            prim_path="{}/defaultLight".format(primName),
            prim_type=primType,
            select_new_prim=False,
            attributes={
                UsdLux.Tokens.angle: angle,
                UsdLux.Tokens.intensity: intensity,
                UsdLux.Tokens.height: height,
                UsdLux.Tokens.length: length,
                UsdLux.Tokens.color: color,
                UsdLux.Tokens.enableColorTemperature: enableColorTemp,
                UsdLux.Tokens.colorTemperature: colorTemp,
                UsdLux.Tokens.diffuse: diffuse,
                UsdLux.Tokens.specular: specular
            },
        )

