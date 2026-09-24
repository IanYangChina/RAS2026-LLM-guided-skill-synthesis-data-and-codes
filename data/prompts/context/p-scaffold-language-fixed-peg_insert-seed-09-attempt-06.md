## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1883 | 0.86 | ❌ rejected |
| 5 | align → approach → descend → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1036 | 0.86 | ✅ accepted |
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2486 | 0.86 | ✅ accepted |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.188) — your mutation base

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
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.arc_height
        mode: replace
- id: descend_to_entry
  type: descend
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
    descend_offset:
      type: scalar
      range:
      - 0.06
      - 0.1
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: continue
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
    - 0.07
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
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
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
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.09]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=40.0
- **contact_entry** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **insert_depth** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.188
- **task_score** (E): 0.860
- **fitness_score**: 0.378  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.33 | 1.00 | 0.1217 |
| approach_socket | 0.33 | 1.00 | 0.0500 |
| contact_entry | 1.00 | 1.00 | 0.0010 |
| insert_depth | 0.00 | 0.67 | 0.0005 |
| retract_from_hole | 0.33 | 0.67 | 0.0313 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.004, 0.201) | (0.504, -0.000, 0.340)→(0.535, -0.002, 0.179) | 0.260→0.105 | 1.00 / 1.667 | 284.733 | 3297.947 |
| approach_socket | approach | 0.33 / step_budget | (0.506, 0.004, 0.201)→(0.522, -0.012, 0.239) | (0.535, -0.002, 0.179)→(0.546, -0.012, 0.211) | 0.105→0.141 | 1.00 / 1.667 | 332.115 | 1558.205 |
| contact_entry | contact | 1.00 / force_exceeded | (0.522, -0.012, 0.239)→(0.522, -0.013, 0.240) | (0.546, -0.012, 0.211)→(0.546, -0.012, 0.212) | 0.141→0.141 | 1.00 / 1.333 | 507.067 | 774.635 |
| insert_depth | insert | 0.00 / guard_failure | (0.522, -0.013, 0.240)→(0.522, -0.013, 0.241) | (0.546, -0.012, 0.212)→(0.546, -0.012, 0.212) | 0.141→0.142 | 0.67 / 1.000 | 425.217 | 546.243 |
| retract_from_hole | retract | 0.33 / step_budget | (0.522, -0.013, 0.241)→(0.527, -0.014, 0.223) | (0.546, -0.012, 0.212)→(0.555, -0.014, 0.198) | 0.142→0.132 | 0.67 / 0.667 | 212.693 | 646.413 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.865
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.865
- phase_score: 0.110
- phase_breakdown.contact_score: 0.116
- phase_breakdown.approach_score: 0.085
- phase_breakdown.insert_score: 0.133
- phase_breakdown.align_score: 0.032

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.412
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.865
- **Median Q (composite search score)**: 0.191
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.249


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.02597,"average_mean_iterations":11.75325,"average_solve_count":77.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.00568,"align_to_socket.lateral_y":0.00936,"approach_socket.approach_speed":0.10922,"contact_entry.contact_force":4.6153,"insert_depth.insertion_depth":0.04041,"retract_from_hole.retract_speed":0.12156},"optimized_scores":{"best_composite_score":0.19089,"best_fitness_score":0.38089,"best_task_score":0.86503},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":139.0,"contact_point_centroid":[0.51204,0.04227,0.07357],"force_p95":1197.01241,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3086.15291,"mean_force":494.50682,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.52689,-0.00658,0.26659]},{"body_a":"peg_socket","body_b":"link6","contact_count":436.0,"contact_point_centroid":[0.58939,0.00409,0.07973],"force_p95":587.28126,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3078.43595,"mean_force":333.69909,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.49679,-0.02387,0.22095]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.47033,-0.001,0.07911],"force_p95":973.62555,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1012.79249,"mean_force":432.48805,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46003,-0.001,0.09049]},{"body_a":"world","body_b":"link5","contact_count":409.0,"contact_point_centroid":[0.56473,0.10617,-0.00013],"force_p95":845.14473,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1009.35483,"mean_force":568.24527,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53922,-0.00503,0.24686]},{"body_a":"peg_socket","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.57585,-0.00392,0.0794],"force_p95":521.24797,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":989.00024,"mean_force":276.95584,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46702,-0.00232,0.14091]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51185,0.0428,0.07372],"force_p95":928.36249,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":928.36249,"mean_force":928.36249,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.52633,-0.00151,0.26744]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51186,0.04279,0.07369],"force_p95":921.38777,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":921.38777,"mean_force":921.38777,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.52633,-0.00163,0.26741]},{"body_a":"peg_socket","body_b":"link6","contact_count":664.0,"contact_point_centroid":[0.58953,-0.00514,0.07986],"force_p95":303.9,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":843.65164,"mean_force":249.06285,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46359,-0.00272,0.17639]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58959,0.04294,0.07998],"force_p95":671.68413,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":671.68413,"mean_force":671.68413,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.52633,-0.00151,0.26744]},{"body_a":"peg_socket","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.55588,-0.07633,0.07937],"force_p95":665.37577,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":666.94056,"mean_force":497.8988,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.49074,-0.0472,0.20013]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58958,0.04294,0.07998],"force_p95":664.82384,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":664.82384,"mean_force":664.82384,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.52633,-0.00163,0.26741]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.5461,0.01339,0.07878],"force_p95":235.86121,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":468.16349,"mean_force":53.80029,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44979,-0.00146,0.09999]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.58956,-0.01327,0.0799],"force_p95":417.25145,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.0398,"mean_force":357.15631,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.4931,-0.00265,0.18159]},{"body_a":"peg_socket","body_b":"link6","contact_count":139.0,"contact_point_centroid":[0.58958,0.04294,0.07998],"force_p95":238.10237,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.94066,"mean_force":185.76079,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.52836,-0.0024,0.2585]},{"body_a":"peg_socket","body_b":"link5","contact_count":8.0,"contact_point_centroid":[0.51726,0.04291,0.06505],"force_p95":181.97903,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.53296,"mean_force":80.56192,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.52836,-0.00262,0.25879]},{"body_a":"peg_socket","body_b":"link5","contact_count":11.0,"contact_point_centroid":[0.52454,0.04257,0.04983],"force_p95":12.34313,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.68627,"mean_force":2.24421,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.52849,-0.02238,0.26269]}],"total_contact_groups":17},"final_pose_error":0.10288,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.55206,-0.00469,0.24464],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":3086.15291,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":843.0,"n_steps_budget":990.0,"object_pos_end":[0.52841,-0.00296,0.16236],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08717,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":337.16264,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":752.0,"raw_peak_contact_force":1012.79249,"tcp_end":[0.49329,-0.00015,0.18131],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.54681,0.00631,0.23398],"object_pos_start":[0.52841,-0.00296,0.16236],"object_to_goal_dist_end":0.16106,"object_to_goal_dist_start":0.08717,"object_z_max":0.23412,"peak_contact_force":353.52311,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":629.0,"raw_peak_contact_force":3086.15291,"tcp_end":[0.52633,-0.00163,0.26741],"tcp_start":[0.49329,-0.00015,0.18131],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54681,0.00641,0.234],"object_pos_start":[0.54681,0.00631,0.23398],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16106,"object_z_max":0.23398,"peak_contact_force":921.38777,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":921.38777,"tcp_end":[0.52633,-0.00151,0.26744],"tcp_start":[0.52633,-0.00163,0.26741],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5468,0.00659,0.23405],"object_pos_start":[0.54681,0.00641,0.234],"object_to_goal_dist_end":0.16114,"object_to_goal_dist_start":0.16109,"object_z_max":0.234,"peak_contact_force":928.36249,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":928.36249,"tcp_end":[0.52632,-0.0013,0.26749],"tcp_start":[0.52633,-0.00151,0.26744],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":590.0,"n_steps_budget":660.0,"object_pos_end":[0.57774,0.00481,0.21548],"object_pos_start":[0.5468,0.00659,0.23405],"object_to_goal_dist_end":0.15627,"object_to_goal_dist_start":0.16114,"object_z_max":0.23411,"peak_contact_force":396.11446,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":556.0,"raw_peak_contact_force":1009.35483,"tcp_end":[0.55206,-0.00469,0.24464],"tcp_start":[0.52632,-0.0013,0.26749],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.26364,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.00433,"align_to_socket.lateral_y":-0.0006,"approach_socket.approach_speed":0.10549,"contact_entry.contact_force":6.89309,"insert_depth.insertion_depth":0.04509,"retract_from_hole.retract_speed":0.09272},"optimized_scores":{"best_composite_score":0.22176,"best_fitness_score":0.41176,"best_task_score":0.86471},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.54601,0.0073,0.07771],"force_p95":819.79694,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1051.34312,"mean_force":206.98453,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4504,-0.00336,0.10245]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47657,-0.0028,0.07976],"force_p95":847.35759,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.05078,"mean_force":420.53674,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45959,-0.00277,0.08942]},{"body_a":"peg_socket","body_b":"link6","contact_count":772.0,"contact_point_centroid":[0.59615,-0.01385,0.07979],"force_p95":369.20837,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":635.61746,"mean_force":260.80176,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46933,-0.00372,0.17665]},{"body_a":"peg_socket","body_b":"link6","contact_count":958.0,"contact_point_centroid":[0.59646,-0.07237,0.07993],"force_p95":365.15699,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":512.46963,"mean_force":265.68732,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.57579,-0.03356,0.33754]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59646,-0.08338,0.07995],"force_p95":394.47933,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.79482,"mean_force":328.63993,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.57377,-0.03606,0.331]},{"body_a":"peg_socket","body_b":"link6","contact_count":937.0,"contact_point_centroid":[0.59645,-0.08335,0.07993],"force_p95":314.8762,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":381.23261,"mean_force":268.24867,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.56561,-0.03754,0.31422]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59647,-0.08338,0.07997],"force_p95":363.07751,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.07751,"mean_force":363.07751,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.574,-0.03689,0.33225]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.56674,-0.00337,0.07854],"force_p95":236.4062,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":273.17584,"mean_force":59.52431,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45024,-0.0034,0.10413]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54637,-0.05347,0.07948],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.44937,-0.00319,0.09474]}],"total_contact_groups":9},"final_pose_error":0.14775,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.56325,-0.03753,0.28961],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1051.34312,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.57489,-0.00242,0.26874],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20307,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":231.84008,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":845.0,"raw_peak_contact_force":1051.34312,"tcp_end":[0.56008,0.01222,0.30289],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58705,-0.04128,0.29306],"object_pos_start":[0.57489,-0.00242,0.26874],"object_to_goal_dist_end":0.23383,"object_to_goal_dist_start":0.20307,"object_z_max":0.30191,"peak_contact_force":342.25773,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":512.46963,"tcp_end":[0.57363,-0.03554,0.3303],"tcp_start":[0.56008,0.01222,0.30289],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.58698,-0.04229,0.29481],"object_pos_start":[0.58705,-0.04128,0.29306],"object_to_goal_dist_end":0.23558,"object_to_goal_dist_start":0.23383,"object_z_max":0.29431,"peak_contact_force":401.79482,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":401.79482,"tcp_end":[0.574,-0.03689,0.33225],"tcp_start":[0.57363,-0.03554,0.3303],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.587,-0.04257,0.29546],"object_pos_start":[0.58698,-0.04229,0.29481],"object_to_goal_dist_end":0.23622,"object_to_goal_dist_start":0.23558,"object_z_max":0.29481,"peak_contact_force":0.0,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":363.07751,"tcp_end":[0.57414,-0.03726,0.33296],"tcp_start":[0.574,-0.03689,0.33225],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5832,-0.04524,0.25581],"object_pos_start":[0.587,-0.04257,0.29546],"object_to_goal_dist_end":0.1997,"object_to_goal_dist_start":0.23622,"object_z_max":0.29624,"peak_contact_force":241.96429,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":937.0,"raw_peak_contact_force":381.23261,"tcp_end":[0.56325,-0.03753,0.28961],"tcp_start":[0.57414,-0.03726,0.33296],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.5974,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.01948,"align_to_socket.lateral_y":-0.00078,"approach_socket.approach_speed":0.0553,"contact_entry.contact_force":5.32212,"insert_depth.insertion_depth":0.04826,"retract_from_hole.retract_speed":0.09737},"optimized_scores":{"best_composite_score":0.15213,"best_fitness_score":0.34213,"best_task_score":0.85063},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":514.0,"contact_point_centroid":[0.52964,2e-05,0.07998],"force_p95":103.76845,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7829.70541,"mean_force":212.79879,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46373,-6e-05,0.11788]},{"body_a":"peg_socket","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.53002,-0.00419,0.0651],"force_p95":335.93962,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5232.04073,"mean_force":351.43253,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46065,-4e-05,0.11395]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43901,0.00991,0.07977],"force_p95":2493.0798,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2555.83305,"mean_force":1290.23504,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.43704,-0.00018,0.08377]},{"body_a":"world","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.68263,0.00061,-0.0001],"force_p95":360.83033,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1075.99319,"mean_force":149.15437,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46544,0.00015,0.12032]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.68264,0.00065,-4e-05],"force_p95":960.58839,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1000.72371,"mean_force":599.37052,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46552,0.00034,0.12057]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.68249,0.00064,-1e-05],"force_p95":527.87662,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.65293,"mean_force":340.88983,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46578,0.00033,0.12135]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53025,-0.00397,0.06408],"force_p95":341.68513,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.68895,"mean_force":281.00121,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.46543,0.00012,0.12028]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53023,-0.00385,0.06419],"force_p95":456.88826,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.88826,"mean_force":456.88826,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.46542,0.00034,0.1204]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68262,0.00064,-2e-05],"force_p95":347.28957,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.28957,"mean_force":347.28957,"phase_index":3.0,"phase_name":"insert_depth","phase_type":"insert","tcp_position_centroid":[0.46563,0.00031,0.12085]},{"body_a":"peg_socket","body_b":"link7","contact_count":204.0,"contact_point_centroid":[0.53025,-0.00409,0.06868],"force_p95":83.53648,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.20329,"mean_force":69.90654,"phase_index":4.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.46567,0.0001,0.12512]},{"body_a":"world","body_b":"link6","contact_count":191.0,"contact_point_centroid":[0.68285,0.00039,-0.0],"force_p95":13.91566,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.20436,"mean_force":3.26859,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4651,-9e-05,0.11948]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53028,-2e-05,0.07997],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.4651,-0.00016,0.11947]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.46683,-0.00011,0.13562],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7829.70541,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50271,-0.0001,0.10586],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02601,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":285.19583,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1530.0,"raw_peak_contact_force":7829.70541,"tcp_end":[0.4651,-0.00016,0.11947],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50297,0.00035,0.10661],"object_pos_start":[0.50271,-0.0001,0.10586],"object_to_goal_dist_end":0.02678,"object_to_goal_dist_start":0.02601,"object_z_max":0.10663,"peak_contact_force":300.564,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37.0,"raw_peak_contact_force":1075.99319,"tcp_end":[0.46542,0.00034,0.1204],"tcp_start":[0.4651,-0.00016,0.11947],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.50316,0.00032,0.10699],"object_pos_start":[0.50297,0.00035,0.10661],"object_to_goal_dist_end":0.02718,"object_to_goal_dist_start":0.02678,"object_z_max":0.1069,"peak_contact_force":198.01734,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":1000.72371,"tcp_end":[0.46563,0.00031,0.12085],"tcp_start":[0.46542,0.00034,0.1204],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5033,0.00034,0.10726],"object_pos_start":[0.50316,0.00032,0.10699],"object_to_goal_dist_end":0.02746,"object_to_goal_dist_start":0.02718,"object_z_max":0.10699,"peak_contact_force":347.28957,"phase_name":"insert_depth","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":347.28957,"tcp_end":[0.4658,0.00033,0.12116],"tcp_start":[0.46563,0.00031,0.12085],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.50417,-0.00011,0.12127],"object_pos_start":[0.5033,0.00034,0.10726],"object_to_goal_dist_end":0.04148,"object_to_goal_dist_start":0.02746,"object_z_max":0.12121,"peak_contact_force":0.0,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":206.0,"raw_peak_contact_force":548.65293,"tcp_end":[0.46683,-0.00011,0.13562],"tcp_start":[0.4658,0.00033,0.12116],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```