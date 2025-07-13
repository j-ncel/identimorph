import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def get_hash_bytes(seed: str) -> np.ndarray:
    return np.frombuffer(hashlib.sha256(seed.encode()).digest(), dtype=np.uint8)


def create_identimorph_grid(hash_bytes: np.ndarray, blocks: int) -> np.ndarray:
    half_width = blocks // 2 + 1
    grid_half = (hash_bytes[:blocks * half_width] %
                 2).reshape((blocks, half_width))
    mirror = grid_half[:, :-1][:, ::-1] if blocks % 2 else grid_half[:, ::-1]
    return np.hstack((grid_half, mirror))


def draw_active_blocks(base_img, grid: np.ndarray, block_size: int, hash_bytes: np.ndarray, glow: int) -> Image.Image:
    for y, x in np.argwhere(grid):
        color = tuple(hash_bytes[(x + y) % 32:(x + y) % 32 + 3])
        block_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(block_img)

        x0 = int(x * block_size)
        y0 = int(y * block_size)
        x1 = int((x + 1) * block_size)
        y1 = int((y + 1) * block_size)
        coords = [x0, y0, x1, y1]

        draw.rectangle(coords, fill=color + (255,))

        if glow > 0:
            glow_img = block_img.filter(ImageFilter.GaussianBlur(glow))
            base_img = Image.alpha_composite(
                base_img.convert("RGBA"), glow_img)

        base_img.paste(block_img.convert("RGB"), (0, 0), block_img)

    return base_img


def generate_identimorph_frame(seed: str, size: int = 96, blocks: int = 5, glow: int = 0) -> Image.Image:
    hash_bytes = get_hash_bytes(seed)
    block_size = size / blocks
    base_img = Image.new("RGB", (size, size), (240, 240, 240))
    grid = create_identimorph_grid(hash_bytes, blocks)
    return draw_active_blocks(base_img, grid, block_size, hash_bytes, glow)


def identimorph(text: str = "github.com/j-ncel", frames: int = 12, size: int = 128, glow: int = 0, fps: int = 1, output_path="identimorph.gif"):
    frame_duration = int(1000 / fps)

    frames_list = [
        generate_identimorph_frame(f"{text}_{i}", size=size, glow=glow)
        for i in range(frames)
    ]

    frames_list[0].save(
        output_path,
        save_all=True,
        append_images=frames_list[1:],
        duration=frame_duration,
        loop=0
    )
    print(f"You identimorph was saved as {output_path}")
