## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1724 | 0.18 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2795 | 0.40 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2542 | 0.58 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3784 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3973 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.172) — your mutation base

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

- **Composite score**: 0.172
- **task_score** (E): 0.177
- **fitness_score**: 0.182  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2022 |
| descend_1 | 1.00 | 1.00 | 0.0693 |
| push_1 | 0.00 | 1.00 | 0.0299 |
| retract_1 | 0.67 | 0.67 | 0.1383 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.096, 0.128) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.550 | 3.242 |
| descend_1 | descend | 1.00 / force_exceeded | (0.516, 0.096, 0.128)→(0.505, 0.089, 0.060) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 25.565 | 25.565 |
| push_1 | push | 0.00 / step_budget | (0.505, 0.089, 0.060)→(0.522, 0.077, 0.075) | (0.505, 0.084, 0.034)→(0.496, 0.062, 0.030) | 0.164→0.142 | 1.00 / 3.333 | 340.317 | 981.117 |
| retract_1 | retract | 0.67 / step_budget | (0.522, 0.077, 0.075)→(0.507, -0.052, 0.121) | (0.496, 0.062, 0.030)→(0.501, 0.027, 0.026) | 0.142→0.108 | 0.67 / 0.667 | 0.364 | 438.211 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.319
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.319
- phase_score: 0.328
- phase_breakdown.reach_peg_score: 0.300
- phase_breakdown.reach_goal_score: 0.340

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.324
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.319
- **Median Q (composite search score)**: 0.124
- **K-run variance**: 0.0104
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.207


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04825,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09427,"descend_1.contact_force":3.68107,"descend_1.speed":0.01359,"push_1.push_speed":0.0203},"optimized_scores":{"best_composite_score":0.07935,"best_fitness_score":0.08935,"best_task_score":0.07572},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":829.0,"contact_point_centroid":[0.52509,0.09686,0.05986],"force_p95":340.72476,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":960.77029,"mean_force":312.70683,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52694,0.07984,0.07153]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":856.0,"contact_point_centroid":[0.52628,0.11996,0.04416],"force_p95":313.18222,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":636.83722,"mean_force":170.02673,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52655,0.07927,0.07206]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.51819,0.08527,0.05603],"force_p95":275.98654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":363.41211,"mean_force":123.74554,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51405,0.07828,0.0628]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":589.0,"contact_point_centroid":[0.52502,0.11994,0.05989],"force_p95":292.41893,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":359.31511,"mean_force":192.59129,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53021,0.07424,0.07165]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":512.0,"contact_point_centroid":[0.52916,0.07535,0.05996],"force_p95":276.33382,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.12779,"mean_force":196.79068,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53029,0.07258,0.07152]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.47495,0.11999,0.05998],"force_p95":299.97799,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":301.38812,"mean_force":236.58268,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52978,0.07714,0.07183]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50213,0.07755,0.00927],"force_p95":27.81421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":276.77472,"mean_force":7.72143,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52563,0.07926,0.07143]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.52573,0.07854,0.05815],"force_p95":167.88623,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.71931,"mean_force":26.26911,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51612,0.07971,0.06062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":851.0,"contact_point_centroid":[0.50119,0.06831,0.00922],"force_p95":2.97607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.28699,"mean_force":5.01527,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5268,0.0546,0.07828]},{"body_a":"peg","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.4991,0.07379,0.06381],"force_p95":119.56124,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.88673,"mean_force":75.96774,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52506,0.02846,0.07933]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50594,0.08089,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.74207,"mean_force":0.61314,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51826,0.08898,0.10321]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5217,0.08398,0.0587],"force_p95":30.17969,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.17969,"mean_force":30.17969,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50985,0.08457,0.0604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":344.0,"contact_point_centroid":[0.50559,0.08091,0.00934],"force_p95":0.56748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59112,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51459,0.14382,0.21808]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50063,0.19638,0.29449]}],"total_contact_groups":14},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49885,0.0221,0.02406],"final_tcp_position":[0.50203,-0.06373,0.12889],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":960.77029,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54618,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":380.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52871,0.09379,0.14764],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.08087,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":30.74207,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":456.0,"raw_peak_contact_force":30.74207,"subtask_id":"reach_peg","tcp_end":[0.50983,0.08455,0.06023],"tcp_start":[0.52871,0.09379,0.14764],"tcp_to_object_dist_end":0.02697,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50139,0.07709,0.03383],"object_pos_start":[0.50601,0.08087,0.03378],"object_to_goal_dist_end":0.15722,"object_to_goal_dist_start":0.16111,"object_z_max":0.03439,"peak_contact_force":303.28456,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2767.0,"raw_peak_contact_force":960.77029,"subtask_id":"reach_goal","tcp_end":[0.52864,0.07974,0.07178],"tcp_start":[0.50983,0.08455,0.06023],"tcp_to_object_dist_end":0.0468,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.49885,0.0221,0.02406],"object_pos_start":[0.50139,0.07709,0.03383],"object_to_goal_dist_end":0.10335,"object_to_goal_dist_start":0.15722,"object_z_max":0.04035,"peak_contact_force":0.59217,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2109.0,"raw_peak_contact_force":359.31511,"tcp_end":[0.50203,-0.06373,0.12889],"tcp_start":[0.52864,0.07974,0.07178],"tcp_to_object_dist_end":0.13552,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02586,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08359,"descend_1.contact_force":3.19396,"descend_1.speed":0.02025,"push_1.push_speed":0.02341},"optimized_scores":{"best_composite_score":0.12381,"best_fitness_score":0.13381,"best_task_score":0.13587},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":919.0,"contact_point_centroid":[0.52513,0.0812,0.05997],"force_p95":406.77963,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1100.40905,"mean_force":256.70794,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51384,0.0799,0.0634]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":533.0,"contact_point_centroid":[0.52695,0.11993,0.05999],"force_p95":632.51455,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1092.9802,"mean_force":248.68793,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51369,0.07895,0.06347]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":805.0,"contact_point_centroid":[0.47497,0.11993,0.05997],"force_p95":513.91382,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":796.87768,"mean_force":351.52163,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51455,0.07998,0.06307]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":840.0,"contact_point_centroid":[0.52503,0.08314,0.05999],"force_p95":323.12359,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":528.17344,"mean_force":245.33836,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51486,0.07983,0.0633]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.47495,0.11992,0.05999],"force_p95":424.93003,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":443.66136,"mean_force":340.57081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51364,0.07919,0.06323]},{"body_a":"attachment","body_b":"peg","contact_count":971.0,"contact_point_centroid":[0.50728,0.09469,0.05528],"force_p95":165.96096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":409.29002,"mean_force":96.69438,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51365,0.08052,0.06327]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49252,0.09349,0.00826],"force_p95":165.34429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":322.60314,"mean_force":78.56369,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51383,0.08113,0.06329]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.5264,0.10219,0.05795],"force_p95":191.35856,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":196.96296,"mean_force":34.94599,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51811,0.10177,0.06125]},{"body_a":"peg","body_b":"channel_base_body","contact_count":951.0,"contact_point_centroid":[0.49131,0.09449,0.00877],"force_p95":73.69462,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.38889,"mean_force":49.83426,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51569,0.07686,0.06436]},{"body_a":"peg","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.49318,0.09102,0.06327],"force_p95":151.48147,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.95808,"mean_force":102.60125,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52557,0.03654,0.07683]},{"body_a":"attachment","body_b":"peg","contact_count":715.0,"contact_point_centroid":[0.50586,0.09138,0.05607],"force_p95":89.41486,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.65553,"mean_force":71.45234,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51368,0.08031,0.06224]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":801.0,"contact_point_centroid":[0.47294,0.094,0.03353],"force_p95":65.21375,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.93234,"mean_force":51.52824,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51371,0.07908,0.06354]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":832.0,"contact_point_centroid":[0.47341,0.09564,0.03379],"force_p95":60.72171,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.3393,"mean_force":37.59659,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51454,0.07992,0.06306]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.50592,0.10473,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.29047,"mean_force":0.59724,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51173,0.11124,0.09904]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51869,0.10747,0.05882],"force_p95":21.76456,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.76456,"mean_force":21.76456,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50682,0.10768,0.06057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":328.0,"contact_point_centroid":[0.50553,0.10457,0.00936],"force_p95":0.60002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58082,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50933,0.15537,0.2142]}],"total_contact_groups":17},"final_pose_error":0.06543,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49855,0.04298,0.03039],"final_tcp_position":[0.51694,-0.02929,0.10228],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1100.40905,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55203,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51891,0.11532,0.13942],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10456,0.03384],"object_pos_start":[0.50584,0.1046,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":22.29047,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":428.0,"raw_peak_contact_force":22.29047,"subtask_id":"reach_peg","tcp_end":[0.50681,0.10767,0.0604],"tcp_start":[0.51891,0.11532,0.13942],"tcp_to_object_dist_end":0.02677,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48804,0.092,0.03166],"object_pos_start":[0.50593,0.10456,0.03384],"object_to_goal_dist_end":0.17262,"object_to_goal_dist_start":0.18476,"object_z_max":0.03463,"peak_contact_force":410.99216,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4697.0,"raw_peak_contact_force":1100.40905,"subtask_id":"reach_goal","tcp_end":[0.51374,0.08009,0.06344],"tcp_start":[0.50681,0.10767,0.0604],"tcp_to_object_dist_end":0.04257,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.49855,0.04298,0.03039],"object_pos_start":[0.48804,0.092,0.03166],"object_to_goal_dist_end":0.12336,"object_to_goal_dist_start":0.17262,"object_z_max":0.03908,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4200.0,"raw_peak_contact_force":796.87768,"tcp_end":[0.51694,-0.02929,0.10228],"tcp_start":[0.51374,0.08009,0.06344],"tcp_to_object_dist_end":0.10358,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23889,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04189,"descend_1.contact_force":3.09614,"descend_1.speed":0.02007,"push_1.push_speed":0.03568},"optimized_scores":{"best_composite_score":0.31416,"best_fitness_score":0.32416,"best_task_score":0.31853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":921.0,"contact_point_centroid":[0.52504,0.11993,0.05992],"force_p95":356.23462,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":882.17212,"mean_force":320.50679,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52017,0.07038,0.08903]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52638,0.07324,0.05956],"force_p95":644.59331,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":754.34648,"mean_force":404.11048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51898,0.06556,0.06312]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.51021,0.0769,0.05896],"force_p95":373.6413,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":399.22005,"mean_force":190.75412,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51028,0.06866,0.06179]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.49858,0.02081,0.00817],"force_p95":1.16862,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":317.10935,"mean_force":6.2592,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51982,0.07015,0.08714]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":382.0,"contact_point_centroid":[0.52502,0.11996,0.05995],"force_p95":153.13076,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.44083,"mean_force":123.90065,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52644,0.06331,0.08537]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52641,0.06432,0.05725],"force_p95":114.10143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.37336,"mean_force":28.19073,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5155,0.06513,0.06037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.50323,0.06755,0.00938],"force_p95":0.55063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.66237,"mean_force":0.64417,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49766,0.07615,0.07786]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5095,0.07298,0.05874],"force_p95":23.14861,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.14861,"mean_force":23.14861,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49764,0.07354,0.06043]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,0.03919,0.02423],"force_p95":7.98469,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.04589,"mean_force":3.18156,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52156,0.07099,0.09015]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.503,0.06746,0.00933],"force_p95":0.56866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56616,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49937,0.13844,0.19543]},{"body_a":"peg","body_b":"channel_base_body","contact_count":638.0,"contact_point_centroid":[0.50125,0.01617,0.00801],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72559,"mean_force":0.60557,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52093,0.03419,0.09484]}],"total_contact_groups":11},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50447,0.0165,0.02409],"final_tcp_position":[0.50156,-0.0623,0.13083],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":882.17212,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5505,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":441.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.49996,0.07926,0.09745],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06743,0.0338],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.1476,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":23.66237,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":238.0,"raw_peak_contact_force":23.66237,"subtask_id":"reach_peg","tcp_end":[0.49765,0.07352,0.06029],"tcp_start":[0.49996,0.07926,0.09745],"tcp_to_object_dist_end":0.02773,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.498,0.01608,0.0241],"object_pos_start":[0.50309,0.06743,0.0338],"object_to_goal_dist_end":0.09741,"object_to_goal_dist_start":0.1476,"object_z_max":0.04024,"peak_contact_force":306.67299,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2003.0,"raw_peak_contact_force":882.17212,"subtask_id":"reach_goal","tcp_end":[0.52335,0.07179,0.08884],"tcp_start":[0.49765,0.07352,0.06029],"tcp_to_object_dist_end":0.0891,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50447,0.0165,0.02409],"object_pos_start":[0.498,0.01608,0.0241],"object_to_goal_dist_end":0.0979,"object_to_goal_dist_start":0.09741,"object_z_max":0.0241,"peak_contact_force":0.49887,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1020.0,"raw_peak_contact_force":158.44083,"tcp_end":[0.50156,-0.0623,0.13083],"tcp_start":[0.52335,0.07179,0.08884],"tcp_to_object_dist_end":0.1327,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```