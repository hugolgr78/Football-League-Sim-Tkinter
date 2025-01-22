from PIL import Image

def change_all_pixels_to_black(image_path):
    try:
        image = Image.open(image_path)
        pixels = image.load()
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    for y in range(image.height):
        for x in range(image.width):
            if len(pixels[x, y]) == 4:
                pixels[x, y] = (0, 0, 0, pixels[x, y][3])  # Preserve alpha channel
            else:
                pixels[x, y] = (0, 0, 0)

    try:
        image.save("black_image.png")
        print("Image saved successfully as 'black_image.png'")
    except Exception as e:
        print(f"Error saving image: {e}")

# Example usage
image_path = ""
change_all_pixels_to_black(image_path)