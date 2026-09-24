## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0261 | 0.85 | ❌ rejected |
| 8 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1199 | 0.85 | ✅ accepted |
| 7 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3981 | 0.85 | ❌ rejected |
| 6 | approach → approach → approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | impedance_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0123 | 0.83 | ❌ rejected |
| 5 | approach → approach → approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.2819 | 0.83 | ❌ rejected |

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

## Current Skill (Q=0.026) — your mutation base

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

- **Composite score**: 0.026
- **task_score** (E): 0.851
- **fitness_score**: 0.366  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_align | 0.00 | 1.00 | 0.1372 |
| align_1 | 0.00 | 1.00 | 0.0522 |
| approach_1 | 0.00 | 0.67 | 0.1383 |
| contact_1 | 1.00 | 1.00 | 0.0044 |
| insert_1 | 0.00 | 0.33 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_align | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.467, 0.004, 0.168) | (0.504, -0.000, 0.340)→(0.503, 0.003, 0.151) | 0.260→0.073 | 1.00 / 1.000 | 278.523 | 1255.846 |
| align_1 | approach | 0.00 / step_budget | (0.467, 0.004, 0.168)→(0.488, 0.045, 0.170) | (0.503, 0.003, 0.151)→(0.519, 0.034, 0.152) | 0.073→0.091 | 1.00 / 1.333 | 387.310 | 666.214 |
| approach_1 | approach | 0.00 / step_budget | (0.488, 0.045, 0.170)→(0.542, 0.014, 0.265) | (0.519, 0.034, 0.152)→(0.565, 0.012, 0.236) | 0.091→0.183 | 0.67 / 0.667 | 209.431 | 879.700 |
| contact_1 | contact | 1.00 / force_exceeded | (0.542, 0.014, 0.265)→(0.543, 0.018, 0.266) | (0.565, 0.012, 0.236)→(0.566, 0.016, 0.238) | 0.183→0.185 | 1.00 / 1.000 | 529.528 | 529.528 |
| insert_1 | insert | 0.00 / guard_failure | (0.544, 0.019, 0.267)→(0.544, 0.020, 0.267) | (0.566, 0.016, 0.238)→(0.566, 0.016, 0.238) | 0.185→0.185 | 0.33 / 0.333 | 123.451 | 284.767 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.860
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.860
- phase_score: 0.052
- phase_breakdown.approach_score: 0.038
- phase_breakdown.align_score: 0.004
- phase_breakdown.insert_score: 0.065
- phase_breakdown.contact_score: 0.056

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.375
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.862
- **Median Q (composite search score)**: 0.031
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.396


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.65672,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.00519,"approach_1.approach_speed":0.02755,"contact_1.contact_force":1.41826,"contact_1.contact_speed":0.00677,"insert_1.insert_speed":0.01997,"insert_1.insertion_depth":0.02271,"insert_1.lateral_offset_x":0.00426,"insert_1.lateral_offset_y":0.00111,"pre_align.pre_align_speed":0.08139},"optimized_scores":{"best_composite_score":0.03109,"best_fitness_score":0.37109,"best_task_score":0.83099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.52657,-0.01077,0.0676],"force_p95":316.71126,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1132.93934,"mean_force":294.5574,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45303,-0.00682,0.11026]},{"body_a":"peg_socket","body_b":"link7","contact_count":928.0,"contact_point_centroid":[0.52678,-0.04909,0.07424],"force_p95":583.48923,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":800.56973,"mean_force":394.34106,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.47177,0.02781,0.11674]},{"body_a":"world","body_b":"link6","contact_count":567.0,"contact_point_centroid":[0.6768,-0.03522,-6e-05],"force_p95":329.6868,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":682.3908,"mean_force":200.86064,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.47206,0.02801,0.11736]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52681,-0.08102,0.07998],"force_p95":634.21805,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":634.21805,"mean_force":634.21805,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54885,-0.02159,0.28125]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.44216,0.00917,0.07988],"force_p95":584.47768,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":589.92306,"mean_force":386.23816,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44011,-0.00375,0.08655]},{"body_a":"attachment","body_b":"peg_socket","contact_count":575.0,"contact_point_centroid":[0.52684,0.00547,0.07997],"force_p95":333.12623,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.45765,"mean_force":174.13075,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.46735,0.02162,0.1177]},{"body_a":"peg_socket","body_b":"link6","contact_count":911.0,"contact_point_centroid":[0.52676,-0.08099,0.07995],"force_p95":294.54048,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":392.24598,"mean_force":292.24231,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55529,-0.0214,0.27991]},{"body_a":"world","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.64251,-0.08223,-0.00012],"force_p95":346.89284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":377.73467,"mean_force":292.18239,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55002,0.07272,0.17147]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.52683,-0.08104,0.07999],"force_p95":366.61076,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":370.35363,"mean_force":332.92488,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54907,-0.02186,0.28133]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.43565,0.00622,0.07976],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.4332,-0.00672,0.08675]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52668,-0.02015,0.07994],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50547,0.07787,0.11233]}],"total_contact_groups":11},"final_pose_error":0.25268,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.54952,-0.02189,0.28107],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1132.93934,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.49746,-0.00854,0.10511],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02665,"object_to_goal_dist_start":0.26034,"object_z_max":0.34429,"peak_contact_force":319.12804,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":1132.93934,"subtask_id":"align","tcp_end":[0.45925,-0.00728,0.11688],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53143,0.05023,0.0997],"object_pos_start":[0.49746,-0.00854,0.10511],"object_to_goal_dist_end":0.06244,"object_to_goal_dist_start":0.02665,"object_z_max":0.10594,"peak_contact_force":399.88046,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2070.0,"raw_peak_contact_force":800.56973,"subtask_id":"align","tcp_end":[0.50508,0.07765,0.11209],"tcp_start":[0.45925,-0.00728,0.11688],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56481,-0.0271,0.24498],"object_pos_start":[0.53143,0.05023,0.0997],"object_to_goal_dist_end":0.17931,"object_to_goal_dist_start":0.06244,"object_z_max":0.24565,"peak_contact_force":293.43721,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":984.0,"raw_peak_contact_force":392.24598,"subtask_id":"approach","tcp_end":[0.54885,-0.02159,0.28125],"tcp_start":[0.50508,0.07765,0.11209],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.56485,-0.02724,0.24509],"object_pos_start":[0.56481,-0.0271,0.24498],"object_to_goal_dist_end":0.17945,"object_to_goal_dist_start":0.17931,"object_z_max":0.24498,"peak_contact_force":634.21805,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":634.21805,"subtask_id":"contact","tcp_end":[0.54891,-0.02174,0.28136],"tcp_start":[0.54885,-0.02159,0.28125],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.56499,-0.02742,0.24517],"object_pos_start":[0.56485,-0.02724,0.24509],"object_to_goal_dist_end":0.1796,"object_to_goal_dist_start":0.17945,"object_z_max":0.24517,"peak_contact_force":370.35363,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":370.35363,"subtask_id":"insert","tcp_end":[0.54952,-0.02189,0.28107],"tcp_start":[0.54923,-0.02198,0.2813],"tcp_to_object_dist_end":0.03948,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.33621,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03901,"approach_1.approach_speed":0.03636,"contact_1.contact_force":5.27231,"contact_1.contact_speed":0.01069,"insert_1.insert_speed":0.00749,"insert_1.insertion_depth":0.07472,"insert_1.lateral_offset_x":-0.00276,"insert_1.lateral_offset_y":-0.00525,"pre_align.pre_align_speed":0.06647},"optimized_scores":{"best_composite_score":0.035,"best_fitness_score":0.375,"best_task_score":0.85968},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":62.0,"contact_point_centroid":[0.59485,0.02481,0.07943],"force_p95":1273.8145,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1800.62788,"mean_force":586.0306,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53158,-0.12607,0.20626]},{"body_a":"peg_socket","body_b":"link7","contact_count":133.0,"contact_point_centroid":[0.5633,-0.05896,0.07842],"force_p95":413.15165,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1361.65786,"mean_force":179.10387,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50008,-0.10754,0.18788]},{"body_a":"peg_socket","body_b":"link6","contact_count":934.0,"contact_point_centroid":[0.59537,-0.00207,0.07986],"force_p95":319.93494,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":860.52448,"mean_force":253.69945,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.46942,0.0017,0.19952]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.47548,-3e-05,0.0799],"force_p95":825.92811,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":827.17598,"mean_force":547.2911,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45733,2e-05,0.08942]},{"body_a":"peg_socket","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.56814,0.00171,0.07844],"force_p95":656.50413,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":729.34186,"mean_force":112.01592,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44716,0.00011,0.10762]},{"body_a":"peg_socket","body_b":"link7","contact_count":125.0,"contact_point_centroid":[0.56573,-0.05898,0.07986],"force_p95":394.38796,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.99981,"mean_force":216.76334,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50023,-0.10476,0.1896]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.59542,0.06089,0.07998],"force_p95":595.40422,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.40422,"mean_force":595.40422,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.59906,-0.03422,0.30126]},{"body_a":"peg_socket","body_b":"link6","contact_count":739.0,"contact_point_centroid":[0.59501,-0.00217,0.07982],"force_p95":275.61887,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":506.70548,"mean_force":235.10618,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45821,0.00043,0.16218]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54281,-0.02942,0.07808],"force_p95":321.29058,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.1894,"mean_force":42.68906,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44654,9e-05,0.09933]},{"body_a":"peg_socket","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.59508,-0.00149,0.07982],"force_p95":446.56601,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.58168,"mean_force":378.90603,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.49491,-0.00023,0.18014]},{"body_a":"peg_socket","body_b":"link6","contact_count":718.0,"contact_point_centroid":[0.59534,-0.00293,0.07983],"force_p95":338.29744,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":437.4752,"mean_force":277.30074,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4827,-0.05306,0.20877]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.59539,0.06087,0.07993],"force_p95":220.33763,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.33763,"mean_force":220.33763,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.59995,-0.03142,0.30262]}],"total_contact_groups":12},"final_pose_error":0.32289,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.60329,-0.02364,0.30501],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1800.62788,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":960.0,"object_pos_end":[0.51029,0.00096,0.17941],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09995,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":249.3686,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":802.0,"raw_peak_contact_force":827.17598,"subtask_id":"align","tcp_end":[0.4756,0.00098,0.19934],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51791,0.00343,0.16898],"object_pos_start":[0.51029,0.00096,0.17941],"object_to_goal_dist_end":0.09083,"object_to_goal_dist_start":0.09995,"object_z_max":0.19702,"peak_contact_force":470.92292,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":943.0,"raw_peak_contact_force":860.52448,"subtask_id":"align","tcp_end":[0.48252,-0.00029,0.18724],"tcp_start":[0.4756,0.00098,0.19934],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62073,-0.02579,0.27003],"object_pos_start":[0.51791,0.00343,0.16898],"object_to_goal_dist_end":0.22661,"object_to_goal_dist_start":0.09083,"object_z_max":0.26871,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1038.0,"raw_peak_contact_force":1800.62788,"subtask_id":"approach","tcp_end":[0.59671,-0.04279,0.29712],"tcp_start":[0.48252,-0.00029,0.18724],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.62281,-0.01453,0.27448],"object_pos_start":[0.62073,-0.02579,0.27003],"object_to_goal_dist_end":0.23046,"object_to_goal_dist_start":0.22661,"object_z_max":0.27338,"peak_contact_force":595.40422,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":595.40422,"subtask_id":"contact","tcp_end":[0.59995,-0.03142,0.30262],"tcp_start":[0.59671,-0.04279,0.29712],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.62358,-0.01183,0.27543],"object_pos_start":[0.62281,-0.01453,0.27448],"object_to_goal_dist_end":0.23153,"object_to_goal_dist_start":0.23046,"object_z_max":0.27607,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":220.33763,"subtask_id":"insert","tcp_end":[0.60329,-0.02364,0.30501],"tcp_start":[0.6021,-0.02614,0.30458],"tcp_to_object_dist_end":0.03776,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.59821,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02318,"approach_1.approach_speed":0.02047,"contact_1.contact_force":5.63211,"contact_1.contact_speed":0.0087,"insert_1.insert_speed":0.01187,"insert_1.insertion_depth":0.05535,"insert_1.lateral_offset_x":-0.00262,"insert_1.lateral_offset_y":-0.0046,"pre_align.pre_align_speed":0.09998},"optimized_scores":{"best_composite_score":0.01217,"best_fitness_score":0.35217,"best_task_score":0.8621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":435.0,"contact_point_centroid":[0.5843,0.00928,0.07955],"force_p95":831.95709,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1807.4227,"mean_force":336.67593,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45862,0.01063,0.16038]},{"body_a":"peg_socket","body_b":"link7","contact_count":217.0,"contact_point_centroid":[0.57965,0.01102,0.07964],"force_p95":1436.022,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1782.41529,"mean_force":392.17807,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45913,0.00646,0.14277]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46606,0.0042,0.07864],"force_p95":1044.96185,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1085.90073,"mean_force":273.55273,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45861,0.0042,0.0906]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.55235,-0.00558,0.07862],"force_p95":818.76711,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.90185,"mean_force":313.45067,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45557,0.00481,0.09974]},{"body_a":"peg_socket","body_b":"link6","contact_count":985.0,"contact_point_centroid":[0.58433,0.00989,0.0799],"force_p95":312.77338,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.22687,"mean_force":282.66854,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47703,0.10966,0.2058]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58418,0.02195,0.07972],"force_p95":358.96125,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.96125,"mean_force":358.96125,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48072,0.10591,0.21519]},{"body_a":"peg_socket","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.58436,0.02168,0.07992],"force_p95":294.11066,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.54771,"mean_force":251.81409,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.45703,0.03254,0.18756]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58425,0.02169,0.07981],"force_p95":263.33039,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.61097,"mean_force":260.56943,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48066,0.10607,0.21523]}],"total_contact_groups":8},"final_pose_error":0.22564,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.48038,0.10664,0.2152],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1807.4227,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50115,0.01777,0.16997],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09172,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":267.07117,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":685.0,"raw_peak_contact_force":1807.4227,"subtask_id":"align","tcp_end":[0.46528,0.01781,0.18766],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50742,0.049,0.18771],"object_pos_start":[0.50115,0.01777,0.16997],"object_to_goal_dist_end":0.11857,"object_to_goal_dist_start":0.09172,"object_z_max":0.18765,"peak_contact_force":291.12756,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":337.54771,"subtask_id":"align","tcp_end":[0.47539,0.05658,0.21044],"tcp_start":[0.46528,0.01781,0.18766],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50913,0.08841,0.19313],"object_pos_start":[0.50742,0.049,0.18771],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.11857,"object_z_max":0.19418,"peak_contact_force":334.85687,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":985.0,"raw_peak_contact_force":446.22687,"subtask_id":"approach","tcp_end":[0.48072,0.10591,0.21519],"tcp_start":[0.47539,0.05658,0.21044],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50914,0.0884,0.19316],"object_pos_start":[0.50913,0.08841,0.19313],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14387,"object_z_max":0.19313,"peak_contact_force":358.96125,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":358.96125,"subtask_id":"contact","tcp_end":[0.48074,0.1059,0.21523],"tcp_start":[0.48072,0.10591,0.21519],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5091,0.08848,0.19322],"object_pos_start":[0.50914,0.0884,0.19316],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14389,"object_z_max":0.1933,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":263.61097,"subtask_id":"insert","tcp_end":[0.48038,0.10664,0.2152],"tcp_start":[0.48056,0.10627,0.21523],"tcp_to_object_dist_end":0.04047,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```