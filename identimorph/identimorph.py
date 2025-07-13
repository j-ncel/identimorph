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


# Classic hash-varying frames: A_0, A_1, ...
def draw_active_blocks(base_img, grid: np.ndarray, block_size: int, hash_bytes: np.ndarray, glow: int) -> Image.Image:
    for y, x in np.argwhere(grid):
        color = tuple(hash_bytes[(x + y) % 32:(x + y) % 32 + 3])
        block_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(block_img)

        x0 = int(x * block_size)
        y0 = int(y * block_size)
        x1 = int((x + 1) * block_size)
        y1 = int((y + 1) * block_size)
        draw.rectangle([x0, y0, x1, y1], fill=color + (255,))

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
    print(f"✅ Classic identimorph saved as: {output_path}")


# Spiral mode functions
def get_spiral_order(shape):
    h, w = shape
    spiral = []
    top, left = 0, 0
    bottom, right = h - 1, w - 1

    while top <= bottom and left <= right:
        # Right
        for x in range(left, right + 1):
            spiral.append((top, x))
        top += 1

        # Down
        for y in range(top, bottom + 1):
            spiral.append((y, right))
        right -= 1

        # Left
        if top <= bottom:
            for x in range(right, left - 1, -1):
                spiral.append((bottom, x))
            bottom -= 1

        # Up
        if left <= right:
            for y in range(bottom, top - 1, -1):
                spiral.append((y, left))
            left += 1

    return spiral


def draw_spiral_blocks(grid, hash_bytes, block_size, glow, step_limit) -> Image.Image:
    height, width = grid.shape
    base_img = Image.new("RGB", (int(width * block_size),
                         int(height * block_size)), (240, 240, 240))
    spiral_coords = get_spiral_order(grid.shape)

    for idx, (y, x) in enumerate(spiral_coords):
        if idx > step_limit or not grid[y, x]:
            continue

        color = tuple(hash_bytes[(x + y) % 32:(x + y) % 32 + 3])
        block_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(block_img)

        x0 = int(x * block_size)
        y0 = int(y * block_size)
        x1 = int((x + 1) * block_size)
        y1 = int((y + 1) * block_size)
        draw.rectangle([x0, y0, x1, y1], fill=color + (255,))

        if glow > 0:
            glow_img = block_img.filter(ImageFilter.GaussianBlur(glow))
            base_img = Image.alpha_composite(
                base_img.convert("RGBA"), glow_img)

        base_img.paste(block_img.convert("RGB"), (0, 0), block_img)

    return base_img


def identimorph_spiral(text="github.com/jncel", blocks=5, size=128, glow=0, fps=5, output_path="identimorph_spiral.gif"):
    frame_duration = int(1000 / fps)
    hash_bytes = get_hash_bytes(text)
    grid = create_identimorph_grid(hash_bytes, blocks)
    block_size = size / blocks
    spiral_coords = get_spiral_order(grid.shape)
    frames_list = [
        draw_spiral_blocks(grid, hash_bytes, block_size, glow, step_limit=i)
        for i in range(len(spiral_coords))
    ]

    frames_list[0].save(
        output_path,
        save_all=True,
        append_images=frames_list[1:],
        duration=frame_duration,
        loop=0
    )
    print(f"Spiral identimorph saved as: {output_path}")
