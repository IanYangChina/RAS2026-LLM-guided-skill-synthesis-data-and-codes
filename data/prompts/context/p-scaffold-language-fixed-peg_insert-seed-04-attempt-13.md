## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.4138 | 0.94 | ✅ accepted |
| 12 | align → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 13 | -0.1702 | 0.93 | ❌ rejected |
| 11 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.4148 | 0.94 | ❌ rejected |
| 10 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 16 | -0.5176 | 0.93 | ❌ rejected |
| 9 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 14 | -0.4146 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5354444884457894, 0.000906204225148928, 0.08]
- Frozen socket pose: [0.5354444884457894, 0.000906204225148928, 0.025] (static fixture for this episode)
- Goal object position: (0.5354444884457894, 0.000906204225148928, 0.025)
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
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5354444884457894, 0.000906204225148928, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5354444884457894, 0.000906204225148928, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.414) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: align
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.09
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.07
- id: insert
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.06
phases:
- id: align_to_socket
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.095
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.03
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: approach_socket
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.055
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: contact_entry
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 12.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.015
      - 0.04
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: excessive_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.003
- id: insert_down
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.045
    offset_along_axis:
      distance: -0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.008
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force:
      type: scalar
      range:
      - 10.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.insert_force_guard.threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: insert_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: continue
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_up
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.08
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
- **align_to_socket** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.095], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.03
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_entry** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.04], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=excessive_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.003]
- **insert_down** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.045], offset_along_axis={axis=channel_axis, distance=-0.04, mode=add_to_offset, sign=positive}, tolerance=0.008
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force: status=consumed; consumers=guards.insert_force_guard.threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=insert_force_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=40.0
  - retries: max_attempts=0, strategy=repeat
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.414
- **task_score** (E): 0.939
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.790

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 1.00 | 0.00 | 0.1751 |
| approach_socket | 1.00 | 0.00 | 0.0652 |
| contact_entry | 0.00 | 0.00 | 0.0121 |
| insert_down | 0.33 | 0.67 | 0.0102 |
| retract_up | 0.00 | 0.00 | 0.1068 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.002, 0.126) | (0.504, -0.000, 0.340)→(0.511, -0.002, 0.166) | 0.260→0.087 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_socket | approach | 1.00 / step_budget | (0.510, -0.002, 0.126)→(0.516, 0.004, 0.063) | (0.511, -0.002, 0.166)→(0.517, 0.004, 0.103) | 0.087→0.035 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_entry | contact | 0.00 / step_budget | (0.516, 0.004, 0.063)→(0.519, 0.005, 0.060) | (0.517, 0.004, 0.103)→(0.520, 0.005, 0.100) | 0.035→0.034 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_down | insert | 0.33 / guard_failure | (0.519, 0.005, 0.060)→(0.517, 0.005, 0.050) | (0.520, 0.005, 0.100)→(0.518, 0.005, 0.090) | 0.034→0.027 | 0.67 / 0.667 | 85.517 | 85.517 |
| retract_up | retract | 0.00 / step_budget | (0.517, 0.005, 0.050)→(0.514, 0.022, 0.156) | (0.518, 0.005, 0.090)→(0.515, 0.022, 0.196) | 0.027→0.120 | 0.00 / 0.000 | 0.000 | 86.091 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.998
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.998
- phase_score: 0.001
- phase_breakdown.insert_score: 0.001
- phase_breakdown.align_score: 0.001
- phase_breakdown.contact_score: 0.001
- phase_breakdown.approach_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.400
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.998
- **Median Q (composite search score)**: -0.423
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.342


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9dafd9212fa57d4ed6b507cf5ac09991f034abfc2fa41dbd37d7c702246c6284`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ab22a59b7a3c9c0e28c9743e3882e986d7ba7a97654ba206ec4bffa38a24163`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_offset_x":-0.00359,"align_to_socket.lateral_offset_y":-0.00574,"align_to_socket.speed":0.06181,"approach_socket.approach_z_offset":0.03366,"approach_socket.speed":0.02818,"contact_entry.contact_force":8.30483,"contact_entry.lateral_offset_x":-0.00969,"contact_entry.lateral_offset_y":-0.00817,"contact_entry.speed":0.02659,"insert_down.insertion_depth":0.03599,"insert_down.insertion_force":31.56993,"insert_down.speed":0.01577,"retract_up.retract_height":0.18156,"retract_up.speed":0.04619},"optimized_scores":{"best_composite_score":-0.42801,"best_fitness_score":0.36199,"best_task_score":0.90355},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":201.0,"contact_point_centroid":[0.50544,0.00297,0.06796],"force_p95":154.60231,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":168.55579,"mean_force":74.99074,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52042,0.00297,0.06752]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53801,-0.00444,0.04992],"force_p95":112.81423,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.81423,"mean_force":112.81423,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.52302,-0.00473,0.05015]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.53807,-0.00432,0.04985],"force_p95":63.16724,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.57774,"mean_force":39.77887,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52308,-0.0046,0.05]}],"total_contact_groups":3},"final_pose_error":0.08961,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.51972,0.01305,0.14377],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":168.55579,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52586,-0.00439,0.17188],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09556,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52539,-0.00439,0.13189],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.53153,0.00039,0.09962],"object_pos_start":[0.52586,-0.00439,0.17188],"object_to_goal_dist_end":0.03714,"object_to_goal_dist_start":0.09556,"object_z_max":0.17188,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.53057,0.00039,0.05963],"tcp_start":[0.52539,-0.00439,0.13189],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":313.0,"n_steps_budget":600.0,"object_pos_end":[0.52373,-0.0064,0.09933],"object_pos_start":[0.53153,0.00039,0.09962],"object_to_goal_dist_end":0.03127,"object_to_goal_dist_start":0.03714,"object_z_max":0.09962,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5223,-0.0064,0.05936],"tcp_start":[0.53057,0.00039,0.05963],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.52387,-0.00469,0.08998],"object_pos_start":[0.52373,-0.0064,0.09933],"object_to_goal_dist_end":0.0263,"object_to_goal_dist_start":0.03127,"object_z_max":0.09933,"peak_contact_force":112.81423,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":112.81423,"tcp_end":[0.52307,-0.0047,0.04999],"tcp_start":[0.5223,-0.0064,0.05936],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52099,0.01307,0.18375],"object_pos_start":[0.52387,-0.00469,0.08998],"object_to_goal_dist_end":0.10665,"object_to_goal_dist_start":0.0263,"object_z_max":0.18366,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":209.0,"raw_peak_contact_force":168.55579,"tcp_end":[0.51972,0.01305,0.14377],"tcp_start":[0.52307,-0.0047,0.04999],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1cd3bcde9ecee8889beeec63bba6949652ce08dd1277aacff8bc717cc59ca677`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73864,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_offset_x":-0.01739,"align_to_socket.lateral_offset_y":-0.01971,"align_to_socket.speed":0.02894,"approach_socket.approach_z_offset":0.03295,"approach_socket.speed":0.04611,"contact_entry.contact_force":8.78404,"contact_entry.lateral_offset_x":0.00848,"contact_entry.lateral_offset_y":0.00881,"contact_entry.speed":0.03771,"insert_down.insertion_depth":0.02507,"insert_down.insertion_force":41.9875,"insert_down.speed":0.00609,"retract_up.retract_height":0.19173,"retract_up.speed":0.07379},"optimized_scores":{"best_composite_score":-0.42308,"best_fitness_score":0.36692,"best_task_score":0.91594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.51982,0.05464,0.08],"force_p95":41.34564,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.97267,"mean_force":31.53042,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51978,0.03965,0.0786]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53824,0.02959,0.04999],"force_p95":23.16112,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.1622,"mean_force":10.44709,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52325,0.02917,0.05029]}],"total_contact_groups":2},"final_pose_error":0.07194,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52063,0.04609,0.17249],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":49.97267,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.00465,0.16323],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08345,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50328,0.00464,0.12324],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":804.0,"n_steps_budget":960.0,"object_pos_end":[0.52027,0.02344,0.09621],"object_pos_start":[0.50374,0.00465,0.16323],"object_to_goal_dist_end":0.03497,"object_to_goal_dist_start":0.08345,"object_z_max":0.16323,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.51934,0.02341,0.05622],"tcp_start":[0.50328,0.00464,0.12324],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.52883,0.03215,0.09893],"object_pos_start":[0.52027,0.02344,0.09621],"object_to_goal_dist_end":0.04715,"object_to_goal_dist_start":0.03497,"object_z_max":0.09892,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52743,0.03208,0.05895],"tcp_start":[0.51934,0.02341,0.05622],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.52462,0.0294,0.09064],"object_pos_start":[0.52883,0.03215,0.09893],"object_to_goal_dist_end":0.0398,"object_to_goal_dist_start":0.04715,"object_z_max":0.09893,"peak_contact_force":0.0,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52385,0.02937,0.05065],"tcp_start":[0.52743,0.03208,0.05895],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52189,0.04617,0.21247],"object_pos_start":[0.52462,0.0294,0.09064],"object_to_goal_dist_end":0.14199,"object_to_goal_dist_start":0.0398,"object_z_max":0.21234,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":19.0,"raw_peak_contact_force":49.97267,"tcp_end":[0.52063,0.04609,0.17249],"tcp_start":[0.52385,0.02937,0.05065],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3a12d7f15d1e6c6a0af002631f15bc7a534f5434829fc9db32b3974b909f1f84`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77041,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_offset_x":0.00294,"align_to_socket.lateral_offset_y":0.00751,"align_to_socket.speed":0.06523,"approach_socket.approach_z_offset":0.0443,"approach_socket.speed":0.02642,"contact_entry.contact_force":6.70491,"contact_entry.lateral_offset_x":0.00878,"contact_entry.lateral_offset_y":0.00239,"contact_entry.speed":0.02896,"insert_down.insertion_depth":0.04812,"insert_down.insertion_force":25.06385,"insert_down.speed":0.01519,"retract_up.retract_height":0.17513,"retract_up.speed":0.04669},"optimized_scores":{"best_composite_score":-0.39025,"best_fitness_score":0.39975,"best_task_score":0.99792},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51844,-0.01029,0.04989],"force_p95":143.73727,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.73727,"mean_force":143.73727,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.50346,-0.01073,0.05007]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.5181,-0.01109,0.04977],"force_p95":38.72501,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.74465,"mean_force":24.00279,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50312,-0.01067,0.04983]}],"total_contact_groups":2},"final_pose_error":0.07644,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50018,0.00586,0.15044],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":143.73727,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.50277,-0.00482,0.16326],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08344,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50231,-0.00482,0.12326],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50011,-0.01144,0.11228],"object_pos_start":[0.50277,-0.00482,0.16326],"object_to_goal_dist_end":0.03424,"object_to_goal_dist_start":0.08344,"object_z_max":0.16326,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4992,-0.01143,0.07229],"tcp_start":[0.50231,-0.00482,0.12326],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.50783,-0.0103,0.10111],"object_pos_start":[0.50011,-0.01144,0.11228],"object_to_goal_dist_end":0.02476,"object_to_goal_dist_start":0.03424,"object_z_max":0.11228,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50646,-0.01029,0.06113],"tcp_start":[0.4992,-0.01143,0.07229],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.50418,-0.01075,0.08985],"object_pos_start":[0.50783,-0.0103,0.10111],"object_to_goal_dist_end":0.01517,"object_to_goal_dist_start":0.02476,"object_z_max":0.10111,"peak_contact_force":143.73727,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":143.73727,"tcp_end":[0.50342,-0.01074,0.04986],"tcp_start":[0.50646,-0.01029,0.06113],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50138,0.00586,0.19042],"object_pos_start":[0.50418,-0.01075,0.08985],"object_to_goal_dist_end":0.11059,"object_to_goal_dist_start":0.01517,"object_z_max":0.19032,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":11.0,"raw_peak_contact_force":39.74465,"tcp_end":[0.50018,0.00586,0.15044],"tcp_start":[0.50342,-0.01074,0.04986],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```