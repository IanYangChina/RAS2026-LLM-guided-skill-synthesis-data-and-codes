## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2486 | 0.86 | ✅ accepted |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ✅ accepted |

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

## Current Skill (Q=0.249) — your mutation base

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
      tolerance: 0.1
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
    - 0.09
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
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
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: insert_depth
  type: insert
  generator: linear_cartesian
  control: admittance_control
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
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: force_monitor
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
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
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.09]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_entry** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **insert_depth** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=force_monitor, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.249
- **task_score** (E): 0.859
- **fitness_score**: 0.389  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.67 | 0.33 | 0.1508 |
| approach_socket | 0.33 | 1.00 | 0.1059 |
| contact_entry | 1.00 | 1.00 | 0.0029 |
| insert_depth | 0.00 | 1.00 | 0.0009 |
| retract_from_hole | 0.33 | 1.00 | 0.0305 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.007, 0.152) | (0.504, -0.000, 0.340)→(0.527, -0.010, 0.140) | 0.260→0.068 | 0.33 / 1.000 | 95.011 | 3297.105 |
| approach_socket | approach | 0.33 / step_budget | (0.490, -0.007, 0.152)→(0.524, -0.008, 0.251) | (0.527, -0.010, 0.140)→(0.548, -0.002, 0.223) | 0.068→0.152 | 1.00 / 1.667 | 287.495 | 1027.408 |
| contact_entry | contact | 1.00 / force_exceeded | (0.524, -0.008, 0.251)→(0.525, -0.006, 0.251) | (0.548, -0.002, 0.223)→(0.546, -0.001, 0.221) | 0.152→0.149 | 1.00 / 1.333 | 266.192 | 546.987 |
| insert_depth | insert | 0.00 / guard_failure | (0.525, -0.006, 0.251)→(0.525, -0.005, 0.251) | (0.546, -0.001, 0.221)→(0.546, -0.000, 0.222) | 0.149→0.149 | 1.00 / 1.333 | 269.773 | 269.773 |
| retract_from_hole | retract | 0.33 / step_budget | (0.525, -0.005, 0.251)→(0.525, -0.015, 0.237) | (0.546, -0.000, 0.222)→(0.551, -0.009, 0.211) | 0.149→0.142 | 1.00 / 1.000 | 434.677 | 625.629 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.143
- phase_breakdown.contact_score: 0.155
- phase_breakdown.approach_score: 0.127
- phase_breakdown.insert_score: 0.174
- phase_breakdown.align_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.432
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: align_to_socket.lateral_x
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.43956,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":-0.00506,"approach_socket.approach_speed":0.11701,"contact_entry.contact_force":4.46686,"insert_depth.insertion_depth":0.03916,"retract_from_hole.retract_speed":0.08849},"optimized_scores":{"best_composite_score":0.25131,"best_fitness_score":0.39131,"best_task_score":0.86146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.57464,-0.00561,0.07938],"force_p95":652.06203,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1062.27036,"mean_force":316.5956,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46539,-0.00491,0.13657]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.47003,-0.00207,0.07912],"force_p95":975.42162,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1013.79763,"mean_force":312.34854,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45883,-0.00208,0.09019]},{"body_a":"world","body_b":"link5","contact_count":431.0,"contact_point_centroid":[0.5556,0.11068,-0.00013],"force_p95":764.14741,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":929.16262,"mean_force":539.53129,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.54645,-0.01087,0.24207]},{"body_a":"peg_socket","body_b":"link6","contact_count":722.0,"contact_point_centroid":[0.58954,-0.00754,0.07986],"force_p95":297.45286,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":909.9473,"mean_force":250.95088,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46226,-0.0059,0.17404]},{"body_a":"peg_socket","body_b":"link5","contact_count":11.0,"contact_point_centroid":[0.5071,0.04054,0.0798],"force_p95":703.98347,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":711.81126,"mean_force":469.38847,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.52692,-0.02452,0.28115]},{"body_a":"peg_socket","body_b":"link6","contact_count":398.0,"contact_point_centroid":[0.58947,-0.00799,0.07972],"force_p95":446.83307,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":622.90498,"mean_force":292.83161,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.48118,-0.00962,0.19889]},{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.58917,-0.01236,0.07978],"force_p95":542.90294,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":604.77142,"mean_force":360.70344,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.49351,-0.00558,0.18241]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.49915,0.0416,0.07959],"force_p95":357.36205,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.36205,"mean_force":357.36205,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.53233,-0.01454,0.28376]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.49919,0.04169,0.07963],"force_p95":347.48184,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.48184,"mean_force":347.48184,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.53301,-0.0126,0.28422]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.50759,0.03999,0.07973],"force_p95":255.29601,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":255.29601,"mean_force":255.29601,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.53233,-0.01454,0.28376]},{"body_a":"peg_socket","body_b":"link6","contact_count":489.0,"contact_point_centroid":[0.58953,0.04292,0.07994],"force_p95":239.62136,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":246.83061,"mean_force":200.57182,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53743,-0.00776,0.26141]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.50768,0.04014,0.07975],"force_p95":246.76082,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":246.76082,"mean_force":246.76082,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.53301,-0.0126,0.28422]},{"body_a":"peg_socket","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.49922,0.04197,0.07967],"force_p95":186.37226,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.78792,"mean_force":82.4825,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.52804,-0.02312,0.28163]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.54687,0.01335,0.07889],"force_p95":59.29936,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.37803,"mean_force":12.03009,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45036,-0.00248,0.0987]},{"body_a":"peg_socket","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.49943,0.04234,0.07983],"force_p95":0.0,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53463,-0.00761,0.28521]},{"body_a":"peg_socket","body_b":"link5","contact_count":7.0,"contact_point_centroid":[0.50853,0.04158,0.07987],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53557,-0.00502,0.28548]}],"total_contact_groups":16},"final_pose_error":0.11838,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.55548,-0.00787,0.24016],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1062.27036,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.52791,-0.0034,0.16337],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08798,"object_to_goal_dist_start":0.26034,"object_z_max":0.34463,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":810.0,"raw_peak_contact_force":1062.27036,"tcp_end":[0.49284,0.00033,0.18224],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.55009,-0.00356,0.24965],"object_pos_start":[0.52791,-0.0034,0.16337],"object_to_goal_dist_end":0.17693,"object_to_goal_dist_start":0.08798,"object_z_max":0.24935,"peak_contact_force":208.58219,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":457.0,"raw_peak_contact_force":711.81126,"tcp_end":[0.53233,-0.01454,0.28376],"tcp_start":[0.49284,0.00033,0.18224],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55064,-0.00166,0.25003],"object_pos_start":[0.55009,-0.00356,0.24965],"object_to_goal_dist_end":0.17741,"object_to_goal_dist_start":0.17693,"object_z_max":0.24965,"peak_contact_force":357.36205,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":357.36205,"tcp_end":[0.53301,-0.0126,0.28422],"tcp_start":[0.53233,-0.01454,0.28376],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55114,0.00035,0.25048],"object_pos_start":[0.55064,-0.00166,0.25003],"object_to_goal_dist_end":0.17798,"object_to_goal_dist_start":0.17741,"object_z_max":0.25003,"peak_contact_force":347.48184,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":347.48184,"tcp_end":[0.53366,-0.01055,0.28476],"tcp_start":[0.53301,-0.0126,0.28422],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57867,0.0045,0.21],"object_pos_start":[0.55114,0.00035,0.25048],"object_to_goal_dist_end":0.15201,"object_to_goal_dist_start":0.17798,"object_z_max":0.25153,"peak_contact_force":466.80359,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":931.0,"raw_peak_contact_force":929.16262,"tcp_end":[0.55548,-0.00787,0.24016],"tcp_start":[0.53366,-0.01055,0.28476],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.05263,"average_mean_iterations":16.63158,"average_solve_count":95.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.0133,"approach_socket.approach_speed":0.10173,"contact_entry.contact_force":6.44022,"insert_depth.insertion_depth":0.0486,"retract_from_hole.retract_speed":0.11016},"optimized_scores":{"best_composite_score":0.29229,"best_fitness_score":0.43229,"best_task_score":0.86574},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":67.0,"contact_point_centroid":[0.58786,-0.08272,0.07941],"force_p95":895.68427,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1298.09179,"mean_force":331.82932,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.5208,-0.05031,0.16352]},{"body_a":"peg_socket","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.54288,-0.08304,0.07638],"force_p95":904.1714,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1134.36634,"mean_force":482.62217,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.48892,-0.09013,0.17987]},{"body_a":"peg_socket","body_b":"link5","contact_count":52.0,"contact_point_centroid":[0.58958,0.00649,0.07919],"force_p95":851.25337,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1077.1883,"mean_force":376.3981,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.45807,-0.10758,0.23447]},{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.54704,0.00723,0.07775],"force_p95":817.56092,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1045.80796,"mean_force":210.59902,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45139,-0.00318,0.10252]},{"body_a":"world","body_b":"link6","contact_count":37.0,"contact_point_centroid":[0.64881,-0.16142,-0.00283],"force_p95":951.30654,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":976.94523,"mean_force":387.14333,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46951,-0.10005,0.16552]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47657,-0.00266,0.07977],"force_p95":841.35068,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":844.1379,"mean_force":417.42358,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46049,-0.00262,0.08975]},{"body_a":"peg_socket","body_b":"link5","contact_count":577.0,"contact_point_centroid":[0.51988,0.00664,0.07993],"force_p95":682.0608,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":746.28742,"mean_force":647.94943,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.55769,-0.02931,0.34856]},{"body_a":"peg_socket","body_b":"link5","contact_count":308.0,"contact_point_centroid":[0.50424,-0.00272,0.0799],"force_p95":662.84017,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":740.29379,"mean_force":535.12556,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.56633,-0.01598,0.34501]},{"body_a":"peg_socket","body_b":"link6","contact_count":148.0,"contact_point_centroid":[0.59572,0.02223,0.07985],"force_p95":623.19597,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":671.08373,"mean_force":383.60143,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.57272,-0.0071,0.34531]},{"body_a":"peg_socket","body_b":"link6","contact_count":642.0,"contact_point_centroid":[0.59617,-0.00866,0.07981],"force_p95":318.35656,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":659.06817,"mean_force":254.18904,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46606,-0.00689,0.16685]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50243,-0.08337,0.07999],"force_p95":597.68078,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":599.56777,"mean_force":585.85397,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.44089,-0.09319,0.16503]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.59637,-0.08313,0.07984],"force_p95":456.5633,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.16891,"mean_force":382.26355,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.44589,-0.11578,0.21759]},{"body_a":"peg_socket","body_b":"link5","contact_count":124.0,"contact_point_centroid":[0.55594,0.03584,0.07991],"force_p95":336.02735,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":380.5301,"mean_force":271.83484,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.55247,-0.03777,0.33839]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.56674,-0.00334,0.07856],"force_p95":229.71754,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.9662,"mean_force":60.25915,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45124,-0.00321,0.10419]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.55525,0.03328,0.07998],"force_p95":231.78978,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.78978,"mean_force":231.78978,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.57373,-0.00898,0.34967]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59643,0.02294,0.07988],"force_p95":113.65896,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.65896,"mean_force":113.65896,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.57627,-0.00465,0.34647]}],"total_contact_groups":18},"final_pose_error":0.22576,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.55236,-0.03781,0.34974],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1298.09179,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.55132,-0.02557,0.14931],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08995,"object_to_goal_dist_start":0.26034,"object_z_max":0.34478,"peak_contact_force":0.0,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":714.0,"raw_peak_contact_force":1045.80796,"tcp_end":[0.51174,-0.02115,0.15299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.59075,-0.00222,0.3141],"object_pos_start":[0.55132,-0.02557,0.14931],"object_to_goal_dist_end":0.25109,"object_to_goal_dist_start":0.08995,"object_z_max":0.31408,"peak_contact_force":336.03885,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":347.0,"raw_peak_contact_force":1298.09179,"tcp_end":[0.57373,-0.00898,0.34967],"tcp_start":[0.51174,-0.02115,0.15299],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":42.0,"n_steps_budget":1000.0,"object_pos_end":[0.58404,-0.00142,0.30737],"object_pos_start":[0.59075,-0.00222,0.3141],"object_to_goal_dist_end":0.2424,"object_to_goal_dist_start":0.25109,"object_z_max":0.31607,"peak_contact_force":231.78978,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":231.78978,"tcp_end":[0.57627,-0.00465,0.34647],"tcp_start":[0.57373,-0.00898,0.34967],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58393,-0.00149,0.30718],"object_pos_start":[0.58404,-0.00142,0.30737],"object_to_goal_dist_end":0.2422,"object_to_goal_dist_start":0.2424,"object_z_max":0.30737,"peak_contact_force":113.65896,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":113.65896,"tcp_end":[0.57633,-0.00466,0.34633],"tcp_start":[0.57627,-0.00465,0.34647],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56927,-0.03321,0.31378],"object_pos_start":[0.58393,-0.00149,0.30718],"object_to_goal_dist_end":0.24608,"object_to_goal_dist_start":0.2422,"object_z_max":0.31378,"peak_contact_force":676.80878,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1033.0,"raw_peak_contact_force":746.28742,"tcp_end":[0.55236,-0.03781,0.34974],"tcp_start":[0.57633,-0.00466,0.34633],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.35897,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.02,"approach_socket.approach_speed":0.10715,"contact_entry.contact_force":8.74495,"insert_depth.insertion_depth":0.04678,"retract_from_hole.retract_speed":0.08438},"optimized_scores":{"best_composite_score":0.20215,"best_fitness_score":0.34215,"best_task_score":0.85067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":516.0,"contact_point_centroid":[0.52964,0.00018,0.07998],"force_p95":102.59173,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7783.23543,"mean_force":211.49303,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46373,0.00013,0.11788]},{"body_a":"peg_socket","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.53002,-0.00405,0.0651],"force_p95":336.13105,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5200.44416,"mean_force":351.17734,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46067,0.00011,0.11397]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43903,0.01027,0.07977],"force_p95":2479.59128,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2541.95674,"mean_force":1284.39441,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.43707,-8e-05,0.08378]},{"body_a":"world","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.68264,0.00059,-0.0001],"force_p95":358.13644,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1072.32078,"mean_force":132.85466,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46545,0.00021,0.12033]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.68267,0.00062,-4e-05],"force_p95":967.57114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1051.80975,"mean_force":475.03502,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46561,0.00027,0.12066]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53025,-0.00392,0.0641],"force_p95":342.72629,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":502.17004,"mean_force":285.41961,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46544,0.0002,0.12029]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00389,0.0642],"force_p95":491.52196,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.52196,"mean_force":491.52196,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46545,0.00027,0.12045]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68264,0.00062,-3e-05],"force_p95":348.17835,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.17835,"mean_force":348.17835,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.46575,0.00027,0.12099]},{"body_a":"world","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.68254,0.00061,-8e-05],"force_p95":178.73683,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.43664,"mean_force":125.74294,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46599,0.00026,0.12151]},{"body_a":"world","body_b":"link6","contact_count":232.0,"contact_point_centroid":[0.68286,0.00052,-0.0],"force_p95":9.96286,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.84063,"mean_force":2.81084,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4651,0.00013,0.11948]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53028,0.00017,0.07997],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.4651,0.00012,0.11947]}],"total_contact_groups":11},"final_pose_error":0.00515,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46622,0.00023,0.12186],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7783.23543,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50271,0.00015,0.10586],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.026,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":285.03194,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1573.0,"raw_peak_contact_force":7783.23543,"tcp_end":[0.4651,0.00012,0.11947],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50299,0.00028,0.10664],"object_pos_start":[0.50271,0.00015,0.10586],"object_to_goal_dist_end":0.02681,"object_to_goal_dist_start":0.026,"object_z_max":0.10665,"peak_contact_force":317.86456,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37.0,"raw_peak_contact_force":1072.32078,"tcp_end":[0.46545,0.00027,0.12045],"tcp_start":[0.4651,0.00012,0.11947],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.50326,0.00029,0.10711],"object_pos_start":[0.50299,0.00028,0.10664],"object_to_goal_dist_end":0.0273,"object_to_goal_dist_start":0.02681,"object_z_max":0.10704,"peak_contact_force":209.42365,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":1051.80975,"tcp_end":[0.46575,0.00027,0.12099],"tcp_start":[0.46545,0.00027,0.12045],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50338,0.0003,0.10735],"object_pos_start":[0.50326,0.00029,0.10711],"object_to_goal_dist_end":0.02756,"object_to_goal_dist_start":0.0273,"object_z_max":0.10711,"peak_contact_force":348.17835,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":348.17835,"tcp_end":[0.46589,0.00028,0.12128],"tcp_start":[0.46575,0.00027,0.12099],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50367,0.00025,0.1078],"object_pos_start":[0.50338,0.0003,0.10735],"object_to_goal_dist_end":0.02804,"object_to_goal_dist_start":0.02756,"object_z_max":0.10772,"peak_contact_force":160.4189,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":17.0,"raw_peak_contact_force":201.43664,"tcp_end":[0.46622,0.00023,0.12186],"tcp_start":[0.46589,0.00028,0.12128],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```