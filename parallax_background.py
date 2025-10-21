import pygame
import sys
import random
import math
import time
import os
import numpy as np
import asyncio

# ...existing imports and initialization...


class ParallaxBackground:
    """多重スクロール背景クラス"""

    def __init__(self):
        self.layers = []
        self.fallback_mode = False

        # 背景画像の読み込みを試行
        try:
            self.layers = [
                {
                    "image": pygame.image.load("assets/backgrounds/sky_layer1.png"),
                    "speed": 0.1,  # 最も遅い（遠景）
                    "x": 0,
                    "name": "sky_layer1",
                },
                {
                    "image": pygame.image.load("assets/backgrounds/sky_layer2.png"),
                    "speed": 0.3,
                    "x": 0,
                    "name": "sky_layer2",
                },
                {
                    "image": pygame.image.load("assets/backgrounds/mountain_layer.png"),
                    "speed": 0.6,
                    "x": 0,
                    "name": "mountain_layer",
                },
                {
                    "image": pygame.image.load("assets/backgrounds/ground_layer.png"),
                    "speed": 0.9,  # 最も速い（近景）
                    "x": 0,
                    "name": "ground_layer",
                },
            ]
            print("✓ All background layers loaded successfully!")

        except pygame.error as e:
            print(f"⚠ Background images not found: {e}")
            print("Using procedural background instead")
            self.fallback_mode = True
            self._create_procedural_background()

    def _create_procedural_background(self):
        """画像がない場合の代替背景を生成"""
        # グラデーション背景を作成
        width, height = 1920, 600

        # 空のグラデーション
        sky_surface = pygame.Surface((width, height))
        for y in range(height):
            # 上から下へのグラデーション（薄い青から濃い青）
            ratio = y / height
            blue_top = (135, 206, 235)  # スカイブルー
            blue_bottom = (25, 25, 112)  # ミッドナイトブルー

            color = (
                int(blue_top[0] * (1 - ratio) + blue_bottom[0] * ratio),
                int(blue_top[1] * (1 - ratio) + blue_bottom[1] * ratio),
                int(blue_top[2] * (1 - ratio) + blue_bottom[2] * ratio),
            )
            pygame.draw.line(sky_surface, color, (0, y), (width, y))

        # 雲を描画
        cloud_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(20):
            x = random.randint(-100, width + 100)
            y = random.randint(50, height // 3)
            size = random.randint(30, 80)

            # 雲の形を複数の円で作成
            cloud_color = (255, 255, 255, 100)
            for j in range(5):
                offset_x = random.randint(-size // 2, size // 2)
                offset_y = random.randint(-size // 4, size // 4)
                pygame.draw.circle(cloud_surface, cloud_color, (x + offset_x, y + offset_y), size // 2)

        # 山のシルエット
        mountain_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        mountain_color = (50, 50, 80, 200)

        # 山の形を描画
        mountain_points = []
        for x in range(0, width, 20):
            # sin波を使って山の形を作成
            peak_height = 150 + 50 * math.sin(x * 0.01) + 30 * math.sin(x * 0.03)
            y = height - peak_height
            mountain_points.append((x, y))

        mountain_points.append((width, height))
        mountain_points.append((0, height))
        pygame.draw.polygon(mountain_surface, mountain_color, mountain_points)

        self.layers = [
            {"surface": sky_surface, "speed": 0.1, "x": 0, "name": "procedural_sky"},
            {"surface": cloud_surface, "speed": 0.3, "x": 0, "name": "procedural_clouds"},
            {"surface": mountain_surface, "speed": 0.6, "x": 0, "name": "procedural_mountains"},
        ]

    def update(self, camera_x):
        """カメラ移動に応じて背景レイヤーを更新"""
        for layer in self.layers:
            # パララックス効果：レイヤーごとに異なる速度でスクロール
            layer["x"] = -camera_x * layer["speed"]

    def draw(self, screen):
        """背景を描画"""
        for layer in self.layers:
            if "image" in layer:
                # 画像ファイルの場合
                image = layer["image"]
                x = layer["x"] % image.get_width()

                # 画像を繰り返し描画してシームレスにする
                screen.blit(image, (x - image.get_width(), 0))
                screen.blit(image, (x, 0))
                if x + image.get_width() < screen.get_width():
                    screen.blit(image, (x + image.get_width(), 0))

            elif "surface" in layer:
                # 手続き的生成の場合
                surface = layer["surface"]
                x = layer["x"] % surface.get_width()

                screen.blit(surface, (x - surface.get_width(), 0))
                screen.blit(surface, (x, 0))
                if x + surface.get_width() < screen.get_width():
                    screen.blit(surface, (x + surface.get_width(), 0))


# 背景インスタンスをグローバルに作成
parallax_background = ParallaxBackground()


# メインループの描画部分に追加する関数
def draw_background(screen, camera):
    """背景を描画"""
    parallax_background.update(camera.x)
    parallax_background.draw(screen)


# 必要なアセットファイルの説明をコンソールに出力
def print_asset_requirements():
    print("\n" + "=" * 50)
    print("🎨 BACKGROUND ASSET REQUIREMENTS")
    print("=" * 50)
    print("多重スクロール背景を有効にするには、以下のファイルを配置してください：")
    print("\n📁 assets/backgrounds/ フォルダに配置:")
    print("├── sky_layer1.png      (1920x600) - 最奥の空・薄い雲")
    print("├── sky_layer2.png      (1920x600) - 中間の濃い雲")
    print("├── mountain_layer.png  (1920x600) - 山のシルエット")
    print("└── ground_layer.png    (1920x600) - 近景の木々・草")
    print("\n💡 ファイル仕様:")
    print("- 形式: PNG（透明度対応推奨）")
    print("- サイズ: 1920x600ピクセル")
    print("- 各レイヤーは水平方向にタイル可能にする")
    print("\n🎯 デザインガイド:")
    print("- sky_layer1: 薄い青空、白い雲（最も薄く）")
    print("- sky_layer2: より濃い雲、夕焼け要素（中間）")
    print("- mountain_layer: 山や丘のシルエット（暗めの色）")
    print("- ground_layer: 木々、草、岩（最も詳細）")
    print("\n現在は代替背景（プロシージャル生成）を使用中")
    print("=" * 50)


if __name__ == "__main__":
    print_asset_requirements()
