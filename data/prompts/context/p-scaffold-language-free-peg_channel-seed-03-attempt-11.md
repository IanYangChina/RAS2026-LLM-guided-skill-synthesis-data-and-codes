## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1404 | 0.11 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3360 | 0.32 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | time_limit | force_exceeded | pose_tolerance | 9 | 0.1497 | 0.06 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1753 | 0.33 | ✅ accepted |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2081 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.140) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_progress
  target_entity: object
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
    entity: peg
    offset:
    - 0.0
    - 0.05
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_peg
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_progress
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_peg, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.140
- **task_score** (E): 0.114
- **fitness_score**: 0.220  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_align | 1.00 | 1.00 | 0.1340 |
| descend_align | 1.00 | 1.00 | 0.1225 |
| push_through | 0.00 | 1.00 | 0.2211 |
| retract_after | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_align | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.142, 0.184) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.543 | 3.954 |
| descend_align | descend | 1.00 / step_budget | (0.505, 0.142, 0.184)→(0.499, 0.132, 0.063) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.547 | 0.561 |
| push_through | push | 0.00 / guard_failure | (0.499, 0.132, 0.063)→(0.495, -0.089, 0.050) | (0.502, 0.081, 0.034)→(0.501, 0.019, 0.024) | 0.162→0.101 | 1.00 / 2.000 | 102.749 | 102.749 |
| retract_after | retract | 1.00 / step_budget | (0.495, -0.089, 0.050)→(0.492, -0.088, 0.130) | (0.501, 0.019, 0.024)→(0.500, 0.019, 0.024) | 0.101→0.101 | 1.00 / 1.000 | 0.551 | 95.650 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.583
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.107
- phase_score: 0.421
- phase_breakdown.reach_peg_score: 0.075
- phase_breakdown.push_progress_score: 0.569

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.295
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.154
- **Median Q (composite search score)**: -0.177
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.283


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81579,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.14397,"approach_align.speed":0.07891,"descend_align.speed":0.16712,"push_through.push_distance":0.1933,"push_through.speed":0.03514,"retract_after.speed":0.08579},"optimized_scores":{"best_composite_score":-0.17685,"best_fitness_score":0.18315,"best_task_score":0.08128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49759,-0.10033,0.065],"force_p95":99.741,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.54433,"mean_force":80.52408,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49522,-0.08854,0.05027]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49749,-0.10039,0.065],"force_p95":91.23562,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.23631,"mean_force":88.12359,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49516,-0.08867,0.05056]},{"body_a":"attachment","body_b":"peg","contact_count":147.0,"contact_point_centroid":[0.49544,0.04389,0.055],"force_p95":47.46026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.95288,"mean_force":32.88603,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48786,0.05237,0.05582]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.09368,0.05997],"force_p95":35.36917,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.36917,"mean_force":35.36917,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48685,0.09365,0.05814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":701.0,"contact_point_centroid":[0.49985,0.02597,0.00876],"force_p95":29.63998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.77028,"mean_force":4.80093,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49032,0.00991,0.05426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":131.0,"contact_point_centroid":[0.52506,0.02266,0.05358],"force_p95":25.8987,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.6249,"mean_force":21.18295,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48807,0.04796,0.05562]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47496,0.03312,0.02426],"force_p95":5.65277,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.89861,"mean_force":1.53834,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49033,0.00582,0.05386]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.49899,0.01146,0.00807],"force_p95":0.65687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.79064,"mean_force":0.64674,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49265,-0.08824,0.08953]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.03293,0.02426],"force_p95":5.66474,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.67071,"mean_force":3.04179,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49218,-0.08848,0.12087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":229.0,"contact_point_centroid":[0.49457,0.05897,0.00931],"force_p95":0.68572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.61001,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.48349,0.15842,0.24369]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.4983,0.19638,0.29498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.49414,0.05905,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54624,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.47838,0.11594,0.1294]}],"total_contact_groups":12},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49751,0.01202,0.02428],"final_tcp_position":[0.49227,-0.0885,0.13065],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":101.54433,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,0.05887,0.03383],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5436,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":264.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.47019,0.12286,0.19793],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":422.0,"n_steps_budget":600.0,"object_pos_end":[0.49403,0.05885,0.03389],"object_pos_start":[0.49414,0.05887,0.03383],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13913,"object_z_max":0.03389,"peak_contact_force":0.54918,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":422.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_peg","tcp_end":[0.48858,0.10935,0.06195],"tcp_start":[0.47019,0.12286,0.19793],"tcp_to_object_dist_end":0.05803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.0123,0.02416],"object_pos_start":[0.49403,0.05885,0.03389],"object_to_goal_dist_end":0.09366,"object_to_goal_dist_start":0.13912,"object_z_max":0.04047,"peak_contact_force":101.54433,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":994.0,"raw_peak_contact_force":101.54433,"subtask_id":"push_progress","tcp_end":[0.49528,-0.08897,0.05025],"tcp_start":[0.48858,0.10935,0.06195],"tcp_to_object_dist_end":0.10474,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":249.0,"n_steps_budget":750.0,"object_pos_end":[0.49751,0.01202,0.02428],"object_pos_start":[0.50092,0.0123,0.02416],"object_to_goal_dist_end":0.09339,"object_to_goal_dist_start":0.09366,"object_z_max":0.02429,"peak_contact_force":0.50964,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":262.0,"raw_peak_contact_force":91.23631,"tcp_end":[0.49227,-0.0885,0.13065],"tcp_start":[0.49528,-0.08897,0.05025],"tcp_to_object_dist_end":0.14645,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80282,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.10107,"approach_align.speed":0.20597,"descend_align.speed":0.1976,"push_through.push_distance":0.21289,"push_through.speed":0.02583,"retract_after.speed":0.06014},"optimized_scores":{"best_composite_score":-0.0649,"best_fitness_score":0.2951,"best_task_score":0.10664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49735,-0.10023,0.065],"force_p95":98.61115,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.15931,"mean_force":81.54518,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49508,-0.08837,0.05097]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49721,-0.10032,0.065],"force_p95":93.75922,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.967,"mean_force":80.7516,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49495,-0.08854,0.05117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.50725,0.02538,0.00923],"force_p95":67.47047,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.81771,"mean_force":31.05285,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50085,0.02421,0.0576]},{"body_a":"attachment","body_b":"peg","contact_count":506.0,"contact_point_centroid":[0.51053,0.0463,0.05869],"force_p95":67.60713,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.32333,"mean_force":46.46468,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50222,0.04353,0.05913]},{"body_a":"peg","body_b":"channel_base_body","contact_count":253.0,"contact_point_centroid":[0.50539,0.08096,0.00933],"force_p95":0.62146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60707,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.51469,0.16735,0.22195]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50115,0.19705,0.2928]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.49614,-0.01214,0.00805],"force_p95":0.72554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97274,"mean_force":0.60516,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49253,-0.08813,0.09008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50598,0.08074,0.00938],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55048,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.5164,0.13518,0.11033]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,-0.0357,0.02414],"force_p95":0.41846,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42112,"mean_force":0.39445,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49207,-0.08831,0.10206]}],"total_contact_groups":9},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49648,-0.01232,0.02411],"final_tcp_position":[0.49217,-0.08838,0.1313],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":100.15931,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5443,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":289.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52818,0.13962,0.15744],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54639,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":273.0,"raw_peak_contact_force":0.55048,"subtask_id":"reach_peg","tcp_end":[0.50567,0.13121,0.06368],"tcp_start":[0.52818,0.13962,0.15744],"tcp_to_object_dist_end":0.05854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.49771,-0.01246,0.02409],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.06943,"object_to_goal_dist_start":0.16112,"object_z_max":0.04027,"peak_contact_force":100.15931,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1280.0,"raw_peak_contact_force":100.15931,"subtask_id":"push_progress","tcp_end":[0.49509,-0.08885,0.05095],"tcp_start":[0.50567,0.13121,0.06368],"tcp_to_object_dist_end":0.08102,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.49648,-0.01232,0.02411],"object_pos_start":[0.49771,-0.01246,0.02409],"object_to_goal_dist_end":0.06961,"object_to_goal_dist_start":0.06943,"object_z_max":0.02448,"peak_contact_force":0.63202,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":277.0,"raw_peak_contact_force":95.967,"tcp_end":[0.49217,-0.08838,0.1313],"tcp_start":[0.49509,-0.08885,0.05095],"tcp_to_object_dist_end":0.1315,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78231,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.13826,"approach_align.speed":0.15724,"descend_align.speed":0.18404,"push_through.push_distance":0.19948,"push_through.speed":0.03089,"retract_after.speed":0.05984},"optimized_scores":{"best_composite_score":-0.17949,"best_fitness_score":0.18051,"best_task_score":0.1537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49699,-0.10029,0.065],"force_p95":104.90354,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.5435,"mean_force":86.7712,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49448,-0.08849,0.04934]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49684,-0.10037,0.065],"force_p95":96.50718,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.74773,"mean_force":82.67001,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49437,-0.08863,0.04954]},{"body_a":"attachment","body_b":"peg","contact_count":114.0,"contact_point_centroid":[0.50324,0.09686,0.05694],"force_p95":25.22373,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.83303,"mean_force":12.94882,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49935,0.10801,0.05746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":789.0,"contact_point_centroid":[0.50537,0.06725,0.0085],"force_p95":14.29632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.31754,"mean_force":2.12341,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49745,0.03069,0.05431]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":38.0,"contact_point_centroid":[0.52507,0.0832,0.05985],"force_p95":16.02907,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.2316,"mean_force":10.6898,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49949,0.11521,0.05765]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50509,0.10445,0.00934],"force_p95":0.718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.60681,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.5093,0.17929,0.242]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50076,0.19791,0.29443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.50586,0.05742,0.00802],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81336,"mean_force":0.60519,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.49195,-0.08823,0.08836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.5059,0.10464,0.00939],"force_p95":0.57504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57958,"mean_force":0.54635,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.51005,0.15799,0.12891]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.08252,0.0242],"force_p95":0.38571,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.388,"mean_force":0.36512,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.4915,-0.08846,0.11701]}],"total_contact_groups":10},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50641,0.05756,0.02416],"final_tcp_position":[0.49157,-0.08848,0.12954],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":106.5435,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54204,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":219.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51787,0.16215,0.19526],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.50584,0.10467,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18486,"object_z_max":0.03384,"peak_contact_force":0.54537,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":364.0,"raw_peak_contact_force":0.57958,"subtask_id":"reach_peg","tcp_end":[0.50363,0.15439,0.06347],"tcp_start":[0.51787,0.16215,0.19526],"tcp_to_object_dist_end":0.05792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.5049,0.05757,0.0241],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.13857,"object_to_goal_dist_start":0.18486,"object_z_max":0.04032,"peak_contact_force":106.5435,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":946.0,"raw_peak_contact_force":106.5435,"subtask_id":"push_progress","tcp_end":[0.4945,-0.08895,0.04932],"tcp_start":[0.50363,0.15439,0.06347],"tcp_to_object_dist_end":0.14904,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.50641,0.05756,0.02416],"object_pos_start":[0.5049,0.05757,0.0241],"object_to_goal_dist_end":0.13862,"object_to_goal_dist_start":0.13857,"object_z_max":0.02424,"peak_contact_force":0.5102,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":276.0,"raw_peak_contact_force":99.74773,"tcp_end":[0.49157,-0.08848,0.12954],"tcp_start":[0.4945,-0.08895,0.04932],"tcp_to_object_dist_end":0.1807,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```