import Phaser from 'phaser';

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' });
  }

  preload(): void {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    const progressBar = this.add.graphics();
    const progressBox = this.add.graphics();
    progressBox.fillStyle(0x222222, 0.8);
    progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

    const loadingText = this.add.text(width / 2, height / 2 - 50, 'Loading...', {
      font: '20px monospace',
      color: '#ffffff'
    }).setOrigin(0.5);

    this.load.on('progress', (value: number) => {
      progressBar.clear();
      progressBar.fillStyle(0x00ff00, 1);
      progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
    });

    this.load.on('complete', () => {
      progressBar.destroy();
      progressBox.destroy();
      loadingText.destroy();
    });

    // Load background images
    this.load.image('sky_layer1', 'assets/backgrounds/sky_layer1.png');
    this.load.image('sky_layer2', 'assets/backgrounds/sky_layer2.png');
    this.load.image('mountain_layer', 'assets/backgrounds/mountain_layer.png');
    this.load.image('ground_layer', 'assets/backgrounds/ground_layer.png');

    // Load sounds
    this.load.audio('bgm', 'assets/sounds/bgm.mp3');
    this.load.audio('pnyo', 'assets/sounds/pnyo.wav');
    this.load.audio('alien_destroy', 'assets/sounds/alien_destroy.wav');
    this.load.audio('explosion', 'assets/sounds/explosion.wav');
  }

  create(): void {
    this.scene.start('GameScene');
  }
}
