"""This is my attempt to recreate Ray's Butterfly example:
    http://cablemodem.hex21.com/~binesh/coursera/compartsprocessing/coalesce05.jpg
    http://cablemodem.hex21.com/~binesh/coursera/compartsprocessing/share/share1.html#post-1049
    http://cablemodem.hex21.com/~binesh/coursera/compartsprocessing/share/share2.html#post-1521
"""

import json

class Butterfly:
    def __init__(self, num_vertices):
        with open("butterfly-%d.json" % (num_vertices,), "rt") as jsfp:
            self.butterfly_data = json.load(jsfp)

    def draw(self, posx, posy, sz, theta, nois):
        pushMatrix()
        translate(posx, posy)
        scale(sz, sz)
        rotate(theta)
    
        noStroke()
        for corner1, corner2, corner3, clr in self.butterfly_data:
            fill(color(*clr))
            noisx = randomGaussian() * nois
            noisy = randomGaussian() * nois
            noistheta = 0.0
            noisscale = 1.0
            if nois > 0.0:
                noistheta = randomGaussian() * PI/16.0
                noisscale = 1 + randomGaussian() * 0.01
            pushMatrix()
            translate(noisx, noisy)
            rotate(noistheta)
            scale(noisscale, noisscale)
            triangle(
                    corner1[0], corner1[1],
                    corner2[0], corner2[1],
                    corner3[0], corner3[1],
            )
            popMatrix()
        popMatrix()
    
def my_background(sky, ground, factor):
    for yline in range(0, height):
        logits = (yline / float(height)) * 2 - 1.0    
        prop = 1.0 / (1 + exp(-factor * logits))
        col = lerpColor(sky, ground, prop)
        stroke(col)
        line(0, yline, width, yline)

def frange(strt, fin, step):
    retval = strt
    while (step > 0 and retval <= fin) or (step < 0 and retval >= fin):
        yield retval
        retval += step

def setup():
    size(1280, 720)
    butterfly = Butterfly(4096)

    my_background(color(4, 18, 77), color(0, 0, 0), 10.0)
    translate(width/2, height/2)
    scale(height/2, -height/2)
    strokeWeight(0.001)
    
    freq = 2
    amplitude = 0.15
    nois = 0.0
    frames = []
    for idx, prop in enumerate(frange(1/(2.0*freq), 1280.0/720.0, 0.1)):
        xpos = 1280.0/720.0 - prop * 2.0
        theta = prop * 2 * PI * freq
        ypos = amplitude*prop*sin(theta)
        orientation = -cos(theta) * PI / 4.0
        nois = idx * 0.015
        frames.append((xpos, ypos, orientation, 0.3 + 0.02 * idx, nois))
    
    frames.reverse()
    for xpos, ypos, orientation, siz, nois in frames:
        butterfly.draw(xpos, ypos, siz, orientation, nois)
    save("imgs/binesh-rs.png")
