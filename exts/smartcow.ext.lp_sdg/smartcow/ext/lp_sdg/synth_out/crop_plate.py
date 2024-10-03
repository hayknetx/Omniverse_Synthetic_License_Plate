import pandas as pd
import cv2
import os
import shutil

# Paths
csv_file = 'data/synth_veh_data_02-10-2024.csv'
image_folder = 'snapshots/'
output_folder = 'cropped_images/'
tsv_file = 'output_file.tsv'

# Read CSV
df = pd.read_csv(csv_file)

# Prepare output folder
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)

# Prepare TSV file
with open(tsv_file, 'w') as tsv:
    tsv.write('image_name\tplate_text\n')

    # Loop through each row in the DataFrame
    for index, row in df.iterrows():
        image_name = row['Image']  # Column name should match exactly
        plate_text = row['LP_Text']  # Column for plate text
        x1, y1, x2, y2 = int(row['x1']), int(row['y1']), int(row['x2']), int(row['y2'])

        # Load image
        image_path = os.path.join(image_folder, image_name)
        image = cv2.imread(image_path)

        # Check if image loaded correctly
        if image is not None:
            # Crop the image based on bounding box
            cropped_image = image[y1:y2, x1:x2]

            # Save the cropped image
            cropped_image_name = f"cropped_{index}.jpg"
            cropped_image_path = os.path.join(output_folder, cropped_image_name)
            cv2.imwrite(cropped_image_path, cropped_image)

            # Write to TSV file
            tsv.write(f"{cropped_image_name}\t{plate_text}\n")
        else:
            print(f"Failed to load {image_name}")
