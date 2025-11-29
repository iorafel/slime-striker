import Phaser from 'phaser';

export class Explosion extends Phaser.GameObjects.Container {
  constructor(scene, x, y, maxRadius = 30, color = 0xff6600) {
    super(scene, x, y);
    scene.add.existing(this);

    this.maxRadius = maxRadius;
    this.color = color;
    this.currentRadius = 5;
    this.growthRate = 3;
    this.active = true;
    this.particles = [];

    // Create particles
    for (let i = 0; i < 15; i++) {
      const angle = (Math.PI * 2 * i) / 15 + Math.random() * 0.5;
      const speed = 2 + Math.random() * 3;
      this.particles.push({
        x: 0,
        y: 0,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 500 + Math.random() * 300,
        maxLife: 500 + Math.random() * 300
      });
    }

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  draw() {
    this.graphics.clear();
    if (!this.active) return;

    const alpha = Math.max(0, 1 - this.currentRadius / this.maxRadius);

    // Main explosion circle
    this.graphics.fillStyle(this.color, alpha * 0.5);
    this.graphics.fillCircle(0, 0, this.currentRadius);

    // Core
    this.graphics.fillStyle(0xffff00, alpha);
    this.graphics.fillCircle(0, 0, this.currentRadius * 0.4);

    // Particles
    for (const p of this.particles) {
      const pAlpha = p.life / p.maxLife;
      this.graphics.fillStyle(this.color, pAlpha);
      this.graphics.fillCircle(p.x, p.y, 3);
    }
  }

  update(delta) {
    if (!this.active) return false;

    this.currentRadius += this.growthRate * (delta / 16.67);

    // Update particles
    for (const p of this.particles) {
      p.x += p.vx * (delta / 16.67);
      p.y += p.vy * (delta / 16.67);
      p.life -= delta;
    }

    this.draw();

    if (this.currentRadius >= this.maxRadius) {
      this.destroy();
      return false;
    }

    return true;
  }

  destroy() {
    this.active = false;
    this.graphics.clear();
    super.destroy();
  }
}

export class BigExplosion extends Phaser.GameObjects.Container {
  constructor(scene, x, y) {
    super(scene, x, y);
    scene.add.existing(this);

    this.maxRadius = 100;
    this.currentRadius = 10;
    this.growthRate = 5;
    this.active = true;
    this.particles = [];

    // Create more particles
    for (let i = 0; i < 50; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 3 + Math.random() * 5;
      this.particles.push({
        x: 0,
        y: 0,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 800 + Math.random() * 400,
        maxLife: 800 + Math.random() * 400,
        color: Math.random() > 0.5 ? 0xff6600 : 0xffff00
      });
    }

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  draw() {
    this.graphics.clear();
    if (!this.active) return;

    const alpha = Math.max(0, 1 - this.currentRadius / this.maxRadius);

    // Outer glow
    this.graphics.fillStyle(0xff0000, alpha * 0.2);
    this.graphics.fillCircle(0, 0, this.currentRadius * 1.5);

    // Main explosion
    this.graphics.fillStyle(0xff6600, alpha * 0.6);
    this.graphics.fillCircle(0, 0, this.currentRadius);

    // Inner core
    this.graphics.fillStyle(0xffff00, alpha);
    this.graphics.fillCircle(0, 0, this.currentRadius * 0.3);

    // Particles
    for (const p of this.particles) {
      const pAlpha = p.life / p.maxLife;
      this.graphics.fillStyle(p.color, pAlpha);
      this.graphics.fillCircle(p.x, p.y, 4);
    }
  }

  update(delta) {
    if (!this.active) return false;

    this.currentRadius += this.growthRate * (delta / 16.67);

    // Update particles
    for (const p of this.particles) {
      p.x += p.vx * (delta / 16.67);
      p.y += p.vy * (delta / 16.67);
      p.vy += 0.1; // Gravity on particles
      p.life -= delta;
    }

    this.draw();

    if (this.currentRadius >= this.maxRadius) {
      this.destroy();
      return false;
    }

    return true;
  }

  destroy() {
    this.active = false;
    this.graphics.clear();
    super.destroy();
  }
}

export class ScreenFlash extends Phaser.GameObjects.Rectangle {
  constructor(scene) {
    super(scene, 400, 300, 800, 600, 0xffffff, 1);
    scene.add.existing(this);

    this.lifetime = 200;
    this.age = 0;
    this.setDepth(1000);
  }

  update(delta) {
    this.age += delta;
    this.setAlpha(Math.max(0, 1 - this.age / this.lifetime));

    if (this.age >= this.lifetime) {
      this.destroy();
      return false;
    }
    return true;
  }
}
