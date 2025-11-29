import Phaser from 'phaser';

export class GameOverScene extends Phaser.Scene {
  constructor() {
    super({ key: 'GameOverScene' });
  }

  init(data) {
    this.finalScore = data.score || 0;
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Semi-transparent overlay
    this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.5);

    // Game Over text
    this.add.text(width / 2, height / 2 - 50, 'GAME OVER', {
      font: 'bold 64px Arial',
      fill: '#ff0000',
      stroke: '#000000',
      strokeThickness: 4
    }).setOrigin(0.5);

    // Score text
    this.add.text(width / 2, height / 2 + 20, `Score: ${this.finalScore}`, {
      font: '32px Arial',
      fill: '#ffffff'
    }).setOrigin(0.5);

    // Restart instruction
    this.add.text(width / 2, height / 2 + 80, 'Press SPACE or Click to Restart', {
      font: '24px Arial',
      fill: '#ffffff'
    }).setOrigin(0.5);

    // Input handlers
    this.input.keyboard.once('keydown-SPACE', () => {
      this.restartGame();
    });

    this.input.once('pointerdown', () => {
      this.restartGame();
    });

    // Auto restart after 5 seconds
    this.time.delayedCall(5000, () => {
      this.restartGame();
    });
  }

  restartGame() {
    this.scene.start('GameScene');
  }
}
