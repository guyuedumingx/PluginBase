from PIL import Image


def convert_png_to_ico(png_path, ico_path, icon_size=(32, 32)):
    # Open PNG image using Pillow
    img = Image.open(png_path)

    # Resize image to the desired icon size
    # img = img.resize(icon_size, Image.ANTIALIAS)

    # Save as ICO
    img.save(ico_path, format="ICO", sizes=[(x, x) for x in [16, 32, 48]])


# Example usage
convert_png_to_ico('assets/icons/BOC.png', 'assets/icons/icon.ico')
