from PIL import Image, ImageDraw, ImageFont
import io
import colorsys

# グラデーションパレットを生成する関数
def create_gradient_palette():
    palette = {}
    num_rows = 10 # 明度と彩度変化用 (縦軸)
    num_cols = 20 # 色相変化用 (横軸)

    palette = {}
    row_chars = "ABCDEFGHIJ" # 10行分の識別子

    for r_idx in range(num_rows): # 行 (明度と彩度を変化させる)
        # 明度と彩度を画像に合わせて調整 (再調整)
        if r_idx == 0: # Row A (非常に暗く、彩度も低い)
            lightness = 0.05
            current_saturation = 0.1
        elif r_idx == 1: # Row B (Aより明るく、彩度も少し高い)
            lightness = 0.15
            current_saturation = 0.25
        elif r_idx == 2: # Row C (Bより明るく、彩度も高い)
            lightness = 0.3
            current_saturation = 0.5
        elif r_idx == 3: # Row D (明るく、彩度が高い)
            lightness = 0.5
            current_saturation = 0.8
        elif r_idx == 4: # Row E (非常に明るく、最高彩度)
            lightness = 0.8
            current_saturation = 1.0
        elif r_idx == 5: # Row F (Eと同様に非常に明るく、最高彩度)
            lightness = 0.8
            current_saturation = 1.0
        elif r_idx == 6: # Row G (少し暗くなり、彩度もわずかに下がる)
            lightness = 0.65
            current_saturation = 0.95
        elif r_idx == 7: # Row H (さらに暗くなり、彩度も下がる)
            lightness = 0.5
            current_saturation = 0.85
        elif r_idx == 8: # Row I (かなり暗く、彩度も中程度)
            lightness = 0.35
            current_saturation = 0.7
        elif r_idx == 9: # Row J (最も暗い行の一つだが、色相は残る)
            lightness = 0.2
            current_saturation = 0.5
        
        lightness = max(0.0, min(1.0, lightness)) # 0.0から1.0の範囲にクランプ
        current_saturation = max(0.0, min(1.0, current_saturation)) # 0.0から1.0の範囲にクランプ

        for c_idx in range(num_cols): # 列 (色相を変化させる)
            # 色相: 左から右へ均等に変化 (0.0から<1.0)
            hue = c_idx / num_cols

            r, g, b = colorsys.hls_to_rgb(hue, lightness, current_saturation)
            r, g, b = int(r * 255), int(g * 255), int(b * 255)
            
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
    cols = 10 # 10列に変更
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