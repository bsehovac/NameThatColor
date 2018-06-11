import sublime
import sublime_plugin
import math
import re

from NameThatColor import color_names

class NameThatColor(sublime_plugin.TextCommand):

    def run(self, edit):
        for sel in self.view.sel():
            str_sel = self.view.substr(sel)
            str_len = len(str_sel)

            if str_len > 7:
                output = self.replace_all(str_sel)
                self.view.replace(edit, sel, output)

            elif str_len == 3 or str_len == 6:
                start = sel.begin() - 1
                end = sel.end()
                self.view.sel().add(sublime.Region(start, end))
                sel = sublime.Region(start, end)

                str_sel = self.view.substr(sel)
                str_len = len(str_sel)

            if str_len == 4 or str_len == 7:
                if re.match('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', str_sel) is not None:
                    str_sel = str_sel[1:]
                    output = self.convert_color(str_sel)
                    self.view.replace(edit, sel, output)

    def replace_all(self, str):
        def repl(m):
            gd = m.groupdict()

            hex = gd.get('hex')
            hex = hex[1:]
            return self.convert_color(hex)

        return re.sub(r'(?P<hex>#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}))', repl, str)

    def convert_color(self, hex_color):
        if (len(hex_color) == 3):
            hex_color = hex_color[0:1] + hex_color[0:1] + hex_color[1:2] + hex_color[1:2] + hex_color[2:3] + hex_color[2:3]

        rgb = self.getRGB(hex_color)
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]

        hsl = self.getHSL(r, g, b)
        h = hsl[0]
        s = hsl[1]
        l = hsl[2]

        ndf = 0
        cl = -1
        df = -1

        for color in color_names.colors:
            if hex_color == color[0]:
                return color[1]

            ndf1 = math.pow(r - color[2], 2) + math.pow(g - color[3], 2) + math.pow(b - color[4], 2)
            ndf2 = math.pow(h - color[5], 2) + math.pow(s - color[6], 2) + math.pow(l - color[7], 2)
            ndf = ndf1 + ndf2 * 2

            if df < 0 or df > ndf:
                df = ndf
                cl = color[1]

        return '$color-' + cl

    def getHSL(self, r, g, b):
        r = r / 255
        g = g / 255
        b = b / 255

        cmin = min(r, min(g, b))
        cmax = max(r, max(g, b))
        delta = cmax - cmin
        l = (cmin + cmax) / 2

        s = 0
        if l > 0 and l < 1:
            s = delta / ((2 * l) if (l < 0.5) else (2 - 2 * l))

        h = 0;
        if delta > 0:
            if cmax == r and cmax != g:
                h += (g - b) / delta
            if cmax == g and cmax != b:
                h += (2 + (b - r) / delta)
            if cmax == b and cmax != r:
                h += (4 + (r - g) / delta)
            h /= 6

        return [int(h * 255), int(s * 255), int(l * 255)]


    def getRGB(self, hex):
        r = (int(hex[0:2], 16))
        g = (int(hex[2:4], 16))
        b = (int(hex[4:6], 16))

        return [r, g, b]