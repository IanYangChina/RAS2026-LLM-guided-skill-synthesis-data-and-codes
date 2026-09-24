## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1338 | 0.95 | ✅ accepted |
| 12 | approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1819 | 0.94 | ✅ accepted |
| 11 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.2282 | 0.88 | ❌ rejected |
| 10 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.1029 | 0.94 | ✅ accepted |
| 9 | approach → align → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.1090 | 0.93 | ❌ rejected |

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
    - 0.05
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
      - 25.0
      default: 15.0
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
      - 40.0
      - 120.0
      default: 80.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    insert_depth_add:
      type: scalar
      range:
      - -0.08
      - 0.0
      default: -0.05
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
      - -0.04
      - 0.04
      default: 0.02
      binds_to:
      - path: retry.offset.x
        mode: add
    retry_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.02
      binds_to:
      - path: retry.offset.y
        mode: add
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 80.0
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
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.05], tolerance=0.01
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
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=80.0
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
| approach_arc | 1.00 | 0.33 | 0.2212 |
| contact_probe | 1.00 | 1.00 | 0.0087 |
| insert | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.009, 0.080) | (0.504, -0.000, 0.340)→(0.504, 0.009, 0.119) | 0.260→0.042 | 0.33 / 0.333 | 24.383 | 0.000 |
| contact_probe | contact | 1.00 / force_exceeded | (0.500, 0.009, 0.080)→(0.498, 0.008, 0.071) | (0.504, 0.009, 0.119)→(0.503, 0.008, 0.111) | 0.042→0.034 | 1.00 / 1.000 | 56.948 | 22.017 |
| insert | insert | 0.00 / guard_failure | (0.498, 0.008, 0.071)→(0.498, 0.008, 0.071) | (0.503, 0.008, 0.111)→(0.503, 0.008, 0.111) | 0.034→0.034 | 1.00 / 1.000 | 91.724 | 105.577 |

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
- **Median Q (composite search score)**: 0.130
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40385,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.0619,"approach_arc.lateral_x":0.00117,"approach_arc.lateral_y":-0.00229,"approach_arc.speed_approach":0.06607,"contact_probe.contact_force_threshold":11.95178,"contact_probe.contact_speed":0.01891,"insert.force_limit":63.57788,"insert.insert_depth_add":-0.0269,"insert.insert_speed":0.01286,"insert.retry_x":-0.00012,"insert.retry_y":-0.00564},"optimized_scores":{"best_composite_score":0.15292,"best_fitness_score":0.39959,"best_task_score":0.99765},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.5123,-0.00858,0.04995],"force_p95":76.17919,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.44529,"mean_force":71.7343,"phase_index":2.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.49741,-0.00853,0.05177]}],"total_contact_groups":1},"final_pose_error":0.05405,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49736,-0.00857,0.05171],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":76.44529,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.50489,-0.00592,0.11607],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.03688,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.50031,-0.00591,0.07633],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.50254,-0.00852,0.09151],"object_pos_start":[0.50489,-0.00592,0.11607],"object_to_goal_dist_end":0.01455,"object_to_goal_dist_start":0.03688,"object_z_max":0.11607,"peak_contact_force":62.53116,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.49751,-0.00851,0.05183],"tcp_start":[0.50031,-0.00591,0.07633],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50245,-0.00854,0.09147],"object_pos_start":[0.50254,-0.00852,0.09151],"object_to_goal_dist_end":0.01451,"object_to_goal_dist_start":0.01455,"object_z_max":0.09151,"peak_contact_force":63.88525,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":76.44529,"subtask_id":"insert","tcp_end":[0.49736,-0.00857,0.05171],"tcp_start":[0.49734,-0.00856,0.05173],"tcp_to_object_dist_end":0.04008,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86364,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.04097,"approach_arc.lateral_x":-0.00723,"approach_arc.lateral_y":-0.02499,"approach_arc.speed_approach":0.08043,"contact_probe.contact_force_threshold":12.87932,"contact_probe.contact_speed":0.00724,"insert.force_limit":110.95546,"insert.insert_depth_add":-0.01346,"insert.insert_speed":0.01306,"insert.retry_x":-0.00232,"insert.retry_y":-0.02991},"optimized_scores":{"best_composite_score":0.12993,"best_fitness_score":0.3766,"best_task_score":0.93936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.50808,0.00176,0.07986],"force_p95":127.52281,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.54891,"mean_force":100.11301,"phase_index":2.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.49878,0.01345,0.08074]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50788,0.00177,0.07997],"force_p95":66.05094,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.05094,"mean_force":66.05094,"phase_index":1.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.49892,0.01376,0.08097]}],"total_contact_groups":2},"final_pose_error":0.07243,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49875,0.0133,0.08067],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":134.54891,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":770.0,"n_steps_budget":1000.0,"object_pos_end":[0.50351,0.01376,0.12071],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04312,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":73.15028,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.49892,0.01376,0.08097],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5035,0.01365,0.12058],"object_pos_start":[0.50351,0.01376,0.12071],"object_to_goal_dist_end":0.04296,"object_to_goal_dist_start":0.04312,"object_z_max":0.12071,"peak_contact_force":66.05094,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":66.05094,"subtask_id":"contact","tcp_end":[0.49891,0.01365,0.08085],"tcp_start":[0.49892,0.01376,0.08097],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.01341,0.12047],"object_pos_start":[0.5035,0.01365,0.12058],"object_to_goal_dist_end":0.04274,"object_to_goal_dist_start":0.04296,"object_z_max":0.12058,"peak_contact_force":105.55058,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":7.0,"raw_peak_contact_force":134.54891,"subtask_id":"insert","tcp_end":[0.49875,0.0133,0.08067],"tcp_start":[0.49874,0.01332,0.08067],"tcp_to_object_dist_end":0.04004,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00775,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_arc.arc_height":0.0347,"approach_arc.lateral_x":0.01718,"approach_arc.lateral_y":-0.02487,"approach_arc.speed_approach":0.0365,"contact_probe.contact_force_threshold":16.51052,"contact_probe.contact_speed":0.0243,"insert.force_limit":73.63243,"insert.insert_depth_add":-0.07668,"insert.insert_speed":0.01529,"insert.retry_x":-0.02188,"insert.retry_y":-0.01711},"optimized_scores":{"best_composite_score":0.11865,"best_fitness_score":0.36532,"best_task_score":0.91116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50934,0.00897,0.07992],"force_p95":103.90079,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.73663,"mean_force":91.18606,"phase_index":2.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.49878,0.01954,0.08106]}],"total_contact_groups":1},"final_pose_error":0.13463,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49859,0.01951,0.08095],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":105.73663,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.50406,0.01986,0.12171],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04637,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach","tcp_end":[0.49948,0.01985,0.08197],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.5036,0.01959,0.12087],"object_pos_start":[0.50406,0.01986,0.12171],"object_to_goal_dist_end":0.04547,"object_to_goal_dist_start":0.04637,"object_z_max":0.12171,"peak_contact_force":42.26227,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"contact","tcp_end":[0.49896,0.01957,0.08114],"tcp_start":[0.49948,0.01985,0.08197],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50345,0.01956,0.12081],"object_pos_start":[0.5036,0.01959,0.12087],"object_to_goal_dist_end":0.04538,"object_to_goal_dist_start":0.04547,"object_z_max":0.12087,"peak_contact_force":105.73663,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":105.73663,"subtask_id":"insert","tcp_end":[0.49859,0.01951,0.08095],"tcp_start":[0.49863,0.01952,0.08098],"tcp_to_object_dist_end":0.04015,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```