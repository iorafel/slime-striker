import Phaser from 'phaser';

export class ParallaxBackground {
  constructor(scene) {
    this.scene = scene;
    this.layers = [];

    // Layer configurations: [key, speedMultiplier, yOffset]
    const layerConfigs = [
      { key: 'sky_layer1', speed: 0.1, y: 0 },
      { key: 'sky_layer2', speed: 0.3, y: 0 },
      { key: 'mountain_layer', speed: 0.6, y: 0 },
      { key: 'ground_layer', speed: 0.9, y: 0 }
    ];

    for (const config of layerConfigs) {
      try {
        const layer = scene.add.tileSprite(
          400, 300, 800, 600, config.key
        );
        layer.setScrollFactor(0);
        layer.speedMultiplier = config.speed;
        this.layers.push(layer);
      } catch (e) {
        // If image not available, create a colored rectangle
        console.warn(`Could not load ${config.key}, using fallback`);
      }
    }

    // If no layers loaded, create procedural background
    if (this.layers.length === 0) {
      this.createProceduralBackground();
    }
  }

  createProceduralBackground() {
    const graphics = this.scene.add.graphics();

    // Sky gradient
    for (let y = 0; y < 600; y++) {
      const ratio = y / 600;
      const r = Math.floor(135 + (200 - 135) * ratio);
      const g = Math.floor(206 + (220 - 206) * ratio);
      const b = Math.floor(235 + (255 - 235) * ratio);
      graphics.fillStyle(Phaser.Display.Color.GetColor(r, g, b), 1);
      graphics.fillRect(0, y, 800, 1);
    }

    // Mountains
    graphics.fillStyle(0x556677, 1);
    graphics.beginPath();
    graphics.moveTo(0, 600);
    graphics.lineTo(0, 400);
    graphics.lineTo(100, 350);
    graphics.lineTo(200, 400);
    graphics.lineTo(300, 320);
    graphics.lineTo(400, 380);
    graphics.lineTo(500, 300);
    graphics.lineTo(600, 360);
    graphics.lineTo(700, 340);
    graphics.lineTo(800, 380);
    graphics.lineTo(800, 600);
    graphics.closePath();
    graphics.fillPath();

    graphics.setScrollFactor(0);
    this.proceduralBg = graphics;
  }

  update(cameraX) {
    for (const layer of this.layers) {
      layer.tilePositionX = cameraX * layer.speedMultiplier;
    }
  }
}
