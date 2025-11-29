import Phaser from 'phaser';

export class Apple extends Phaser.GameObjects.Container {
  constructor(scene, x, y, type = 'red') {
    super(scene, x, y);
    scene.add.existing(this);

    this.appleType = type;
    this.collected = false;
    this.sparkleTimer = 0;
    this.sparkles = [];

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  get color() {
    switch (this.appleType) {
      case 'red': return 0xff0000;
      case 'blue': return 0x0088ff;
      case 'green': return 0x00ff00;
      case 'purple': return 0x9932cc;
      case 'brown': return 0x8b4513;
      default: return 0xff0000;
    }
  }

  get isSpecial() {
    return ['blue', 'green', 'purple', 'brown'].includes(this.appleType);
  }

  draw() {
    this.graphics.clear();
    if (this.collected) return;

    const size = 15;
    const color = this.color;

    // Glow for special apples
    if (this.isSpecial) {
      this.graphics.fillStyle(color, 0.3);
      this.graphics.fillCircle(0, 0, size * 1.5);
    }

    // Apple body
    this.graphics.fillStyle(color, 1);
    this.graphics.fillCircle(0, 0, size);

    // Highlight
    this.graphics.fillStyle(0xffffff, 0.4);
    this.graphics.fillCircle(-size * 0.3, -size * 0.3, size * 0.3);

    // Stem
    this.graphics.fillStyle(0x4a2800, 1);
    this.graphics.fillRect(-2, -size - 5, 4, 8);

    // Leaf
    this.graphics.fillStyle(0x228b22, 1);
    this.graphics.beginPath();
    this.graphics.moveTo(2, -size - 2);
    this.graphics.lineTo(10, -size - 8);
    this.graphics.lineTo(8, -size);
    this.graphics.closePath();
    this.graphics.fillPath();

    // Draw sparkles for special apples
    if (this.isSpecial) {
      for (const sparkle of this.sparkles) {
        const alpha = sparkle.life / sparkle.maxLife;
        this.graphics.fillStyle(0xffffff, alpha);
        this.graphics.fillCircle(sparkle.x, sparkle.y, 2);
      }
    }
  }

  update(delta) {
    if (this.collected) return;

    // Sparkle effect for special apples
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

  collect() {
    this.collected = true;
    this.graphics.clear();
  }

  getBounds() {
    return new Phaser.Geom.Rectangle(this.x - 15, this.y - 15, 30, 30);
  }

  static getRandomType() {
    const rand = Math.random();
    if (rand < 0.02) return 'purple';       // 2%
    if (rand < 0.07) return 'green';        // 5%
    if (rand < 0.17) return 'brown';        // 10%
    if (rand < 0.42) return 'blue';         // 25%
    return 'red';                           // 58%
  }
}
