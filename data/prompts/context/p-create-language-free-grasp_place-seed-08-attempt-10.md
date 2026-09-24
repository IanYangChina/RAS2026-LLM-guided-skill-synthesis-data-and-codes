## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3133 | 0.25 | ❌ rejected |
| 9 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6395 | 1.00 | ✅ accepted |
| 8 | descend → grasp → lift → approach → descend | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6368 | 1.00 | ✅ accepted |
| 7 | descend → grasp → lift → approach → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2065 | 0.29 | ✅ accepted |
| 6 | descend → grasp → lift → descend → descend → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2419 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.313) — your mutation base

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

- **Composite score**: 0.313
- **task_score** (E): 0.250
- **fitness_score**: 0.603  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.2723 |
| grasp_1 | 0.00 | 1.00 | 0.0077 |
| lift_1 | 1.00 | 1.00 | 0.0987 |
| transport_1 | 1.00 | 1.00 | 0.2857 |
| descend_2 | 1.00 | 1.00 | 0.0878 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.032) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.516, -0.001, 0.032)→(0.511, -0.001, 0.027) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 45.667 | 0.160 | 0.256 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.027)→(0.507, -0.001, 0.125) | (0.522, -0.001, 0.025)→(0.523, -0.001, 0.117) | 0.290→0.243 | 1.00 / 26.667 | 55983.980 | 0.758 |
| transport_1 | approach | 1.00 / step_budget | (0.507, -0.001, 0.125)→(0.599, 0.191, 0.312) | (0.523, -0.001, 0.117)→(0.574, 0.119, 0.019) | 0.243→0.210 | 1.00 / 8.000 | 3249.716 | 1.743 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.191, 0.312)→(0.605, 0.205, 0.225) | (0.574, 0.119, 0.019)→(0.574, 0.119, 0.019) | 0.210→0.210 | 1.00 / 8.333 | 94251.508 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.304
- phase_score: 0.657
- phase_breakdown.pre_grasp_score: 0.174
- phase_breakdown.lift_clear_score: 0.593
- phase_breakdown.place_score: 0.888
- grasp_place_fitness: 0.626

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.626
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.304
- **Median Q (composite search score)**: 0.307
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.286


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93258,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.0185,"descend_2.place_z_offset":0.00024,"lift_1.lift_height":0.11831,"transport_1.approach_height":0.14437},"optimized_scores":{"best_composite_score":0.30707,"best_fitness_score":0.59707,"best_task_score":0.23426},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1042.0,"contact_point_centroid":[0.54854,0.15988,-0.00315],"force_p95":0.63447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59617,"mean_force":0.17924,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55003,0.17881,0.29972]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.48004,0.04515,-0.00137],"force_p95":0.81083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01673,"mean_force":0.11993,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47259,0.04539,0.01761]},{"body_a":"grasp_target","body_b":"hand","contact_count":213.0,"contact_point_centroid":[0.48761,0.06514,0.06985],"force_p95":0.07492,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42774,"mean_force":0.05595,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47062,0.0452,0.03136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2501.0,"contact_point_centroid":[0.49068,0.05532,0.15798],"force_p95":0.20264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3506,"mean_force":0.10617,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48551,0.07378,0.15804]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.48266,0.04734,-0.0024],"force_p95":0.22773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30451,"mean_force":0.15774,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47471,0.04564,0.01585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2563.0,"contact_point_centroid":[0.49209,0.0948,0.16108],"force_p95":0.21673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3002,"mean_force":0.10752,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48699,0.07627,0.16134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12925.0,"contact_point_centroid":[0.47099,0.06419,0.06797],"force_p95":0.08012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2966,"mean_force":0.0536,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47016,0.04517,0.06638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11796.0,"contact_point_centroid":[0.47106,0.02606,0.06707],"force_p95":0.09175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26399,"mean_force":0.05755,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47018,0.04517,0.06487]},{"body_a":"grasp_target","body_b":"hand","contact_count":376.0,"contact_point_centroid":[0.49108,0.06468,0.0546],"force_p95":0.23211,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25091,"mean_force":0.07825,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47451,0.04561,0.01565]},{"body_a":"world","body_b":"grasp_target","contact_count":3480.0,"contact_point_centroid":[0.4827,0.04873,-0.00196],"force_p95":0.12631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48839,0.02297,0.15833]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.54999,0.16125,-0.00199],"force_p95":0.12275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12331,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57503,0.22059,0.2907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5184.0,"contact_point_centroid":[0.47436,0.06515,0.01725],"force_p95":0.07476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0959,"mean_force":0.04707,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47423,0.04558,0.01537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4378.0,"contact_point_centroid":[0.47436,0.02646,0.01732],"force_p95":0.07455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09386,"mean_force":0.04485,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47421,0.04558,0.01536]},{"body_a":"left_finger","body_b":"right_finger","contact_count":977.0,"contact_point_centroid":[0.55369,0.18413,0.30918],"force_p95":0.01232,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01069,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55334,0.18411,0.30692]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1906.0,"contact_point_centroid":[0.57545,0.22062,0.29292],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01048,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57503,0.2206,0.2906]}],"total_contact_groups":15},"final_pose_error":0.0049,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54999,0.16125,0.02602],"final_tcp_position":[0.57823,0.22642,0.23293],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273005.45392,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3480.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.47906,0.046,0.0203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":0.0,"n_steps_budget":50.0,"object_pos_end":[0.48234,0.04562,0.02489],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29283,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17193,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11542.0,"raw_peak_contact_force":0.30451,"tcp_end":[0.4742,0.04556,0.01534],"tcp_start":[0.47906,0.046,0.0203],"tcp_to_object_dist_end":0.01255,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.48948,0.04497,0.12315],"object_pos_start":[0.48234,0.04562,0.02489],"object_to_goal_dist_end":0.2321,"object_to_goal_dist_start":0.29283,"object_z_max":0.12305,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25090.0,"raw_peak_contact_force":1.01673,"subtask_id":"lift_clear","tcp_end":[0.47024,0.04519,0.12218],"tcp_start":[0.4742,0.04556,0.01534],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.54999,0.16124,0.02602],"object_pos_start":[0.48948,0.04497,0.12315],"object_to_goal_dist_end":0.2177,"object_to_goal_dist_start":0.2321,"object_z_max":0.18829,"peak_contact_force":9748.90209,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7083.0,"raw_peak_contact_force":1.59617,"tcp_end":[0.57308,0.2156,0.34951],"tcp_start":[0.47024,0.04519,0.12218],"tcp_to_object_dist_end":0.32884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.54999,0.16125,0.02602],"object_pos_start":[0.54999,0.16124,0.02602],"object_to_goal_dist_end":0.2177,"object_to_goal_dist_start":0.2177,"object_z_max":0.02602,"peak_contact_force":273005.45392,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3698.0,"raw_peak_contact_force":0.12331,"subtask_id":"place","tcp_end":[0.57823,0.22642,0.23293],"tcp_start":[0.57308,0.2156,0.34951],"tcp_to_object_dist_end":0.21876,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92982,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":-0.00317,"descend_2.place_z_offset":0.03181,"lift_1.lift_height":0.10835,"transport_1.approach_height":0.14411},"optimized_scores":{"best_composite_score":0.2966,"best_fitness_score":0.5866,"best_task_score":0.21151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.57102,0.10047,-0.00281],"force_p95":0.46125,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84584,"mean_force":0.16852,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58243,0.1557,0.27813]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53402,-0.01959,-0.0012],"force_p95":0.5124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69731,"mean_force":0.09565,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52356,-0.0201,0.02983]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10953.0,"contact_point_centroid":[0.52253,-0.03894,0.07213],"force_p95":0.09635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31541,"mean_force":0.05772,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52092,-0.02005,0.07069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9867.0,"contact_point_centroid":[0.52252,-0.001,0.07359],"force_p95":0.10329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31531,"mean_force":0.06277,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52094,-0.02005,0.07148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2382.0,"contact_point_centroid":[0.53792,0.03732,0.15481],"force_p95":0.17299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2899,"mean_force":0.10119,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53234,0.01883,0.15499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2464.0,"contact_point_centroid":[0.53758,-0.00032,0.15429],"force_p95":0.17405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26841,"mean_force":0.10033,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53215,0.01816,0.1545]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.53706,-0.02107,-0.00212],"force_p95":0.15404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23035,"mean_force":0.1323,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52577,-0.02015,0.02866]},{"body_a":"world","body_b":"grasp_target","contact_count":3412.0,"contact_point_centroid":[0.53702,-0.02132,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51411,-0.01009,0.16536]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.57048,0.10093,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60435,0.21737,0.28362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4793.0,"contact_point_centroid":[0.52521,-0.00092,0.03041],"force_p95":0.06972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11525,"mean_force":0.04493,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52523,-0.02014,0.02805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5226.0,"contact_point_centroid":[0.52506,-0.0394,0.02993],"force_p95":0.06875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07978,"mean_force":0.04294,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52524,-0.02014,0.02805]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1113.0,"contact_point_centroid":[0.58586,0.16412,0.28804],"force_p95":0.01249,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01527,"mean_force":0.01073,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58558,0.16411,0.28576]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1449.0,"contact_point_centroid":[0.60476,0.21739,0.28581],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01038,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60435,0.21737,0.28356]}],"total_contact_groups":13},"final_pose_error":0.00492,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57048,0.10093,0.01602],"final_tcp_position":[0.60674,0.22463,0.24055],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.94603,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3412.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53039,-0.02021,0.03404],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":0.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02023,0.02561],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31612,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14905,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11623.0,"raw_peak_contact_force":0.23035,"tcp_end":[0.52521,-0.02013,0.02802],"tcp_start":[0.53039,-0.02021,0.03404],"tcp_to_object_dist_end":0.01196,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53764,-0.02001,0.11404],"object_pos_start":[0.53692,-0.02023,0.02561],"object_to_goal_dist_end":0.27457,"object_to_goal_dist_start":0.31612,"object_z_max":0.11393,"peak_contact_force":0.10785,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20966.0,"raw_peak_contact_force":0.69731,"subtask_id":"lift_clear","tcp_end":[0.52099,-0.02004,0.1239],"tcp_start":[0.52521,-0.02013,0.02802],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.57048,0.10093,0.01602],"object_pos_start":[0.53764,-0.02001,0.11404],"object_to_goal_dist_end":0.23302,"object_to_goal_dist_start":0.27457,"object_z_max":0.17485,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7199.0,"raw_peak_contact_force":1.84584,"tcp_end":[0.60321,0.21098,0.32815],"tcp_start":[0.52099,-0.02004,0.1239],"tcp_to_object_dist_end":0.33257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.57048,0.10093,0.01602],"object_pos_start":[0.57048,0.10093,0.01602],"object_to_goal_dist_end":0.23302,"object_to_goal_dist_start":0.23302,"object_z_max":0.01602,"peak_contact_force":9748.94603,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2797.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.60674,0.22463,0.24055],"tcp_start":[0.60321,0.21098,0.32815],"tcp_to_object_dist_end":0.2589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79739,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_z_offset":0.00608,"descend_2.place_z_offset":0.03315,"lift_1.lift_height":0.10572,"transport_1.approach_height":0.10247},"optimized_scores":{"best_composite_score":0.33617,"best_fitness_score":0.62617,"best_task_score":0.30446},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":793.0,"contact_point_centroid":[0.60105,0.09483,-0.00324],"force_p95":0.63269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78787,"mean_force":0.18292,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60179,0.11184,0.2306]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.54275,-0.02705,-0.00126],"force_p95":0.36242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55922,"mean_force":0.08362,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53164,-0.02749,0.03844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10634.0,"contact_point_centroid":[0.53065,-0.04637,0.07904],"force_p95":0.09917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31165,"mean_force":0.0593,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52908,-0.0274,0.07742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10167.0,"contact_point_centroid":[0.53071,-0.00842,0.08132],"force_p95":0.0981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30111,"mean_force":0.06082,"phase_index":2.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52908,-0.0274,0.07935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1961.0,"contact_point_centroid":[0.54967,-0.01396,0.15082],"force_p95":0.17781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27826,"mean_force":0.0984,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54396,0.0046,0.15026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.55069,0.02468,0.15158],"force_p95":0.16233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24688,"mean_force":0.09352,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54474,0.00622,0.15133]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.54566,-0.02903,-0.00218],"force_p95":0.16537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23252,"mean_force":0.13557,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53392,-0.02757,0.03726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.53308,-0.00828,0.03945],"force_p95":0.06949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1531,"mean_force":0.04302,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53339,-0.02754,0.03663]},{"body_a":"world","body_b":"grasp_target","contact_count":3368.0,"contact_point_centroid":[0.5456,-0.02923,-0.00195],"force_p95":0.12666,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51819,-0.01381,0.16971]},{"body_a":"world","body_b":"grasp_target","contact_count":3204.0,"contact_point_centroid":[0.60092,0.09484,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62509,0.15696,0.22156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5519.0,"contact_point_centroid":[0.53294,-0.04686,0.03891],"force_p95":0.06967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07363,"mean_force":0.04093,"phase_index":1.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53339,-0.02754,0.03664]},{"body_a":"left_finger","body_b":"right_finger","contact_count":599.0,"contact_point_centroid":[0.60821,0.12269,0.24107],"force_p95":0.01332,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.0108,"phase_index":3.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60777,0.12268,0.23888]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3445.0,"contact_point_centroid":[0.62548,0.15697,0.2239],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01037,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62509,0.15696,0.22158]}],"total_contact_groups":13},"final_pose_error":0.00838,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60092,0.09484,0.01602],"final_tcp_position":[0.62884,0.1632,0.20292],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.78787,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3368.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53852,-0.02767,0.04282],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":0.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02791,0.02546],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26029,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15918,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12159.0,"raw_peak_contact_force":0.23252,"tcp_end":[0.53336,-0.02754,0.0366],"tcp_start":[0.53852,-0.02767,0.04282],"tcp_to_object_dist_end":0.01651,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54331,-0.02758,0.11259],"object_pos_start":[0.54555,-0.02791,0.02546],"object_to_goal_dist_end":0.22184,"object_to_goal_dist_start":0.26029,"object_z_max":0.11248,"peak_contact_force":0.10341,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20957.0,"raw_peak_contact_force":0.55922,"subtask_id":"lift_clear","tcp_end":[0.52915,-0.02739,0.12982],"tcp_start":[0.53336,-0.02754,0.0366],"tcp_to_object_dist_end":0.0223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.60092,0.09483,0.01602],"object_pos_start":[0.54331,-0.02758,0.11259],"object_to_goal_dist_end":0.17839,"object_to_goal_dist_start":0.22184,"object_z_max":0.15596,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5405.0,"raw_peak_contact_force":1.78787,"tcp_end":[0.62157,0.14761,0.25788],"tcp_start":[0.52915,-0.02739,0.12982],"tcp_to_object_dist_end":0.24841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.60092,0.09484,0.01602],"object_pos_start":[0.60092,0.09483,0.01602],"object_to_goal_dist_end":0.17838,"object_to_goal_dist_start":0.17839,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6649.0,"raw_peak_contact_force":0.12264,"subtask_id":"place","tcp_end":[0.62884,0.1632,0.20292],"tcp_start":[0.62157,0.14761,0.25788],"tcp_to_object_dist_end":0.20096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```