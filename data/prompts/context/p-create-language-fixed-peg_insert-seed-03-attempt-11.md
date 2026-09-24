## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1344 | 0.85 | ❌ rejected |
| 10 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1234 | 0.85 | ✅ accepted |
| 9 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0261 | 0.85 | ❌ rejected |
| 8 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1199 | 0.85 | ✅ accepted |
| 7 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3981 | 0.85 | ❌ rejected |

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

## Current Skill (Q=0.134) — your mutation base

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

- **Composite score**: 0.134
- **task_score** (E): 0.849
- **fitness_score**: 0.374  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_align | 0.00 | 1.00 | 0.1348 |
| align_1 | 0.33 | 0.67 | 0.0366 |
| approach_1 | 0.00 | 1.00 | 0.1422 |
| contact_1 | 1.00 | 1.00 | 0.0002 |
| insert_1 | 0.00 | 0.00 | 0.0007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_align | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.467, 0.003, 0.170) | (0.504, -0.000, 0.340)→(0.503, 0.002, 0.153) | 0.260→0.074 | 1.00 / 1.333 | 288.314 | 1034.387 |
| align_1 | align | 0.33 / step_budget | (0.467, 0.003, 0.170)→(0.486, 0.013, 0.167) | (0.503, 0.002, 0.153)→(0.520, 0.012, 0.149) | 0.074→0.080 | 0.67 / 1.000 | 224.983 | 610.459 |
| approach_1 | approach | 0.00 / step_budget | (0.486, 0.013, 0.167)→(0.549, -0.021, 0.282) | (0.520, 0.012, 0.149)→(0.568, -0.021, 0.248) | 0.080→0.187 | 1.00 / 1.333 | 300.680 | 1687.095 |
| contact_1 | contact | 1.00 / force_exceeded | (0.549, -0.021, 0.282)→(0.549, -0.021, 0.282) | (0.568, -0.021, 0.248)→(0.568, -0.021, 0.248) | 0.187→0.187 | 1.00 / 1.333 | 683.080 | 683.080 |
| insert_1 | insert | 0.00 / guard_failure | (0.549, -0.021, 0.281)→(0.549, -0.021, 0.281) | (0.568, -0.021, 0.248)→(0.569, -0.021, 0.248) | 0.187→0.187 | 0.00 / 0.000 | 0.000 | 165.395 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.864
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.864
- phase_score: 0.064
- phase_breakdown.approach_score: 0.046
- phase_breakdown.align_score: 0.007
- phase_breakdown.insert_score: 0.080
- phase_breakdown.contact_score: 0.068

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.384
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.864
- **Median Q (composite search score)**: 0.141
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.44,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04556,"approach_1.approach_speed":0.00894,"contact_1.contact_force":12.4688,"contact_1.contact_speed":0.01322,"insert_1.insert_speed":0.02333,"insert_1.insertion_depth":0.02609,"pre_align.pre_align_speed":0.09275},"optimized_scores":{"best_composite_score":0.11859,"best_fitness_score":0.35859,"best_task_score":0.83246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":227.0,"contact_point_centroid":[0.66842,-0.04694,-0.00015],"force_p95":604.72888,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1844.08067,"mean_force":239.55442,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4781,0.01928,0.13357]},{"body_a":"peg_socket","body_b":"link7","contact_count":591.0,"contact_point_centroid":[0.52677,-0.03827,0.07303],"force_p95":745.23139,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1269.68361,"mean_force":435.36493,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46697,0.01638,0.11784]},{"body_a":"peg_socket","body_b":"link7","contact_count":539.0,"contact_point_centroid":[0.52653,-0.0112,0.067],"force_p95":312.71549,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1131.25222,"mean_force":293.87962,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45273,-0.00708,0.10893]},{"body_a":"peg_socket","body_b":"link6","contact_count":327.0,"contact_point_centroid":[0.52666,-0.08091,0.07992],"force_p95":304.61293,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1043.53002,"mean_force":317.63935,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53059,-0.04279,0.26038]},{"body_a":"attachment","body_b":"peg_socket","contact_count":515.0,"contact_point_centroid":[0.52684,-0.0018,0.07998],"force_p95":468.90547,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":869.70619,"mean_force":268.16724,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46604,0.01434,0.11816]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.44191,0.00916,0.07989],"force_p95":570.92118,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":578.0972,"mean_force":369.16943,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44007,-0.00415,0.08583]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52681,-0.08101,0.07998],"force_p95":573.27611,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":573.27611,"mean_force":573.27611,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53031,-0.05243,0.26351]},{"body_a":"peg_socket","body_b":"link7","contact_count":281.0,"contact_point_centroid":[0.52677,-0.01334,0.06356],"force_p95":334.28662,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.64057,"mean_force":293.23636,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46159,-0.00518,0.11889]},{"body_a":"world","body_b":"link6","contact_count":127.0,"contact_point_centroid":[0.67948,-0.01792,-3e-05],"force_p95":170.02518,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.20284,"mean_force":50.94604,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46212,-0.00469,0.1194]},{"body_a":"attachment","body_b":"peg_socket","contact_count":208.0,"contact_point_centroid":[0.52685,-0.00946,0.07998],"force_p95":162.34431,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.92108,"mean_force":88.49816,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46178,-0.00489,0.11905]},{"body_a":"attachment","body_b":"peg_socket","contact_count":52.0,"contact_point_centroid":[0.52685,-0.00933,0.07999],"force_p95":107.47385,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.9467,"mean_force":97.24595,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45851,-0.00742,0.11567]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52683,-0.08103,0.07999],"force_p95":55.50277,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.50277,"mean_force":55.50277,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53044,-0.05258,0.2636]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.43557,0.00653,0.07975],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.43324,-0.00703,0.08556]}],"total_contact_groups":13},"final_pose_error":0.22518,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.53125,-0.05381,0.26219],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1844.08067,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.4973,-0.00853,0.10464],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02622,"object_to_goal_dist_start":0.26034,"object_z_max":0.3443,"peak_contact_force":305.26612,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":610.0,"raw_peak_contact_force":1131.25222,"subtask_id":"align","tcp_end":[0.45905,-0.00732,0.11629],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.49969,-0.0069,0.10574],"object_pos_start":[0.4973,-0.00853,0.10464],"object_to_goal_dist_end":0.02665,"object_to_goal_dist_start":0.02622,"object_z_max":0.10593,"peak_contact_force":295.97295,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":616.0,"raw_peak_contact_force":365.64057,"subtask_id":"align","tcp_end":[0.46219,-0.00395,0.11933],"tcp_start":[0.45905,-0.00732,0.11629],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54627,-0.05794,0.22725],"object_pos_start":[0.49969,-0.0069,0.10574],"object_to_goal_dist_end":0.16487,"object_to_goal_dist_start":0.02665,"object_z_max":0.22726,"peak_contact_force":297.13694,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":1844.08067,"subtask_id":"approach","tcp_end":[0.53031,-0.05243,0.26351],"tcp_start":[0.46219,-0.00395,0.11933],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54638,-0.05809,0.22733],"object_pos_start":[0.54627,-0.05794,0.22725],"object_to_goal_dist_end":0.16502,"object_to_goal_dist_start":0.16487,"object_z_max":0.22725,"peak_contact_force":573.27611,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":573.27611,"subtask_id":"contact","tcp_end":[0.53044,-0.05258,0.2636],"tcp_start":[0.53031,-0.05243,0.26351],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.54655,-0.0583,0.22724],"object_pos_start":[0.54638,-0.05809,0.22733],"object_to_goal_dist_end":0.16506,"object_to_goal_dist_start":0.16502,"object_z_max":0.22733,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":55.50277,"subtask_id":"insert","tcp_end":[0.53125,-0.05381,0.26219],"tcp_start":[0.531,-0.05329,0.26276],"tcp_to_object_dist_end":0.03842,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.03226,"average_mean_iterations":12.80645,"average_solve_count":93.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.07267,"approach_1.approach_speed":0.04459,"contact_1.contact_force":15.42927,"contact_1.contact_speed":0.01302,"insert_1.insert_speed":0.02279,"insert_1.insertion_depth":0.03722,"pre_align.pre_align_speed":0.08935},"optimized_scores":{"best_composite_score":0.14381,"best_fitness_score":0.38381,"best_task_score":0.86376},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":969.0,"contact_point_centroid":[0.51236,0.06081,0.07577],"force_p95":368.64151,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2265.22122,"mean_force":315.3013,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52383,0.0089,0.27346]},{"body_a":"peg_socket","body_b":"link6","contact_count":970.0,"contact_point_centroid":[0.59539,0.05928,0.07996],"force_p95":452.76772,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2193.86269,"mean_force":250.95258,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52352,0.00862,0.27297]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.56561,0.00094,0.07905],"force_p95":776.80687,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":996.96354,"mean_force":215.25082,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44628,-0.00011,0.10556]},{"body_a":"peg_socket","body_b":"link6","contact_count":575.0,"contact_point_centroid":[0.59535,-0.00144,0.07981],"force_p95":424.53353,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":832.33907,"mean_force":269.26842,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47265,0.00035,0.19689]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.4755,-1e-05,0.07986],"force_p95":825.79393,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":827.62527,"mean_force":786.37117,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.46153,4e-05,0.09057]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51222,0.06086,0.07609],"force_p95":803.54075,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":803.54075,"mean_force":803.54075,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52648,0.00987,0.27345]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.59449,0.00208,0.07972],"force_p95":692.7605,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":723.64842,"mean_force":393.93568,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49456,-0.00332,0.18014]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59541,0.0609,0.07997],"force_p95":590.06424,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":590.06424,"mean_force":590.06424,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52648,0.00987,0.27345]},{"body_a":"peg_socket","body_b":"link6","contact_count":526.0,"contact_point_centroid":[0.59498,-0.00252,0.07985],"force_p95":275.28924,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.36578,"mean_force":236.67802,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45889,0.00018,0.16502]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59542,0.06091,0.07998],"force_p95":312.98249,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.98249,"mean_force":312.98249,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52646,0.00995,0.27349]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51222,0.06088,0.07612],"force_p95":251.52839,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.52839,"mean_force":251.52839,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52646,0.00995,0.27349]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.54268,-0.02929,0.07885],"force_p95":54.67439,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.45284,"mean_force":6.95007,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44613,-0.00011,0.1001]},{"body_a":"peg_socket","body_b":"link5","contact_count":13.0,"contact_point_centroid":[0.54061,0.06031,0.04983],"force_p95":0.0,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51858,-0.01399,0.26303]}],"total_contact_groups":13},"final_pose_error":0.23455,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52722,0.01098,0.27197],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":2265.22122,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50955,0.00069,0.1775],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09797,"object_to_goal_dist_start":0.26034,"object_z_max":0.34476,"peak_contact_force":289.60429,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":571.0,"raw_peak_contact_force":996.96354,"subtask_id":"align","tcp_end":[0.47459,0.00069,0.19694],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":810.0,"object_pos_end":[0.52433,-0.01227,0.19362],"object_pos_start":[0.50955,0.00069,0.1775],"object_to_goal_dist_end":0.11684,"object_to_goal_dist_start":0.09797,"object_z_max":0.19281,"peak_contact_force":378.97543,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":587.0,"raw_peak_contact_force":832.33907,"subtask_id":"align","tcp_end":[0.49395,-0.0204,0.21833],"tcp_start":[0.47459,0.00069,0.19694],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54704,0.01905,0.24039],"object_pos_start":[0.52433,-0.01227,0.19362],"object_to_goal_dist_end":0.16823,"object_to_goal_dist_start":0.11684,"object_z_max":0.24103,"peak_contact_force":294.46132,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":2265.22122,"subtask_id":"approach","tcp_end":[0.52648,0.00987,0.27345],"tcp_start":[0.49395,-0.0204,0.21833],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54703,0.01913,0.24043],"object_pos_start":[0.54704,0.01905,0.24039],"object_to_goal_dist_end":0.16827,"object_to_goal_dist_start":0.16823,"object_z_max":0.24039,"peak_contact_force":803.54075,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":803.54075,"subtask_id":"contact","tcp_end":[0.52646,0.00995,0.27349],"tcp_start":[0.52648,0.00987,0.27345],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.5471,0.01929,0.24037],"object_pos_start":[0.54703,0.01913,0.24043],"object_to_goal_dist_end":0.16826,"object_to_goal_dist_start":0.16827,"object_z_max":0.24043,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":312.98249,"subtask_id":"insert","tcp_end":[0.52722,0.01098,0.27197],"tcp_start":[0.52688,0.01062,0.27265],"tcp_to_object_dist_end":0.03825,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.01923,"average_mean_iterations":11.89423,"average_solve_count":104.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.06528,"approach_1.approach_speed":0.02725,"contact_1.contact_force":9.24223,"contact_1.contact_speed":0.01542,"insert_1.insert_speed":0.01826,"insert_1.insertion_depth":0.05437,"pre_align.pre_align_speed":0.07354},"optimized_scores":{"best_composite_score":0.14089,"best_fitness_score":0.38089,"best_task_score":0.85035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.46472,0.00311,0.07933],"force_p95":923.13716,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":974.94409,"mean_force":225.23355,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45287,0.00309,0.09071]},{"body_a":"peg_socket","body_b":"link6","contact_count":896.0,"contact_point_centroid":[0.58416,0.03822,0.07978],"force_p95":385.66817,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":951.98321,"mean_force":310.63197,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51953,0.07938,0.22715]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.54459,-0.00575,0.07765],"force_p95":749.609,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":937.42833,"mean_force":251.89863,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44855,0.00334,0.10244]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.55478,0.00249,0.07796],"force_p95":232.61378,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":689.18684,"mean_force":184.31467,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44856,0.00336,0.10306]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58435,-0.03534,0.07996],"force_p95":672.42445,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":672.42445,"mean_force":672.42445,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5898,-0.01983,0.30865]},{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.58429,0.03651,0.07981],"force_p95":617.23254,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":633.39692,"mean_force":448.38897,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49562,0.05901,0.1764]},{"body_a":"peg_socket","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.58438,0.04242,0.07995],"force_p95":502.38955,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":582.95095,"mean_force":350.68845,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49989,0.07745,0.17419]},{"body_a":"peg_socket","body_b":"link6","contact_count":639.0,"contact_point_centroid":[0.58432,0.01749,0.07986],"force_p95":335.03601,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.7967,"mean_force":260.02399,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46569,0.02155,0.20105]},{"body_a":"peg_socket","body_b":"link6","contact_count":650.0,"contact_point_centroid":[0.58436,0.00674,0.07987],"force_p95":284.95148,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.06266,"mean_force":248.9568,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45353,0.00924,0.16744]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58438,-0.03535,0.07999],"force_p95":127.69995,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.69995,"mean_force":127.69995,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.58981,-0.02012,0.30882]}],"total_contact_groups":10},"final_pose_error":0.29945,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.58979,-0.02152,0.30918],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":974.94409,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50092,0.0151,0.17809],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09925,"object_to_goal_dist_start":0.26034,"object_z_max":0.34454,"peak_contact_force":270.07253,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":719.0,"raw_peak_contact_force":974.94409,"subtask_id":"align","tcp_end":[0.46617,0.01534,0.1979],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":724.0,"n_steps_budget":900.0,"object_pos_end":[0.53625,0.05495,0.1491],"object_pos_start":[0.50092,0.0151,0.17809],"object_to_goal_dist_end":0.09544,"object_to_goal_dist_start":0.09925,"object_z_max":0.19518,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":668.0,"raw_peak_contact_force":633.39692,"subtask_id":"align","tcp_end":[0.50064,0.06435,0.16471],"tcp_start":[0.46617,0.01534,0.1979],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61197,-0.02292,0.2755],"object_pos_start":[0.53625,0.05495,0.1491],"object_to_goal_dist_end":0.22645,"object_to_goal_dist_start":0.09544,"object_z_max":0.27549,"peak_contact_force":310.44296,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":937.0,"raw_peak_contact_force":951.98321,"subtask_id":"approach","tcp_end":[0.5898,-0.01983,0.30865],"tcp_start":[0.50064,0.06435,0.16471],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.61199,-0.02317,0.27567],"object_pos_start":[0.61197,-0.02292,0.2755],"object_to_goal_dist_end":0.22664,"object_to_goal_dist_start":0.22645,"object_z_max":0.2755,"peak_contact_force":672.42445,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":672.42445,"subtask_id":"contact","tcp_end":[0.58981,-0.02012,0.30882],"tcp_start":[0.5898,-0.01983,0.30865],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.61205,-0.02347,0.27584],"object_pos_start":[0.61199,-0.02317,0.27567],"object_to_goal_dist_end":0.22685,"object_to_goal_dist_start":0.22664,"object_z_max":0.2761,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":127.69995,"subtask_id":"insert","tcp_end":[0.58979,-0.02152,0.30918],"tcp_start":[0.58983,-0.02119,0.30908],"tcp_to_object_dist_end":0.04013,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```