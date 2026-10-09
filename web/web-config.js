window.GAME_CONFIG = {
  display: { width: 800, height: 640, targetFps: 60, tileSize: 40 },
  physics: { gravity: 0.75, maxFallSpeed: 11, jumpVelocity: -14 },
  player: { speed: 5, health: 100, ammo: 20, grenades: 5, width: 42, height: 58 },
  enemy: { speed: 2, health: 100, ammo: 20, visionDistance: 190, visionHeight: 55, patrolFrames: 75 },
  combat: { fireCooldownFrames: 18, bulletSpeed: 11, bulletLifetime: 100, playerBulletDamage: 25, enemyBulletDamage: 5, grenadeSpeed: 7, grenadeVelocity: -11, grenadeLifetime: 85, grenadeDamage: 50, grenadeRadius: 90 },
  world: { levelCount: 3, cameraPlayerOffset: 0.35, deathAnimationFrames: 45, pickupAmmo: 15, pickupGrenades: 3, pickupHealth: 25 },
  storage: { achievementKey: "quantum-squad-vanguard" },
  text: {
    pageTitle: "Quantum Squad Shooter",
    description: "Quantum Squad Shooter - a browser-based side-scrolling action game.",
    eyebrow: "QUANTUM SQUAD PRESENTS", title: "SHOOTER", tagline: "Can you survive the hostile mountain pass?",
    startTitle: "READY FOR DEPLOYMENT?", startMessage: "Clear all three sectors. Watch your health.", startButton: "START MISSION",
    guideTitle: "GUIDE", guideTip: "Reach the exit in Sector 3 to unlock the Quantum Vanguard achievement.", guideBack: "BACK TO GAME",
    pauseTitle: "MISSION PAUSED", pauseMessage: "Take a breath, then get back to the action.", resumeButton: "RESUME",
    restartButton: "TRY AGAIN", failedTitle: "MISSION FAILED", failedMessage: "Your health was depleted. Regroup and try again.",
    completionTitle: "MISSION COMPLETE", completionMessage: "All sectors secured. Quantum Squad wins.",
    achievementTitle: "ACHIEVEMENT UNLOCKED", achievementMessage: "Quantum Vanguard - all three sectors secured. Your achievement is saved on this browser.",
    loadErrorTitle: "LOAD ERROR", loadErrorMessage: "Unable to load the requested level.", ammo: "AMMO", grenades: "GRENADES", sector: "SECTOR",
    legalCopyright: "© 2024 Quantum Squad. Educational project - not for commercial redistribution without permission.",
    legalAssets: "All assets used in this game are either original, free for commercial use, or used with permission. See the README for details."
  },
  controls: ["A / D or Left/Right Arrow Keys - Move Forward and Backward", "W or Up Arrow - Jump", "F - Fire", "Q - Throw grenade", "Esc or Ⅱ - Pause or resume"]
};
