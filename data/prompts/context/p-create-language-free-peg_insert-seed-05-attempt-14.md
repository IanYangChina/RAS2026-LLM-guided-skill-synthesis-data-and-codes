## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | 0.0194 | 0.91 | ❌ rejected |
| 13 | approach → align → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | 0.0466 | 0.97 | ❌ rejected |
| 12 | approach → align → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | 0.1624 | 0.97 | ❌ rejected |
| 11 | approach → align → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | 0.2123 | 0.97 | ❌ rejected |
| 10 | approach → align → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.3763 | 0.98 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5244002338996304, 0.024635263178919502, 0.08]
- Frozen socket pose: [0.5244002338996304, 0.024635263178919502, 0.025] (static fixture for this episode)
- Goal object position: (0.5244002338996304, 0.024635263178919502, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5244, 0.0246, 0.08]
  frozen_socket_position: [0.5244, 0.0246, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5244002338996304, 0.024635263178919502, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5244002338996304, 0.024635263178919502, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.980, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, 0.024635263178919502, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5244002338996304, 0.024635263178919502, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.019) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_standoff
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_hole_entry
  weight: 0.4
- id: reach_full_insertion
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - -0.05
  weight: 0.3
phases:
- id: approach_1
  type: approach
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
  subtask_id: reach_standoff
- id: align_1
  type: align
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
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_standoff
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.15
      - -0.05
      default: -0.1
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
  subtask_id: reach_hole_entry
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - -0.08
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
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
  subtask_id: reach_hole_entry
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.065
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_full_insertion
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
    tolerance: 0.01
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.019
- **task_score** (E): 0.906
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1045 |
| align_1 | 1.00 | 0.00 | 0.0183 |
| descend_1 | 1.00 | 0.33 | 0.0840 |
| contact_1 | 0.67 | 0.67 | 0.0394 |
| insert_1 | 0.33 | 1.00 | 0.0070 |
| retract_1 | 1.00 | 0.00 | 0.0890 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.012, 0.198) | (0.504, -0.000, 0.340)→(0.512, 0.012, 0.238) | 0.260→0.160 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.508, 0.012, 0.198)→(0.521, 0.011, 0.186) | (0.512, 0.012, 0.238)→(0.526, 0.011, 0.226) | 0.160→0.150 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.521, 0.011, 0.186)→(0.517, 0.011, 0.102) | (0.526, 0.011, 0.226)→(0.523, 0.011, 0.142) | 0.150→0.070 | 0.33 / 0.333 | 86.926 | 102.312 |
| contact_1 | contact | 0.67 / force_exceeded | (0.517, 0.011, 0.102)→(0.514, 0.011, 0.063) | (0.523, 0.011, 0.142)→(0.520, 0.011, 0.103) | 0.070→0.037 | 0.67 / 0.667 | 50.409 | 27.661 |
| insert_1 | insert | 0.33 / guard_failure | (0.513, 0.011, 0.058)→(0.512, 0.011, 0.051) | (0.520, 0.011, 0.103)→(0.516, 0.011, 0.091) | 0.037→0.028 | 1.00 / 1.000 | 126.935 | 71.804 |
| retract_1 | retract | 1.00 / step_budget | (0.512, 0.011, 0.051)→(0.509, 0.011, 0.140) | (0.516, 0.011, 0.091)→(0.513, 0.011, 0.180) | 0.027→0.103 | 0.00 / 0.000 | 0.000 | 225.077 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.936
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.936
- phase_score: 0.547
- phase_breakdown.reach_full_insertion_score: 0.575
- phase_breakdown.reach_standoff_score: 0.289
- phase_breakdown.reach_hole_entry_score: 0.719

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.703
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.936
- **Median Q (composite search score)**: 0.042
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.284


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5dab308f3f0d3a4c4fc859445abf2870fb989899bfcd82caf016befc5af88e16`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `195061a138fd9757490665621e9d85a89af1c36de72bed7c93df67d7bd9941b0`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23669,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.02053,"align_1.lateral_offset_y":-0.01326,"align_1.speed":0.05102,"approach_1.speed":0.06598,"contact_1.contact_force":13.84473,"contact_1.speed":0.03292,"descend_1.descend_z":-0.10343,"descend_1.speed":0.07521,"insert_1.guard_force_threshold":17.4971,"insert_1.insertion_depth":0.04583,"insert_1.retry_offset_x":0.00463,"insert_1.retry_offset_y":0.00268,"retract_1.speed":0.04222},"optimized_scores":{"best_composite_score":0.04243,"best_fitness_score":0.64577,"best_task_score":0.89978},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.53391,0.0164,0.04993],"force_p95":373.46647,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":400.27126,"mean_force":163.68539,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51907,0.01606,0.05198]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53421,0.0165,0.04996],"force_p95":85.63922,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.05793,"mean_force":82.7584,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51937,0.01618,0.05209]}],"total_contact_groups":2},"final_pose_error":0.01007,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51576,0.01599,0.1425],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":400.27126,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.52201,0.01985,0.23747],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16024,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.51744,0.01983,0.19773],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":43.0,"n_steps_budget":600.0,"object_pos_end":[0.5321,0.01659,0.22665],"object_pos_start":[0.52201,0.01985,0.23747],"object_to_goal_dist_end":0.15103,"object_to_goal_dist_start":0.16024,"object_z_max":0.23747,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.52722,0.01655,0.18695],"tcp_start":[0.51744,0.01983,0.19773],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":295.0,"n_steps_budget":870.0,"object_pos_end":[0.52891,0.01644,0.13228],"object_pos_start":[0.5321,0.01659,0.22665],"object_to_goal_dist_end":0.06196,"object_to_goal_dist_start":0.15103,"object_z_max":0.22665,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hole_entry","tcp_end":[0.52355,0.01638,0.09264],"tcp_start":[0.52722,0.01655,0.18695],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.52529,0.01626,0.09174],"object_pos_start":[0.52891,0.01644,0.13228],"object_to_goal_dist_end":0.03227,"object_to_goal_dist_start":0.06196,"object_z_max":0.13228,"peak_contact_force":68.24519,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hole_entry","tcp_end":[0.51945,0.01619,0.05217],"tcp_start":[0.52355,0.01638,0.09264],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.5252,0.01625,0.09166],"object_pos_start":[0.52529,0.01626,0.09174],"object_to_goal_dist_end":0.03217,"object_to_goal_dist_start":0.03227,"object_z_max":0.09174,"peak_contact_force":86.05793,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":86.05793,"subtask_id":"reach_full_insertion","tcp_end":[0.5192,0.01615,0.05197],"tcp_start":[0.51929,0.01616,0.05202],"tcp_to_object_dist_end":0.04014,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52191,0.01608,0.18203],"object_pos_start":[0.52488,0.01622,0.09156],"object_to_goal_dist_end":0.10559,"object_to_goal_dist_start":0.03187,"object_z_max":0.18195,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":6.0,"raw_peak_contact_force":400.27126,"tcp_end":[0.51576,0.01599,0.1425],"tcp_start":[0.5192,0.01615,0.05197],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2449f4fe819a4bbdd9aec1335ce72ae3bc4ae0ee808de76617a31b3392ec72d5`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.59316,"average_solve_count":263.0,"average_success_count":263.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.03881,"align_1.lateral_offset_y":0.00234,"align_1.speed":0.07966,"approach_1.speed":0.0546,"contact_1.contact_force":8.8868,"contact_1.speed":0.04157,"descend_1.descend_z":-0.12094,"descend_1.speed":0.02329,"insert_1.guard_force_threshold":19.30368,"insert_1.insertion_depth":0.02981,"insert_1.retry_offset_x":0.00065,"insert_1.retry_offset_y":-0.0026,"retract_1.speed":0.02788},"optimized_scores":{"best_composite_score":0.09922,"best_fitness_score":0.70255,"best_task_score":0.93621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":36.0,"contact_point_centroid":[0.53314,-0.01027,0.07999],"force_p95":295.7689,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.93657,"mean_force":231.34609,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51757,-0.01023,0.0765]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.5332,-0.01037,0.07998],"force_p95":78.8329,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.982,"mean_force":41.491,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51694,-0.01032,0.07138]},{"body_a":"attachment","body_b":"peg_socket","contact_count":18.0,"contact_point_centroid":[0.52773,-0.01061,0.04972],"force_p95":41.46292,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.8805,"mean_force":12.48209,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51276,-0.01024,0.05024]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53316,-0.01038,0.07999],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51682,-0.01032,0.07121]}],"total_contact_groups":4},"final_pose_error":0.01437,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.51002,-0.01025,0.1366],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":306.93657,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50456,-0.00999,0.23908],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15946,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.49997,-0.00998,0.19934],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.52734,-0.01015,0.22366],"object_pos_start":[0.50456,-0.00999,0.23908],"object_to_goal_dist_end":0.14659,"object_to_goal_dist_start":0.15946,"object_z_max":0.23908,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.52235,-0.01015,0.18398],"tcp_start":[0.49997,-0.00998,0.19934],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.52274,-0.01033,0.11103],"object_pos_start":[0.52734,-0.01015,0.22366],"object_to_goal_dist_end":0.03984,"object_to_goal_dist_start":0.14659,"object_z_max":0.22366,"peak_contact_force":260.77679,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36.0,"raw_peak_contact_force":306.93657,"subtask_id":"reach_hole_entry","tcp_end":[0.51699,-0.01032,0.07145],"tcp_start":[0.52235,-0.01015,0.18398],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.52259,-0.01034,0.11079],"object_pos_start":[0.52274,-0.01033,0.11103],"object_to_goal_dist_end":0.03956,"object_to_goal_dist_start":0.03984,"object_z_max":0.11103,"peak_contact_force":82.982,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":82.982,"subtask_id":"reach_hole_entry","tcp_end":[0.51682,-0.01032,0.07121],"tcp_start":[0.51699,-0.01032,0.07145],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":66.0,"n_steps_budget":600.0,"object_pos_end":[0.51549,-0.01028,0.0905],"object_pos_start":[0.52259,-0.01034,0.11079],"object_to_goal_dist_end":0.02135,"object_to_goal_dist_start":0.03956,"object_z_max":0.11079,"peak_contact_force":240.64911,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_full_insertion","tcp_end":[0.51343,-0.01027,0.05055],"tcp_start":[0.51682,-0.01032,0.07121],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51255,-0.01027,0.17652],"object_pos_start":[0.51549,-0.01028,0.0905],"object_to_goal_dist_end":0.09787,"object_to_goal_dist_start":0.02135,"object_z_max":0.17643,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":18.0,"raw_peak_contact_force":46.8805,"tcp_end":[0.51002,-0.01025,0.1366],"tcp_start":[0.51343,-0.01027,0.05055],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c3c1e2ca75f8f9fa89b5aa82a3db3edf9cebca69b40eef83389e8297541d8019`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0215,"align_1.lateral_offset_y":-0.00198,"align_1.speed":0.05646,"approach_1.speed":0.0484,"contact_1.contact_force":15.56103,"contact_1.speed":0.01422,"descend_1.descend_z":-0.0543,"descend_1.speed":0.0994,"insert_1.guard_force_threshold":30.32424,"insert_1.insertion_depth":0.03971,"insert_1.retry_offset_x":-0.00786,"insert_1.retry_offset_y":0.00451,"retract_1.speed":0.07667},"optimized_scores":{"best_composite_score":-0.08353,"best_fitness_score":0.68647,"best_task_score":0.88136},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.5183,0.02683,0.0498],"force_p95":146.20088,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.08059,"mean_force":34.57244,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50334,0.02631,0.05058]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51858,0.02689,0.04986],"force_p95":124.47353,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":129.35354,"mean_force":88.00188,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50362,0.0264,0.05073]}],"total_contact_groups":2},"final_pose_error":0.01026,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50026,0.0262,0.14078],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":228.08059,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.51025,0.02551,0.238],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16038,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.50568,0.02548,0.19827],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.51871,0.02721,0.2281],"object_pos_start":[0.51025,0.02551,0.238],"object_to_goal_dist_end":0.15174,"object_to_goal_dist_start":0.16038,"object_z_max":0.238,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.51386,0.02716,0.1884],"tcp_start":[0.50568,0.02548,0.19827],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":149.0,"n_steps_budget":600.0,"object_pos_end":[0.51597,0.02703,0.18304],"object_pos_start":[0.51871,0.02721,0.2281],"object_to_goal_dist_end":0.10772,"object_to_goal_dist_start":0.15174,"object_z_max":0.2281,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hole_entry","tcp_end":[0.51065,0.02696,0.1434],"tcp_start":[0.51386,0.02716,0.1884],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.51247,0.0268,0.106],"object_pos_start":[0.51597,0.02703,0.18304],"object_to_goal_dist_end":0.03937,"object_to_goal_dist_start":0.10772,"object_z_max":0.18304,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_hole_entry","tcp_end":[0.50668,0.02671,0.06642],"tcp_start":[0.51065,0.02696,0.1434],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.50631,0.02649,0.09061],"object_pos_start":[0.51247,0.0268,0.106],"object_to_goal_dist_end":0.02923,"object_to_goal_dist_start":0.03937,"object_z_max":0.106,"peak_contact_force":54.09865,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":129.35354,"subtask_id":"reach_full_insertion","tcp_end":[0.50361,0.0264,0.05047],"tcp_start":[0.50362,0.02641,0.05054],"tcp_to_object_dist_end":0.04023,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":736.0,"n_steps_budget":840.0,"object_pos_end":[0.50332,0.02631,0.18066],"object_pos_start":[0.50621,0.02649,0.09038],"object_to_goal_dist_end":0.10409,"object_to_goal_dist_start":0.02912,"object_z_max":0.18056,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":10.0,"raw_peak_contact_force":228.08059,"tcp_end":[0.50026,0.0262,0.14078],"tcp_start":[0.50361,0.0264,0.05047],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```