# Alien Game - ローカルストレージ実装例

## 基本的なスコア保存機能

```python
import asyncio
import json
import sys

class GameStorage:
    """ゲームデータの永続化クラス"""

    def __init__(self):
        self.high_score = 0
        self.settings = {
            'sound_volume': 0.7,
            'music_volume': 0.5,
            'player_name': 'Player'
        }
        self.load_data()

    def save_score(self, score):
        """スコアを保存"""
        if score > self.high_score:
            self.high_score = score
            self.save_data()

    def load_data(self):
        """データを読み込み"""
        if sys.platform == "emscripten":
            # Web版 - localStorage使用
            self._load_from_localStorage()
        else:
            # デスクトップ版 - ファイル使用
            self._load_from_file()

    def save_data(self):
        """データを保存"""
        if sys.platform == "emscripten":
            # Web版 - localStorage使用
            self._save_to_localStorage()
        else:
            # デスクトップ版 - ファイル使用
            self._save_to_file()

    def _load_from_localStorage(self):
        """localStorage からデータ読み込み（Web版）"""
        try:
            # JavaScriptのlocalStorageにアクセス
            import js
            data = js.localStorage.getItem('alienGame_data')
            if data:
                game_data = json.loads(data)
                self.high_score = game_data.get('high_score', 0)
                self.settings.update(game_data.get('settings', {}))
        except:
            pass

    def _save_to_localStorage(self):
        """localStorage にデータ保存（Web版）"""
        try:
            import js
            data = {
                'high_score': self.high_score,
                'settings': self.settings
            }
            js.localStorage.setItem('alienGame_data', json.dumps(data))
        except:
            pass

    def _load_from_file(self):
        """ファイルからデータ読み込み（デスクトップ版）"""
        try:
            with open('alien_save.json', 'r') as f:
                data = json.load(f)
                self.high_score = data.get('high_score', 0)
                self.settings.update(data.get('settings', {}))
        except FileNotFoundError:
            pass

    def _save_to_file(self):
        """ファイルにデータ保存（デスクトップ版）"""
        try:
            data = {
                'high_score': self.high_score,
                'settings': self.settings
            }
            with open('alien_save.json', 'w') as f:
                json.dump(data, f)
        except:
            pass

# ゲーム状態クラスに統合
class GameState:
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.storage = GameStorage()

    def add_score(self, points):
        """スコア追加"""
        self.score += points

    def trigger_game_over(self):
        """ゲームオーバー処理"""
        self.game_over = True
        self.storage.save_score(self.score)

    def get_high_score(self):
        """ハイスコア取得"""
        return self.storage.high_score

    def reset(self):
        """ゲームリセット"""
        self.score = 0
        self.game_over = False

# UI描画の更新
def draw_ui(screen, game_state, slime):
    """UI描画（ハイスコア表示付き）"""
    # 現在のスコア
    score_text = font.render(f"スコア: {game_state.score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # ハイスコア
    high_score_text = font.render(f"ハイスコア: {game_state.get_high_score()}", True, YELLOW)
    screen.blit(high_score_text, (10, 40))

    # その他のUI...
```

## Web 版での注意点

1. **pygbag 使用時**: `sys.platform == "emscripten"` で判定
2. **localStorage 制限**: ドメインごとに約 5-10MB まで
3. **非同期処理**: Web 版では`asyncio`が必須

## 実装のポイント

- **デュアル対応**: デスクトップと Web 両方で動作
- **エラーハンドリング**: ストレージアクセス失敗に対応
- **軽量データ**: JSON 形式で必要最小限のデータのみ

これで GitHub Pages 上でもスコアやゲーム設定が保存されます！
