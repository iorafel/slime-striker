import Phaser from 'phaser';

export type AppleType = 'red' | 'blue' | 'green' | 'purple' | 'brown';

interface Sparkle {
  x: number;
  y: number;
  life: number;
  maxLife: number;
}

export class Apple extends Phaser.GameObjects.Container {
  public appleType: AppleType;
  public collected: boolean = false;

  private graphics: Phaser.GameObjects.Graphics;
  private sparkleTimer: number = 0;
  private sparkles: Sparkle[] = [];

  constructor(scene: Phaser.Scene, x: number, y: number, type: AppleType = 'red') {
    super(scene, x, y);
    scene.add.existing(this);

    this.appleType = type;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  get color(): number {
    switch (this.appleType) {
      case 'red': return 0xff0000;
      case 'blue': return 0x0088ff;
      case 'green': return 0x00ff00;
      case 'purple': return 0x9932cc;
      case 'brown': return 0x8b4513;
      default: return 0xff0000;
    }
  }

  get isSpecial(): boolean {
    return ['blue', 'green', 'purple', 'brown'].includes(this.appleType);
  }

  private draw(): void {
    this.graphics.clear();
    if (this.collected) return;

    const size = 15;
    const color = this.color;

    if (this.isSpecial) {
      this.graphics.fillStyle(color, 0.3);
      this.graphics.fillCircle(0, 0, size * 1.5);
    }

    this.graphics.fillStyle(color, 1);
    this.graphics.fillCircle(0, 0, size);

    this.graphics.fillStyle(0xffffff, 0.4);
    this.graphics.fillCircle(-size * 0.3, -size * 0.3, size * 0.3);

    this.graphics.fillStyle(0x4a2800, 1);
    this.graphics.fillRect(-2, -size - 5, 4, 8);

    this.graphics.fillStyle(0x228b22, 1);
    this.graphics.beginPath();
    this.graphics.moveTo(2, -size - 2);
    this.graphics.lineTo(10, -size - 8);
    this.graphics.lineTo(8, -size);
    this.graphics.closePath();
    this.graphics.fillPath();

    if (this.isSpecial) {
      for (const sparkle of this.sparkles) {
        const alpha = sparkle.life / sparkle.maxLife;
        this.graphics.fillStyle(0xffffff, alpha);
        this.graphics.fillCircle(sparkle.x, sparkle.y, 2);
      }
    }
  }

  update(delta: number): void {
    if (this.collected) return;

    if (this.isSpecial) {
      this.sparkleTimer += delta;
      if (this.sparkleTimer > 100) {
        this.sparkleTimer = 0;
        this.sparkles.push({
          x: (Math.random() - 0.5) * 30,
          y: (Math.random() - 0.5) * 30,
          life: 500,
          maxLife: 500
        });
      }

      for (let i = this.sparkles.length - 1; i >= 0; i--) {
        this.sparkles[i].life -= delta;
        if (this.sparkles[i].life <= 0) {
          this.sparkles.splice(i, 1);
        }
      }
    }

    this.draw();
  }

  collect(): void {
    this.collected = true;
    this.graphics.clear();
  }

  getBounds(): Phaser.Geom.Rectangle {
    return new Phaser.Geom.Rectangle(this.x - 15, this.y - 15, 30, 30);
  }

  static getRandomType(): AppleType {
    const rand = Math.random();
    if (rand < 0.02) return 'purple';
    if (rand < 0.07) return 'green';
    if (rand < 0.17) return 'brown';
    if (rand < 0.42) return 'blue';
    return 'red';
  }
}
