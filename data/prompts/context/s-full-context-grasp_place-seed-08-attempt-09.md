## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2025 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1653 | 0.31 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1203 | 0.15 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2145 | 0.15 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5552 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.202) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_subtask
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: place_subtask
  target_entity: object
  weight: 0.8
phases:
- id: approach_obj
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
  parameters:
    pre_grasp_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_subtask
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
- id: grasp_phase
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  parameters:
    grasp_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_obj
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
  parameters:
    lift_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    approach_goal_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: descend_place
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
    - 0.0
    tolerance: 0.02
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_subtask

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_obj** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - parameter_bindings:
    - pre_grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_phase** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_obj** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - lift_z_offset: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_goal_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.202
- **task_score** (E): 0.170
- **fitness_score**: 0.168  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 0.00 | 1.00 | 0.1369 |
| descend_grasp | 0.00 | 1.00 | 0.0663 |
| grasp_phase | 1.00 | 1.00 | 0.0000 |
| lift_obj | 0.00 | 1.00 | 0.1174 |
| approach_goal | 0.67 | 1.00 | 0.1912 |
| descend_place | 0.00 | 1.00 | 0.0348 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.438, -0.001, 0.182) | (0.522, -0.001, 0.030)→(0.484, -0.002, 0.016) | 0.287→0.310 | 1.00 / 5.000 | 299.917 | 1499.327 |
| descend_grasp | descend | 0.00 / step_budget | (0.438, -0.001, 0.182)→(0.463, -0.019, 0.176) | (0.484, -0.002, 0.016)→(0.484, -0.002, 0.016) | 0.310→0.310 | 1.00 / 6.333 | 384.057 | 930.491 |
| grasp_phase | grasp | 1.00 / step_budget | (0.463, -0.019, 0.175)→(0.463, -0.019, 0.175) | (0.484, -0.002, 0.016)→(0.484, -0.002, 0.016) | 0.310→0.310 | 1.00 / 9.667 | 502.241 | 519.860 |
| lift_obj | lift | 0.00 / step_budget | (0.463, -0.019, 0.175)→(0.491, 0.003, 0.251) | (0.484, -0.002, 0.016)→(0.484, 0.009, 0.016) | 0.310→0.302 | 1.00 / 9.667 | 632.992 | 446.968 |
| approach_goal | approach | 0.67 / step_budget | (0.491, 0.003, 0.251)→(0.547, 0.182, 0.269) | (0.484, 0.009, 0.016)→(0.483, 0.062, 0.016) | 0.302→0.269 | 1.00 / 9.333 | 91119.738 | 411.178 |
| descend_place | descend | 0.00 / step_budget | (0.547, 0.182, 0.269)→(0.563, 0.183, 0.255) | (0.483, 0.062, 0.016)→(0.483, 0.062, 0.016) | 0.269→0.269 | 1.00 / 9.667 | 91192.327 | 789.958 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.213
- phase_score: 0.104
- phase_breakdown.place_subtask_score: 0.097
- phase_breakdown.approach_subtask_score: 0.132
- grasp_place_fitness: 0.191

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.191
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.213
- **Median Q (composite search score)**: -0.199
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.464


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.37864,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.10213,"approach_obj.pre_grasp_z_offset":0.19971,"descend_grasp.grasp_z_offset":0.04563,"grasp_phase.grasp_time":0.40323,"lift_obj.lift_z_offset":0.15828},"optimized_scores":{"best_composite_score":-0.23007,"best_fitness_score":0.13993,"best_task_score":0.12529},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":792.0,"contact_point_centroid":[0.63179,0.02294,-0.00049],"force_p95":232.30185,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1470.94437,"mean_force":222.77205,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38919,0.02129,0.11993]},{"body_a":"world","body_b":"link6","contact_count":982.0,"contact_point_centroid":[0.6246,0.049,-0.00022],"force_p95":480.67419,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":915.08496,"mean_force":288.0426,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.42373,0.0492,0.18856]},{"body_a":"world","body_b":"link5","contact_count":217.0,"contact_point_centroid":[0.59081,0.25766,-0.00016],"force_p95":538.21854,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":870.82321,"mean_force":297.15995,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.42165,0.15295,0.19002]},{"body_a":"world","body_b":"link6","contact_count":883.0,"contact_point_centroid":[0.61364,0.10645,-0.00027],"force_p95":387.00732,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":690.23046,"mean_force":287.48057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.41187,0.16936,0.17622]},{"body_a":"world","body_b":"link6","contact_count":543.0,"contact_point_centroid":[0.66037,0.06112,-0.00014],"force_p95":83.03244,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":683.67524,"mean_force":73.53009,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.45866,0.07422,0.1899]},{"body_a":"world","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.58646,0.07153,-0.00028],"force_p95":383.0771,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":603.01208,"mean_force":305.47519,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40965,0.18966,0.17213]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.52645,0.01582,-0.00349],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.87082,"mean_force":20.35776,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.37255,0.01192,0.04894]},{"body_a":"world","body_b":"link6","contact_count":273.0,"contact_point_centroid":[0.62374,0.06122,-0.00021],"force_p95":256.61214,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.54056,"mean_force":201.55164,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.41757,0.12202,0.17342]},{"body_a":"grasp_target","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.46025,0.04566,0.03891],"force_p95":3.68192,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.06023,"mean_force":1.73467,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38237,0.01204,0.05267]},{"body_a":"grasp_target","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.48549,0.02909,0.01062],"force_p95":1.51702,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.64338,"mean_force":0.64737,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.37408,0.01205,0.0575]},{"body_a":"world","body_b":"grasp_target","contact_count":3527.0,"contact_point_centroid":[0.44841,0.0504,-0.00219],"force_p95":0.13848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.64766,"mean_force":0.1433,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40279,0.01991,0.13121]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44285,0.05066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.42421,0.04942,0.18885]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.44285,0.05066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.45866,0.07422,0.18991]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.44285,0.05066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.41808,0.12147,0.17368]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44285,0.05066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40966,0.18929,0.17218]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44285,0.05066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.41292,0.16746,0.17798]}],"total_contact_groups":20},"final_pose_error":0.18094,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44285,0.05066,0.01602],"final_tcp_position":[0.42399,0.15753,0.17831],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1470.94437,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.44285,0.05066,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":225.11487,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4421.0,"raw_peak_contact_force":1470.94437,"subtask_id":"approach_subtask","tcp_end":[0.39645,0.03567,0.1463],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1391,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44285,0.05066,0.01602],"object_pos_start":[0.44285,0.05066,0.01602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31157,"object_z_max":0.01602,"peak_contact_force":394.58566,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4982.0,"raw_peak_contact_force":915.08496,"tcp_end":[0.45878,0.07405,0.19089],"tcp_start":[0.39645,0.03567,0.1463],"tcp_to_object_dist_end":0.17715,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.44285,0.05066,0.01602],"object_pos_start":[0.44285,0.05066,0.01602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31157,"object_z_max":0.01602,"peak_contact_force":69.96758,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3491.0,"raw_peak_contact_force":683.67524,"tcp_end":[0.45866,0.07421,0.18981],"tcp_start":[0.45866,0.07421,0.18981],"tcp_to_object_dist_end":0.17609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.44285,0.05066,0.01602],"object_pos_start":[0.44285,0.05066,0.01602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31157,"object_z_max":0.01602,"peak_contact_force":196.52274,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2585.0,"raw_peak_contact_force":286.54056,"tcp_end":[0.40997,0.13798,0.18119],"tcp_start":[0.45866,0.07421,0.18981],"tcp_to_object_dist_end":0.1897,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44285,0.05066,0.01602],"object_pos_start":[0.44285,0.05066,0.01602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31157,"object_z_max":0.01602,"peak_contact_force":339.00123,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9226.0,"raw_peak_contact_force":603.01208,"tcp_end":[0.40818,0.1846,0.16994],"tcp_start":[0.40997,0.13798,0.18119],"tcp_to_object_dist_end":0.20696,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44285,0.05066,0.01602],"object_pos_start":[0.44285,0.05066,0.01602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31157,"object_z_max":0.01602,"peak_contact_force":233.4125,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9311.0,"raw_peak_contact_force":870.82321,"subtask_id":"place_subtask","tcp_end":[0.42399,0.15753,0.17831],"tcp_start":[0.40818,0.1846,0.16994],"tcp_to_object_dist_end":0.19522,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.38562,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.139,"approach_obj.pre_grasp_z_offset":0.16432,"descend_grasp.grasp_z_offset":0.0582,"grasp_phase.grasp_time":0.3225,"lift_obj.lift_z_offset":0.11463},"optimized_scores":{"best_composite_score":-0.19863,"best_fitness_score":0.17137,"best_task_score":0.17148},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64947,-0.00807,-0.00044],"force_p95":284.55904,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1512.46449,"mean_force":209.20437,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.42662,-0.00915,0.15086]},{"body_a":"world","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.63416,-0.01998,-0.00024],"force_p95":476.3611,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":938.2133,"mean_force":297.42401,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44236,-0.03256,0.19989]},{"body_a":"world","body_b":"link6","contact_count":834.0,"contact_point_centroid":[0.61336,0.21813,-0.00032],"force_p95":525.65273,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":687.93195,"mean_force":386.96911,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61357,0.22425,0.29362]},{"body_a":"world","body_b":"link6","contact_count":375.0,"contact_point_centroid":[0.59765,-0.09701,-0.00017],"force_p95":396.00345,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":493.00426,"mean_force":288.30041,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.50103,-0.0316,0.23596]},{"body_a":"world","body_b":"link6","contact_count":540.0,"contact_point_centroid":[0.67569,-0.02063,-0.00013],"force_p95":76.27797,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":420.57694,"mean_force":73.18321,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46531,-0.06462,0.16825]},{"body_a":"world","body_b":"link6","contact_count":111.0,"contact_point_centroid":[0.54018,-0.0684,-4e-05],"force_p95":296.75885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.00965,"mean_force":191.19356,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54124,-0.04892,0.29282]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54074,-0.00181,-0.00379],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.59832,"mean_force":13.8521,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38982,-0.00463,0.04627]},{"body_a":"link5","body_b":"hand","contact_count":142.0,"contact_point_centroid":[0.5247,0.0274,0.18384],"force_p95":161.30775,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.15995,"mean_force":76.02498,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46455,-0.05941,0.17896]},{"body_a":"link5","body_b":"hand","contact_count":98.0,"contact_point_centroid":[0.50215,-0.16702,0.24268],"force_p95":179.9679,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.07196,"mean_force":142.34397,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52915,-0.06802,0.28332]},{"body_a":"link5","body_b":"hand","contact_count":559.0,"contact_point_centroid":[0.52128,0.02724,0.18252],"force_p95":29.77428,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.45573,"mean_force":5.01399,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46532,-0.06463,0.16829]},{"body_a":"grasp_target","body_b":"link7","contact_count":183.0,"contact_point_centroid":[0.51237,-0.02441,0.0377],"force_p95":4.12506,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.5987,"mean_force":0.86101,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40199,-0.00493,0.09077]},{"body_a":"grasp_target","body_b":"hand","contact_count":164.0,"contact_point_centroid":[0.50505,-0.03119,0.05049],"force_p95":2.34202,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.56326,"mean_force":0.86063,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40109,-0.00488,0.08811]},{"body_a":"world","body_b":"grasp_target","contact_count":3624.0,"contact_point_centroid":[0.507,-0.02523,-0.0024],"force_p95":0.33504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43638,"mean_force":0.164,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.43858,-0.00879,0.16254]},{"body_a":"grasp_target","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.51897,-0.03255,0.03979],"force_p95":0.72292,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.18939,"mean_force":0.46506,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.39428,0.00706,0.14008]},{"body_a":"grasp_target","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.53146,-0.03534,0.03727],"force_p95":1.09159,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.12422,"mean_force":0.85626,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.39025,-0.00814,0.13913]},{"body_a":"grasp_target","body_b":"link6","contact_count":410.0,"contact_point_centroid":[0.53203,0.04046,0.02168],"force_p95":0.82226,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.90908,"mean_force":0.51248,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55982,0.03285,0.30118]}],"total_contact_groups":27},"final_pose_error":0.08652,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49736,0.08433,0.01602],"final_tcp_position":[0.61961,0.22945,0.29341],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273020.09022,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4996,-0.02591,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.3365,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":338.72716,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4997.0,"raw_peak_contact_force":1512.46449,"subtask_id":"approach_subtask","tcp_end":[0.45933,-0.01823,0.19865],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18717,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4996,-0.02591,0.01602],"object_pos_start":[0.4996,-0.02591,0.01602],"object_to_goal_dist_end":0.3365,"object_to_goal_dist_start":0.3365,"object_z_max":0.01602,"peak_contact_force":374.94262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5123.0,"raw_peak_contact_force":938.2133,"tcp_end":[0.46535,-0.06485,0.16938],"tcp_start":[0.45933,-0.01823,0.19865],"tcp_to_object_dist_end":0.16189,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4996,-0.02591,0.01602],"object_pos_start":[0.4996,-0.02591,0.01602],"object_to_goal_dist_end":0.3365,"object_to_goal_dist_start":0.3365,"object_z_max":0.01602,"peak_contact_force":69.91457,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4076.0,"raw_peak_contact_force":420.57694,"tcp_end":[0.4653,-0.06466,0.16818],"tcp_start":[0.46531,-0.06465,0.16818],"tcp_to_object_dist_end":0.16072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.50004,0.00795,0.01602],"object_pos_start":[0.4996,-0.02591,0.01602],"object_to_goal_dist_end":0.31161,"object_to_goal_dist_start":0.3365,"object_z_max":0.02124,"peak_contact_force":335.61246,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3693.0,"raw_peak_contact_force":493.00426,"tcp_end":[0.533,-0.06691,0.28447],"tcp_start":[0.4653,-0.06466,0.16818],"tcp_to_object_dist_end":0.28063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.49736,0.08433,0.01602],"object_pos_start":[0.50004,0.00795,0.01602],"object_to_goal_dist_end":0.2645,"object_to_goal_dist_start":0.31161,"object_z_max":0.01711,"peak_contact_force":273020.09022,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6972.0,"raw_peak_contact_force":326.00965,"tcp_end":[0.60645,0.21189,0.33533],"tcp_start":[0.533,-0.06691,0.28447],"tcp_to_object_dist_end":0.36074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.49736,0.08433,0.01602],"object_pos_start":[0.49736,0.08433,0.01602],"object_to_goal_dist_end":0.2645,"object_to_goal_dist_start":0.2645,"object_z_max":0.01602,"peak_contact_force":273006.69444,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8427.0,"raw_peak_contact_force":687.93195,"subtask_id":"place_subtask","tcp_end":[0.61961,0.22945,0.29341],"tcp_start":[0.60645,0.21189,0.33533],"tcp_to_object_dist_end":0.33608,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.84783,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.13487,"approach_obj.pre_grasp_z_offset":0.13882,"descend_grasp.grasp_z_offset":0.04871,"grasp_phase.grasp_time":0.99794,"lift_obj.lift_z_offset":0.14933},"optimized_scores":{"best_composite_score":-0.17874,"best_fitness_score":0.19126,"best_task_score":0.21251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64874,-0.00876,-0.00045],"force_p95":270.06975,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1514.57243,"mean_force":209.85467,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.42568,-0.00983,0.15048]},{"body_a":"world","body_b":"link6","contact_count":980.0,"contact_point_centroid":[0.63203,-0.02151,-0.00024],"force_p95":482.75121,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":938.17496,"mean_force":304.06608,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.44209,-0.03387,0.20197]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.63747,0.15281,-0.00031],"force_p95":547.71909,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":811.12018,"mean_force":386.60508,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.63502,0.15827,0.29359]},{"body_a":"link5","body_b":"hand","contact_count":204.0,"contact_point_centroid":[0.49536,-0.14095,0.24734],"force_p95":280.38474,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.3601,"mean_force":210.88079,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.50874,-0.04047,0.27374]},{"body_a":"world","body_b":"link6","contact_count":289.0,"contact_point_centroid":[0.59342,-0.08604,-0.00019],"force_p95":371.38555,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.80126,"mean_force":289.25897,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.49047,-0.03641,0.24898]},{"body_a":"world","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.67632,-0.02435,-0.00013],"force_p95":76.4809,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":455.32865,"mean_force":72.62985,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46504,-0.06687,0.16751]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.5403,-0.00224,-0.00381],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.2813,"mean_force":13.8818,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.38938,-0.005,0.04625]},{"body_a":"world","body_b":"link6","contact_count":237.0,"contact_point_centroid":[0.54104,-0.04797,-2e-05],"force_p95":260.36403,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.51257,"mean_force":183.41929,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55061,-0.02989,0.29332]},{"body_a":"link5","body_b":"hand","contact_count":139.0,"contact_point_centroid":[0.52485,0.02463,0.18342],"force_p95":159.43422,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.3754,"mean_force":76.58427,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.46438,-0.0619,0.17823]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.49235,-0.15833,0.24358],"force_p95":71.43195,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.58454,"mean_force":26.20462,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53121,-0.06331,0.28778]},{"body_a":"link5","body_b":"hand","contact_count":560.0,"contact_point_centroid":[0.52176,0.02446,0.18209],"force_p95":28.20798,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.41664,"mean_force":4.84929,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46505,-0.06687,0.16754]},{"body_a":"grasp_target","body_b":"link7","contact_count":270.0,"contact_point_centroid":[0.52753,-0.01877,0.03303],"force_p95":2.79737,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.98896,"mean_force":0.52904,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.40451,-0.00563,0.10087]},{"body_a":"grasp_target","body_b":"hand","contact_count":120.0,"contact_point_centroid":[0.50319,-0.03549,0.04642],"force_p95":2.53005,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.35602,"mean_force":0.96181,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.39888,-0.00516,0.0797]},{"body_a":"world","body_b":"grasp_target","contact_count":3747.0,"contact_point_centroid":[0.51487,-0.03031,-0.00224],"force_p95":0.27484,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.35987,"mean_force":0.15541,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.43663,-0.00933,0.16058]},{"body_a":"grasp_target","body_b":"link6","contact_count":575.0,"contact_point_centroid":[0.53066,0.00261,0.02306],"force_p95":1.29884,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.4872,"mean_force":0.71156,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56955,0.01677,0.29438]},{"body_a":"grasp_target","body_b":"link6","contact_count":109.0,"contact_point_centroid":[0.55007,-0.01297,0.02334],"force_p95":0.65623,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.96427,"mean_force":0.38523,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.39678,-0.00519,0.08401]}],"total_contact_groups":25},"final_pose_error":0.11683,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.50973,0.05125,0.01602],"final_tcp_position":[0.64398,0.16318,0.2932],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273004.12069,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50893,-0.03035,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28174,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":335.90798,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5156.0,"raw_peak_contact_force":1514.57243,"subtask_id":"approach_subtask","tcp_end":[0.45843,-0.01917,0.20064],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19173,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50893,-0.03035,0.01602],"object_pos_start":[0.50893,-0.03035,0.01602],"object_to_goal_dist_end":0.28174,"object_to_goal_dist_start":0.28174,"object_z_max":0.01602,"peak_contact_force":382.64211,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5119.0,"raw_peak_contact_force":938.17496,"tcp_end":[0.46516,-0.06675,0.16862],"tcp_start":[0.45843,-0.01917,0.20064],"tcp_to_object_dist_end":0.16288,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50893,-0.03035,0.01602],"object_pos_start":[0.50893,-0.03035,0.01602],"object_to_goal_dist_end":0.28174,"object_to_goal_dist_start":0.28174,"object_z_max":0.01602,"peak_contact_force":1366.84211,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4089.0,"raw_peak_contact_force":455.32865,"tcp_end":[0.46504,-0.06691,0.16743],"tcp_start":[0.46504,-0.0669,0.16743],"tcp_to_object_dist_end":0.16182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":345.0,"n_steps_budget":600.0,"object_pos_end":[0.50893,-0.03035,0.01602],"object_pos_start":[0.50893,-0.03035,0.01602],"object_to_goal_dist_end":0.28174,"object_to_goal_dist_start":0.28174,"object_z_max":0.01602,"peak_contact_force":1366.84211,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3378.0,"raw_peak_contact_force":561.3601,"tcp_end":[0.53098,-0.06304,0.28726],"tcp_start":[0.46504,-0.06691,0.16743],"tcp_to_object_dist_end":0.27409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.50971,0.0512,0.01605],"object_pos_start":[0.50893,-0.03035,0.01602],"object_to_goal_dist_end":0.23233,"object_to_goal_dist_start":0.28174,"object_z_max":0.01692,"peak_contact_force":0.12384,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6033.0,"raw_peak_contact_force":304.51257,"tcp_end":[0.6257,0.14919,0.30219],"tcp_start":[0.53098,-0.06304,0.28726],"tcp_to_object_dist_end":0.32393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50973,0.05125,0.01602],"object_pos_start":[0.50971,0.0512,0.01605],"object_to_goal_dist_end":0.23231,"object_to_goal_dist_start":0.23233,"object_z_max":0.01605,"peak_contact_force":336.87349,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9263.0,"raw_peak_contact_force":811.12018,"subtask_id":"place_subtask","tcp_end":[0.64398,0.16318,0.2932],"tcp_start":[0.6257,0.14919,0.30219],"tcp_to_object_dist_end":0.3277,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```