import Phaser from 'phaser';
import { Slime } from '../entities/Slime';
import { Platform, SpikedPlatform, FlyingPlatform } from '../entities/Platform';
import { Alien } from '../entities/Alien';
import { Apple, AppleType } from '../entities/Apple';
import { Projectile, AlienBullet, DeflectedBullet } from '../entities/Projectile';
import { Explosion, BigExplosion, ScreenFlash } from '../entities/Explosion';
import { ParallaxBackground } from '../systems/ParallaxBackground';

interface GameSounds {
  pnyo: Phaser.Sound.BaseSound;
  alienDestroy: Phaser.Sound.BaseSound;
  explosion: Phaser.Sound.BaseSound;
}

export class GameScene extends Phaser.Scene {
  private score: number = 0;
  private cameraX: number = 0;
  private lastPlatformX: number = 0;
  private lastGroundX: number = 0;
  private isGameOver: boolean = false;
  private gameStartTime: number = 0;

  private background!: ParallaxBackground;
  private slime!: Slime;

  private platforms: (Platform | SpikedPlatform)[] = [];
  private aliens: Alien[] = [];
  private apples: Apple[] = [];
  private projectiles: Projectile[] = [];
  private alienBullets: AlienBullet[] = [];
  private deflectedBullets: DeflectedBullet[] = [];
  private explosions: (Explosion | BigExplosion)[] = [];
  private flyingPlatforms: FlyingPlatform[] = [];
  private screenFlash: ScreenFlash | null = null;

  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private spaceKey!: Phaser.Input.Keyboard.Key;

  // Touch controls
  private touchLeft: boolean = false;
  private touchRight: boolean = false;
  private touchJump: boolean = false;
  private touchFire: boolean = false;
  private lastTouchTime: number = 0;
  private touchIndicators: Phaser.GameObjects.Arc[] = [];
  private jumpButton!: Phaser.GameObjects.Container;
  private resetButton!: Phaser.GameObjects.Container;
  private fullscreenButton!: Phaser.GameObjects.Container;
  private resetConfirmOverlay: Phaser.GameObjects.Container | null = null;
  private pauseStartTime: number = 0;

  private alienAttackTimer: number = 0;
  private alienAttackInterval: number = 1000;

  private scoreText!: Phaser.GameObjects.Text;
  private doubleJumpText!: Phaser.GameObjects.Text;
  private purpleTimerText!: Phaser.GameObjects.Text;

  private bgm?: Phaser.Sound.BaseSound;
  private sounds!: GameSounds;

  constructor() {
    super({ key: 'GameScene' });
  }

  create(): void {
    // Game state
    this.score = 0;
    this.cameraX = 0;
    this.lastPlatformX = 0;
    this.lastGroundX = 0;
    this.isGameOver = false;
    this.gameStartTime = this.time.now;

    // Reset touch states
    this.touchLeft = false;
    this.touchRight = false;
    this.touchJump = false;
    this.touchFire = false;
    this.touchIndicators = [];
    this.resetConfirmOverlay = null;
    this.pauseStartTime = 0;

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
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.spaceKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    // Touch controls setup
    this.setupTouchControls();

    // Jump button
    this.createJumpButton();

    // Reset button
    this.createResetButton();

    // Fullscreen button
    this.createFullscreenButton();

    // Alien attack timer
    this.alienAttackTimer = 0;
    this.alienAttackInterval = 1000;

    // UI
    this.scoreText = this.add.text(16, 16, 'Score: 0', {
      font: '24px Arial',
      color: '#ffffff',
      stroke: '#000000',
      strokeThickness: 2
    }).setScrollFactor(0).setDepth(100);

    this.doubleJumpText = this.add.text(16, 50, '', {
      font: '18px Arial',
      color: '#8b4513',
      stroke: '#000000',
      strokeThickness: 2
    }).setScrollFactor(0).setDepth(100);

    this.purpleTimerText = this.add.text(16, 80, '', {
      font: '18px Arial',
      color: '#9932cc',
      stroke: '#000000',
      strokeThickness: 2
    }).setScrollFactor(0).setDepth(100);

    // Sound
    this.setupSounds();

    // Camera
    this.cameras.main.setBounds(0, 0, Number.MAX_SAFE_INTEGER, 600);

    // Cleanup on shutdown
    this.events.once('shutdown', this.cleanupInputListeners, this);
  }

  private cleanupInputListeners(): void {
    this.input.off('pointerdown');
    this.input.off('pointerup');
    this.input.off('pointermove');
  }

  private createJumpButton(): void {
    const screenHeight = this.cameras.main.height;
    const buttonX = 80;
    const buttonY = screenHeight - 80;
    const radius = 50;

    this.jumpButton = this.add.container(buttonX, buttonY);
    this.jumpButton.setScrollFactor(0);
    this.jumpButton.setDepth(150);

    // Circle background
    const circle = this.add.graphics();
    circle.fillStyle(0x000000, 0.4);
    circle.fillCircle(0, 0, radius);
    circle.lineStyle(3, 0xffffff, 0.8);
    circle.strokeCircle(0, 0, radius);
    this.jumpButton.add(circle);

    // Arrow (pointing up)
    const arrow = this.add.graphics();
    arrow.fillStyle(0xffffff, 0.9);
    // Arrow body
    arrow.fillRect(-8, -5, 16, 25);
    // Arrow head (triangle)
    arrow.beginPath();
    arrow.moveTo(0, -25);
    arrow.lineTo(-18, -5);
    arrow.lineTo(18, -5);
    arrow.closePath();
    arrow.fillPath();
    this.jumpButton.add(arrow);

    // Make interactive
    const hitArea = new Phaser.Geom.Circle(0, 0, radius);
    this.jumpButton.setInteractive(hitArea, Phaser.Geom.Circle.Contains);

    this.jumpButton.on('pointerdown', () => {
      if (this.resetConfirmOverlay) return;
      this.slime.jump();
      // Visual feedback
      this.jumpButton.setScale(0.9);
    });

    this.jumpButton.on('pointerup', () => {
      this.jumpButton.setScale(1);
    });

    this.jumpButton.on('pointerout', () => {
      this.jumpButton.setScale(1);
    });
  }

  private createResetButton(): void {
    const buttonX = this.cameras.main.width - 80;
    const buttonY = 80;
    const radius = 50;

    this.resetButton = this.add.container(buttonX, buttonY);
    this.resetButton.setScrollFactor(0);
    this.resetButton.setDepth(150);

    // Circle background
    const circle = this.add.graphics();
    circle.fillStyle(0x000000, 0.4);
    circle.fillCircle(0, 0, radius);
    circle.lineStyle(2, 0xffffff, 0.8);
    circle.strokeCircle(0, 0, radius);
    this.resetButton.add(circle);

    // Circular arrow (refresh icon)
    const arrow = this.add.graphics();
    arrow.lineStyle(4, 0xffffff, 0.9);

    // Draw arc (circular part)
    arrow.beginPath();
    arrow.arc(0, 0, 22, Phaser.Math.DegToRad(-60), Phaser.Math.DegToRad(200), false);
    arrow.strokePath();

    // Draw arrowhead
    arrow.fillStyle(0xffffff, 0.9);
    arrow.beginPath();
    const arrowTipX = 22 * Math.cos(Phaser.Math.DegToRad(-60));
    const arrowTipY = 22 * Math.sin(Phaser.Math.DegToRad(-60));
    arrow.moveTo(arrowTipX, arrowTipY);
    arrow.lineTo(arrowTipX + 12, arrowTipY - 3);
    arrow.lineTo(arrowTipX + 3, arrowTipY + 12);
    arrow.closePath();
    arrow.fillPath();

    this.resetButton.add(arrow);

    // Make interactive
    const hitArea = new Phaser.Geom.Circle(0, 0, radius);
    this.resetButton.setInteractive(hitArea, Phaser.Geom.Circle.Contains);

    this.resetButton.on('pointerdown', () => {
      if (this.resetConfirmOverlay) return;
      this.resetButton.setScale(0.9);
    });

    this.resetButton.on('pointerup', () => {
      if (this.resetConfirmOverlay) return;
      this.resetButton.setScale(1);
      this.showResetConfirm();
    });

    this.resetButton.on('pointerout', () => {
      this.resetButton.setScale(1);
    });
  }

  private createFullscreenButton(): void {
    const screenWidth = this.cameras.main.width;
    const screenHeight = this.cameras.main.height;
    const buttonX = screenWidth - 50;
    const buttonY = screenHeight - 50;
    const radius = 35;

    this.fullscreenButton = this.add.container(buttonX, buttonY);
    this.fullscreenButton.setScrollFactor(0);
    this.fullscreenButton.setDepth(150);

    // Circle background
    const circle = this.add.graphics();
    circle.fillStyle(0x000000, 0.4);
    circle.fillCircle(0, 0, radius);
    circle.lineStyle(2, 0xffffff, 0.8);
    circle.strokeCircle(0, 0, radius);
    this.fullscreenButton.add(circle);

    // Fullscreen icon (four corners)
    const icon = this.add.graphics();
    icon.lineStyle(3, 0xffffff, 0.9);
    const s = 10; // size
    const g = 5;  // gap from center

    // Top-left corner
    icon.moveTo(-g - s, -g);
    icon.lineTo(-g, -g);
    icon.lineTo(-g, -g - s);

    // Top-right corner
    icon.moveTo(g + s, -g);
    icon.lineTo(g, -g);
    icon.lineTo(g, -g - s);

    // Bottom-left corner
    icon.moveTo(-g - s, g);
    icon.lineTo(-g, g);
    icon.lineTo(-g, g + s);

    // Bottom-right corner
    icon.moveTo(g + s, g);
    icon.lineTo(g, g);
    icon.lineTo(g, g + s);

    icon.strokePath();
    this.fullscreenButton.add(icon);

    // Make interactive
    const hitArea = new Phaser.Geom.Circle(0, 0, radius);
    this.fullscreenButton.setInteractive(hitArea, Phaser.Geom.Circle.Contains);

    this.fullscreenButton.on('pointerdown', () => {
      if (this.resetConfirmOverlay) return;
      this.fullscreenButton.setScale(0.9);

      // Toggle fullscreen
      if (this.scale.isFullscreen) {
        this.scale.stopFullscreen();
      } else {
        this.scale.startFullscreen();
      }
    });

    this.fullscreenButton.on('pointerup', () => {
      this.fullscreenButton.setScale(1);
    });

    this.fullscreenButton.on('pointerout', () => {
      this.fullscreenButton.setScale(1);
    });
  }

  private showResetConfirm(): void {
    if (this.resetConfirmOverlay) return;

    // Record pause start time
    this.pauseStartTime = this.time.now;

    const screenWidth = this.cameras.main.width;
    const screenHeight = this.cameras.main.height;

    this.resetConfirmOverlay = this.add.container(0, 0);
    this.resetConfirmOverlay.setScrollFactor(0);
    this.resetConfirmOverlay.setDepth(300);

    // Dark overlay (also interactive to block input to game)
    const overlay = this.add.rectangle(screenWidth / 2, screenHeight / 2, screenWidth, screenHeight, 0x000000, 0.7);
    overlay.setInteractive();
    this.resetConfirmOverlay.add(overlay);

    // Confirm text
    const confirmText = this.add.text(screenWidth / 2, screenHeight / 2 - 50, 'リセットしますか？', {
      font: 'bold 32px Arial',
      color: '#ffffff'
    }).setOrigin(0.5);
    this.resetConfirmOverlay.add(confirmText);

    // Yes button
    const yesBg = this.add.rectangle(screenWidth / 2 - 80, screenHeight / 2 + 40, 120, 50, 0x44aa44);
    yesBg.setInteractive({ useHandCursor: true });
    yesBg.on('pointerdown', () => {
      try {
        if (this.bgm) {
          this.bgm.stop();
        }
      } catch (e) {
        // Ignore sound errors
      }
      this.resetConfirmOverlay?.destroy();
      this.resetConfirmOverlay = null;
      this.scene.restart();
    });
    this.resetConfirmOverlay.add(yesBg);

    const yesText = this.add.text(screenWidth / 2 - 80, screenHeight / 2 + 40, 'はい', {
      font: 'bold 24px Arial',
      color: '#ffffff'
    }).setOrigin(0.5);
    this.resetConfirmOverlay.add(yesText);

    // No button
    const noBg = this.add.rectangle(screenWidth / 2 + 80, screenHeight / 2 + 40, 120, 50, 0xaa4444);
    noBg.setInteractive({ useHandCursor: true });
    noBg.on('pointerdown', () => {
      this.hideResetConfirm();
    });
    this.resetConfirmOverlay.add(noBg);

    const noText = this.add.text(screenWidth / 2 + 80, screenHeight / 2 + 40, 'いいえ', {
      font: 'bold 24px Arial',
      color: '#ffffff'
    }).setOrigin(0.5);
    this.resetConfirmOverlay.add(noText);
  }

  private hideResetConfirm(): void {
    if (this.resetConfirmOverlay) {
      // Adjust game start time to account for pause duration
      const pauseDuration = this.time.now - this.pauseStartTime;
      this.gameStartTime += pauseDuration;
      this.alienAttackTimer += pauseDuration;

      this.resetConfirmOverlay.destroy();
      this.resetConfirmOverlay = null;
    }
  }

  private setupTouchControls(): void {
    // Support multi-touch
    this.input.addPointer(2);

    this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      // Skip if reset confirm is showing
      if (this.resetConfirmOverlay) return;

      const screenWidth = this.cameras.main.width;
      const screenHeight = this.cameras.main.height;
      const relativeX = pointer.x; // Screen coordinates (not world)
      const relativeY = pointer.y;

      // Check if touching jump button area (skip other controls)
      const jumpButtonX = 80;
      const jumpButtonY = screenHeight - 80;
      const distToJumpButton = Math.sqrt(
        Math.pow(relativeX - jumpButtonX, 2) + Math.pow(relativeY - jumpButtonY, 2)
      );
      if (distToJumpButton < 60) {
        // Jump button handles this
        return;
      }

      // Check if touching fullscreen button area (skip other controls)
      const fullscreenButtonX = screenWidth - 50;
      const fullscreenButtonY = screenHeight - 50;
      const distToFullscreenButton = Math.sqrt(
        Math.pow(relativeX - fullscreenButtonX, 2) + Math.pow(relativeY - fullscreenButtonY, 2)
      );
      if (distToFullscreenButton < 45) {
        // Fullscreen button handles this
        return;
      }

      // Check if touching reset button area (skip other controls)
      const resetButtonX = screenWidth - 80;
      const resetButtonY = 80;
      const distToResetButton = Math.sqrt(
        Math.pow(relativeX - resetButtonX, 2) + Math.pow(relativeY - resetButtonY, 2)
      );
      if (distToResetButton < 60) {
        // Reset button handles this
        return;
      }

      // Show touch indicator
      this.showTouchIndicator(relativeX, relativeY, pointer.id);

      // Lower left = move left
      if (relativeX < screenWidth * 0.3 && relativeY >= screenHeight * 0.5) {
        this.touchLeft = true;
        this.touchRight = false;
      }
      // Lower right = move right
      else if (relativeX > screenWidth * 0.7 && relativeY >= screenHeight * 0.5) {
        this.touchRight = true;
        this.touchLeft = false;
      }
      // Lower center = fire
      else if (relativeY >= screenHeight * 0.5) {
        this.touchFire = true;
      }

      this.lastTouchTime = this.time.now;
    });

    this.input.on('pointerup', (pointer: Phaser.Input.Pointer) => {
      // Skip if reset confirm is showing
      if (this.resetConfirmOverlay) return;

      const screenWidth = this.cameras.main.width;
      const relativeX = pointer.x;

      // Hide touch indicator
      this.hideTouchIndicator(pointer.id);

      // Check which zone was released
      if (relativeX < screenWidth * 0.3) {
        this.touchLeft = false;
      } else if (relativeX > screenWidth * 0.7) {
        this.touchRight = false;
      }

      this.touchJump = false;
      this.touchFire = false;
    });

    this.input.on('pointermove', (pointer: Phaser.Input.Pointer) => {
      // Skip if reset confirm is showing
      if (this.resetConfirmOverlay) return;
      if (!pointer.isDown) return;

      const screenWidth = this.cameras.main.width;
      const screenHeight = this.cameras.main.height;
      const relativeX = pointer.x;
      const relativeY = pointer.y;

      // Update touch indicator position
      this.updateTouchIndicator(relativeX, relativeY, pointer.id);

      // Update movement based on current position (for drag)
      if (relativeY >= screenHeight * 0.5) {
        if (relativeX < screenWidth * 0.3) {
          this.touchLeft = true;
          this.touchRight = false;
        } else if (relativeX > screenWidth * 0.7) {
          this.touchRight = true;
          this.touchLeft = false;
        } else {
          this.touchLeft = false;
          this.touchRight = false;
        }
      }
    });
  }

  private showTouchIndicator(x: number, y: number, pointerId: number): void {
    const indicator = this.add.circle(x, y, 40, 0x000000, 0.3);
    indicator.setScrollFactor(0);
    indicator.setDepth(200);
    indicator.setData('pointerId', pointerId);
    this.touchIndicators.push(indicator);
  }

  private hideTouchIndicator(pointerId: number): void {
    for (let i = this.touchIndicators.length - 1; i >= 0; i--) {
      if (this.touchIndicators[i].getData('pointerId') === pointerId) {
        this.touchIndicators[i].destroy();
        this.touchIndicators.splice(i, 1);
        break;
      }
    }
  }

  private updateTouchIndicator(x: number, y: number, pointerId: number): void {
    for (const indicator of this.touchIndicators) {
      if (indicator.getData('pointerId') === pointerId) {
        indicator.setPosition(x, y);
        break;
      }
    }
  }

  private setupSounds(): void {
    try {
      this.bgm = this.sound.add('bgm', { loop: true, volume: 0.5 });
      this.bgm.play();
    } catch (e) {
      console.warn('BGM not available');
    }

    try {
      this.sounds = {
        pnyo: this.sound.add('pnyo', { volume: 0.7 }),
        alienDestroy: this.sound.add('alien_destroy', { volume: 0.6 }),
        explosion: this.sound.add('explosion', { volume: 0.5 })
      };
    } catch (e) {
      console.warn('Sound effects not available');
      this.sounds = {
        pnyo: { play: () => {} } as Phaser.Sound.BaseSound,
        alienDestroy: { play: () => {} } as Phaser.Sound.BaseSound,
        explosion: { play: () => {} } as Phaser.Sound.BaseSound
      };
    }
  }

  private createInitialPlatforms(): void {
    // Initial ground platforms
    for (let i = 0; i < 5; i++) {
      const ground = new Platform(this, i * 400 + 200, 550, 400, 40);
      this.platforms.push(ground);
    }
    this.lastGroundX = 4 * 400 + 200;

    // Starting platforms
    for (let i = 0; i < 10; i++) {
      this.generatePlatform(200 + i * 150);
    }
    this.lastPlatformX = 200 + 9 * 150;
  }

  private generatePlatform(x: number): void {
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

  private generateAlien(x: number): void {
    const y = Phaser.Math.Between(100, 400);
    const type = Math.random() < 0.1 ? 'red' : 'normal';
    const alien = new Alien(this, x, y, type);
    this.aliens.push(alien);
  }

  private generateApple(x: number, y: number): void {
    const type = Apple.getRandomType();
    const apple = new Apple(this, x, y, type);
    this.apples.push(apple);
  }

  update(time: number, delta: number): void {
    // Skip update if game over or reset confirm is showing
    if (this.isGameOver || this.resetConfirmOverlay) return;

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
    this.handleCollisions();

    // Alien attacks
    this.handleAlienAttacks(time);

    // Cleanup off-screen entities
    this.cleanup();

    // Update UI
    this.updateUI();

    // Update background
    this.background.update(this.cameraX);
  }

  private handleInput(time: number): void {
    const slime = this.slime;

    // Movement (keyboard)
    if (this.cursors.left.isDown) {
      slime.x -= 5;
      slime.facingRight = false;
    }
    if (this.cursors.right.isDown) {
      slime.x += 5;
      slime.facingRight = true;
    }

    // Movement (touch)
    if (this.touchLeft) {
      slime.x -= 5;
      slime.facingRight = false;
    }
    if (this.touchRight) {
      slime.x += 5;
      slime.facingRight = true;
    }

    // Jump (keyboard)
    if (Phaser.Input.Keyboard.JustDown(this.cursors.up)) {
      slime.jump();
    }

    // Fire (keyboard or touch)
    if ((this.spaceKey.isDown || this.touchFire) && slime.canFire(time)) {
      this.fireProjectile(time);
    }
  }

  private fireProjectile(time: number): void {
    const slime = this.slime;
    slime.fire(time);

    const direction = slime.facingRight ? 1 : -1;
    let velocityX: number;
    let velocityY = 0;

    // Upward fire if up is held
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

  private updateSlimePhysics(delta: number): void {
    const slime = this.slime;

    // Gravity
    if (!slime.isPurpleForm) {
      slime.velocityY += 0.8;
    }

    slime.y += slime.velocityY;

    // Update slime
    slime.update(this.time.now, delta);
  }

  private updateCamera(): void {
    // Follow slime (one-directional)
    const targetX = this.slime.x - 200;
    if (targetX > this.cameraX) {
      this.cameraX += (targetX - this.cameraX) * 0.1;
    }
    this.cameras.main.scrollX = this.cameraX;
  }

  private generateContent(): void {
    const screenRight = this.cameraX + 1000;

    // Generate ground (continuous)
    while (this.lastGroundX < screenRight) {
      this.lastGroundX += 400;
      const ground = new Platform(this, this.lastGroundX, 550, 400, 40);
      this.platforms.push(ground);
    }

    // Generate platforms
    while (this.lastPlatformX < screenRight) {
      this.lastPlatformX += Phaser.Math.Between(100, 250);
      this.generatePlatform(this.lastPlatformX);
    }
  }

  private updateEntities(delta: number): void {
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

  private handleCollisions(): void {
    const slime = this.slime;
    const slimeBounds = slime.getBounds();

    // Reset ground state
    slime.isOnGround = false;

    // Platform collisions - collect platforms to launch after loop
    const platformsToLaunch: Platform[] = [];

    for (const platform of this.platforms) {
      const platBounds = platform.getBounds();

      if (Phaser.Geom.Rectangle.Overlaps(slimeBounds, platBounds)) {
        // Check if landing from above
        if (slime.velocityY > 0 && slime.y < platform.y) {
          slime.y = platBounds.y - slime.size * 0.35;
          slime.land();

          // Purple form launches platforms (defer to after loop)
          if (slime.isPurpleForm && !(platform instanceof SpikedPlatform)) {
            platformsToLaunch.push(platform as Platform);
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

    // Launch platforms after loop to avoid modifying array during iteration
    for (const platform of platformsToLaunch) {
      this.launchPlatform(platform);
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

  private circleRectOverlap(circle: Phaser.Geom.Circle, rect: Phaser.Geom.Rectangle): boolean {
    const closestX = Phaser.Math.Clamp(circle.x, rect.x, rect.x + rect.width);
    const closestY = Phaser.Math.Clamp(circle.y, rect.y, rect.y + rect.height);
    const distanceX = circle.x - closestX;
    const distanceY = circle.y - closestY;
    return (distanceX * distanceX + distanceY * distanceY) < (circle.radius * circle.radius);
  }

  private collectApple(apple: Apple): void {
    try {
      this.sounds.pnyo.play();
    } catch (e) {
      // Sound may not be available
    }

    if (apple.appleType === 'green') {
      this.destroyAllAliens();
    } else {
      this.slime.eatApple(apple.appleType);
    }
  }

  private destroyAllAliens(): void {
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

  private destroyAlien(alien: Alien, index: number): void {
    try {
      this.sounds.alienDestroy.play();
    } catch (e) {
      // Sound may not be available
    }

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

  private createExplosion(x: number, y: number, big: boolean = false): void {
    const explosion = big
      ? new BigExplosion(this, x, y)
      : new Explosion(this, x, y);
    this.explosions.push(explosion);
  }

  private launchPlatform(platform: Platform): void {
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

  private handleAlienAttacks(time: number): void {
    // No attacks for first 10 seconds after game start
    if (time - this.gameStartTime < 10000) return;

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

  private cleanup(): void {
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

  private updateUI(): void {
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

  private gameOver(): void {
    if (this.isGameOver) return;
    this.isGameOver = true;

    try {
      if (this.bgm) {
        this.bgm.stop();
      }
    } catch (e) {
      // Ignore sound errors
    }

    this.time.delayedCall(100, () => {
      this.scene.start('GameOverScene', { score: this.score });
    });
  }
}
