import pygame
import sys
import random
import math
import time
import os
import numpy as np
import asyncio

# Pygameの初期化
pygame.init()
pygame.mixer.init()  # サウンド用の初期化

# 画面の設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Side-Scroller Game")

# 色の定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 255, 50)  # より明るい緑
BLUE = (100, 100, 255)  # より明るい青
RED = (255, 100, 100)  # より明るい赤
YELLOW = (255, 255, 100)  # より明るい黄
ORANGE = (255, 200, 50)  # より明るいオレンジ
PURPLE = (200, 100, 255)  # 紫色
APPLE_RED = (255, 50, 50)
BROWN = (139, 69, 19)  # 茶色

# 多重スクロール背景の読み込み
try:
    from parallax_background import ParallaxBackground, print_asset_requirements

    parallax_background = ParallaxBackground()
    print_asset_requirements()
except ImportError as e:
    print(f"Parallax background module not found: {e}")
    parallax_background = None

# フォントの初期化
try:
    # Linuxの日本語フォントを試す
    font = pygame.font.SysFont("notosanscjkjp", 24)  # Noto Sans CJK JP
    big_font = pygame.font.SysFont("notosanscjkjp", 48)
except:
    try:
        font = pygame.font.SysFont("hackgenconsole", 24)  # HackGen Console
        big_font = pygame.font.SysFont("hackgenconsole", 48)
    except:
        try:
            # TTFファイルを直接読み込み
            font = pygame.font.Font("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", 24)
            big_font = pygame.font.Font("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", 48)
        except:
            try:
                # Windowsの日本語フォントも試す（WSL対応）
                font = pygame.font.SysFont("meiryo", 24)
                big_font = pygame.font.SysFont("meiryo", 48)
            except:
                # デフォルトフォント（英語のみ）
                font = pygame.font.Font(None, 24)
                big_font = pygame.font.Font(None, 48)
                print("Warning: Japanese font not found, using default font")

# サウンドの読み込み
try:
    eat_sound = pygame.mixer.Sound("pnyo.wav")
    eat_sound.set_volume(0.3)
except:
    print("Warning: Sound file 'pnyo.wav' not found. Game will run without sound.")
    eat_sound = pygame.mixer.Sound(buffer=bytes(0))

try:
    alien_destroy_sound = pygame.mixer.Sound("alien_destroy.wav")
    alien_destroy_sound.set_volume(0.5)
except:
    print("Warning: Sound file 'alien_destroy.wav' not found. Game will run without sound.")
    alien_destroy_sound = pygame.mixer.Sound(buffer=bytes(0))

try:
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    explosion_sound.set_volume(0.4)
except:
    print("Warning: Sound file 'explosion.wav' not found. Game will run without sound.")
    explosion_sound = pygame.mixer.Sound(buffer=bytes(0))


# 緑りんご効果音を生成
def generate_green_apple_sound():
    sample_rate = 22050
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # 「BOOM!」という感じの音
    # 低音から高音に上がるスイープ
    frequency_start = 60
    frequency_end = 400
    frequency = frequency_start + (frequency_end - frequency_start) * (t / duration)

    # 音量エンベロープ（最初が一番大きく、徐々に減衰）
    envelope = np.exp(-t * 3)

    # 複数の音を重ねる
    wave1 = np.sin(2 * np.pi * frequency * t) * envelope
    wave2 = np.sin(2 * np.pi * frequency * 2 * t) * envelope * 0.5
    wave3 = np.sin(2 * np.pi * frequency * 0.5 * t) * envelope * 0.3

    # ノイズ成分を追加
    noise = np.random.normal(0, 0.1, len(t)) * envelope * 0.2

    # 全体を合成
    wave = wave1 + wave2 + wave3 + noise

    # 音量を調整
    wave = wave * 0.6
    wave = np.clip(wave, -1, 1)

    # 16bit整数に変換
    wave_int = (wave * 32767).astype(np.int16)

    # ステレオ化
    stereo_wave = np.column_stack((wave_int, wave_int))

    # Pygameのサウンドオブジェクトを作成
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound


green_apple_sound = generate_green_apple_sound()
green_apple_sound.set_volume(0.7)


# 二段ジャンプ効果音を生成
def generate_double_jump_sound():
    sample_rate = 22050
    duration = 0.5
    t = np.linspace(0, duration, int(sample_rate * duration))

    # パワーアップ感のある上昇音
    frequency_start = 220  # A3
    frequency_end = 880  # A5 (2オクターブ上)
    frequency = frequency_start * np.power(frequency_end / frequency_start, t / duration)

    # 音量エンベロープ（最初強く、途中で少し弱くなり、最後に強くなる）
    envelope = np.exp(-t * 2) * (1 + np.sin(2 * np.pi * 8 * t) * 0.3)

    # メインの音波
    wave1 = np.sin(2 * np.pi * frequency * t) * envelope
    wave2 = np.sin(2 * np.pi * frequency * 1.5 * t) * envelope * 0.4  # 5度上の倍音
    wave3 = np.sin(2 * np.pi * frequency * 2 * t) * envelope * 0.2  # オクターブ上

    # キラキラ感を出すための高周波成分
    sparkle = np.sin(2 * np.pi * frequency * 4 * t) * envelope * 0.1

    # 全体を合成
    wave = wave1 + wave2 + wave3 + sparkle

    # 音量を調整
    wave = wave * 0.6
    wave = np.clip(wave, -1, 1)

    # 16bit整数に変換
    wave_int = (wave * 32767).astype(np.int16)

    # ステレオ化
    stereo_wave = np.column_stack((wave_int, wave_int))

    # Pygameのサウンドオブジェクトを作成
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound


double_jump_sound = generate_double_jump_sound()
double_jump_sound.set_volume(0.5)


# 紫りんご効果音を生成
def generate_purple_apple_sound():
    sample_rate = 22050
    duration = 1.2
    t = np.linspace(0, duration, int(sample_rate * duration))

    # 強力なパワーアップ感のある音
    # 低音から高音に上がり、さらに複雑な倍音を持つ
    frequency_start = 55  # A1 (低音)
    frequency_end = 440  # A4
    frequency = frequency_start * np.power(frequency_end / frequency_start, t / duration)

    # より複雑な音量エンベロープ
    envelope = np.exp(-t * 1.5) * (1 + np.sin(2 * np.pi * 6 * t) * 0.4) * (1 - np.exp(-t * 8))

    # より多くの倍音成分
    wave1 = np.sin(2 * np.pi * frequency * t) * envelope
    wave2 = np.sin(2 * np.pi * frequency * 1.5 * t) * envelope * 0.6  # 5度
    wave3 = np.sin(2 * np.pi * frequency * 2 * t) * envelope * 0.4  # オクターブ
    wave4 = np.sin(2 * np.pi * frequency * 3 * t) * envelope * 0.3  # オクターブ+5度
    wave5 = np.sin(2 * np.pi * frequency * 4 * t) * envelope * 0.2  # 2オクターブ

    # 魔法的な効果音のためのノイズ成分
    magic_noise = np.random.normal(0, 0.05, len(t)) * envelope * 0.3

    # 全体を合成
    wave = wave1 + wave2 + wave3 + wave4 + wave5 + magic_noise

    # 音量を調整
    wave = wave * 0.7
    wave = np.clip(wave, -1, 1)

    # 16bit整数に変換
    wave_int = (wave * 32767).astype(np.int16)

    # ステレオ化
    stereo_wave = np.column_stack((wave_int, wave_int))

    # Pygameのサウンドオブジェクトを作成
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound


purple_apple_sound = generate_purple_apple_sound()
purple_apple_sound.set_volume(0.6)


# トゲダメージ効果音を生成
def generate_spike_damage_sound():
    """トゲダメージの効果音（グサッという音）を生成"""
    duration = 0.3  # 0.3秒
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # 刺すような鋭い音の組み合わせ
    # 高周波のインパクト音（金属的な音）
    impact_freq = 3000
    impact_wave = np.sin(2 * np.pi * impact_freq * t) * 0.4

    # 中間周波数のカット音
    cut_freq = 800
    cut_wave = np.sin(2 * np.pi * cut_freq * t) * 0.3

    # 低周波のダメージ音
    damage_freq = 200
    damage_wave = np.sin(2 * np.pi * damage_freq * t) * 0.2

    # ノイズを追加（刺すような質感）
    noise = np.random.normal(0, 0.1, len(t))

    # 急激な減衰エンベロープ（一瞬でサッと音が消える）
    attack = np.linspace(0, 1, int(sample_rate * 0.01))  # 素早い立ち上がり
    decay = np.exp(-10 * t[len(attack) :])  # 急激な減衰
    envelope = np.concatenate([attack, decay])
    envelope = envelope[: len(t)]

    # 全ての要素を組み合わせ
    wave = (impact_wave + cut_wave + damage_wave + noise) * envelope

    # 音量を調整
    wave = np.clip(wave * 0.4, -1.0, 1.0)

    # ステレオに変換
    stereo_wave = np.column_stack((wave, wave))

    # 16ビット整数に変換
    audio_data = (stereo_wave * 32767).astype(np.int16)

    return pygame.sndarray.make_sound(audio_data)


spike_damage_sound = generate_spike_damage_sound()
spike_damage_sound.set_volume(0.7)


# BGM生成関数
def generate_bgm():
    sample_rate = 22050
    duration = 8.0  # 8秒のループ
    t = np.linspace(0, duration, int(sample_rate * duration))

    # ドラムビートのパターン（キック、スネア、ハイハット）
    beats_per_second = 2.0
    beat_interval = 1.0 / beats_per_second

    # ベースライン
    bass_notes = [65.41, 73.42, 82.41, 65.41, 87.31, 73.42, 65.41, 82.41]  # Low notes
    bass_wave = np.zeros(len(t))

    # メロディライン
    melody_notes = [261.63, 329.63, 392.00, 329.63, 440.00, 392.00, 329.63, 261.63]
    melody_wave = np.zeros(len(t))

    # ドラムビート
    drum_wave = np.zeros(len(t))

    for i in range(len(bass_notes)):
        start_time = i * (duration / len(bass_notes))
        end_time = (i + 1) * (duration / len(bass_notes))
        start_idx = int(start_time * sample_rate)
        end_idx = int(end_time * sample_rate)

        if end_idx > len(t):
            end_idx = len(t)

        segment_t = t[start_idx:end_idx] - start_time

        # ベースライン（サイン波 + ノコギリ波）
        bass_freq = bass_notes[i]
        bass_envelope = np.exp(-segment_t * 8) * (1 - np.exp(-segment_t * 20))
        bass_segment = (
            (np.sin(2 * np.pi * bass_freq * segment_t) * 0.8 + np.sin(2 * np.pi * bass_freq * 2 * segment_t) * 0.3)
            * bass_envelope
            * 0.6
        )
        bass_wave[start_idx:end_idx] = bass_segment

        # メロディライン
        melody_freq = melody_notes[i]
        melody_envelope = np.exp(-segment_t * 4) * (1 - np.exp(-segment_t * 12))
        melody_segment = (
            (np.sin(2 * np.pi * melody_freq * segment_t) * 0.6 + np.sin(2 * np.pi * melody_freq * 3 * segment_t) * 0.2)
            * melody_envelope
            * 0.4
        )
        melody_wave[start_idx:end_idx] = melody_segment

        # ドラムビート（より音楽的に）
        if i % 2 == 0:  # キック
            drum_env = np.exp(-segment_t * 12)
            kick = np.sin(2 * np.pi * 55 * segment_t) * drum_env * 0.7
            drum_wave[start_idx:end_idx] += kick

        if i % 4 == 2:  # スネア（ノイズ量を減らす）
            snare_env = np.exp(-segment_t * 8)
            # トーンとノイズのミックス
            snare_tone = np.sin(2 * np.pi * 200 * segment_t) * snare_env * 0.3
            snare_noise = np.random.normal(0, 0.1, len(segment_t)) * snare_env * 0.2
            drum_wave[start_idx:end_idx] += snare_tone + snare_noise

    # ハイハット（よりクリーンに）
    hihat_pattern = np.sin(2 * np.pi * beats_per_second * 8 * t) > 0.8
    hihat_env = np.exp(-((t % (1 / beats_per_second / 2)) * 20))
    hihat_clean = np.sin(2 * np.pi * 8000 * t) * hihat_pattern * hihat_env * 0.1

    # 全体をミックス
    wave = bass_wave + melody_wave + drum_wave + hihat_clean

    # 音量を調整
    wave = wave * 0.4
    wave = np.clip(wave, -1, 1)

    # 16bit整数に変換
    wave_int = (wave * 32767).astype(np.int16)

    # ステレオ化
    stereo_wave = np.column_stack((wave_int, wave_int))

    # Pygameのサウンドオブジェクトを作成
    sound = pygame.sndarray.make_sound(stereo_wave)
    return sound


# BGMを読み込み
try:
    bgm = pygame.mixer.Sound("bgm.mp3")
    bgm.set_volume(0.7)  # 音量調整
    print("✓ BGM loaded from bgm.mp3")
except pygame.error:
    print("⚠ Failed to load bgm.mp3, using generated BGM")
    bgm = generate_bgm()
    bgm.set_volume(0.6)


class GameState:
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.game_over_time = 0
        self.game_over_duration = 5.0  # 5秒

    def add_score(self):
        self.score += 1

    def trigger_game_over(self):
        self.game_over = True
        self.game_over_time = time.time()

    def should_reset(self):
        if self.game_over:
            return time.time() - self.game_over_time >= self.game_over_duration
        return False

    def reset(self):
        self.score = 0
        self.game_over = False
        self.game_over_time = 0


class Camera:
    def __init__(self):
        self.x = 0
        self.follow_speed = 0.1

    def update(self, target_x):
        # スライムの位置に基づいてカメラを更新
        target_camera_x = target_x - SCREEN_WIDTH // 3

        # 右方向のみスクロール（左には戻らない）
        if target_camera_x > self.x:
            self.x += (target_camera_x - self.x) * self.follow_speed

        # カメラが左に戻らないようにする（右スクロールのみ）
        if self.x < 0:
            self.x = 0

    def reset(self):
        self.x = 0


class PlatformGenerator:
    def __init__(self):
        self.platforms = []
        self.last_platform_x = 0
        self.platform_width = 100
        self.platform_height = 20
        self.min_gap = 50
        self.max_gap = 200
        self.min_height = 100
        self.max_height = 500

        # 初期プラットフォームを生成
        self.generate_initial_platforms()

    def generate_initial_platforms(self):
        # 画面内に初期プラットフォームを配置
        for i in range(10):
            x = i * 150
            y = random.randint(self.min_height, self.max_height)
            self.platforms.append(Block(x, y, self.platform_width, self.platform_height))
            self.last_platform_x = x

    def update(self, camera_x):
        # カメラの右端より先にプラットフォームを生成
        rightmost_visible = camera_x + SCREEN_WIDTH + 200

        while self.last_platform_x < rightmost_visible:
            # 新しいプラットフォームを生成
            gap = random.randint(self.min_gap, self.max_gap)
            new_x = self.last_platform_x + self.platform_width + gap
            new_y = random.randint(self.min_height, self.max_height)

            # 10%の確率でトゲプラットフォームを生成
            if random.random() < 0.1:  # 10%の確率
                platform = SpikedPlatform(new_x, new_y, self.platform_width, self.platform_height)
                print(f"Generated spiked platform at x={new_x}, y={new_y}")
            else:
                platform = Block(new_x, new_y, self.platform_width, self.platform_height)

            self.platforms.append(platform)
            self.last_platform_x = new_x

        # 画面外のプラットフォームを削除
        leftmost_visible = camera_x - 200
        self.platforms = [platform for platform in self.platforms if platform.rect.right > leftmost_visible]

    def reset(self):
        self.platforms = []
        self.last_platform_x = 0
        self.generate_initial_platforms()


class AlienGenerator:
    def __init__(self):
        self.aliens = []
        self.last_alien_x = 600
        self.attack_timer = 0
        self.attack_interval = 1.0  # 1秒間隔
        self.generate_initial_aliens()

    def generate_initial_aliens(self):
        # 初期エイリアンを配置
        for i in range(5):
            x = 600 + i * 400
            y = random.choice([50, 200, 350, SCREEN_HEIGHT - 150])
            # 10%の確率で赤いエイリアンを生成
            alien_type = "red" if random.random() < 0.1 else "normal"
            self.aliens.append(Alien(x, y, alien_type))
            if alien_type == "red":
                print(f"Generated RED alien at x={x}, y={y}")
            self.last_alien_x = x

    def update(self, camera_x):
        # 新しいエイリアンを生成
        rightmost_visible = camera_x + SCREEN_WIDTH + 300

        while self.last_alien_x < rightmost_visible:
            gap = random.randint(300, 600)
            new_x = self.last_alien_x + gap
            new_y = random.choice([50, 200, 350, SCREEN_HEIGHT - 150])

            # 10%の確率で赤いエイリアンを生成
            alien_type = "red" if random.random() < 0.1 else "normal"
            self.aliens.append(Alien(new_x, new_y, alien_type))
            self.last_alien_x = new_x
            if alien_type == "red":
                print(f"Generated RED alien at x={new_x}, y={new_y}")
            else:
                print(f"Generated new alien at x={new_x}, y={new_y}")  # デバッグ用

        # 画面外のエイリアンを削除（破壊されたものも削除）
        leftmost_visible = camera_x - 200
        initial_count = len(self.aliens)
        self.aliens = [alien for alien in self.aliens if alien.x > leftmost_visible and alien.alive]
        removed_count = initial_count - len(self.aliens)
        if removed_count > 0:
            print(f"Removed {removed_count} aliens")  # デバッグ用

    def should_attack(self):
        current_time = time.time()
        if current_time - self.attack_timer >= self.attack_interval:
            self.attack_timer = current_time
            return True
        return False

    def get_active_aliens(self):
        return [alien for alien in self.aliens if alien.alive]

    def add_alien(self, x, y, alien_type="normal"):
        """エイリアンを追加する（赤いエイリアンの分裂用）"""
        self.aliens.append(Alien(x, y, alien_type))
        print(f"Spawned alien at x={x}, y={y}, type={alien_type}")

    def reset(self):
        self.aliens = []
        self.last_alien_x = 600
        self.attack_timer = 0
        self.generate_initial_aliens()


class AlienBullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = 5
        self.speed = 8
        self.angle = angle
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.active = True
        self.color = (255, 0, 0)  # 赤色
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def draw(self, screen, camera):
        if self.active:
            screen_x = self.x - camera.x
            screen_y = self.y
            if screen_x > -50 and screen_x < SCREEN_WIDTH + 50:
                pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)


class Alien:
    def __init__(self, x, y, alien_type="normal"):
        self.x = x
        self.y = y
        self.alien_type = alien_type

        if alien_type == "red":
            self.width = 75  # 大きくする
            self.height = 90
            self.color = (255, 100, 100)  # 赤色
            self.eye_color = (255, 255, 0)  # 黄色い目
            self.antenna_color = (200, 50, 50)
        elif alien_type == "spawned":
            self.width = 70  # 大きくする
            self.height = 85
            self.color = (100, 100, 255)  # 青色（スライムを狙う特別な能力）
            self.eye_color = (255, 0, 0)  # 赤い目
            self.antenna_color = (50, 50, 200)
        else:
            self.width = 50
            self.height = 60
            self.color = (150, 255, 150)  # 薄い緑色
            self.eye_color = BLACK
            self.antenna_color = (100, 200, 100)

        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.hover_offset = 0
        self.hover_speed = 0.05
        self.hover_amount = 8
        self.alive = True

    def update(self):
        if self.alive:
            # 浮遊効果
            self.hover_offset += self.hover_speed
            if self.hover_offset > 2 * math.pi:
                self.hover_offset -= 2 * math.pi

    def destroy(self):
        if self.alive:
            self.alive = False
            alien_destroy_sound.play()

            # 赤いエイリアンが破壊された場合、4体のエイリアンを生成する情報を返す
            if self.alien_type == "red":
                spawn_info = []
                # ゲーム画面の4角に配置：右上、右下、左上、左下
                # 現在のカメラ位置を基準にした画面の4角
                positions = [
                    {"x": "screen_right", "y": "screen_top"},  # 右上
                    {"x": "screen_right", "y": "screen_bottom"},  # 右下
                    {"x": "screen_left", "y": "screen_top"},  # 左上
                    {"x": "screen_left", "y": "screen_bottom"},  # 左下
                ]
                for pos in positions:
                    spawn_info.append({"x": pos["x"], "y": pos["y"], "type": "spawned"})
                return {"destroyed": True, "spawn_aliens": spawn_info, "current_alien_pos": {"x": self.x, "y": self.y}}

            return {"destroyed": True}
        return {"destroyed": False}

    def shoot(self, slime_x=None, slime_y=None):
        bullets = []
        bullet_x = self.x
        bullet_y = self.y + self.height // 2

        if self.alien_type == "red":
            # 赤いエイリアンは3発撃つ（左方向に-45度～45度）
            angles = [
                math.radians(random.uniform(135, 155)),  # 上寄り
                math.radians(random.uniform(170, 190)),  # 真ん中
                math.radians(random.uniform(205, 225)),  # 下寄り
            ]
            for angle in angles:
                bullets.append(AlienBullet(bullet_x, bullet_y, angle))
        elif self.alien_type == "spawned" and slime_x is not None and slime_y is not None:
            # spawnedタイプはスライムを狙う
            # スライムの中心を狙う
            target_x = slime_x + 25  # スライムの中心
            target_y = slime_y + 25

            # エイリアンからスライムへの角度を計算
            dx = target_x - bullet_x
            dy = target_y - bullet_y
            angle = math.atan2(dy, dx)

            bullets.append(AlienBullet(bullet_x, bullet_y, angle))
            print(f"Spawned alien shooting at slime! Angle: {math.degrees(angle):.1f}°")
        else:
            # 通常のエイリアンは1発
            angle = math.radians(random.uniform(135, 225))  # 左向きに調整
            bullets.append(AlienBullet(bullet_x, bullet_y, angle))

        return bullets

    def draw(self, screen, camera):
        if not self.alive:
            return

        # カメラオフセットを適用した描画位置
        screen_x = self.x - camera.x
        screen_y = self.y

        # 画面外なら描画しない
        if screen_x < -self.width or screen_x > SCREEN_WIDTH:
            return

        # 浮遊による上下の動き
        hover_y = screen_y + math.sin(self.hover_offset) * self.hover_amount

        # 衝突判定用のrectを更新
        self.rect.x = self.x
        self.rect.y = self.y + math.sin(self.hover_offset) * self.hover_amount

        # エイリアンの体（楕円）
        body_rect = pygame.Rect(screen_x, hover_y + self.height * 0.3, self.width, self.height * 0.7)
        pygame.draw.ellipse(screen, self.color, body_rect)

        # エイリアンの頭（円）
        head_radius = self.width // 3
        head_x = screen_x + self.width // 2
        head_y = hover_y + head_radius
        pygame.draw.circle(screen, self.color, (head_x, head_y), head_radius)

        # 触角
        antenna_length = 15
        # 左の触角
        left_antenna_x = head_x - head_radius // 2
        left_antenna_y = head_y - head_radius
        pygame.draw.line(
            screen,
            self.antenna_color,
            (left_antenna_x, left_antenna_y),
            (left_antenna_x - 5, left_antenna_y - antenna_length),
            3,
        )
        pygame.draw.circle(screen, self.antenna_color, (left_antenna_x - 5, left_antenna_y - antenna_length), 4)

        # 右の触角
        right_antenna_x = head_x + head_radius // 2
        right_antenna_y = head_y - head_radius
        pygame.draw.line(
            screen,
            self.antenna_color,
            (right_antenna_x, right_antenna_y),
            (right_antenna_x + 5, right_antenna_y - antenna_length),
            3,
        )
        pygame.draw.circle(screen, self.antenna_color, (right_antenna_x + 5, right_antenna_y - antenna_length), 4)

        # 目（2つの大きな楕円）
        left_eye_x = head_x - head_radius // 3
        right_eye_x = head_x + head_radius // 3
        eye_y = head_y - head_radius // 4
        eye_width = 8
        eye_height = 12

        pygame.draw.ellipse(
            screen, self.eye_color, (left_eye_x - eye_width // 2, eye_y - eye_height // 2, eye_width, eye_height)
        )
        pygame.draw.ellipse(
            screen, self.eye_color, (right_eye_x - eye_width // 2, eye_y - eye_height // 2, eye_width, eye_height)
        )

        # 腕（細い楕円）
        arm_width = 8
        arm_height = 25
        # 左腕
        left_arm_rect = pygame.Rect(screen_x - arm_width // 2, hover_y + self.height * 0.4, arm_width, arm_height)
        pygame.draw.ellipse(screen, self.color, left_arm_rect)

        # 右腕
        right_arm_rect = pygame.Rect(
            screen_x + self.width - arm_width // 2, hover_y + self.height * 0.4, arm_width, arm_height
        )
        pygame.draw.ellipse(screen, self.color, right_arm_rect)


class Explosion:
    def __init__(self, x, y, power_level=1, play_sound=True):
        self.x = x
        self.y = y
        self.power_level = power_level
        self.radius = 5
        self.max_radius = 30 + power_level * 10
        self.growth_speed = 2 + power_level * 0.5
        self.active = True
        self.color = ORANGE
        self.particles = []
        self.create_particles()

        if play_sound:
            explosion_sound.play()

    def create_particles(self):
        num_particles = 15 + self.power_level * 5
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8 + self.power_level * 2)
            self.particles.append(
                {
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(20, 40 + self.power_level * 5),
                    "max_life": random.uniform(20, 40 + self.power_level * 5),
                    "size": random.uniform(2, 4 + self.power_level),
                }
            )

    def update(self):
        if self.radius < self.max_radius:
            self.radius += self.growth_speed
        else:
            self.active = False

        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.pop(i)

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y

        if screen_x < -100 or screen_x > SCREEN_WIDTH + 100:
            return

        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(self.radius))

        for particle in self.particles:
            if particle["life"] > 0:
                alpha_ratio = max(0, min(1, particle["life"] / particle["max_life"]))
                color = (
                    max(0, min(255, int(self.color[0] * alpha_ratio))),
                    max(0, min(255, int(self.color[1] * alpha_ratio))),
                    max(0, min(255, int(self.color[2] * alpha_ratio))),
                )
                particle_screen_x = particle["x"] - camera.x
                particle_screen_y = particle["y"]
                pos = (int(particle_screen_x), int(particle_screen_y))
                pygame.draw.circle(screen, color, pos, max(1, int(particle["size"])))


class BigExplosion:
    def __init__(self, x, y, play_sound=True):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 80
        self.growth_speed = 4
        self.active = True
        self.color = (255, 100, 0)
        self.particles = []
        self.create_particles()

        if play_sound:
            alien_destroy_sound.play()

    def create_particles(self):
        num_particles = 50
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            self.particles.append(
                {
                    "x": self.x,
                    "y": self.y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(40, 80),
                    "max_life": random.uniform(40, 80),
                    "size": random.uniform(3, 8),
                }
            )

    def update(self):
        if self.radius < self.max_radius:
            self.radius += self.growth_speed
        else:
            self.active = False

        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.pop(i)

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y

        if screen_x < -100 or screen_x > SCREEN_WIDTH + 100:
            return

        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), int(self.radius))

        for particle in self.particles:
            if particle["life"] > 0:
                alpha_ratio = max(0, min(1, particle["life"] / particle["max_life"]))
                color = (max(0, min(255, int(255 * alpha_ratio))), max(0, min(255, int(100 * alpha_ratio))), 0)
                particle_screen_x = particle["x"] - camera.x
                particle_screen_y = particle["y"]
                pos = (int(particle_screen_x), int(particle_screen_y))
                pygame.draw.circle(screen, color, pos, max(1, int(particle["size"])))


class Projectile:
    def __init__(self, x, y, direction, power_level=1, is_big=False):
        self.x = x
        self.y = y
        self.radius = 100 if is_big else 8  # 大きい弾は半径100に超巨大化
        self.speed = 22 if is_big else 10  # 大きい弾は速度22に増加
        self.direction = direction
        self.active = True
        self.color = (255, 200, 0) if is_big else PURPLE  # 大きい弾は金色
        self.creation_time = time.time()
        self.explosion = None
        self.explosion_delay = 1.0 if is_big else 0.5  # 大きい弾はもっと長く飛ぶ
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.power_level = power_level
        self.is_big = is_big
        self.can_penetrate = is_big and power_level == 4  # 紫フォーム（power_level 4）の大きい弾のみ貫通

    def move(self):
        # velocity_xとvelocity_yが設定されている場合はそれを使用（上方向の弾用）
        if hasattr(self, "velocity_x") and hasattr(self, "velocity_y"):
            self.x += self.velocity_x
            self.y += self.velocity_y
        else:
            # 通常の左右方向の弾
            self.x += self.speed * self.direction

        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def update(self):
        if time.time() - self.creation_time >= self.explosion_delay and not self.explosion:
            explosion_power = self.power_level * (3 if self.is_big else 1)  # 大きい弾の爆発力も増加
            self.explosion = Explosion(self.x, self.y, explosion_power)
            self.active = False

    def draw(self, screen, camera):
        if self.active:
            screen_x = self.x - camera.x
            screen_y = self.y
            if screen_x > -50 and screen_x < SCREEN_WIDTH + 50:
                pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)

                # 大きい弾の特別なエフェクト
                if self.is_big:
                    # 青色弾と他の弾で異なるエフェクト
                    if self.color == (100, 150, 255):  # 青色弾の場合
                        # 内側の光る核（青色系）
                        pygame.draw.circle(screen, (200, 220, 255), (int(screen_x), int(screen_y)), self.radius // 2)
                        # 中間の輝き
                        pygame.draw.circle(screen, (150, 180, 255), (int(screen_x), int(screen_y)), self.radius // 3)
                        # キラキラエフェクト（青色系）
                        for i in range(8):
                            sparkle_angle = (time.time() * 8 + i * 0.785) % (2 * math.pi)
                            sparkle_x = screen_x + math.cos(sparkle_angle) * (self.radius + 8)
                            sparkle_y = screen_y + math.sin(sparkle_angle) * (self.radius + 8)
                            pygame.draw.circle(screen, (150, 200, 255), (int(sparkle_x), int(sparkle_y)), 4)

                        # 追加の外側キラキラ（青色系）
                        for i in range(6):
                            sparkle_angle2 = (time.time() * -6 + i * 1.047) % (2 * math.pi)
                            sparkle_x2 = screen_x + math.cos(sparkle_angle2) * (self.radius + 15)
                            sparkle_y2 = screen_y + math.sin(sparkle_angle2) * (self.radius + 15)
                            pygame.draw.circle(screen, (100, 180, 255), (int(sparkle_x2), int(sparkle_y2)), 3)
                    else:  # 金色弾（紫フォーム）の場合
                        # 内側の光る核（より大きく）
                        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), self.radius // 2)
                        # 中間の輝き
                        pygame.draw.circle(screen, (255, 255, 200), (int(screen_x), int(screen_y)), self.radius // 3)
                        # キラキラエフェクト（数を増やす）
                        for i in range(8):
                            sparkle_angle = (time.time() * 8 + i * 0.785) % (2 * math.pi)
                            sparkle_x = screen_x + math.cos(sparkle_angle) * (self.radius + 8)
                            sparkle_y = screen_y + math.sin(sparkle_angle) * (self.radius + 8)
                            pygame.draw.circle(screen, (255, 255, 150), (int(sparkle_x), int(sparkle_y)), 4)

                        # 追加の外側キラキラ
                        for i in range(6):
                            sparkle_angle2 = (time.time() * -6 + i * 1.047) % (2 * math.pi)
                            sparkle_x2 = screen_x + math.cos(sparkle_angle2) * (self.radius + 15)
                            sparkle_y2 = screen_y + math.sin(sparkle_angle2) * (self.radius + 15)
                            pygame.draw.circle(screen, (255, 200, 100), (int(sparkle_x2), int(sparkle_y2)), 3)

        elif self.explosion and self.explosion.active:
            self.explosion.update()
            self.explosion.draw(screen, camera)

    def check_collision(self, blocks):
        if not self.active:
            return False
        for block in blocks:
            if (
                self.x + self.radius > block.rect.left
                and self.x - self.radius < block.rect.right
                and self.y + self.radius > block.rect.top
                and self.y - self.radius < block.rect.bottom
            ):

                # 貫通弾の場合は衝突時に爆発エフェクトのみ生成して、弾は継続
                if self.can_penetrate:
                    # 貫通時の小爆発エフェクト
                    penetration_explosion = Explosion(self.x, self.y, 1, False)  # 音は鳴らさない
                    # メイン関数で管理するために、戻り値で爆発オブジェクトを返す可能性もあるが、今回は簡単な実装にする
                    print(f"Purple bullet penetrating through platform at x={self.x:.1f}, y={self.y:.1f}")
                    return False  # 弾は継続するので衝突扱いにしない
                else:
                    # 通常弾の場合は従来通り爆発して停止
                    explosion_power = self.power_level * (3 if self.is_big else 1)
                    self.explosion = Explosion(self.x, self.y, explosion_power)
                    self.active = False
                    return True
        return False

    def explode(self):
        if self.active:
            explosion_power = self.power_level * (3 if self.is_big else 1)  # 大きい弾の爆発力も増加
            self.explosion = Explosion(self.x, self.y, explosion_power)
            self.active = False


class Block:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = RED

    def draw(self, screen, camera):
        screen_x = self.rect.x - camera.x
        screen_y = self.rect.y

        if screen_x > -self.rect.width and screen_x < SCREEN_WIDTH:
            screen_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)
            pygame.draw.rect(screen, self.color, screen_rect)


class SpikedPlatform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (100, 100, 100)  # ダークグレー
        self.spike_color = (200, 0, 0)  # 濃い赤
        self.is_spiked = True  # トゲプラットフォーム識別用

    def draw(self, screen, camera):
        screen_x = self.rect.x - camera.x
        screen_y = self.rect.y

        if screen_x > -self.rect.width and screen_x < SCREEN_WIDTH:
            # プラットフォーム本体を描画
            screen_rect = pygame.Rect(screen_x, screen_y, self.rect.width, self.rect.height)
            pygame.draw.rect(screen, self.color, screen_rect)

            # プラットフォームの輪郭を描画
            pygame.draw.rect(screen, (50, 50, 50), screen_rect, 2)

            # トゲを描画（上面にのみ）
            spike_width = 8
            spike_height = 12
            # プラットフォームの幅に合わせてトゲの数を調整し、左右に余白を作る
            available_width = self.rect.width - 4  # 両端に2ピクセルずつ余白
            num_spikes = available_width // spike_width
            # 残りのスペースを均等に分配して、トゲを中央寄せに配置
            total_spike_width = num_spikes * spike_width
            offset = (self.rect.width - total_spike_width) // 2

            for i in range(num_spikes):
                spike_x = screen_x + offset + i * spike_width + spike_width // 2
                spike_top_y = screen_y - spike_height
                spike_bottom_y = screen_y

                # 三角形のトゲを描画
                spike_points = [
                    (spike_x, spike_top_y),  # 頂点
                    (spike_x - spike_width // 2, spike_bottom_y),  # 左下
                    (spike_x + spike_width // 2, spike_bottom_y),  # 右下
                ]
                pygame.draw.polygon(screen, self.spike_color, spike_points)

                # トゲの輪郭を描画
                pygame.draw.polygon(screen, (150, 0, 0), spike_points, 2)


class Apple:
    def __init__(self, x, y, apple_type="red"):
        self.x = x
        self.y = y
        self.type = apple_type
        self.consumed = False
        self.sparkle_timer = 0
        self.sparkle_particles = []

    def update(self):
        """りんごの更新（キラキラエフェクト用）"""
        if self.type in ["blue", "purple", "green", "brown"]:
            self.sparkle_timer += 1
            if self.sparkle_timer % 10 == 0:  # 10フレームごとに新しいキラキラ
                for _ in range(3):
                    particle = {
                        "x": self.x + random.randint(-15, 15),
                        "y": self.y + random.randint(-15, 15),
                        "life": 30,
                        "vx": random.uniform(-1, 1),
                        "vy": random.uniform(-1, 1),
                    }
                    self.sparkle_particles.append(particle)

            # パーティクルの更新
            for particle in self.sparkle_particles[:]:
                particle["x"] += particle["vx"]
                particle["y"] += particle["vy"]
                particle["life"] -= 1
                if particle["life"] <= 0:
                    self.sparkle_particles.remove(particle)

    def draw(self, screen, camera):
        if not self.consumed:
            screen_x = self.x - camera.x
            screen_y = self.y
            width = 30
            height = 30

            # 画面外なら描画しない
            if screen_x < -50 or screen_x > SCREEN_WIDTH + 50:
                return

            # キラキラエフェクトを描画（青、紫、緑、茶色りんご用）
            if self.type in ["blue", "purple", "green", "brown"]:
                for particle in self.sparkle_particles:
                    sparkle_screen_x = particle["x"] - camera.x
                    sparkle_screen_y = particle["y"]
                    alpha = int(255 * (particle["life"] / 30))

                    # キラキラの色
                    if self.type == "blue":
                        sparkle_color = (100, 150, 255)
                    elif self.type == "purple":
                        sparkle_color = (255, 100, 255)
                    elif self.type == "green":
                        sparkle_color = (50, 255, 50)
                    elif self.type == "brown":
                        sparkle_color = (255, 200, 100)  # 茶色のキラキラは暖色系

                    # キラキラを描画
                    size = max(1, particle["life"] // 10)
                    if size > 0:
                        pygame.draw.circle(screen, sparkle_color, (int(sparkle_screen_x), int(sparkle_screen_y)), size)

            # りんご本体を描画
            if self.type == "red":
                color = RED
            elif self.type == "blue":
                color = BLUE
            elif self.type == "green":
                color = (0, 255, 0)  # 鮮やかな緑
            elif self.type == "purple":
                color = (128, 0, 128)  # 紫色
            elif self.type == "brown":
                color = BROWN  # 茶色

            # りんごの本体（円）
            apple_center_x = int(screen_x + width // 2)
            apple_center_y = int(screen_y + height // 2)
            pygame.draw.circle(screen, color, (apple_center_x, apple_center_y), width // 2)

            # りんごのハイライト
            highlight_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.circle(screen, highlight_color, (apple_center_x - 3, apple_center_y - 3), width // 4)

            # りんごの葉っぱ（茎の部分）
            leaf_color = (0, 150, 0)
            stem_rect = pygame.Rect(apple_center_x - 2, screen_y - 2, 4, 8)
            pygame.draw.rect(screen, (139, 69, 19), stem_rect)  # 茶色の茎

            # 葉っぱ
            leaf_points = [
                (apple_center_x + 2, screen_y + 2),
                (apple_center_x + 8, screen_y - 3),
                (apple_center_x + 6, screen_y + 4),
                (apple_center_x + 2, screen_y + 6),
            ]
            pygame.draw.polygon(screen, leaf_color, leaf_points)


class FlyingPlatform:
    def __init__(self, platform, angle):
        self.x = platform.rect.x
        self.y = platform.rect.y
        self.width = platform.rect.width
        self.height = platform.rect.height
        self.angle = angle
        self.rotation_angle = 0
        self.speed = 15  # 速度を倍近くに上げる

        # 角度から速度成分を計算
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed

        self.life = 180  # 3秒間表示
        self.active = True

    def update(self):
        if not self.active:
            return

        # 移動
        self.x += self.vx
        self.y += self.vy

        # 重力の影響を少し受ける（上に飛んでいる場合のみ）
        if self.vy < 0:
            self.vy += 0.5
        else:
            self.vy += 0.2

        # 回転
        self.rotation_angle += 20  # 20度ずつ回転（より激しく）

        # ライフタイマー減少
        self.life -= 1
        if self.life <= 0:
            self.active = False

    def draw(self, screen, camera):
        if not self.active:
            return

        screen_x = self.x - camera.x
        screen_y = self.y

        # 画面外なら描画しない
        if screen_x < -200 or screen_x > SCREEN_WIDTH + 200:
            return

        # 回転した四角形を描画
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2

        # 四角形の頂点を計算
        half_width = self.width // 2
        half_height = self.height // 2

        # 回転行列を適用
        cos_angle = math.cos(math.radians(self.rotation_angle))
        sin_angle = math.sin(math.radians(self.rotation_angle))

        corners = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height),
        ]

        rotated_corners = []
        for corner_x, corner_y in corners:
            rotated_x = corner_x * cos_angle - corner_y * sin_angle
            rotated_y = corner_x * sin_angle + corner_y * cos_angle
            rotated_corners.append((center_x + rotated_x, center_y + rotated_y))

        # 色を時間と共に薄くする
        alpha_factor = self.life / 180
        base_color = (int(255 * alpha_factor), int(100 * alpha_factor), int(100 * alpha_factor))

        # 背景に光の効果を追加
        for i in range(3):
            glow_factor = (3 - i) / 3 * alpha_factor
            glow_color = (int(255 * glow_factor), int(150 * glow_factor), int(150 * glow_factor))

            # 拡大した四角形で光の効果
            glow_corners = []
            for corner_x, corner_y in corners:
                expanded_x = corner_x * (1 + i * 0.2)
                expanded_y = corner_y * (1 + i * 0.2)
                rotated_x = expanded_x * cos_angle - expanded_y * sin_angle
                rotated_y = expanded_x * sin_angle + expanded_y * cos_angle
                glow_corners.append((center_x + rotated_x, center_y + rotated_y))

            pygame.draw.polygon(screen, glow_color, glow_corners)

        # 四角形を描画
        pygame.draw.polygon(screen, base_color, rotated_corners)

        # より太い輪郭を描画
        if alpha_factor > 0.3:
            outline_color = (255, 255, 100) if alpha_factor > 0.7 else (255, 200, 100)
            pygame.draw.polygon(screen, outline_color, rotated_corners, 4)

        # 火花エフェクトを追加
        if alpha_factor > 0.5:
            for i in range(6):
                spark_angle = self.rotation_angle + i * 60
                spark_distance = 30 + random.randint(-10, 10)
                spark_x = center_x + math.cos(math.radians(spark_angle)) * spark_distance
                spark_y = center_y + math.sin(math.radians(spark_angle)) * spark_distance
                pygame.draw.circle(screen, (255, 255, 150), (int(spark_x), int(spark_y)), 3)


class Slime:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.form = 1  # 1: 小さい, 2: 中間, 3: 大きい, 4: 紫（超巨大）
        self.has_been_red = False  # 一度赤くなったかのフラグ
        self.invincible_timer = 0
        self.purple_timer = 0  # 紫りんご効果の時間
        self.purple_invincible = False
        self.sparkle_particles = []
        self.can_deflect = False
        self.deflect_timer = 0
        self.direction = 1  # 1: 右向き, -1: 左向き
        self.shoot_cooldown = 0
        self.speed = 5
        self.jump_power = -18
        self.gravity = 0.8

        # 二段ジャンプ機能
        self.double_jump_count = 0  # 持っている二段ジャンプの回数
        self.can_double_jump = False  # 現在の空中で二段ジャンプが可能か
        self.jump_key_pressed = False  # ジャンプキーの状態管理

        # 回転飛行用の変数
        self.is_flying = False
        self.fly_velocity_x = 0
        self.fly_velocity_y = 0
        self.rotation_angle = 0
        self.fly_timer = 0

        # 初期rect設定
        width = int(40 * (1 + (self.form - 1) * 0.4))
        height = int(40 * (1 + (self.form - 1) * 0.4))
        self.rect = pygame.Rect(self.x, self.y, width, height)

    def eat_apple(self, apple):
        """りんごを食べる処理"""
        if apple.type == "red":
            # 通常の成長（3つ目で赤になる）
            if self.form == 1:
                self.form = 2
            elif self.form == 2:
                self.form = 3
                self.has_been_red = True  # 3つ目で赤フラグON
        elif apple.type == "blue":
            # 青りんごで即座に第三形態
            self.form = 3
            self.can_deflect = True
            self.deflect_timer = 300  # 5秒
        elif apple.type == "green":
            # 緑りんごでエイリアン全消去
            return "destroy_all_aliens"
        elif apple.type == "purple":
            # 紫りんごで超巨大フォーム
            self.form = 4
            self.purple_timer = 300  # 5秒間（60FPS * 5）
            self.purple_invincible = True
            purple_apple_sound.play()  # 効果音再生
        elif apple.type == "brown":
            # 茶色りんごで二段ジャンプ追加
            self.double_jump_count += 1
            # 地面にいる場合は即座に二段ジャンプ可能にする
            if self.on_ground:
                self.can_double_jump = self.double_jump_count > 0
            print(
                f"Brown apple eaten! double_jump_count: {self.double_jump_count}, can_double_jump: {self.can_double_jump}, on_ground: {self.on_ground}"
            )
            return "double_jump_gained"

        return None

    def update(self, platforms, flying_platforms_list=None):
        # 飛行中の処理
        if self.is_flying:
            # 回転角度を更新（より高速回転）
            self.rotation_angle += 20  # 20度ずつ回転でより派手に
            if self.rotation_angle >= 360:
                self.rotation_angle -= 360

            # 飛行移動
            self.x += self.fly_velocity_x
            self.y += self.fly_velocity_y

            # 飛行タイマー減少
            self.fly_timer -= 1
            if self.fly_timer <= 0:
                self.is_flying = False
                self.rotation_angle = 0
                self.velocity_y = 0  # 飛行終了時は落下開始

                # 飛行終了時に地面に埋まらないように位置を調整
                if self.form == 4:
                    width = int(40 * 8.0)
                    height = int(40 * 8.0)
                else:
                    width = int(40 * (1 + (self.form - 1) * 0.4))
                    height = int(40 * (1 + (self.form - 1) * 0.4))

                if self.y + height > SCREEN_HEIGHT - 20:
                    self.y = SCREEN_HEIGHT - 20 - height
        else:
            # 通常の移動処理
            keys = pygame.key.get_pressed()

            # 紫フォームの場合は自動で右に移動
            if self.form == 4:
                self.velocity_x = self.speed * 1.5  # 通常より早く移動
                self.direction = 1
            elif keys[pygame.K_LEFT]:
                self.velocity_x = -self.speed
                self.direction = -1
            elif keys[pygame.K_RIGHT]:
                self.velocity_x = self.speed
                self.direction = 1
            else:
                self.velocity_x = 0

            # ジャンプ処理（改良版）- 紫フォーム時はジャンプ禁止
            jump_key_current = keys[pygame.K_UP]

            if jump_key_current and not self.jump_key_pressed and self.form != 4:
                # ジャンプキーが新たに押された（紫フォーム以外）
                print(
                    f"Jump key pressed! on_ground: {self.on_ground}, form: {self.form}, can_double_jump: {self.can_double_jump}, double_jump_count: {self.double_jump_count}"
                )
                if self.on_ground:
                    # 地面にいる場合は必ず通常のジャンプ
                    self.velocity_y = self.jump_power
                    self.on_ground = False
                    self.can_double_jump = self.double_jump_count > 0
                    print(
                        f"Normal jump performed, can_double_jump: {self.can_double_jump}, count: {self.double_jump_count}"
                    )
                elif self.can_double_jump and self.double_jump_count > 0 and not self.on_ground:
                    # 空中にいて、二段ジャンプが可能な場合のみ二段ジャンプ
                    self.velocity_y = self.jump_power
                    self.double_jump_count -= 1
                    self.can_double_jump = False
                    double_jump_sound.play()  # 効果音再生
                    print(f"Double jump used! Remaining: {self.double_jump_count}")
                else:
                    print("Jump failed - conditions not met")
            elif jump_key_current and self.form == 4:
                print("Jump blocked - purple form")

            self.jump_key_pressed = jump_key_current

            # 重力
            self.velocity_y += self.gravity

            # 移動
            self.x += self.velocity_x
            self.y += self.velocity_y

        # rectを更新（紫フォーム時の正確なサイズ計算）
        if self.form == 4:
            width = int(40 * 8.0)  # さらに巨大化
            height = int(40 * 8.0)
        else:
            width = int(40 * (1 + (self.form - 1) * 0.4))
            height = int(40 * (1 + (self.form - 1) * 0.4))
        self.rect = pygame.Rect(self.x, self.y, width, height)

        # プラットフォームとの衝突（飛行中は無視）
        if not self.is_flying:
            # 現在のon_groundの状態を保持（地面の判定で上書きされる可能性があるため）
            current_on_ground = self.on_ground

            for platform in platforms[:]:  # スライスを作成して安全にイテレート
                if self.rect.colliderect(platform.rect):
                    # トゲプラットフォームかどうかを確認
                    if hasattr(platform, "is_spiked") and platform.is_spiked:
                        # トゲプラットフォームの場合、トゲに触れたかどうかを確認
                        platform_top = platform.rect.top
                        slime_bottom = self.rect.bottom
                        spike_height = 12  # SpikedPlatformと同じ値

                        # スライムがトゲの高さ範囲内に触れた場合
                        if slime_bottom >= platform_top - spike_height and slime_bottom <= platform_top + 5:
                            print("SPIKE DAMAGE! Game Over!")
                            spike_damage_sound.play()  # トゲダメージ効果音を再生
                            return "game_over"  # ゲームオーバーシグナルを返す

                        # トゲに触れていない場合は通常の着地判定
                        if (
                            slime_bottom >= platform_top - 5
                            and slime_bottom <= platform_top + 15
                            and self.velocity_y >= -2
                        ):
                            self.y = platform_top - height
                            self.rect.y = self.y
                            if self.velocity_y > 0:
                                self.velocity_y = 0
                            self.on_ground = True
                            self.can_double_jump = self.double_jump_count > 0
                            if self.double_jump_count > 0:
                                print(
                                    f"Spiked platform landing: can_double_jump set to True, count: {self.double_jump_count}"
                                )
                            break
                    # 紫フォームでプラットフォームに当たった場合、回転飛行開始
                    elif self.form == 4:
                        # 右上方向（-30度から60度）にランダムに飛ぶ
                        angle = random.uniform(-30, 60)
                        angle_rad = math.radians(angle)
                        speed = 25  # 飛行速度を上げる
                        self.fly_velocity_x = math.cos(angle_rad) * speed
                        self.fly_velocity_y = math.sin(angle_rad) * speed
                        self.is_flying = True
                        self.fly_timer = 120  # 2秒間飛行

                        # プラットフォームを飛ばす
                        if flying_platforms_list is not None:
                            # プラットフォームを右方向（-15度から45度）に飛ばす
                            platform_angle = random.uniform(-15, 45)
                            flying_platform = FlyingPlatform(platform, platform_angle)
                            flying_platforms_list.append(flying_platform)
                            platforms.remove(platform)  # 元のプラットフォームを削除

                        print(
                            f"MEGA PURPLE SMASH! Slime bounced at {angle:.1f} degrees! Platform launched at {platform_angle:.1f} degrees!"
                        )
                        break
                    else:
                        # 通常の場合：より寛容な着地判定
                        platform_top = platform.rect.top
                        slime_bottom = self.rect.bottom

                        # プラットフォームの上に乗っている、または落下中でプラットフォームに近い場合
                        if (
                            slime_bottom >= platform_top - 5
                            and slime_bottom <= platform_top + 15
                            and self.velocity_y >= -2
                        ):  # ジャンプ直後でなければ
                            self.y = platform_top - height
                            self.rect.y = self.y
                            if self.velocity_y > 0:  # 落下中の場合のみ速度を0にする
                                self.velocity_y = 0
                            self.on_ground = True
                            # 地面に着地した時に二段ジャンプをリセット
                            self.can_double_jump = self.double_jump_count > 0
                            if self.double_jump_count > 0:
                                print(f"Platform landing: can_double_jump set to True, count: {self.double_jump_count}")
                            break  # 一つのプラットフォームに着地したら他は確認しない

        # 左の壁
        if self.x < 0:
            self.x = 0

        # 地面との衝突判定
        if self.y + height >= SCREEN_HEIGHT - 20:
            self.y = SCREEN_HEIGHT - 20 - height
            if self.velocity_y > 0:  # 落下中のみ着地とする
                self.velocity_y = 0
                if not self.on_ground:
                    print("Landed on ground!")
                self.on_ground = True
                # 地面に着地した時に二段ジャンプをリセット
                self.can_double_jump = self.double_jump_count > 0
                if self.double_jump_count > 0:
                    print(f"Ground landing: can_double_jump set to True, count: {self.double_jump_count}")

        # 紫フォームのタイマー更新
        if self.purple_timer > 0:
            self.purple_timer -= 1
            # キラキラパーティクル生成
            if self.purple_timer % 5 == 0:
                for _ in range(5):
                    particle = {
                        "x": self.x + random.randint(-20, 20),
                        "y": self.y + random.randint(-20, 20),
                        "life": 30,
                        "vx": random.uniform(-2, 2),
                        "vy": random.uniform(-2, 2),
                    }
                    self.sparkle_particles.append(particle)

            if self.purple_timer <= 0:
                old_height = height
                self.form = 3 if self.has_been_red else 1
                self.purple_invincible = False

                # フォーム変更後の新しいサイズを計算
                new_width = int(40 * (1 + (self.form - 1) * 0.4))
                new_height = int(40 * (1 + (self.form - 1) * 0.4))

                # 地面に埋まらないように位置を調整
                if self.y + new_height > SCREEN_HEIGHT - 20:
                    self.y = SCREEN_HEIGHT - 20 - new_height

                # rectも即座に更新
                self.rect = pygame.Rect(self.x, self.y, new_width, new_height)

        # デフレクトタイマー更新
        if self.deflect_timer > 0:
            self.deflect_timer -= 1
            if self.deflect_timer <= 0:
                self.can_deflect = False

        # キラキラパーティクルの更新
        for particle in self.sparkle_particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.sparkle_particles.remove(particle)

        # 射撃クールダウン
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def deflect_bullet(self, bullet):
        """弾をランダムな方向にはじき返す"""
        if not self.can_deflect:
            return None

        # ランダムな角度（0-360度）
        deflect_angle = random.uniform(0, 2 * math.pi)

        # はじき返された弾を作成
        deflected = DeflectedBullet(bullet.x, bullet.y, deflect_angle)

        print("Bullet deflected!")
        return deflected

    def take_damage(self):
        """エイリアンの弾に当たった時の処理"""
        # 紫フォームの無敵時間中はダメージを受けない
        if self.purple_invincible:
            return False

        # デフレクト中もダメージを受けない
        if self.can_deflect:
            return False

        if self.form == 4:
            # 紫フォームから第三形態に戻る
            self.form = 3 if self.has_been_red else 1
            self.purple_timer = 0
            self.purple_invincible = False

            # フォーム変更後の新しいサイズを計算
            new_width = int(40 * (1 + (self.form - 1) * 0.4))
            new_height = int(40 * (1 + (self.form - 1) * 0.4))

            # 地面に埋まらないように位置を調整
            if self.y + new_height > SCREEN_HEIGHT - 20:
                self.y = SCREEN_HEIGHT - 20 - new_height

            # rectも即座に更新
            self.rect = pygame.Rect(self.x, self.y, new_width, new_height)
            return False
        elif self.form > 1:
            # サイズを小さくする（色は維持）
            self.form -= 1
            return False  # まだ生きている
        else:
            # 最小サイズでダメージを受けたらゲームオーバー
            return True

    def reset(self):
        self.x = 100
        self.y = SCREEN_HEIGHT - 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.form = 1
        self.has_been_red = False
        self.invincible_timer = 0
        self.purple_timer = 0
        self.purple_invincible = False
        self.sparkle_particles = []
        self.can_deflect = False
        self.deflect_timer = 0
        self.direction = 1
        self.shoot_cooldown = 0
        # 二段ジャンプのリセット
        self.double_jump_count = 0
        self.can_double_jump = False
        self.jump_key_pressed = False
        width = int(40 * (1 + (self.form - 1) * 0.4))
        height = int(40 * (1 + (self.form - 1) * 0.4))
        self.rect = pygame.Rect(self.x, self.y, width, height)

    def shoot(self, up_direction=False):
        if self.shoot_cooldown > 0:
            return None

        # 弾の設定を決定
        if self.form == 4:  # 紫フォーム
            self.shoot_cooldown = 30  # 普通のクールダウン
            is_big = True  # 紫フォームは大きい弾
        elif self.can_deflect:  # 青色状態（青りんご効果）
            self.shoot_cooldown = 5  # 高速連射
            is_big = False  # 青状態は通常サイズの弾
        elif self.form == 3:  # 第三形態（通常赤）
            self.shoot_cooldown = 15  # 中程度のクールダウン
            is_big = False
        else:
            self.shoot_cooldown = 30  # 普通のクールダウン
            is_big = False

        if up_direction:
            # 上方向の弾
            bullet_x = self.x + self.rect.width // 2
            bullet_y = self.y
            projectile = Projectile(bullet_x, bullet_y, 0, self.form, is_big)  # 上方向（direction=0で上向きを示す）
            # 上方向の弾は上向きに設定
            projectile.velocity_x = 0
            projectile.velocity_y = -projectile.speed
            print("Shooting upward!")
        else:
            # 通常の左右方向の弾
            bullet_x = self.x + (self.rect.width if self.direction > 0 else 0)
            projectile = Projectile(bullet_x, self.y + self.rect.height // 2, self.direction, self.form, is_big)

        # 青色状態の場合、弾の色を青色に変更
        if self.can_deflect:
            projectile.color = (100, 150, 255)  # 青色

        return projectile

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y

        # 元のサイズ計算システムに戻す
        width = int(40 * (1 + (self.form - 1) * 0.4))
        height = int(40 * (1 + (self.form - 1) * 0.4))

        # 紫フォームは超巨大に
        if self.form == 4:
            width = int(40 * 8.0)  # さらに巨大化
            height = int(40 * 8.0)

        # 飛行中の回転エフェクト
        if self.is_flying and self.form == 4:
            # 回転中は少し光らせる
            pulse_intensity = (math.sin(time.time() * 20) + 1) / 2
            glow_size = width * (1.8 + pulse_intensity * 0.8)

            for i in range(8):
                ring_size = glow_size * (1 + i * 0.1)
                alpha_factor = (8 - i) / 8
                ring_color = (int(255 * alpha_factor), int(100 * alpha_factor), int(255 * alpha_factor))
                # 回転角度を適用して描画位置をずらす
                offset_x = math.cos(math.radians(self.rotation_angle + i * 45)) * 10
                offset_y = math.sin(math.radians(self.rotation_angle + i * 45)) * 10
                pygame.draw.circle(
                    screen,
                    ring_color,
                    (int(screen_x + width // 2 + offset_x), int(screen_y + height // 2 + offset_y)),
                    int(ring_size // 2),
                    4,
                )

        # 色を決定
        if self.form == 4:  # 紫フォーム
            color = (128, 0, 128)
            eye_color = (255, 255, 0)
        elif self.form >= 3 and self.has_been_red:  # 3つ以上食べた場合のみ赤
            color = RED
            eye_color = YELLOW
        elif self.can_deflect:  # 青りんご効果（第三形態）
            color = BLUE
            eye_color = YELLOW
        else:
            color = GREEN
            eye_color = WHITE

        center_x = screen_x + width // 2
        center_y = screen_y + height // 2

        # 紫フォームの光エフェクト
        if self.form == 4:
            pulse_intensity = (math.sin(time.time() * 10) + 1) / 2
            glow_size = width * (1.5 + pulse_intensity * 0.5)

            for i in range(5):
                ring_size = glow_size * (1 + i * 0.15)
                alpha_factor = (5 - i) / 5
                ring_color = (int(255 * alpha_factor), int(0 * alpha_factor), int(255 * alpha_factor))
                pygame.draw.circle(screen, ring_color, (int(center_x), int(center_y)), int(ring_size // 2), 3)

        # 第三形態の青い光エフェクト
        elif self.can_deflect:
            pulse_intensity = (math.sin(time.time() * 8) + 1) / 2
            glow_size = width * (1.2 + pulse_intensity * 0.3)

            for i in range(3):
                ring_size = glow_size * (1 + i * 0.1)
                alpha_factor = (3 - i) / 3
                ring_color = (int(100 * alpha_factor), int(150 * alpha_factor), int(255 * alpha_factor))
                pygame.draw.circle(screen, ring_color, (int(center_x), int(center_y)), int(ring_size // 2), 2)

        # スライムの本体（元の楕円形に戻す）
        base_width = width * 0.9
        base_height = height * 0.9
        base_rect = pygame.Rect(center_x - base_width // 2, center_y - base_height // 2, base_width, base_height)
        pygame.draw.ellipse(screen, color, base_rect)

        # 下部のつぶれた部分
        bottom_width = base_width * 1.1
        bottom_height = base_height * 0.3
        bottom_rect = pygame.Rect(
            center_x - bottom_width // 2, center_y + base_height // 4, bottom_width, bottom_height
        )
        pygame.draw.ellipse(screen, color, bottom_rect)

        # バブル（3つ）- 元のスタイルに戻す
        bubble_flip = self.direction
        bubbles = [
            (center_x - base_width * 0.2 * bubble_flip, center_y - base_height * 0.1, base_width * 0.15),
            (center_x + base_width * 0.15 * bubble_flip, center_y - base_height * 0.25, base_width * 0.12),
            (center_x + base_width * 0.05 * bubble_flip, center_y + base_height * 0.15, base_width * 0.1),
        ]

        for bubble_x, bubble_y, bubble_size in bubbles:
            pygame.draw.circle(screen, WHITE, (int(bubble_x), int(bubble_y)), int(bubble_size))
            pygame.draw.circle(
                screen,
                WHITE,
                (int(bubble_x - bubble_size * 0.3 * bubble_flip), int(bubble_y - bubble_size * 0.3)),
                int(bubble_size * 0.4),
            )

        # 目
        eye_offset = base_width // 6
        if self.direction == 1:
            left_eye_x = center_x - eye_offset
            right_eye_x = center_x + eye_offset
        else:
            left_eye_x = center_x + eye_offset
            right_eye_x = center_x - eye_offset

        eye_y = center_y - base_height // 8
        eye_radius = max(3, int(base_width // 10))

        pygame.draw.circle(screen, eye_color, (int(left_eye_x), int(eye_y)), eye_radius)
        pygame.draw.circle(screen, eye_color, (int(right_eye_x), int(eye_y)), eye_radius)

        # 瞳
        pupil_radius = max(1, eye_radius // 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(left_eye_x), int(eye_y)), pupil_radius)
        pygame.draw.circle(screen, (0, 0, 0), (int(right_eye_x), int(eye_y)), pupil_radius)

        # 紫フォームのキラキラパーティクル
        if self.form == 4:
            for particle in self.sparkle_particles:
                alpha = min(255, particle["life"] * 8)
                size = max(1, particle["life"] // 10)
                sparkle_color = (255, 0, 255)
                particle_x = particle["x"] - camera.x
                particle_y = particle["y"]
                if 0 <= particle_x < SCREEN_WIDTH and 0 <= particle_y < SCREEN_HEIGHT:
                    pygame.draw.circle(screen, sparkle_color, (int(particle_x), int(particle_y)), size)


class AppleGenerator:
    def __init__(self):
        self.apples = []
        self.last_apple_x = 0
        self.apple_spacing = 200

    def generate_apples(self, camera_x):
        # カメラの右端から少し先まで生成
        target_x = camera_x + SCREEN_WIDTH + 500

        while self.last_apple_x < target_x:
            # プラットフォームの上にりんごを配置
            platform_y = random.randint(200, 450)
            apple_x = self.last_apple_x + random.randint(150, 300)
            apple_y = platform_y - 50

            # りんごの種類を決定
            rand = random.random()
            if rand < 0.02:  # 2%の確率で紫りんご
                apple_type = "purple"
            elif rand < 0.07:  # 5%の確率で緑りんご
                apple_type = "green"
            elif rand < 0.17:  # 10%の確率で茶色りんご
                apple_type = "brown"
            elif rand < 0.42:  # 25%の確率で青りんご
                apple_type = "blue"
            else:  # 残り58%で赤りんご
                apple_type = "red"

            apple = Apple(apple_x, apple_y, apple_type)
            self.apples.append(apple)
            self.last_apple_x = apple_x

    def update(self, camera_x):
        self.generate_apples(camera_x)

        # 画面外の古いりんごを削除
        self.apples = [apple for apple in self.apples if apple.x > camera_x - 200]

        # りんごを更新
        for apple in self.apples:
            apple.update()

    def draw(self, screen, camera):
        for apple in self.apples:
            apple.draw(screen, camera)

    def reset(self):
        self.apples = []
        self.last_apple_x = 0

    def generate_apple(self, x):
        """新しいりんごを生成"""
        apple_type = "red"
        rand = random.random()
        if rand < 0.02:  # 2%の確率で紫りんご
            apple_type = "purple"
        elif rand < 0.07:  # 5%の確率で緑りんご
            apple_type = "green"
        elif rand < 0.17:  # 10%の確率で茶色りんご
            apple_type = "brown"
        elif rand < 0.42:  # 25%の確率で青りんご
            apple_type = "blue"

        y = random.randint(150, 400)
        return Apple(x, y, apple_type)


class DeflectedBullet:
    def __init__(self, x, y, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 12
        # 速度を反転してランダムな角度で跳ね返す
        angle = random.uniform(-45, 45)
        self.vx = math.cos(math.radians(angle)) * self.speed
        self.vy = math.sin(math.radians(angle)) * self.speed
        self.active = True
        self.color = (255, 100, 255)  # ピンク色（はじき返された弾）
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.creation_time = time.time()
        self.lifetime = 3.0  # 3秒で消える

    def update(self):
        if time.time() - self.creation_time > self.lifetime:
            self.active = False
            return

        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius

    def draw(self, screen, camera):
        if self.active:
            screen_x = self.x - camera.x
            screen_y = self.y
            if screen_x > -50 and screen_x < SCREEN_WIDTH + 50:
                # はじき返された弾の特別なエフェクト
                pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)
                pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), self.radius // 2)

                # 回転するキラキラエフェクト
                for i in range(4):
                    sparkle_angle = (time.time() * 10 + i * 1.57) % (2 * math.pi)
                    sparkle_x = screen_x + math.cos(sparkle_angle) * (self.radius + 3)
                    sparkle_y = screen_y + math.sin(sparkle_angle) * (self.radius + 3)
                    pygame.draw.circle(screen, (255, 200, 255), (int(sparkle_x), int(sparkle_y)), 2)


# 画面フラッシュエフェクトクラス
class ScreenFlash:
    def __init__(self, duration=12):  # 0.2秒 (60FPS * 0.2)
        self.duration = duration
        self.timer = 0  # 初期状態では非表示
        self.alpha = 0

    def trigger(self):
        """フラッシュエフェクトを発動"""
        self.timer = self.duration
        self.alpha = 255

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            self.alpha = int(255 * (self.timer / self.duration))
            return True
        return False

    def draw(self, screen):
        if self.timer > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(self.alpha)
            screen.blit(flash_surface, (0, 0))


# ゲームオーバー画面クラス
class GameOverScreen:
    def __init__(self):
        self.active = False
        self.timer = 0

    def activate(self):
        self.active = True
        self.timer = 0

    def update(self):
        if self.active:
            self.timer += 1

            # 5秒後にリセット
            if self.timer >= 300:  # 5秒
                return True
        return False

    def draw(self, screen, font):
        if self.active:
            # 背景を半透明にする
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # GAME OVERテキストを中央に表示
            text = font.render("GAME OVER", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)


def draw_score(screen, score):
    score_text = font.render(f"スコア: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))


def draw_ui(screen, score, slime):
    # スコア表示
    score_text = font.render(f"スコア: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # 二段ジャンプ情報表示
    if slime.double_jump_count > 0:
        # スコアテキストの右端座標を取得
        score_width = score_text.get_width()

        # 「二段ジャンプ」テキスト
        jump_text = font.render("二段ジャンプ", True, WHITE)
        jump_x = 10 + score_width + 20  # スコアから20ピクセル離す
        screen.blit(jump_text, (jump_x, 10))

        # 茶色りんごアイコン（小さくて取れないもの）
        jump_text_width = jump_text.get_width()
        apple_x = jump_x + jump_text_width + 10
        apple_y = 10 + 5  # 少し下にずらしてバランスを取る
        apple_size = 15  # 小さなサイズ

        # 茶色りんごを描画
        pygame.draw.circle(screen, BROWN, (apple_x + apple_size // 2, apple_y + apple_size // 2), apple_size // 2)
        # ハイライト
        highlight_color = tuple(min(255, c + 50) for c in BROWN)
        pygame.draw.circle(
            screen, highlight_color, (apple_x + apple_size // 2 - 2, apple_y + apple_size // 2 - 2), apple_size // 4
        )
        # 葉っぱ
        leaf_points = [
            (apple_x + apple_size // 2 + 1, apple_y + 1),
            (apple_x + apple_size // 2 + 4, apple_y - 1),
            (apple_x + apple_size // 2 + 3, apple_y + 2),
            (apple_x + apple_size // 2 + 1, apple_y + 3),
        ]
        pygame.draw.polygon(screen, (0, 150, 0), leaf_points)

        # 残り回数をりんごの右に表示
        count_text = font.render(f"×{slime.double_jump_count}", True, WHITE)
        count_x = apple_x + apple_size + 5
        screen.blit(count_text, (count_x, 10))

    # 紫状態のタイマー表示
    if slime.form == 4 and slime.purple_timer > 0:
        # 残り時間を秒単位で計算（小数点第1位まで）
        remaining_seconds = slime.purple_timer / 60.0
        purple_text = font.render(f"紫状態: {remaining_seconds:.1f}秒", True, (255, 100, 255))
        screen.blit(purple_text, (10, 50))  # スコアの下に表示


# ゲームのメインループ
async def main():
    clock = pygame.time.Clock()
    frame_count = 0

    # ゲーム状態の管理
    game_state = GameState()

    # カメラとプラットフォーム生成器
    camera = Camera()
    platform_generator = PlatformGenerator()
    alien_generator = AlienGenerator()

    # スライムのインスタンスを作成
    slime = Slime(100, SCREEN_HEIGHT - 100)

    # 弾のリスト
    projectiles = []
    alien_bullets = []
    deflected_bullets = []  # はじき返された弾

    # 大爆発エフェクトのリスト
    big_explosions = []

    # 飛んでいくプラットフォームのリスト
    flying_platforms = []

    # りんごの生成器
    apple_generator = AppleGenerator()

    # 画面フラッシュエフェクト
    screen_flash = ScreenFlash()

    # ゲームオーバー画面
    game_over_screen = GameOverScreen()

    print("Game started! Left/Right arrows to move, UP arrow to jump, SPACE to shoot")

    # BGMを開始（ループ再生）
    bgm_channel = pygame.mixer.Channel(0)
    bgm_channel.play(bgm, loops=-1)  # 無限ループ
    print(f"BGM started - volume: {bgm.get_volume()}")

    while True:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # ゲームオーバー状態の確認
            if game_state.should_reset():
                # ゲームリセット
                game_state.reset()
                camera.reset()
                platform_generator.reset()
                alien_generator.reset()
                slime.reset()
                projectiles = []
                alien_bullets = []
                deflected_bullets = []
                big_explosions = []
                flying_platforms = []  # 飛んでいくプラットフォームもリセット
                apple_generator.reset()
                screen_flash = ScreenFlash()  # フラッシュをリセット
                game_over_screen = GameOverScreen()

            if not game_state.game_over:
                keys = pygame.key.get_pressed()

                # スライムの移動とアップデート
                result = slime.update(platform_generator.platforms, flying_platforms)
                if result == "game_over":
                    print("SPIKE DAMAGE! Game Over triggered!")
                    big_explosions.append(
                        BigExplosion(slime.x + slime.rect.width // 2, slime.y + slime.rect.height // 2)
                    )
                    game_state.trigger_game_over()
                    game_over_screen.activate()

                # カメラの更新
                camera.update(slime.x)

                # プラットフォームの生成と削除
                platform_generator.update(camera.x)

                # エイリアンの生成と削除
                alien_generator.update(camera.x)

                # エイリアンの更新
                for alien in alien_generator.aliens:
                    alien.update()

                # りんごの更新
                apple_generator.update(camera.x)
                for apple in apple_generator.apples:
                    apple.update()

                # 飛んでいくプラットフォームの更新
                for flying_platform in flying_platforms[:]:
                    flying_platform.update()
                    if not flying_platform.active:
                        flying_platforms.remove(flying_platform)

                # エイリアンの攻撃
                if alien_generator.should_attack():
                    bullets_created = 0
                    for alien in alien_generator.get_active_aliens():
                        bullets = alien.shoot(slime.x, slime.y)  # スライムの位置を渡す
                        if bullets:
                            for bullet in bullets:
                                alien_bullets.append(bullet)
                                bullets_created += 1

                # スライムの弾の発射
                if keys[pygame.K_SPACE] and slime.shoot_cooldown <= 0:
                    # 上矢印キー+スペースキーで上方向射撃
                    if keys[pygame.K_UP]:
                        projectile = slime.shoot(up_direction=True)
                    else:
                        projectile = slime.shoot()
                    if projectile:
                        projectiles.append(projectile)

                # スライムの弾の更新
                for projectile in projectiles[:]:
                    projectile.move()
                    projectile.update()

                    # エイリアンとの衝突判定
                    for alien in alien_generator.aliens:
                        if alien.alive and projectile.active and projectile.rect.colliderect(alien.rect):
                            if projectile.is_big:  # 紫フォームの超大弾
                                # 超大爆発
                                big_explosions.append(
                                    BigExplosion(alien.x + alien.width // 2, alien.y + alien.height // 2)
                                )
                                big_explosions.append(BigExplosion(projectile.x, projectile.y))
                                print("Super massive explosion!")
                            else:
                                big_explosions.append(
                                    BigExplosion(alien.x + alien.width // 2, alien.y + alien.height // 2)
                                )

                            # エイリアンを破壊し、赤いエイリアンの場合は4体分裂
                            destroy_result = alien.destroy()
                            if destroy_result.get("destroyed", False):
                                spawn_aliens = destroy_result.get("spawn_aliens", [])
                                if spawn_aliens:
                                    print(f"Red alien destroyed! Spawning {len(spawn_aliens)} aliens")
                                    for spawn_info in spawn_aliens:
                                        alien_type = spawn_info.get("type", "normal")

                                        # 画面の絶対座標に変換
                                        spawn_x = spawn_info["x"]
                                        spawn_y = spawn_info["y"]

                                        if spawn_x == "screen_right":
                                            spawn_x = camera.x + SCREEN_WIDTH - 100
                                        elif spawn_x == "screen_left":
                                            spawn_x = camera.x + 100

                                        if spawn_y == "screen_top":
                                            spawn_y = 50
                                        elif spawn_y == "screen_bottom":
                                            spawn_y = SCREEN_HEIGHT - 150

                                        alien_generator.add_alien(spawn_x, spawn_y, alien_type)

                            projectile.explode()
                            game_state.add_score()
                            break

                    if projectile.check_collision(platform_generator.platforms):
                        projectiles.remove(projectile)
                    elif projectile.can_penetrate:
                        # 貫通弾はより遠くまで飛ばす（通常の3倍の距離）
                        if projectile.x < camera.x - 600 or projectile.x > camera.x + SCREEN_WIDTH + 600:
                            projectiles.remove(projectile)
                        elif not projectile.active and (not projectile.explosion or not projectile.explosion.active):
                            projectiles.remove(projectile)
                    elif projectile.x < camera.x - 200 or projectile.x > camera.x + SCREEN_WIDTH + 200:
                        projectiles.remove(projectile)
                    elif not projectile.active and (not projectile.explosion or not projectile.explosion.active):
                        projectiles.remove(projectile)

                # エイリアンの弾を更新
                for bullet in alien_bullets[:]:
                    bullet.update()
                    if not bullet.active:
                        alien_bullets.remove(bullet)

                # りんごとの衝突判定
                for apple in apple_generator.apples[:]:
                    apple_rect = pygame.Rect(apple.x, apple.y, 30, 30)
                    if slime.rect.colliderect(apple_rect):
                        eat_sound.play()
                        effect = slime.eat_apple(apple)
                        apple.consumed = True
                        apple_generator.apples.remove(apple)

                        if effect == "destroy_all_aliens":
                            # 緑りんご効果：画面フラッシュ + 全エイリアン爆発
                            screen_flash = ScreenFlash()
                            green_apple_sound.play()

                            # 全エイリアンを爆発させる
                            for alien in alien_generator.aliens[:]:  # コピーを作成して安全にイテレート
                                if alien.alive:
                                    big_explosions.append(
                                        BigExplosion(alien.x + alien.width // 2, alien.y + alien.height // 2)
                                    )

                                    # エイリアンを破壊し、赤いエイリアンの場合は4体分裂
                                    destroy_result = alien.destroy()
                                    if destroy_result.get("destroyed", False):
                                        spawn_aliens = destroy_result.get("spawn_aliens", [])
                                        if spawn_aliens:
                                            print(
                                                f"Red alien destroyed by green apple! Spawning {len(spawn_aliens)} aliens"
                                            )
                                            for spawn_info in spawn_aliens:
                                                alien_type = spawn_info.get("type", "normal")

                                                # 画面の絶対座標に変換
                                                spawn_x = spawn_info["x"]
                                                spawn_y = spawn_info["y"]

                                                if spawn_x == "screen_right":
                                                    spawn_x = camera.x + SCREEN_WIDTH - 100
                                                elif spawn_x == "screen_left":
                                                    spawn_x = camera.x + 100

                                                if spawn_y == "screen_top":
                                                    spawn_y = 50
                                                elif spawn_y == "screen_bottom":
                                                    spawn_y = SCREEN_HEIGHT - 150

                                                alien_generator.add_alien(spawn_x, spawn_y, alien_type)

                                    game_state.add_score()
                        elif effect == "double_jump_gained":
                            # 茶色りんご効果：二段ジャンプ獲得
                            print(f"Brown apple collected! Double jumps: {slime.double_jump_count}")

                # 紫状態のスライムとエイリアンの直接衝突判定
                if slime.form == 4:  # 紫フォーム
                    for alien in alien_generator.aliens[:]:
                        if alien.alive and slime.rect.colliderect(alien.rect):
                            # 超巨大爆発
                            big_explosions.append(BigExplosion(alien.x + alien.width // 2, alien.y + alien.height // 2))
                            big_explosions.append(
                                BigExplosion(slime.x + slime.rect.width // 2, slime.y + slime.rect.height // 2)
                            )

                            # エイリアンを破壊し、赤いエイリアンの場合は4体分裂
                            destroy_result = alien.destroy()
                            if destroy_result.get("destroyed", False):
                                spawn_aliens = destroy_result.get("spawn_aliens", [])
                                if spawn_aliens:
                                    print(f"Red alien destroyed by purple slime! Spawning {len(spawn_aliens)} aliens")
                                    for spawn_info in spawn_aliens:
                                        alien_type = spawn_info.get("type", "normal")

                                        # 画面の絶対座標に変換
                                        spawn_x = spawn_info["x"]
                                        spawn_y = spawn_info["y"]

                                        if spawn_x == "screen_right":
                                            spawn_x = camera.x + SCREEN_WIDTH - 100
                                        elif spawn_x == "screen_left":
                                            spawn_x = camera.x + 100

                                        if spawn_y == "screen_top":
                                            spawn_y = 50
                                        elif spawn_y == "screen_bottom":
                                            spawn_y = SCREEN_HEIGHT - 150

                                        alien_generator.add_alien(spawn_x, spawn_y, alien_type)

                            game_state.add_score()
                            print("Purple slime destroyed alien with massive explosion!")
                            break

                # エイリアンの弾との衝突判定
                for bullet in alien_bullets[:]:
                    if bullet.active and slime.rect.colliderect(bullet.rect):
                        if slime.purple_invincible:
                            # 紫フォームで無敵の場合、弾を大爆発させる
                            big_explosions.append(BigExplosion(bullet.x, bullet.y))
                            bullet.active = False
                            alien_bullets.remove(bullet)
                            print("Purple invincibility blocked bullet!")
                        elif slime.can_deflect:
                            # デフレクト中の場合、弾をはじき返す
                            deflected_bullets.append(DeflectedBullet(bullet.x, bullet.y, bullet.vx, bullet.vy))
                            bullet.active = False
                            alien_bullets.remove(bullet)
                            print("Bullet deflected!")
                        else:
                            # 通常の場合、ダメージを受ける
                            print(f"Bullet hit slime! Form: {slime.form}")
                            if slime.take_damage():
                                print("GAME OVER triggered!")
                                big_explosions.append(
                                    BigExplosion(slime.x + slime.rect.width // 2, slime.y + slime.rect.height // 2)
                                )
                                game_state.trigger_game_over()
                                game_over_screen.activate()
                            else:
                                print(f"Slime damaged! New form: {slime.form}")
                            bullet.active = False
                            alien_bullets.remove(bullet)

                # はじき返された弾の更新
                for deflected in deflected_bullets[:]:
                    deflected.update()

                    # エイリアンとの衝突判定
                    if deflected.active:
                        for alien in alien_generator.aliens:
                            if alien.alive and deflected.rect.colliderect(alien.rect):
                                # はじき返された弾がエイリアンに当たったら大爆発
                                big_explosions.append(
                                    BigExplosion(alien.x + alien.width // 2, alien.y + alien.height // 2)
                                )
                                big_explosions.append(BigExplosion(deflected.x, deflected.y))  # 弾の位置でも爆発

                                # エイリアンを破壊し、赤いエイリアンの場合は4体分裂
                                destroy_result = alien.destroy()
                                if destroy_result.get("destroyed", False):
                                    spawn_aliens = destroy_result.get("spawn_aliens", [])
                                    if spawn_aliens:
                                        print(
                                            f"Red alien destroyed by deflected bullet! Spawning {len(spawn_aliens)} aliens"
                                        )
                                        for spawn_info in spawn_aliens:
                                            alien_type = spawn_info.get("type", "normal")

                                            # 画面の絶対座標に変換
                                            spawn_x = spawn_info["x"]
                                            spawn_y = spawn_info["y"]

                                            if spawn_x == "screen_right":
                                                spawn_x = camera.x + SCREEN_WIDTH - 100
                                            elif spawn_x == "screen_left":
                                                spawn_x = camera.x + 100

                                            if spawn_y == "screen_top":
                                                spawn_y = 50
                                            elif spawn_y == "screen_bottom":
                                                spawn_y = SCREEN_HEIGHT - 150

                                            alien_generator.add_alien(spawn_x, spawn_y, alien_type)

                                deflected.active = False
                                game_state.add_score()
                                print("Deflected bullet hit alien! Double explosion!")
                                break

                    # 画面外に出たか時間切れの弾を削除
                    if (
                        not deflected.active
                        or deflected.x < camera.x - 200
                        or deflected.x > camera.x + SCREEN_WIDTH + 200
                    ):
                        deflected_bullets.remove(deflected)

                # 画面のクリア
                screen.fill(BLACK)

                # 多重スクロール背景の描画
                if parallax_background:
                    parallax_background.update(camera.x)
                    parallax_background.draw(screen)

                if not game_state.game_over:
                    # 地面の描画（スクロールに対応）
                    ground_start_x = int(camera.x // 100) * 100 - 100
                    for i in range(ground_start_x, int(camera.x + SCREEN_WIDTH + 100), 100):
                        screen_x = i - camera.x
                        pygame.draw.rect(screen, BLUE, (screen_x, SCREEN_HEIGHT - 20, 100, 20))

                    # プラットフォームの描画
                    for platform in platform_generator.platforms:
                        platform.draw(screen, camera)

                    # りんごの描画
                    for apple in apple_generator.apples:
                        apple.draw(screen, camera)

                    # 弾の描画
                    for projectile in projectiles:
                        projectile.draw(screen, camera)

                    # エイリアンの弾の描画
                    for bullet in alien_bullets:
                        bullet.draw(screen, camera)

                    # はじき返された弾の描画
                    for deflected in deflected_bullets:
                        deflected.draw(screen, camera)

                    # エイリアンの描画
                    for alien in alien_generator.aliens:
                        alien.draw(screen, camera)

                    # 飛んでいくプラットフォームの描画
                    for flying_platform in flying_platforms:
                        flying_platform.draw(screen, camera)

                    # スライムの描画
                    slime.draw(screen, camera)

                # 大爆発エフェクトの更新と描画
                for big_explosion in big_explosions[:]:
                    big_explosion.update()
                    big_explosion.draw(screen, camera)
                    if not big_explosion.active:
                        big_explosions.remove(big_explosion)

                # UI描画
                draw_ui(screen, game_state.score, slime)

                # 画面フラッシュエフェクトの描画
                screen_flash.draw(screen)

                # ゲームオーバー画面の描画（ゲームオーバー時またはアクティブ時）
                if game_state.game_over or game_over_screen.active:
                    game_over_screen.draw(screen, big_font)

                # デバッグ情報
                frame_count += 1
                if frame_count % 120 == 0:  # 2秒に1回
                    active_aliens = len([alien for alien in alien_generator.aliens if alien.alive])
                    print(
                        f"FPS: {clock.get_fps():.1f}, Score: {game_state.score}, Aliens: {len(alien_generator.aliens)} (Active: {active_aliens}), Bullets: {len(alien_bullets)}, Apples: {len(apple_generator.apples)}, Flying Platforms: {len(flying_platforms)}"
                    )

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

        except Exception as e:
            print(f"Error occurred: {e}")
            import traceback

            traceback.print_exc()
            break


if __name__ == "__main__":
    asyncio.run(main())
