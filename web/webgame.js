(() => {
  const C = window.GAME_CONFIG;
  const canvas = document.querySelector("#game"), ctx = canvas.getContext("2d");
  const startScreen = document.querySelector("#start-screen"), endScreen = document.querySelector("#end-screen");
  const endTitle = document.querySelector("#end-title"), endMessage = document.querySelector("#end-message");
  const guideScreen = document.querySelector("#guide-screen"), pauseScreen = document.querySelector("#pause-screen");
  canvas.width = C.display.width; canvas.height = C.display.height;
  document.title = C.text.pageTitle;
  document.querySelector('meta[name="description"]').content = C.text.description;
  const copy = (id, value) => { document.querySelector(`#${id}`).textContent = value; };
  [["eyebrow", C.text.eyebrow], ["site-title", C.text.title], ["tagline", C.text.tagline], ["start-title", C.text.startTitle], ["start-message", C.text.startMessage], ["start-button", C.text.startButton], ["guide-title", C.text.guideTitle], ["close-guide-button", C.text.guideBack], ["pause-title", C.text.pauseTitle], ["pause-message", C.text.pauseMessage], ["resume-button", C.text.resumeButton], ["restart-button", C.text.restartButton], ["legal-copyright", C.text.legalCopyright], ["legal-assets", C.text.legalAssets]].forEach(([id, value]) => copy(id, value));
  const controlsHtml = C.controls.map(line => `<p>${line}</p>`).join("");
  document.querySelector("#full-guide").innerHTML = controlsHtml;
  document.querySelector("#start-guide").innerHTML = `<h3>${C.text.guideTitle}</h3>${controlsHtml}<p class="guide-tip">${C.text.guideTip}</p>`;
  document.querySelector("#controls-summary").innerHTML = C.controls.slice(0, 4).map(line => `<span>${line}</span>`).join("");
  endTitle.textContent = C.text.failedTitle;
  const W = C.display.width, H = C.display.height, TILE = C.display.tileSize, GRAVITY = C.physics.gravity;
  const keys = new Set(), images = new Map();
  const audio = { jump: new Audio("/assets/audio/jump.wav"), shot: new Audio("/assets/audio/shot.wav"), grenade: new Audio("/assets/audio/grenade.wav") };
  let world, player, enemies, bullets, grenades, pickups, camera, level = 1, running = false, paused = false, jumpRequested = false, last = 0, shake = 0;

  const image = (path) => {
    if (!images.has(path)) { const asset = new Image(); asset.src = path; images.set(path, asset); }
    return images.get(path);
  };
  const sound = (name) => { const effect = audio[name].cloneNode(); effect.volume = name === "jump" ? .12 : .18; effect.play().catch(() => {}); };
  const drawImage = (asset, x, y, width, height, flip = false) => {
    if (!asset.complete || !asset.naturalWidth) return;
    ctx.save(); if (flip) { ctx.translate(x + width, y); ctx.scale(-1, 1); ctx.drawImage(asset, 0, 0, width, height); } else ctx.drawImage(asset, x, y, width, height); ctx.restore();
  };

  async function loadLevel(number) {
    const response = await fetch(`/assets/levels/level${number}_data.csv`);
    if (!response.ok) throw new Error(C.text.loadErrorMessage);
    const cells = (await response.text()).trim().split(/\r?\n/).map(row => row.split(",").map(Number));
    world = { cells, width: cells[0].length * TILE };
    enemies = []; bullets = []; grenades = []; pickups = []; camera = 0;
    cells.forEach((row, y) => row.forEach((tile, x) => {
      const px = x * TILE, py = y * TILE;
      if (tile === 15) player = actor("player", px, py, C.player.speed, C.player.ammo, C.player.grenades);
      if (tile === 16) enemies.push(actor("enemy", px, py, C.enemy.speed, C.enemy.ammo, 0));
      if (tile >= 17 && tile <= 19) pickups.push({ type: tile, x: px, y: py, w: TILE, h: TILE });
    }));
  }
  const actor = (type, x, y, speed, ammo, grenadesCount) => ({ type, x, y, w: C.player.width, h: C.player.height, speed, ammo, grenades: grenadesCount, health: type === "player" ? C.player.health : C.enemy.health, vy: 0, facing: 1, onGround: false, cooldown: 0, patrol: 0, dead: false, animation: 0, deathFrames: 0 });
  const tileAt = (x, y) => world.cells[Math.floor(y / TILE)]?.[Math.floor(x / TILE)] ?? -1;
  const solidAt = (x, y) => { const tile = tileAt(x, y); return tile >= 0 && tile <= 8; };
  const overlapsSolid = (entity, nx, ny) => solidAt(nx, ny) || solidAt(nx + entity.w - 1, ny) || solidAt(nx, ny + entity.h - 1) || solidAt(nx + entity.w - 1, ny + entity.h - 1);

  function move(entity, dx, isPlayer = false) {
    if (!overlapsSolid(entity, entity.x + dx, entity.y)) entity.x += dx;
    entity.vy = Math.min(entity.vy + GRAVITY, C.physics.maxFallSpeed);
    const nextY = entity.y + entity.vy;
    const leftFoot = entity.x + 2, rightFoot = entity.x + entity.w - 3;
    if (entity.vy >= 0 && (solidAt(leftFoot, nextY + entity.h) || solidAt(rightFoot, nextY + entity.h))) {
      entity.y = Math.floor((nextY + entity.h) / TILE) * TILE - entity.h;
      entity.vy = 0;
      entity.onGround = true;
    } else if (entity.vy < 0 && (solidAt(leftFoot, nextY) || solidAt(rightFoot, nextY))) {
      entity.y = (Math.floor(nextY / TILE) + 1) * TILE;
      entity.vy = 0;
      entity.onGround = false;
    } else {
      entity.y = nextY;
      entity.onGround = false;
    }
    if (tileAt(entity.x + entity.w / 2, entity.y + entity.h - 2) >= 9 && tileAt(entity.x + entity.w / 2, entity.y + entity.h - 2) <= 10) damage(entity, 100);
    if (entity.y > H + 120) damage(entity, 100);
    if (isPlayer) camera = Math.round(Math.max(0, Math.min(world.width - W, entity.x - W * C.world.cameraPlayerOffset)));
  }
  function damage(entity, amount) {
    if (entity.dead) return;
    entity.health -= amount;
    if (entity === player) shake = 9;
    if (entity.health <= 0) { entity.health = 0; entity.dead = true; entity.deathFrames = 0; }
  }
  function fire(shooter) { if (shooter.cooldown || shooter.ammo <= 0 || shooter.dead) return; shooter.cooldown = C.combat.fireCooldownFrames; shooter.ammo--; bullets.push({ x: shooter.x + shooter.w / 2 + shooter.facing * 24, y: shooter.y + 23, vx: shooter.facing * C.combat.bulletSpeed, owner: shooter, life: C.combat.bulletLifetime }); sound("shot"); }
  function throwGrenade() { if (player.grenades <= 0) return; player.grenades--; grenades.push({ x: player.x + player.w / 2, y: player.y, vx: player.facing * C.combat.grenadeSpeed, vy: C.combat.grenadeVelocity, life: C.combat.grenadeLifetime }); sound("grenade"); }
  function rectHit(a, b) { return a.x < b.x + b.w && a.x + (a.w || 7) > b.x && a.y < b.y + b.h && a.y + (a.h || 7) > b.y; }

  function update() {
    if (!running || paused) return;
    if (!player.dead) {
      const direction = (keys.has("KeyD") || keys.has("ArrowRight") ? 1 : 0) - (keys.has("KeyA") || keys.has("ArrowLeft") ? 1 : 0);
      if (direction) player.facing = direction;
      if (jumpRequested && player.onGround) { player.vy = C.physics.jumpVelocity; sound("jump"); }
      jumpRequested = false;
      if (keys.has("KeyF")) fire(player);
      move(player, direction * player.speed, true);
      if (tileAt(player.x + player.w / 2, player.y + player.h / 2) === 20) nextLevel();
      player.animation++;
    }
    enemies.forEach(enemy => {
      if (enemy.dead) { enemy.deathFrames++; return; }
      const dx = player.x - enemy.x, dy = Math.abs(player.y - enemy.y);
      if (Math.abs(dx) < C.enemy.visionDistance && dy < C.enemy.visionHeight && !player.dead) { enemy.facing = dx < 0 ? -1 : 1; fire(enemy); }
      else { if (enemy.patrol++ > C.enemy.patrolFrames) { enemy.patrol = 0; enemy.facing *= -1; } move(enemy, enemy.facing * enemy.speed); }
      enemy.cooldown = Math.max(0, enemy.cooldown - 1); enemy.animation++;
    });
    player.cooldown = Math.max(0, player.cooldown - 1);
    bullets = bullets.filter(bullet => {
      bullet.x += bullet.vx; bullet.life--;
      if (solidAt(bullet.x, bullet.y) || bullet.life <= 0) return false;
      const targets = bullet.owner === player ? enemies : [player];
      const target = targets.find(entity => !entity.dead && rectHit({ ...bullet, w: 7, h: 3 }, entity));
      if (target) { damage(target, bullet.owner === player ? C.combat.playerBulletDamage : C.combat.enemyBulletDamage); return false; }
      return true;
    });
    grenades = grenades.filter(grenade => { grenade.vy += GRAVITY; grenade.x += grenade.vx; grenade.y += grenade.vy; grenade.life--; if (grenade.life > 0) return true; [player, ...enemies].forEach(entity => { if (!entity.dead && Math.hypot(entity.x - grenade.x, entity.y - grenade.y) < C.combat.grenadeRadius) damage(entity, C.combat.grenadeDamage); }); shake = 14; return false; });
    pickups = pickups.filter(box => { if (!rectHit(player, box)) return true; if (box.type === 17) player.ammo += C.world.pickupAmmo; if (box.type === 18) player.grenades += C.world.pickupGrenades; if (box.type === 19) player.health = Math.min(C.player.health, player.health + C.world.pickupHealth); return false; });
    if (player.dead) { player.deathFrames++; if (player.deathFrames > C.world.deathAnimationFrames) finish(false); }
  }
  async function nextLevel() { if (!running) return; if (level === C.world.levelCount) { finish(true); return; } level++; await loadLevel(level); }
  function finish(won) {
    if (!running) return;
    running = false; paused = false;
    if (won) {
      localStorage.setItem(C.storage.achievementKey, "unlocked");
      endTitle.textContent = C.text.achievementTitle;
      endMessage.textContent = C.text.achievementMessage;
    } else {
      endTitle.textContent = C.text.failedTitle;
      endMessage.textContent = C.text.failedMessage;
    }
    endScreen.classList.remove("hidden");
  }

  function render() {
    ctx.fillStyle = "#90c978"; ctx.fillRect(0, 0, W, H);
    ["sky_cloud", "mountain", "pine1", "pine2"].forEach((name, index) => { const asset = image(`/assets/images/background/${name}.png`), y = index === 0 ? 0 : index === 1 ? 120 : index === 2 ? 260 : 380, shift = camera * (.25 + index * .12); for (let x = -shift % 640 - 640; x < W + 640; x += 640) drawImage(asset, x, y, 640, index === 0 ? 640 : 360); });
    world.cells.forEach((row, y) => row.forEach((tile, x) => { if (tile >= 0 && tile <= 14) drawImage(image(`/assets/images/tile/${tile}.png`), x * TILE - camera, y * TILE, TILE, TILE); if (tile === 20) drawImage(image("/assets/images/tile/20.png"), x * TILE - camera, y * TILE, TILE, TILE); }));
    pickups.forEach(box => drawImage(image(`/assets/images/icons/${box.type === 17 ? "ammo_box" : box.type === 18 ? "grenade_box" : "health_box"}.png`), box.x - camera, box.y, TILE, TILE));
    bullets.forEach(bullet => drawImage(image("/assets/images/icons/bullet.png"), bullet.x - camera, bullet.y, 12, 6, bullet.vx < 0));
    grenades.forEach(grenade => drawImage(image("/assets/images/icons/grenade.png"), grenade.x - camera, grenade.y, 16, 16));
    [...enemies, player].forEach(entity => {
      const state = entity.dead ? "death" : entity.onGround && Math.abs(entity.vy) < 1 ? "idle" : "jump";
      const frame = state === "death" ? Math.min(7, Math.floor(entity.deathFrames / 6)) : state === "idle" ? Math.floor(entity.animation / 12) % 5 : 0;
      drawImage(image(`/assets/images/${entity.type}/${state}/${frame}.png`), entity.x - camera - 12, entity.y - 14, 70, 84, entity.facing < 0);
      if (entity.type === "enemy" && !entity.dead) drawHealthBar(entity.x - camera, entity.y - 12, entity.health);
    });
    if (shake) { shake--; ctx.fillStyle = "#f4363630"; ctx.fillRect(0, 0, W, H); }
    ctx.fillStyle = "#151d20"; ctx.fillRect(10, 10, 154, 24); ctx.fillStyle = "#cf3030"; ctx.fillRect(12, 12, 150, 20); ctx.fillStyle = "#35b54a"; ctx.fillRect(12, 12, 150 * player.health / 100, 20);
    ctx.fillStyle = "white"; ctx.font = "22px Trebuchet MS"; ctx.fillText(`${C.text.ammo}: ${player.ammo}`, 10, 62); ctx.fillText(`${C.text.grenades}: ${player.grenades}`, 10, 88); ctx.fillText(`${C.text.sector} ${level}/${C.world.levelCount}`, 670, 32);
  }
  function drawHealthBar(x, y, health) { ctx.fillStyle = "#101415"; ctx.fillRect(x, y, 44, 7); ctx.fillStyle = "#d33c38"; ctx.fillRect(x + 1, y + 1, 42, 5); ctx.fillStyle = "#42be5a"; ctx.fillRect(x + 1, y + 1, 42 * health / 100, 5); }
  function loop(time) { if (time - last > 1000 / 60) { update(); render(); last = time; } requestAnimationFrame(loop); }
  async function start() { level = 1; paused = false; endScreen.classList.add("hidden"); pauseScreen.classList.add("hidden"); await loadLevel(level); running = true; }
  document.querySelector("#start-button").addEventListener("click", () => { startScreen.classList.add("hidden"); start(); });
  document.querySelector("#restart-button").addEventListener("click", () => start());
  document.querySelector("#help-button").addEventListener("click", () => guideScreen.classList.remove("hidden"));
  document.querySelector("#close-guide-button").addEventListener("click", () => guideScreen.classList.add("hidden"));
  document.querySelector("#pause-button").addEventListener("click", () => { if (!running) return; paused = !paused; pauseScreen.classList.toggle("hidden", !paused); });
  document.querySelector("#resume-button").addEventListener("click", () => { paused = false; pauseScreen.classList.add("hidden"); });
  addEventListener("keydown", event => {
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(event.code)) event.preventDefault();
    const wasPressed = keys.has(event.code); keys.add(event.code);
    if (!wasPressed && (event.code === "KeyW" || event.code === "ArrowUp")) jumpRequested = true;
    if (event.code === "KeyQ" && !wasPressed && running && !player.dead) throwGrenade();
    if (event.code === "Escape" && running && !wasPressed) { paused = !paused; pauseScreen.classList.toggle("hidden", !paused); }
  });
  addEventListener("keyup", event => keys.delete(event.code));
  loadLevel(1).then(() => requestAnimationFrame(loop)).catch(error => { endScreen.classList.remove("hidden"); endTitle.textContent = C.text.loadErrorTitle; endMessage.textContent = error.message; });
})();
