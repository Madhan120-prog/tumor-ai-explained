"""Manim scenes for the explainer, in the same colours as the web page.

Render (from the repo root):
    video/.venv/bin/manim -qh video/scenes.py XorAndLayers -o xor-and-layers.mp4 --media_dir video/media
then copy video/media/videos/scenes/1080p60/xor-and-layers.mp4 to video/, and make the still shown before play:
    ffmpeg -ss 27 -i video/xor-and-layers.mp4 -frames:v 1 -vf scale=1280:-1 -q:v 4 video/xor-and-layers.jpg
"""
import numpy as np
from manim import (
    Axes, Create, DashedLine, Dot, FadeIn, FadeOut, Line, Polygon, Scene, Text, Transform,
    ValueTracker, VGroup, Write, always_redraw, config, DOWN, UP, LEFT, RIGHT, UR, smooth,
)

BG, INK, MUTED = "#fbfaf6", "#1f2933", "#5f6b76"
SIGNAL, MASK, LINE = "#12925c", "#e8590c", "#e6e1d6"
config.background_color = BG
FONT = "Avenir Next"

CORNERS = [(0, 0), (0, 1), (1, 0), (1, 1)]
XOR = [0, 1, 1, 0]


class XorAndLayers(Scene):
    def caption(self, text, old=None):
        new = Text(text, font_size=30, color=INK, font=FONT).to_edge(UP, buff=0.5)
        if old is None:
            self.play(FadeIn(new, shift=DOWN * 0.2))
        else:
            # one after the other, so two captions never overlap on screen
            self.play(FadeOut(old, shift=UP * 0.2), run_time=0.35)
            self.play(FadeIn(new, shift=DOWN * 0.2), run_time=0.5)
        return new

    def border(self, ax, w1, w2, b, color, dashed=False):
        """The neuron's dividing line w1*x + w2*y + b = 0, drawn across the plot."""
        lo, hi = -0.25, 1.25
        # where the line crosses the four edges of the plot, so it never runs into the caption
        hits = []
        for x in (lo, hi):
            if abs(w2) > 1e-6:
                y = -(w1 * x + b) / w2
                if lo <= y <= hi:
                    hits.append((x, y))
        for y in (lo, hi):
            if abs(w1) > 1e-6:
                x = -(w2 * y + b) / w1
                if lo <= x <= hi:
                    hits.append((x, y))
        if len(hits) < 2:   # line misses the plot: draw nothing visible
            hits = [(lo, lo), (lo, lo + 1e-3)]
        p, q = max(((a, c) for a in hits for c in hits), key=lambda pq: np.hypot(*np.subtract(*pq)))
        cls = DashedLine if dashed else Line
        return cls(ax.c2p(*p), ax.c2p(*q), color=color, stroke_width=6)

    def construct(self):
        ax = Axes(x_range=[-0.25, 1.25, 1], y_range=[-0.25, 1.25, 1], x_length=5.2, y_length=5.2,
                  axis_config={"color": LINE, "include_ticks": False}).shift(DOWN * 0.5)
        xl = Text("x₁", font_size=24, color=MUTED, font=FONT).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = Text("x₂", font_size=24, color=MUTED, font=FONT).next_to(ax.y_axis, UP, buff=0.1)

        def dots_at(positions):
            return VGroup(*[
                Dot(ax.c2p(*p), radius=0.16, color=INK, fill_opacity=1 if XOR[i] else 0, stroke_width=5)
                .set_stroke(INK) for i, p in enumerate(positions)])

        dots = dots_at(CORNERS)
        labels = VGroup(*[Text(f"({x},{y})", font_size=20, color=MUTED, font=FONT).next_to(ax.c2p(x, y), UR, buff=0.12)
                          for x, y in CORNERS])

        cap = self.caption("XOR: one or the other, but not both")
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(FadeIn(dots, lag_ratio=0.2), FadeIn(labels, lag_ratio=0.2))
        self.wait(1)

        # 1. one neuron = one straight line; turn it all the way round
        cap = self.caption("One neuron can only draw one straight line", cap)
        angle = ValueTracker(0.3)
        sweep = always_redraw(lambda: self.border(
            ax, np.cos(angle.get_value()), np.sin(angle.get_value()),
            -0.5 * np.cos(angle.get_value()) - 0.5 * np.sin(angle.get_value()), SIGNAL))
        self.play(Create(sweep))
        self.play(angle.animate.set_value(0.3 + 2 * np.pi), run_time=6, rate_func=smooth)
        cap = self.caption("No line puts both filled dots on one side", cap)
        self.wait(1.5)
        self.play(FadeOut(sweep))

        # 2. two hidden neurons, each with its own line
        cap = self.caption("Two hidden neurons: A = OR,  B = NAND", cap)
        or_line = self.border(ax, 1, 1, -0.5, SIGNAL, dashed=True)
        nand_line = self.border(ax, -1, -1, 1.5, SIGNAL, dashed=True)
        tag_a = Text("A", font_size=26, color=SIGNAL, font=FONT).next_to(or_line.get_start(), RIGHT, buff=0.15)
        tag_b = Text("B", font_size=26, color=SIGNAL, font=FONT).next_to(nand_line.get_end(), LEFT, buff=0.15)
        self.play(Create(or_line), FadeIn(tag_a))
        self.play(Create(nand_line), FadeIn(tag_b))
        self.wait(1.5)

        # 3. the hidden layer moves every point to (A, B)
        cap = self.caption("The hidden layer moves each point to (A, B)", cap)
        hidden = [(int(x + y > 0.5), int(-x - y + 1.5 > 0)) for x, y in CORNERS]
        # (0,1) and (1,0) both land on (1,1): offset them a little so both stay visible
        nudged = [(a + d, b - d) for (a, b), d in zip(hidden, [0, -0.05, 0.05, 0])]
        new_xl = Text("A", font_size=24, color=MUTED, font=FONT).move_to(xl)
        new_yl = Text("B", font_size=24, color=MUTED, font=FONT).move_to(yl)
        self.play(FadeOut(or_line), FadeOut(nand_line), FadeOut(tag_a), FadeOut(tag_b), FadeOut(labels))
        self.play(Transform(dots, dots_at(nudged)), Transform(xl, new_xl), Transform(yl, new_yl), run_time=2.5)
        self.wait(1)

        # 4. now one straight line, the output neuron (AND), splits them
        cap = self.caption("Now one line splits them: output = AND(A, B)", cap)
        and_line = self.border(ax, 1, 1, -1.5, MASK)
        fire = Polygon(ax.c2p(0.25, 1.25), ax.c2p(1.25, 1.25), ax.c2p(1.25, 0.25),
                       stroke_width=0, fill_color=MASK, fill_opacity=0.15)
        self.play(FadeIn(fire), Create(and_line))
        self.wait(2)

        cap = self.caption("Each layer turns the clues into better clues", cap)
        self.wait(2.5)
