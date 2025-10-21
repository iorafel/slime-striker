import pygame
import sys
import random
import math
import time
import os
import traceback

print("Starting game initialization...")

try:
    # Pygameの初期化
    print("Initializing pygame...")
    pygame.init()
    pygame.mixer.init()  # サウンド用の初期化
    print("Pygame initialized successfully!")

    # 画面の設定
    print("Setting up display...")
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("My Pygame Game")
    print("Display setup complete!")

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

    # サウンドの読み込み
    print("Loading sounds...")
    try:
        eat_sound = pygame.mixer.Sound("pnyo.wav")
        eat_sound.set_volume(0.5)
        print("✓ pnyo.wav loaded")
    except Exception as e:
        print(f"⚠ Warning: pnyo.wav not found - {e}")
        eat_sound = pygame.mixer.Sound(buffer=bytes(0))

    try:
        alien_destroy_sound = pygame.mixer.Sound("alien_destroy.wav")
        alien_destroy_sound.set_volume(0.6)
        print("✓ alien_destroy.wav loaded")
    except Exception as e:
        print(f"⚠ Warning: alien_destroy.wav not found - {e}")
        alien_destroy_sound = pygame.mixer.Sound(buffer=bytes(0))

    try:
        explosion_sound = pygame.mixer.Sound("explosion.wav")
        explosion_sound.set_volume(0.4)
        print("✓ explosion.wav loaded")
    except Exception as e:
        print(f"⚠ Warning: explosion.wav not found - {e}")
        explosion_sound = pygame.mixer.Sound(buffer=bytes(0))

    print("All sounds loaded!")

    print("🎮 Game ready to start!")
    print("Controls:")
    print("- Arrow keys: Move slime")
    print("- Space: Jump")
    print("- Z: Shoot")
    print("- Close window to quit")
    print("\nStarting game loop...")

    # 簡単なテストループ
    clock = pygame.time.Clock()
    running = True
    frame_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Quit event received")
                running = False

        # 画面をクリア
        screen.fill(BLACK)
        
        # テスト用の文字を描画
        font = pygame.font.Font(None, 36)
        text = font.render("Game is working! Press ESC to close", True, WHITE)
        screen.blit(text, (50, 50))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            print("ESC pressed")
            running = False

        pygame.display.flip()
        clock.tick(60)

        frame_count += 1
        if frame_count % 60 == 0:
            print(f"Game running - FPS: {clock.get_fps():.1f}")

    print("Game ended normally")
    pygame.quit()

except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    print("Full traceback:")
    traceback.print_exc()
    
    input("Press Enter to exit...") 