## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2445 | 0.50 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1823 | 0.58 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1338 | 0.05 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1973 | 0.30 | ✅ accepted |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 5 | -0.1008 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.50 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.244) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - -0.03
  - 0.0
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.19
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.19, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.244
- **task_score** (E): 0.503
- **fitness_score**: 0.504  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2005 |
| descend_1 | 1.00 | 1.00 | 0.0684 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.0914 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.116) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.546 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.123, 0.116)→(0.505, 0.116, 0.050) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.556 | 0.560 |
| push_1 | push | 0.00 / guard_failure | (0.501, -0.065, 0.031)→(0.501, -0.065, 0.031) | (0.505, 0.084, 0.034)→(0.500, -0.043, 0.032) | 0.165→0.044 | 1.00 / 2.667 | 74.025 | 74.025 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.065, 0.031)→(0.497, -0.077, 0.121) | (0.500, -0.043, 0.032)→(0.503, -0.040, 0.031) | 0.044→0.044 | 1.00 / 1.000 | 0.548 | 67.983 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.913
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.913
- phase_score: 0.491
- phase_breakdown.reach_goal_score: 0.318
- phase_breakdown.reach_peg_score: 0.894

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.660
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.913
- **Median Q (composite search score)**: 0.210
- **K-run variance**: 0.0133
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.350


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93985,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04707,"descend_1.speed":0.01823,"descend_1.z_target":0.00856,"push_1.push_speed":0.02965},"optimized_scores":{"best_composite_score":0.12335,"best_fitness_score":0.38335,"best_task_score":0.06219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.5082,-0.10018,0.065],"force_p95":117.03274,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.14791,"mean_force":106.99623,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50287,-0.0881,0.03144]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.5079,-0.1003,0.065],"force_p95":83.05964,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.11038,"mean_force":72.92908,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50256,-0.08834,0.03164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":510.0,"contact_point_centroid":[0.49924,0.04429,0.00847],"force_p95":15.78911,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.26038,"mean_force":2.22505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50591,0.0122,0.04426]},{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.50559,0.06811,0.05357],"force_p95":18.05165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.05067,"mean_force":11.6947,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50822,0.07969,0.05309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50559,0.08093,0.00935],"force_p95":0.56159,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5864,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51451,0.15755,0.1957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50058,0.19746,0.29383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":271.0,"contact_point_centroid":[0.49876,0.03675,0.00807],"force_p95":0.69723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81755,"mean_force":0.60435,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49879,-0.08416,0.07475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":103.0,"contact_point_centroid":[0.50613,0.08079,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5211,0.1165,0.08484]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.0155,0.02414],"force_p95":0.46483,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46483,"mean_force":0.46483,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50165,-0.08722,0.0335]}],"total_contact_groups":9},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50049,0.03641,0.02414],"final_tcp_position":[0.49734,-0.08073,0.12021],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":118.14791,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54466,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":421.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52882,0.1194,0.1038],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":103.0,"raw_peak_contact_force":0.5501,"subtask_id":"reach_peg","tcp_end":[0.51179,0.11336,0.06104],"tcp_start":[0.52882,0.1194,0.1038],"tcp_to_object_dist_end":0.04282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.49714,0.03705,0.02405],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.11816,"object_to_goal_dist_start":0.16109,"object_z_max":0.04079,"peak_contact_force":118.14791,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":584.0,"raw_peak_contact_force":118.14791,"subtask_id":"reach_goal","tcp_end":[0.50288,-0.08845,0.03139],"tcp_start":[0.50287,-0.08827,0.03142],"tcp_to_object_dist_end":0.12584,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":271.0,"n_steps_budget":690.0,"object_pos_end":[0.50049,0.03641,0.02414],"object_pos_start":[0.49714,0.03705,0.02405],"object_to_goal_dist_end":0.11749,"object_to_goal_dist_start":0.11817,"object_z_max":0.02438,"peak_contact_force":0.6192,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":281.0,"raw_peak_contact_force":83.11038,"tcp_end":[0.49734,-0.08073,0.12021],"tcp_start":[0.50288,-0.08845,0.03139],"tcp_to_object_dist_end":0.15153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0073,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08674,"descend_1.speed":0.02548,"descend_1.z_target":-0.00932,"push_1.push_speed":0.02695},"optimized_scores":{"best_composite_score":0.2104,"best_fitness_score":0.4704,"best_task_score":0.53372},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.50633,-0.10074,0.0635],"force_p95":56.7566,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.0684,"mean_force":38.5707,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49771,-0.05791,0.06308]},{"body_a":"attachment","body_b":"peg","contact_count":234.0,"contact_point_centroid":[0.50119,-0.06765,0.06114],"force_p95":56.94354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.61782,"mean_force":42.84632,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49774,-0.05688,0.05951]},{"body_a":"attachment","body_b":"peg","contact_count":247.0,"contact_point_centroid":[0.50357,0.02551,0.04384],"force_p95":27.12887,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.47336,"mean_force":5.82314,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50228,0.03715,0.03529]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50648,-0.10051,0.06054],"force_p95":48.96101,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.09654,"mean_force":35.88583,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50228,-0.05329,0.03063]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":54.0,"contact_point_centroid":[0.47462,-0.00131,0.03228],"force_p95":26.7752,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.16193,"mean_force":6.13574,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50215,0.02712,0.03462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":212.0,"contact_point_centroid":[0.50098,0.00505,0.00957],"force_p95":20.26225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.52831,"mean_force":4.77054,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5024,0.04276,0.03571]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":116.0,"contact_point_centroid":[0.52516,0.01559,0.03224],"force_p95":19.26437,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.72935,"mean_force":3.54592,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50235,0.04588,0.03584]},{"body_a":"peg","body_b":"channel_base_body","contact_count":44.0,"contact_point_centroid":[0.49697,-0.07303,0.00858],"force_p95":3.95499,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.10901,"mean_force":1.21268,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49788,-0.0713,0.10324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50533,0.10473,0.00936],"force_p95":0.60312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58461,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5093,0.16937,0.21632]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50039,0.19797,0.29472]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.52518,-0.07718,0.0194],"force_p95":1.925,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29946,"mean_force":0.70404,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49727,-0.07298,0.11153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.50584,0.10459,0.00939],"force_p95":0.57505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54628,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51175,0.13871,0.0962]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,-0.07982,0.03239],"force_p95":0.53712,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57544,"mean_force":0.27476,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49657,-0.05605,0.062]}],"total_contact_groups":13},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,-0.07775,0.03455],"final_tcp_position":[0.49721,-0.07573,0.12096],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":60.0684,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10469,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54799,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":328.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51872,0.14226,0.1438],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03383],"object_pos_start":[0.50599,0.10469,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":0.57517,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":207.0,"raw_peak_contact_force":0.57941,"subtask_id":"reach_peg","tcp_end":[0.5054,0.13538,0.0445],"tcp_start":[0.51872,0.14226,0.1438],"tcp_to_object_dist_end":0.03248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.5047,-0.08331,0.03562],"object_pos_start":[0.50597,0.10471,0.03383],"object_to_goal_dist_end":0.00723,"object_to_goal_dist_start":0.18491,"object_z_max":0.04175,"peak_contact_force":55.47336,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":634.0,"raw_peak_contact_force":55.47336,"subtask_id":"reach_goal","tcp_end":[0.50225,-0.05414,0.03053],"tcp_start":[0.50227,-0.05394,0.03057],"tcp_to_object_dist_end":0.02972,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":328.0,"n_steps_budget":720.0,"object_pos_end":[0.50684,-0.07775,0.03455],"object_pos_start":[0.50468,-0.08352,0.03558],"object_to_goal_dist_end":0.00903,"object_to_goal_dist_start":0.00734,"object_z_max":0.06878,"peak_contact_force":0.63013,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":576.0,"raw_peak_contact_force":60.0684,"tcp_end":[0.49721,-0.07573,0.12096],"tcp_start":[0.50225,-0.05414,0.03053],"tcp_to_object_dist_end":0.08697,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29268,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04433,"descend_1.speed":0.04237,"descend_1.z_target":-0.00984,"push_1.push_speed":0.02511},"optimized_scores":{"best_composite_score":0.39969,"best_fitness_score":0.65969,"best_task_score":0.91332},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":223.0,"contact_point_centroid":[0.4961,-0.06767,0.06175],"force_p95":59.22931,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.76958,"mean_force":41.94587,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49563,-0.05642,0.06105]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.49558,-0.10068,0.06293],"force_p95":59.04221,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.68537,"mean_force":37.41729,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49573,-0.05757,0.06489]},{"body_a":"attachment","body_b":"peg","contact_count":211.0,"contact_point_centroid":[0.49979,0.01566,0.04508],"force_p95":31.29804,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.45355,"mean_force":4.81213,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49698,0.02735,0.03577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49527,-0.10047,0.05936],"force_p95":40.74192,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.91959,"mean_force":16.2324,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,-0.05194,0.0321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":213.0,"contact_point_centroid":[0.50214,-0.01398,0.00957],"force_p95":14.07392,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.80763,"mean_force":3.94973,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49716,0.02241,0.03566]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52524,0.0187,0.03677],"force_p95":29.37623,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.86907,"mean_force":8.86699,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49678,0.04762,0.03686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":46.0,"contact_point_centroid":[0.50298,-0.0758,0.00807],"force_p95":4.78842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.04593,"mean_force":1.63692,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49684,-0.0694,0.09712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.503,0.06741,0.00932],"force_p95":0.5828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56794,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4994,0.15256,0.19739]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47485,-0.03756,0.05866],"force_p95":1.64336,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65241,"mean_force":0.83996,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49738,-0.00468,0.03418]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52507,-0.07783,0.05466],"force_p95":0.75841,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78958,"mean_force":0.50541,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49662,-0.07446,0.11735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":123.0,"contact_point_centroid":[0.50342,0.06753,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49896,0.10343,0.07337]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.4749,-0.08227,0.02071],"force_p95":0.19224,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21492,"mean_force":0.07777,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49478,-0.05443,0.04935]}],"total_contact_groups":12},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50187,-0.07867,0.03542],"final_tcp_position":[0.49677,-0.07554,0.12102],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":60.76958,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54516,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49996,0.10709,0.10118],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.5464,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":123.0,"raw_peak_contact_force":0.55115,"subtask_id":"reach_peg","tcp_end":[0.49909,0.09979,0.04316],"tcp_start":[0.49996,0.10709,0.10118],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.49904,-0.08228,0.03534],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.00527,"object_to_goal_dist_start":0.14759,"object_z_max":0.03971,"peak_contact_force":48.45355,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":482.0,"raw_peak_contact_force":48.45355,"subtask_id":"reach_goal","tcp_end":[0.4982,-0.05323,0.03201],"tcp_start":[0.49821,-0.05302,0.03205],"tcp_to_object_dist_end":0.02925,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":314.0,"n_steps_budget":720.0,"object_pos_end":[0.50187,-0.07867,0.03542],"object_pos_start":[0.49904,-0.08232,0.03544],"object_to_goal_dist_end":0.00512,"object_to_goal_dist_start":0.00521,"object_z_max":0.07112,"peak_contact_force":0.39365,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":534.0,"raw_peak_contact_force":60.76958,"tcp_end":[0.49677,-0.07554,0.12102],"tcp_start":[0.4982,-0.05323,0.03201],"tcp_to_object_dist_end":0.0858,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```