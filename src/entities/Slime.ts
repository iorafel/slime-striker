import Phaser from 'phaser';

interface Sparkle {
  x: number;
  y: number;
  life: number;
  maxLife: number;
}

type AppleType = 'red' | 'blue' | 'green' | 'purple' | 'brown';

export class Slime extends Phaser.GameObjects.Container {
  public form: number = 1;
  public appleCount: number = 0;
  public doubleJumpCharges: number = 0;
  public canDoubleJump: boolean = false;
  public isOnGround: boolean = false;
  public velocityY: number = 0;
  public facingRight: boolean = true;
  public canDeflect: boolean = false;
  public isPurpleForm: boolean = false;
  public purpleFormTimer: number = 0;

  private graphics: Phaser.GameObjects.Graphics;
  private deflectTimer: number = 0;
  private lastFireTime: number = 0;
  private purpleFormDuration: number = 5000;
  private slimeRotation: number = 0;
  private sparkles: Sparkle[] = [];

  private readonly formSizes: Record<number, number> = {
    1: 40,
    2: 50,
    3: 60,
    4: 320
  };

  private readonly formColors: Record<number, number> = {
    1: 0x00ff00,
    2: 0x00ff00,
    3: 0xff0000,
    4: 0x9932cc
  };

  constructor(scene: Phaser.Scene, x: number, y: number) {
    super(scene, x, y);
    scene.add.existing(this);

    this.graphics = scene.add.graphics();
    this.add(this.graphics);

    this.draw();
  }

  get size(): number {
    return this.formSizes[this.form];
  }

  get color(): number {
    return this.formColors[this.form];
  }

  private draw(): void {
    this.graphics.clear();

    const size = this.size;
    const color = this.color;

    if (this.isPurpleForm) {
      this.graphics.save();
      this.graphics.rotate(this.slimeRotation);

      this.graphics.fillStyle(0x9932cc, 0.3);
      this.graphics.fillCircle(0, 0, size * 0.7);

      this.graphics.fillStyle(color, 1);
      this.graphics.fillEllipse(0, 0, size, size * 0.7);

      const eyeOffset = size * 0.15;
      this.graphics.fillStyle(0xffffff, 1);
      this.graphics.fillCircle(-eyeOffset, -size * 0.1, size * 0.12);
      this.graphics.fillCircle(eyeOffset, -size * 0.1, size * 0.12);
      this.graphics.fillStyle(0x000000, 1);
      this.graphics.fillCircle(-eyeOffset, -size * 0.1, size * 0.06);
      this.graphics.fillCircle(eyeOffset, -size * 0.1, size * 0.06);

      this.graphics.restore();
    } else {
      this.graphics.fillStyle(color, 1);
      this.graphics.fillEllipse(0, 0, size, size * 0.7);

      this.graphics.fillStyle(0xffffff, 0.3);
      this.graphics.fillEllipse(-size * 0.15, -size * 0.15, size * 0.3, size * 0.2);

      const eyeOffset = size * 0.15;
      const eyeY = -size * 0.05;
      this.graphics.fillStyle(0xffffff, 1);
      this.graphics.fillCircle(-eyeOffset, eyeY, size * 0.12);
      this.graphics.fillCircle(eyeOffset, eyeY, size * 0.12);

      const pupilOffset = this.facingRight ? 2 : -2;
      this.graphics.fillStyle(0x000000, 1);
      this.graphics.fillCircle(-eyeOffset + pupilOffset, eyeY, size * 0.06);
      this.graphics.fillCircle(eyeOffset + pupilOffset, eyeY, size * 0.06);

      if (this.form === 3) {
        this.graphics.lineStyle(3, 0xff6600, 0.5);
        this.graphics.strokeEllipse(0, 0, size * 1.1, size * 0.8);
      }

      if (this.canDeflect) {
        this.graphics.lineStyle(4, 0x00ffff, 0.7);
        this.graphics.strokeCircle(0, 0, size * 0.6);
      }
    }
  }

  update(_time: number, delta: number): void {
    if (this.isPurpleForm) {
      this.purpleFormTimer -= delta;
      this.slimeRotation += 0.35;
      if (this.purpleFormTimer <= 0) {
        this.endPurpleForm();
      }
    }

    if (this.canDeflect) {
      this.deflectTimer -= delta;
      if (this.deflectTimer <= 0) {
        this.canDeflect = false;
      }
    }

    this.updateSparkles(delta);
    this.draw();
  }

  jump(): boolean {
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

  land(): void {
    this.isOnGround = true;
    this.velocityY = 0;
  }

  eatApple(type: AppleType): void {
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
        break;
      case 'purple':
        this.startPurpleForm();
        break;
      case 'brown':
        this.doubleJumpCharges++;
        break;
    }
  }

  private startPurpleForm(): void {
    this.isPurpleForm = true;
    this.form = 4;
    this.purpleFormTimer = this.purpleFormDuration;
  }

  private endPurpleForm(): void {
    this.isPurpleForm = false;
    if (this.appleCount >= 2) this.form = 3;
    else if (this.appleCount >= 1) this.form = 2;
    else this.form = 1;
  }

  takeDamage(): boolean {
    if (this.isPurpleForm) return false;

    if (this.form > 1) {
      this.form--;
      this.appleCount = Math.max(0, this.appleCount - 1);
      return false;
    }
    return true;
  }

  canFire(time: number): boolean {
    const cooldown = this.canDeflect ? 50 : (this.form === 3 ? 150 : 300);
    return time - this.lastFireTime >= cooldown;
  }

  fire(time: number): void {
    this.lastFireTime = time;
  }

  private updateSparkles(delta: number): void {
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

    for (let i = this.sparkles.length - 1; i >= 0; i--) {
      this.sparkles[i].life -= delta;
      if (this.sparkles[i].life <= 0) {
        this.sparkles.splice(i, 1);
      }
    }
  }

  getBounds(): Phaser.Geom.Rectangle {
    const size = this.size;
    return new Phaser.Geom.Rectangle(
      this.x - size / 2,
      this.y - size * 0.35,
      size,
      size * 0.7
    );
  }
}
