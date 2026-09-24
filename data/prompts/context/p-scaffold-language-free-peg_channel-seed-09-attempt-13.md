## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | pose_tolerance | 9 | 0.2843 | 0.28 | ✅ accepted |
| 12 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.0437 | 0.12 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3691 | 0.18 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | 0.0845 | 0.12 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3782 | 0.23 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.284) — your mutation base

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
- id: push_through_channel
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.06
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: peg_contact
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: reach_peg
- id: align_pusher
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through_channel
- id: push_along_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_time_limit:
      type: scalar
      range:
      - 2.0
      - 6.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_through_channel
- id: retract_from_channel
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=peg_contact, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **align_pusher** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time_limit: status=consumed; consumers=duration.max_time (replace)
- **retract_from_channel** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.284
- **task_score** (E): 0.281
- **fitness_score**: 0.574  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2115 |
| contact_peg | 1.00 | 1.00 | 0.0581 |
| align_pusher | 1.00 | 1.00 | 0.0281 |
| push_along_channel | 1.00 | 1.00 | 0.1174 |
| retract_from_channel | 1.00 | 1.00 | 0.1065 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.510, 0.130, 0.101) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.542 | 4.034 |
| contact_peg | contact | 1.00 / force_exceeded | (0.510, 0.130, 0.101)→(0.502, 0.093, 0.058) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.035) | 0.147→0.146 | 1.00 / 2.000 | 16.974 | 16.974 |
| align_pusher | align | 1.00 / step_budget | (0.502, 0.093, 0.058)→(0.502, 0.074, 0.039) | (0.502, 0.066, 0.035)→(0.500, 0.042, 0.038) | 0.146→0.122 | 1.00 / 1.333 | 7.934 | 106.781 |
| push_along_channel | push | 1.00 / time_limit | (0.502, 0.074, 0.039)→(0.497, -0.044, 0.035) | (0.500, 0.042, 0.038)→(0.505, -0.075, 0.037) | 0.122→0.009 | 1.00 / 2.333 | 18.633 | 26.896 |
| retract_from_channel | retract | 1.00 / step_budget | (0.497, -0.044, 0.035)→(0.494, -0.043, 0.142) | (0.505, -0.075, 0.037)→(0.505, -0.075, 0.036) | 0.009→0.010 | 1.00 / 1.333 | 0.526 | 19.927 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.888
- alignment_error: None
- force_efficiency: 0.110
- terminal_score: 0.363
- phase_score: 0.768
- phase_breakdown.push_through_channel_score: 0.931
- phase_breakdown.reach_peg_score: 0.386

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.606
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: 0.275
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.301


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02439,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pusher.align_speed":0.01992,"approach_peg.approach_height":0.04894,"approach_peg.lateral_offset":-0.00492,"approach_peg.speed":0.03658,"contact_peg.contact_force":7.28372,"push_along_channel.push_speed":0.074,"push_along_channel.push_time_limit":4.41814,"retract_from_channel.retract_height":0.10856,"retract_from_channel.speed":0.05689},"optimized_scores":{"best_composite_score":0.3158,"best_fitness_score":0.6058,"best_task_score":0.36284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":66.0,"contact_point_centroid":[0.5053,0.06329,0.04175],"force_p95":31.05229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.49796,"mean_force":27.54447,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50414,0.07472,0.0417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50563,0.04159,0.00989],"force_p95":31.05544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.88016,"mean_force":15.07037,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50502,0.07921,0.04557]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.50554,-0.03397,0.00992],"force_p95":7.73145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.53737,"mean_force":3.84741,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4986,0.01106,0.03452]},{"body_a":"attachment","body_b":"peg","contact_count":798.0,"contact_point_centroid":[0.50245,-0.00336,0.04159],"force_p95":7.71034,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.27228,"mean_force":2.78866,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49851,0.00821,0.03453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":306.0,"contact_point_centroid":[0.50586,0.06099,0.00941],"force_p95":0.55275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.82018,"mean_force":0.67159,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51268,0.10769,0.07407]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50745,0.07925,0.05731],"force_p95":7.4736,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.59084,"mean_force":5.35422,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50848,0.09117,0.05722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":960.0,"contact_point_centroid":[0.50668,-0.07936,0.0094],"force_p95":0.55525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.98516,"mean_force":0.55449,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49351,-0.04982,0.08479]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":475.0,"contact_point_centroid":[0.52506,-0.02824,0.0222],"force_p95":3.11589,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.84288,"mean_force":1.01555,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49814,-0.00013,0.03445]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50217,-0.06174,0.05729],"force_p95":3.16328,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.33005,"mean_force":0.64998,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49553,-0.05025,0.03653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":718.0,"contact_point_centroid":[0.50579,0.06302,0.00936],"force_p95":0.55914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56541,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50923,0.16208,0.19386]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49973,0.19868,0.29675]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,-0.07738,0.01111],"force_p95":0.27072,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27248,"mean_force":0.25333,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49682,-0.05022,0.03501]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50672,-0.07913,0.03381],"final_tcp_position":[0.4937,-0.0498,0.13419],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":44.49796,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54138,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.51979,0.12677,0.09651],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":306.0,"n_steps_budget":600.0,"object_pos_end":[0.50577,0.06062,0.03616],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14079,"object_to_goal_dist_start":0.14324,"object_z_max":0.0361,"peak_contact_force":7.82018,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":314.0,"raw_peak_contact_force":7.82018,"subtask_id":"reach_peg","tcp_end":[0.508,0.08894,0.05501],"tcp_start":[0.51979,0.12677,0.09651],"tcp_to_object_dist_end":0.03409,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.50519,0.03949,0.03947],"object_pos_start":[0.50577,0.06062,0.03616],"object_to_goal_dist_end":0.1196,"object_to_goal_dist_start":0.14079,"object_z_max":0.0404,"peak_contact_force":22.99892,"phase_name":"align_pusher","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":190.0,"raw_peak_contact_force":44.49796,"subtask_id":"push_through_channel","tcp_end":[0.50377,0.07006,0.03818],"tcp_start":[0.508,0.08894,0.05501],"tcp_to_object_dist_end":0.03063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50693,-0.07841,0.03592],"object_pos_start":[0.50519,0.03949,0.03947],"object_to_goal_dist_end":0.0082,"object_to_goal_dist_start":0.1196,"object_z_max":0.03951,"peak_contact_force":2.21989,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1886.0,"raw_peak_contact_force":17.53737,"subtask_id":"push_through_channel","tcp_end":[0.4969,-0.05004,0.03505],"tcp_start":[0.50377,0.07006,0.03818],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.50672,-0.07913,0.03381],"object_pos_start":[0.50693,-0.07841,0.03592],"object_to_goal_dist_end":0.00918,"object_to_goal_dist_start":0.0082,"object_z_max":0.03604,"peak_contact_force":0.54787,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":973.0,"raw_peak_contact_force":5.98516,"tcp_end":[0.4937,-0.0498,0.13419],"tcp_start":[0.4969,-0.05004,0.03505],"tcp_to_object_dist_end":0.10538,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pusher.align_speed":0.02545,"approach_peg.approach_height":0.05062,"approach_peg.lateral_offset":-0.00938,"approach_peg.speed":0.07516,"contact_peg.contact_force":7.76072,"push_along_channel.push_speed":0.06863,"push_along_channel.push_time_limit":3.58168,"retract_from_channel.retract_height":0.10541,"retract_from_channel.speed":0.0682},"optimized_scores":{"best_composite_score":0.26235,"best_fitness_score":0.55235,"best_task_score":0.23674},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.50528,0.06379,0.04677],"force_p95":23.81253,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.19735,"mean_force":15.23438,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50616,0.07552,0.0466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50213,0.0361,0.0098],"force_p95":23.95936,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.96551,"mean_force":10.86323,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50673,0.07761,0.0489]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.50613,0.05649,0.00938],"force_p95":0.57546,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.7449,"mean_force":0.61213,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5148,0.10336,0.07688]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51039,0.07407,0.05876],"force_p95":18.34439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.34439,"mean_force":18.34439,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50981,0.08604,0.05889]},{"body_a":"attachment","body_b":"peg","contact_count":808.0,"contact_point_centroid":[0.50231,-0.00491,0.0414],"force_p95":6.60799,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.68561,"mean_force":2.56264,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49861,0.00673,0.03385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50453,-0.03164,0.00991],"force_p95":6.71042,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.62072,"mean_force":3.36827,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49892,0.01321,0.03387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":847.0,"contact_point_centroid":[0.50684,-0.07657,0.00947],"force_p95":0.55346,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.70246,"mean_force":0.53766,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49364,-0.04651,0.08273]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50141,-0.0581,0.05936],"force_p95":1.72241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.08908,"mean_force":0.59438,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49454,-0.04667,0.04114]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":347.0,"contact_point_centroid":[0.52503,-0.0336,0.02005],"force_p95":2.57702,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.62616,"mean_force":0.93325,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49818,-0.00556,0.03399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":676.0,"contact_point_centroid":[0.5059,0.05666,0.00936],"force_p95":0.60211,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56988,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51047,0.15891,0.19426]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49991,0.19833,0.29593]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":81.0,"contact_point_centroid":[0.52502,-0.07472,0.05915],"force_p95":1.48279,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16949,"mean_force":0.26092,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49386,-0.04654,0.09042]}],"total_contact_groups":12},"final_pose_error":0.01005,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50664,-0.07453,0.03387],"final_tcp_position":[0.4938,-0.0465,0.13065],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":82.19735,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05659,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52586,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":713.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_peg","tcp_end":[0.52203,0.12084,0.09802],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":278.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.05659,0.03378],"object_pos_start":[0.50615,0.05659,0.03376],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":18.7449,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":279.0,"raw_peak_contact_force":18.7449,"subtask_id":"reach_peg","tcp_end":[0.50978,0.08593,0.05877],"tcp_start":[0.52203,0.12084,0.09802],"tcp_to_object_dist_end":0.03871,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":128.0,"n_steps_budget":960.0,"object_pos_end":[0.49878,0.0357,0.03512],"object_pos_start":[0.50614,0.05659,0.03378],"object_to_goal_dist_end":0.11581,"object_to_goal_dist_start":0.13687,"object_z_max":0.03787,"peak_contact_force":0.48412,"phase_name":"align_pusher","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":182.0,"raw_peak_contact_force":82.19735,"subtask_id":"push_through_channel","tcp_end":[0.50402,0.06565,0.03718],"tcp_start":[0.50978,0.08593,0.05877],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50676,-0.07517,0.03561],"object_pos_start":[0.49878,0.0357,0.03512],"object_to_goal_dist_end":0.0094,"object_to_goal_dist_start":0.11581,"object_z_max":0.03602,"peak_contact_force":1.4264,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1826.0,"raw_peak_contact_force":9.68561,"subtask_id":"push_through_channel","tcp_end":[0.49703,-0.04672,0.03475],"tcp_start":[0.50402,0.06565,0.03718],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":847.0,"n_steps_budget":960.0,"object_pos_end":[0.50664,-0.07453,0.03387],"object_pos_start":[0.50676,-0.07517,0.03561],"object_to_goal_dist_end":0.01057,"object_to_goal_dist_start":0.0094,"object_z_max":0.03573,"peak_contact_force":0.55213,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":991.0,"raw_peak_contact_force":6.70246,"tcp_end":[0.4938,-0.0465,0.13065],"tcp_start":[0.49703,-0.04672,0.03475],"tcp_to_object_dist_end":0.10157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67308,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_pusher.align_speed":0.0277,"approach_peg.approach_height":0.06092,"approach_peg.lateral_offset":0.0199,"approach_peg.speed":0.09318,"contact_peg.contact_force":9.50302,"push_along_channel.push_speed":0.07638,"push_along_channel.push_time_limit":5.62165,"retract_from_channel.retract_height":0.13485,"retract_from_channel.speed":0.0909},"optimized_scores":{"best_composite_score":0.27478,"best_fitness_score":0.56478,"best_task_score":0.24352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50416,0.07964,0.00768],"force_p95":187.60895,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.64896,"mean_force":133.08414,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.49633,0.09319,0.05075]},{"body_a":"attachment","body_b":"peg","contact_count":337.0,"contact_point_centroid":[0.50508,0.08616,0.05256],"force_p95":187.95013,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.16555,"mean_force":140.45041,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.49616,0.09361,0.05115]},{"body_a":"attachment","body_b":"peg","contact_count":968.0,"contact_point_centroid":[0.49763,0.01159,0.03695],"force_p95":31.01536,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.46635,"mean_force":14.54671,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49517,0.0231,0.03708]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49853,-0.04513,0.03714],"force_p95":38.19888,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.0933,"mean_force":12.18594,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49562,-0.03381,0.03734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":842.0,"contact_point_centroid":[0.50187,-0.06755,0.00997],"force_p95":0.73379,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.73395,"mean_force":0.71829,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49303,-0.03378,0.09774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":75.0,"contact_point_centroid":[0.50158,-0.10044,0.04492],"force_p95":38.04502,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.40454,"mean_force":26.54255,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49603,-0.03103,0.03637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.49988,-0.00961,0.0099],"force_p95":17.97092,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.51519,"mean_force":13.47593,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4952,0.02491,0.03716]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47438,0.053,0.0569],"force_p95":32.60834,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.01188,"mean_force":7.08722,"phase_index":2.0,"phase_name":"align_pusher","phase_type":"align","tcp_position_centroid":[0.50064,0.08676,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":762.0,"contact_point_centroid":[0.50288,-0.10002,0.04802],"force_p95":0.41911,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.74087,"mean_force":0.39449,"phase_index":4.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49298,-0.03379,0.10325]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.49385,0.07993,0.00938],"force_p95":0.55096,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.35739,"mean_force":0.61281,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48652,0.12377,0.08337]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49723,0.0976,0.05872],"force_p95":23.9641,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.9641,"mean_force":23.9641,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48778,0.10486,0.06008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.49408,0.07992,0.00937],"force_p95":0.58811,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56869,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49292,0.17039,0.20044]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49934,0.19858,0.2959]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52522,0.02768,0.05429],"force_p95":1.91846,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15834,"mean_force":0.69918,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49545,0.08205,0.03913]}],"total_contact_groups":14},"final_pose_error":0.01104,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50225,-0.07009,0.04066],"final_tcp_position":[0.49329,-0.0338,0.16062],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":193.64896,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.49383,0.07995,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55777,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":612.0,"raw_peak_contact_force":3.77147,"subtask_id":"reach_peg","tcp_end":[0.48777,0.14319,0.10996],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":360.0,"n_steps_budget":630.0,"object_pos_end":[0.49384,0.07994,0.03378],"object_pos_start":[0.49383,0.07995,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16019,"object_z_max":0.03378,"peak_contact_force":24.35739,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":361.0,"raw_peak_contact_force":24.35739,"subtask_id":"reach_peg","tcp_end":[0.4878,0.10475,0.05994],"tcp_start":[0.48777,0.14319,0.10996],"tcp_to_object_dist_end":0.03655,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":357.0,"n_steps_budget":840.0,"object_pos_end":[0.49691,0.05139,0.03945],"object_pos_start":[0.49384,0.07994,0.03378],"object_to_goal_dist_end":0.13142,"object_to_goal_dist_start":0.16018,"object_z_max":0.03928,"peak_contact_force":0.31897,"phase_name":"align_pusher","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":704.0,"raw_peak_contact_force":193.64896,"subtask_id":"push_through_channel","tcp_end":[0.49734,0.08524,0.04146],"tcp_start":[0.4878,0.10475,0.05994],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50145,-0.07108,0.03984],"object_pos_start":[0.49691,0.05139,0.03945],"object_to_goal_dist_end":0.00903,"object_to_goal_dist_start":0.13142,"object_z_max":0.04061,"peak_contact_force":52.25197,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2056.0,"raw_peak_contact_force":53.46635,"subtask_id":"push_through_channel","tcp_end":[0.49628,-0.03394,0.0364],"tcp_start":[0.49734,0.08524,0.04146],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":842.0,"n_steps_budget":930.0,"object_pos_end":[0.50225,-0.07009,0.04066],"object_pos_start":[0.50145,-0.07108,0.03984],"object_to_goal_dist_end":0.01018,"object_to_goal_dist_start":0.00903,"object_z_max":0.04074,"peak_contact_force":0.47719,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1624.0,"raw_peak_contact_force":47.0933,"tcp_end":[0.49329,-0.0338,0.16062],"tcp_start":[0.49628,-0.03394,0.0364],"tcp_to_object_dist_end":0.12565,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```