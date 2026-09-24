## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | align → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2656 | 0.86 | ❌ rejected |
| 7 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0485 | 0.86 | ✅ accepted |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1883 | 0.86 | ❌ rejected |
| 5 | align → approach → descend → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1036 | 0.86 | ✅ accepted |
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2486 | 0.86 | ✅ accepted |

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

## Current Skill (Q=0.266) — your mutation base

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
      tolerance: 0.1
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
      tolerance: 0.1
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
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
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.266
- **task_score** (E): 0.861
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.33 | 1.00 | 0.1075 |
| contact_entry | 1.00 | 1.00 | 0.0031 |
| insert_into_hole | 0.00 | 0.67 | 0.0003 |
| retract_from_hole | 0.33 | 1.00 | 0.0429 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.532, -0.007, 0.245) | (0.504, -0.000, 0.340)→(0.554, -0.015, 0.217) | 0.260→0.149 | 1.00 / 1.333 | 304.996 | 3192.788 |
| contact_entry | contact | 1.00 / force_exceeded | (0.532, -0.007, 0.245)→(0.534, -0.009, 0.245) | (0.554, -0.015, 0.217)→(0.556, -0.017, 0.217) | 0.149→0.150 | 1.00 / 1.333 | 76.117 | 76.117 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.535, -0.011, 0.246)→(0.535, -0.011, 0.246) | (0.556, -0.017, 0.217)→(0.557, -0.018, 0.217) | 0.150→0.150 | 0.67 / 1.000 | 52.399 | 88.205 |
| retract_from_hole | retract | 0.33 / step_budget | (0.535, -0.011, 0.246)→(0.529, -0.021, 0.205) | (0.557, -0.018, 0.217)→(0.555, -0.029, 0.179) | 0.151→0.118 | 1.00 / 1.000 | 216.634 | 398.901 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.090
- phase_breakdown.contact_score: 0.111
- phase_breakdown.approach_score: 0.000
- phase_breakdown.insert_score: 0.127
- phase_breakdown.align_score: 0.039

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.400
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: 0.275
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.41558,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.01776,"align_to_socket.lateral_y":-0.00752,"contact_entry.contact_force_threshold":7.06969,"insert_into_hole.insert_depth":0.02681,"insert_into_hole.insert_speed":0.02086,"retract_from_hole.retract_speed":0.09001},"optimized_scores":{"best_composite_score":0.2903,"best_fitness_score":0.4003,"best_task_score":0.86645},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.47044,-0.00291,0.07907],"force_p95":1056.01803,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.01228,"mean_force":310.2557,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4602,-0.0029,0.09055]},{"body_a":"peg_socket","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.57544,-0.00744,0.07926],"force_p95":609.49166,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":879.74566,"mean_force":268.06596,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46519,-0.00838,0.13542]},{"body_a":"peg_socket","body_b":"link6","contact_count":720.0,"contact_point_centroid":[0.58953,-0.01398,0.07982],"force_p95":382.05156,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":814.62272,"mean_force":266.51951,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46948,-0.0009,0.1846]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.55133,0.01332,0.07897],"force_p95":33.79318,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.9318,"mean_force":17.78588,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45459,-0.00325,0.09727]},{"body_a":"peg_socket","body_b":"link6","contact_count":936.0,"contact_point_centroid":[0.58959,-0.07701,0.07994],"force_p95":260.66285,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.94964,"mean_force":231.69939,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.56636,-0.01392,0.29856]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58956,-0.07704,0.07987],"force_p95":91.93868,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.93868,"mean_force":91.93868,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.57145,8e-05,0.31849]},{"body_a":"peg_socket","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.58959,-0.07704,0.07993],"force_p95":53.63673,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.6925,"mean_force":22.64954,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.57279,-0.00265,0.31956]}],"total_contact_groups":7},"final_pose_error":0.14664,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.56073,-0.02183,0.26822],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1088.01228,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.58394,-0.01138,0.28226],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21928,"object_to_goal_dist_start":0.26034,"object_z_max":0.34478,"peak_contact_force":389.0898,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":814.0,"raw_peak_contact_force":1088.01228,"tcp_end":[0.57145,8e-05,0.31849],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.58442,-0.0124,0.28265],"object_pos_start":[0.58394,-0.01138,0.28226],"object_to_goal_dist_end":0.21988,"object_to_goal_dist_start":0.21928,"object_z_max":0.28226,"peak_contact_force":91.93868,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":91.93868,"tcp_end":[0.57196,-0.0011,0.31894],"tcp_start":[0.57145,8e-05,0.31849],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":6.0,"n_steps_budget":810.0,"object_pos_end":[0.58649,-0.01585,0.284],"object_pos_start":[0.58442,-0.0124,0.28265],"object_to_goal_dist_end":0.22215,"object_to_goal_dist_start":0.21988,"object_z_max":0.28426,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":57.6925,"tcp_end":[0.57543,-0.00644,0.32105],"tcp_start":[0.57485,-0.00572,0.32078],"tcp_to_object_dist_end":0.03979,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57889,-0.03377,0.23463],"object_pos_start":[0.58757,-0.01721,0.28449],"object_to_goal_dist_end":0.17685,"object_to_goal_dist_start":0.22312,"object_z_max":0.28511,"peak_contact_force":243.5795,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":936.0,"raw_peak_contact_force":295.94964,"tcp_end":[0.56073,-0.02183,0.26822],"tcp_start":[0.57543,-0.00644,0.32105],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.58667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.00562,"align_to_socket.lateral_y":8e-05,"contact_entry.contact_force_threshold":6.29342,"insert_into_hole.insert_depth":0.03003,"insert_into_hole.insert_speed":0.03157,"retract_from_hole.retract_speed":0.10224},"optimized_scores":{"best_composite_score":0.27478,"best_fitness_score":0.38478,"best_task_score":0.86509},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.5462,0.00729,0.07772],"force_p95":820.09258,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":958.43327,"mean_force":209.34214,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4506,-0.00329,0.10251]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47657,-0.00272,0.07974],"force_p95":847.39404,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.15851,"mean_force":420.4718,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45978,-0.00269,0.08945]},{"body_a":"peg_socket","body_b":"link6","contact_count":777.0,"contact_point_centroid":[0.59617,-0.01541,0.0798],"force_p95":352.93607,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":720.71061,"mean_force":257.38613,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.47129,-0.00591,0.17766]},{"body_a":"world","body_b":"link6","contact_count":47.0,"contact_point_centroid":[0.67009,-0.11876,-9e-05],"force_p95":432.31184,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.61157,"mean_force":315.8128,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.56366,-0.03927,0.22831]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.56673,-0.00337,0.07859],"force_p95":236.72238,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.07404,"mean_force":63.89158,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45069,-0.00331,0.1037]},{"body_a":"peg_socket","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.59644,-0.08334,0.07996],"force_p95":247.25147,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.34525,"mean_force":223.40651,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.56171,-0.03328,0.2617]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59643,-0.08332,0.07993],"force_p95":120.07058,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.01852,"mean_force":96.61659,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.56532,-0.02847,0.29734]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59647,-0.08337,0.07998],"force_p95":59.92037,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.3245,"mean_force":56.28322,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.56275,-0.02556,0.29739]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54657,-0.05347,0.0795],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44956,-0.00312,0.09477]}],"total_contact_groups":9},"final_pose_error":0.10686,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.56038,-0.04214,0.22745],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":958.43327,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.57585,-0.03408,0.26227],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20034,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":238.67244,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":851.0,"raw_peak_contact_force":958.43327,"tcp_end":[0.56,-0.02254,0.29713],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":22.0,"n_steps_budget":930.0,"object_pos_end":[0.58052,-0.03963,0.26215],"object_pos_start":[0.57585,-0.03408,0.26227],"object_to_goal_dist_end":0.20305,"object_to_goal_dist_start":0.20034,"object_z_max":0.26359,"peak_contact_force":60.3245,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":60.3245,"tcp_end":[0.56537,-0.02849,0.29745],"tcp_start":[0.56,-0.02254,0.29713],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":630.0,"object_pos_end":[0.58046,-0.03959,0.26202],"object_pos_start":[0.58052,-0.03963,0.26215],"object_to_goal_dist_end":0.20291,"object_to_goal_dist_start":0.20305,"object_z_max":0.26215,"peak_contact_force":73.29216,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":123.01852,"tcp_end":[0.56531,-0.02849,0.29717],"tcp_start":[0.56529,-0.02845,0.29723],"tcp_to_object_dist_end":0.03986,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.58173,-0.05442,0.19593],"object_pos_start":[0.58045,-0.03964,0.26187],"object_to_goal_dist_end":0.15193,"object_to_goal_dist_start":0.20278,"object_z_max":0.26187,"peak_contact_force":298.07979,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":933.0,"raw_peak_contact_force":575.61157,"tcp_end":[0.56038,-0.04214,0.22745],"tcp_start":[0.56531,-0.02849,0.29717],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.29825,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.01939,"align_to_socket.lateral_y":0.00457,"contact_entry.contact_force_threshold":5.77288,"insert_into_hole.insert_depth":0.02783,"insert_into_hole.insert_speed":0.03284,"retract_from_hole.retract_speed":0.10752},"optimized_scores":{"best_composite_score":0.23181,"best_fitness_score":0.34181,"best_task_score":0.85059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":515.0,"contact_point_centroid":[0.52964,0.00111,0.07998],"force_p95":104.62288,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7531.91887,"mean_force":209.51543,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46371,0.00115,0.11786]},{"body_a":"peg_socket","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.53002,-0.00322,0.06511],"force_p95":334.91475,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5135.52156,"mean_force":350.26341,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46065,0.00097,0.11394]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43901,0.01187,0.07977],"force_p95":2534.09848,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2546.09222,"mean_force":1211.76742,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.43702,0.00046,0.0838]},{"body_a":"world","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.68295,0.00096,-1e-05],"force_p95":319.27394,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.14302,"mean_force":204.62158,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46523,0.00162,0.11952]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53022,-0.0029,0.06358],"force_p95":175.3413,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":179.52314,"mean_force":106.88669,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46513,0.00165,0.11945]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.53027,0.00141,0.07996],"force_p95":89.30559,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.29258,"mean_force":33.04483,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.4651,0.00166,0.11943]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53027,0.0014,0.07996],"force_p95":83.59787,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.90365,"mean_force":80.95442,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46508,0.00167,0.11943]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53028,0.0014,0.07997],"force_p95":76.08687,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.08687,"mean_force":76.08687,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46508,0.00166,0.11943]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5302,-0.00289,0.06358],"force_p95":68.4384,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.59051,"mean_force":66.67861,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46508,0.00167,0.11943]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53021,-0.0029,0.06359],"force_p95":54.05982,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.05982,"mean_force":54.05982,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46508,0.00166,0.11943]},{"body_a":"world","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.68284,0.00117,-1e-05],"force_p95":28.13361,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.25764,"mean_force":9.02979,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4651,0.00123,0.1195]}],"total_contact_groups":11},"final_pose_error":0.00724,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46552,0.0015,0.11977],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7531.91887,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.5027,0.00152,0.10585],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02603,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":287.22662,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1386.0,"raw_peak_contact_force":7531.91887,"tcp_end":[0.46508,0.00166,0.11943],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.5027,0.00152,0.10584],"object_pos_start":[0.5027,0.00152,0.10585],"object_to_goal_dist_end":0.02603,"object_to_goal_dist_start":0.02603,"object_z_max":0.10585,"peak_contact_force":76.08687,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":76.08687,"tcp_end":[0.46508,0.00166,0.11943],"tcp_start":[0.46508,0.00166,0.11943],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.5027,0.00153,0.10583],"object_pos_start":[0.5027,0.00152,0.10584],"object_to_goal_dist_end":0.02602,"object_to_goal_dist_start":0.02603,"object_z_max":0.10584,"peak_contact_force":83.90365,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":83.90365,"tcp_end":[0.46508,0.00167,0.11942],"tcp_start":[0.46508,0.00167,0.11942],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50311,0.00137,0.1061],"object_pos_start":[0.50269,0.00153,0.10583],"object_to_goal_dist_end":0.02633,"object_to_goal_dist_start":0.02601,"object_z_max":0.10606,"peak_contact_force":108.24416,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":41.0,"raw_peak_contact_force":325.14302,"tcp_end":[0.46552,0.0015,0.11977],"tcp_start":[0.46508,0.00167,0.11942],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```