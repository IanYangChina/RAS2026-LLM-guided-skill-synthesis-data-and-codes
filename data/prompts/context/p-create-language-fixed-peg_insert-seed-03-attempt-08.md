## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1199 | 0.85 | ✅ accepted |
| 7 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3981 | 0.85 | ❌ rejected |
| 6 | approach → approach → approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | impedance_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0123 | 0.83 | ❌ rejected |
| 5 | approach → approach → approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.2819 | 0.83 | ❌ rejected |
| 4 | approach → approach → approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.2347 | 0.81 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.46685193337148995, -0.021055159472312023, 0.08]
- Frozen socket pose: [0.46685193337148995, -0.021055159472312023, 0.025] (static fixture for this episode)
- Goal object position: (0.46685193337148995, -0.021055159472312023, 0.025)
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
  frozen_task_target: [0.4669, -0.0211, 0.08]
  frozen_socket_position: [0.4669, -0.0211, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.46685193337148995, -0.021055159472312023, 0.08]}
  frozen_fixtures: {'peg_socket': [0.46685193337148995, -0.021055159472312023, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e

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

## Current Skill (Q=0.120) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: pre_align
  type: approach
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
    - 0.18
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    pre_align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align
- id: align_1
  type: approach
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
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lateral_tolerance
    when: during_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: align
- id: approach_1
  type: approach
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
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
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
      - 1.0
      align_with: world_z
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
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: insert_1
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
    - 0.05
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: insert

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **pre_align** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.18]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - pre_align_speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lateral_tolerance, when=during_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.07]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.05], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.120
- **task_score** (E): 0.853
- **fitness_score**: 0.360  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_align | 0.00 | 1.00 | 0.1362 |
| align_1 | 0.00 | 1.00 | 0.0001 |
| approach_1 | 0.00 | 0.67 | 0.0807 |
| contact_1 | 1.00 | 1.00 | 0.0044 |
| insert_1 | 0.00 | 1.00 | 0.0040 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_align | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.466, 0.004, 0.169) | (0.504, -0.000, 0.340)→(0.502, 0.003, 0.152) | 0.260→0.074 | 1.00 / 1.000 | 304.169 | 2275.139 |
| align_1 | approach | 0.00 / guard_failure | (0.466, 0.004, 0.169)→(0.466, 0.004, 0.169) | (0.502, 0.003, 0.152)→(0.503, 0.003, 0.152) | 0.074→0.074 | 1.00 / 1.000 | 299.385 | 314.578 |
| approach_1 | approach | 0.00 / step_budget | (0.466, 0.004, 0.169)→(0.501, 0.003, 0.235) | (0.503, 0.003, 0.153)→(0.526, -0.003, 0.206) | 0.074→0.135 | 0.67 / 0.667 | 179.760 | 539.329 |
| contact_1 | contact | 1.00 / force_exceeded | (0.501, 0.003, 0.235)→(0.502, -0.001, 0.236) | (0.526, -0.003, 0.206)→(0.528, -0.007, 0.208) | 0.135→0.135 | 1.00 / 1.000 | 505.489 | 505.489 |
| insert_1 | insert | 0.00 / guard_failure | (0.502, -0.001, 0.236)→(0.504, -0.004, 0.239) | (0.528, -0.007, 0.208)→(0.528, -0.010, 0.210) | 0.135→0.138 | 1.00 / 1.000 | 785.029 | 542.499 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.869
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.869
- phase_score: 0.025
- phase_breakdown.approach_score: 0.018
- phase_breakdown.align_score: 0.005
- phase_breakdown.insert_score: 0.032
- phase_breakdown.contact_score: 0.026

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.363
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.869
- **Median Q (composite search score)**: 0.120
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.413


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f11800d9c2e1994b03c35d775c68a936832c378ea82102a5404a99f161f65289`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ef8adc000d20c9595fb92eedb002c99ab6f0fb118834572ef2a426eae092b67`; realized-scene SHA-256: `3a9889f49656bcc88af2945ad0b69da740661b3d51c4f32509721809854ac75e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.93617,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02728,"approach_1.approach_speed":0.00583,"contact_1.contact_force":1.5835,"contact_1.contact_speed":0.00506,"insert_1.insert_speed":0.02177,"insert_1.insertion_depth":0.07059,"pre_align.pre_align_speed":0.0812},"optimized_scores":{"best_composite_score":0.12048,"best_fitness_score":0.36048,"best_task_score":0.83099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.52657,-0.01077,0.0676],"force_p95":316.71126,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1132.93934,"mean_force":294.5574,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45303,-0.00682,0.11026]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.52675,-0.08094,0.07994],"force_p95":820.68106,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":863.8748,"mean_force":431.9374,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53458,-0.05009,0.26673]},{"body_a":"peg_socket","body_b":"link7","contact_count":772.0,"contact_point_centroid":[0.52678,-0.05017,0.07264],"force_p95":627.15097,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":829.28051,"mean_force":408.96398,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46813,0.02201,0.11734]},{"body_a":"peg_socket","body_b":"link6","contact_count":120.0,"contact_point_centroid":[0.52653,-0.08077,0.07984],"force_p95":641.87595,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":734.41533,"mean_force":325.23591,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5368,-0.03088,0.25717]},{"body_a":"world","body_b":"link6","contact_count":503.0,"contact_point_centroid":[0.67522,-0.03256,-7e-05],"force_p95":395.68165,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":635.25989,"mean_force":228.14839,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47327,0.02394,0.12417]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.44216,0.00917,0.07988],"force_p95":584.47768,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":589.92306,"mean_force":386.23816,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44011,-0.00375,0.08655]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52676,-0.08096,0.07995],"force_p95":582.01216,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":582.01216,"mean_force":582.01216,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53292,-0.04665,0.26361]},{"body_a":"attachment","body_b":"peg_socket","contact_count":519.0,"contact_point_centroid":[0.52684,0.005,0.07997],"force_p95":357.51468,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.72458,"mean_force":175.7145,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46706,0.02049,0.11775]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52679,-0.01267,0.06408],"force_p95":326.00579,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.23896,"mean_force":323.90726,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.45926,-0.00725,0.11689]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.43565,0.00622,0.07976],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.4332,-0.00672,0.08675]}],"total_contact_groups":10},"final_pose_error":0.27711,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.53629,-0.05421,0.27062],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1132.93934,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.49746,-0.00854,0.10511],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02665,"object_to_goal_dist_start":0.26034,"object_z_max":0.34429,"peak_contact_force":319.12804,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":1132.93934,"subtask_id":"align","tcp_end":[0.45925,-0.00728,0.11688],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":750.0,"object_pos_end":[0.49747,-0.00852,0.10511],"object_pos_start":[0.49746,-0.00854,0.10511],"object_to_goal_dist_end":0.02664,"object_to_goal_dist_start":0.02665,"object_z_max":0.10511,"peak_contact_force":321.57556,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":326.23896,"subtask_id":"align","tcp_end":[0.45929,-0.00723,0.1169],"tcp_start":[0.45927,-0.00723,0.11689],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54893,-0.05281,0.22747],"object_pos_start":[0.49749,-0.00852,0.10511],"object_to_goal_dist_end":0.1641,"object_to_goal_dist_start":0.02664,"object_z_max":0.22744,"peak_contact_force":294.63485,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1914.0,"raw_peak_contact_force":829.28051,"subtask_id":"approach","tcp_end":[0.53292,-0.04665,0.26361],"tcp_start":[0.45929,-0.00723,0.1169],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.549,-0.05303,0.22758],"object_pos_start":[0.54893,-0.05281,0.22747],"object_to_goal_dist_end":0.16429,"object_to_goal_dist_start":0.1641,"object_z_max":0.22747,"peak_contact_force":582.01216,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":582.01216,"subtask_id":"contact","tcp_end":[0.53301,-0.04689,0.26372],"tcp_start":[0.53292,-0.04665,0.26361],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.55019,-0.0605,0.23365],"object_pos_start":[0.549,-0.05303,0.22758],"object_to_goal_dist_end":0.17259,"object_to_goal_dist_start":0.16429,"object_z_max":0.23289,"peak_contact_force":863.8748,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":863.8748,"subtask_id":"insert","tcp_end":[0.53629,-0.05421,0.27062],"tcp_start":[0.53301,-0.04689,0.26372],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3e77e957595308cac760f5f4d0307201511ded613ae0a20d2d9d48ef360ca4f0`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.11594,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.08041,"approach_1.approach_speed":0.03115,"contact_1.contact_force":8.06775,"contact_1.contact_speed":0.01993,"insert_1.insert_speed":0.02444,"insert_1.insertion_depth":0.08257,"pre_align.pre_align_speed":0.09999},"optimized_scores":{"best_composite_score":0.12258,"best_fitness_score":0.36258,"best_task_score":0.86857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.56829,0.0017,0.07934],"force_p95":798.43383,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":895.61755,"mean_force":318.68983,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44599,-9e-05,0.11001]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.47552,5e-05,0.07981],"force_p95":826.29397,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.772,"mean_force":781.79069,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.4659,6e-05,0.09196]},{"body_a":"peg_socket","body_b":"link6","contact_count":453.0,"contact_point_centroid":[0.59535,-0.00295,0.07983],"force_p95":276.64193,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":430.80382,"mean_force":239.0492,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45866,0.00013,0.17407]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59541,-0.00272,0.07996],"force_p95":326.026,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.32185,"mean_force":305.3633,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48145,0.00192,0.22478]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59535,-0.00269,0.07987],"force_p95":316.88197,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.88197,"mean_force":316.88197,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48128,0.00195,0.22476]},{"body_a":"peg_socket","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.59537,-0.0031,0.07986],"force_p95":272.05923,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.34154,"mean_force":235.56013,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46227,0.00096,0.20001]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59532,-0.00277,0.07979],"force_p95":288.42685,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.50515,"mean_force":287.72214,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.47462,0.00064,0.20168]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.54387,-0.02924,0.0791],"force_p95":14.36238,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.03537,"mean_force":2.9311,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44714,-0.0001,0.09991]}],"total_contact_groups":8},"final_pose_error":0.2385,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.48106,0.00196,0.22464],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1044.46985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50904,0.00063,0.18132],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10172,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":292.80682,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":497.0,"raw_peak_contact_force":895.61755,"subtask_id":"align","tcp_end":[0.47458,0.00064,0.20163],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":660.0,"object_pos_end":[0.5091,0.00064,0.18139],"object_pos_start":[0.50904,0.00063,0.18132],"object_to_goal_dist_end":0.10179,"object_to_goal_dist_start":0.10172,"object_z_max":0.18139,"peak_contact_force":286.93913,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":288.50515,"subtask_id":"align","tcp_end":[0.47473,0.00064,0.20182],"tcp_start":[0.47466,0.00064,0.20173],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51301,0.00173,0.20011],"object_pos_start":[0.50916,0.00064,0.18145],"object_to_goal_dist_end":0.12082,"object_to_goal_dist_start":0.10187,"object_z_max":0.20133,"peak_contact_force":244.64464,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":991.0,"raw_peak_contact_force":295.34154,"subtask_id":"approach","tcp_end":[0.48152,0.00191,0.22477],"tcp_start":[0.47473,0.00064,0.20182],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51275,0.00177,0.20008],"object_pos_start":[0.51301,0.00173,0.20011],"object_to_goal_dist_end":0.12076,"object_to_goal_dist_start":0.12082,"object_z_max":0.20015,"peak_contact_force":328.32185,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":328.32185,"subtask_id":"contact","tcp_end":[0.48128,0.00195,0.22476],"tcp_start":[0.48152,0.00191,0.22477],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51255,0.00178,0.19997],"object_pos_start":[0.51275,0.00177,0.20008],"object_to_goal_dist_end":0.12064,"object_to_goal_dist_start":0.12076,"object_z_max":0.20008,"peak_contact_force":1044.46985,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":316.88197,"subtask_id":"insert","tcp_end":[0.48106,0.00196,0.22464],"tcp_start":[0.48128,0.00195,0.22476],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f1677605f38c34d5c76967e3b08a88589314d198860b89f86514cd0f3e96f4b3`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.2,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04366,"approach_1.approach_speed":0.03612,"contact_1.contact_force":13.95043,"contact_1.contact_speed":0.00989,"insert_1.insert_speed":0.02496,"insert_1.insertion_depth":0.05323,"pre_align.pre_align_speed":0.09409},"optimized_scores":{"best_composite_score":0.11673,"best_fitness_score":0.35673,"best_task_score":0.86002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":466.0,"contact_point_centroid":[0.58425,0.00882,0.07948],"force_p95":2517.49345,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4796.86157,"mean_force":504.49374,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.4579,0.0103,0.16049]},{"body_a":"peg_socket","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.57937,0.01036,0.07952],"force_p95":4046.30059,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4754.69004,"mean_force":765.40487,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45862,0.00586,0.14218]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46583,0.004,0.07881],"force_p95":1039.97467,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1081.57261,"mean_force":272.29785,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45797,0.004,0.09084]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.55168,-0.00559,0.07855],"force_p95":900.29971,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1002.0863,"mean_force":268.72296,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.455,0.00447,0.10044]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58427,-0.01565,0.07985],"force_p95":606.13311,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":606.13311,"mean_force":606.13311,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49241,0.04335,0.21995]},{"body_a":"peg_socket","body_b":"link6","contact_count":973.0,"contact_point_centroid":[0.58434,0.02103,0.07988],"force_p95":309.56607,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":493.36444,"mean_force":258.74907,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46282,0.03217,0.19497]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58415,-0.01769,0.07972],"force_p95":446.74125,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.74125,"mean_force":446.74125,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49295,0.04195,0.22023]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.5843,0.01491,0.0798],"force_p95":327.02289,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.99038,"mean_force":309.31556,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.46528,0.01783,0.18891]}],"total_contact_groups":8},"final_pose_error":0.20182,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.49353,0.0409,0.22055],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":4796.86157,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50097,0.01774,0.17084],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09256,"object_to_goal_dist_start":0.26034,"object_z_max":0.34463,"peak_contact_force":300.57336,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":718.0,"raw_peak_contact_force":4796.86157,"subtask_id":"align","tcp_end":[0.46525,0.01784,0.18884],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50101,0.01773,0.17093],"object_pos_start":[0.50097,0.01774,0.17084],"object_to_goal_dist_end":0.09265,"object_to_goal_dist_start":0.09256,"object_z_max":0.17093,"peak_contact_force":289.64074,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":328.99038,"subtask_id":"align","tcp_end":[0.46536,0.01786,0.18909],"tcp_start":[0.46531,0.01781,0.18897],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5175,0.04131,0.19178],"object_pos_start":[0.50104,0.0178,0.17101],"object_to_goal_dist_end":0.12044,"object_to_goal_dist_start":0.09274,"object_z_max":0.19301,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":973.0,"raw_peak_contact_force":493.36444,"subtask_id":"approach","tcp_end":[0.48778,0.0526,0.21606],"tcp_start":[0.46536,0.01786,0.18909],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.52105,0.02876,0.195],"object_pos_start":[0.5175,0.04131,0.19178],"object_to_goal_dist_end":0.12039,"object_to_goal_dist_start":0.12044,"object_z_max":0.19482,"peak_contact_force":606.13311,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":606.13311,"subtask_id":"contact","tcp_end":[0.49295,0.04195,0.22023],"tcp_start":[0.48778,0.0526,0.21606],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52143,0.02744,0.19525],"object_pos_start":[0.52105,0.02876,0.195],"object_to_goal_dist_end":0.12039,"object_to_goal_dist_start":0.12039,"object_z_max":0.195,"peak_contact_force":446.74125,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":446.74125,"subtask_id":"insert","tcp_end":[0.49353,0.0409,0.22055],"tcp_start":[0.49295,0.04195,0.22023],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```