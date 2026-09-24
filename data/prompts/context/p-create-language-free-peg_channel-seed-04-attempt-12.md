## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.0457 | 0.16 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0877 | 0.48 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2445 | 0.50 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1823 | 0.58 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1338 | 0.05 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.046) — your mutation base

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

- **Composite score**: 0.046
- **task_score** (E): 0.161
- **fitness_score**: 0.206  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2005 |
| descend_1 | 1.00 | 1.00 | 0.0673 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.2277 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.117) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.549 | 3.242 |
| descend_1 | descend | 1.00 / force_exceeded | (0.516, 0.123, 0.117)→(0.505, 0.092, 0.060) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 14.085 | 14.085 |
| push_1 | push | 0.00 / guard_failure | (0.504, 0.091, 0.060)→(0.504, 0.091, 0.060) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 44.213 | 44.213 |
| retract_1 | retract | 1.00 / step_budget | (0.504, 0.091, 0.060)→(0.497, -0.125, 0.129) | (0.505, 0.084, 0.034)→(0.499, 0.036, 0.024) | 0.164→0.117 | 1.00 / 1.000 | 0.571 | 37.073 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.309
- alignment_error: None
- force_efficiency: 0.126
- terminal_score: 0.309
- phase_score: 0.300
- phase_breakdown.reach_goal_score: 0.047
- phase_breakdown.reach_peg_score: 0.888

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.304
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.309
- **Median Q (composite search score)**: 0.014
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.306


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10294,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.03081,"descend_1.contact_force":1.99915,"descend_1.speed":0.02619,"push_1.max_push_time":3.09026,"push_1.push_speed":0.04104,"retract_1.retract_push_dist":0.01446,"retract_1.retract_speed":0.03698},"optimized_scores":{"best_composite_score":-0.02012,"best_fitness_score":0.13988,"best_task_score":0.06113},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.52351,0.08272,0.00938],"force_p95":40.71038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.35721,"mean_force":29.21828,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50984,0.09282,0.06004]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.52144,0.09032,0.05854],"force_p95":40.26854,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.9136,"mean_force":28.71728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50984,0.09282,0.06004]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.50153,0.04506,0.00892],"force_p95":26.28869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.37023,"mean_force":4.06939,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50258,0.00703,0.09252]},{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.51546,0.08039,0.064],"force_p95":29.38777,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.89511,"mean_force":17.07537,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50774,0.07747,0.06473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":229.0,"contact_point_centroid":[0.50598,0.08095,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.55308,"mean_force":0.60793,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51857,0.10607,0.07255]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52153,0.08996,0.05874],"force_p95":14.09254,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.09254,"mean_force":14.09254,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51011,0.09322,0.06043]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.5251,0.05444,0.02441],"force_p95":6.90361,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.34657,"mean_force":1.74958,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50112,-0.01126,0.0996]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.50558,0.08086,0.00935],"force_p95":0.56099,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58371,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51451,0.15733,0.18757]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50053,0.19759,0.29377]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47498,0.01243,0.03025],"force_p95":1.27266,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28268,"mean_force":1.18246,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5022,0.01,0.09045]}],"total_contact_groups":10},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49862,0.03289,0.02413],"final_tcp_position":[0.49783,-0.07843,0.12851],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":43.35721,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":449.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52891,0.11878,0.08769],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03377],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":14.55308,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":230.0,"raw_peak_contact_force":14.55308,"subtask_id":"reach_peg","tcp_end":[0.51005,0.09311,0.06034],"tcp_start":[0.52891,0.11878,0.08769],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50609,0.08083,0.03388],"object_pos_start":[0.50599,0.08089,0.03377],"object_to_goal_dist_end":0.16107,"object_to_goal_dist_start":0.16112,"object_z_max":0.03388,"peak_contact_force":43.35721,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":43.35721,"subtask_id":"reach_goal","tcp_end":[0.50964,0.09248,0.05974],"tcp_start":[0.50967,0.09254,0.05979],"tcp_to_object_dist_end":0.02858,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.49862,0.03289,0.02413],"object_pos_start":[0.50609,0.08081,0.03389],"object_to_goal_dist_end":0.11401,"object_to_goal_dist_start":0.16104,"object_z_max":0.04079,"peak_contact_force":0.53264,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":636.0,"raw_peak_contact_force":36.37023,"tcp_end":[0.49783,-0.07843,0.12851],"tcp_start":[0.50964,0.09248,0.05974],"tcp_to_object_dist_end":0.15261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10233,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05421,"descend_1.contact_force":1.43978,"descend_1.speed":0.03011,"push_1.max_push_time":2.96822,"push_1.push_speed":0.05479,"retract_1.retract_push_dist":0.07113,"retract_1.retract_speed":0.03916},"optimized_scores":{"best_composite_score":0.01369,"best_fitness_score":0.17369,"best_task_score":0.11342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49999,0.10645,0.00941],"force_p95":42.06236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.58246,"mean_force":25.86193,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50458,0.11066,0.06006]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.51643,0.11008,0.05858],"force_p95":41.62374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.14289,"mean_force":25.43164,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50458,0.11066,0.06006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":700.0,"contact_point_centroid":[0.50165,0.06453,0.00857],"force_p95":31.43744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.58129,"mean_force":4.0341,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49958,-0.0133,0.09362]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.51072,0.10134,0.06297],"force_p95":36.6719,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.14379,"mean_force":22.24157,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50318,0.09353,0.06364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.50572,0.10451,0.00939],"force_p95":0.57556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.67422,"mean_force":0.59092,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51076,0.12612,0.08485]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51667,0.11036,0.05885],"force_p95":14.24236,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.24236,"mean_force":14.24236,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50482,0.11111,0.06058]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50558,0.10467,0.00936],"force_p95":0.59057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57846,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5093,0.16893,0.20018]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50031,0.1982,0.2946]}],"total_contact_groups":8},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49964,0.05589,0.02406],"final_tcp_position":[0.49733,-0.13409,0.13001],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":45.58246,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54908,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51893,0.14109,0.11192],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10469,0.03383],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":14.67422,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":318.0,"raw_peak_contact_force":14.67422,"subtask_id":"reach_peg","tcp_end":[0.50479,0.11102,0.06044],"tcp_start":[0.51893,0.14109,0.11192],"tcp_to_object_dist_end":0.02737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50571,0.10457,0.03388],"object_pos_start":[0.50584,0.10469,0.03383],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18488,"object_z_max":0.03388,"peak_contact_force":45.58246,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":45.58246,"subtask_id":"reach_goal","tcp_end":[0.50437,0.11021,0.0597],"tcp_start":[0.5044,0.11028,0.05975],"tcp_to_object_dist_end":0.02646,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.49964,0.05589,0.02406],"object_pos_start":[0.5057,0.10453,0.03388],"object_to_goal_dist_end":0.13682,"object_to_goal_dist_start":0.18472,"object_z_max":0.0408,"peak_contact_force":0.52458,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":809.0,"raw_peak_contact_force":37.58129,"tcp_end":[0.49733,-0.13409,0.13001],"tcp_start":[0.50437,0.11021,0.0597],"tcp_to_object_dist_end":0.21754,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6051,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09608,"descend_1.contact_force":2.52897,"descend_1.speed":0.04992,"push_1.max_push_time":2.88119,"push_1.push_speed":0.01296,"retract_1.retract_push_dist":0.09967,"retract_1.retract_speed":0.07816},"optimized_scores":{"best_composite_score":0.14355,"best_fitness_score":0.30355,"best_task_score":0.30947},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49294,0.06347,0.00942],"force_p95":41.01097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.6995,"mean_force":27.1741,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49877,0.07149,0.05999]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51063,0.07106,0.05857],"force_p95":40.61249,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.30491,"mean_force":26.75038,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49877,0.07149,0.05999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":646.0,"contact_point_centroid":[0.49873,0.03117,0.0089],"force_p95":30.59509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.26732,"mean_force":3.86508,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49659,-0.04711,0.09356]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.50555,0.06391,0.06279],"force_p95":36.58541,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.82662,"mean_force":22.5012,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49791,0.05614,0.06343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.50303,0.06745,0.00938],"force_p95":0.55068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.02667,"mean_force":0.56795,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49829,0.09026,0.10373]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51082,0.07135,0.05877],"force_p95":12.54839,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.54839,"mean_force":12.54839,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49896,0.07182,0.06047]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":17.0,"contact_point_centroid":[0.47497,-0.00376,0.02514],"force_p95":9.52317,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.69482,"mean_force":4.41017,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49609,-0.04309,0.09169]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.50309,0.06738,0.00931],"force_p95":0.66028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57344,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49958,0.15369,0.22273]}],"total_contact_groups":8},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49999,0.01795,0.02416],"final_tcp_position":[0.497,-0.16278,0.12975],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":43.6995,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06746,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55165,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":321.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50022,0.10948,0.15139],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06747,0.0338],"object_pos_start":[0.50301,0.06746,0.0338],"object_to_goal_dist_end":0.14763,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":13.02667,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":587.0,"raw_peak_contact_force":13.02667,"subtask_id":"reach_peg","tcp_end":[0.49897,0.07176,0.06035],"tcp_start":[0.50022,0.10948,0.15139],"tcp_to_object_dist_end":0.0272,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.50276,0.06734,0.03394],"object_pos_start":[0.50301,0.06747,0.0338],"object_to_goal_dist_end":0.14749,"object_to_goal_dist_start":0.14763,"object_z_max":0.03394,"peak_contact_force":43.6995,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":43.6995,"subtask_id":"reach_goal","tcp_end":[0.49861,0.07109,0.05967],"tcp_start":[0.49863,0.07115,0.05971],"tcp_to_object_dist_end":0.02633,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.49999,0.01795,0.02416],"object_pos_start":[0.50274,0.0673,0.03393],"object_to_goal_dist_end":0.09922,"object_to_goal_dist_start":0.14745,"object_z_max":0.04078,"peak_contact_force":0.6566,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":755.0,"raw_peak_contact_force":37.26732,"tcp_end":[0.497,-0.16278,0.12975],"tcp_start":[0.49861,0.07109,0.05967],"tcp_to_object_dist_end":0.20934,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```