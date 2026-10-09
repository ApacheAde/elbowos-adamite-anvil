#!/usr/bin/env python3
"""Adamite Anvil — chartreuse forge-strike arcade for ElbowOS. Python 3 + pygame.

Swing is automatic. Space / click strikes when the hammer is over a dwelling ingot.
--play  interactive window
--record  headless 15s 1080x1920 MP4 (default if neither flag)
"""
import math
import os
import random
import subprocess
import sys

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
if "--play" not in sys.argv:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "ADAMITE_ANVIL_ElbowOS.mp4")
TITLE, HANDLE = "ADAMITE ANVIL", "x.com/ElbowOS"
INK = (14, 11, 8)
LIME = (198, 240, 77)
AMBER = (255, 170, 46)
COPPER = (176, 92, 40)
CREAM = (255, 236, 198)
SLAG = (72, 62, 54)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if "--play" in sys.argv else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(TITLE)
        self.surf = pygame.Surface((W, H))
        self.font = pygame.font.SysFont("dejavusans", 78, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 46, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 34, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.best = 0
        self.sparks = []
        self.pops = []
        self.embers = [{"x": random.randint(80, W - 80), "y": random.randint(400, H - 80),
                        "v": random.uniform(1.2, 3.4), "s": random.randint(2, 5)} for _ in range(48)]
        self.ingots = []
        self.spawn = 12
        self.cool = 0
        self.flash = 0
        self.judge = ""
        self.shake = 0

    def spawn_ingot(self):
        self.ingots.append({
            "x": W + 160, "state": "travel", "dwell": 0, "heat": 0.15,
            "vy": 0, "dead": False,
        })

    def strike(self):
        if self.cool > 0:
            return
        ang = math.sin(self.t * 0.13) * 1.05
        aligned = abs(ang) < 0.2
        hit = None
        for ing in self.ingots:
            if ing["state"] == "dwell" and 390 < ing["x"] < 690:
                hit = ing
                break
        self.cool = 8
        self.flash = 6
        self.shake = 10
        hx, hy = 540 + math.sin(ang) * 40, 1188
        if hit and aligned:
            perfect = abs(ang) < 0.08
            gain = 140 if perfect else 70
            gain += self.combo * 12
            self.score += gain
            self.combo += 1
            self.best = max(self.best, self.combo)
            self.judge = "PERFECT" if perfect else "STRIKE"
            hit["state"] = "burst"
            hit["heat"] = 1
            self.pops.append({"x": hit["x"], "y": 1240, "life": 28, "txt": f"+{gain}"})
            for _ in range(36):
                a = random.random() * math.tau
                sp = random.uniform(3, 16)
                self.sparks.append({
                    "x": hit["x"], "y": 1288, "vx": math.cos(a) * sp,
                    "vy": math.sin(a) * sp - 8, "life": random.randint(14, 32),
                    "c": random.choice((LIME, AMBER, CREAM, (255, 90, 40))),
                })
        else:
            self.combo = 0
            self.judge = "MISS"
            for _ in range(10):
                self.sparks.append({
                    "x": hx, "y": hy, "vx": random.uniform(-4, 4),
                    "vy": random.uniform(-6, -1), "life": 16, "c": SLAG,
                })

    def step(self, auto=False):
        self.t += 1
        self.cool = max(0, self.cool - 1)
        self.flash = max(0, self.flash - 1)
        self.shake = max(0, self.shake - 1)
        self.spawn -= 1
        if self.spawn <= 0:
            self.spawn_ingot()
            self.spawn = random.randint(48, 62)
        ang = math.sin(self.t * 0.13) * 1.05
        if auto and self.cool == 0 and abs(ang) < 0.1:
            if any(i["state"] == "dwell" and 400 < i["x"] < 680 for i in self.ingots):
                self.strike()
        for ing in self.ingots:
            if ing["state"] == "travel":
                ing["x"] -= 11
                if ing["x"] <= 540:
                    ing["x"] = 540
                    ing["state"] = "dwell"
                    ing["dwell"] = 28
            elif ing["state"] == "dwell":
                ing["dwell"] -= 1
                ing["heat"] = min(1, ing["heat"] + 0.02)
                if ing["dwell"] <= 0:
                    ing["state"] = "exit"
                    self.combo = 0
                    self.judge = "SLAG"
            elif ing["state"] == "exit":
                ing["x"] -= 13
                ing["heat"] *= 0.96
            elif ing["state"] == "burst":
                ing["vy"] -= 0.4
                ing["y"] = ing.get("y", 0) + ing["vy"]
                ing["heat"] = 1
                if ing.get("y", 0) < -80:
                    ing["dead"] = True
        self.ingots = [i for i in self.ingots if i["x"] > -240 and not i["dead"]]
        for s in self.sparks:
            s["x"] += s["vx"]
            s["y"] += s["vy"]
            s["vy"] += 0.35
            s["life"] -= 1
        self.sparks = [s for s in self.sparks if s["life"] > 0]
        for p in self.pops:
            p["y"] -= 3
            p["life"] -= 1
        self.pops = [p for p in self.pops if p["life"] > 0]
        for e in self.embers:
            e["y"] -= e["v"]
            e["x"] += math.sin(self.t * 0.05 + e["y"] * 0.01) * 0.6
            if e["y"] < 280:
                e["y"] = 1680
                e["x"] = random.randint(60, W - 60)

    def draw(self, surf):
        surf.fill(INK)
        for i, col in enumerate(((32, 18, 10), (48, 26, 12), (22, 16, 10))):
            pygame.draw.rect(surf, col, (0, 700 + i * 280, W, 280))
        ox = random.randint(-self.shake, self.shake) if self.shake else 0
        for e in self.embers:
            pygame.draw.circle(surf, (255, 140, 40), (int(e["x"]), int(e["y"])), e["s"])
        # forge mouth glow
        glow = pygame.Surface((520, 220), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 120, 30, 70), glow.get_rect())
        surf.blit(glow, (280 + ox, 1040))
        # belt
        pygame.draw.rect(surf, (42, 32, 24), (0, 1368, W, 36))
        pygame.draw.rect(surf, (88, 64, 36), (0, 1404, W, 14))
        for n in range(14):
            pygame.draw.rect(surf, (60, 44, 28), (n * 90 - (self.t * 8) % 90, 1374, 40, 22))
        # anvil
        ax = 540 + ox
        pygame.draw.polygon(surf, (58, 60, 66), [
            (ax - 250, 1348), (ax + 250, 1348), (ax + 210, 1428), (ax - 210, 1428)])
        pygame.draw.polygon(surf, (168, 172, 180), [
            (ax - 210, 1310), (ax + 210, 1310), (ax + 190, 1352), (ax - 190, 1352)])
        pygame.draw.rect(surf, (40, 42, 48), (ax - 46, 1428, 92, 90))
        # ingots
        for ing in self.ingots:
            x = int(ing["x"] + ox)
            y = 1288 + int(ing.get("y", 0))
            heat = ing["heat"]
            body = (
                int(90 + 80 * heat), int(70 + 150 * heat), int(40 + 30 * heat),
            )
            pygame.draw.rect(surf, body, (x - 92, y, 184, 58), border_radius=8)
            pygame.draw.rect(surf, LIME if heat > 0.7 else AMBER, (x - 92, y, 184, 58), 3, border_radius=8)
            pygame.draw.rect(surf, (255, 236, 160), (x - 60, y + 14, int(120 * heat), 12))
        # hammer
        ang = math.sin(self.t * 0.13) * 1.05
        px, py = 540 + ox, 760
        hx = px + math.sin(ang) * 430
        hy = py + math.cos(ang) * 430
        pygame.draw.line(surf, (90, 70, 48), (px, py), (hx, hy), 22)
        pygame.draw.circle(surf, (120, 90, 50), (px, py), 28)
        head = pygame.Surface((150, 54), pygame.SRCALPHA)
        pygame.draw.rect(head, (210, 214, 220), (0, 0, 150, 54), border_radius=8)
        pygame.draw.rect(head, LIME, (8, 8, 134, 10))
        rot = pygame.transform.rotate(head, -math.degrees(ang))
        surf.blit(rot, rot.get_rect(center=(hx, hy)))
        if self.flash:
            pygame.draw.circle(surf, CREAM, (int(hx), int(hy) + 20), 30 + self.flash * 4)
        for s in self.sparks:
            pygame.draw.circle(surf, s["c"], (int(s["x"]), int(s["y"])), max(2, s["life"] // 6))
        # hud
        title = self.font.render(TITLE, True, LIME)
        surf.blit(title, title.get_rect(center=(W // 2, 120)))
        sub = self.small.render("FORGE STRIKE", True, AMBER)
        surf.blit(sub, sub.get_rect(center=(W // 2, 190)))
        sc = self.font.render(f"{self.score:05d}", True, CREAM)
        surf.blit(sc, sc.get_rect(center=(W // 2, 300)))
        cb = self.mid.render(f"COMBO  x{self.combo}", True, LIME if self.combo else (120, 110, 90))
        surf.blit(cb, cb.get_rect(center=(W // 2, 380)))
        if self.judge:
            jc = LIME if self.judge in ("PERFECT", "STRIKE") else (255, 90, 70)
            j = self.mid.render(self.judge, True, jc)
            surf.blit(j, j.get_rect(center=(W // 2, 980)))
        for p in self.pops:
            lab = self.mid.render(p["txt"], True, LIME)
            surf.blit(lab, lab.get_rect(center=(p["x"], p["y"])))
        hint = self.small.render("SPACE strikes the swing", True, (200, 180, 140))
        surf.blit(hint, hint.get_rect(center=(W // 2, H - 150)))
        handle = self.mid.render(HANDLE, True, LIME)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 80)))

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.strike()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    self.strike()
            self.step(False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.step(auto=True)
                self.draw(self.surf)
                proc.stdin.write(pygame.image.tobytes(self.surf, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        if proc.wait() != 0:
            raise SystemExit(f"ffmpeg failed:\n{err[-1500:]}")
        alt = "/home/workdir/artifacts/ADAMITE_ANVIL_ElbowOS.mp4"
        if os.path.abspath(alt) != os.path.abspath(OUT):
            os.makedirs(os.path.dirname(alt), exist_ok=True)
            subprocess.check_call(["cp", OUT, alt])
        print("wrote", OUT)


def main():
    g = Game()
    if "--play" in sys.argv:
        g.play()
    else:
        g.record()
        pygame.quit()


if __name__ == "__main__":
    main()
