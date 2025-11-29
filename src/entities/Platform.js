import Phaser from 'phaser';

export class Platform extends Phaser.GameObjects.Container {
  constructor(scene, x, y, width = 100, height = 20) {
    super(scene, x, y);
    scene.add.existing(this);

    this.platformWidth = width;
    this.platformHeight = height;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  draw() {
    this.graphics.clear();
    this.graphics.fillStyle(0xcc4444, 1);
    this.graphics.fillRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);

    // Border
    this.graphics.lineStyle(2, 0x882222, 1);
    this.graphics.strokeRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);
  }

  getBounds() {
    return new Phaser.Geom.Rectangle(
      this.x - this.platformWidth / 2,
      this.y - this.platformHeight / 2,
      this.platformWidth,
      this.platformHeight
    );
  }
}

export class SpikedPlatform extends Phaser.GameObjects.Container {
  constructor(scene, x, y, width = 100, height = 20) {
    super(scene, x, y);
    scene.add.existing(this);

    this.platformWidth = width;
    this.platformHeight = height;
    this.spikeHeight = 12;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  draw() {
    this.graphics.clear();

    // Platform base
    this.graphics.fillStyle(0x444444, 1);
    this.graphics.fillRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);

    // Spikes on top
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

    // Border
    this.graphics.lineStyle(2, 0x222222, 1);
    this.graphics.strokeRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);
  }

  getBounds() {
    return new Phaser.Geom.Rectangle(
      this.x - this.platformWidth / 2,
      this.y - this.platformHeight / 2,
      this.platformWidth,
      this.platformHeight
    );
  }

  getSpikeBounds() {
    return new Phaser.Geom.Rectangle(
      this.x - this.platformWidth / 2,
      this.y - this.platformHeight / 2 - this.spikeHeight,
      this.platformWidth,
      this.spikeHeight
    );
  }
}

export class FlyingPlatform extends Phaser.GameObjects.Container {
  constructor(scene, x, y, velocityX, velocityY) {
    super(scene, x, y);
    scene.add.existing(this);

    this.velocityX = velocityX;
    this.velocityY = velocityY;
    this.platformWidth = 100;
    this.platformHeight = 20;
    this.lifetime = 3000;
    this.age = 0;
    this.rotationAngle = 0;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  update(delta) {
    this.age += delta;
    this.velocityY += 0.5; // Gravity

    this.x += this.velocityX * (delta / 16.67);
    this.y += this.velocityY * (delta / 16.67);
    this.rotationAngle += 0.35;

    this.draw();

    return this.age < this.lifetime;
  }

  draw() {
    this.graphics.clear();

    const alpha = Math.max(0, 1 - this.age / this.lifetime);
    this.graphics.save();

    // Rotation is handled by the container
    this.setRotation(this.rotationAngle);

    // Glow
    this.graphics.fillStyle(0xff6600, alpha * 0.3);
    this.graphics.fillRect(-this.platformWidth / 2 - 5, -this.platformHeight / 2 - 5,
      this.platformWidth + 10, this.platformHeight + 10);

    // Platform
    this.graphics.fillStyle(0xcc4444, alpha);
    this.graphics.fillRect(-this.platformWidth / 2, -this.platformHeight / 2,
      this.platformWidth, this.platformHeight);

    this.graphics.restore();
  }
}
