## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1339 | 0.95 | ✅ accepted |
| 13 | approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1338 | 0.95 | ✅ accepted |
| 12 | approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1819 | 0.94 | ✅ accepted |
| 11 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.2282 | 0.88 | ❌ rejected |
| 10 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.1029 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177555, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177555, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177555, -0.012538330414932925, 0.025)
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
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177555, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177555, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e

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

## Current Skill (Q=0.134) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.09
- id: align
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
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
- id: approach_arc
  type: approach
  generator: arc_cartesian
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    lateral_x:
      type: scalar
      range:
      - -0.025
      - 0.025
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.025
      - 0.025
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed_approach:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_probe
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
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: insert
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    force_limit:
      type: scalar
      range:
      - 80.0
      - 160.0
      default: 120.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    insert_depth_add:
      type: scalar
      range:
      - -0.1
      - 0.0
      default: -0.06
      binds_to:
      - path: target.offset.z
        mode: add
    insert_speed:
      type: scalar
      range:
      - 0.001
      - 0.02
      default: 0.008
      binds_to:
      - path: generator.speed
        mode: replace
    retry_x:
      type: scalar
      range:
      - -0.06
      - 0.06
      default: 0.03
      binds_to:
      - path: retry.offset.x
        mode: add
    retry_y:
      type: scalar
      range:
      - -0.06
      - 0.06
      default: 0.03
      binds_to:
      - path: retry.offset.y
        mode: add
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 120.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insert

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_arc** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
    - speed_approach: status=consumed; consumers=generator.speed (replace)
- **contact_probe** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **insert** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - insert_depth_add: status=consumed; consumers=target.offset.z (add)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - retry_x: status=consumed; consumers=retry.offset.x (add)
    - retry_y: status=consumed; consumers=retry.offset.y (add)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=120.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.134
- **task_score** (E): 0.949
- **fitness_score**: 0.381  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_arc | 1.00 | 0.00 | 0.2163 |
| contact_probe | 1.00 | 1.00 | 0.0136 |
| insert | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, 0.011, 0.085) | (0.504, -0.000, 0.340)→(0.507, 0.011, 0.124) | 0.260→0.047 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_probe | contact | 1.00 / force_exceeded | (0.502, 0.011, 0.085)→(0.500, 0.009, 0.072) | (0.507, 0.011, 0.124)→(0.505, 0.009, 0.111) | 0.047→0.034 | 1.00 / 1.000 | 67.094 | 24.797 |
| insert | insert | 0.00 / guard_failure | (0.500, 0.009, 0.071)→(0.500, 0.009, 0.071) | (0.505, 0.009, 0.111)→(0.504, 0.009, 0.111) | 0.034→0.034 | 1.00 / 1.000 | 91.071 | 143.032 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.998
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.998
- phase_score: 0.001
- phase_breakdown.insert_score: 0.001
- phase_breakdown.align_score: 0.000
- phase_breakdown.approach_score: 0.001
- phase_breakdown.contact_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.400
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.998
- **Median Q (composite search score)**: 0.133
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.352


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2bcd5d362bce9ed2c176357e9c3237720ebba2a98dd8bfe48970c9fba5840ac0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ac7031668c6a08077e83f2359534923b723fe0e5a20a177feb2fc3bf67104f66`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11111,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.07231,"approach_arc.lateral_x":0.00084,"approach_arc.lateral_y":0.00406,"approach_arc.speed_approach":0.07962,"contact_probe.contact_force_threshold":10.96242,"contact_probe.contact_speed":0.01493,"insert.force_limit":109.02159,"insert.insert_depth_add":-0.0617,"insert.insert_speed":0.00823,"insert.retry_x":-0.04107,"insert.retry_y":0.01459},"optimized_scores":{"best_composite_score":0.15297,"best_fitness_score":0.39964,"best_task_score":0.99777},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.51219,-0.00512,0.04995],"force_p95":145.81858,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.41896,"mean_force":93.79622,"phase_index":2.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.4973,-0.00509,0.0517]}],"total_contact_groups":1},"final_pose_error":0.08879,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49733,-0.00515,0.0516],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":169.41896,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":919.0,"n_steps_budget":1000.0,"object_pos_end":[0.50461,0.00072,0.11978],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04006,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50003,0.00072,0.08005],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.50243,-0.00501,0.09149],"object_pos_start":[0.50461,0.00072,0.11978],"object_to_goal_dist_end":0.01277,"object_to_goal_dist_start":0.04006,"object_z_max":0.11978,"peak_contact_force":61.12716,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.49739,-0.00501,0.05181],"tcp_start":[0.50003,0.00072,0.08005],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50201,-0.00512,0.09139],"object_pos_start":[0.50243,-0.00501,0.09149],"object_to_goal_dist_end":0.01265,"object_to_goal_dist_start":0.01277,"object_z_max":0.09149,"peak_contact_force":96.66286,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":8.0,"raw_peak_contact_force":169.41896,"subtask_id":"insert","tcp_end":[0.49733,-0.00515,0.0516],"tcp_start":[0.49732,-0.00514,0.05162],"tcp_to_object_dist_end":0.04006,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4cf364ad7cdeb78864f76dd2c5686ed9e91b61eb5e5b2735897d619cb8f6dad4`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.02003,"approach_arc.lateral_x":-0.00481,"approach_arc.lateral_y":-0.02489,"approach_arc.speed_approach":0.07563,"contact_probe.contact_force_threshold":9.72795,"contact_probe.contact_speed":0.02323,"insert.force_limit":115.15777,"insert.insert_depth_add":-0.07095,"insert.insert_speed":0.01253,"insert.retry_x":0.00669,"insert.retry_y":-0.00927},"optimized_scores":{"best_composite_score":0.13318,"best_fitness_score":0.37985,"best_task_score":0.94742},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.51068,0.00177,0.0799],"force_p95":105.99037,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.74202,"mean_force":74.9149,"phase_index":2.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.49952,0.01169,0.08112]}],"total_contact_groups":1},"final_pose_error":0.12894,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49957,0.01173,0.08099],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":115.74202,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.01053,0.12791],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0494,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50131,0.01052,0.08817],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.50447,0.01166,0.12098],"object_pos_start":[0.50588,0.01053,0.12791],"object_to_goal_dist_end":0.04284,"object_to_goal_dist_start":0.0494,"object_z_max":0.12791,"peak_contact_force":65.76418,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.49962,0.01164,0.08128],"tcp_start":[0.50131,0.01052,0.08817],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.5041,0.01173,0.12079],"object_pos_start":[0.50447,0.01166,0.12098],"object_to_goal_dist_end":0.04264,"object_to_goal_dist_start":0.04284,"object_z_max":0.12098,"peak_contact_force":64.13356,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":115.74202,"subtask_id":"insert","tcp_end":[0.49957,0.01173,0.08099],"tcp_start":[0.49954,0.01173,0.08101],"tcp_to_object_dist_end":0.04006,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `989b6885a6cc20cf657766879d873fa27d37f906fbac12db49d02020abcc24a4`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64407,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.04327,"approach_arc.lateral_x":0.02252,"approach_arc.lateral_y":-0.02494,"approach_arc.speed_approach":0.10644,"contact_probe.contact_force_threshold":9.56122,"contact_probe.contact_speed":0.02534,"insert.force_limit":129.89068,"insert.insert_depth_add":-0.05215,"insert.insert_speed":0.00237,"insert.retry_x":0.00653,"insert.retry_y":-0.0035},"optimized_scores":{"best_composite_score":0.11551,"best_fitness_score":0.36218,"best_task_score":0.90327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.51703,0.02143,0.07981],"force_p95":136.39003,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.93403,"mean_force":107.75134,"phase_index":2.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.50213,0.02125,0.08134]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51731,0.02134,0.07993],"force_p95":74.39028,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.39028,"mean_force":74.39028,"phase_index":1.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.50242,0.02118,0.08166]}],"total_contact_groups":2},"final_pose_error":0.11093,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.50202,0.02126,0.0812],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":143.93403,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.50916,0.02101,0.12552],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05097,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50457,0.021,0.08579],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.50713,0.02125,0.12122],"object_pos_start":[0.50916,0.02101,0.12552],"object_to_goal_dist_end":0.04691,"object_to_goal_dist_start":0.05097,"object_z_max":0.12552,"peak_contact_force":74.39028,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":74.39028,"subtask_id":"contact","tcp_end":[0.50235,0.02122,0.0815],"tcp_start":[0.50457,0.021,0.08579],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,0.0213,0.12103],"object_pos_start":[0.50713,0.02125,0.12122],"object_to_goal_dist_end":0.04669,"object_to_goal_dist_start":0.04691,"object_z_max":0.12122,"peak_contact_force":112.41808,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":143.93403,"subtask_id":"insert","tcp_end":[0.50202,0.02126,0.0812],"tcp_start":[0.50202,0.02126,0.08122],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```