import win32print
import win32con
import win32ui

from PIL import ImageWin, Image

scale_factor = 20


class Document:
    def __init__(self, printer=None, width=None):
        # width, 1 mm = 53.325
        self.height = None
        self.font = None
        self.dc = None
        self.width = width
        self.printer = printer

    def begin_document(self):
        if self.printer is None:
            self.printer = win32print.GetDefaultPrinter()
        self.dc = win32ui.CreateDC()
        self.dc.CreatePrinterDC(self.printer)
        self.dc.StartDoc("Document")
        self.dc.StartPage()
        self.dc.SetMapMode(win32con.MM_TWIPS)

    def end_document(self):
        self.dc.EndPage()
        self.dc.EndDoc()

    def set_font(self, family, size, bold=None):
        weight = 400
        if bold:
            weight = 700
        self.font = win32ui.CreateFont({
            "name": family,
            "height": size * scale_factor,
            "weight": weight,
        })
        self.height = size * scale_factor
        self.dc.SelectObject(self.font)

    def aligned_text(self, text, y, align):
        aligns = {
            "center": win32con.DT_CENTER,
            "right": win32con.DT_RIGHT,
            "left": win32con.DT_LEFT
        }
        self.dc.DrawText(text, (0, -1 * y, self.width, -1 * (y + self.height)), aligns[align])

    def text(self, position, text):
        self.dc.TetxtOut(scale_factor * position[0], -1 * scale_factor * position[1], text)

    def image(self, position, image_path, size):
        img = Image.open(image_path)
        img.convert('1')
        dib = ImageWin.Dib(img)
        end_pos = (position[0] + size[0], position[1] + size[1])
        dest = (position[0] * scale_factor,
                -1 * position[1] * scale_factor,
                end_pos[0] * scale_factor,
                -1 * end_pos[1] * scale_factor)
        dib.draw(self.dc.GetHandleOutput(), dest)
