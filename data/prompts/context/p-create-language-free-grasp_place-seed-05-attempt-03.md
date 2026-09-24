## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1097 | 0.23 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2087 | 0.26 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2041 | 0.33 | ✅ accepted |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1995 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.110) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.06
  weight: 0.3
- id: reach_place
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.06
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_depth:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_place
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.06], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_depth: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.110
- **task_score** (E): 0.226
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1337 |
| descend_1 | 1.00 | 1.00 | 0.1312 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 0.33 | 1.00 | 0.1611 |
| transport_1 | 0.33 | 1.00 | 0.1069 |
| descend_place | 0.33 | 1.00 | 0.0888 |
| release_1 | 1.00 | 1.00 | 0.0224 |
| retract_1 | 1.00 | 1.00 | 0.0862 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.172) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.016, 0.172)→(0.511, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, 0.018, 0.040)→(0.503, 0.018, 0.032) | (0.516, 0.018, 0.026)→(0.515, 0.018, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.139 | 0.196 |
| lift_1 | lift | 0.33 / step_budget | (0.503, 0.018, 0.032)→(0.509, 0.018, 0.193) | (0.515, 0.018, 0.026)→(0.518, 0.018, 0.170) | 0.237→0.195 | 1.00 / 16.333 | 0.148 | 0.582 |
| transport_1 | approach | 0.33 / step_budget | (0.509, 0.018, 0.193)→(0.539, 0.072, 0.266) | (0.518, 0.018, 0.170)→(0.511, 0.027, 0.016) | 0.195→0.238 | 1.00 / 8.000 | 3249.686 | 1.815 |
| descend_place | descend | 0.33 / step_budget | (0.539, 0.072, 0.266)→(0.570, 0.125, 0.217) | (0.511, 0.027, 0.016)→(0.511, 0.027, 0.016) | 0.238→0.238 | 1.00 / 8.667 | 182003.997 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.570, 0.125, 0.217)→(0.566, 0.124, 0.238) | (0.511, 0.027, 0.016)→(0.511, 0.027, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.566, 0.124, 0.238)→(0.563, 0.123, 0.325) | (0.511, 0.027, 0.016)→(0.511, 0.027, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.311
- phase_score: 0.383
- phase_breakdown.reach_grasp_score: 0.369
- phase_breakdown.reach_place_score: 0.389
- grasp_place_fitness: 0.633

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.633
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.311
- **Median Q (composite search score)**: 0.123
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.411


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00641,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15216,"descend_1.descend_depth":0.01756,"descend_place.place_depth":0.04778,"lift_1.lift_height":0.22737,"transport_1.transport_arc_height":0.16347,"transport_1.transport_speed":0.14967},"optimized_scores":{"best_composite_score":0.1529,"best_fitness_score":0.6329,"best_task_score":0.31125},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3504.0,"contact_point_centroid":[0.5314,0.04724,-0.00229],"force_p95":0.12438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88524,"mean_force":0.1356,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55008,0.08572,0.23759]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.52821,0.02925,-0.00117],"force_p95":0.44748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58947,"mean_force":0.07697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51575,0.02973,0.03291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13309.0,"contact_point_centroid":[0.52068,0.01084,0.09947],"force_p95":0.12295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3137,"mean_force":0.07453,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5173,0.02956,0.09836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13740.0,"contact_point_centroid":[0.52038,0.04834,0.09781],"force_p95":0.12569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31007,"mean_force":0.0732,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51723,0.02956,0.0967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.52841,0.013,0.18941],"force_p95":0.21144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2446,"mean_force":0.15337,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52339,0.03101,0.19449]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.03057,-0.00209],"force_p95":0.14818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21717,"mean_force":0.12952,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51841,0.02992,0.03252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":359.0,"contact_point_centroid":[0.52807,0.04876,0.19006],"force_p95":0.14393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19885,"mean_force":0.09246,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52342,0.03157,0.19522]},{"body_a":"world","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51074,0.01333,0.24399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4083.0,"contact_point_centroid":[0.5178,0.01064,0.03392],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1369,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51719,0.02984,0.03114]},{"body_a":"world","body_b":"grasp_target","contact_count":3776.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52347,0.02907,0.10056]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53136,0.04724,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5874,0.15936,0.19265]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53136,0.04724,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59135,0.173,0.15573]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.53136,0.04724,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58672,0.17146,0.21601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.51779,0.04896,0.03295],"force_p95":0.07145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08381,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51719,0.02984,0.03114]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3509.0,"contact_point_centroid":[0.55207,0.08864,0.24178],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55163,0.08863,0.23949]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4252.0,"contact_point_centroid":[0.58785,0.15933,0.19505],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58737,0.15931,0.19279]}],"total_contact_groups":17},"final_pose_error":0.01502,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53136,0.04724,0.01602],"final_tcp_position":[0.58697,0.17149,0.26068],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.88524,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1540.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52387,0.02738,0.18851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3776.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52536,0.03039,0.04044],"tcp_start":[0.52387,0.02738,0.18851],"tcp_to_object_dist_end":0.01532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02983,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18433,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14279,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10831.0,"raw_peak_contact_force":0.21717,"tcp_end":[0.51716,0.02984,0.03111],"tcp_start":[0.52536,0.03039,0.04044],"tcp_to_object_dist_end":0.01429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53304,0.02975,0.16983],"object_pos_start":[0.53039,0.02983,0.0257],"object_to_goal_dist_end":0.17508,"object_to_goal_dist_start":0.18433,"object_z_max":0.16965,"peak_contact_force":0.13651,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27193.0,"raw_peak_contact_force":0.58947,"tcp_end":[0.52339,0.02958,0.19225],"tcp_start":[0.51716,0.02984,0.03111],"tcp_to_object_dist_end":0.02442,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53136,0.04724,0.01602],"object_pos_start":[0.53304,0.02975,0.16983],"object_to_goal_dist_end":0.17508,"object_to_goal_dist_start":0.17508,"object_z_max":0.17257,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7573.0,"raw_peak_contact_force":1.88524,"tcp_end":[0.58036,0.14234,0.24407],"tcp_start":[0.52339,0.02958,0.19225],"tcp_to_object_dist_end":0.2519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53136,0.04724,0.01602],"object_pos_start":[0.53136,0.04724,0.01602],"object_to_goal_dist_end":0.17508,"object_to_goal_dist_start":0.17508,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8252.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.59568,0.17436,0.15481],"tcp_start":[0.58036,0.14234,0.24407],"tcp_to_object_dist_end":0.19889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53136,0.04724,0.01602],"object_pos_start":[0.53136,0.04724,0.01602],"object_to_goal_dist_end":0.17508,"object_to_goal_dist_start":0.17508,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58968,0.17243,0.17542],"tcp_start":[0.59568,0.17436,0.15481],"tcp_to_object_dist_end":0.21092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.53136,0.04724,0.01602],"object_pos_start":[0.53136,0.04724,0.01602],"object_to_goal_dist_end":0.17508,"object_to_goal_dist_start":0.17508,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58697,0.17149,0.26068],"tcp_start":[0.58968,0.17243,0.17542],"tcp_to_object_dist_end":0.27998,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7907,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07343,"descend_1.descend_depth":0.01299,"descend_place.place_depth":0.0321,"lift_1.lift_height":0.24825,"transport_1.transport_arc_height":0.08447,"transport_1.transport_speed":0.05272},"optimized_scores":{"best_composite_score":0.05302,"best_fitness_score":0.53302,"best_task_score":0.10728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3448.0,"contact_point_centroid":[0.48806,-0.03266,-0.00229],"force_p95":0.1247,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82919,"mean_force":0.13625,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49346,-0.01354,0.24167]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.50119,-0.01535,-0.00109],"force_p95":0.46038,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63614,"mean_force":0.07376,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48957,-0.01545,0.02935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13692.0,"contact_point_centroid":[0.49363,0.0034,0.0977],"force_p95":0.12756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32267,"mean_force":0.0737,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49067,-0.01536,0.09672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14172.0,"contact_point_centroid":[0.4937,-0.03409,0.09586],"force_p95":0.1251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29466,"mean_force":0.07175,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4906,-0.01536,0.09511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":345.0,"contact_point_centroid":[0.49802,0.00229,0.18603],"force_p95":0.21524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29394,"mean_force":0.1238,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49455,-0.0157,0.19123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":498.0,"contact_point_centroid":[0.49759,-0.03318,0.18693],"force_p95":0.16446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28368,"mean_force":0.10722,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49412,-0.01587,0.19214]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01555,-0.00202],"force_p95":0.13059,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15365,"mean_force":0.12502,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49209,-0.01548,0.02887]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49876,-0.00712,0.20585]},{"body_a":"world","body_b":"grasp_target","contact_count":2272.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49774,-0.0151,0.06623]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48797,-0.0327,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51354,0.03473,0.27367]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48797,-0.0327,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52789,0.07167,0.27601]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.48797,-0.0327,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52504,0.07119,0.3387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.49135,0.00374,0.0304],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11271,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49091,-0.01547,0.02763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.49142,-0.03454,0.02947],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08884,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49091,-0.01547,0.02763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3430.0,"contact_point_centroid":[0.49389,-0.01327,0.24649],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4936,-0.01327,0.24422]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4260.0,"contact_point_centroid":[0.51393,0.03489,0.27586],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.51361,0.03488,0.27367]}],"total_contact_groups":17},"final_pose_error":0.01287,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48797,-0.0327,0.01602],"final_tcp_position":[0.52538,0.07121,0.38376],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.02905,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49956,-0.01449,0.11216],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2272.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49881,-0.01557,0.03599],"tcp_start":[0.49956,-0.01449,0.11216],"tcp_to_object_dist_end":0.01115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01532,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31213,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12872,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15365,"tcp_end":[0.49088,-0.01547,0.0276],"tcp_start":[0.49881,-0.01557,0.03599],"tcp_to_object_dist_end":0.01291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50737,-0.01528,0.16776],"object_pos_start":[0.50368,-0.01532,0.02589],"object_to_goal_dist_end":0.23213,"object_to_goal_dist_start":0.31213,"object_z_max":0.1676,"peak_contact_force":0.15479,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27996.0,"raw_peak_contact_force":0.63614,"tcp_end":[0.49586,-0.0153,0.18927],"tcp_start":[0.49088,-0.01547,0.0276],"tcp_to_object_dist_end":0.02439,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48797,-0.0327,0.01602],"object_pos_start":[0.50737,-0.01528,0.16776],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.23213,"object_z_max":0.16985,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7721.0,"raw_peak_contact_force":1.82919,"tcp_end":[0.49804,-0.00427,0.27923],"tcp_start":[0.49586,-0.0153,0.18927],"tcp_to_object_dist_end":0.26494,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48797,-0.0327,0.01602],"object_pos_start":[0.48797,-0.0327,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":273006.02905,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8260.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.53076,0.07202,0.27317],"tcp_start":[0.49804,-0.00427,0.27923],"tcp_to_object_dist_end":0.28094,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48797,-0.0327,0.01602],"object_pos_start":[0.48797,-0.0327,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52688,0.07148,0.29654],"tcp_start":[0.53076,0.07202,0.27317],"tcp_to_object_dist_end":0.30176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.48797,-0.0327,0.01602],"object_pos_start":[0.48797,-0.0327,0.01602],"object_to_goal_dist_end":0.33485,"object_to_goal_dist_start":0.33485,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52538,0.07121,0.38376],"tcp_start":[0.52688,0.07148,0.29654],"tcp_to_object_dist_end":0.38396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88462,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17746,"descend_1.descend_depth":0.0205,"descend_place.place_depth":0.04892,"lift_1.lift_height":0.21596,"transport_1.transport_arc_height":0.15026,"transport_1.transport_speed":0.08668},"optimized_scores":{"best_composite_score":0.12308,"best_fitness_score":0.60308,"best_task_score":0.25823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3422.0,"contact_point_centroid":[0.51319,0.06523,-0.00232],"force_p95":0.12596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72935,"mean_force":0.13586,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51938,0.0559,0.24657]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.51032,0.03788,-0.00118],"force_p95":0.35766,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52058,"mean_force":0.06681,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49821,0.03841,0.0378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13642.0,"contact_point_centroid":[0.50329,0.0195,0.10422],"force_p95":0.12017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30726,"mean_force":0.07241,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50001,0.03824,0.10288]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13998.0,"contact_point_centroid":[0.50303,0.05705,0.10304],"force_p95":0.11794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30395,"mean_force":0.07154,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49996,0.03824,0.10171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":354.0,"contact_point_centroid":[0.51111,0.02083,0.19389],"force_p95":0.21689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2663,"mean_force":0.13295,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5055,0.03862,0.19874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.5107,0.05628,0.19438],"force_p95":0.21147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2636,"mean_force":0.12498,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50533,0.03875,0.19968]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03951,-0.0021],"force_p95":0.15256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21816,"mean_force":0.1306,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50076,0.03864,0.03728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.50005,0.01934,0.03879],"force_p95":0.07976,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1443,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03855,0.03598]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50289,0.01651,0.25697]},{"body_a":"world","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50629,0.03678,0.12259]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51317,0.06521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56117,0.10364,0.24508]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51317,0.06521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58127,0.12844,0.22358]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.51317,0.06521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57769,0.12746,0.28451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4968.0,"contact_point_centroid":[0.50007,0.05768,0.0378],"force_p95":0.07244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08082,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03855,0.03599]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3425.0,"contact_point_centroid":[0.5207,0.05684,0.25092],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01592,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52023,0.05682,0.24866]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4298.0,"contact_point_centroid":[0.56166,0.10368,0.24733],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56119,0.10366,0.24506]}],"total_contact_groups":17},"final_pose_error":0.01417,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51317,0.06521,0.01602],"final_tcp_position":[0.57803,0.1275,0.32946],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273005.84078,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50768,0.03424,0.21403],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":903.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3612.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50751,0.0392,0.04472],"tcp_start":[0.50768,0.03424,0.21403],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03863,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21315,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14656,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10849.0,"raw_peak_contact_force":0.21816,"tcp_end":[0.49955,0.03854,0.03595],"tcp_start":[0.50751,0.0392,0.04472],"tcp_to_object_dist_end":0.01649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51503,0.03878,0.17192],"object_pos_start":[0.51243,0.03863,0.02564],"object_to_goal_dist_end":0.17685,"object_to_goal_dist_start":0.21315,"object_z_max":0.17174,"peak_contact_force":0.1515,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27782.0,"raw_peak_contact_force":0.52058,"tcp_end":[0.50629,0.03832,0.19621],"tcp_start":[0.49955,0.03854,0.03595],"tcp_to_object_dist_end":0.02582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51317,0.06521,0.01602],"object_pos_start":[0.51503,0.03878,0.17192],"object_to_goal_dist_end":0.20309,"object_to_goal_dist_start":0.17685,"object_z_max":0.17608,"peak_contact_force":9748.81277,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7637.0,"raw_peak_contact_force":1.72935,"tcp_end":[0.53896,0.07719,0.27483],"tcp_start":[0.50629,0.03832,0.19621],"tcp_to_object_dist_end":0.26036,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51317,0.06521,0.01602],"object_pos_start":[0.51317,0.06521,0.01602],"object_to_goal_dist_end":0.20309,"object_to_goal_dist_start":0.20309,"object_z_max":0.01602,"peak_contact_force":273005.84078,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8298.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place","tcp_end":[0.58477,0.12927,0.2222],"tcp_start":[0.53896,0.07719,0.27483],"tcp_to_object_dist_end":0.22747,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51317,0.06521,0.01602],"object_pos_start":[0.51317,0.06521,0.01602],"object_to_goal_dist_end":0.20309,"object_to_goal_dist_start":0.20309,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57998,0.12807,0.24348],"tcp_start":[0.58477,0.12927,0.2222],"tcp_to_object_dist_end":0.24526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.51317,0.06521,0.01602],"object_pos_start":[0.51317,0.06521,0.01602],"object_to_goal_dist_end":0.20309,"object_to_goal_dist_start":0.20309,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57803,0.1275,0.32946],"tcp_start":[0.57998,0.12807,0.24348],"tcp_to_object_dist_end":0.32609,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```