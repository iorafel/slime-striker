import Phaser from 'phaser';

export type AlienType = 'normal' | 'red' | 'spawned';

export class Alien extends Phaser.GameObjects.Container {
  public alienType: AlienType;
  public alive: boolean = true;
  public size: number;

  private graphics: Phaser.GameObjects.Graphics;
  private hoverOffset: number = 0;
  private hoverSpeed: number = 0.05;
  private baseY: number;

  constructor(scene: Phaser.Scene, x: number, y: number, type: AlienType = 'normal') {
    super(scene, x, y);
    scene.add.existing(this);

    this.alienType = type;
    this.baseY = y;
    this.size = type === 'red' ? 50 : (type === 'spawned' ? 25 : 35);

    this.graphics = scene.add.graphics();
    this.add(this.graphics);
    this.draw();
  }

  get color(): number {
    switch (this.alienType) {
      case 'red': return 0xff4444;
      case 'spawned': return 0x4444ff;
      default: return 0x44ff44;
    }
  }

  private draw(): void {
    this.graphics.clear();
    if (!this.alive) return;

    const size = this.size;
    const color = this.color;

    this.graphics.fillStyle(color, 1);
    this.graphics.fillEllipse(0, 0, size, size * 0.8);

    this.graphics.fillStyle(color, 1);
    this.graphics.fillCircle(0, -size * 0.3, size * 0.4);

    this.graphics.fillStyle(0xffffff, 1);
    this.graphics.fillCircle(-size * 0.12, -size * 0.35, size * 0.12);
    this.graphics.fillCircle(size * 0.12, -size * 0.35, size * 0.12);

    this.graphics.fillStyle(0x000000, 1);
    this.graphics.fillCircle(-size * 0.12, -size * 0.35, size * 0.06);
    this.graphics.fillCircle(size * 0.12, -size * 0.35, size * 0.06);

    this.graphics.lineStyle(2, color, 1);
    this.graphics.beginPath();
    this.graphics.moveTo(-size * 0.15, -size * 0.5);
    this.graphics.lineTo(-size * 0.25, -size * 0.8);
    this.graphics.stroke();
    this.graphics.beginPath();
    this.graphics.moveTo(size * 0.15, -size * 0.5);
    this.graphics.lineTo(size * 0.25, -size * 0.8);
    this.graphics.stroke();

    this.graphics.fillStyle(0xffff00, 1);
    this.graphics.fillCircle(-size * 0.25, -size * 0.8, 3);
    this.graphics.fillCircle(size * 0.25, -size * 0.8, 3);

    this.graphics.lineStyle(3, color, 1);
    this.graphics.beginPath();
    this.graphics.moveTo(-size * 0.4, 0);
    this.graphics.lineTo(-size * 0.6, size * 0.2);
    this.graphics.stroke();
    this.graphics.beginPath();
    this.graphics.moveTo(size * 0.4, 0);
    this.graphics.lineTo(size * 0.6, size * 0.2);
    this.graphics.stroke();
  }

  update(delta: number): void {
    if (!this.alive) return;

    this.hoverOffset += this.hoverSpeed * delta;
    this.y = this.baseY + Math.sin(this.hoverOffset) * 8;

    this.draw();
  }

  die(): void {
    this.alive = false;
    this.graphics.clear();
  }

  getBounds(): Phaser.Geom.Rectangle {
    return new Phaser.Geom.Rectangle(
      this.x - this.size / 2,
      this.y - this.size / 2,
      this.size,
      this.size
    );
  }

  getAttackAngles(targetX: number, targetY: number): number[] {
    const angle = Math.atan2(targetY - this.y, targetX - this.x);

    switch (this.alienType) {
      case 'red':
        return [angle - Math.PI / 4, angle, angle + Math.PI / 4];
      case 'spawned':
        return [angle];
      default:
        return [angle];
    }
  }
}
