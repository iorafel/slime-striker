# ゲームデータ永続化ガイド

## GitHub Pages の制限

- 静的ファイルのみ（HTML, CSS, JS, 画像等）
- サーバーサイド処理不可
- データベース接続不可
- ファイル書き込み不可

## 永続化の解決策

### 1. ローカルストレージ（推奨）

```javascript
// スコア保存
localStorage.setItem("alienGame_highScore", score);

// スコア読み込み
const highScore = localStorage.getItem("alienGame_highScore") || 0;

// 設定保存
const settings = {
  soundVolume: 0.8,
  difficulty: "normal",
  playerName: "Player1",
};
localStorage.setItem("alienGame_settings", JSON.stringify(settings));
```

### 2. IndexedDB（大容量データ）

```javascript
// ゲームセーブデータ、プレイ履歴等
const request = indexedDB.open("AlienGameDB", 1);
```

### 3. 外部 API 連携

```javascript
// Firebase Firestore（無料枠あり）
// Supabase（無料枠あり）
// JSONBin.io（シンプルなJSON保存）
```

### 4. URL パラメータ

```javascript
// シェア用のゲーム状態
const gameState = btoa(JSON.stringify(data));
const shareUrl = `${location.origin}?state=${gameState}`;
```

### 5. クラウドストレージ

- Google Drive API
- Dropbox API
- OneDrive API

## 実装例

### ローカルストレージ実装

```python
# pygbag用のJavaScript注入
async def save_score(score):
    import platform
    if platform.system() == "Emscripten":
        import asyncio
        await asyncio.create_subprocess_exec(
            "window.localStorage.setItem('score', arguments[0])",
            str(score)
        )
```

### Firebase 連携例

```html
<!-- build/web/index.html に追加 -->
<script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-firestore.js"></script>
```

## おすすめアプローチ

1. **ローカルストレージ**: 基本のスコア・設定保存
2. **Firebase**: オンラインランキング・マルチプレイ
3. **URL 共有**: ゲーム状態のシェア機能
