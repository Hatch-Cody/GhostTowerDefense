# Ghost Tower Defense - MVP Roadmap

## Current State Assessment

### What Works
The game is a **runnable proof-of-concept** built with Python/Pygame. The core tower defense loop exists: players place towers, start waves, and watch towers shoot homing projectiles at enemies walking a fixed path.

| System | Status |
|--------|--------|
| Game window & rendering | Working (800x600, 60 FPS) |
| Tower placement with collision checks | Working |
| 2 tower types (Cannon, Archer) | Working |
| 13 enemy health tiers with visual damage | Working |
| Homing projectile system | Working |
| Waypoint-based enemy pathing | Working (but 3x speed bug) |
| 25 escalating waves | Working |
| Manual wave start via toolbar | Working |
| Health HUD & wave counter | Working |
| Placement range preview (valid/invalid) | Working |

### Critical Bugs (Must Fix)

1. **Triple enemy update** (`main.py:245,249,253`) — `enemies.update()` is called 3 times per frame, making enemies move 3x faster than intended.
2. **Tower damage ignored** (`main.py:244`) — Global `projectile_damage=1` is passed to all towers, overriding the per-tower damage values (Cannon should deal 2).
3. **Reset doesn't restore wave data** (`main.py:174`) — `wave_data` enemy counts are mutated in-place during spawning. After reset, waves are already depleted.
4. **No game-over condition** — Health goes negative with no consequence or feedback.
5. **Debug print statements** (`main.py:156,233`) — `print(rect_points)` on startup, `print('adding tower')` on every placement.
6. **Duplicate `resize_image`** (`main.py:86`) — Shadows the imported `utils.resize_image`.

### What's Missing for a Fun Game

- **No economy** — Towers are free, kills earn nothing. No resource decisions = no strategy.
- **No win/lose screens** — Game just continues or prints to console.
- **Only 2 tower types** — Not enough variety for strategic depth (assets for more exist but are unwired).
- **No enemy health bars** — Can't tell how much HP an enemy has left.
- **No tower info** — No way to see a tower's stats, range, or damage.
- **No tower selling** — Misplaced towers are permanent.
- **No audio** — Silent gameplay.
- **No score/stats** — No sense of accomplishment or progress tracking.

---

## MVP Roadmap

The roadmap is organized into **4 phases**, ordered by impact on gameplay. Each phase builds on the previous and results in a meaningfully better game.

---

### Phase 1: Fix Critical Bugs & Core Loop

**Goal:** Make the existing game work correctly.

- [ ] **Fix triple enemy update** — Remove the duplicate `enemies.update()` calls at lines 249 and 252-256. Consolidate enemy exit/health-loss logic into a single pass.
- [ ] **Fix tower damage** — Pass each tower's `self.damage` to `self.shoot()` instead of the global `projectile_damage`. Remove the global `projectile_damage` variable.
- [ ] **Fix reset** — Deep-copy `wave_data` on load so reset can restore original values. Also reset `player_health`, `wave`, and `current_wave`.
- [ ] **Add game-over state** — When `player_health <= 0`, stop gameplay and show a "Game Over" overlay with a restart option.
- [ ] **Add win state** — After wave 25 completes with health > 0, show a "Victory" overlay.
- [ ] **Remove debug prints** — Delete `print(rect_points)` and `print('adding tower')`.
- [ ] **Remove dead code** — Delete the duplicate `resize_image` in main.py, the unused `take_damage()` in enemy.py, and the orphaned `angle_diff()` in tower.py.

---

### Phase 2: Economy & Strategic Depth

**Goal:** Add the core resource management that makes tower defense fun — choosing *which* towers to build and *where* to spend limited money.

- [ ] **Add currency system** — Start with a gold amount (e.g., 200). Earn gold per kill (scaled to enemy health). Display gold in the HUD.
- [ ] **Add tower costs** — Each tower type has a gold cost. Show cost on toolbar tower icons. Block placement if insufficient gold.
- [ ] **Add 2 more tower types** — Use existing unused assets (tank.png, etc.) or generate new ones. Suggestions:
  - **Sniper Tower** — Long range, high damage, slow fire rate. Expensive.
  - **Freeze Tower** — Slows enemies in radius. Low/no damage. Medium cost.
- [ ] **Add tower selling** — Right-click or sell button to remove a placed tower and refund a portion of its cost (e.g., 60%).
- [ ] **Add enemy kill rewards display** — Brief floating "+X gold" text when enemies die.

---

### Phase 3: Visual Feedback & Polish

**Goal:** Give players the information they need to make good decisions and make the game *feel* good.

- [ ] **Enemy health bars** — Small bar above each enemy showing remaining HP.
- [ ] **Tower info panel** — Click a placed tower to see its stats (damage, range, fire rate) in the toolbar area. Show its range circle.
- [ ] **Tower range on placement** — Already partially working; ensure range circle is visible and accurate using actual tower range values.
- [ ] **Wave preview** — Show upcoming wave composition (enemy types/counts) before clicking Start.
- [ ] **Damage numbers** — Floating damage text when projectiles hit.
- [ ] **Improved HUD** — Show wave progress (e.g., "Wave 3/25"), gold, health in a clean top bar.
- [ ] **Start screen** — Simple title screen with a "Play" button instead of launching directly into gameplay.
- [ ] **Pause functionality** — Press Escape or a pause button to pause/resume.

---

### Phase 4: Progression & Replayability

**Goal:** Give players reasons to keep playing and improve.

- [ ] **Tower upgrades** — Click a placed tower to upgrade it (increase damage, range, or fire rate) for gold. 2-3 upgrade tiers per tower.
- [ ] **Score system** — Track score based on kills, wave completion, and remaining health. Show end-of-game score.
- [ ] **Difficulty scaling** — Enemies get slight speed increases in later waves. Maybe a "Fast Forward" button to speed up easy waves.
- [ ] **Sound effects** — Tower shooting, enemy death, wave start/complete, game over. Even basic sounds dramatically improve feel.
- [ ] **Multiple maps** — Define 2-3 different path layouts that players can select.

---

## Architecture Notes

The current monolithic `main.py` approach works fine for MVP scope. A few structural improvements to consider as complexity grows:

- **Game state manager** — A simple state enum (`MENU`, `PLAYING`, `PAUSED`, `GAME_OVER`, `VICTORY`) with corresponding update/draw functions would clean up the main loop significantly. This is the most impactful refactor.
- **Move `gameData.json` to be the source of truth** — Currently tower/enemy data lives in static Python methods AND an unused JSON file. Pick one. JSON is more flexible for balance tuning.
- **Event system** — As more systems need to react to events (enemy killed, wave complete, tower placed), a simple event bus would reduce coupling between systems.

These are not prerequisites for the MVP — they're suggested if the main loop starts feeling unwieldy.

---

## Priority Summary

| Priority | Item | Impact |
|----------|------|--------|
| **P0** | Fix triple update, tower damage, reset bugs | Game is broken without these |
| **P0** | Game over / win conditions | No complete game loop without these |
| **P1** | Currency + tower costs | Core strategic gameplay |
| **P1** | 2 more tower types | Strategic variety |
| **P1** | Tower selling | Correcting mistakes |
| **P2** | Enemy health bars | Essential visual feedback |
| **P2** | Tower info panel | Player needs to understand tools |
| **P2** | Start screen + pause | Basic UX expectations |
| **P3** | Tower upgrades | Depth & progression |
| **P3** | Score system | Motivation & replayability |
| **P3** | Sound effects | Game feel |
| **P3** | Multiple maps | Variety |
