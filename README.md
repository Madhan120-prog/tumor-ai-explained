# Tumour AI, explained

An interactive explainer, hosted on GitHub Pages, about our research on AI that finds and outlines lung tumours on CT.
It tells one story, from general to specific:

1. **A general neural network**: neuron, weights, layers, how it learns.
2. **Changing the shape for the input**: sliding filters for pictures, zooming out and back in for outlines,
   U-Net's skip connections, 3D filters for scans.
3. **The models we compare**: our own 3D U-Net, nnU-Net, Swin UNETR (a transformer) and, later, MedSAM,
   and why each is shaped the way it is.
4. **Preparing, training, testing fairly, improving**: patient-level split, locked test set, 5 folds, Dice,
   and the tumour cut-off finding.
5. **The working system**: a lung CT flowing through it from file to outline, and where it could go next.

Plain HTML/JS with no build step; WebGL (Three.js) for a few 3D scenes. To view it with the videos working,
run `python3 -m http.server 8123` here and open http://localhost:8123.

## Videos

Each chapter's animation plays on the page by itself as you scroll to it. Some chapters also have a short
[Manim](https://www.manim.community/) video, made from `video/scenes.py`; the rendered MP4s live in `video/`.
To render them again:

```bash
uv venv --python 3.12 video/.venv && VIRTUAL_ENV=video/.venv uv pip install manim
video/.venv/bin/manim -qh video/scenes.py XorAndLayers -o xor-and-layers.mp4 --media_dir video/media
```

Example data: public NSCLC-Radiomics scans, The Cancer Imaging Archive (TCIA), CC BY-NC 3.0. No clinic or hospital data.
