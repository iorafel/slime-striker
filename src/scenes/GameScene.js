import Phaser from 'phaser';
import { Slime } from '../entities/Slime.js';
import { Platform, SpikedPlatform, FlyingPlatform } from '../entities/Platform.js';
import { Alien } from '../entities/Alien.js';
import { Apple } from '../entities/Apple.js';
import { Projectile, AlienBullet, DeflectedBullet } from '../entities/Projectile.js';
import { Explosion, BigExplosion, ScreenFlash } from '../entities/Explosion.js';
import { ParallaxBackground } from '../systems/ParallaxBackground.js';

export class GameScene extends Phaser.Scene {
  constructor() {
    super({ key: 'GameScene' });
  }

  create() {
    // Game state
    this.score = 0;
    this.cameraX = 0;
    this.lastPlatformX = 0;
    this.lastAlienX = 0;
    this.lastAppleX = 0;

    // Parallax background
    this.background = new ParallaxBackground(this);

    // Entity arrays
    this.platforms = [];
    this.aliens = [];
    this.apples = [];
    this.projectiles = [];
    this.alienBullets = [];
    this.deflectedBullets = [];
    this.explosions = [];
    this.flyingPlatforms = [];
    this.screenFlash = null;

    // Create initial platforms
    this.createInitialPlatforms();

    // Create player
    this.slime = new Slime(this, 200, 300);

    // Input
    this.cursors = this.input.keyboard.createCursorKeys();
    this.spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    // Alien attack timer
    this.alienAttackTimer = 0;
    this.alienAttackInterval = 1000;

    // UI
    this.scoreText = this.add.text(16, 16, 'Score: 0', {
      font: '24px Arial',
      fill: '#ffffff',
      stroke: '#000000',
      strokeThickness: 2
    }).setScrollFactor(0).setDepth(100);

    this.doubleJumpText = this.add.text(16, 50, '', {
      font: '18px Arial',
      fill: '#8b4513',
      stroke: '#000000',
      strokeThickness: 2
    }).setScrollFactor(0).setDepth(100);

    this.purpleTimerText = this.add.text(16, 80, '', {
      font: '18px Arial',
      fill: '#9932cc',
      stroke: '#000000',
      strokeThickness: 2
    }).setScrollFactor(0).setDepth(100);

    // Sound
    this.setupSounds();

    // Camera
    this.cameras.main.setBounds(0, 0, Number.MAX_SAFE_INTEGER, 600);
  }

  setupSounds() {
    try {
      this.bgm = this.sound.add('bgm', { loop: true, volume: 0.5 });
      this.bgm.play();
    } catch (e) {
      console.warn('BGM not available');
    }

    this.sounds = {
      pnyo: this.sound.add('pnyo', { volume: 0.7 }),
      alienDestroy: this.sound.add('alien_destroy', { volume: 0.6 }),
      explosion: this.sound.add('explosion', { volume: 0.5 })
    };
  }

  createInitialPlatforms() {
    // Ground platform
    const ground = new Platform(this, 400, 550, 800, 40);
    this.platforms.push(ground);

    // Starting platforms
    for (let i = 0; i < 10; i++) {
      this.generatePlatform(200 + i * 150);
    }
    this.lastPlatformX = 200 + 9 * 150;
  }

  generatePlatform(x) {
    const y = Phaser.Math.Between(200, 500);
    const isSpike = Math.random() < 0.1;

    const platform = isSpike
      ? new SpikedPlatform(this, x, y)
      : new Platform(this, x, y);

    this.platforms.push(platform);

    // Maybe spawn apple
    if (Math.random() < 0.3) {
      this.generateApple(x, y - 50);
    }

    // Maybe spawn alien
    if (Math.random() < 0.2) {
      this.generateAlien(x + 100);
    }
  }

  generateAlien(x) {
    const y = Phaser.Math.Between(100, 400);
    const type = Math.random() < 0.1 ? 'red' : 'normal';
    const alien = new Alien(this, x, y, type);
    this.aliens.push(alien);
  }

  generateApple(x, y) {
    const type = Apple.getRandomType();
    const apple = new Apple(this, x, y, type);
    this.apples.push(apple);
  }

  update(time, delta) {
    // Input handling
    this.handleInput(time);

    // Update slime physics
    this.updateSlimePhysics(delta);

    // Update camera
    this.updateCamera();

    // Generate new content
    this.generateContent();

    // Update entities
    this.updateEntities(delta);

    // Handle collisions
    this.handleCollisions(time);

    // Alien attacks
    this.handleAlienAttacks(time);

    // Cleanup off-screen entities
    this.cleanup();

    // Update UI
    this.updateUI();

    // Update background
    this.background.update(this.cameraX);
  }

  handleInput(time) {
    const slime = this.slime;

    // Movement
    if (this.cursors.left.isDown) {
      slime.x -= 5;
      slime.facingRight = false;
    }
    if (this.cursors.right.isDown) {
      slime.x += 5;
      slime.facingRight = true;
    }

    // Jump
    if (Phaser.Input.Keyboard.JustDown(this.cursors.up)) {
      slime.jump();
    }

    // Fire
    if (this.spaceKey.isDown && slime.canFire(time)) {
      this.fireProjectile(time);
    }
  }

  fireProjectile(time) {
    const slime = this.slime;
    slime.fire(time);

    const direction = slime.facingRight ? 1 : -1;
    let velocityX = direction * 10;
    let velocityY = 0;

    // Upward fire if up is held
    if (this.cursors.up.isDown) {
      velocityY = -10;
      velocityX = direction * 3;
    }

    const isBig = slime.isPurpleForm;
    const speed = isBig ? 22 : 10;
    velocityX = direction * speed;
    if (this.cursors.up.isDown) {
      velocityY = -speed;
      velocityX = direction * speed * 0.3;
    }

    const projectile = new Projectile(
      this,
      slime.x + direction * 30,
      slime.y,
      velocityX,
      velocityY,
      slime.form,
      isBig
    );
    this.projectiles.push(projectile);
  }

  updateSlimePhysics(delta) {
    const slime = this.slime;

    // Gravity
    if (!slime.isPurpleForm) {
      slime.velocityY += 0.8;
    }

    slime.y += slime.velocityY;

    // Update slime
    slime.update(this.time.now, delta);
  }

  updateCamera() {
    // Follow slime (one-directional)
    const targetX = this.slime.x - 200;
    if (targetX > this.cameraX) {
      this.cameraX += (targetX - this.cameraX) * 0.1;
    }
    this.cameras.main.scrollX = this.cameraX;
  }

  generateContent() {
    const screenRight = this.cameraX + 1000;

    // Generate platforms
    while (this.lastPlatformX < screenRight) {
      this.lastPlatformX += Phaser.Math.Between(100, 250);
      this.generatePlatform(this.lastPlatformX);
    }
  }

  updateEntities(delta) {
    // Update aliens
    for (const alien of this.aliens) {
      alien.update(delta);
    }

    // Update apples
    for (const apple of this.apples) {
      apple.update(delta);
    }

    // Update projectiles
    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      if (!this.projectiles[i].update(delta)) {
        this.projectiles.splice(i, 1);
      }
    }

    // Update alien bullets
    for (let i = this.alienBullets.length - 1; i >= 0; i--) {
      if (!this.alienBullets[i].update(delta)) {
        this.alienBullets.splice(i, 1);
      }
    }

    // Update deflected bullets
    for (let i = this.deflectedBullets.length - 1; i >= 0; i--) {
      if (!this.deflectedBullets[i].update(delta)) {
        this.deflectedBullets.splice(i, 1);
      }
    }

    // Update explosions
    for (let i = this.explosions.length - 1; i >= 0; i--) {
      if (!this.explosions[i].update(delta)) {
        this.explosions.splice(i, 1);
      }
    }

    // Update flying platforms
    for (let i = this.flyingPlatforms.length - 1; i >= 0; i--) {
      if (!this.flyingPlatforms[i].update(delta)) {
        this.flyingPlatforms.splice(i, 1);
      }
    }

    // Update screen flash
    if (this.screenFlash && !this.screenFlash.update(delta)) {
      this.screenFlash = null;
    }
  }

  handleCollisions(time) {
    const slime = this.slime;
    const slimeBounds = slime.getBounds();

    // Reset ground state
    slime.isOnGround = false;

    // Platform collisions
    for (const platform of this.platforms) {
      const platBounds = platform.getBounds();

      if (Phaser.Geom.Rectangle.Overlaps(slimeBounds, platBounds)) {
        // Check if landing from above
        if (slime.velocityY > 0 && slime.y < platform.y) {
          slime.y = platBounds.y - slime.size * 0.35;
          slime.land();

          // Purple form launches platforms
          if (slime.isPurpleForm && !(platform instanceof SpikedPlatform)) {
            this.launchPlatform(platform);
          }
        }
      }

      // Spike collision
      if (platform instanceof SpikedPlatform) {
        const spikeBounds = platform.getSpikeBounds();
        if (Phaser.Geom.Rectangle.Overlaps(slimeBounds, spikeBounds)) {
          this.gameOver();
          return;
        }
      }
    }

    // Apple collisions
    for (let i = this.apples.length - 1; i >= 0; i--) {
      const apple = this.apples[i];
      if (!apple.collected && Phaser.Geom.Rectangle.Overlaps(slimeBounds, apple.getBounds())) {
        this.collectApple(apple);
        this.apples.splice(i, 1);
        apple.destroy();
      }
    }

    // Alien bullet collisions with slime
    for (let i = this.alienBullets.length - 1; i >= 0; i--) {
      const bullet = this.alienBullets[i];
      if (this.circleRectOverlap(bullet.getBounds(), slimeBounds)) {
        if (slime.canDeflect) {
          // Deflect bullet
          const deflected = new DeflectedBullet(this, bullet.x, bullet.y,
            Math.atan2(bullet.velocityY, bullet.velocityX));
          this.deflectedBullets.push(deflected);
          bullet.destroy();
          this.alienBullets.splice(i, 1);
        } else {
          if (slime.takeDamage()) {
            this.gameOver();
            return;
          }
          bullet.destroy();
          this.alienBullets.splice(i, 1);
        }
      }
    }

    // Projectile collisions with aliens
    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      const proj = this.projectiles[i];

      for (let j = this.aliens.length - 1; j >= 0; j--) {
        const alien = this.aliens[j];
        if (alien.alive && this.circleRectOverlap(proj.getBounds(), alien.getBounds())) {
          this.destroyAlien(alien, j);
          if (!proj.isBig) {
            proj.destroy();
            this.projectiles.splice(i, 1);
          }
          break;
        }
      }
    }

    // Deflected bullet collisions with aliens
    for (let i = this.deflectedBullets.length - 1; i >= 0; i--) {
      const bullet = this.deflectedBullets[i];

      for (let j = this.aliens.length - 1; j >= 0; j--) {
        const alien = this.aliens[j];
        if (alien.alive && this.circleRectOverlap(bullet.getBounds(), alien.getBounds())) {
          this.destroyAlien(alien, j);
          bullet.destroy();
          this.deflectedBullets.splice(i, 1);
          break;
        }
      }
    }

    // Fall death
    if (slime.y > 650) {
      this.gameOver();
    }
  }

  circleRectOverlap(circle, rect) {
    const closestX = Phaser.Math.Clamp(circle.x, rect.x, rect.x + rect.width);
    const closestY = Phaser.Math.Clamp(circle.y, rect.y, rect.y + rect.height);
    const distanceX = circle.x - closestX;
    const distanceY = circle.y - closestY;
    return (distanceX * distanceX + distanceY * distanceY) < (circle.radius * circle.radius);
  }

  collectApple(apple) {
    try {
      this.sounds.pnyo.play();
    } catch (e) {}

    if (apple.appleType === 'green') {
      this.destroyAllAliens();
    } else {
      this.slime.eatApple(apple.appleType);
    }
  }

  destroyAllAliens() {
    this.screenFlash = new ScreenFlash(this);

    for (let i = this.aliens.length - 1; i >= 0; i--) {
      const alien = this.aliens[i];
      if (alien.alive) {
        this.createExplosion(alien.x, alien.y);
        this.score++;
        alien.die();
        alien.destroy();
        this.aliens.splice(i, 1);
      }
    }
  }

  destroyAlien(alien, index) {
    try {
      this.sounds.alienDestroy.play();
    } catch (e) {}

    this.createExplosion(alien.x, alien.y);
    this.score++;

    // Red aliens spawn 4 smaller aliens
    if (alien.alienType === 'red') {
      for (let i = 0; i < 4; i++) {
        const angle = (Math.PI * 2 * i) / 4;
        const spawnX = alien.x + Math.cos(angle) * 50;
        const spawnY = alien.y + Math.sin(angle) * 50;
        const spawned = new Alien(this, spawnX, spawnY, 'spawned');
        this.aliens.push(spawned);
      }
    }

    alien.die();
    alien.destroy();
    this.aliens.splice(index, 1);
  }

  createExplosion(x, y, big = false) {
    const explosion = big
      ? new BigExplosion(this, x, y)
      : new Explosion(this, x, y);
    this.explosions.push(explosion);
  }

  launchPlatform(platform) {
    const index = this.platforms.indexOf(platform);
    if (index > -1) {
      const vx = (Math.random() - 0.5) * 10;
      const vy = -10 - Math.random() * 5;
      const flying = new FlyingPlatform(this, platform.x, platform.y, vx, vy);
      this.flyingPlatforms.push(flying);

      platform.destroy();
      this.platforms.splice(index, 1);
      this.score++;
    }
  }

  handleAlienAttacks(time) {
    if (time - this.alienAttackTimer < this.alienAttackInterval) return;
    this.alienAttackTimer = time;

    for (const alien of this.aliens) {
      if (!alien.alive) continue;

      // Only attack if on screen
      if (alien.x < this.cameraX - 100 || alien.x > this.cameraX + 900) continue;

      const angles = alien.getAttackAngles(this.slime.x, this.slime.y);
      for (const angle of angles) {
        const bullet = new AlienBullet(this, alien.x, alien.y, angle);
        this.alienBullets.push(bullet);
      }
    }
  }

  cleanup() {
    const leftBound = this.cameraX - 200;
    const rightBound = this.cameraX + 1000;

    // Cleanup platforms
    for (let i = this.platforms.length - 1; i >= 0; i--) {
      if (this.platforms[i].x < leftBound) {
        this.platforms[i].destroy();
        this.platforms.splice(i, 1);
      }
    }

    // Cleanup aliens
    for (let i = this.aliens.length - 1; i >= 0; i--) {
      if (this.aliens[i].x < leftBound) {
        this.aliens[i].destroy();
        this.aliens.splice(i, 1);
      }
    }

    // Cleanup apples
    for (let i = this.apples.length - 1; i >= 0; i--) {
      if (this.apples[i].x < leftBound) {
        this.apples[i].destroy();
        this.apples.splice(i, 1);
      }
    }

    // Cleanup projectiles
    for (let i = this.projectiles.length - 1; i >= 0; i--) {
      const proj = this.projectiles[i];
      if (proj.x < leftBound || proj.x > rightBound) {
        proj.destroy();
        this.projectiles.splice(i, 1);
      }
    }

    // Cleanup alien bullets
    for (let i = this.alienBullets.length - 1; i >= 0; i--) {
      const bullet = this.alienBullets[i];
      if (bullet.x < leftBound || bullet.x > rightBound ||
          bullet.y < -100 || bullet.y > 700) {
        bullet.destroy();
        this.alienBullets.splice(i, 1);
      }
    }
  }

  updateUI() {
    this.scoreText.setText(`Score: ${this.score}`);

    if (this.slime.doubleJumpCharges > 0) {
      this.doubleJumpText.setText(`Double Jump: ${this.slime.doubleJumpCharges}`);
    } else {
      this.doubleJumpText.setText('');
    }

    if (this.slime.isPurpleForm) {
      const remaining = (this.slime.purpleFormTimer / 1000).toFixed(1);
      this.purpleTimerText.setText(`Purple Form: ${remaining}s`);
    } else {
      this.purpleTimerText.setText('');
    }
  }

  gameOver() {
    if (this.bgm) {
      this.bgm.stop();
    }
    this.scene.start('GameOverScene', { score: this.score });
  }
}
