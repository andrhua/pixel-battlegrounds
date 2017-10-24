import pygame
import pygame.freetype
from pygame.rect import Rect
from pygame.surface import Surface
from assets import Assets

class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class Widget:
    def __init__(self, width, height, canvas_color):
        self.width = width
        self.height = height
        self.canvas = Surface([width, height]).convert_alpha()
        self.canvas.fill(canvas_color)

    def draw(self, canvas):
        pass

    @staticmethod
    def multiline_surface(self, string, font, rect, fontColour, BGColour, justification=0):
        """Returns a surface containing the passed text string, reformatted
        to fit within the given rect, word-wrapping as necessary. The text
        will be anti-aliased.

        Parameters
        ----------
        string - the text you wish to render. \n begins a new line.
        font - a Font object
        rect - a rect style giving the size of the surface requested.
        fontColour - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
        BGColour - a three-byte tuple of the rgb value of the surface.
        justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

        Returns
        -------
        Success - a surface object with the text rendered onto it.
        Failure - raises a TextRectException if the text won't fit onto the surface.
        """

        finalLines = []
        requestedLines = string.splitlines()
        # Create a series of lines that will fit on the provided
        # rectangle.
        for requestedLine in requestedLines:
            if font.get_metrics(requestedLine)[0] > rect.width:
                words = requestedLine.split(' ')
                # if any of our words are too long to fit, return.
                for word in words:
                    if font.get_metrics(word)[0] >= rect.width:
                        raise TextRectException("The word " + word + " is too long to fit in the rect passed.")
                # Start a new line
                accumulatedLine = ""
                for word in words:
                    testLine = accumulatedLine + word + " "
                    # Build the line while the words fit.
                    if font.size(testLine)[0] < rect.width:
                        accumulatedLine = testLine
                    else:
                        finalLines.append(accumulatedLine)
                        accumulatedLine = word + " "
                finalLines.append(accumulatedLine)
            else:
                finalLines.append(requestedLine)

        # Let's try to write the text out on the surface.
        surface = pygame.Surface(rect.size)
        surface.fill(BGColour)
        accumulatedHeight = 0
        for line in finalLines:
            if accumulatedHeight + font.size(line)[1] >= rect.height:
                raise TextRectException("Once word-wrapped, the text string was too tall to fit in the rect.")
            if line != "":
                tempSurface = font.render(line, 1, fontColour)
            if justification == 0:
                surface.blit(tempSurface, (0, accumulatedHeight))
            elif justification == 1:
                surface.blit(tempSurface, ((rect.width - tempSurface.get_width()) / 2, accumulatedHeight))
            elif justification == 2:
                surface.blit(tempSurface, (rect.width - tempSurface.get_width(), accumulatedHeight))
            else:
                raise TextRectException("Invalid justification argument: " + str(justification))
            accumulatedHeight += font.size(line)[1]
        return surface


class TextView(Widget):
    def __init__(self, width, height, canvas_color, text, text_color, bg_color, dest):
        super().__init__(width, height, canvas_color)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.dest = dest
        self.font = Assets.font_regular

    def draw(self, canvas):
        canvas.blit(
            super().multiline_surface(self.text, self.text, self.font, Rect(0, 0, self.width, self.height), self.text_color,
                                      self.bg_color, 1), (self.dest[0], self.dest[1]))
