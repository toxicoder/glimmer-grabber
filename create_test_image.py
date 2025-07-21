from PIL import Image, ImageDraw, ImageFont

# Create a blank white image
img = Image.new('RGB', (250, 100), color = (255, 255, 255))

# Get a drawing context
d = ImageDraw.Draw(img)

# Draw text on the image
try:
    # Use a larger, bold font
    font = ImageFont.truetype("arial.ttf", 40)
except IOError:
    font = ImageFont.load_default()
d.text((10,10), "Hello, World!", fill=(0,0,0), font=font)

# Save the image
img.save('processing_service/test_image.png')
