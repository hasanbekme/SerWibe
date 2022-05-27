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

    def br(self, delta):
        self.y += delta * 20

    def save(self, path=None):
        self.height = self.y + 5
        self.image = self.image.crop((0, 0, self.width, self.height))
        self.image.show()
        if path is not None:
            self.image.save(path)
