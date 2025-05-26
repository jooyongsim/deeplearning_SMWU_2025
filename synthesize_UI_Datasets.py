import os
import requests
from PIL import Image, ImageDraw, UnidentifiedImageError
from io import BytesIO
import random

# Define directories
os.makedirs('datasets', exist_ok=True)
images_path = 'datasets/icon/images/train'
labels_path = 'datasets/icon/labels/train'
os.makedirs(images_path, exist_ok=True)
os.makedirs(labels_path, exist_ok=True)

# Verified list of public icon URLs
icons_base_url = "https://img.icons8.com/color/96/000000/"
icon_names = [
    "home--v1", "settings--v1", "search--v1", "user-male-circle--v1", "calendar--v1", "camera--v1", "phone--v1", "lock--v1", "cloud--v1",
    "facebook", "twitter", "instagram", "linkedin", "whatsapp", "youtube", "github", "google-logo", "dropbox", "spotify",
    "paypal", "visa", "mastercard", "bitcoin", "alarm", "windows-10", "android-os", "ubuntu", "linux",
    "trash", "download", "upload", "edit", "copy", "paste", "print", "refresh", "save",
    "bookmark", "shopping-cart", "tag", "star", "bell", "document", "briefcase", "key", "map",
    "clock", "gift", "graph", "chat", "network", "shield", "lightning-bolt", "rocket",
    "puzzle", "trophy", "globe", "flag", "compass", "paper-plane", "thumbs-down", "play", "pause",
    "stop", "rewind", "forward", "microphone", "headphones", "speaker", "video",
    "music", "film-reel", "paint-palette", "scissors", "hammer", "wrench", "gear", "car", "bus",
    "train", "bicycle", "motorcycle", "flower", "sun", "moon", "snowflake"
]
icons = [f"{icons_base_url}{name}.png" for name in icon_names]

# Cache downloaded icons to avoid repeated requests
icon_cache = {}

def download_icon(url):
    if url not in icon_cache:
        response = requests.get(url)
        try:
            icon_cache[url] = Image.open(BytesIO(response.content)).convert("RGBA")
        except UnidentifiedImageError:
            print(f"Failed to load image from URL: {url}")
            icon_cache[url] = None
    return icon_cache[url]

def is_overlapping(box1, box2):
    return not (box1[2] <= box2[0] or box1[0] >= box2[2] or box1[3] <= box2[1] or box1[1] >= box2[3])

def generate_synthetic_image(img_idx):
    panel_width, panel_height = 800, 470
    panel_color = tuple(random.randint(150, 255) for _ in range(3))
    panel = Image.new("RGB", (panel_width, panel_height), panel_color)
    draw = ImageDraw.Draw(panel)

    num_panels = random.randint(3, 10)
    annotations = []
    existing_boxes = []

    attempts = 0
    while len(existing_boxes) < num_panels and attempts < 50:
        arrange_vertical = random.choice([True, False])
        num_icons = random.randint(2, 6)
        icon_spacing = 10
        icon_size = random.randint(40, 60)

        if arrange_vertical:
            panel_w = icon_size + 20
            panel_h = num_icons * icon_size + (num_icons - 1) * icon_spacing + 20
        else:
            panel_w = num_icons * icon_size + (num_icons - 1) * icon_spacing + 20
            panel_h = icon_size + 20

        panel_x = random.randint(0, panel_width - panel_w)
        panel_y = random.randint(0, panel_height - panel_h)
        panel_box = [panel_x, panel_y, panel_x + panel_w, panel_y + panel_h]

        if any(is_overlapping(panel_box, eb) for eb in existing_boxes):
            attempts += 1
            continue

        existing_boxes.append(panel_box)
        panel_color_inner = tuple(random.randint(100, 200) for _ in range(3))
        draw.rectangle(panel_box, fill=panel_color_inner)

        x_center = (panel_x + panel_w / 2) / panel_width
        y_center = (panel_y + panel_h / 2) / panel_height
        width = panel_w / panel_width
        height = panel_h / panel_height
        annotations.append(f"1 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        for i in range(num_icons):
            icon_url = random.choice(icons)
            icon = download_icon(icon_url)

            if icon is None:
                continue

            icon_resized = icon.resize((icon_size, icon_size))

            if arrange_vertical:
                icon_x = panel_x + (panel_w - icon_size) // 2
                icon_y = panel_y + 10 + i * (icon_size + icon_spacing)
            else:
                icon_x = panel_x + 10 + i * (icon_size + icon_spacing)
                icon_y = panel_y + (panel_h - icon_size) // 2

            panel.paste(icon_resized, (icon_x, icon_y), icon_resized)

            x_center_icon = (icon_x + icon_size / 2) / panel_width
            y_center_icon = (icon_y + icon_size / 2) / panel_height
            width_icon = icon_size / panel_width
            height_icon = icon_size / panel_height
            annotations.append(f"0 {x_center_icon:.6f} {y_center_icon:.6f} {width_icon:.6f} {height_icon:.6f}")

        attempts += 1

    img_path = os.path.join(images_path,f'synthetic_{img_idx}.png')
    panel.save(img_path)

    annotation_path = os.path.join(labels_path,f'synthetic_{img_idx}.txt')
    with open(annotation_path, 'w') as f:
        for annotation in annotations:
            f.write(annotation + "\n")

for i in range(100):
    generate_synthetic_image(i)

print("Synthetic UI dataset generated with non-overlapping panels and aligned icons!")