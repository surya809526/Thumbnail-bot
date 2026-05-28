def create_and_send_thumbnail(chat_id, text):
    try:
        # Canvas
        img = Image.new('RGB', (1280, 720), color=(15, 15, 25))
        draw = ImageDraw.Draw(img)

        # Gradient background manually
        for y in range(720):
            r = int(15 + (y / 720) * 40)
            g = int(15 + (y / 720) * 20)
            b = int(25 + (y / 720) * 60)
            draw.line([(0, y), (1280, y)], fill=(r, g, b))

        # Side color bar (left accent)
        draw.rectangle([0, 0, 12, 720], fill=(255, 60, 60))

        # Top-bottom border lines
        draw.rectangle([0, 0, 1280, 8], fill=(255, 60, 60))
        draw.rectangle([0, 712, 1280, 720], fill=(255, 60, 60))

        # Try loading a font, fallback to default
        try:
            from PIL import ImageFont
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            from PIL import ImageFont
            font_big = ImageFont.load_default()
            font_small = font_big

        # Word wrap text
        words = text.upper().split()
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=font_big)
            if bbox[2] > 1100:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)

        # Draw text centered
        total_h = len(lines) * 110
        start_y = (720 - total_h) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_big)
            w = bbox[2] - bbox[0]
            x = (1280 - w) // 2
            y = start_y + i * 110
            # Shadow
            draw.text((x+4, y+4), line, font=font_big, fill=(0, 0, 0, 128))
            # Main text
            draw.text((x, y), line, font=font_big, fill=(255, 255, 255))

        # Bottom watermark
        draw.text((50, 660), "🎬 Swaraj Thumbnails", font=font_small, fill=(180, 180, 180))

        output_path = f"/tmp/thumb_{chat_id}.jpg"
        img.save(output_path, quality=95)

        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        with open(output_path, 'rb') as photo:
            requests.post(url, data={'chat_id': chat_id}, files={'photo': photo})

        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        send_text(chat_id, f"Error: {str(e)}")
