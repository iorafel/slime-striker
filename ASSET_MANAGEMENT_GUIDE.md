# アセット管理ガイド - Claude との効果的なファイル名相談方法

## 🎯 最適なアプローチ：Claude 主導の指定方式

### **1. Claude 主導でファイル名を指定**

**✅ 良い例：**

```
Claude: 「以下のファイルを配置してください：
- `assets/backgrounds/sky_layer1.png` (1920x1080) - 最奥の雲
- `assets/backgrounds/sky_layer2.png` (1920x1080) - 中間の雲
- `assets/backgrounds/mountain_layer.png` (1920x1080) - 山々
- `assets/sprites/slime_idle.png` (64x64) - スライムのアイドル状態
- `assets/sprites/slime_jump.png` (64x64) - スライムのジャンプ状態
」

User: 「わかりました、その名前で配置します」
```

**❌ 避けるべき例：**

```
User: 「背景画像はどんな名前にしましょうか？」
Claude: 「お任せします」→ 曖昧で非効率
```

### **2. 統一的な命名規則を提示**

```
📁 alien/
├── assets/
│   ├── backgrounds/     # 背景画像
│   │   ├── sky_layer1.png      # 最奥レイヤー
│   │   ├── sky_layer2.png      # 中間レイヤー
│   │   └── ground_layer.png    # 地面レイヤー
│   ├── sprites/         # キャラクタースプライト
│   │   ├── slime_idle.png      # 待機状態
│   │   ├── slime_walk_1.png    # 歩行1
│   │   ├── slime_walk_2.png    # 歩行2
│   │   └── slime_jump.png      # ジャンプ
│   ├── effects/         # エフェクト
│   │   ├── explosion_1.png     # 爆発フレーム1
│   │   └── spark.png           # 火花
│   └── sounds/          # 音声（既存）
│       ├── pnyo.ogg
│       └── explosion.ogg
```

## 🎨 具体的な実装例

### **多重スクロール背景の実装**

```python
# assets/backgrounds/ に以下のファイルを配置してください：
# - sky_layer1.png (1920x1080) - 最奥の空・雲
# - sky_layer2.png (1920x1080) - 中間の雲
# - mountain_layer.png (1920x1080) - 山のシルエット
# - ground_layer.png (1920x1080) - 近景の地面・木々

class ParallaxBackground:
    def __init__(self):
        self.layers = []
        try:
            # 背景レイヤーを読み込み（エラーハンドリング付き）
            self.layers = [
                {
                    'image': pygame.image.load('assets/backgrounds/sky_layer1.png'),
                    'speed': 0.2,  # 最も遅い
                    'x': 0
                },
                {
                    'image': pygame.image.load('assets/backgrounds/sky_layer2.png'),
                    'speed': 0.4,
                    'x': 0
                },
                {
                    'image': pygame.image.load('assets/backgrounds/mountain_layer.png'),
                    'speed': 0.6,
                    'x': 0
                },
                {
                    'image': pygame.image.load('assets/backgrounds/ground_layer.png'),
                    'speed': 1.0,  # 最も速い
                    'x': 0
                }
            ]
        except pygame.error as e:
            print(f"Background images not found: {e}")
            print("Using solid color background")
            self.layers = []

    def update(self, camera_x):
        """カメラ移動に応じて背景を更新"""
        for layer in self.layers:
            layer['x'] = -camera_x * layer['speed']

    def draw(self, screen):
        """背景を描画"""
        if not self.layers:
            # 画像がない場合は単色背景
            screen.fill((50, 150, 200))  # 空色
            return

        for layer in self.layers:
            image = layer['image']
            x = layer['x'] % image.get_width()

            # 画像を繰り返し描画
            screen.blit(image, (x - image.get_width(), 0))
            screen.blit(image, (x, 0))
            if x + image.get_width() < SCREEN_WIDTH:
                screen.blit(image, (x + image.get_width(), 0))
```

### **スプライトアニメーション**

```python
# assets/sprites/ に以下のファイルを配置してください：
# - slime_idle.png (64x64) - 待機状態
# - slime_walk_1.png (64x64) - 歩行フレーム1
# - slime_walk_2.png (64x64) - 歩行フレーム2
# - slime_jump.png (64x64) - ジャンプ状態

class AnimatedSprite:
    def __init__(self):
        self.sprites = {}
        self.current_animation = 'idle'
        self.frame = 0
        self.animation_speed = 10

        try:
            self.sprites = {
                'idle': [pygame.image.load('assets/sprites/slime_idle.png')],
                'walk': [
                    pygame.image.load('assets/sprites/slime_walk_1.png'),
                    pygame.image.load('assets/sprites/slime_walk_2.png')
                ],
                'jump': [pygame.image.load('assets/sprites/slime_jump.png')]
            }
        except pygame.error as e:
            print(f"Sprite images not found: {e}")
            print("Using colored rectangles")
            self.sprites = None

    def set_animation(self, animation_name):
        if animation_name != self.current_animation:
            self.current_animation = animation_name
            self.frame = 0

    def update(self):
        if self.sprites and self.current_animation in self.sprites:
            frames = len(self.sprites[self.current_animation])
            self.frame = (self.frame + 1) % (frames * self.animation_speed)

    def draw(self, screen, x, y):
        if self.sprites and self.current_animation in self.sprites:
            frames = self.sprites[self.current_animation]
            frame_index = self.frame // self.animation_speed
            current_sprite = frames[frame_index % len(frames)]
            screen.blit(current_sprite, (x, y))
        else:
            # フォールバック: 色付き四角形
            pygame.draw.rect(screen, GREEN, (x, y, 64, 64))
```

## 📋 Claude との相談テンプレート

### **新機能追加時**

```
「◯◯機能を追加したいので、以下のアセットファイルを配置してください：

📁 必要なファイル：
- `assets/[カテゴリ]/[ファイル名]` (サイズ) - 用途説明

💡 ファイル仕様：
- 形式：PNG（透明度対応）
- サイズ：64x64ピクセル
- 背景：透明

🎨 デザイン要件：
- [具体的なデザイン要件]
」
```

### **既存機能改善時**

```
「現在の[機能名]を改善するため、以下のファイルを置き換えてください：

🔄 置き換え対象：
- 既存：`assets/old/file.png`
- 新規：`assets/new/file.png` - 改善内容

📝 変更理由：
- [改善の理由と効果]
」
```

## 🔄 実際の会話フロー例

**Claude:** 「多重スクロール背景を実装します。以下 4 つの PNG 画像ファイル（1920x1080）を `assets/backgrounds/` フォルダに配置してください：

1. `sky_layer1.png` - 最奥の空・薄い雲
2. `sky_layer2.png` - 中間の濃い雲
3. `mountain_layer.png` - 山のシルエット
4. `ground_layer.png` - 近景の木々・草

各レイヤーは異なる速度でスクロールし、立体感のある背景を作ります。」

**User:** 「わかりました。その名前で配置します。」

**Claude:** 「ありがとうございます。コードを実装しますので、ファイル配置後にテストしてください。画像がない場合でも動作するフォールバック機能も含めます。」

## ✅ このアプローチの利点

1. **明確性**: 具体的なファイル名・仕様を提示
2. **一貫性**: 統一された命名規則
3. **効率性**: 迷いなく作業を進められる
4. **保守性**: 後から見てもわかりやすい構成
5. **エラー対応**: ファイルがない場合の代替手段も提供
