## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1799 | 0.19 | ❌ rejected |
| 12 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2474 | 0.32 | ❌ rejected |
| 11 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3875 | 0.52 | ❌ rejected |
| 10 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3133 | 0.25 | ❌ rejected |
| 9 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6395 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.180) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_clear
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: place
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.5
phases:
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_grasp
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
  guards:
  - id: bilateral_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_clear
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_retained
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retained, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.180
- **task_score** (E): 0.191
- **fitness_score**: 0.570  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2633 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 1.00 | 0.1045 |
| transport_1 | 0.67 | 1.00 | 0.0029 |
| descend_2 | 1.00 | 1.00 | 0.0591 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.042) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.042)→(0.508, -0.001, 0.032) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.289 | 1.00 / 43.333 | 0.168 | 0.253 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.032)→(0.504, -0.001, 0.137) | (0.522, -0.001, 0.025)→(0.519, -0.001, 0.120) | 0.289→0.243 | 1.00 / 21.667 | 15.856 | 0.611 |
| transport_1 | approach | 0.67 / step_budget | (0.599, 0.192, 0.320)→(0.600, 0.194, 0.318) | (0.519, -0.001, 0.120)→(0.554, 0.076, 0.016) | 0.243→0.251 | 1.00 / 8.333 | 3249.685 | 2.093 |
| descend_2 | descend | 1.00 / step_budget | (0.600, 0.194, 0.318)→(0.604, 0.203, 0.260) | (0.554, 0.076, 0.016)→(0.554, 0.076, 0.016) | 0.251→0.251 | 1.00 / 8.333 | 3249.723 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.238
- phase_score: 0.576
- phase_breakdown.pre_grasp_score: 0.186
- phase_breakdown.lift_clear_score: 0.723
- phase_breakdown.place_score: 0.643
- grasp_place_fitness: 0.592

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.592
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.238
- **Median Q (composite search score)**: 0.180
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.413


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23938,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00741,"descend_2.place_z_offset":0.00054,"lift_1.lift_height":0.11882,"transport_1.approach_height":0.10129,"transport_1.arc_height":0.07289,"transport_1.transport_speed":0.04042},"optimized_scores":{"best_composite_score":0.20194,"best_fitness_score":0.59194,"best_task_score":0.23818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.57514,0.21263,-0.00576],"force_p95":1.23082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39534,"mean_force":0.27546,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56613,0.20556,0.32702]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.47969,0.04389,-0.0014],"force_p95":0.34918,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56551,"mean_force":0.07764,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46995,0.04497,0.04026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8086.0,"contact_point_centroid":[0.4892,0.05588,0.23814],"force_p95":0.15034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35041,"mean_force":0.09348,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48374,0.07432,0.23789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11275.0,"contact_point_centroid":[0.46956,0.06367,0.08671],"force_p95":0.10064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31798,"mean_force":0.06135,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46763,0.04476,0.08502]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48282,0.04838,-0.00231],"force_p95":0.20676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27542,"mean_force":0.14484,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47263,0.04524,0.03919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10400.0,"contact_point_centroid":[0.46972,0.02576,0.08865],"force_p95":0.10552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25863,"mean_force":0.06469,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46766,0.04476,0.0865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8483.0,"contact_point_centroid":[0.49049,0.0947,0.24074],"force_p95":0.1334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1928,"mean_force":0.08931,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48501,0.07631,0.24066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5223.0,"contact_point_centroid":[0.47091,0.02586,0.03952],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15755,"mean_force":0.04142,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47153,0.04513,0.03806]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48857,0.02279,0.17165]},{"body_a":"world","body_b":"grasp_target","contact_count":924.0,"contact_point_centroid":[0.57521,0.21226,-0.00199],"force_p95":0.12503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13183,"mean_force":0.12301,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57419,0.22008,0.28191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5641.0,"contact_point_centroid":[0.47089,0.06466,0.03919],"force_p95":0.07615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0818,"mean_force":0.04131,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47154,0.04513,0.03807]},{"body_a":"left_finger","body_b":"right_finger","contact_count":333.0,"contact_point_centroid":[0.56871,0.20902,0.32886],"force_p95":0.01421,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01116,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56819,0.209,0.32652]},{"body_a":"left_finger","body_b":"right_finger","contact_count":994.0,"contact_point_centroid":[0.57462,0.2201,0.28429],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01037,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57418,0.22007,0.28204]}],"total_contact_groups":13},"final_pose_error":0.0098,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57521,0.21226,0.01602],"final_tcp_position":[0.57761,0.22538,0.23913],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.81073,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47928,0.04581,0.04609],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48269,0.04604,0.02494],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29242,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19496,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12664.0,"raw_peak_contact_force":0.27542,"tcp_end":[0.4715,0.04513,0.03803],"tcp_start":[0.47928,0.04581,0.04609],"tcp_to_object_dist_end":0.01725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.481,0.04526,0.12471],"object_pos_start":[0.48269,0.04604,0.02494],"object_to_goal_dist_end":0.23467,"object_to_goal_dist_start":0.29242,"object_z_max":0.1246,"peak_contact_force":0.10051,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21821.0,"raw_peak_contact_force":0.56551,"subtask_id":"lift_clear","tcp_end":[0.46771,0.04478,0.14533],"tcp_start":[0.4715,0.04513,0.03803],"tcp_to_object_dist_end":0.02454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1040.0,"n_steps_budget":1000.0,"object_pos_end":[0.57529,0.21097,0.01622],"object_pos_start":[0.481,0.04526,0.12471],"object_to_goal_dist_end":0.21511,"object_to_goal_dist_start":0.23467,"object_z_max":0.29406,"peak_contact_force":9748.81073,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17314.0,"raw_peak_contact_force":2.39534,"tcp_end":[0.57199,0.21564,0.32406],"tcp_start":[0.57086,0.2134,0.32548],"tcp_to_object_dist_end":0.3079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.57521,0.21226,0.01602],"object_pos_start":[0.57521,0.21251,0.01637],"object_to_goal_dist_end":0.21521,"object_to_goal_dist_start":0.21484,"object_z_max":0.01637,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1918.0,"raw_peak_contact_force":0.13183,"subtask_id":"place","tcp_end":[0.57761,0.22538,0.23913],"tcp_start":[0.57199,0.21564,0.32406],"tcp_to_object_dist_end":0.22351,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48571,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.0012,"descend_2.place_z_offset":0.0631,"lift_1.lift_height":0.11228,"transport_1.approach_height":0.13454,"transport_1.arc_height":0.05009,"transport_1.transport_speed":0.04514},"optimized_scores":{"best_composite_score":0.15764,"best_fitness_score":0.54764,"best_task_score":0.14389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.53859,0.02092,-0.00238],"force_p95":0.12617,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95502,"mean_force":0.13949,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5696,0.12441,0.29713]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53386,-0.01916,-0.00119],"force_p95":0.46173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64421,"mean_force":0.09147,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52024,-0.02004,0.0305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8200.0,"contact_point_centroid":[0.52152,-0.00119,0.07496],"force_p95":0.11209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33547,"mean_force":0.07757,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51766,-0.01998,0.07277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3819.0,"contact_point_centroid":[0.52621,-0.01838,0.16635],"force_p95":0.14395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32847,"mean_force":0.09309,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52205,-0.00023,0.16898]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8924.0,"contact_point_centroid":[0.52146,-0.03868,0.0735],"force_p95":0.1072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31757,"mean_force":0.07259,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51767,-0.01999,0.07185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3354.0,"contact_point_centroid":[0.52631,0.01836,0.16735],"force_p95":0.16377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24537,"mean_force":0.10083,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52212,5e-05,0.16977]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02105,-0.00212],"force_p95":0.15706,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23569,"mean_force":0.13174,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52314,-0.0201,0.0301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4068.0,"contact_point_centroid":[0.52314,-0.00087,0.03141],"force_p95":0.07991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14203,"mean_force":0.05191,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52191,-0.02008,0.02872]},{"body_a":"world","body_b":"grasp_target","contact_count":3356.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01007,0.16764]},{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.53848,0.02093,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60426,0.21748,0.30825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.52306,-0.03921,0.03053],"force_p95":0.0723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.04467,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52192,-0.02008,0.02872]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2939.0,"contact_point_centroid":[0.57188,0.12951,0.30316],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01051,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57155,0.1295,0.30084]},{"body_a":"left_finger","body_b":"right_finger","contact_count":691.0,"contact_point_centroid":[0.60481,0.21748,0.31061],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01045,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60424,0.21745,0.30843]}],"total_contact_groups":13},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53848,0.02093,0.01602],"final_tcp_position":[0.60651,0.22314,0.27822],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.95502,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3356.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.5304,-0.02019,0.03844],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02009,0.02561],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31601,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14995,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10852.0,"raw_peak_contact_force":0.23569,"tcp_end":[0.52188,-0.02007,0.02868],"tcp_start":[0.5304,-0.02019,0.03844],"tcp_to_object_dist_end":0.01534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53403,-0.02003,0.1146],"object_pos_start":[0.53692,-0.02009,0.02561],"object_to_goal_dist_end":0.27537,"object_to_goal_dist_start":0.31601,"object_z_max":0.11449,"peak_contact_force":0.11386,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17270.0,"raw_peak_contact_force":0.64421,"subtask_id":"lift_clear","tcp_end":[0.51772,-0.01998,0.1286],"tcp_start":[0.52188,-0.02007,0.02868],"tcp_to_object_dist_end":0.0215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1185.0,"n_steps_budget":1000.0,"object_pos_end":[0.53848,0.02093,0.01602],"object_pos_start":[0.53403,-0.02003,0.1146],"object_to_goal_dist_end":0.2908,"object_to_goal_dist_start":0.27537,"object_z_max":0.18978,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13036.0,"raw_peak_contact_force":1.95502,"tcp_end":[0.60293,0.21269,0.33767],"tcp_start":[0.60248,0.20981,0.34023],"tcp_to_object_dist_end":0.37998,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.53848,0.02093,0.01602],"object_pos_start":[0.53848,0.02093,0.01602],"object_to_goal_dist_end":0.2908,"object_to_goal_dist_start":0.2908,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1339.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.60651,0.22314,0.27822],"tcp_start":[0.60293,0.21269,0.33767],"tcp_to_object_dist_end":0.33803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14176,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00333,"descend_2.place_z_offset":0.0779,"lift_1.lift_height":0.11864,"transport_1.approach_height":0.12637,"transport_1.arc_height":0.05015,"transport_1.transport_speed":0.03043},"optimized_scores":{"best_composite_score":0.18026,"best_fitness_score":0.57026,"best_task_score":0.19165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2531.0,"contact_point_centroid":[0.54932,-0.004,-0.00244],"force_p95":0.12595,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92849,"mean_force":0.14118,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58382,0.08094,0.27035]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.54233,-0.02635,-0.00125],"force_p95":0.44211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62314,"mean_force":0.09041,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52826,-0.02744,0.03176]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8129.0,"contact_point_centroid":[0.53011,-0.0086,0.07983],"force_p95":0.11383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33164,"mean_force":0.08137,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52571,-0.02735,0.07774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8704.0,"contact_point_centroid":[0.53009,-0.04601,0.07825],"force_p95":0.10971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32167,"mean_force":0.07746,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52573,-0.02735,0.07652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2720.0,"contact_point_centroid":[0.53421,-0.03244,0.16601],"force_p95":0.15128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27765,"mean_force":0.10216,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52996,-0.01447,0.16953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.53391,0.00357,0.16618],"force_p95":0.17827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26393,"mean_force":0.10975,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52983,-0.01461,0.16959]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54568,-0.02891,-0.00216],"force_p95":0.16954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24803,"mean_force":0.13482,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.02753,0.03137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4054.0,"contact_point_centroid":[0.5314,-0.00828,0.03262],"force_p95":0.08172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15106,"mean_force":0.05196,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52998,-0.02749,0.02994]},{"body_a":"world","body_b":"grasp_target","contact_count":3400.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51822,-0.01384,0.16813]},{"body_a":"world","body_b":"grasp_target","contact_count":376.0,"contact_point_centroid":[0.54923,-0.00398,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62531,0.15675,0.27744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5034.0,"contact_point_centroid":[0.53127,-0.04667,0.03173],"force_p95":0.07448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08387,"mean_force":0.04462,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52998,-0.02749,0.02995]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2490.0,"contact_point_centroid":[0.58696,0.08587,0.27587],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01469,"mean_force":0.01058,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58662,0.08587,0.27366]},{"body_a":"left_finger","body_b":"right_finger","contact_count":401.0,"contact_point_centroid":[0.62585,0.15681,0.27948],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01047,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62534,0.15679,0.27724]}],"total_contact_groups":13},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54923,-0.00398,0.01602],"final_tcp_position":[0.62737,0.16008,0.26155],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9749.00372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3400.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.0277,0.03996],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02761,0.02548],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26006,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16014,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10888.0,"raw_peak_contact_force":0.24803,"tcp_end":[0.52995,-0.02749,0.0299],"tcp_start":[0.53853,-0.0277,0.03996],"tcp_to_object_dist_end":0.01618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.54145,-0.02738,0.11982],"object_pos_start":[0.54551,-0.02761,0.02548],"object_to_goal_dist_end":0.22044,"object_to_goal_dist_start":0.26006,"object_z_max":0.11971,"peak_contact_force":47.35377,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16981.0,"raw_peak_contact_force":0.62314,"subtask_id":"lift_clear","tcp_end":[0.52581,-0.02734,0.13591],"tcp_start":[0.52995,-0.02749,0.0299],"tcp_to_object_dist_end":0.02244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1009.0,"n_steps_budget":1000.0,"object_pos_end":[0.54923,-0.00398,0.01602],"object_pos_start":[0.54145,-0.02738,0.11982],"object_to_goal_dist_end":0.24782,"object_to_goal_dist_start":0.22044,"object_z_max":0.17787,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10117.0,"raw_peak_contact_force":1.92849,"tcp_end":[0.62416,0.15401,0.29205],"tcp_start":[0.62365,0.15237,0.29319],"tcp_to_object_dist_end":0.32676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.54923,-0.00398,0.01602],"object_pos_start":[0.54923,-0.00398,0.01602],"object_to_goal_dist_end":0.24782,"object_to_goal_dist_start":0.24782,"object_z_max":0.01602,"peak_contact_force":9748.92262,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":777.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.62737,0.16008,0.26155],"tcp_start":[0.62416,0.15401,0.29205],"tcp_to_object_dist_end":0.30546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```