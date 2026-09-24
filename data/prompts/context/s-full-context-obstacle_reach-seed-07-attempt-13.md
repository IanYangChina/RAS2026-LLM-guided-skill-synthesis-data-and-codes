## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | lift → approach → approach → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0753 | 0.59 | ❌ rejected |
| 12 | lift → approach → approach → approach → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0043 | 0.59 | ❌ rejected |
| 11 | lift → approach → approach → approach → approach | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0043 | 0.59 | ✅ accepted |
| 10 | lift → approach → approach | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.3800 | 0.00 | ❌ rejected |
| 9 | lift → approach → approach | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3056 | 0.59 | ❌ rejected |

**Proposal policy**: task_score is 0.59 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: obstacle_reach
- Frozen realised-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`
- Frozen task target: [0.7125095466604666, 0.039721380096957554, 0.15]
- Goal object position: (0.7125095466604666, 0.039721380096957554, 0.15)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Robot initial TCP position: (0.35, 0.0, 0.32)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.35, 0, 0.32]
objects:
  - name: obstacle_block
    role: obstacle
    dynamics: static
    geometry: box
    dimensions_m: [0.08, 0.3, 0.3]
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_task_target: [0.7125, 0.0397, 0.15]
  frozen_obstacle_position: [0.5, 0, 0.15]
  frozen_targets: {'task_goal': [0.7125095466604666, 0.039721380096957554, 0.15]}
  frozen_obstacles: {'obstacle_block': [0.5, 0.0, 0.15]}
  goal_tolerance_m: 0.02
  force_limit_n: 5
  obstacle_height_m: 0.3
  force_scale_n: 5
  realized_scene_sha256: f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position (0.7125095466604666, 0.039721380096957554, 0.15) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.15) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.075) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: lift_clear
  anchor: world
  offset:
  - 0.35
  - 0.0
  - 0.45
  weight: 0.1
- id: go_side
  anchor: world
  offset:
  - 0.5
  - 0.25
  - 0.45
  weight: 0.2
- id: go_forward
  offset:
  - 0.0
  - 0.21
  - 0.3
  weight: 0.2
- id: align_y
  offset:
  - 0.0
  - 0.0
  - 0.3
  weight: 0.2
- id: final_goal
  weight: 0.3
phases:
- id: lift_z
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.13
    tolerance: 0.01
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    lift_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.13
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: move_side
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.25
    - 0.45
    tolerance: 0.02
  parameters:
    side_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    side_y:
      type: scalar
      range:
      - 0.2
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset.y
        mode: replace
    side_z:
      type: scalar
      range:
      - 0.35
      - 0.55
      default: 0.45
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: go_side
- id: move_forward
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.21
    - 0.3
    tolerance: 0.02
  parameters:
    forward_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    forward_y:
      type: scalar
      range:
      - 0.16
      - 0.3
      default: 0.21
      binds_to:
      - path: target.offset.y
        mode: replace
    forward_z:
      type: scalar
      range:
      - 0.25
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: go_forward
- id: align_y
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_y
- id: descend_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: final_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **lift_z** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.13], tolerance=0.01
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_z_offset: status=consumed; consumers=target.offset.z (replace)
- **move_side** (`approach`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.25, 0.45], tolerance=0.02
  - parameter_bindings:
    - side_speed: status=consumed; consumers=generator.speed (replace)
    - side_y: status=consumed; consumers=target.offset.y (replace)
    - side_z: status=consumed; consumers=target.offset.z (replace)
- **move_forward** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.21, 0.3], tolerance=0.02
  - parameter_bindings:
    - forward_speed: status=consumed; consumers=generator.speed (replace)
    - forward_y: status=consumed; consumers=target.offset.y (replace)
    - forward_z: status=consumed; consumers=target.offset.z (replace)
- **align_y** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.075
- **task_score** (E): 0.585
- **fitness_score**: 0.585  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| lift_z | 1.00 | 0.00 | 0.1307 |
| move_side | 1.00 | 0.00 | 0.3882 |
| move_forward | 1.00 | 0.00 | 0.2459 |
| descend_to_goal | 1.00 | 0.33 | 0.4207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force | Obstacle/contact |
|---|---|---|---|---|---|---|---|---|---|
| lift_z | lift | 1.00 / step_budget | (0.350, -0.000, 0.321)→(0.350, 0.000, 0.452) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| move_side | approach | 1.00 / step_budget | (0.350, 0.000, 0.452)→(0.493, 0.359, 0.446) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| move_forward | approach | 1.00 / step_budget | (0.493, 0.359, 0.446)→(0.733, 0.345, 0.443) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.00 / 0.000 | 0.000 | 0.000 | — |
| descend_to_goal | approach | 1.00 / step_budget | (0.733, 0.345, 0.443)→(0.710, 0.040, 0.158) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.727→0.727 | 0.33 / 0.333 | 54.510 | 58.023 | link5 ↔ obstacle_block/obstacle_block_geom |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.879
- path_efficiency: 0.334
- arc_smoothness: 0.995
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.019
- min_tcp_distance: 0.019
- tcp_proximity_score: 0.878
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.878
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.878
- **Median Q (composite search score)**: 0.368
- **K-run variance**: 0.1713
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 5.3
- **Final σ (mean)**: 0.302


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ee3df1cfa385834280b1b81fd9f0e349b6eb2ac9615126fa1df028e39d9bc447`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c0103a17499c8e8b9aa43b2853a2df398616901e8934c1ef10fa47d87723b50d`; realized-scene SHA-256: `f5f2ee542fad8ea5b5618e39465af4fd2d024325ca55c46b8aecfe9ce333bfb2`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.71251,0.03972,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.71251,0.03972,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95324,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_speed":0.0445,"lift_z.lift_speed":0.10822,"lift_z.lift_z_offset":0.14852,"move_forward.forward_speed":0.0909,"move_forward.forward_y":0.32595,"move_forward.forward_z":0.47213,"move_side.side_speed":0.12321,"move_side.side_y":0.39008,"move_side.side_z":0.43447},"optimized_scores":{"best_composite_score":0.3681,"best_fitness_score":0.8781,"best_task_score":0.8781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0195,"key_states":{"actual_goal_position":[0.71251,0.03972,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.71103,0.05673,0.15941],"realised_goal_position":[0.71251,0.03972,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":789.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_z","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"lift_clear","tcp_end":[0.34956,3e-05,0.45915],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.57707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"go_side","tcp_end":[0.49319,0.37195,0.42947],"tcp_start":[0.34956,3e-05,0.45915],"tcp_to_object_dist_end":0.75235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_forward","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"go_forward_clear","tcp_end":[0.73428,0.32986,0.46044],"tcp_start":[0.49319,0.37195,0.42947],"tcp_to_object_dist_end":0.92734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.72921,"object_to_goal_dist_start":0.72921,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.71103,0.05673,0.15941],"tcp_start":[0.73428,0.32986,0.46044],"tcp_to_object_dist_end":0.73089,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5aed51a381cd066930e6976e6d6ccfd73886636bec948604cbfe8eb976a9a4c5`; realized-scene SHA-256: `4d99f589f09839c4f3a4e389174672e239f050e8ccee110af89dc738cbe9e683`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.6827,0.04873,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.6827,0.04873,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.068,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_speed":0.07823,"lift_z.lift_speed":0.10491,"lift_z.lift_z_offset":0.12399,"move_forward.forward_speed":0.10035,"move_forward.forward_y":0.33465,"move_forward.forward_z":0.45511,"move_side.side_speed":0.14352,"move_side.side_y":0.40473,"move_side.side_z":0.48771},"optimized_scores":{"best_composite_score":-0.51,"best_fitness_score":0.0,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"obstacle_block","body_b":"link5","contact_count":126.0,"contact_point_centroid":[0.53997,0.14696,0.29999],"force_p95":172.42144,"geom_a":"obstacle_block_geom","involves_obstacle":true,"involves_robot_link":true,"involves_task_object":false,"max_force":174.06845,"mean_force":159.47225,"phase_index":3.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.68714,0.07876,0.17466]}],"total_contact_groups":1},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.6827,0.04873,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.68577,0.0645,0.16161],"realised_goal_position":[0.6827,0.04873,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":174.06845,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":666.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_z","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"lift_clear","tcp_end":[0.3494,2e-05,0.43484],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.55782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"go_side","tcp_end":[0.49419,0.38776,0.47935],"tcp_start":[0.3494,2e-05,0.43484],"tcp_to_object_dist_end":0.79016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_forward","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"go_forward_clear","tcp_end":[0.73215,0.33952,0.44842],"tcp_start":[0.49419,0.38776,0.47935],"tcp_to_object_dist_end":0.92325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.70068,"object_to_goal_dist_start":0.70068,"object_z_max":0.0,"peak_contact_force":163.53096,"phase_name":"descend_to_goal","phase_peak_obstacle_force":174.06845,"phase_type":"approach","raw_contact_event_count":126.0,"raw_peak_contact_force":174.06845,"subtask_id":"final_goal","tcp_end":[0.68577,0.0645,0.16161],"tcp_start":[0.73215,0.33952,0.44842],"tcp_to_object_dist_end":0.7075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f024bcb71fae796c72f6d149639f1bf75bdc180037c5c08610261d31ea463257`; realized-scene SHA-256: `fda113aaf8e8c099f2c28b9d9dc98e35a2e52600fa9b3eec61a8dea75fa26f9a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.0,0.15]},{"name":"goal","value":[0.73702,-0.02132,0.15]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":5.0},{"name":"obstacle_height_m","value":0.3},{"name":"force_scale_n","value":5.0}],"object_starts":[],"obstacles":[{"name":"obstacle_block","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,0.0,0.15]}],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.73702,-0.02132,0.15]}],"task_name":"obstacle_reach"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0754,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_goal.descend_speed":0.04996,"lift_z.lift_speed":0.07582,"lift_z.lift_z_offset":0.14983,"move_forward.forward_speed":0.15955,"move_forward.forward_y":0.36797,"move_forward.forward_z":0.43156,"move_side.side_speed":0.13191,"move_side.side_y":0.33421,"move_side.side_z":0.43357},"optimized_scores":{"best_composite_score":0.36772,"best_fitness_score":0.87772,"best_task_score":0.87772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01956,"key_states":{"actual_goal_position":[0.73702,-0.02132,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.73391,-0.00237,0.15372],"realised_goal_position":[0.73702,-0.02132,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":867.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_z","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"lift_clear","tcp_end":[0.34955,3e-05,0.46073],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.57833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"go_side","tcp_end":[0.4921,0.3165,0.42935],"tcp_start":[0.34955,3e-05,0.46073],"tcp_to_object_dist_end":0.72572,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_forward","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"go_forward_clear","tcp_end":[0.73318,0.36558,0.42118],"tcp_start":[0.4921,0.3165,0.42935],"tcp_to_object_dist_end":0.92119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75244,"object_to_goal_dist_start":0.75244,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"final_goal","tcp_end":[0.73391,-0.00237,0.15372],"tcp_start":[0.73318,0.36558,0.42118],"tcp_to_object_dist_end":0.74984,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```