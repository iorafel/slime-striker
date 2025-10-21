import numpy as np
import scipy.io.wavfile as wavfile

def generate_eat_sound():
    # サンプリングレート
    sample_rate = 44100
    
    # 音の長さ（秒）
    duration = 0.6
    
    # 時間軸の配列を作成
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # "ta-ta-ta-tan"のリズムを作成
    # 4つの音に分割
    segment_duration = duration / 4
    sound = np.zeros_like(t)
    
    # 各セグメントの音を作成
    for i in range(4):
        start_idx = int(i * segment_duration * sample_rate)
        end_idx = int((i + 1) * segment_duration * sample_rate)
        segment_t = t[start_idx:end_idx]
        
        if i < 3:  # "ta-ta-ta"部分
            freq = 800 + i * 100  # 周波数を少しずつ上げる
            segment_sound = np.sin(2 * np.pi * freq * segment_t)
            # エンベロープを適用（急激に減衰）
            envelope = np.exp(-segment_t * 20)
        else:  # "tan"部分（最後）
            freq = 600  # より低い音
            segment_sound = np.sin(2 * np.pi * freq * segment_t)
            # より長い持続音
            envelope = np.exp(-segment_t * 8)
        
        sound[start_idx:end_idx] = segment_sound * envelope
    
    # 音量を調整
    sound = sound * 0.55
    
    # 16ビット整数に変換
    audio = (sound * 32767).astype(np.int16)
    
    # WAVファイルとして保存
    wavfile.write('pnyo.wav', sample_rate, audio)
    print("pnyo.wav generated successfully!")

def generate_alien_destroy_sound():
    sample_rate = 44100
    duration = 1.2
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 低音の「ドガーン！」音を作成
    # 低周波数のベース音
    bass_freq = 60
    bass = np.sin(2 * np.pi * bass_freq * t)
    
    # 中音域の「ガーン」音
    mid_freq = 200
    mid = np.sin(2 * np.pi * mid_freq * t)
    
    # 高音の「シャー」音
    high_freq1 = 800
    high_freq2 = 1600
    high1 = np.sin(2 * np.pi * high_freq1 * t)
    high2 = np.sin(2 * np.pi * high_freq2 * t)
    
    # ノイズ成分を追加
    noise = np.random.normal(0, 0.1, len(t))
    
    # 各成分を組み合わせ
    sound = (bass * 0.4 + mid * 0.3 + high1 * 0.2 + high2 * 0.1 + noise * 0.1)
    
    # エンベロープを適用
    envelope = np.exp(-t * 2)
    sound = sound * envelope
    
    # 音量を調整
    sound = sound * 0.6
    
    # 16ビット整数に変換
    audio = (sound * 32767).astype(np.int16)
    
    # WAVファイルとして保存
    wavfile.write('alien_destroy.wav', sample_rate, audio)
    print("alien_destroy.wav generated successfully!")

def generate_explosion_sound():
    """弾の爆発音を生成"""
    sample_rate = 44100
    duration = 0.8
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # 爆発音の特徴的な音を作成
    # 低音のボン音
    bass_freq = 80
    bass = np.sin(2 * np.pi * bass_freq * t)
    
    # 中音域のパチパチ音
    mid_freq = 300
    mid = np.sin(2 * np.pi * mid_freq * t)
    
    # 高音のパチパチ音
    high_freq = 1200
    high = np.sin(2 * np.pi * high_freq * t)
    
    # ホワイトノイズでパチパチ感を演出
    noise = np.random.normal(0, 0.2, len(t))
    
    # 各成分を組み合わせ
    sound = (bass * 0.5 + mid * 0.3 + high * 0.2 + noise * 0.3)
    
    # 急激に減衰するエンベロープ
    envelope = np.exp(-t * 5)
    sound = sound * envelope
    
    # 音量を調整
    sound = sound * 0.4
    
    # 16ビット整数に変換
    audio = (sound * 32767).astype(np.int16)
    
    # WAVファイルとして保存
    wavfile.write('explosion.wav', sample_rate, audio)
    print("explosion.wav generated successfully!")

if __name__ == "__main__":
    generate_eat_sound()
    generate_alien_destroy_sound()
    generate_explosion_sound() 