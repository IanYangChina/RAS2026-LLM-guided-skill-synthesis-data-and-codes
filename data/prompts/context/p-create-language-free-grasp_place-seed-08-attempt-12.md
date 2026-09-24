## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2474 | 0.32 | ❌ rejected |
| 11 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3875 | 0.52 | ❌ rejected |
| 10 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3133 | 0.25 | ❌ rejected |
| 9 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6395 | 1.00 | ✅ accepted |
| 8 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6368 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.247) — your mutation base

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

- **Composite score**: 0.247
- **task_score** (E): 0.323
- **fitness_score**: 0.637  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2631 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0982 |
| transport_1 | 0.00 | 1.00 | 0.0005 |
| descend_2 | 0.00 | 1.00 | 0.0794 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.042) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.511, -0.001, 0.036)→(0.511, -0.001, 0.036) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.333 | 0.164 | 0.243 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.036)→(0.507, -0.001, 0.134) | (0.522, -0.001, 0.025)→(0.521, -0.001, 0.117) | 0.290→0.243 | 1.00 / 26.000 | 0.104 | 0.571 |
| transport_1 | approach | 0.00 / guard_failure | (0.505, -0.002, 0.139)→(0.505, -0.002, 0.139) | (0.521, -0.001, 0.117)→(0.519, -0.001, 0.122) | 0.243→0.244 | 1.00 / 29.000 | 0.000 | 0.285 |
| descend_2 | descend | 0.00 / step_budget | (0.505, -0.002, 0.139)→(0.535, 0.065, 0.168) | (0.518, -0.002, 0.122)→(0.541, 0.066, 0.139) | 0.244→0.171 | 1.00 / 14.333 | 55983.998 | 0.222 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.363
- phase_score: 0.235
- phase_breakdown.pre_grasp_score: 0.174
- phase_breakdown.lift_clear_score: 0.581
- phase_breakdown.place_score: 0.051
- grasp_place_fitness: 0.655

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.655
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: 0.256
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.248


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87037,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00108,"descend_2.place_z_offset":0.0381,"lift_1.lift_height":0.11318,"transport_1.approach_height":0.15683,"transport_1.arc_height":0.1258,"transport_1.transport_speed":0.03821},"optimized_scores":{"best_composite_score":0.25583,"best_fitness_score":0.64583,"best_task_score":0.33266},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.47947,0.04419,-0.0014],"force_p95":0.37125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5978,"mean_force":0.07793,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47293,0.04528,0.03703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11853.0,"contact_point_centroid":[0.47115,0.06421,0.08438],"force_p95":0.08335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3311,"mean_force":0.05551,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47056,0.04506,0.08228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12342.0,"contact_point_centroid":[0.47119,0.026,0.08634],"force_p95":0.081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29821,"mean_force":0.05252,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47056,0.04506,0.08436]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48281,0.04825,-0.00235],"force_p95":0.20275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27379,"mean_force":0.14767,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47492,0.04549,0.03529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.47257,0.06353,0.13854],"force_p95":0.16752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25925,"mean_force":0.0967,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46968,0.04451,0.13734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":247.0,"contact_point_centroid":[0.47193,0.02587,0.13863],"force_p95":0.16412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25884,"mean_force":0.08493,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46973,0.04454,0.13729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11209.0,"contact_point_centroid":[0.48615,0.05208,0.15339],"force_p95":0.13099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24398,"mean_force":0.08238,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48167,0.07056,0.15325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11158.0,"contact_point_centroid":[0.48666,0.08951,0.1537],"force_p95":0.12943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22805,"mean_force":0.08331,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.48192,0.07096,0.15353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5739.0,"contact_point_centroid":[0.47468,0.02625,0.03679],"force_p95":0.07975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16578,"mean_force":0.0451,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47451,0.04544,0.03485]},{"body_a":"world","body_b":"grasp_target","contact_count":3236.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48852,0.02284,0.16838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6168.0,"contact_point_centroid":[0.47466,0.06485,0.03673],"force_p95":0.08104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08545,"mean_force":0.04498,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47452,0.04544,0.03486]}],"total_contact_groups":11},"final_pose_error":0.17324,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51021,0.10771,0.14419],"final_tcp_position":[0.50282,0.10511,0.17667],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3236.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47923,0.04585,0.03983],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04613,0.02495],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29236,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18767,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13711.0,"raw_peak_contact_force":0.27379,"tcp_end":[0.47449,0.04544,0.03483],"tcp_start":[0.47449,0.04544,0.03484],"tcp_to_object_dist_end":0.01284,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.48398,0.04564,0.12112],"object_pos_start":[0.48266,0.04608,0.025],"object_to_goal_dist_end":0.23476,"object_to_goal_dist_start":0.29236,"object_z_max":0.12101,"peak_contact_force":0.10012,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24342.0,"raw_peak_contact_force":0.5978,"subtask_id":"lift_clear","tcp_end":[0.47063,0.04508,0.13651],"tcp_start":[0.47449,0.04544,0.03483],"tcp_to_object_dist_end":0.02038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.48122,0.0442,0.12274],"object_pos_start":[0.48398,0.04564,0.12112],"object_to_goal_dist_end":0.2363,"object_to_goal_dist_start":0.23476,"object_z_max":0.1229,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":468.0,"raw_peak_contact_force":0.25925,"tcp_end":[0.4684,0.04343,0.13882],"tcp_start":[0.46861,0.04369,0.13847],"tcp_to_object_dist_end":0.02058,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51021,0.10771,0.14419],"object_pos_start":[0.48099,0.04391,0.12308],"object_to_goal_dist_end":0.16509,"object_to_goal_dist_start":0.23647,"object_z_max":0.14885,"peak_contact_force":167951.73011,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22367.0,"raw_peak_contact_force":0.24398,"subtask_id":"place","tcp_end":[0.50282,0.10511,0.17667],"tcp_start":[0.4684,0.04343,0.13882],"tcp_to_object_dist_end":0.03341,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87273,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00491,"descend_2.place_z_offset":0.05854,"lift_1.lift_height":0.11336,"transport_1.approach_height":0.18645,"transport_1.arc_height":0.0914,"transport_1.transport_speed":0.04801},"optimized_scores":{"best_composite_score":0.22101,"best_fitness_score":0.61101,"best_task_score":0.27197},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53424,-0.01965,-0.0012],"force_p95":0.40976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56447,"mean_force":0.08063,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52365,-0.02006,0.03804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10485.0,"contact_point_centroid":[0.52265,-0.00099,0.08408],"force_p95":0.10092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30329,"mean_force":0.06174,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52107,-0.02,0.08201]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11302.0,"contact_point_centroid":[0.52268,-0.03893,0.08232],"force_p95":0.09716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30233,"mean_force":0.05836,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52106,-0.02,0.08082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":655.0,"contact_point_centroid":[0.5234,-0.00187,0.14332],"force_p95":0.13648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24555,"mean_force":0.0843,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51935,-0.02044,0.14251]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53707,-0.02111,-0.00214],"force_p95":0.154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22237,"mean_force":0.13254,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52577,-0.02011,0.0368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":661.0,"contact_point_centroid":[0.52324,-0.0391,0.14387],"force_p95":0.13384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22108,"mean_force":0.08347,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51928,-0.02047,0.14292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12657.0,"contact_point_centroid":[0.53207,0.03241,0.16049],"force_p95":0.10904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2064,"mean_force":0.0738,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52726,0.01392,0.16034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11894.0,"contact_point_centroid":[0.53153,-0.00537,0.16059],"force_p95":0.12386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20454,"mean_force":0.07826,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52706,0.01326,0.16011]},{"body_a":"world","body_b":"grasp_target","contact_count":3304.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01006,0.16956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5808.0,"contact_point_centroid":[0.52526,-0.00088,0.03856],"force_p95":0.06999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1109,"mean_force":0.04513,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5253,-0.02009,0.03625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6273.0,"contact_point_centroid":[0.52512,-0.03933,0.0381],"force_p95":0.06892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07325,"mean_force":0.0431,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52531,-0.02009,0.03626]}],"total_contact_groups":11},"final_pose_error":0.20795,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54597,0.05234,0.15052],"final_tcp_position":[0.54156,0.05243,0.17775],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.56447,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3304.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53039,-0.02017,0.04227],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02033,0.0256],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3162,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14825,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13885.0,"raw_peak_contact_force":0.22237,"tcp_end":[0.52528,-0.02009,0.03623],"tcp_start":[0.52528,-0.02009,0.03623],"tcp_to_object_dist_end":0.01579,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53535,-0.02007,0.11985],"object_pos_start":[0.53696,-0.02031,0.02562],"object_to_goal_dist_end":0.27332,"object_to_goal_dist_start":0.31617,"object_z_max":0.11974,"peak_contact_force":0.10612,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21933.0,"raw_peak_contact_force":0.56447,"subtask_id":"lift_clear","tcp_end":[0.52118,-0.02,0.13709],"tcp_start":[0.52528,-0.02009,0.03623],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.53172,-0.02095,0.13101],"object_pos_start":[0.53535,-0.02007,0.11985],"object_to_goal_dist_end":0.27179,"object_to_goal_dist_start":0.27332,"object_z_max":0.13164,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.24555,"tcp_end":[0.51807,-0.02094,0.14983],"tcp_start":[0.51827,-0.02088,0.14893],"tcp_to_object_dist_end":0.02325,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54597,0.05234,0.15052],"object_pos_start":[0.53154,-0.02097,0.13189],"object_to_goal_dist_end":0.19531,"object_to_goal_dist_start":0.27161,"object_z_max":0.15051,"peak_contact_force":0.15396,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24551.0,"raw_peak_contact_force":0.2064,"subtask_id":"place","tcp_end":[0.54156,0.05243,0.17775],"tcp_start":[0.51807,-0.02094,0.14983],"tcp_to_object_dist_end":0.02759,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85294,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00608,"descend_2.place_z_offset":0.03207,"lift_1.lift_height":0.10464,"transport_1.approach_height":0.15132,"transport_1.arc_height":0.14926,"transport_1.transport_speed":0.06687},"optimized_scores":{"best_composite_score":0.26546,"best_fitness_score":0.65546,"best_task_score":0.36288},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":154.0,"contact_point_centroid":[0.54248,-0.02694,-0.00126],"force_p95":0.36366,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5521,"mean_force":0.08353,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53166,-0.0275,0.03835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.53417,-0.00886,0.13015],"force_p95":0.2587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35096,"mean_force":0.13753,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52904,-0.02746,0.12858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.53379,-0.04603,0.1304],"force_p95":0.25572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3479,"mean_force":0.12913,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52903,-0.02746,0.12858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10409.0,"contact_point_centroid":[0.53078,-0.04631,0.07861],"force_p95":0.09675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3117,"mean_force":0.05802,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52911,-0.02741,0.07716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9437.0,"contact_point_centroid":[0.53072,-0.00836,0.08003],"force_p95":0.10332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30068,"mean_force":0.06253,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52912,-0.02741,0.07792]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54568,-0.02898,-0.00218],"force_p95":0.16494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23245,"mean_force":0.13588,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53387,-0.02757,0.03711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12717.0,"contact_point_centroid":[0.54532,-0.01597,0.13635],"force_p95":0.10748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21543,"mean_force":0.07423,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54102,0.00275,0.1354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13633.0,"contact_point_centroid":[0.54592,0.02166,0.13621],"force_p95":0.09545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19091,"mean_force":0.06954,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.54121,0.0031,0.13554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6086.0,"contact_point_centroid":[0.53308,-0.0083,0.03936],"force_p95":0.06944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15311,"mean_force":0.04317,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53339,-0.02755,0.03655]},{"body_a":"world","body_b":"grasp_target","contact_count":3368.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01381,0.1697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6619.0,"contact_point_centroid":[0.53295,-0.04685,0.03882],"force_p95":0.06957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07374,"mean_force":0.04126,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53339,-0.02755,0.03656]}],"total_contact_groups":11},"final_pose_error":0.1574,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56716,0.03856,0.12366],"final_tcp_position":[0.56035,0.03846,0.14961],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.5521,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3368.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.02768,0.04274],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02792,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26029,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15731,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":14509.0,"raw_peak_contact_force":0.23245,"tcp_end":[0.53337,-0.02755,0.03652],"tcp_start":[0.53337,-0.02755,0.03652],"tcp_to_object_dist_end":0.01646,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":575.0,"n_steps_budget":660.0,"object_pos_end":[0.54344,-0.02747,0.1112],"object_pos_start":[0.54555,-0.02789,0.02549],"object_to_goal_dist_end":0.2221,"object_to_goal_dist_start":0.26025,"object_z_max":0.11109,"peak_contact_force":0.10428,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20000.0,"raw_peak_contact_force":0.5521,"subtask_id":"lift_clear","tcp_end":[0.52916,-0.0274,0.12843],"tcp_start":[0.53337,-0.02755,0.03652],"tcp_to_object_dist_end":0.02238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.54281,-0.0276,0.11137],"object_pos_start":[0.54344,-0.02747,0.1112],"object_to_goal_dist_end":0.22242,"object_to_goal_dist_start":0.2221,"object_z_max":0.11137,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":140.0,"raw_peak_contact_force":0.35096,"tcp_end":[0.52858,-0.02766,0.12878],"tcp_start":[0.52867,-0.02758,0.12876],"tcp_to_object_dist_end":0.02248,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56716,0.03856,0.12366],"object_pos_start":[0.5427,-0.02768,0.11138],"object_to_goal_dist_end":0.15205,"object_to_goal_dist_start":0.22253,"object_z_max":0.12364,"peak_contact_force":0.11138,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26350.0,"raw_peak_contact_force":0.21543,"subtask_id":"place","tcp_end":[0.56035,0.03846,0.14961],"tcp_start":[0.52858,-0.02766,0.12878],"tcp_to_object_dist_end":0.02682,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```