## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4417 | 0.72 | ❌ rejected |
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4518 | 0.74 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4356 | 0.71 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4383 | 0.72 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1376 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.761, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=0.442) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.06
  weight: 0.3
- id: descend_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.2
- id: push_to_goal
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_above
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
    - 0.06
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_peg
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.16
      - 0.2
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: retract_home
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.2
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.06], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_home** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.2, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.442
- **task_score** (E): 0.718
- **fitness_score**: 0.752  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1958 |
| descend_to_peg | 1.00 | 0.67 | 0.0755 |
| push_channel | 1.00 | 1.00 | 0.1569 |
| retract_home | 1.00 | 1.00 | 0.3254 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.132, 0.117) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.553 | 2.488 |
| descend_to_peg | descend | 1.00 / step_budget | (0.508, 0.132, 0.117)→(0.505, 0.119, 0.044) | (0.504, 0.095, 0.034)→(0.505, 0.079, 0.037) | 0.175→0.160 | 0.67 / 1.333 | 65.111 | 147.430 |
| push_channel | push | 1.00 / step_budget | (0.505, 0.119, 0.044)→(0.503, -0.038, 0.039) | (0.505, 0.079, 0.037)→(0.498, -0.058, 0.028) | 0.160→0.031 | 1.00 / 3.000 | 95.752 | 141.724 |
| retract_home | retract | 1.00 / step_budget | (0.503, -0.038, 0.039)→(0.498, 0.183, 0.278) | (0.498, -0.058, 0.028)→(0.505, -0.052, 0.024) | 0.031→0.035 | 1.00 / 1.000 | 0.667 | 66.470 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.858
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.858
- phase_score: 0.833
- phase_breakdown.approach_peg_score: 0.676
- phase_breakdown.push_to_goal_score: 0.897
- phase_breakdown.descend_peg_score: 0.905

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.843
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.858
- **Median Q (composite search score)**: 0.419
- **K-run variance**: 0.0045
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.320


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15249,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06746,"descend_to_peg.descend_speed":0.04504,"push_channel.insert_depth":0.18791,"push_channel.push_speed":0.02791,"retract_home.speed":0.03965},"optimized_scores":{"best_composite_score":0.37305,"best_fitness_score":0.68305,"best_task_score":0.51004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.50766,0.10533,0.00927],"force_p95":117.44608,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.91487,"mean_force":18.64588,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5112,0.13383,0.07957]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.51432,0.11975,0.05606],"force_p95":132.26156,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.41262,"mean_force":94.77417,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50809,0.12938,0.05569]},{"body_a":"attachment","body_b":"peg","contact_count":456.0,"contact_point_centroid":[0.50156,-0.00549,0.03958],"force_p95":92.11526,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.57988,"mean_force":23.66866,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50255,0.00599,0.03855]},{"body_a":"peg","body_b":"channel_base_body","contact_count":135.0,"contact_point_centroid":[0.50657,-0.1013,0.03904],"force_p95":92.63195,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.07296,"mean_force":74.6585,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50253,-0.04288,0.03829]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50231,-0.05313,0.042],"force_p95":45.66819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.48108,"mean_force":11.22077,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50173,-0.04223,0.03981]},{"body_a":"peg","body_b":"channel_base_body","contact_count":35.0,"contact_point_centroid":[0.48673,-0.1011,0.04111],"force_p95":45.88641,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.44945,"mean_force":9.71515,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.5016,-0.04158,0.04034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50311,-0.07227,0.0081],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.65426,"mean_force":0.64669,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49877,0.07289,0.15984]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":66.0,"contact_point_centroid":[0.47494,-0.04278,0.02787],"force_p95":8.46196,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76955,"mean_force":4.05149,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50254,0.01591,0.03865]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,-0.05958,0.02425],"force_p95":8.03208,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.37801,"mean_force":2.62278,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49858,0.09432,0.18277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":580.0,"contact_point_centroid":[0.49741,-0.0152,0.0095],"force_p95":5.48378,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.80363,"mean_force":1.63765,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50273,0.03113,0.0388]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,-0.05164,0.03064],"force_p95":5.24143,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.00683,"mean_force":1.95656,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50142,-0.04128,0.04045]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.50556,0.10458,0.00936],"force_p95":0.58894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5783,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50913,0.16909,0.20338]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5002,0.1983,0.29511]}],"total_contact_groups":13},"final_pose_error":0.03123,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50593,-0.072,0.02409],"final_tcp_position":[0.49841,0.18103,0.27524],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":134.91487,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.10459,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54785,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51874,0.14123,0.11754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.50416,0.07419,0.03893],"object_pos_start":[0.50585,0.10459,0.03384],"object_to_goal_dist_end":0.15425,"object_to_goal_dist_start":0.18479,"object_z_max":0.04101,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":305.0,"raw_peak_contact_force":134.91487,"subtask_id":"descend_peg","tcp_end":[0.50622,0.12698,0.0433],"tcp_start":[0.51874,0.14123,0.11754],"tcp_to_object_dist_end":0.05301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.49502,-0.07855,0.02805],"object_pos_start":[0.50416,0.07419,0.03893],"object_to_goal_dist_end":0.01302,"object_to_goal_dist_start":0.15425,"object_z_max":0.03893,"peak_contact_force":93.57988,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1237.0,"raw_peak_contact_force":93.57988,"subtask_id":"push_to_goal","tcp_end":[0.50266,-0.04518,0.038],"tcp_start":[0.50622,0.12698,0.0433],"tcp_to_object_dist_end":0.03565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,-0.072,0.02409],"object_pos_start":[0.49502,-0.07855,0.02805],"object_to_goal_dist_end":0.01877,"object_to_goal_dist_start":0.01302,"object_z_max":0.02996,"peak_contact_force":0.72551,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1044.0,"raw_peak_contact_force":48.48108,"tcp_end":[0.49841,0.18103,0.27524],"tcp_start":[0.50266,-0.04518,0.038],"tcp_to_object_dist_end":0.35659,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89637,"average_solve_count":386.0,"average_success_count":386.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.08989,"descend_to_peg.descend_speed":0.00842,"push_channel.insert_depth":0.185,"push_channel.push_speed":0.03679,"retract_home.speed":0.01688},"optimized_scores":{"best_composite_score":0.53269,"best_fitness_score":0.84269,"best_task_score":0.85784},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":858.0,"contact_point_centroid":[0.49902,-0.02835,0.04326],"force_p95":155.86025,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.21251,"mean_force":86.057,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49715,-0.01802,0.03816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.49676,-0.10249,0.0422],"force_p95":157.3478,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.11854,"mean_force":123.38826,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49693,-0.04745,0.03726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.5043,0.06549,0.00939],"force_p95":89.73194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.70995,"mean_force":8.25312,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49864,0.09896,0.07923]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.50609,0.08439,0.05721],"force_p95":104.49535,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.19641,"mean_force":72.35305,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49949,0.09378,0.05715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.49799,-0.10154,0.04347],"force_p95":82.66928,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.8687,"mean_force":22.0486,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49693,-0.04349,0.04081]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.49789,-0.05476,0.04163],"force_p95":73.74973,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.95334,"mean_force":22.93548,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49706,-0.04445,0.04]},{"body_a":"peg","body_b":"channel_base_body","contact_count":881.0,"contact_point_centroid":[0.50425,-0.0563,0.00974],"force_p95":61.34152,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.8175,"mean_force":12.58469,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49723,-0.01062,0.03833]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,-0.1054,0.02797],"force_p95":18.04608,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.64921,"mean_force":9.41021,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.49817,-0.04997,0.03677]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.50271,-0.07061,0.00813],"force_p95":0.7374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.64767,"mean_force":0.72905,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.4965,0.06985,0.15876]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.5251,-0.08085,0.02766],"force_p95":12.39568,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.45929,"mean_force":4.2285,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49709,-0.02327,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50312,0.06748,0.00932],"force_p95":0.61538,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56917,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49948,0.15295,0.20527]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52508,0.05061,0.05999],"force_p95":0.73918,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77278,"mean_force":0.51392,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50033,0.09244,0.05116]}],"total_contact_groups":12},"final_pose_error":0.03264,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50123,-0.06979,0.02413],"final_tcp_position":[0.49807,0.17988,0.27437],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":164.21251,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54666,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":382.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.50008,0.10768,0.1164],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.50343,0.04985,0.04074],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.1299,"object_to_goal_dist_start":0.14758,"object_z_max":0.04072,"peak_contact_force":0.47006,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":326.0,"raw_peak_contact_force":107.70995,"subtask_id":"descend_peg","tcp_end":[0.49975,0.0902,0.04255],"tcp_start":[0.50008,0.10768,0.1164],"tcp_to_object_dist_end":0.04055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50679,-0.08078,0.02855],"object_pos_start":[0.50343,0.04985,0.04074],"object_to_goal_dist_end":0.01334,"object_to_goal_dist_start":0.1299,"object_z_max":0.04081,"peak_contact_force":156.05113,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2367.0,"raw_peak_contact_force":164.21251,"subtask_id":"push_to_goal","tcp_end":[0.49826,-0.0503,0.03679],"tcp_start":[0.49975,0.0902,0.04255],"tcp_to_object_dist_end":0.03271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50123,-0.06979,0.02413],"object_pos_start":[0.50679,-0.08078,0.02855],"object_to_goal_dist_end":0.01891,"object_to_goal_dist_start":0.01334,"object_z_max":0.03166,"peak_contact_force":0.55146,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1071.0,"raw_peak_contact_force":100.8687,"tcp_end":[0.49807,0.17988,0.27437],"tcp_start":[0.49826,-0.0503,0.03679],"tcp_to_object_dist_end":0.35351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11045,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.09072,"descend_to_peg.descend_speed":0.03515,"push_channel.insert_depth":0.17876,"push_channel.push_speed":0.02353,"retract_home.speed":0.0512},"optimized_scores":{"best_composite_score":0.41943,"best_fitness_score":0.72943,"best_task_score":0.78758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.50912,0.11581,0.00845],"force_p95":193.09038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":199.66574,"mean_force":76.39816,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50502,0.14026,0.0684]},{"body_a":"attachment","body_b":"peg","contact_count":223.0,"contact_point_centroid":[0.51328,0.12915,0.05163],"force_p95":195.97718,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":199.09908,"mean_force":143.2912,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50696,0.13855,0.04998]},{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.50414,0.06858,0.00854],"force_p95":153.40905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.38076,"mean_force":86.9443,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51134,0.0861,0.0473]},{"body_a":"attachment","body_b":"peg","contact_count":954.0,"contact_point_centroid":[0.50966,0.0788,0.04892],"force_p95":152.9563,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.42148,"mean_force":89.1115,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51134,0.08795,0.04729]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":415.0,"contact_point_centroid":[0.52504,0.11641,0.06],"force_p95":123.51398,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.37959,"mean_force":86.1547,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51286,0.11943,0.05075]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":453.0,"contact_point_centroid":[0.47418,0.03418,0.03516],"force_p95":58.21149,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.31512,"mean_force":22.77153,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50959,0.05213,0.04367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50257,-0.01411,0.0081],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.06035,"mean_force":0.81608,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50185,0.08717,0.16202]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.4966,-0.01962,0.04388],"force_p95":39.81238,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.79235,"mean_force":18.01186,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50826,-0.01747,0.04224]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47484,-0.0141,0.0264],"force_p95":12.8457,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.63296,"mean_force":6.22688,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50753,-0.0159,0.04377]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":88.0,"contact_point_centroid":[0.52514,0.11464,0.05225],"force_p95":16.96985,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.22783,"mean_force":12.03143,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51315,0.13556,0.04888]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52503,0.11785,0.04552],"force_p95":6.65734,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.99105,"mean_force":1.20905,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5102,0.14029,0.0457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.50347,0.11167,0.00935],"force_p95":0.62823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.5675,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50265,0.1728,0.20496]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49995,0.19928,0.29847]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.01086,0.02418],"force_p95":0.3939,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39618,"mean_force":0.37337,"phase_index":3.0,"phase_name":"retract_home","phase_type":"retract","tcp_position_centroid":[0.50121,0.10219,0.17969]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50666,-0.01424,0.02409],"final_tcp_position":[0.49866,0.18948,0.28309],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":199.66574,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.11178,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56566,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":356.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50621,0.14779,0.11855],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.11402,0.03026],"object_pos_start":[0.50379,0.11178,0.03381],"object_to_goal_dist_end":0.19439,"object_to_goal_dist_start":0.19191,"object_z_max":0.03387,"peak_contact_force":194.86338,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":671.0,"raw_peak_contact_force":199.66574,"subtask_id":"descend_peg","tcp_end":[0.51043,0.14055,0.04517],"tcp_start":[0.50621,0.14779,0.11855],"tcp_to_object_dist_end":0.03063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49302,-0.01401,0.02668],"object_pos_start":[0.50701,0.11402,0.03026],"object_to_goal_dist_end":0.06768,"object_to_goal_dist_start":0.19439,"object_z_max":0.04014,"peak_contact_force":37.62566,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2845.0,"raw_peak_contact_force":167.38076,"subtask_id":"push_to_goal","tcp_end":[0.50846,-0.01729,0.04212],"tcp_start":[0.51043,0.14055,0.04517],"tcp_to_object_dist_end":0.02209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.50666,-0.01424,0.02409],"object_pos_start":[0.49302,-0.01401,0.02668],"object_to_goal_dist_end":0.06799,"object_to_goal_dist_start":0.06768,"object_z_max":0.0267,"peak_contact_force":0.72551,"phase_name":"retract_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1034.0,"raw_peak_contact_force":50.06035,"tcp_end":[0.49866,0.18948,0.28309],"tcp_start":[0.50846,-0.01729,0.04212],"tcp_to_object_dist_end":0.32961,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```