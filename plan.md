# Phase 2 Implementation Plan: Economy & Strategic Depth

## Overview
5 tasks that add the core resource management loop — earning gold, spending it on towers, and making strategic choices about what to build and where. This is what transforms the demo into an actual game.

---

## Task 1: Add currency system (gold)

**New global state in `main.py`:**
- `gold = 200` (starting gold)
- Add `gold` to `reset_game()` globals, reset to 200

**Earning gold — changes in `main.py`:**
- In the enemy-exit-screen check loop (`main.py:280-283`), enemies that leak do NOT give gold.
- Need a way to detect enemy *kills* (from projectile damage, not from reaching the end). Currently `enemy.hit()` calls `self.kill()` when health <= 0. The cleanest approach:
  - Add a `reward` property to `Enemy`: `self.reward = health * 2` (set at spawn time based on initial health).
  - Add an `on_kill_callback` to `Enemy.__init__` (a function to call when killed by damage).
  - In `Enemy.hit()`, when health <= 0, call `self.on_kill_callback(self)` before `self.kill()`.
  - In `spawn_enemy()`, pass a callback: `lambda enemy: award_kill(enemy)`.
  - `award_kill(enemy)` adds `enemy.reward` to `gold` and spawns floating text.

**HUD — changes in `main.py`:**
- Update `draw_player_health()` (or create a unified `draw_hud()`) to also render gold.
- Show gold as "Gold: 200" in the top-left HUD bar, below health and wave.
- Use a gold color `(255, 215, 0)` for the gold text.
- Expand the dark background surface to fit all three lines (health, wave, gold).

---

## Task 2: Add tower costs & enforce affordability

**Tower data — changes in `tower.py` `get_towers_data()`:**
- Add `"cost"` field to each tower dict:
  - Cannon: `"cost": 50`
  - Archer Tower: `"cost": 75`
  - (New towers in Task 3 will also have costs)

**Placement gating — changes in `main.py`:**
- In the tower placement click handler (~line 259-265), after `is_valid_position` check, also check `gold >= tower_data["cost"]`. Only place if both pass.
- On successful placement, deduct: `gold -= tower_data["cost"]`.

**Toolbar display — changes in `toolbar.py`:**
- Pass `towers_data` (the full data list) into `Toolbar.__init__` so it has access to cost info.
- In `Toolbar.draw()`, render cost text below each tower icon (e.g., "50g" in small font).
- Accept a `gold` parameter in `Toolbar.draw(screen, gold)`. If the player can't afford a tower, render its cost in red.
- In `main.py`, update the `toolbar.draw(screen)` call to `toolbar.draw(screen, gold)`.

---

## Task 3: Add 2 new tower types

### Sniper Tower (using `assets/towers/tank.png`)
High damage, long range, slow fire rate. The expensive precision option.

**Tower data entry in `tower.py`:**
```python
{
    "name": "Sniper",
    "filename": "assets/towers/tank.png",
    "size": 40,
    "placement_center": (20, 20),
    "tower_base": (20, 20),
    "damage": 5,
    "rotatable": True,
    "angle_threshold": 3,
    "range_radius": 200,
    "cost": 150,
    "slow_duration": 0,
    "slow_factor": 1.0,
}
```

### Freeze Tower (using `assets/towers/tower-2.png`)
Slows enemies on hit. Low damage, but invaluable for buying time.

**Tower data entry in `tower.py`:**
```python
{
    "name": "Freeze Tower",
    "filename": "assets/towers/tower-2.png",
    "size": 50,
    "placement_center": (25, 25),
    "tower_base": (25, 25),
    "damage": 1,
    "rotatable": False,
    "angle_threshold": 365,
    "range_radius": 120,
    "cost": 100,
    "slow_duration": 2000,
    "slow_factor": 0.4,
}
```

### Slow mechanic — changes in `enemy.py`:
- Add to `Enemy.__init__()`:
  ```python
  self.slow_factor = 1.0
  self.slow_end_time = 0
  ```
- Add `Enemy.apply_slow(self, duration_ms, factor)`:
  ```python
  def apply_slow(self, duration_ms, factor):
      self.slow_factor = factor
      self.slow_end_time = pygame.time.get_ticks() + duration_ms
  ```
- In `Enemy.update()`, before `self.move()`, check slow expiry:
  ```python
  if self.slow_factor < 1.0 and pygame.time.get_ticks() > self.slow_end_time:
      self.slow_factor = 1.0
  ```
- In `Enemy.move()`, use `self.speed * self.slow_factor` instead of `self.speed`.

### Projectile slow support — changes in `projectile.py`:
- Add optional params to `Projectile.__init__()`: `slow_duration=0, slow_factor=1.0`
- Store as `self.slow_duration`, `self.slow_factor`
- In `Projectile.update()`, on hit, after `self.target.hit(self.damage)`, add:
  ```python
  if self.slow_duration > 0:
      self.target.apply_slow(self.slow_duration, self.slow_factor)
  ```
  Note: must call apply_slow *before* hit, since hit may kill the enemy. Reorder to: apply_slow first (if target alive), then hit.

### Tower shooting — changes in `tower.py`:
- Add `self.slow_duration` and `self.slow_factor` to `Tower.__init__()`, reading from `tower_data`.
- In `Tower.shoot()`, pass slow params to `Projectile()` constructor.

### Existing tower data — add slow fields:
- Cannon and Archer Tower get `"slow_duration": 0, "slow_factor": 1.0` (no slow effect).

---

## Task 4: Add tower selling

**Right-click detection — changes in `main.py`:**
- In the event handler, add a check for right-click (`event.button == 3`).
- On right-click, iterate `towers` group and check if click position is within any tower's rect.
- If a tower is found:
  - Calculate refund: `int(tower.tower_data["cost"] * 0.6)`
  - Add refund to `gold`
  - Spawn floating text at tower position showing "+Xg"
  - Call `tower.kill()` to remove it

**No toolbar changes needed** — selling is purely via right-click on placed towers.

---

## Task 5: Add floating text for gold rewards

**New floating_texts list in `main.py`:**
- `floating_texts = []` (list of dicts)
- Each entry: `{"text": "+4g", "x": int, "y": float, "timer": int, "color": (R, G, B)}`

**Spawning floating text:**
- `spawn_floating_text(text, x, y, color=(255, 215, 0))` appends to the list with `timer=45` (frames, ~0.75 sec at 60fps).
- Called from `award_kill(enemy)` with enemy's center position.
- Called from tower sell with tower's center position.

**Updating & drawing in main loop:**
- Each frame, iterate `floating_texts`:
  - Decrement `timer`, move `y` upward by 1px
  - Calculate alpha: `int(255 * (timer / 45))`
  - Render text with alpha
  - Remove entries where `timer <= 0`
- Draw after game objects, before overlays.

**Reset:**
- Clear `floating_texts` in `reset_game()`.

---

## Implementation Order

1. **Task 1** — Currency system (gold variable, kill callback, HUD display)
2. **Task 2** — Tower costs (data, placement gating, toolbar cost labels)
3. **Task 3** — New tower types + slow mechanic (enemy.py, projectile.py, tower.py)
4. **Task 5** — Floating text (visual feedback system, used by tasks 1 & 4)
5. **Task 4** — Tower selling (right-click handler, refund logic)

Tasks 1 & 2 form the core economy. Task 3 adds strategic variety. Tasks 4 & 5 round out the UX. Task 5 is listed before 4 because the sell feedback uses floating text.

## Files Changed

| File | Changes |
|------|---------|
| `main.py` | Gold state, HUD, kill callback, placement cost check, sell handler, floating text system |
| `tower.py` | Cost field on all towers, slow fields, pass slow to projectiles |
| `enemy.py` | Reward property, on_kill callback, slow_factor/slow_end_time, apply_slow() |
| `projectile.py` | Slow params, apply slow on hit |
| `toolbar.py` | Accept towers_data + gold, show cost labels, red text if unaffordable |

## Balance Summary

| Tower | Damage | Range | Cooldown | Cost | Special |
|-------|--------|-------|----------|------|---------|
| Cannon | 2 | 100 | 500ms | 50g | Rotates to aim |
| Archer Tower | 1 | 70 | 500ms | 75g | Fires 360 degrees |
| Freeze Tower | 1 | 120 | 800ms | 100g | Slows enemy to 40% speed for 2s |
| Sniper | 5 | 200 | 1500ms | 150g | Long range, must aim precisely |

Starting gold: 200 | Kill reward: `enemy_initial_health * 2` gold | Sell refund: 60% of cost
