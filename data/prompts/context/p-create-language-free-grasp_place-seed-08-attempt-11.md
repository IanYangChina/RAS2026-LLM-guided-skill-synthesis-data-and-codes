## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3875 | 0.52 | ❌ rejected |
| 10 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3133 | 0.25 | ❌ rejected |
| 9 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6395 | 1.00 | ✅ accepted |
| 8 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6368 | 1.00 | ✅ accepted |
| 7 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2065 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.387) — your mutation base

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

- **Composite score**: 0.387
- **task_score** (E): 0.517
- **fitness_score**: 0.727  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2567 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.0969 |
| transport_1 | 1.00 | 1.00 | 0.0991 |
| descend_2 | 1.00 | 1.00 | 0.0683 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.048) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.048)→(0.508, -0.001, 0.039) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 44.333 | 0.168 | 0.242 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.039)→(0.504, -0.001, 0.136) | (0.522, -0.001, 0.025)→(0.518, -0.001, 0.115) | 0.290→0.246 | 1.00 / 24.667 | 0.102 | 0.521 |
| transport_1 | approach | 1.00 / step_budget | (0.564, 0.134, 0.240)→(0.600, 0.195, 0.308) | (0.518, -0.001, 0.115)→(0.597, 0.149, 0.113) | 0.246→0.156 | 1.00 / 14.333 | 91003.766 | 1.166 |
| descend_2 | descend | 1.00 / step_budget | (0.600, 0.195, 0.308)→(0.605, 0.205, 0.241) | (0.597, 0.149, 0.113)→(0.598, 0.154, 0.086) | 0.156→0.131 | 1.00 / 12.667 | 91001.500 | 0.157 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.769
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.526
- phase_breakdown.pre_grasp_score: 0.196
- phase_breakdown.lift_clear_score: 0.705
- phase_breakdown.place_score: 0.551
- grasp_place_fitness: 0.970

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.970
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.283
- **K-run variance**: 0.0296
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41315,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.0099,"descend_2.place_z_offset":0.0343,"lift_1.lift_height":0.11288,"transport_1.approach_height":0.1362,"transport_1.transport_speed":0.05092},"optimized_scores":{"best_composite_score":0.63002,"best_fitness_score":0.97002,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.4797,0.044,-0.00141],"force_p95":0.33567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53785,"mean_force":0.07579,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47001,0.04496,0.04271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10805.0,"contact_point_centroid":[0.46925,0.06375,0.08716],"force_p95":0.10083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31503,"mean_force":0.06163,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46769,0.04474,0.08533]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48281,0.04844,-0.0023],"force_p95":0.20357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26783,"mean_force":0.14405,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47268,0.04522,0.04168]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10600.0,"contact_point_centroid":[0.46956,0.02583,0.08939],"force_p95":0.09812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25411,"mean_force":0.06068,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46771,0.04474,0.08755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4173.0,"contact_point_centroid":[0.57785,0.23656,0.29578],"force_p95":0.12742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22605,"mean_force":0.08796,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57329,0.2182,0.29766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4382.0,"contact_point_centroid":[0.57766,0.19988,0.29484],"force_p95":0.13312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22221,"mean_force":0.08825,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57345,0.21845,0.29651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13620.0,"contact_point_centroid":[0.52159,0.14545,0.23788],"force_p95":0.09655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16461,"mean_force":0.06975,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51632,0.12671,0.23673]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5231.0,"contact_point_centroid":[0.47094,0.02591,0.0419],"force_p95":0.07719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16152,"mean_force":0.04118,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47158,0.04511,0.04054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13647.0,"contact_point_centroid":[0.52068,0.10689,0.23647],"force_p95":0.09723,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15282,"mean_force":0.06962,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51562,0.12558,0.23538]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48859,0.02276,0.173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5297.0,"contact_point_centroid":[0.47152,0.06462,0.04215],"force_p95":0.07985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08597,"mean_force":0.04362,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47159,0.04511,0.04055]}],"total_contact_groups":11},"final_pose_error":0.00624,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5808,0.22617,0.22688],"final_tcp_position":[0.57845,0.2267,0.26003],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.53785,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47931,0.04578,0.04858],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48269,0.04615,0.02496],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29233,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.19357,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12328.0,"raw_peak_contact_force":0.26783,"tcp_end":[0.47155,0.04511,0.04051],"tcp_start":[0.47931,0.04578,0.04858],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.48075,0.04525,0.11995],"object_pos_start":[0.48269,0.04615,0.02496],"object_to_goal_dist_end":0.23696,"object_to_goal_dist_start":0.29233,"object_z_max":0.11984,"peak_contact_force":0.10663,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21551.0,"raw_peak_contact_force":0.53785,"subtask_id":"lift_clear","tcp_end":[0.46773,0.04476,0.14194],"tcp_start":[0.47155,0.04511,0.04051],"tcp_to_object_dist_end":0.02555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57628,0.21067,0.30832],"object_pos_start":[0.48075,0.04525,0.11995],"object_to_goal_dist_end":0.08012,"object_to_goal_dist_start":0.23696,"object_z_max":0.30814,"peak_contact_force":0.08982,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27267.0,"raw_peak_contact_force":0.16461,"tcp_end":[0.56958,0.21077,0.33764],"tcp_start":[0.46773,0.04476,0.14194],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.5808,0.22617,0.22688],"object_pos_start":[0.57628,0.21067,0.30832],"object_to_goal_dist_end":0.00462,"object_to_goal_dist_start":0.08012,"object_z_max":0.30838,"peak_contact_force":0.1243,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8555.0,"raw_peak_contact_force":0.22605,"subtask_id":"place","tcp_end":[0.57845,0.2267,0.26003],"tcp_start":[0.56958,0.21077,0.33764],"tcp_to_object_dist_end":0.03324,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61905,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.01684,"descend_2.place_z_offset":0.00435,"lift_1.lift_height":0.10716,"transport_1.approach_height":0.12404,"transport_1.transport_speed":0.06831},"optimized_scores":{"best_composite_score":0.249,"best_fitness_score":0.589,"best_task_score":0.25148},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":975.0,"contact_point_centroid":[0.60734,0.14866,-0.00337],"force_p95":0.64692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70253,"mean_force":0.17575,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59596,0.19444,0.29732]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.53456,-0.01993,-0.00121],"force_p95":0.30819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4363,"mean_force":0.07038,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52054,-0.01998,0.04606]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9608.0,"contact_point_centroid":[0.52164,-0.03887,0.08928],"force_p95":0.09845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28835,"mean_force":0.06489,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51802,-0.01993,0.08714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9725.0,"contact_point_centroid":[0.5215,-0.00104,0.08821],"force_p95":0.09611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28607,"mean_force":0.06389,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51803,-0.01993,0.08571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8260.0,"contact_point_centroid":[0.5503,0.07665,0.19412],"force_p95":0.14438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24528,"mean_force":0.08246,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54415,0.05799,0.19376]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53707,-0.02121,-0.00211],"force_p95":0.153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21367,"mean_force":0.13099,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52338,-0.02004,0.0457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8995.0,"contact_point_centroid":[0.55169,0.04324,0.19684],"force_p95":0.11561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16911,"mean_force":0.07631,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54557,0.06173,0.19662]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5141,-0.01002,0.17566]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.60737,0.1488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60524,0.22153,0.26392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.52329,-0.00084,0.0471],"force_p95":0.06964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10758,"mean_force":0.04402,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52218,-0.02001,0.0443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.52325,-0.03929,0.0461],"force_p95":0.07219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07391,"mean_force":0.04474,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52219,-0.02001,0.04431]},{"body_a":"left_finger","body_b":"right_finger","contact_count":874.0,"contact_point_centroid":[0.59773,0.19816,0.30225],"force_p95":0.01317,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01539,"mean_force":0.01081,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59737,0.19814,0.30006]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1535.0,"contact_point_centroid":[0.60568,0.22154,0.26633],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01049,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60523,0.22152,0.26407]}],"total_contact_groups":13},"final_pose_error":0.00495,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60737,0.1488,0.01602],"final_tcp_position":[0.60669,0.22543,0.21419],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273011.08456,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53046,-0.02013,0.05407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02046,0.02559],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3163,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1489,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11684.0,"raw_peak_contact_force":0.21367,"tcp_end":[0.52216,-0.02001,0.04427],"tcp_start":[0.53046,-0.02013,0.05407],"tcp_to_object_dist_end":0.02384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53115,-0.01996,0.11419],"object_pos_start":[0.53697,-0.02046,0.02559],"object_to_goal_dist_end":0.27626,"object_to_goal_dist_start":0.3163,"object_z_max":0.11407,"peak_contact_force":0.08649,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19480.0,"raw_peak_contact_force":0.4363,"subtask_id":"lift_clear","tcp_end":[0.51807,-0.01992,0.13905],"tcp_start":[0.52216,-0.02001,0.04427],"tcp_to_object_dist_end":0.02809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1084.0,"n_steps_budget":1000.0,"object_pos_end":[0.60737,0.1488,0.016],"object_pos_start":[0.53115,-0.01996,0.11419],"object_to_goal_dist_end":0.20707,"object_to_goal_dist_start":0.27626,"object_z_max":0.22834,"peak_contact_force":273011.08456,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19104.0,"raw_peak_contact_force":1.70253,"tcp_end":[0.60512,0.21845,0.31471],"tcp_start":[0.59931,0.2028,0.30426],"tcp_to_object_dist_end":0.30672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.60737,0.1488,0.01602],"object_pos_start":[0.60737,0.1488,0.01602],"object_to_goal_dist_end":0.20706,"object_to_goal_dist_start":0.20706,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2979.0,"raw_peak_contact_force":0.12264,"subtask_id":"place","tcp_end":[0.60669,0.22543,0.21419],"tcp_start":[0.60512,0.21845,0.31471],"tcp_to_object_dist_end":0.21247,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13389,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00522,"descend_2.place_z_offset":0.07958,"lift_1.lift_height":0.10682,"transport_1.approach_height":0.11146,"transport_1.transport_speed":0.02165},"optimized_scores":{"best_composite_score":0.28338,"best_fitness_score":0.62338,"best_task_score":0.29979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1391.0,"contact_point_centroid":[0.606,0.08709,-0.0028],"force_p95":0.39288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63053,"mean_force":0.1558,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60977,0.12779,0.2493]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.54245,-0.02645,-0.00125],"force_p95":0.39597,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58822,"mean_force":0.08605,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52826,-0.02742,0.03371]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7637.0,"contact_point_centroid":[0.52979,-0.00855,0.07615],"force_p95":0.11224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32773,"mean_force":0.07889,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52572,-0.02733,0.07389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8292.0,"contact_point_centroid":[0.52972,-0.04601,0.07449],"force_p95":0.10759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31751,"mean_force":0.07434,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52573,-0.02733,0.07276]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54568,-0.02894,-0.00216],"force_p95":0.16951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.13481,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53123,-0.02751,0.03332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4618.0,"contact_point_centroid":[0.556,0.04205,0.16151],"force_p95":0.15708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22968,"mean_force":0.10367,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55102,0.02377,0.16352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5440.0,"contact_point_centroid":[0.55561,0.00543,0.16114],"force_p95":0.13235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17045,"mean_force":0.08972,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55093,0.02358,0.16338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.5314,-0.00826,0.03457],"force_p95":0.08174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15143,"mean_force":0.05198,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52999,-0.02747,0.03188]},{"body_a":"world","body_b":"grasp_target","contact_count":3376.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01382,0.16923]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.60603,0.08718,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62779,0.16135,0.25394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5034.0,"contact_point_centroid":[0.53128,-0.04665,0.03368],"force_p95":0.07454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08266,"mean_force":0.04456,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53,-0.02747,0.03189]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1261.0,"contact_point_centroid":[0.61283,0.1325,0.25543],"force_p95":0.01203,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01065,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61245,0.1325,0.25319]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2248.0,"contact_point_centroid":[0.62832,0.16137,0.25617],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.0104,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62779,0.16136,0.25392]}],"total_contact_groups":13},"final_pose_error":0.00875,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60603,0.08718,0.01602],"final_tcp_position":[0.62941,0.16344,0.24859],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.25426,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":845.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53853,-0.02768,0.04192],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02764,0.02547],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26008,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16036,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10891.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.52997,-0.02747,0.03185],"tcp_start":[0.53853,-0.02768,0.04192],"tcp_to_object_dist_end":0.01682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54099,-0.02746,0.11006],"object_pos_start":[0.54552,-0.02764,0.02547],"object_to_goal_dist_end":0.22343,"object_to_goal_dist_start":0.26008,"object_z_max":0.10995,"peak_contact_force":0.11312,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16081.0,"raw_peak_contact_force":0.58822,"subtask_id":"lift_clear","tcp_end":[0.52574,-0.02733,0.12617],"tcp_start":[0.52997,-0.02747,0.03185],"tcp_to_object_dist_end":0.02219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.60603,0.08718,0.01602],"object_pos_start":[0.54099,-0.02746,0.11006],"object_to_goal_dist_end":0.1807,"object_to_goal_dist_start":0.22343,"object_z_max":0.18263,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12710.0,"raw_peak_contact_force":1.63053,"tcp_end":[0.62597,0.15709,0.27204],"tcp_start":[0.62573,0.15568,0.27242],"tcp_to_object_dist_end":0.26614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.60603,0.08718,0.01602],"object_pos_start":[0.60603,0.08718,0.01602],"object_to_goal_dist_end":0.1807,"object_to_goal_dist_start":0.1807,"object_z_max":0.01602,"peak_contact_force":273004.25426,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4344.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.62941,0.16344,0.24859],"tcp_start":[0.62597,0.15709,0.27204],"tcp_to_object_dist_end":0.24586,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```