# Quick-Start Guide

In order to use this extension, all you need to do is unzip the file provided and load it into Omniverse via the Extension Manager. Should the installation be successful, you will be able to enable the 'LP-SDG' extension and the UI will appear in your scene. Thank you for using our extension!

## Packages Note

Omniverse typically handles python package installation on its own, however, on occasion it has been observed that the system will throw out an error that **opencv-python** cannot be found on the system. 

In that case, it is advisable to install it using the command:

`omni.kit.pipapi.install("opencv-python")`

If that still fails, you may try to create a virtual environment and install the package via

`pip install opencv-python`

This should address the issue and create all necessary files in order for an installation of **open-cv** compatible with Omniverse to work.

# Getting Started

One thing to note with this extension is that in V1.0 it is currently only compatible with the format provided in the example lightweight USD scene which can be loaded from the path:

`/smartcow/ext/lp_sdg/usd_scene`

Should everything be set up well, the UI will natively interact with the scene and you may begin utilizing all the components found within LP-SDG.

## Generating your Synthetic Data

If you would like to get started with generating synthetic data, all you need to do is click the 'Generate Synthetic Data' button in the UI panel and you will find the output in the path:

`/smartcow/ext/lp_sdg/synth_out`

Here, you will have the generated .csv files and the images in the `data` and `snapshots` folders respectively. Load them into the Machine Learning framework of your choice and you can start training right away! Happy Modelling!

## Customization

Should you want to capture single screenshots with finer-granularity control, you may use the "Vehicle Settings" menu to change license plates to the desired framework with the exact required level of scratches, dirt, etc., and capture a singular screenshot of all these adjusted settings.