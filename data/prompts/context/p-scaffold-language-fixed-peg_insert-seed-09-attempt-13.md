## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0898 | 0.86 | ❌ rejected |
| 12 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2156 | 0.85 | ❌ rejected |
| 11 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0599 | 0.86 | ❌ rejected |
| 10 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0133 | 0.86 | ❌ rejected |
| 9 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0215 | 0.86 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176067, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176067, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176067, -0.017054623272995572, 0.025)
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
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176067, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176067, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464

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

## Current Skill (Q=0.090) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
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
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: align
- id: descend_to_entry
  type: approach
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
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.08
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: insert_into_hole
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
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.04
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: insert
- id: retract_from_hole
  type: retract
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_socket** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
- **descend_to_entry** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.08
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.090
- **task_score** (E): 0.858
- **fitness_score**: 0.350  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.00 | 1.00 | 0.1259 |
| contact_entry | 1.00 | 1.00 | 0.0002 |
| insert_into_hole | 0.00 | 1.00 | 0.0003 |
| retract_from_hole | 0.33 | 1.00 | 0.0283 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.008, 0.178) | (0.504, -0.000, 0.340)→(0.513, -0.007, 0.158) | 0.260→0.080 | 1.00 / 1.667 | 260.719 | 3297.615 |
| contact_entry | contact | 1.00 / force_exceeded | (0.479, -0.008, 0.178)→(0.479, -0.008, 0.178) | (0.513, -0.007, 0.158)→(0.513, -0.007, 0.158) | 0.080→0.080 | 1.00 / 1.000 | 302.021 | 554.475 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.479, -0.008, 0.178)→(0.479, -0.008, 0.178) | (0.513, -0.007, 0.158)→(0.513, -0.007, 0.158) | 0.080→0.080 | 1.00 / 1.000 | 547.302 | 380.537 |
| retract_from_hole | retract | 0.33 / step_budget | (0.479, -0.008, 0.178)→(0.504, -0.014, 0.180) | (0.514, -0.007, 0.158)→(0.541, -0.012, 0.164) | 0.080→0.095 | 1.00 / 1.000 | 151.866 | 1945.078 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.015
- phase_breakdown.contact_score: 0.018
- phase_breakdown.approach_score: 0.000
- phase_breakdown.insert_score: 0.022
- phase_breakdown.align_score: 0.005

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.355
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: 0.093
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.341


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9cec5bdbb03cce7c3c09816ace5d94f97b8f61fe750542a4a790173a53dc00b4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `aa1cc88294efeb3bf6fcf727f27d837e44fca2942932baa7feaaed37c752b2f3`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.11765,"average_mean_iterations":32.43137,"average_solve_count":51.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.09991,"align_to_socket.lateral_x":0.00111,"align_to_socket.lateral_y":0.01999,"contact_entry.contact_force_threshold":8.92563,"contact_entry.contact_speed":0.0272,"insert_into_hole.insert_speed":0.01143,"insert_into_hole.insertion_depth":0.00053,"insert_into_hole.insertion_force_threshold":21.77579,"retract_from_hole.retract_speed":0.10953},"optimized_scores":{"best_composite_score":0.09526,"best_fitness_score":0.35526,"best_task_score":0.86559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":63.0,"contact_point_centroid":[0.58008,0.04174,0.06539],"force_p95":3302.02473,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3908.04557,"mean_force":700.62527,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51997,-0.01184,0.21074]},{"body_a":"world","body_b":"link5","contact_count":58.0,"contact_point_centroid":[0.6438,0.10093,-0.00045],"force_p95":1052.3613,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1292.63055,"mean_force":555.63753,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51154,-0.00675,0.19302]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47029,0.00028,0.0792],"force_p95":964.50552,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1011.59403,"mean_force":370.14264,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45941,0.00026,0.09055]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54739,0.01347,0.07858],"force_p95":596.92026,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":797.12134,"mean_force":116.1356,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45109,-0.0001,0.1003]},{"body_a":"peg_socket","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.56791,0.00118,0.079],"force_p95":364.61825,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":507.28692,"mean_force":175.69823,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4498,-6e-05,0.11387]},{"body_a":"peg_socket","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.58957,-0.00044,0.07991],"force_p95":365.72173,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.54723,"mean_force":307.20845,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.49991,-0.00342,0.18259]},{"body_a":"peg_socket","body_b":"link6","contact_count":60.0,"contact_point_centroid":[0.58957,0.00293,0.07993],"force_p95":403.99242,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.42958,"mean_force":271.35068,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.48976,0.00287,0.19543]},{"body_a":"peg_socket","body_b":"link6","contact_count":595.0,"contact_point_centroid":[0.58956,-0.00208,0.07985],"force_p95":282.62457,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":439.35314,"mean_force":243.07046,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46206,0.00059,0.17286]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58957,-0.00067,0.07992],"force_p95":299.76999,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.03793,"mean_force":298.05063,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48384,0.00242,0.20522]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58955,-0.00066,0.0799],"force_p95":291.42926,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.42926,"mean_force":291.42926,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.48389,0.00243,0.20528]},{"body_a":"peg_socket","body_b":"link5","contact_count":11.0,"contact_point_centroid":[0.58935,0.04274,0.0497],"force_p95":249.0378,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.15343,"mean_force":103.30269,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51864,-0.01368,0.20848]},{"body_a":"peg_socket","body_b":"link5","contact_count":36.0,"contact_point_centroid":[0.5595,0.04193,0.07985],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.52022,-0.0115,0.21126]}],"total_contact_groups":12},"final_pose_error":0.09318,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52291,-0.00915,0.2176],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":3908.04557,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.51691,0.00234,0.1827],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10411,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":219.11385,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":667.0,"raw_peak_contact_force":1011.59403,"subtask_id":"align","tcp_end":[0.48389,0.00243,0.20528],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5169,0.00234,0.18269],"object_pos_start":[0.51691,0.00234,0.1827],"object_to_goal_dist_end":0.1041,"object_to_goal_dist_start":0.10411,"object_z_max":0.1827,"peak_contact_force":291.42926,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":291.42926,"subtask_id":"contact","tcp_end":[0.48387,0.00243,0.20526],"tcp_start":[0.48389,0.00243,0.20528],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51688,0.00233,0.18267],"object_pos_start":[0.5169,0.00234,0.18269],"object_to_goal_dist_end":0.10407,"object_to_goal_dist_start":0.1041,"object_z_max":0.18269,"peak_contact_force":297.35856,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":300.03793,"subtask_id":"insert","tcp_end":[0.48377,0.0024,0.20513],"tcp_start":[0.48381,0.00241,0.20518],"tcp_to_object_dist_end":0.04001,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":600.0,"object_pos_end":[0.56001,-0.00673,0.20285],"object_pos_start":[0.51683,0.00231,0.18261],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.10401,"object_z_max":0.20243,"peak_contact_force":148.31729,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":296.0,"raw_peak_contact_force":3908.04557,"tcp_end":[0.52291,-0.00915,0.2176],"tcp_start":[0.48377,0.0024,0.20513],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `688a3926bc1208c752fc2d1535fab63bd957243e02b13eac53840dc266efeb6b`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.10938,"average_mean_iterations":28.89062,"average_solve_count":64.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.06617,"align_to_socket.lateral_x":0.01284,"align_to_socket.lateral_y":-0.00528,"contact_entry.contact_force_threshold":8.29415,"contact_entry.contact_speed":0.02051,"insert_into_hole.insert_speed":0.01048,"insert_into_hole.insertion_depth":-0.00254,"insert_into_hole.insertion_force_threshold":24.47089,"retract_from_hole.retract_speed":0.0927},"optimized_scores":{"best_composite_score":0.0927,"best_fitness_score":0.3527,"best_task_score":0.85858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":76.0,"contact_point_centroid":[0.6435,0.09115,-0.00026],"force_p95":837.03885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1598.62006,"mean_force":583.05073,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51927,-0.02722,0.19256]},{"body_a":"peg_socket","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.54433,0.00765,0.0771],"force_p95":910.87965,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1169.7942,"mean_force":217.03235,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44898,-0.00389,0.10137]},{"body_a":"peg_socket","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.59559,-0.04622,0.07975],"force_p95":490.55641,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":606.67001,"mean_force":338.14561,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51105,-0.02986,0.18579]},{"body_a":"peg_socket","body_b":"link6","contact_count":50.0,"contact_point_centroid":[0.59646,-0.00938,0.07996],"force_p95":413.41433,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":424.13199,"mean_force":352.03678,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.4948,-0.02482,0.19293]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59647,-0.01122,0.07998],"force_p95":417.46568,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.95233,"mean_force":386.08581,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48729,-0.02652,0.20807]},{"body_a":"peg_socket","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.56736,-0.00358,0.07799],"force_p95":320.66266,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.64021,"mean_force":70.30703,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.449,-0.00398,0.10459]},{"body_a":"peg_socket","body_b":"link6","contact_count":888.0,"contact_point_centroid":[0.59611,-0.01013,0.07982],"force_p95":290.79322,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.64639,"mean_force":241.95636,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46238,-0.01017,0.16794]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59645,-0.01117,0.07995],"force_p95":297.44952,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.44952,"mean_force":297.44952,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.48735,-0.0265,0.20817]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.4766,-0.00334,0.07961],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45201,-0.00324,0.08761]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54515,-0.05364,0.07852],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44832,-0.00362,0.0933]}],"total_contact_groups":10},"final_pose_error":0.073,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52256,-0.03386,0.19589],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1598.62006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5202,-0.02327,0.18557],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10998,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":276.36549,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":982.0,"raw_peak_contact_force":1169.7942,"subtask_id":"align","tcp_end":[0.48735,-0.0265,0.20817],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52021,-0.02329,0.18554],"object_pos_start":[0.5202,-0.02327,0.18557],"object_to_goal_dist_end":0.10995,"object_to_goal_dist_start":0.10998,"object_z_max":0.18557,"peak_contact_force":297.44952,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":297.44952,"subtask_id":"contact","tcp_end":[0.48735,-0.02655,0.20811],"tcp_start":[0.48735,-0.0265,0.20817],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52021,-0.02324,0.18553],"object_pos_start":[0.52021,-0.02329,0.18554],"object_to_goal_dist_end":0.10994,"object_to_goal_dist_start":0.10995,"object_z_max":0.18554,"peak_contact_force":934.93308,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":420.95233,"subtask_id":"insert","tcp_end":[0.48712,-0.02646,0.20798],"tcp_start":[0.48723,-0.0265,0.20803],"tcp_to_object_dist_end":0.04012,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":660.0,"object_pos_end":[0.55788,-0.0295,0.17762],"object_pos_start":[0.52,-0.02325,0.18543],"object_to_goal_dist_end":0.11726,"object_to_goal_dist_start":0.1098,"object_z_max":0.18543,"peak_contact_force":156.84323,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":209.0,"raw_peak_contact_force":1598.62006,"tcp_end":[0.52256,-0.03386,0.19589],"tcp_start":[0.48712,-0.02646,0.20798],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a628d07ffd5fd1634a1f36dba43ee92c313515a1a075bf67fe2ba29ce8996148`; realized-scene SHA-256: `025a988ff91962c08fa963a737fe7ec85e866c8c15bf8e1bf01c5bb6961db318`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.62963,"average_solve_count":54.0,"average_success_count":54.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.align_speed":0.09731,"align_to_socket.lateral_x":0.02,"align_to_socket.lateral_y":-0.00087,"contact_entry.contact_force_threshold":8.80426,"contact_entry.contact_speed":0.03728,"insert_into_hole.insert_speed":0.0179,"insert_into_hole.insertion_depth":-0.00363,"insert_into_hole.insertion_force_threshold":26.24553,"retract_from_hole.retract_speed":0.08835},"optimized_scores":{"best_composite_score":0.08157,"best_fitness_score":0.34157,"best_task_score":0.84988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":331.0,"contact_point_centroid":[0.52929,-1e-05,0.07998],"force_p95":107.31488,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7711.45821,"mean_force":275.96684,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46289,-9e-05,0.11692]},{"body_a":"peg_socket","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.52997,-0.00425,0.06558],"force_p95":336.00374,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5201.81242,"mean_force":370.27311,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45926,-8e-05,0.11224]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.4389,0.00982,0.07974],"force_p95":2413.08142,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2477.42581,"mean_force":1250.59503,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4368,-0.00021,0.08377]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68286,0.00034,-0.0],"force_p95":1074.54576,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1074.54576,"mean_force":1074.54576,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.4651,-0.00015,0.11948]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53024,-0.00419,0.06371],"force_p95":494.61386,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":503.95218,"mean_force":410.56892,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46521,-0.00012,0.11965]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.6831,0.00043,-3e-05],"force_p95":419.52106,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.62177,"mean_force":352.28689,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46581,-6e-05,0.12026]},{"body_a":"world","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.68177,0.00048,-0.00018],"force_p95":326.57496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.56951,"mean_force":176.37077,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46675,-3e-05,0.12398]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53027,-0.0041,0.06715],"force_p95":114.01688,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.17669,"mean_force":102.14002,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46673,-3e-05,0.12476]},{"body_a":"world","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.68284,0.00034,-1e-05],"force_p95":27.93193,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.12224,"mean_force":8.2831,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4651,-0.00012,0.1195]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53028,-3e-05,0.07997],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.4651,-0.00015,0.11948]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53027,-0.00414,0.06392],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46536,-6e-05,0.11997]}],"total_contact_groups":11},"final_pose_error":0.00343,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46686,-3e-05,0.12523],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7711.45821,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50271,-0.00011,0.10587],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02601,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":286.67838,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1018.0,"raw_peak_contact_force":7711.45821,"subtask_id":"align","tcp_end":[0.4651,-0.00015,0.11948],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50294,-2e-05,0.10628],"object_pos_start":[0.50271,-0.00011,0.10587],"object_to_goal_dist_end":0.02644,"object_to_goal_dist_start":0.02601,"object_z_max":0.10617,"peak_contact_force":317.18566,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":1074.54576,"subtask_id":"contact","tcp_end":[0.46536,-6e-05,0.11997],"tcp_start":[0.4651,-0.00015,0.11948],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50333,-0.0,0.10643],"object_pos_start":[0.50294,-2e-05,0.10628],"object_to_goal_dist_end":0.02664,"object_to_goal_dist_start":0.02644,"object_z_max":0.10673,"peak_contact_force":409.61465,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":420.62177,"subtask_id":"insert","tcp_end":[0.46655,-3e-05,0.12113],"tcp_start":[0.46609,-6e-05,0.12054],"tcp_to_object_dist_end":0.03961,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50408,1e-05,0.11058],"object_pos_start":[0.50406,1e-05,0.10723],"object_to_goal_dist_end":0.03085,"object_to_goal_dist_start":0.02753,"object_z_max":0.11047,"peak_contact_force":150.43895,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":22.0,"raw_peak_contact_force":328.56951,"tcp_end":[0.46686,-3e-05,0.12523],"tcp_start":[0.46655,-3e-05,0.12113],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```