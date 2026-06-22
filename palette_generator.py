from PIL import Image, ImageDraw, ImageFont
import io
import colorsys

def linear_to_srgb(c):
    if c <= 0.0031308:
        return c * 12.92
    else:
        return 1.055 * (c ** (1/2.4)) - 0.055

# グラデーションパレットを生成する関数
def create_gradient_palette():
    palette = {}
    row_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" # Zまで拡張
    num_rows = len(row_chars) # 明度と彩度変化用 (縦軸)
    num_cols = 20 # 色相変化用 (横軸)

    for r_idx in range(num_rows): # 行 (明度と彩度を変化させる)
        # 明度: 上から下へ明るい色から暗い色へ線形に変化 (0.95 -> 0.05)
        lightness = 0.95 - (r_idx / (num_rows - 1)) * (0.95 - 0.05)

        # 彩度: 上下で低く (0.10)、中央で高く (1.00) なるように変化
        mid_row = (num_rows - 1) / 2.0
        distance_from_mid = abs(r_idx - mid_row) / mid_row
        current_saturation = 1.0 - distance_from_mid * (1.0 - 0.10)
        
        lightness = max(0.0, min(1.0, lightness)) # 0.0から1.0の範囲にクランプ
        current_saturation = max(0.0, min(1.0, current_saturation)) # 0.0から1.0の範囲にクランプ

        for c_idx in range(num_cols): # 列 (色相を変化させる)
            # 色相: 左から右へ均等に変化 (0.0から<1.0)
            hue = c_idx / num_cols

            r_linear, g_linear, b_linear = colorsys.hls_to_rgb(hue, lightness, current_saturation)
            
            # sRGBガンマ補正を適用
            r_srgb = linear_to_srgb(r_linear)
            g_srgb = linear_to_srgb(g_linear)
            b_srgb = linear_to_srgb(b_linear)

            r, g, b = int(r_srgb * 255), int(g_srgb * 255), int(b_srgb * 255)
            
            # 0-255の範囲にクランプ
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # 16進数カラーコードに変換
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            
            # 識別番号を生成 (例: A1, A2, ..., J20)
            identifier = f"{row_chars[r_idx]}{c_idx + 1}"
            palette[identifier] = hex_color
            
    return palette

# 色パレット画像を生成する関数
def create_palette_image():
    COLOR_PALETTE = create_gradient_palette() # 動的にパレットを生成
    cell_size = 60
    margin = 5
    cols = 20 # 20列に変更 (生成されるパレットの列数に合わせる)
    rows = (len(COLOR_PALETTE) + cols - 1) // cols
    
    # 行数が多すぎる場合は調整
    max_rows = 20 # 最大20行に制限
    if rows > max_rows:
        rows = max_rows
        # 表示する色数を調整
        display_colors = cols * rows
        COLOR_PALETTE = dict(list(COLOR_PALETTE.items())[:display_colors])

    img_width = cols * cell_size + (cols + 1) * margin
    img_height = rows * cell_size + (rows + 1) * margin

    img = Image.new('RGB', (img_width, img_height), (54, 57, 63))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    # 識別番号でソートして表示順を安定させる
    sorted_items = sorted(COLOR_PALETTE.items(), key=lambda item: (item[0][0], int(item[0][1:])))

    for i, (code, color_hex) in enumerate(sorted_items):
        if i >= cols * rows: # 表示制限を超えたら終了
            break
        col = i % cols
        row = i // cols
        x0 = margin + col * (cell_size + margin)
        y0 = margin + row * (cell_size + margin)
        x1 = x0 + cell_size
        y1 = y0 + cell_size

        draw.rectangle([x0, y0, x1, y1], fill=color_hex)
        
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_color = "black" if (r*0.299 + g*0.587 + b*0.114) > 186 else "white"
        
        text_bbox = draw.textbbox((0, 0), code, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x0 + (cell_size - text_width) / 2
        text_y = y0 + (cell_size - text_height) / 2
        draw.text((text_x, text_y), code, font=font, fill=text_color)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer