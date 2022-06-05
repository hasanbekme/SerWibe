from PIL import Image, ImageDraw, ImageFont


class Receipt:
    def __init__(self, width=6000):
        # 4px == 1mm
        self.width = width
        self.height = 0
        self.image = Image.new(mode='1', size=(width, 80000), color="white")
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype("fonts/cour.ttf", size=24)
        self.y = 0

    def set_font(self, family: str, size: int):
        size = int(self.width * size / 300)
        self.font = ImageFont.truetype(f"fonts/{family}.ttf", size=size)

    def text(self, text: str, align="center", space=False):
        w, h = self.draw.textsize(text, font=self.font)
        if align == "right":
            w = self.width - w
        elif align == "left":
            w = 0
        else:
            w = (self.width - w) / 2
        self.draw.text((w, self.y), text=text, fill="black", font=self.font)
        if space:
            self.y += h

    def insert_image(self, image_path: str):
        temp_img = Image.open(image_path)
        logo_width = int(self.width * 2 / 3)
        logo_height = int(logo_width / temp_img.size[0] * temp_img.size[1])
        resized = temp_img.resize((logo_width, logo_height))
        offset = ((self.width - resized.size[0]) // 2, self.y)
        self.image.paste(resized, offset)
        self.y += logo_height

    def br(self, delta):
        self.y += int(delta * self.width / 300)

    def save(self, path=None):
        self.height = self.y + 5
        self.image = self.image.crop((0, 0, self.width, self.height))
        if path is not None:
            self.image.save(path)
