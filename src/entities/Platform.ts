import Phaser from 'phaser';

export class Platform extends Phaser.GameObjects.Container {
  public platformWidth: number;
  public platformHeight: number;
  protected graphics: Phaser.GameObjects.Graphics;

  constructor(scene: Phaser.Scene, x: number, y: number, width: number = 100, height: number = 20) {
    super(scene, x, y);
    scene.add.existing(this);

    this.platformWidth = width;
    this.platformHeight = height;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  protected draw(): void {
    this.graphics.clear();
    this.graphics.fillStyle(0xcc4444, 1);
    this.graphics.fillRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);

    this.graphics.lineStyle(2, 0x882222, 1);
    this.graphics.strokeRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);
  }

  getBounds(): Phaser.Geom.Rectangle {
    return new Phaser.Geom.Rectangle(
      this.x - this.platformWidth / 2,
      this.y - this.platformHeight / 2,
      this.platformWidth,
      this.platformHeight
    );
  }
}

export class SpikedPlatform extends Phaser.GameObjects.Container {
  public platformWidth: number;
  public platformHeight: number;
  public spikeHeight: number = 12;
  protected graphics: Phaser.GameObjects.Graphics;

  constructor(scene: Phaser.Scene, x: number, y: number, width: number = 100, height: number = 20) {
    super(scene, x, y);
    scene.add.existing(this);

    this.platformWidth = width;
    this.platformHeight = height;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  protected draw(): void {
    this.graphics.clear();

    this.graphics.fillStyle(0x444444, 1);
    this.graphics.fillRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);

    const spikeWidth = 10;
    const numSpikes = Math.floor(this.platformWidth / spikeWidth);

    this.graphics.fillStyle(0xff0000, 1);
    for (let i = 0; i < numSpikes; i++) {
      const spikeX = -this.platformWidth / 2 + i * spikeWidth + spikeWidth / 2;
      const spikeY = -this.platformHeight / 2;

      this.graphics.beginPath();
      this.graphics.moveTo(spikeX - spikeWidth / 2, spikeY);
      this.graphics.lineTo(spikeX, spikeY - this.spikeHeight);
      this.graphics.lineTo(spikeX + spikeWidth / 2, spikeY);
      this.graphics.closePath();
      this.graphics.fillPath();
    }

    this.graphics.lineStyle(2, 0x222222, 1);
    this.graphics.strokeRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);
  }

  getBounds(): Phaser.Geom.Rectangle {
    return new Phaser.Geom.Rectangle(
      this.x - this.platformWidth / 2,
      this.y - this.platformHeight / 2,
      this.platformWidth,
      this.platformHeight
    );
  }

  getSpikeBounds(): Phaser.Geom.Rectangle {
    return new Phaser.Geom.Rectangle(
      this.x - this.platformWidth / 2,
      this.y - this.platformHeight / 2 - this.spikeHeight,
      this.platformWidth,
      this.spikeHeight
    );
  }
}

export class FlyingPlatform extends Phaser.GameObjects.Container {
  public velocityX: number;
  public velocityY: number;
  private platformWidth: number = 100;
  private platformHeight: number = 20;
  private lifetime: number = 3000;
  private age: number = 0;
  private rotationAngle: number = 0;
  private graphics: Phaser.GameObjects.Graphics;

  constructor(scene: Phaser.Scene, x: number, y: number, velocityX: number, velocityY: number) {
    super(scene, x, y);
    scene.add.existing(this);

    this.velocityX = velocityX;
    this.velocityY = velocityY;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  update(delta: number): boolean {
    this.age += delta;
    this.velocityY += 0.5;

    this.x += this.velocityX * (delta / 16.67);
    this.y += this.velocityY * (delta / 16.67);
    this.rotationAngle += 0.35;

    this.draw();

    return this.age < this.lifetime;
  }

  private draw(): void {
    this.graphics.clear();

    const alpha = Math.max(0, 1 - this.age / this.lifetime);
    this.graphics.save();

    this.setRotation(this.rotationAngle);

    this.graphics.fillStyle(0xff6600, alpha * 0.3);
    this.graphics.fillRect(-this.platformWidth / 2 - 5, -this.platformHeight / 2 - 5,
      this.platformWidth + 10, this.platformHeight + 10);

    this.graphics.fillStyle(0xcc4444, alpha);
    this.graphics.fillRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);

    this.graphics.restore();
  }
}
