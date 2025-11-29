import Phaser from 'phaser';

interface GameOverData {
  score: number;
}

export class GameOverScene extends Phaser.Scene {
  private finalScore: number = 0;

  constructor() {
    super({ key: 'GameOverScene' });
  }

  init(data: GameOverData): void {
    this.finalScore = data.score || 0;
  }

  create(): void {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Semi-transparent overlay
    this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.5);

    // Game Over text
    this.add.text(width / 2, height / 2 - 50, 'GAME OVER', {
      font: 'bold 64px Arial',
      color: '#ff0000',
      stroke: '#000000',
      strokeThickness: 4
    }).setOrigin(0.5);

    // Score text
    this.add.text(width / 2, height / 2 + 20, `Score: ${this.finalScore}`, {
      font: '32px Arial',
      color: '#ffffff'
    }).setOrigin(0.5);

    // Restart instruction
    this.add.text(width / 2, height / 2 + 80, 'Press SPACE or Click to Restart', {
      font: '24px Arial',
      color: '#ffffff'
    }).setOrigin(0.5);

    // Input handlers
    this.input.keyboard?.once('keydown-SPACE', () => {
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

  private restartGame(): void {
    this.scene.start('GameScene');
  }
}
