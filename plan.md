# Phase 1 Implementation Plan: Fix Critical Bugs & Complete Game Loop

## Overview
7 tasks that transform the game from a buggy proof-of-concept into a correctly functioning game with a complete play-through loop (start → play → win/lose → restart).

---

## Task 1: Fix triple enemy update

**Problem:** `enemies.update()` is called 3 times per frame in `main.py` — at lines 245, 249, and inside the loop at line 253. Enemies move 3x their intended speed.

**Changes in `main.py`:**
- Keep line 245 (`enemies.update()`) as the single update call
- Delete line 249 (`enemies.update()` under "Move game objects")
- In the loop at lines 252-256, remove the `enemy.update()` call but keep the screen-exit health check. The loop becomes:
  ```python
  for enemy in enemies.sprites():
      if enemy.rect.right >= SCREEN_WIDTH - 80:
          player_health -= enemy.health
          enemy.kill()
  ```

---

## Task 2: Fix tower damage being ignored

**Problem:** `main.py:244` passes global `projectile_damage = 1` to `towers.update()`, which forwards it to `shoot()`. Each tower's `self.damage` (Cannon=2, Archer=1) is never used for projectile creation.

**Changes in `tower.py`:**
- In `Tower.update()` (line 101): remove `projectile_damage` from the signature. Change signature to `update(self, enemies, projectile_image, projectile_speed)`.
- In `Tower.update()` (line 128): pass `self.damage` to `shoot()` instead of the parameter:
  ```python
  self.shoot(target, projectile_image, projectile_speed, self.damage)
  ```

**Changes in `main.py`:**
- Line 244: remove `projectile_damage` from the call:
  ```python
  towers.update(enemies, projectile_image, projectile_speed)
  ```
- Delete the global `projectile_damage = 1` variable (line 31), since it's no longer used anywhere (projectile speed is still needed and stays).

---

## Task 3: Fix reset not restoring wave data

**Problem:** `spawn_enemy()` mutates `wave_data[wave-1]["enemies"][i]["num"]` in-place by decrementing it. After `reset_game()`, the wave data still shows depleted counts. Also, reset doesn't restore `player_health`, `wave`, or `enemies_remaining`.

**Changes in `main.py`:**
- After loading wave data (line 33), store an immutable original copy:
  ```python
  import copy
  _original_wave_data = wave_data()
  wave_data = copy.deepcopy(_original_wave_data)
  ```
- In `reset_game()`, add restoration of all game state:
  ```python
  def reset_game():
      global enemies, towers, projectiles, last_spawn_time, game_started
      global wave_data, wave, enemies_remaining, player_health
      enemies = pygame.sprite.Group()
      towers = pygame.sprite.Group()
      projectiles = pygame.sprite.Group()
      last_spawn_time = 0
      game_started = False
      wave = 0
      enemies_remaining = 0
      player_health = 100
      wave_data = copy.deepcopy(_original_wave_data)
  ```

---

## Task 4: Add game-over state

**Problem:** When `player_health` drops to 0 or below, the game continues indefinitely with a negative health number.

**Changes in `main.py`:**
- Add a `game_state` variable at the top, with values: `"playing"`, `"game_over"`, `"victory"`. Initialize to `"playing"`.
- In the enemy exit check (the loop from Task 1), after decrementing health, check:
  ```python
  if player_health <= 0:
      player_health = 0
      game_state = "game_over"
  ```
- When `game_state == "game_over"`:
  - Skip enemy spawning, tower/enemy/projectile updates
  - Draw a semi-transparent dark overlay over the game
  - Render "GAME OVER" text centered on screen (large font)
  - Draw a "Restart" button below it
  - On click of the Restart button, call `reset_game()` and set `game_state = "playing"`
- Add a `draw_overlay(screen, title_text, subtitle_text)` helper function that handles the overlay rendering for reuse with the victory screen.

---

## Task 5: Add victory state

**Problem:** After all 25 waves are cleared, the game just prints to console and keeps running.

**Changes in `main.py`:**
- In the main loop, after the enemy exit check, add a victory condition:
  ```python
  if game_state == "playing" and wave >= len(wave_data) and len(enemies) == 0 and enemies_remaining == 0 and game_started:
      game_state = "victory"
  ```
- When `game_state == "victory"`:
  - Use the same overlay approach as game-over
  - Show "VICTORY!" text and a "Play Again" button
  - On click, call `reset_game()` and set `game_state = "playing"`

---

## Task 6: Remove debug print statements

**Changes in `main.py`:**
- Line 156: delete `print(rect_points)`
- Line 233: delete `print('adding tower')`
- Line 236: delete `print(is_valid_pos)`

---

## Task 7: Remove dead code

**Changes in `main.py`:**
- Lines 86-87: delete the duplicate `resize_image` function (the imported one from `utils.py` is sufficient and is already used before line 86)

**Changes in `enemy.py`:**
- Lines 35-38: delete the unused `take_damage()` method (only `hit()` is called by projectiles)

**Changes in `tower.py`:**
- Lines 58-59: delete the unused `angle_diff()` method (never called, also missing `@staticmethod`)

---

## Implementation Order

Tasks 1-3 and 6-7 are independent bug fixes and cleanup — they can be done in any order. Tasks 4 and 5 depend on each other (shared overlay helper) and should be done together. Suggested order:

1. **Task 6** — Remove debug prints (trivial, immediate cleanup)
2. **Task 7** — Remove dead code (trivial, reduces noise)
3. **Task 1** — Fix triple enemy update (critical gameplay bug)
4. **Task 2** — Fix tower damage (critical gameplay bug)
5. **Task 3** — Fix reset (critical usability bug)
6. **Tasks 4 & 5** — Game over + Victory (completes the game loop)

Total: ~7 surgical edits across 3 files (`main.py`, `tower.py`, `enemy.py`), plus the new overlay drawing helper.
