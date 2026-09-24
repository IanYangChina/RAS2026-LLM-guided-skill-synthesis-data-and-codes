## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0214 | 0.02 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4166 | 0.12 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4151 | 0.11 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.021) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.1
  weight: 0.3
- id: goal_push
  offset:
  - 0.0
  - 0.025
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
    offset:
    - 0.0
    - 0.025
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.2
      default: 0.16
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
  subtask_id: goal_push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.021
- **task_score** (E): 0.018
- **fitness_score**: 0.161  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1828 |
| descend_1 | 1.00 | 1.00 | 0.0830 |
| align_1 | 0.67 | 1.00 | 0.0260 |
| push_1 | 1.00 | 1.00 | 0.0179 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.117, 0.140) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| descend_1 | contact | 1.00 / force_exceeded | (0.505, 0.117, 0.140)→(0.499, 0.109, 0.059) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.333 | 35.647 | 35.647 |
| align_1 | align | 0.67 / step_budget | (0.499, 0.109, 0.059)→(0.521, 0.107, 0.054) | (0.502, 0.082, 0.034)→(0.502, 0.079, 0.035) | 0.162→0.159 | 1.00 / 1.667 | 76.167 | 277.741 |
| push_1 | push | 1.00 / force_exceeded | (0.521, 0.107, 0.054)→(0.527, 0.099, 0.039) | (0.502, 0.079, 0.035)→(0.502, 0.079, 0.035) | 0.159→0.159 | 1.00 / 2.333 | 415.648 | 415.648 |
| retract_1 | retract | 1.00 / step_budget | (0.527, 0.099, 0.039)→(0.524, 0.098, 0.120) | (0.502, 0.079, 0.035)→(0.505, 0.064, 0.031) | 0.159→0.145 | 1.00 / 1.000 | 0.571 | 272.421 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.176
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.042
- phase_score: 0.265
- phase_breakdown.pre_contact_score: 0.777
- phase_breakdown.goal_push_score: 0.046

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.176
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.042
- **Median Q (composite search score)**: 0.016
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.349


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64257,"average_solve_count":249.0,"average_success_count":249.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03235,"align_1.lateral_offset":0.01743,"approach_1.approach_height":0.08244,"approach_1.approach_speed":0.02362,"descend_1.contact_force":2.5122,"descend_1.descend_speed":0.01994,"push_1.push_distance":0.16923,"push_1.push_force_limit":28.4356,"push_1.push_speed":0.03039},"optimized_scores":{"best_composite_score":0.036,"best_fitness_score":0.176,"best_task_score":0.0418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":36.0,"contact_point_centroid":[0.47499,0.08039,0.05995],"force_p95":350.38083,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":378.67895,"mean_force":198.86608,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4846,0.08691,0.05851]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49312,0.07438,0.05556],"force_p95":59.18794,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.18794,"mean_force":59.18794,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49198,0.08606,0.05574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.4995,0.04146,0.00991],"force_p95":51.94004,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.66395,"mean_force":19.50367,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49148,0.08648,0.05597]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.07814,0.05999],"force_p95":48.99262,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.99262,"mean_force":48.99262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48318,0.08677,0.05883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":78.0,"contact_point_centroid":[0.49693,0.04226,0.00975],"force_p95":2.94339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.4065,"mean_force":1.06893,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48664,0.08701,0.05789]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.48973,0.07551,0.05918],"force_p95":4.20963,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.22524,"mean_force":1.60044,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48647,0.08696,0.05789]},{"body_a":"peg","body_b":"channel_base_body","contact_count":235.0,"contact_point_centroid":[0.49938,0.0242,0.00884],"force_p95":1.26143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.14962,"mean_force":0.69132,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49003,0.08475,0.09485]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.525,-0.00827,0.02408],"force_p95":5.92355,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.99631,"mean_force":3.52814,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4898,0.08481,0.11687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":370.0,"contact_point_centroid":[0.4944,0.0589,0.00934],"force_p95":0.60242,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58573,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48279,0.14582,0.2139]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.19736,0.29569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.49425,0.05892,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0981,"mean_force":0.54731,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.47452,0.09112,0.0955]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47489,0.04815,0.06],"force_p95":1.02511,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08298,"mean_force":0.60231,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49263,0.08469,0.05409]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.48775,0.0757,0.05896],"force_p95":0.72576,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.7518,"mean_force":0.47733,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48315,0.08678,0.05892]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49353,0.07345,0.05533],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49282,0.08536,0.0554]}],"total_contact_groups":14},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50171,0.01202,0.0242],"final_tcp_position":[0.48995,0.08484,0.13577],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":378.67895,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.05888,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54168,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":405.0,"raw_peak_contact_force":4.20518,"subtask_id":"pre_contact","tcp_end":[0.46807,0.09632,0.13789],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.49428,0.05898,0.03395],"object_pos_start":[0.4942,0.05888,0.03385],"object_to_goal_dist_end":0.13923,"object_to_goal_dist_start":0.13914,"object_z_max":0.03394,"peak_contact_force":48.99262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":723.0,"raw_peak_contact_force":48.99262,"tcp_end":[0.4832,0.08676,0.05875],"tcp_start":[0.46807,0.09632,0.13789],"tcp_to_object_dist_end":0.03884,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":78.0,"n_steps_budget":600.0,"object_pos_end":[0.49452,0.05758,0.0356],"object_pos_start":[0.49428,0.05898,0.03395],"object_to_goal_dist_end":0.13776,"object_to_goal_dist_start":0.13923,"object_z_max":0.03557,"peak_contact_force":0.42776,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":147.0,"raw_peak_contact_force":378.67895,"tcp_end":[0.49106,0.08682,0.05616],"tcp_start":[0.4832,0.08676,0.05875],"tcp_to_object_dist_end":0.03591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49432,0.05682,0.03597],"object_pos_start":[0.49452,0.05758,0.0356],"object_to_goal_dist_end":0.13699,"object_to_goal_dist_start":0.13776,"object_z_max":0.03562,"peak_contact_force":59.18794,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":59.18794,"subtask_id":"goal_push","tcp_end":[0.49282,0.08536,0.0554],"tcp_start":[0.49106,0.08682,0.05616],"tcp_to_object_dist_end":0.03456,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":254.0,"n_steps_budget":630.0,"object_pos_end":[0.50171,0.01202,0.0242],"object_pos_start":[0.49432,0.05682,0.03597],"object_to_goal_dist_end":0.09339,"object_to_goal_dist_start":0.13699,"object_z_max":0.04081,"peak_contact_force":0.60459,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":250.0,"raw_peak_contact_force":6.14962,"tcp_end":[0.48995,0.08484,0.13577],"tcp_start":[0.49282,0.08536,0.0554],"tcp_to_object_dist_end":0.13375,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85115,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04119,"align_1.lateral_offset":0.0717,"approach_1.approach_height":0.08822,"approach_1.approach_speed":0.02793,"descend_1.contact_force":5.55989,"descend_1.descend_speed":0.02216,"push_1.push_distance":0.17393,"push_1.push_force_limit":28.50866,"push_1.push_speed":0.02595},"optimized_scores":{"best_composite_score":0.01251,"best_fitness_score":0.15251,"best_task_score":0.00848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52509,0.10674,0.05994],"force_p95":408.91803,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":408.91803,"mean_force":408.91803,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50563,0.10533,0.05157]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":833.0,"contact_point_centroid":[0.52511,0.10814,0.05996],"force_p95":328.38378,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.70917,"mean_force":267.60338,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50956,0.10755,0.05386]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52505,0.10686,0.05997],"force_p95":88.42825,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.08237,"mean_force":46.54118,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5055,0.10543,0.05158]},{"body_a":"attachment","body_b":"peg","contact_count":567.0,"contact_point_centroid":[0.50914,0.09591,0.05514],"force_p95":39.75242,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.87126,"mean_force":6.38093,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50965,0.10761,0.05433]},{"body_a":"peg","body_b":"channel_base_body","contact_count":878.0,"contact_point_centroid":[0.50482,0.06751,0.00977],"force_p95":37.62462,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.93252,"mean_force":4.49978,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50957,0.10757,0.05403]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":68.0,"contact_point_centroid":[0.52528,0.0792,0.05915],"force_p95":21.08569,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.45146,"mean_force":6.59426,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51003,0.10745,0.05566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.37518,"mean_force":0.60974,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51759,0.11198,0.10062]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51365,0.0972,0.05876],"force_p95":26.84912,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.84912,"mean_force":26.84912,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50859,0.10805,0.05956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50551,0.08091,0.00934],"force_p95":0.56727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59062,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51416,0.15622,0.21673]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50023,0.19771,0.29558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.50511,0.07439,0.00947],"force_p95":0.62131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77475,"mean_force":0.53427,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5025,0.10482,0.09069]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50457,0.09374,0.05548],"force_p95":0.55012,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61472,"mean_force":0.37962,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50361,0.10563,0.05493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50275,0.05818,0.00993],"force_p95":0.40128,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40128,"mean_force":0.40128,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50563,0.10533,0.05157]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50599,0.09339,0.05247],"force_p95":0.31673,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31673,"mean_force":0.31673,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50563,0.10533,0.05157]}],"total_contact_groups":14},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5054,0.07616,0.03379],"final_tcp_position":[0.50244,0.10459,0.13192],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":408.91803,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55009,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":4.32595,"subtask_id":"pre_contact","tcp_end":[0.52851,0.11638,0.14321],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":27.37518,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":427.0,"raw_peak_contact_force":27.37518,"tcp_end":[0.50857,0.10803,0.05939],"tcp_start":[0.52851,0.11638,0.14321],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.50556,0.07563,0.03509],"object_pos_start":[0.50599,0.0809,0.03378],"object_to_goal_dist_end":0.15581,"object_to_goal_dist_start":0.16113,"object_z_max":0.03552,"peak_contact_force":227.53294,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2346.0,"raw_peak_contact_force":385.70917,"tcp_end":[0.50563,0.10533,0.05157],"tcp_start":[0.50857,0.10803,0.05939],"tcp_to_object_dist_end":0.03397,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50556,0.07562,0.0351],"object_pos_start":[0.50556,0.07563,0.03509],"object_to_goal_dist_end":0.15579,"object_to_goal_dist_start":0.15581,"object_z_max":0.03509,"peak_contact_force":408.91803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":408.91803,"subtask_id":"goal_push","tcp_end":[0.50562,0.10532,0.05159],"tcp_start":[0.50563,0.10533,0.05157],"tcp_to_object_dist_end":0.03398,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":255.0,"n_steps_budget":630.0,"object_pos_end":[0.5054,0.07616,0.03379],"object_pos_start":[0.50556,0.07562,0.0351],"object_to_goal_dist_end":0.15638,"object_to_goal_dist_start":0.15579,"object_z_max":0.03512,"peak_contact_force":0.5393,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":268.0,"raw_peak_contact_force":93.08237,"tcp_end":[0.50244,0.10459,0.13192],"tcp_start":[0.50562,0.10532,0.05159],"tcp_to_object_dist_end":0.10221,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77465,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02383,"align_1.lateral_offset":0.08596,"approach_1.approach_height":0.08226,"approach_1.approach_speed":0.01819,"descend_1.contact_force":9.04365,"descend_1.descend_speed":0.02237,"push_1.push_distance":0.19691,"push_1.push_force_limit":47.67908,"push_1.push_speed":0.04179},"optimized_scores":{"best_composite_score":0.0157,"best_fitness_score":0.1557,"best_task_score":0.00354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.57993,0.11762,0.00977],"force_p95":778.83856,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":778.83856,"mean_force":778.83856,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.58357,0.1066,0.0125]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":23.0,"contact_point_centroid":[0.57945,0.11735,0.00824],"force_p95":568.21806,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":718.03174,"mean_force":163.74861,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58275,0.10675,0.01054]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.55471,0.11985,0.05977],"force_p95":308.84789,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.64635,"mean_force":223.38862,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58209,0.10647,0.00853]},{"body_a":"attachment","body_b":"peg","contact_count":103.0,"contact_point_centroid":[0.5163,0.12097,0.05793],"force_p95":61.6664,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.8339,"mean_force":48.29629,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.512,0.13154,0.05793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50754,0.1048,0.00938],"force_p95":49.14371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.82356,"mean_force":5.164,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54015,0.13177,0.0539]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":548.0,"contact_point_centroid":[0.54181,0.11999,0.05942],"force_p95":29.51931,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.08496,"mean_force":20.01372,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54084,0.13197,0.05341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50583,0.10476,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.57296,"mean_force":0.61777,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.51113,0.1341,0.09862]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51288,0.12141,0.05871],"force_p95":30.01345,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.01345,"mean_force":30.01345,"phase_index":1.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.50587,0.13109,0.05973]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":96.0,"contact_point_centroid":[0.52541,0.10535,0.05891],"force_p95":26.26837,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.7908,"mean_force":18.66035,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51337,0.13163,0.05764]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50543,0.10454,0.00936],"force_p95":0.59995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58061,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50899,0.16749,0.21531]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49998,0.19843,0.29623]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.50628,0.10364,0.00939],"force_p95":0.56131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57162,"mean_force":0.54639,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58027,0.10541,0.04976]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50599,0.10168,0.00939],"force_p95":0.557,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56105,"mean_force":0.54671,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.58062,0.11596,0.0388]}],"total_contact_groups":13},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5065,0.10355,0.03384],"final_tcp_position":[0.57936,0.10549,0.09152],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":778.83856,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54467,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":362.0,"raw_peak_contact_force":3.33087,"subtask_id":"pre_contact","tcp_end":[0.51863,0.13774,0.13947],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10472,0.03384],"object_pos_start":[0.50584,0.10467,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18487,"object_z_max":0.03384,"peak_contact_force":30.57296,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":421.0,"raw_peak_contact_force":30.57296,"tcp_end":[0.50586,0.13108,0.05956],"tcp_start":[0.51863,0.13774,0.13947],"tcp_to_object_dist_end":0.03683,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5065,0.10341,0.03384],"object_pos_start":[0.50597,0.10472,0.03384],"object_to_goal_dist_end":0.18363,"object_to_goal_dist_start":0.18492,"object_z_max":0.03454,"peak_contact_force":0.53943,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1747.0,"raw_peak_contact_force":68.8339,"tcp_end":[0.56651,0.1302,0.05327],"tcp_start":[0.50586,0.13108,0.05956],"tcp_to_object_dist_end":0.06854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":30.0,"n_steps_budget":1000.0,"object_pos_end":[0.50638,0.10346,0.03384],"object_pos_start":[0.5065,0.10341,0.03384],"object_to_goal_dist_end":0.18367,"object_to_goal_dist_start":0.18363,"object_z_max":0.03384,"peak_contact_force":778.83856,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":31.0,"raw_peak_contact_force":778.83856,"subtask_id":"goal_push","tcp_end":[0.58299,0.10653,0.01097],"tcp_start":[0.56651,0.1302,0.05327],"tcp_to_object_dist_end":0.08001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":278.0,"n_steps_budget":630.0,"object_pos_end":[0.5065,0.10355,0.03384],"object_pos_start":[0.50638,0.10346,0.03384],"object_to_goal_dist_end":0.18377,"object_to_goal_dist_start":0.18367,"object_z_max":0.03384,"peak_contact_force":0.56835,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":310.0,"raw_peak_contact_force":718.03174,"tcp_end":[0.57936,0.10549,0.09152],"tcp_start":[0.58299,0.10653,0.01097],"tcp_to_object_dist_end":0.09295,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```