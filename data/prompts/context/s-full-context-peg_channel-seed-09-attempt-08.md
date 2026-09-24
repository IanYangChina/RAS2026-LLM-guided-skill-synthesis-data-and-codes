## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0222 | 0.32 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1539 | 0.12 | ❌ rejected |
| 6 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2651 | 0.36 | ✅ accepted |
| 5 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3940 | 0.35 | ✅ accepted |
| 4 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2014 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=-0.022) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.16
  weight: 0.2
- id: align_to_peg
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_through
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_prep
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
    - 0.16
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_to_peg_height
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_to_peg
- id: lateral_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    contact_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  guards:
  - id: force_high
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: align_to_peg
- id: push_channel
  type: push
  generator: linear_cartesian
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
      distance: 0.22
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.18
      - 0.26
      default: 0.22
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_lateral_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 60.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_through

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_prep** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.16], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg_height** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **lateral_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - contact_x_offset: status=consumed; consumers=target.offset.x (replace)
  - guards:
    - id=force_high, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.22, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=60.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.022
- **task_score** (E): 0.324
- **fitness_score**: 0.538  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prep | 1.00 | 1.00 | 0.1208 |
| descend_to_peg_height | 0.00 | 1.00 | 0.1700 |
| lateral_contact | 0.00 | 1.00 | 0.0838 |
| push_channel | 0.00 | 1.00 | 0.0833 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prep | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.130, 0.205) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.534 | 4.034 |
| descend_to_peg_height | descend | 0.00 / step_budget | (0.508, 0.130, 0.205)→(0.499, 0.116, 0.037) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.536 | 0.603 |
| lateral_contact | contact | 0.00 / guard_failure | (0.499, 0.116, 0.037)→(0.508, 0.033, 0.031) | (0.502, 0.067, 0.034)→(0.506, 0.003, 0.035) | 0.147→0.084 | 1.00 / 1.333 | 0.330 | 53.007 |
| push_channel | push | 0.00 / guard_failure | (0.508, 0.033, 0.031)→(0.502, -0.050, 0.026) | (0.506, 0.003, 0.035)→(0.502, -0.080, 0.037) | 0.084→0.007 | 1.00 / 2.000 | 2.130 | 101.503 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.887
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.323
- phase_score: 0.710
- phase_breakdown.push_through_score: 0.943
- phase_breakdown.align_to_peg_score: 0.387
- phase_breakdown.reach_peg_score: 0.612

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.555
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.396
- **Median Q (composite search score)**: -0.029
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.320


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10204,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.1675,"approach_prep.approach_speed":0.09338,"descend_to_peg_height.descend_force_threshold":9.9904,"descend_to_peg_height.descend_speed":0.05075,"lateral_contact.contact_push_distance":0.05022,"lateral_contact.contact_speed":0.04149,"lateral_contact.contact_x_offset":0.01277,"push_channel.push_distance":0.2356,"push_channel.push_lateral_offset":0.00369,"push_channel.push_speed":0.04746},"optimized_scores":{"best_composite_score":-0.00492,"best_fitness_score":0.55508,"best_task_score":0.32259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56344,-0.1,0.06497],"force_p95":128.12749,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.12749,"mean_force":128.12749,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5063,-0.0466,0.02574]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52501,0.04203,0.06],"force_p95":50.47867,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.2391,"mean_force":41.10592,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50814,0.04216,0.03051]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":60.0,"contact_point_centroid":[0.52529,-0.04923,0.03347],"force_p95":7.36564,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.4898,"mean_force":1.48654,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50636,-0.01913,0.0265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50572,0.03804,0.0097],"force_p95":6.00016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.16357,"mean_force":1.49853,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50406,0.07746,0.0323]},{"body_a":"attachment","body_b":"peg","contact_count":133.0,"contact_point_centroid":[0.50758,-0.00773,0.03814],"force_p95":5.42954,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.88965,"mean_force":1.68897,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50638,0.00403,0.02714]},{"body_a":"attachment","body_b":"peg","contact_count":231.0,"contact_point_centroid":[0.50606,0.05485,0.03799],"force_p95":7.6971,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.78265,"mean_force":1.54073,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50502,0.06676,0.03141]},{"body_a":"peg","body_b":"channel_base_body","contact_count":86.0,"contact_point_centroid":[0.50328,-0.02633,0.00985],"force_p95":5.97972,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.25928,"mean_force":2.38685,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50656,0.0074,0.02749]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":70.0,"contact_point_centroid":[0.52508,0.03787,0.02873],"force_p95":2.57747,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.79547,"mean_force":0.69612,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50489,0.06776,0.03145]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50545,0.06299,0.00931],"force_p95":0.74342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.61417,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51157,0.16052,0.25429]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.5008,0.19624,0.29546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":914.0,"contact_point_centroid":[0.50594,0.06296,0.00938],"force_p95":0.55226,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55664,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.5114,0.11981,0.12568]},{"body_a":"peg","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.52165,-0.07442,0.06394],"force_p95":0.4341,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46577,"mean_force":0.25044,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50628,-0.04484,0.02576]}],"total_contact_groups":12},"final_pose_error":0.14684,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50438,-0.07903,0.03724],"final_tcp_position":[0.50633,-0.04714,0.02577],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":128.12749,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":228.0,"n_steps_budget":870.0,"object_pos_end":[0.50598,0.06294,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54292,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":234.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52224,0.12751,0.21828],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.19613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06303,0.03381],"object_pos_start":[0.50598,0.06294,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":0.54707,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":914.0,"raw_peak_contact_force":0.55664,"subtask_id":"align_to_peg","tcp_end":[0.50285,0.11276,0.03755],"tcp_start":[0.52224,0.12751,0.21828],"tcp_to_object_dist_end":0.04997,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.50688,0.01163,0.03475],"object_pos_start":[0.50596,0.06303,0.03381],"object_to_goal_dist_end":0.09204,"object_to_goal_dist_start":0.14329,"object_z_max":0.03563,"peak_contact_force":0.0,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":641.0,"raw_peak_contact_force":51.2391,"subtask_id":"align_to_peg","tcp_end":[0.50809,0.0418,0.03043],"tcp_start":[0.50285,0.11276,0.03755],"tcp_to_object_dist_end":0.0305,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.50438,-0.07903,0.03724],"object_pos_start":[0.50688,0.01163,0.03475],"object_to_goal_dist_end":0.00527,"object_to_goal_dist_start":0.09204,"object_z_max":0.03819,"peak_contact_force":0.47482,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":287.0,"raw_peak_contact_force":128.12749,"subtask_id":"push_through","tcp_end":[0.50633,-0.04714,0.02577],"tcp_start":[0.50809,0.0418,0.03043],"tcp_to_object_dist_end":0.03394,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1976,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.13194,"approach_prep.approach_speed":0.15538,"descend_to_peg_height.descend_force_threshold":6.12732,"descend_to_peg_height.descend_speed":0.05734,"lateral_contact.contact_push_distance":0.11867,"lateral_contact.contact_speed":0.06018,"lateral_contact.contact_x_offset":0.02337,"push_channel.push_distance":0.23931,"push_channel.push_lateral_offset":-0.01043,"push_channel.push_speed":0.03267},"optimized_scores":{"best_composite_score":-0.03271,"best_fitness_score":0.52729,"best_task_score":0.25429},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.507,-0.1002,0.03699],"force_p95":67.2235,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.52467,"mean_force":37.51297,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50096,-0.05339,0.02702]},{"body_a":"attachment","body_b":"peg","contact_count":145.0,"contact_point_centroid":[0.50568,-0.01738,0.04206],"force_p95":3.90898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.60765,"mean_force":1.79849,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50372,-0.00566,0.02812]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52501,0.04255,0.06],"force_p95":51.9584,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.72197,"mean_force":42.65415,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50834,0.0427,0.03172]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":22.0,"contact_point_centroid":[0.5251,-0.03975,0.03348],"force_p95":10.65261,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.88965,"mean_force":2.1346,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.504,-0.01002,0.02875]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.50619,0.03493,0.00971],"force_p95":6.86082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.59364,"mean_force":1.59064,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50458,0.07475,0.03318]},{"body_a":"attachment","body_b":"peg","contact_count":202.0,"contact_point_centroid":[0.5066,0.05168,0.03942],"force_p95":7.04483,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.1712,"mean_force":1.72251,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50561,0.06362,0.03233]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50374,-0.03433,0.00984],"force_p95":5.68261,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.98692,"mean_force":2.32749,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50436,0.00242,0.02854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.5056,0.05648,0.00932],"force_p95":0.67305,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.61237,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51511,0.1565,0.23668]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50115,0.19596,0.29391]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52506,0.04345,0.02179],"force_p95":1.13105,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62756,"mean_force":0.50557,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50432,0.07331,0.0326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.50613,0.05665,0.00938],"force_p95":0.55771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60349,"mean_force":0.54673,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51513,0.11276,0.10994]}],"total_contact_groups":11},"final_pose_error":0.14285,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50682,-0.08297,0.03694],"final_tcp_position":[0.50092,-0.05421,0.02701],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":70.52467,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":270.0,"n_steps_budget":660.0,"object_pos_end":[0.50612,0.05663,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.50286,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":278.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52891,0.1195,0.18507],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.50612,0.05663,0.03377],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13691,"object_z_max":0.03379,"peak_contact_force":0.54975,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":718.0,"raw_peak_contact_force":0.60349,"subtask_id":"align_to_peg","tcp_end":[0.50361,0.10659,0.03798],"tcp_start":[0.52891,0.1195,0.18507],"tcp_to_object_dist_end":0.05023,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50664,0.01224,0.03499],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.09262,"object_to_goal_dist_start":0.13688,"object_z_max":0.03556,"peak_contact_force":0.0,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":541.0,"raw_peak_contact_force":52.72197,"subtask_id":"align_to_peg","tcp_end":[0.5083,0.04236,0.03166],"tcp_start":[0.50361,0.10659,0.03798],"tcp_to_object_dist_end":0.03035,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,-0.08297,0.03694],"object_pos_start":[0.50664,0.01224,0.03499],"object_to_goal_dist_end":0.00805,"object_to_goal_dist_start":0.09262,"object_z_max":0.03702,"peak_contact_force":4.50128,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":253.0,"raw_peak_contact_force":70.52467,"subtask_id":"push_through","tcp_end":[0.50092,-0.05421,0.02701],"tcp_start":[0.5083,0.04236,0.03166],"tcp_to_object_dist_end":0.03099,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46154,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_prep.approach_height":0.15814,"approach_prep.approach_speed":0.13412,"descend_to_peg_height.descend_force_threshold":5.69963,"descend_to_peg_height.descend_speed":0.07419,"lateral_contact.contact_push_distance":0.10152,"lateral_contact.contact_speed":0.062,"lateral_contact.contact_x_offset":0.02994,"push_channel.push_distance":0.19726,"push_channel.push_lateral_offset":-0.01665,"push_channel.push_speed":0.04415},"optimized_scores":{"best_composite_score":-0.02893,"best_fitness_score":0.53107,"best_task_score":0.39637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55686,-0.1,0.06498],"force_p95":105.85585,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.85585,"mean_force":105.85585,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49995,-0.04673,0.02557]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.01605,0.06],"force_p95":54.23166,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.05954,"mean_force":45.82082,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.50812,0.01619,0.02981]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.01574,0.06],"force_p95":45.86953,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.40483,"mean_force":40.75047,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5081,0.01588,0.02975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":553.0,"contact_point_centroid":[0.49697,0.03154,0.00979],"force_p95":3.8831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.68876,"mean_force":1.35539,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49765,0.06971,0.03104]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.49909,0.04866,0.03511],"force_p95":4.21105,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.21704,"mean_force":1.20231,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49922,0.06051,0.03057]},{"body_a":"attachment","body_b":"peg","contact_count":95.0,"contact_point_centroid":[0.50179,-0.02355,0.03198],"force_p95":4.8906,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.044,"mean_force":1.70282,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50374,-0.01198,0.02697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.49774,-0.04265,0.00988],"force_p95":4.89177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.46406,"mean_force":2.37508,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50387,-0.01173,0.02712]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.4747,-0.06677,0.04296],"force_p95":5.72948,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.87893,"mean_force":1.37636,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50076,-0.03804,0.02571]},{"body_a":"peg","body_b":"channel_base_body","contact_count":174.0,"contact_point_centroid":[0.49471,0.08003,0.00933],"force_p95":0.79168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.61985,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.4855,0.16835,0.25088]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.49808,0.19622,0.29415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49379,0.07995,0.00938],"force_p95":0.58359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64788,"mean_force":0.54648,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.48071,0.13559,0.12116]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.07647,0.01046],"force_p95":0.55522,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5597,"mean_force":0.51603,"phase_index":2.0,"phase_name":"lateral_contact","phase_type":"contact","tcp_position_centroid":[0.49017,0.10686,0.03162]}],"total_contact_groups":12},"final_pose_error":0.13436,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49336,-0.07663,0.03572],"final_tcp_position":[0.49992,-0.04727,0.02558],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":105.85585,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":600.0,"object_pos_end":[0.4938,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55561,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":209.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47418,0.1426,0.21281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07995,0.03377],"object_pos_start":[0.4938,0.07993,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16017,"object_z_max":0.03384,"peak_contact_force":0.51254,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.64788,"subtask_id":"align_to_peg","tcp_end":[0.48922,0.12944,0.03617],"tcp_start":[0.47418,0.1426,0.21281],"tcp_to_object_dist_end":0.04977,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.50328,-0.01366,0.03492],"object_pos_start":[0.49383,0.07995,0.03377],"object_to_goal_dist_end":0.06662,"object_to_goal_dist_start":0.16019,"object_z_max":0.03567,"peak_contact_force":0.99045,"phase_name":"lateral_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":990.0,"raw_peak_contact_force":55.05954,"subtask_id":"align_to_peg","tcp_end":[0.50813,0.01596,0.02979],"tcp_start":[0.48922,0.12944,0.03617],"tcp_to_object_dist_end":0.03044,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.49336,-0.07663,0.03572],"object_pos_start":[0.50328,-0.01366,0.03492],"object_to_goal_dist_end":0.00859,"object_to_goal_dist_start":0.06662,"object_z_max":0.0363,"peak_contact_force":1.41406,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":194.0,"raw_peak_contact_force":105.85585,"subtask_id":"push_through","tcp_end":[0.49992,-0.04727,0.02558],"tcp_start":[0.50813,0.01596,0.02979],"tcp_to_object_dist_end":0.03175,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```