import Phaser from 'phaser';

export class Projectile extends Phaser.GameObjects.Container {
  constructor(scene, x, y, velocityX, velocityY, powerLevel = 1, isBig = false) {
    super(scene, x, y);
    scene.add.existing(this);

    this.velocityX = velocityX;
    this.velocityY = velocityY;
    this.powerLevel = powerLevel;
    this.isBig = isBig;
    this.active = true;

    this.radius = isBig ? 50 : 8;
    this.sparkles = [];

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  get color() {
    if (this.isBig) return 0xffd700; // Gold
    if (this.powerLevel >= 3) return 0xff6600; // Orange for form 3
    return 0x9966ff; // Purple
  }

  draw() {
    this.graphics.clear();
    if (!this.active) return;

    // Glow
    this.graphics.fillStyle(this.color, 0.3);
    this.graphics.fillCircle(0, 0, this.radius * 1.5);

    // Main body
    this.graphics.fillStyle(this.color, 1);
    this.graphics.fillCircle(0, 0, this.radius);

    // Core
    this.graphics.fillStyle(0xffffff, 0.8);
    this.graphics.fillCircle(0, 0, this.radius * 0.4);

    // Sparkles
    for (const sparkle of this.sparkles) {
      const alpha = sparkle.life / sparkle.maxLife;
      this.graphics.fillStyle(0xffffff, alpha);
      this.graphics.fillCircle(sparkle.x, sparkle.y, 2);
    }
  }

  update(delta) {
    if (!this.active) return false;

    this.x += this.velocityX * (delta / 16.67);
    this.y += this.velocityY * (delta / 16.67);

    // Add sparkles
    if (Math.random() < 0.3) {
      this.sparkles.push({
        x: (Math.random() - 0.5) * this.radius * 2,
        y: (Math.random() - 0.5) * this.radius * 2,
        life: 200,
        maxLife: 200
      });
    }

    // Update sparkles
    for (let i = this.sparkles.length - 1; i >= 0; i--) {
      this.sparkles[i].life -= delta;
      if (this.sparkles[i].life <= 0) {
        this.sparkles.splice(i, 1);
      }
    }

    this.draw();
    return true;
  }

  destroy() {
    this.active = false;
    this.graphics.clear();
    super.destroy();
  }

  getBounds() {
    return new Phaser.Geom.Circle(this.x, this.y, this.radius);
  }
}

export class AlienBullet extends Phaser.GameObjects.Container {
  constructor(scene, x, y, angle, speed = 5) {
    super(scene, x, y);
    scene.add.existing(this);

    this.velocityX = Math.cos(angle) * speed;
    this.velocityY = Math.sin(angle) * speed;
    this.active = true;
    this.radius = 5;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  draw() {
    this.graphics.clear();
    if (!this.active) return;

    // Glow
    this.graphics.fillStyle(0xff0000, 0.3);
    this.graphics.fillCircle(0, 0, this.radius * 2);

    // Main body
    this.graphics.fillStyle(0xff0000, 1);
    this.graphics.fillCircle(0, 0, this.radius);

    // Core
    this.graphics.fillStyle(0xffff00, 0.8);
    this.graphics.fillCircle(0, 0, this.radius * 0.4);
  }

  update(delta) {
    if (!this.active) return false;

    this.x += this.velocityX * (delta / 16.67);
    this.y += this.velocityY * (delta / 16.67);

    this.draw();
    return true;
  }

  destroy() {
    this.active = false;
    this.graphics.clear();
    super.destroy();
  }

  getBounds() {
    return new Phaser.Geom.Circle(this.x, this.y, this.radius);
  }
}

export class DeflectedBullet extends Phaser.GameObjects.Container {
  constructor(scene, x, y, angle) {
    super(scene, x, y);
    scene.add.existing(this);

    // Random deflection angle
    const deflectAngle = angle + (Math.random() - 0.5) * Math.PI / 2;
    const speed = 8;
    this.velocityX = Math.cos(deflectAngle) * speed;
    this.velocityY = Math.sin(deflectAngle) * speed;
    this.active = true;
    this.radius = 5;
    this.lifetime = 3000;
    this.age = 0;
    this.sparkleAngle = 0;

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  draw() {
    this.graphics.clear();
    if (!this.active) return;

    const alpha = Math.max(0, 1 - this.age / this.lifetime);

    // Glow
    this.graphics.fillStyle(0xff69b4, 0.3 * alpha);
    this.graphics.fillCircle(0, 0, this.radius * 2);

    // Main body
    this.graphics.fillStyle(0xff69b4, alpha);
    this.graphics.fillCircle(0, 0, this.radius);

    // Sparkle effect
    this.graphics.fillStyle(0xffffff, alpha);
    const sparkleX = Math.cos(this.sparkleAngle) * this.radius * 1.5;
    const sparkleY = Math.sin(this.sparkleAngle) * this.radius * 1.5;
    this.graphics.fillCircle(sparkleX, sparkleY, 2);
  }

  update(delta) {
    if (!this.active) return false;

    this.age += delta;
    if (this.age >= this.lifetime) {
      this.destroy();
      return false;
    }

    this.x += this.velocityX * (delta / 16.67);
    this.y += this.velocityY * (delta / 16.67);
    this.sparkleAngle += 0.3;

    this.draw();
    return true;
  }

  destroy() {
    this.active = false;
    this.graphics.clear();
    super.destroy();
  }

  getBounds() {
    return new Phaser.Geom.Circle(this.x, this.y, this.radius);
  }
}
