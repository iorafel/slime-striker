import Phaser from 'phaser';

export class Slime extends Phaser.GameObjects.Container {
  constructor(scene, x, y) {
    super(scene, x, y);
    scene.add.existing(this);

    this.scene = scene;

    // State
    this.form = 1;
    this.appleCount = 0;
    this.doubleJumpCharges = 0;
    this.canDoubleJump = false;
    this.isOnGround = false;
    this.velocityY = 0;
    this.facingRight = true;

    // Form properties
    this.formSizes = {
      1: 40,
      2: 50,
      3: 60,
      4: 320
    };
    this.formColors = {
      1: 0x00ff00,  // Green
      2: 0x00ff00,  // Green
      3: 0xff0000,  // Red
      4: 0x9932cc   // Purple
    };

    // Combat
    this.canDeflect = false;
    this.deflectTimer = 0;
    this.lastFireTime = 0;
    this.fireCooldown = 300;

    // Purple form
    this.isPurpleForm = false;
    this.purpleFormTimer = 0;
    this.purpleFormDuration = 5000;
    this.rotation = 0;

    // Graphics
    this.graphics = scene.add.graphics();
    this.add(this.graphics);

    // Sparkles
    this.sparkles = [];

    // Physics body simulation
    this.body = {
      velocity: { x: 0, y: 0 },
      blocked: { down: false }
    };

    this.draw();
  }

  get size() {
    return this.formSizes[this.form];
  }

  get color() {
    return this.formColors[this.form];
  }

  draw() {
    this.graphics.clear();

    const size = this.size;
    const color = this.color;

    if (this.isPurpleForm) {
      // Purple form - rotating slime
      this.graphics.save();
      this.graphics.rotate(this.rotation);

      // Glow effect
      this.graphics.fillStyle(0x9932cc, 0.3);
      this.graphics.fillCircle(0, 0, size * 0.7);

      // Main body
      this.graphics.fillStyle(color, 1);
      this.graphics.fillEllipse(0, 0, size, size * 0.7);

      // Eyes
      const eyeOffset = size * 0.15;
      this.graphics.fillStyle(0xffffff, 1);
      this.graphics.fillCircle(-eyeOffset, -size * 0.1, size * 0.12);
      this.graphics.fillCircle(eyeOffset, -size * 0.1, size * 0.12);
      this.graphics.fillStyle(0x000000, 1);
      this.graphics.fillCircle(-eyeOffset, -size * 0.1, size * 0.06);
      this.graphics.fillCircle(eyeOffset, -size * 0.1, size * 0.06);

      this.graphics.restore();
    } else {
      // Normal form
      // Body
      this.graphics.fillStyle(color, 1);
      this.graphics.fillEllipse(0, 0, size, size * 0.7);

      // Highlight
      this.graphics.fillStyle(0xffffff, 0.3);
      this.graphics.fillEllipse(-size * 0.15, -size * 0.15, size * 0.3, size * 0.2);

      // Eyes
      const eyeOffset = size * 0.15;
      const eyeY = -size * 0.05;
      this.graphics.fillStyle(0xffffff, 1);
      this.graphics.fillCircle(-eyeOffset, eyeY, size * 0.12);
      this.graphics.fillCircle(eyeOffset, eyeY, size * 0.12);

      // Pupils (look in facing direction)
      const pupilOffset = this.facingRight ? 2 : -2;
      this.graphics.fillStyle(0x000000, 1);
      this.graphics.fillCircle(-eyeOffset + pupilOffset, eyeY, size * 0.06);
      this.graphics.fillCircle(eyeOffset + pupilOffset, eyeY, size * 0.06);

      // Form 3 glow
      if (this.form === 3) {
        this.graphics.lineStyle(3, 0xff6600, 0.5);
        this.graphics.strokeEllipse(0, 0, size * 1.1, size * 0.8);
      }

      // Deflect aura
      if (this.canDeflect) {
        this.graphics.lineStyle(4, 0x00ffff, 0.7);
        this.graphics.strokeCircle(0, 0, size * 0.6);
      }
    }
  }

  update(time, delta) {
    // Purple form timer
    if (this.isPurpleForm) {
      this.purpleFormTimer -= delta;
      this.rotation += 0.35;
      if (this.purpleFormTimer <= 0) {
        this.endPurpleForm();
      }
    }

    // Deflect timer
    if (this.canDeflect) {
      this.deflectTimer -= delta;
      if (this.deflectTimer <= 0) {
        this.canDeflect = false;
      }
    }

    // Update sparkles
    this.updateSparkles(delta);

    this.draw();
  }

  jump() {
    if (this.isOnGround) {
      this.velocityY = -18;
      this.isOnGround = false;
      this.canDoubleJump = this.doubleJumpCharges > 0;
      return true;
    } else if (this.canDoubleJump && this.doubleJumpCharges > 0) {
      this.velocityY = -16;
      this.doubleJumpCharges--;
      this.canDoubleJump = false;
      return true;
    }
    return false;
  }

  land() {
    this.isOnGround = true;
    this.velocityY = 0;
  }

  eatApple(type) {
    switch (type) {
      case 'red':
        this.appleCount++;
        if (this.appleCount === 1) this.form = 2;
        else if (this.appleCount >= 2) this.form = 3;
        break;
      case 'blue':
        this.form = 3;
        this.canDeflect = true;
        this.deflectTimer = 5000;
        break;
      case 'green':
        // Handled in GameScene
        break;
      case 'purple':
        this.startPurpleForm();
        break;
      case 'brown':
        this.doubleJumpCharges++;
        break;
    }
  }

  startPurpleForm() {
    this.isPurpleForm = true;
    this.form = 4;
    this.purpleFormTimer = this.purpleFormDuration;
  }

  endPurpleForm() {
    this.isPurpleForm = false;
    // Return to previous form based on apple count
    if (this.appleCount >= 2) this.form = 3;
    else if (this.appleCount >= 1) this.form = 2;
    else this.form = 1;
  }

  takeDamage() {
    if (this.isPurpleForm) return false;

    if (this.form > 1) {
      this.form--;
      this.appleCount = Math.max(0, this.appleCount - 1);
      return false; // Not dead
    }
    return true; // Dead
  }

  canFire(time) {
    const cooldown = this.canDeflect ? 50 : (this.form === 3 ? 150 : 300);
    return time - this.lastFireTime >= cooldown;
  }

  fire(time) {
    this.lastFireTime = time;
  }

  updateSparkles(delta) {
    // Add sparkles for special forms
    if (this.isPurpleForm || this.form >= 3) {
      if (Math.random() < 0.3) {
        this.sparkles.push({
          x: (Math.random() - 0.5) * this.size,
          y: (Math.random() - 0.5) * this.size * 0.7,
          life: 500,
          maxLife: 500
        });
      }
    }

    // Update existing sparkles
    for (let i = this.sparkles.length - 1; i >= 0; i--) {
      this.sparkles[i].life -= delta;
      if (this.sparkles[i].life <= 0) {
        this.sparkles.splice(i, 1);
      }
    }
  }

  getBounds() {
    const size = this.size;
    return new Phaser.Geom.Rectangle(
      this.x - size / 2,
      this.y - size * 0.35,
      size,
      size * 0.7
    );
  }
}
