import pandas as pd
import cv2
import os
import shutil
from tqdm import tqdm
import random
import glob

# Paths
csv_data_files = sorted(glob.glob('data*/*.csv'))
output_folder = 'cropped_images/'
csv_output_file = 'output_file.csv'

# Read CSV


# Prepare output folder
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)
# Prepare TSV file
with open(csv_output_file, 'w') as csv:
    # Loop through each row in the DataFrame
    for csv_data_file in csv_data_files[:1]:
        image_folder = os.path.dirname(csv_data_file).replace("data", "snapshots")
        df = pd.read_csv(csv_data_file)
        for index, row in tqdm(df.iterrows(), total=len(df)):
            image_name = row['Image']  # Column name should match exactly
            plate_text = row['LP_Text']  # Column for plate text
            x1, y1, x2, y2 = int(row['x1']), int(row['y1']), int(row['x2']), int(row['y2'])
            x1 -= random.randint(8, 10)
            y1 -= random.randint(8, 10)
            x2 += random.randint(8, 10)
            y2 += random.randint(8, 10)
            # Load image
            image_path = os.path.join(image_folder, image_name)
            image = cv2.imread(image_path)

            # Check if image loaded correctly
            if image is not None:
                # Crop the image based on bounding box
                cropped_image = image[y1:y2, x1:x2]

                # Save the cropped image
                cropped_image_name = f"cropped_{image_folder}_{image_name}"
                cropped_image_path = os.path.join(output_folder, cropped_image_name)
                cv2.imwrite(cropped_image_path, cropped_image)

                # Write to TSV file
                csv.write(f"{cropped_image_name},{plate_text}\n")
            else:
                print(f"Failed to load {image_name}")
