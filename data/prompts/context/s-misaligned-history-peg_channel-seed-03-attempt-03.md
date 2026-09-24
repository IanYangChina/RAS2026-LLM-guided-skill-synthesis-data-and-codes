## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.2944 | 0.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7  | 0.0131 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6  | -0.1168 | 0.09 | ✅ accepted |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3  | -0.2368 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.237) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: push_through_channel
  metric: goal_progress
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
    - 0.04
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_offset_y:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: add
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.04
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: add
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.04
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.174
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push_through_channel
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    retract_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (add)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.04], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (add)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.04], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.174
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.237
- **task_score** (E): 0.131
- **fitness_score**: 0.323  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0676 |
| descend_1 | 1.00 | 1.00 | 0.1218 |
| push_1 | 1.00 | 1.00 | 0.1420 |
| retract_1 | 1.00 | 1.00 | 0.2575 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.173, 0.243) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.531 | 3.954 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.173, 0.243)→(0.501, 0.130, 0.131) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.546 | 0.564 |
| push_1 | push | 1.00 / time_limit | (0.501, 0.130, 0.131)→(0.504, -0.008, 0.097) | (0.502, 0.082, 0.034)→(0.505, 0.019, 0.029) | 0.162→0.100 | 1.00 / 3.667 | 337.157 | 345.217 |
| retract_1 | retract | 1.00 / step_budget | (0.504, -0.008, 0.097)→(0.504, -0.001, 0.354) | (0.505, 0.019, 0.029)→(0.506, 0.018, 0.031) | 0.100→0.099 | 1.00 / 1.000 | 0.568 | 106.920 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.390
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.203
- phase_score: 0.429
- phase_breakdown.push_through_channel_score: 0.333
- phase_breakdown.reach_peg_score: 0.652

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.338
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.203
- **Median Q (composite search score)**: -0.223
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31429,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.05736,"approach_1.approach_offset_z":0.09785,"approach_1.approach_speed":0.19611,"descend_1.descend_offset_z":0.03031,"descend_1.descend_speed":0.11871,"push_1.push_distance":0.19295,"push_1.push_max_time":6.74712,"push_1.push_speed":0.09996,"retract_1.retract_height":0.1422,"retract_1.retract_speed":0.5239},"optimized_scores":{"best_composite_score":-0.22336,"best_fitness_score":0.33664,"best_task_score":0.07904},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":147.0,"contact_point_centroid":[0.52508,0.03338,0.05987],"force_p95":412.52107,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":425.21124,"mean_force":341.30519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50433,-0.01816,0.09655]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":591.0,"contact_point_centroid":[0.47498,0.10012,0.05997],"force_p95":271.65829,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.36328,"mean_force":185.46095,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49687,0.03641,0.10368]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.45957,0.11474,0.0598],"force_p95":210.98939,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.77512,"mean_force":199.0424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45436,0.10879,0.06861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.49426,0.04359,0.00928],"force_p95":72.95732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.46568,"mean_force":9.72067,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49185,0.04609,0.10084]},{"body_a":"peg","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.49538,0.05094,0.06326],"force_p95":98.96491,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.28186,"mean_force":59.80401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50146,0.00342,0.10009]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52507,0.03355,0.05988],"force_p95":82.66466,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.47231,"mean_force":31.6227,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50562,-0.01844,0.0967]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.05818,0.06],"force_p95":84.33676,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.33676,"mean_force":84.33676,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50537,-0.01848,0.09697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.49558,0.05869,0.0092],"force_p95":1.51631,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.69959,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48491,0.18121,0.27057]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4971,0.1966,0.29486]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.01262,0.05471],"force_p95":0.78262,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78262,"mean_force":0.78262,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50343,-0.01772,0.09668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50075,-0.01038,0.00804],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68359,"mean_force":0.60601,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50459,0.00105,0.22821]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.49428,0.05906,0.00938],"force_p95":0.55181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55647,"mean_force":0.54642,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48089,0.13893,0.18624]}],"total_contact_groups":12},"final_pose_error":0.02287,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5059,-0.01043,0.02413],"final_tcp_position":[0.50534,-0.01175,0.36695],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":425.21124,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.49416,0.05896,0.0338],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.53273,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":130.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.47477,0.16815,0.25117],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":870.0,"object_pos_end":[0.49411,0.05906,0.03385],"object_pos_start":[0.49416,0.05896,0.0338],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.13922,"object_z_max":0.03385,"peak_contact_force":0.54355,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":281.0,"raw_peak_contact_force":0.55647,"subtask_id":"reach_peg","tcp_end":[0.48855,0.1083,0.12046],"tcp_start":[0.47477,0.16815,0.25117],"tcp_to_object_dist_end":0.09978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49585,-0.01048,0.02414],"object_pos_start":[0.49411,0.05906,0.03385],"object_to_goal_dist_end":0.07143,"object_to_goal_dist_start":0.13932,"object_z_max":0.04069,"peak_contact_force":402.23986,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1889.0,"raw_peak_contact_force":425.21124,"subtask_id":"push_through_channel","tcp_end":[0.50566,-0.01841,0.09662],"tcp_start":[0.48855,0.1083,0.12046],"tcp_to_object_dist_end":0.07357,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5059,-0.01043,0.02413],"object_pos_start":[0.49585,-0.01048,0.02414],"object_to_goal_dist_end":0.0716,"object_to_goal_dist_start":0.07143,"object_z_max":0.02414,"peak_contact_force":0.60162,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":546.0,"raw_peak_contact_force":91.47231,"tcp_end":[0.50534,-0.01175,0.36695],"tcp_start":[0.50566,-0.01841,0.09662],"tcp_to_object_dist_end":0.34282,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82883,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.02004,"approach_1.approach_offset_z":0.05187,"approach_1.approach_speed":0.64204,"descend_1.descend_offset_z":0.04651,"descend_1.descend_speed":0.05548,"push_1.push_distance":0.19616,"push_1.push_max_time":4.34337,"push_1.push_speed":0.09907,"retract_1.retract_height":0.11224,"retract_1.retract_speed":0.54661},"optimized_scores":{"best_composite_score":-0.26512,"best_fitness_score":0.29488,"best_task_score":0.11249},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.52502,0.03216,0.05998],"force_p95":226.04639,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.21031,"mean_force":170.51566,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50255,-0.01845,0.09717]},{"body_a":"peg","body_b":"link7","contact_count":437.0,"contact_point_centroid":[0.49775,0.06647,0.05459],"force_p95":151.99618,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.41673,"mean_force":90.63798,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50238,0.00996,0.10323]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,0.0666,0.00879],"force_p95":121.56489,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":148.25471,"mean_force":35.42199,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5005,0.0518,0.10857]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":386.0,"contact_point_centroid":[0.52647,0.05068,0.02849],"force_p95":71.36647,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.3665,"mean_force":35.82409,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50242,0.00637,0.10246]},{"body_a":"peg","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.50172,0.03772,0.054],"force_p95":43.15951,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.96523,"mean_force":26.5626,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50211,-0.01766,0.10074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":535.0,"contact_point_centroid":[0.50614,0.02291,0.00934],"force_p95":1.0056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.23313,"mean_force":1.94792,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50165,-0.00142,0.21577]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":268.0,"contact_point_centroid":[0.52539,0.02277,0.04185],"force_p95":20.69736,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.41492,"mean_force":1.95321,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50153,-0.00397,0.17998]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52501,0.03185,0.05998],"force_p95":29.47615,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.02753,"mean_force":15.51376,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50287,-0.01891,0.0972]},{"body_a":"peg","body_b":"channel_base_body","contact_count":184.0,"contact_point_centroid":[0.50517,0.0808,0.00931],"force_p95":0.83967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.62969,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5142,0.17296,0.24728]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50134,0.19687,0.29376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":144.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55104,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51797,0.14018,0.17333]}],"total_contact_groups":11},"final_pose_error":0.02133,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50697,0.0227,0.03377],"final_tcp_position":[0.5023,-0.0129,0.33896],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":227.21031,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54623,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":220.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52675,0.15109,0.20632],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54619,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":144.0,"raw_peak_contact_force":0.55104,"subtask_id":"reach_peg","tcp_end":[0.50893,0.12832,0.13845],"tcp_start":[0.52675,0.15109,0.20632],"tcp_to_object_dist_end":0.11496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51239,0.02441,0.02863],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.10575,"object_to_goal_dist_start":0.16112,"object_z_max":0.03403,"peak_contact_force":226.00115,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1858.0,"raw_peak_contact_force":227.21031,"subtask_id":"push_through_channel","tcp_end":[0.5029,-0.01889,0.09718],"tcp_start":[0.50893,0.12832,0.13845],"tcp_to_object_dist_end":0.08163,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":535.0,"n_steps_budget":600.0,"object_pos_end":[0.50697,0.0227,0.03377],"object_pos_start":[0.51239,0.02441,0.02863],"object_to_goal_dist_end":0.10312,"object_to_goal_dist_start":0.10575,"object_z_max":0.03445,"peak_contact_force":0.55261,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":830.0,"raw_peak_contact_force":79.96523,"tcp_end":[0.5023,-0.0129,0.33896],"tcp_start":[0.5029,-0.01889,0.09718],"tcp_to_object_dist_end":0.30729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03226,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.05534,"approach_1.approach_offset_z":0.11726,"approach_1.approach_speed":0.189,"descend_1.descend_offset_z":0.0416,"descend_1.descend_speed":0.07185,"push_1.push_distance":0.19761,"push_1.push_max_time":6.66742,"push_1.push_speed":0.09959,"retract_1.retract_height":0.1317,"retract_1.retract_speed":0.47057},"optimized_scores":{"best_composite_score":-0.22181,"best_fitness_score":0.33819,"best_task_score":0.20261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.52507,0.06549,0.05989],"force_p95":353.12954,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.22852,"mean_force":261.21142,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50317,0.01441,0.09662]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":108.0,"contact_point_centroid":[0.47499,0.09489,0.05999],"force_p95":226.44362,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.23096,"mean_force":100.71966,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5028,0.01615,0.09704]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47499,0.09319,0.05999],"force_p95":145.30973,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.32251,"mean_force":109.19467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50364,0.01418,0.09629]},{"body_a":"peg","body_b":"link7","contact_count":456.0,"contact_point_centroid":[0.50117,0.08936,0.05624],"force_p95":96.3435,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.42768,"mean_force":61.75339,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50133,0.0359,0.1013]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50637,0.08718,0.00902],"force_p95":89.00709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.42477,"mean_force":26.66165,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49847,0.07566,0.10525]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52507,0.06565,0.05989],"force_p95":74.77749,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.0861,"mean_force":27.69537,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50364,0.01418,0.09633]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":410.0,"contact_point_centroid":[0.52587,0.0707,0.03339],"force_p95":39.15565,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.79109,"mean_force":20.12689,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5015,0.03281,0.10069]},{"body_a":"peg","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.50452,0.06059,0.05937],"force_p95":6.34005,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.78625,"mean_force":2.90556,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5036,0.01417,0.0964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":538.0,"contact_point_centroid":[0.50612,0.04184,0.00941],"force_p95":0.57492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.34009,"mean_force":0.56207,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50249,0.03289,0.22347]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52512,0.04294,0.02973],"force_p95":5.17026,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.6205,"mean_force":2.0638,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50355,0.01417,0.09651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.50232,0.10524,0.00921],"force_p95":2.30811,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.82005,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50773,0.19961,0.28226]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50173,0.19977,0.2959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":280.0,"contact_point_centroid":[0.50583,0.10465,0.00938],"force_p95":0.57174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54571,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50771,0.17637,0.20379]}],"total_contact_groups":13},"final_pose_error":0.0226,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50631,0.04226,0.03383],"final_tcp_position":[0.50321,0.02059,0.3563],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":383.22852,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":69.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.10465,0.03365],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.51482,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":74.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51213,0.19949,0.27296],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50595,0.10465,0.03365],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":0.54878,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":280.0,"raw_peak_contact_force":0.58307,"subtask_id":"reach_peg","tcp_end":[0.50414,0.15206,0.13371],"tcp_start":[0.51213,0.19949,0.27296],"tcp_to_object_dist_end":0.11056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50733,0.04302,0.03433],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.12337,"object_to_goal_dist_start":0.18488,"object_z_max":0.0343,"peak_contact_force":383.22852,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2062.0,"raw_peak_contact_force":383.22852,"subtask_id":"push_through_channel","tcp_end":[0.50366,0.01419,0.09627],"tcp_start":[0.50414,0.15206,0.13371],"tcp_to_object_dist_end":0.06842,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":540.0,"n_steps_budget":600.0,"object_pos_end":[0.50631,0.04226,0.03383],"object_pos_start":[0.50733,0.04302,0.03433],"object_to_goal_dist_end":0.12257,"object_to_goal_dist_start":0.12337,"object_z_max":0.03525,"peak_contact_force":0.54952,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":552.0,"raw_peak_contact_force":149.32251,"tcp_end":[0.50321,0.02059,0.3563],"tcp_start":[0.50366,0.01419,0.09627],"tcp_to_object_dist_end":0.32321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```