import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# Load the CSV
csv_file = 'input.csv'
df = pd.read_csv(csv_file)

# Path to the certificate template
certificate_template = 'template.png'

# Font path (You can use a default system font or load your own)
font_path = 'arial.ttf' 
font_size = 40  # Adjust the font size based on your template

# Create a new column to store PDF file paths
df['pdf_file'] = ''

# Loop through each name and email in the CSV
for index, row in df.iterrows():
    name = row['fullname']
    email = row['user_email']
    
    # Open the certificate template
    img = Image.open(certificate_template)
    draw = ImageDraw.Draw(img)

    # Load the font
    font = ImageFont.truetype(font_path, font_size)

    # Calculate the text position using textbbox (returns bounding box of the text)
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    img_width, img_height = img.size
    position = ((img_width - text_width) / 2, (img_height - text_height) / 2)

    # Overlay the name on the certificate template
    draw.text(position, name, font=font, fill="white")

    # Save the image directly as a PDF
    pdf_file_path = f'certs/{email}.pdf'
    img.save(pdf_file_path, "PDF", resolution=100.0)

    # Add the PDF file path to the dataframe
    df.at[index, 'pdf_file'] = pdf_file_path

# Save the updated CSV
df.to_csv('output.csv', index=False)
