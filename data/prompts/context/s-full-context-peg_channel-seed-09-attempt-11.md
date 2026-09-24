## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1731 | 0.03 | ❌ rejected |
| 10 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0973 | 0.06 | ❌ rejected |
| 9 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.3200 | 0.56 | ✅ accepted |
| 8 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0222 | 0.32 | ❌ rejected |
| 7 | approach → descend → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1539 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.173) — your mutation base

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
  control: position_control
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
    threshold: 60.0
    on_failure: continue
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
    - id=force_high, when=during_phase, predicate=force_below, on_failure=continue, threshold=60.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.22, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.173
- **task_score** (E): 0.026
- **fitness_score**: 0.267  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_prep | 1.00 | 1.00 | 0.1278 |
| descend_to_peg_height | 1.00 | 1.00 | 0.1507 |
| make_contact | 1.00 | 1.00 | 0.0306 |
| align_pusher | 1.00 | 1.00 | 0.0269 |
| push_channel | 0.00 | 1.00 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_prep | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.129, 0.197) | (0.512, 0.067, 0.040)→(0.502, 0.066, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.530 | 4.034 |
| descend_to_peg_height | descend | 1.00 / step_budget | (0.508, 0.129, 0.197)→(0.499, 0.117, 0.048) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.547 | 0.591 |
| make_contact | contact | 1.00 / force_exceeded | (0.499, 0.117, 0.048)→(0.502, 0.090, 0.034) | (0.502, 0.066, 0.034)→(0.501, 0.061, 0.035) | 0.147→0.141 | 1.00 / 2.333 | 30.332 | 8.009 |
| align_pusher | align | 1.00 / step_budget | (0.502, 0.090, 0.034)→(0.495, 0.116, 0.034) | (0.501, 0.061, 0.035)→(0.501, 0.060, 0.034) | 0.141→0.140 | 1.00 / 1.000 | 0.549 | 11.945 |
| push_channel | push | 0.00 / guard_failure | (0.510, 0.102, 0.026)→(0.511, 0.101, 0.026) | (0.501, 0.060, 0.034)→(0.503, 0.054, 0.035) | 0.140→0.134 | 1.00 / 2.333 | 1987.412 | 2144.006 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.144
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.042
- phase_score: 0.466
- phase_breakdown.push_through_score: 0.121
- phase_breakdown.lower_to_peg_score: 0.678
- phase_breakdown.establish_contact_score: 0.571
- phase_breakdown.reach_peg_score: 0.783
- phase_breakdown.center_pusher_score: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.297
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.042
- **Median Q (composite search score)**: -0.179
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51852,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pusher.align_speed":0.05514,"align_pusher.align_y_offset":0.20899,"approach_prep.approach_height":0.14379,"approach_prep.approach_speed":0.08919,"descend_to_peg_height.descend_speed":0.0654,"make_contact.contact_force_threshold":4.32154,"make_contact.contact_speed":0.05465,"make_contact.contact_x_offset":0.00946,"push_channel.push_distance":0.24102,"push_channel.push_speed":0.0187,"push_channel.push_x_offset":0.00074},"optimized_scores":{"best_composite_score":-0.17895,"best_fitness_score":0.26105,"best_task_score":0.02186},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52589,0.11386,0.05985],"force_p95":1468.91292,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1488.66986,"mean_force":1289.74546,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50939,0.1115,0.02858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50579,0.06019,0.00948],"force_p95":1.51293,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.07135,"mean_force":0.66517,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.50476,0.09868,0.03879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.50549,0.0629,0.00932],"force_p95":0.68603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.60487,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51158,0.16018,0.24322]},{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.50651,0.07698,0.03546],"force_p95":1.84474,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.50599,"mean_force":0.86203,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.50699,0.08893,0.03484]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50066,0.19668,0.29513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":243.0,"contact_point_centroid":[0.50712,0.05385,0.00943],"force_p95":0.60487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92922,"mean_force":0.55308,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50144,0.10337,0.03237]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50759,0.0729,0.0334],"force_p95":1.80564,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.80564,"mean_force":1.80564,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50809,0.08485,0.03336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50598,0.0631,0.00938],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55641,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51288,0.11969,0.12291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50692,0.05492,0.00938],"force_p95":0.54994,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55073,"mean_force":0.54705,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50289,0.11697,0.03165]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52511,0.05422,0.0554],"force_p95":0.09496,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14891,"mean_force":0.01784,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50759,0.08514,0.03292]}],"total_contact_groups":10},"final_pose_error":0.22957,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50677,0.05441,0.03382],"final_tcp_position":[0.51138,0.10949,0.0276],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1488.66986,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":260.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54799,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":266.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52257,0.12599,0.19671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.0338],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14322,"object_z_max":0.03381,"peak_contact_force":0.54934,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":357.0,"raw_peak_contact_force":0.55641,"subtask_id":"lower_to_peg","tcp_end":[0.5044,0.11372,0.04835],"tcp_start":[0.52257,0.12599,0.19671],"tcp_to_object_dist_end":0.05284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":382.0,"n_steps_budget":600.0,"object_pos_end":[0.50682,0.05494,0.03465],"object_pos_start":[0.50601,0.06295,0.0338],"object_to_goal_dist_end":0.13522,"object_to_goal_dist_start":0.14321,"object_z_max":0.03472,"peak_contact_force":71.04126,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":456.0,"raw_peak_contact_force":4.07135,"subtask_id":"establish_contact","tcp_end":[0.50809,0.08485,0.03336],"tcp_start":[0.5044,0.11372,0.04835],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":600.0,"object_pos_end":[0.50677,0.05442,0.03382],"object_pos_start":[0.50682,0.05494,0.03465],"object_to_goal_dist_end":0.13473,"object_to_goal_dist_start":0.13522,"object_z_max":0.03468,"peak_contact_force":0.53911,"phase_name":"align_pusher","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":256.0,"raw_peak_contact_force":1.92922,"subtask_id":"center_pusher","tcp_end":[0.49736,0.12142,0.03415],"tcp_start":[0.50809,0.08485,0.03336],"tcp_to_object_dist_end":0.06766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50685,0.0544,0.03382],"object_pos_start":[0.50677,0.05442,0.03382],"object_to_goal_dist_end":0.13472,"object_to_goal_dist_start":0.13473,"object_z_max":0.03382,"peak_contact_force":1291.10042,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":1488.66986,"subtask_id":"push_through","tcp_end":[0.51138,0.10949,0.0276],"tcp_start":[0.51058,0.1104,0.02795],"tcp_to_object_dist_end":0.05562,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29252,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pusher.align_speed":0.04871,"align_pusher.align_y_offset":0.2031,"approach_prep.approach_height":0.14199,"approach_prep.approach_speed":0.09672,"descend_to_peg_height.descend_speed":0.05627,"make_contact.contact_force_threshold":4.08333,"make_contact.contact_speed":0.03765,"make_contact.contact_x_offset":0.00881,"push_channel.push_distance":0.25252,"push_channel.push_speed":0.05035,"push_channel.push_x_offset":-0.01176},"optimized_scores":{"best_composite_score":-0.1969,"best_fitness_score":0.2431,"best_task_score":0.01369},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5258,0.10726,0.05987],"force_p95":1418.02204,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1433.26985,"mean_force":1250.58617,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50919,0.10486,0.02858]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.07638,0.06],"force_p95":20.84789,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.02313,"mean_force":19.27079,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50846,0.0765,0.03263]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.07646,0.06],"force_p95":13.86462,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.86462,"mean_force":13.86462,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.50846,0.07658,0.03267]},{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.50549,0.05675,0.00932],"force_p95":0.66512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.61127,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.51484,0.15692,0.24181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.50097,0.19617,0.29459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":500.0,"contact_point_centroid":[0.50523,0.05224,0.0095],"force_p95":1.20264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56232,"mean_force":0.64971,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.50545,0.0909,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":123.0,"contact_point_centroid":[0.50589,0.06978,0.03496],"force_p95":1.42632,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.1929,"mean_force":0.66358,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.50729,0.08163,0.03451]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50169,0.04675,0.00942],"force_p95":0.57803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40123,"mean_force":0.55081,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50156,0.09639,0.03196]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50587,0.06473,0.03292],"force_p95":0.97464,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.04035,"mean_force":0.52317,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50841,0.07644,0.03255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50623,0.05648,0.00938],"force_p95":0.59835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63032,"mean_force":0.54675,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51645,0.1136,0.12177]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49993,0.04577,0.00938],"force_p95":0.55509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55807,"mean_force":0.54601,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5028,0.11088,0.03163]}],"total_contact_groups":11},"final_pose_error":0.2409,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50174,0.04693,0.03378],"final_tcp_position":[0.51114,0.10251,0.0276],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1433.26985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05659,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.49757,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":282.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52859,0.12002,0.19428],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.05659,0.03378],"object_pos_start":[0.50614,0.05659,0.03377],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":0.54764,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":357.0,"raw_peak_contact_force":0.63032,"subtask_id":"lower_to_peg","tcp_end":[0.50539,0.10748,0.04847],"tcp_start":[0.52859,0.12002,0.19428],"tcp_to_object_dist_end":0.05297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":500.0,"n_steps_budget":750.0,"object_pos_end":[0.50203,0.04722,0.03467],"object_pos_start":[0.5061,0.05659,0.03378],"object_to_goal_dist_end":0.12735,"object_to_goal_dist_start":0.13687,"object_z_max":0.03475,"peak_contact_force":13.86462,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":624.0,"raw_peak_contact_force":13.86462,"subtask_id":"establish_contact","tcp_end":[0.50847,0.07652,0.03265],"tcp_start":[0.50539,0.10748,0.04847],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":259.0,"n_steps_budget":630.0,"object_pos_end":[0.50174,0.04691,0.03378],"object_pos_start":[0.50203,0.04722,0.03467],"object_to_goal_dist_end":0.12707,"object_to_goal_dist_start":0.12735,"object_z_max":0.03467,"peak_contact_force":0.54238,"phase_name":"align_pusher","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":264.0,"raw_peak_contact_force":21.02313,"subtask_id":"center_pusher","tcp_end":[0.49734,0.11558,0.03412],"tcp_start":[0.50847,0.07652,0.03265],"tcp_to_object_dist_end":0.06881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50175,0.0469,0.03378],"object_pos_start":[0.50174,0.04691,0.03378],"object_to_goal_dist_end":0.12706,"object_to_goal_dist_start":0.12707,"object_z_max":0.03378,"peak_contact_force":1280.79182,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":1433.26985,"subtask_id":"push_through","tcp_end":[0.51114,0.10251,0.0276],"tcp_start":[0.51035,0.10357,0.02795],"tcp_to_object_dist_end":0.05674,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09489,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pusher.align_speed":0.04692,"align_pusher.align_y_offset":0.19196,"approach_prep.approach_height":0.14433,"approach_prep.approach_speed":0.13113,"descend_to_peg_height.descend_speed":0.05268,"make_contact.contact_force_threshold":3.92712,"make_contact.contact_speed":0.04595,"make_contact.contact_x_offset":0.00602,"push_channel.push_distance":0.23279,"push_channel.push_speed":0.01825,"push_channel.push_x_offset":-0.0089},"optimized_scores":{"best_composite_score":-0.14338,"best_fitness_score":0.29662,"best_task_score":0.04219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54016,0.11469,0.05877],"force_p95":3498.10465,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3510.07813,"mean_force":3009.58645,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50881,0.09339,0.02413]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52588,0.09776,0.05986],"force_p95":3287.04563,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3288.38678,"mean_force":2684.19132,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50881,0.09339,0.02413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50008,0.06489,0.00939],"force_p95":22.46514,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.83647,"mean_force":6.12171,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50038,0.10197,0.03037]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49482,0.09539,0.03476],"force_p95":33.05626,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.82002,"mean_force":20.07497,"phase_index":4.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4949,0.10725,0.03361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":36.0,"contact_point_centroid":[0.49392,0.07159,0.00977],"force_p95":7.87059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.88319,"mean_force":1.77162,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.49053,0.10929,0.03515]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.49312,0.09713,0.05192],"force_p95":10.66446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.6815,"mean_force":3.97239,"phase_index":3.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.4901,0.10914,0.03544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.49378,0.07937,0.00938],"force_p95":0.59659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.09002,"mean_force":0.58688,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.48799,0.11909,0.03978]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49342,0.09775,0.05562],"force_p95":5.3136,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.79779,"mean_force":2.45074,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.49007,0.10977,0.03605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":195.0,"contact_point_centroid":[0.49457,0.07999,0.00934],"force_p95":0.70554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.61198,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.4854,0.16821,0.2445]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_prep","phase_type":"approach","tcp_position_centroid":[0.49827,0.1966,0.29413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.4938,0.07993,0.00938],"force_p95":0.56474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58537,"mean_force":0.5466,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.47989,0.13583,0.12398]}],"total_contact_groups":11},"final_pose_error":0.21707,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49985,0.05689,0.03916],"final_tcp_position":[0.51023,0.09192,0.0229],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":3510.07813,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":223.0,"n_steps_budget":690.0,"object_pos_end":[0.49381,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.5459,"phase_name":"approach_prep","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":230.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.47371,0.14166,0.20011],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49381,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03379,"peak_contact_force":0.54281,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":405.0,"raw_peak_contact_force":0.58537,"subtask_id":"lower_to_peg","tcp_end":[0.48824,0.13034,0.04734],"tcp_start":[0.47371,0.14166,0.20011],"tcp_to_object_dist_end":0.05249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":279.0,"n_steps_budget":630.0,"object_pos_end":[0.49374,0.07954,0.03425],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.15977,"object_to_goal_dist_start":0.16018,"object_z_max":0.0342,"peak_contact_force":6.09002,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":284.0,"raw_peak_contact_force":6.09002,"subtask_id":"establish_contact","tcp_end":[0.49022,0.10925,0.03588],"tcp_start":[0.48824,0.13034,0.04734],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":36.0,"n_steps_budget":600.0,"object_pos_end":[0.49368,0.07908,0.03419],"object_pos_start":[0.49374,0.07954,0.03425],"object_to_goal_dist_end":0.15931,"object_to_goal_dist_start":0.15977,"object_z_max":0.03488,"peak_contact_force":0.56563,"phase_name":"align_pusher","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":48.0,"raw_peak_contact_force":12.88319,"subtask_id":"center_pusher","tcp_end":[0.49176,0.10971,0.03489],"tcp_start":[0.49022,0.10925,0.03588],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.49915,0.06004,0.03783],"object_pos_start":[0.49368,0.07908,0.03419],"object_to_goal_dist_end":0.14006,"object_to_goal_dist_start":0.15931,"object_z_max":0.0385,"peak_contact_force":3390.34326,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":27.0,"raw_peak_contact_force":3510.07813,"subtask_id":"push_through","tcp_end":[0.51023,0.09192,0.0229],"tcp_start":[0.50965,0.09254,0.02333],"tcp_to_object_dist_end":0.03691,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```