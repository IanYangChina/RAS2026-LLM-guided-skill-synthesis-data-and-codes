## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0717 | 0.17 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4170 | 0.52 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0835 | 0.01 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4290 | 0.69 | ✅ accepted |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0845 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=-0.072) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_approach
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
  weight: 0.3
- id: push_complete
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - -0.003
    - 0.0
    - 0.0
  subtask_id: reach_contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_complete
- id: retract_away
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[-0.003, 0.0, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.072
- **task_score** (E): 0.169
- **fitness_score**: 0.218  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_over_peg | 1.00 | 0.1095 |
| descend_to_alignment | 1.00 | 0.1449 |
| contact_peg | 1.00 | 0.0001 |
| push_channel | 0.00 | 0.0001 |
| retract_away | 0.00 | 0.0933 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_over_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.209, 0.195) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 |
| descend_to_alignment | descend | 1.00 / step_budget | (0.506, 0.209, 0.195)→(0.499, 0.167, 0.057) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 |
| contact_peg | contact | 1.00 / force_exceeded | (0.499, 0.167, 0.057)→(0.499, 0.166, 0.057) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.166, 0.058)→(0.499, 0.166, 0.057) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 |
| retract_away | retract | 0.00 / step_budget | (0.499, 0.166, 0.057)→(0.507, 0.075, 0.076) | (0.502, 0.098, 0.034)→(0.503, 0.066, 0.028) | 0.178→0.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.293
- alignment_error: None
- terminal_score: 0.293
- phase_score: 0.254
- phase_breakdown.push_complete_score: 0.000
- phase_breakdown.reach_approach_score: 0.744

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.270
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.293
- **Median Q (composite search score)**: -0.056
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20305,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_peg.approach_speed":0.0651,"approach_over_peg.arc_height":0.09616,"contact_peg.contact_force_threshold":10.38508,"contact_peg.contact_speed":0.01722,"descend_to_alignment.descend_speed":0.03373,"push_channel.push_distance":0.15886,"push_channel.push_speed":0.0281,"retract_away.retract_speed":0.05926},"optimized_scores":{"best_composite_score":-0.0203,"best_fitness_score":0.2697,"best_task_score":0.29257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":210.0,"contact_point_centroid":[0.49822,0.2392,-0.00013],"force_p95":260.50677,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":273.82098,"mean_force":232.18941,"phase_index":1.0,"phase_name":"descend_to_alignment","phase_type":"descend","tcp_position_centroid":[0.50037,0.17903,0.056]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.49681,0.23587,-0.0],"force_p95":104.22942,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":240.43521,"mean_force":67.23484,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49927,0.17678,0.05743]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.52507,0.1199,0.05994],"force_p95":223.60537,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.7117,"mean_force":163.50054,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.5054,0.07341,0.08313]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":401.0,"contact_point_centroid":[0.47496,0.11992,0.05997],"force_p95":182.92261,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.01472,"mean_force":132.05792,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50082,0.07668,0.08453]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49784,0.23898,-8e-05],"force_p95":141.09707,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.09707,"mean_force":141.09707,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49996,0.17998,0.05739]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49784,0.23888,-3e-05],"force_p95":76.23359,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.23359,"mean_force":76.23359,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49997,0.17988,0.05748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.50461,0.08782,0.00903],"force_p95":1.85368,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.66705,"mean_force":0.74632,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49877,0.10794,0.07509]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.525,0.04482,0.02742],"force_p95":8.20366,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.23917,"mean_force":3.58342,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50386,0.07562,0.08322]},{"body_a":"attachment","body_b":"peg","contact_count":114.0,"contact_point_centroid":[0.50228,0.11477,0.06174],"force_p95":2.82747,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.50826,"mean_force":1.07201,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49707,0.11554,0.0725]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50349,0.11178,0.00933],"force_p95":0.70595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.57436,"phase_index":0.0,"phase_name":"approach_over_peg","phase_type":"approach","tcp_position_centroid":[0.50225,0.22557,0.2513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":797.0,"contact_point_centroid":[0.50364,0.11164,0.00941],"force_p95":0.59458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63478,"mean_force":0.54418,"phase_index":1.0,"phase_name":"descend_to_alignment","phase_type":"descend","tcp_position_centroid":[0.50185,0.1987,0.10867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51129,0.11093,0.00939],"force_p95":0.59007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59781,"mean_force":0.5386,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49998,0.17979,0.05752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51952,0.12,0.00938],"force_p95":0.55254,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55254,"mean_force":0.55254,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49996,0.17998,0.05739]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_over_peg","phase_type":"approach","tcp_position_centroid":[0.49991,0.20063,0.29921]}],"total_contact_groups":14},"final_pose_error":0.16375,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50578,0.06497,0.02465],"final_tcp_position":[0.50581,0.07341,0.08305],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"phases":[{"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11176,0.0339],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"phase_name":"approach_over_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.50608,0.22204,0.19994],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19934,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":797.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11177,0.03379],"object_pos_start":[0.50372,0.11176,0.0339],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19189,"object_z_max":0.03402,"phase_name":"descend_to_alignment","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_contact","tcp_end":[0.49996,0.17998,0.05739],"tcp_start":[0.50608,0.22204,0.19994],"tcp_to_object_dist_end":0.07227,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11176,0.0338],"object_pos_start":[0.50375,0.11177,0.03379],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19191,"object_z_max":0.03379,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.49997,0.17988,0.05748],"tcp_start":[0.49996,0.17998,0.05739],"tcp_to_object_dist_end":0.07222,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.11174,0.0338],"object_pos_start":[0.50375,0.11176,0.0338],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.1919,"object_z_max":0.0338,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49992,0.17964,0.05743],"tcp_start":[0.49997,0.1797,0.05753],"tcp_to_object_dist_end":0.072,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50578,0.06497,0.02465],"object_pos_start":[0.50368,0.11171,0.03379],"object_to_goal_dist_end":0.14589,"object_to_goal_dist_start":0.19184,"object_z_max":0.04079,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50581,0.07341,0.08305],"tcp_start":[0.49992,0.17964,0.05743],"tcp_to_object_dist_end":0.05901,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50568,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_peg.approach_speed":0.05827,"approach_over_peg.arc_height":0.0957,"contact_peg.contact_force_threshold":11.35804,"contact_peg.contact_speed":0.01929,"descend_to_alignment.descend_speed":0.04173,"push_channel.push_distance":0.19323,"push_channel.push_speed":0.01065,"retract_away.retract_speed":0.07583},"optimized_scores":{"best_composite_score":-0.05583,"best_fitness_score":0.23417,"best_task_score":0.20232},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.48899,0.24638,-0.00015],"force_p95":263.79603,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.86531,"mean_force":234.36808,"phase_index":1.0,"phase_name":"descend_to_alignment","phase_type":"descend","tcp_position_centroid":[0.49115,0.18631,0.05609]},{"body_a":"world","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.4888,0.24305,-1e-05],"force_p95":134.25091,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.69344,"mean_force":70.68147,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49025,0.18423,0.05775]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":427.0,"contact_point_centroid":[0.47466,0.11991,0.05944],"force_p95":202.51064,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.44082,"mean_force":154.15598,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49592,0.07936,0.08279]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48963,0.24624,-8e-05],"force_p95":143.21697,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.21697,"mean_force":143.21697,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49074,0.18751,0.05769]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48963,0.24614,-4e-05],"force_p95":73.37985,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.37985,"mean_force":73.37985,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49077,0.18742,0.05779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49758,0.09312,0.00894],"force_p95":1.51035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33975,"mean_force":0.67128,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49257,0.11037,0.07517]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.49518,0.12281,0.06125],"force_p95":3.27199,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.99288,"mean_force":1.25476,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49006,0.12361,0.07204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.49642,0.11908,0.00936],"force_p95":0.6473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57277,"phase_index":0.0,"phase_name":"approach_over_peg","phase_type":"approach","tcp_position_centroid":[0.49285,0.22911,0.25291]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_over_peg","phase_type":"approach","tcp_position_centroid":[0.49961,0.20154,0.29846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":761.0,"contact_point_centroid":[0.49606,0.11905,0.00947],"force_p95":0.60454,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6552,"mean_force":0.53822,"phase_index":1.0,"phase_name":"descend_to_alignment","phase_type":"descend","tcp_position_centroid":[0.48751,0.20661,0.10955]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48027,0.12,0.0095],"force_p95":0.5469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5469,"mean_force":0.5469,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49074,0.18751,0.05769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5032,0.12,0.0095],"force_p95":0.53558,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53625,"mean_force":0.52282,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49078,0.18733,0.05784]}],"total_contact_groups":12},"final_pose_error":0.16762,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49764,0.07421,0.02415],"final_tcp_position":[0.50227,0.07643,0.07982],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"phases":[{"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.49607,0.11911,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"phase_name":"approach_over_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.4858,0.22866,0.2011],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20023,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11905,0.034],"object_pos_start":[0.49607,0.11911,0.03382],"object_to_goal_dist_end":0.19918,"object_to_goal_dist_start":0.19924,"object_z_max":0.03423,"phase_name":"descend_to_alignment","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_contact","tcp_end":[0.49074,0.18751,0.05769],"tcp_start":[0.4858,0.22866,0.2011],"tcp_to_object_dist_end":0.07263,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11906,0.03401],"object_pos_start":[0.49603,0.11905,0.034],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19918,"object_z_max":0.034,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.49077,0.18742,0.05779],"tcp_start":[0.49074,0.18751,0.05769],"tcp_to_object_dist_end":0.07258,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11906,0.03401],"object_pos_start":[0.49603,0.11906,0.03401],"object_to_goal_dist_end":0.19918,"object_to_goal_dist_start":0.19919,"object_z_max":0.03401,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49075,0.18719,0.05775],"tcp_start":[0.49079,0.18725,0.05785],"tcp_to_object_dist_end":0.07235,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49764,0.07421,0.02415],"object_pos_start":[0.49603,0.11905,0.03401],"object_to_goal_dist_end":0.15504,"object_to_goal_dist_start":0.19918,"object_z_max":0.0408,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50227,0.07643,0.07982],"tcp_start":[0.49075,0.18719,0.05775],"tcp_to_object_dist_end":0.05591,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94048,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_peg.approach_speed":0.02738,"approach_over_peg.arc_height":0.05555,"contact_peg.contact_force_threshold":4.8177,"contact_peg.contact_speed":0.02367,"descend_to_alignment.descend_speed":0.00882,"push_channel.push_distance":0.18034,"push_channel.push_speed":0.01471,"retract_away.retract_speed":0.0901},"optimized_scores":{"best_composite_score":-0.13891,"best_fitness_score":0.15109,"best_task_score":0.01206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":665.0,"contact_point_centroid":[0.47475,0.11992,0.05968],"force_p95":310.05592,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.37987,"mean_force":206.07305,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51008,0.07859,0.06709]},{"body_a":"world","body_b":"link7","contact_count":245.0,"contact_point_centroid":[0.50793,0.19183,-0.00014],"force_p95":275.25199,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.06989,"mean_force":249.61276,"phase_index":1.0,"phase_name":"descend_to_alignment","phase_type":"descend","tcp_position_centroid":[0.50557,0.13153,0.05589]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":276.0,"contact_point_centroid":[0.52504,0.07998,0.05998],"force_p95":214.33553,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.39988,"mean_force":181.33926,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.5146,0.07688,0.06486]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5086,0.19145,-7e-05],"force_p95":136.0263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.0263,"mean_force":136.0263,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50528,0.13216,0.05706]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.52501,0.11983,0.0512],"force_p95":98.67854,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.97932,"mean_force":57.30217,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50116,0.08052,0.07203]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50855,0.19137,-3e-05],"force_p95":112.05685,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.05685,"mean_force":112.05685,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50528,0.13208,0.05715]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50795,0.18981,-1e-05],"force_p95":81.54443,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.70749,"mean_force":56.20857,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50486,0.13042,0.05708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05453,0.00962],"force_p95":3.20768,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.70582,"mean_force":1.25885,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.50749,0.08602,0.06627]},{"body_a":"attachment","body_b":"peg","contact_count":418.0,"contact_point_centroid":[0.50372,0.07739,0.0604],"force_p95":6.40969,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.26149,"mean_force":1.85509,"phase_index":4.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.51282,0.07763,0.06577]},{"body_a":"peg","body_b":"channel_base_body","contact_count":422.0,"contact_point_centroid":[0.5057,0.06293,0.00935],"force_p95":0.58052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57861,"phase_index":0.0,"phase_name":"approach_over_peg","phase_type":"approach","tcp_position_centroid":[0.51482,0.21606,0.23177]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_over_peg","phase_type":"approach","tcp_position_centroid":[0.50007,0.20229,0.29752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":818.0,"contact_point_centroid":[0.506,0.06302,0.00938],"force_p95":0.55222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_alignment","phase_type":"descend","tcp_position_centroid":[0.513,0.15084,0.10131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49013,0.06154,0.00938],"force_p95":0.5514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55162,"mean_force":0.54904,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50524,0.13199,0.05719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50362,0.04516,0.00939],"force_p95":0.54282,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54282,"mean_force":0.54282,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50528,0.13216,0.05706]}],"total_contact_groups":14},"final_pose_error":0.17416,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,0.05808,0.03523],"final_tcp_position":[0.51434,0.07612,0.06415],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"phases":[{"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"phase_name":"approach_over_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_approach","tcp_end":[0.52673,0.17642,0.18456],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18981,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.06294,0.03381],"object_pos_start":[0.50594,0.06298,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"phase_name":"descend_to_alignment","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_contact","tcp_end":[0.50528,0.13216,0.05706],"tcp_start":[0.52673,0.17642,0.18456],"tcp_to_object_dist_end":0.07303,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06295,0.0338],"object_pos_start":[0.50597,0.06294,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_contact","tcp_end":[0.50528,0.13208,0.05715],"tcp_start":[0.50528,0.13216,0.05706],"tcp_to_object_dist_end":0.07296,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06298,0.0338],"object_pos_start":[0.50594,0.06295,0.0338],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14321,"object_z_max":0.0338,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50516,0.13186,0.05712],"tcp_start":[0.50519,0.13191,0.0572],"tcp_to_object_dist_end":0.07272,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05808,0.03523],"object_pos_start":[0.50596,0.06303,0.0338],"object_to_goal_dist_end":0.1383,"object_to_goal_dist_start":0.14329,"object_z_max":0.03569,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51434,0.07612,0.06415],"tcp_start":[0.50516,0.13186,0.05712],"tcp_to_object_dist_end":0.03505,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```