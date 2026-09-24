## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1264 | 0.85 | ❌ rejected |
| 12 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0203 | 0.85 | ❌ rejected |
| 11 | approach → align → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1344 | 0.85 | ❌ rejected |
| 10 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1234 | 0.85 | ✅ accepted |
| 9 | approach → approach → approach → contact → insert | impedance_motion | impedance_motion | impedance_motion | linear_cartesian | impedance_motion | impedance_control | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.0261 | 0.85 | ❌ rejected |

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

## Current Skill (Q=0.126) — your mutation base

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

- **Composite score**: 0.126
- **task_score** (E): 0.854
- **fitness_score**: 0.366  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| pre_align | 0.00 | 1.00 | 0.1367 |
| align_1 | 0.00 | 1.00 | 0.0001 |
| approach_1 | 0.00 | 1.00 | 0.1073 |
| contact_1 | 1.00 | 1.00 | 0.0008 |
| insert_1 | 0.00 | 0.67 | 0.0010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_align | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.466, 0.004, 0.169) | (0.504, -0.000, 0.340)→(0.503, 0.003, 0.152) | 0.260→0.073 | 1.00 / 1.000 | 292.865 | 1282.883 |
| align_1 | approach | 0.00 / guard_failure | (0.466, 0.004, 0.169)→(0.466, 0.004, 0.169) | (0.503, 0.003, 0.152)→(0.503, 0.003, 0.152) | 0.073→0.073 | 1.00 / 1.000 | 289.402 | 303.861 |
| approach_1 | approach | 0.00 / step_budget | (0.466, 0.004, 0.169)→(0.528, -0.008, 0.253) | (0.503, 0.003, 0.152)→(0.549, -0.014, 0.221) | 0.073→0.153 | 1.00 / 1.000 | 263.376 | 571.651 |
| contact_1 | contact | 1.00 / force_exceeded | (0.528, -0.008, 0.253)→(0.528, -0.009, 0.254) | (0.549, -0.014, 0.221)→(0.549, -0.015, 0.222) | 0.153→0.153 | 1.00 / 1.000 | 471.303 | 471.303 |
| insert_1 | insert | 0.00 / guard_failure | (0.528, -0.009, 0.254)→(0.528, -0.010, 0.254) | (0.549, -0.015, 0.222)→(0.549, -0.015, 0.222) | 0.153→0.154 | 0.67 / 0.667 | 428.141 | 237.527 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.862
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.862
- phase_score: 0.052
- phase_breakdown.approach_score: 0.038
- phase_breakdown.align_score: 0.004
- phase_breakdown.insert_score: 0.066
- phase_breakdown.contact_score: 0.055

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.376
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.869
- **Median Q (composite search score)**: 0.123
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.430


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.86667,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03503,"approach_1.approach_speed":0.00626,"contact_1.contact_force":9.05436,"contact_1.contact_speed":0.0401,"insert_1.insert_speed":0.02505,"insert_1.insertion_depth":0.02843,"pre_align.pre_align_speed":0.08593},"optimized_scores":{"best_composite_score":0.12051,"best_fitness_score":0.36051,"best_task_score":0.83144},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":599.0,"contact_point_centroid":[0.52656,-0.01099,0.0673],"force_p95":316.2568,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1145.60977,"mean_force":294.50231,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45292,-0.00692,0.10968]},{"body_a":"peg_socket","body_b":"link7","contact_count":781.0,"contact_point_centroid":[0.52678,-0.04949,0.07261],"force_p95":612.47935,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":832.94661,"mean_force":393.44479,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46812,0.02112,0.11762]},{"body_a":"peg_socket","body_b":"link6","contact_count":64.0,"contact_point_centroid":[0.52617,-0.08056,0.07957],"force_p95":673.07317,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":760.8716,"mean_force":333.5436,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53997,-0.01331,0.25303]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52666,-0.08087,0.07988],"force_p95":600.48405,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":600.48405,"mean_force":600.48405,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5381,-0.03236,0.26257]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.44208,0.00917,0.07988],"force_p95":576.6529,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":581.94399,"mean_force":369.12619,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44009,-0.00388,0.08633]},{"body_a":"attachment","body_b":"peg_socket","contact_count":531.0,"contact_point_centroid":[0.52684,0.00257,0.07997],"force_p95":360.49449,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":569.10151,"mean_force":177.4653,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46636,0.01721,0.11795]},{"body_a":"world","body_b":"link6","contact_count":566.0,"contact_point_centroid":[0.67416,-0.0374,-8e-05],"force_p95":356.8698,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":563.93023,"mean_force":217.13367,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4761,0.03071,0.12353]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52679,-0.01278,0.06378],"force_p95":325.68741,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.91241,"mean_force":323.66242,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.45916,-0.00735,0.11647]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.52673,-0.08094,0.07993],"force_p95":149.60101,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.21009,"mean_force":81.11928,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53821,-0.03306,0.26281]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.43564,0.00644,0.07976],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.43325,-0.00678,0.08625]}],"total_contact_groups":10},"final_pose_error":0.22825,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.53858,-0.03397,0.26288],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1145.60977,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49738,-0.00862,0.10476],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02635,"object_to_goal_dist_start":0.26034,"object_z_max":0.34429,"peak_contact_force":318.71691,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":618.0,"raw_peak_contact_force":1145.60977,"subtask_id":"align","tcp_end":[0.45916,-0.00737,0.11647],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.4974,-0.00859,0.10476],"object_pos_start":[0.49738,-0.00862,0.10476],"object_to_goal_dist_end":0.02634,"object_to_goal_dist_start":0.02635,"object_z_max":0.10476,"peak_contact_force":321.41243,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":325.91241,"subtask_id":"align","tcp_end":[0.4592,-0.00732,0.11649],"tcp_start":[0.45917,-0.00732,0.11648],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55332,-0.04042,0.22646],"object_pos_start":[0.49742,-0.0086,0.10476],"object_to_goal_dist_end":0.16102,"object_to_goal_dist_start":0.02634,"object_z_max":0.22634,"peak_contact_force":275.1109,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1942.0,"raw_peak_contact_force":832.94661,"subtask_id":"approach","tcp_end":[0.5381,-0.03236,0.26257],"tcp_start":[0.4592,-0.00732,0.11649],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55336,-0.04081,0.22667],"object_pos_start":[0.55332,-0.04042,0.22646],"object_to_goal_dist_end":0.16132,"object_to_goal_dist_start":0.16102,"object_z_max":0.22646,"peak_contact_force":600.48405,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":600.48405,"subtask_id":"contact","tcp_end":[0.53814,-0.03281,0.26279],"tcp_start":[0.5381,-0.03236,0.26257],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55386,-0.04188,0.22677],"object_pos_start":[0.55336,-0.04081,0.22667],"object_to_goal_dist_end":0.16185,"object_to_goal_dist_start":0.16132,"object_z_max":0.22671,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":157.21009,"subtask_id":"insert","tcp_end":[0.53858,-0.03397,0.26288],"tcp_start":[0.53814,-0.03281,0.26279],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.11594,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03085,"approach_1.approach_speed":0.03119,"contact_1.contact_force":11.77164,"contact_1.contact_speed":0.03421,"insert_1.insert_speed":0.02387,"insert_1.insertion_depth":0.02455,"pre_align.pre_align_speed":0.09967},"optimized_scores":{"best_composite_score":0.12258,"best_fitness_score":0.36258,"best_task_score":0.86857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.56829,0.0017,0.07934],"force_p95":798.43383,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":895.61755,"mean_force":318.68983,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44599,-9e-05,0.11001]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.47552,5e-05,0.07981],"force_p95":826.29397,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.772,"mean_force":781.79069,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.4659,6e-05,0.09196]},{"body_a":"peg_socket","body_b":"link6","contact_count":453.0,"contact_point_centroid":[0.59535,-0.00295,0.07983],"force_p95":276.64193,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":430.80382,"mean_force":239.0492,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45866,0.00013,0.17407]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59541,-0.00272,0.07996],"force_p95":325.7753,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.05797,"mean_force":305.23136,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48145,0.00192,0.22478]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59535,-0.00269,0.07987],"force_p95":316.42803,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.42803,"mean_force":316.42803,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48128,0.00195,0.22475]},{"body_a":"peg_socket","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.59537,-0.0031,0.07986],"force_p95":272.05923,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.34154,"mean_force":235.56013,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46227,0.00096,0.20001]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59532,-0.00277,0.07979],"force_p95":288.42685,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.50515,"mean_force":287.72214,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.47462,0.00064,0.20168]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.54387,-0.02924,0.0791],"force_p95":14.36238,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.03537,"mean_force":2.9311,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.44714,-0.0001,0.09991]}],"total_contact_groups":8},"final_pose_error":0.18247,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.48106,0.00196,0.22463],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1045.47846,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50904,0.00063,0.18132],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10172,"object_to_goal_dist_start":0.26034,"object_z_max":0.34481,"peak_contact_force":292.80682,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":497.0,"raw_peak_contact_force":895.61755,"subtask_id":"align","tcp_end":[0.47458,0.00064,0.20163],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.5091,0.00064,0.18139],"object_pos_start":[0.50904,0.00063,0.18132],"object_to_goal_dist_end":0.10179,"object_to_goal_dist_start":0.10172,"object_z_max":0.18139,"peak_contact_force":286.93913,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":288.50515,"subtask_id":"align","tcp_end":[0.47473,0.00064,0.20182],"tcp_start":[0.47466,0.00064,0.20173],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51301,0.00173,0.20011],"object_pos_start":[0.50916,0.00064,0.18145],"object_to_goal_dist_end":0.12082,"object_to_goal_dist_start":0.10187,"object_z_max":0.20133,"peak_contact_force":244.64464,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":991.0,"raw_peak_contact_force":295.34154,"subtask_id":"approach","tcp_end":[0.48152,0.00191,0.22477],"tcp_start":[0.47473,0.00064,0.20182],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51276,0.00177,0.20007],"object_pos_start":[0.51301,0.00173,0.20011],"object_to_goal_dist_end":0.12076,"object_to_goal_dist_start":0.12082,"object_z_max":0.20015,"peak_contact_force":328.05797,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":328.05797,"subtask_id":"contact","tcp_end":[0.48128,0.00195,0.22475],"tcp_start":[0.48152,0.00191,0.22477],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51256,0.00178,0.19996],"object_pos_start":[0.51276,0.00177,0.20007],"object_to_goal_dist_end":0.12063,"object_to_goal_dist_start":0.12076,"object_z_max":0.20007,"peak_contact_force":1045.47846,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":316.42803,"subtask_id":"insert","tcp_end":[0.48106,0.00196,0.22463],"tcp_start":[0.48128,0.00195,0.22475],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.93846,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04153,"approach_1.approach_speed":0.04015,"contact_1.contact_force":6.8012,"contact_1.contact_speed":0.02073,"insert_1.insert_speed":0.01893,"insert_1.insertion_depth":0.01928,"pre_align.pre_align_speed":0.09982},"optimized_scores":{"best_composite_score":0.13613,"best_fitness_score":0.37613,"best_task_score":0.8621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":435.0,"contact_point_centroid":[0.5843,0.00928,0.07955],"force_p95":831.95709,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1807.4227,"mean_force":336.67593,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45862,0.01063,0.16038]},{"body_a":"peg_socket","body_b":"link7","contact_count":217.0,"contact_point_centroid":[0.57965,0.01102,0.07964],"force_p95":1436.022,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1782.41529,"mean_force":392.17807,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45913,0.00646,0.14277]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46606,0.0042,0.07864],"force_p95":1044.96185,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1085.90073,"mean_force":273.55273,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45861,0.0042,0.0906]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.55235,-0.00558,0.07862],"force_p95":818.76711,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.90185,"mean_force":313.45067,"phase_index":0.0,"phase_name":"pre_align","phase_type":"approach","tcp_position_centroid":[0.45557,0.00481,0.09974]},{"body_a":"peg_socket","body_b":"link6","contact_count":962.0,"contact_point_centroid":[0.58429,0.01969,0.07984],"force_p95":332.35207,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":586.66393,"mean_force":261.94847,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46845,0.03284,0.19761]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5842,-0.03507,0.07982],"force_p95":485.36758,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":485.36758,"mean_force":485.36758,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.563,0.00528,0.27294]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.58437,0.01515,0.07995],"force_p95":295.29915,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.16469,"mean_force":278.50927,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.46531,0.01783,0.18772]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58422,-0.0351,0.07985],"force_p95":238.94425,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.94425,"mean_force":238.94425,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.56374,0.00404,0.27344]}],"total_contact_groups":8},"final_pose_error":0.22291,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.5645,0.00266,0.27389],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1807.4227,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.50115,0.01777,0.16997],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09172,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":267.07117,"phase_name":"pre_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":685.0,"raw_peak_contact_force":1807.4227,"subtask_id":"align","tcp_end":[0.46528,0.01781,0.18766],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50121,0.01781,0.17006],"object_pos_start":[0.50115,0.01777,0.16997],"object_to_goal_dist_end":0.09181,"object_to_goal_dist_start":0.09172,"object_z_max":0.17006,"peak_contact_force":259.85385,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":297.16469,"subtask_id":"align","tcp_end":[0.4654,0.01792,0.18786],"tcp_start":[0.46534,0.01784,0.18777],"tcp_to_object_dist_end":0.03999,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58013,-0.00354,0.23788],"object_pos_start":[0.50125,0.01789,0.17014],"object_to_goal_dist_end":0.17709,"object_to_goal_dist_start":0.0919,"object_z_max":0.23757,"peak_contact_force":270.3722,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":962.0,"raw_peak_contact_force":586.66393,"subtask_id":"approach","tcp_end":[0.563,0.00528,0.27294],"tcp_start":[0.4654,0.01792,0.18786],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58072,-0.00469,0.23829],"object_pos_start":[0.58013,-0.00354,0.23788],"object_to_goal_dist_end":0.17774,"object_to_goal_dist_start":0.17709,"object_z_max":0.23788,"peak_contact_force":485.36758,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":485.36758,"subtask_id":"contact","tcp_end":[0.56374,0.00404,0.27344],"tcp_start":[0.563,0.00528,0.27294],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58138,-0.00596,0.23867],"object_pos_start":[0.58072,-0.00469,0.23829],"object_to_goal_dist_end":0.17842,"object_to_goal_dist_start":0.17774,"object_z_max":0.23829,"peak_contact_force":238.94425,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":238.94425,"subtask_id":"insert","tcp_end":[0.5645,0.00266,0.27389],"tcp_start":[0.56374,0.00404,0.27344],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```