## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1653 | 0.31 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1203 | 0.15 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2145 | 0.15 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5552 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5550 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.165) — your mutation base

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

- **Composite score**: 0.165
- **task_score** (E): 0.306
- **fitness_score**: 0.615  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1132 |
| descend_grasp | 1.00 | 1.00 | 0.1398 |
| grasp_phase | 1.00 | 1.00 | 0.0130 |
| lift_obj | 1.00 | 1.00 | 0.1195 |
| approach_goal | 1.00 | 0.67 | 0.2563 |
| descend_place | 1.00 | 1.00 | 0.1049 |
| release_obj | 1.00 | 1.00 | 0.0201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.000, 0.195) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 34.815 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.514, 0.000, 0.195)→(0.516, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.516, -0.001, 0.055)→(0.508, -0.001, 0.046) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 44.333 | 0.152 | 0.193 |
| lift_obj | lift | 1.00 / step_budget | (0.508, -0.001, 0.046)→(0.517, -0.001, 0.165) | (0.522, -0.001, 0.026)→(0.528, -0.001, 0.142) | 0.290→0.235 | 1.00 / 37.333 | 0.087 | 0.444 |
| approach_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.165)→(0.602, 0.197, 0.300) | (0.528, -0.001, 0.142)→(0.612, 0.193, 0.235) | 0.235→0.064 | 0.67 / 21.333 | 0.058 | 0.251 |
| descend_place | descend | 1.00 / step_budget | (0.602, 0.197, 0.300)→(0.604, 0.204, 0.195) | (0.612, 0.193, 0.235)→(0.615, 0.201, 0.103) | 0.064→0.102 | 1.00 / 23.000 | 3249.613 | 0.989 |
| release_obj | release | 1.00 / step_budget | (0.604, 0.204, 0.195)→(0.598, 0.202, 0.215) | (0.615, 0.201, 0.103)→(0.604, 0.196, 0.027) | 0.102→0.179 | 1.00 / 2.667 | 0.163 | 1.029 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.368
- phase_score: 0.591
- phase_breakdown.place_subtask_score: 0.689
- phase_breakdown.approach_subtask_score: 0.200
- grasp_place_fitness: 0.648

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.648
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.368
- **Median Q (composite search score)**: 0.163
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_grasp.grasp_z_offset
- **Final σ (mean)**: 0.441


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90964,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.11425,"approach_obj.pre_grasp_z_offset":0.11387,"descend_grasp.grasp_z_offset":0.02354,"descend_place.place_z_offset":-0.00337,"lift_obj.lift_z_offset":0.14961,"release_obj.release_time":0.26291},"optimized_scores":{"best_composite_score":0.13458,"best_fitness_score":0.58458,"best_task_score":0.25288},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":407.0,"contact_point_centroid":[0.59753,0.20628,-0.00545],"force_p95":1.14992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.39262,"mean_force":0.26529,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57658,0.22328,0.27692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8217.0,"contact_point_centroid":[0.51492,0.13683,0.22172],"force_p95":0.14261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39876,"mean_force":0.09181,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51612,0.11799,0.22431]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.48111,0.04639,-0.00154],"force_p95":0.29828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38825,"mean_force":0.06122,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46903,0.04649,0.05124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5428.0,"contact_point_centroid":[0.47213,0.06551,0.10109],"force_p95":0.10165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32125,"mean_force":0.06871,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.4722,0.04668,0.10135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5381.0,"contact_point_centroid":[0.47433,0.02801,0.09984],"force_p95":0.11768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30918,"mean_force":0.06923,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47219,0.04668,0.10141]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04867,-0.00219],"force_p95":0.17214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21627,"mean_force":0.13614,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47115,0.04672,0.05072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9592.0,"contact_point_centroid":[0.52623,0.10999,0.22964],"force_p95":0.11774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20591,"mean_force":0.07731,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52137,0.12718,0.23361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3829.0,"contact_point_centroid":[0.47179,0.0277,0.04826],"force_p95":0.09711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19703,"mean_force":0.05725,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46999,0.04661,0.04951]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59775,0.20715,-0.00199],"force_p95":0.13016,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16668,"mean_force":0.12302,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57447,0.22415,0.24627]},{"body_a":"world","body_b":"grasp_target","contact_count":1100.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49067,0.01969,0.23251]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47878,0.04412,0.10939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4103.0,"contact_point_centroid":[0.4699,0.06568,0.04982],"force_p95":0.09461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09742,"mean_force":0.05578,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47,0.04661,0.04951]},{"body_a":"left_finger","body_b":"right_finger","contact_count":319.0,"contact_point_centroid":[0.57682,0.22369,0.27035],"force_p95":0.01446,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01588,"mean_force":0.01134,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57692,0.22389,0.26813]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.57624,0.22473,0.24399],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00997,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.57632,0.22495,0.24168]}],"total_contact_groups":14},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59776,0.20717,0.02602],"final_tcp_position":[0.57792,0.22558,0.24636],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.66404,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.48203,0.04112,0.16214],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47809,0.04737,0.05809],"tcp_start":[0.48203,0.04112,0.16214],"tcp_to_object_dist_end":0.03242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48283,0.04756,0.0252],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29123,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17319,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9732.0,"raw_peak_contact_force":0.21627,"tcp_end":[0.46996,0.0466,0.04948],"tcp_start":[0.47809,0.04737,0.05809],"tcp_to_object_dist_end":0.02749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":342.0,"n_steps_budget":810.0,"object_pos_end":[0.48675,0.04827,0.12696],"object_pos_start":[0.48283,0.04756,0.0252],"object_to_goal_dist_end":0.22886,"object_to_goal_dist_start":0.29123,"object_z_max":0.1267,"peak_contact_force":0.11466,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10894.0,"raw_peak_contact_force":0.38825,"tcp_end":[0.47779,0.04709,0.15556],"tcp_start":[0.46996,0.0466,0.04948],"tcp_to_object_dist_end":0.02999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.58648,0.20139,0.18255],"object_pos_start":[0.48675,0.04827,0.12696],"object_to_goal_dist_end":0.05544,"object_to_goal_dist_start":0.22886,"object_z_max":0.27649,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17809.0,"raw_peak_contact_force":0.39876,"tcp_end":[0.57524,0.21979,0.32835],"tcp_start":[0.47779,0.04709,0.15556],"tcp_to_object_dist_end":0.14739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.59808,0.2081,0.02628],"object_pos_start":[0.58648,0.20139,0.18255],"object_to_goal_dist_end":0.20589,"object_to_goal_dist_start":0.05544,"object_z_max":0.18255,"peak_contact_force":9748.66404,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":726.0,"raw_peak_contact_force":2.39262,"subtask_id":"place_subtask","tcp_end":[0.57792,0.22558,0.24636],"tcp_start":[0.57524,0.21979,0.32835],"tcp_to_object_dist_end":0.22169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59776,0.20717,0.02602],"object_pos_start":[0.59808,0.2081,0.02628],"object_to_goal_dist_end":0.20622,"object_to_goal_dist_start":0.20589,"object_z_max":0.02628,"peak_contact_force":0.12289,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.16668,"tcp_end":[0.5734,0.22366,0.26625],"tcp_start":[0.57792,0.22558,0.24636],"tcp_to_object_dist_end":0.24203,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91803,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.11519,"approach_obj.pre_grasp_z_offset":0.1472,"descend_grasp.grasp_z_offset":0.02,"descend_place.place_z_offset":-0.04586,"lift_obj.lift_z_offset":0.16744,"release_obj.release_time":0.74134},"optimized_scores":{"best_composite_score":0.16315,"best_fitness_score":0.61315,"best_task_score":0.29776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.59445,0.21942,-0.00725],"force_p95":1.22157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49447,"mean_force":0.37809,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60034,0.22208,0.18988]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.5345,-0.02081,-0.00137],"force_p95":0.406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47024,"mean_force":0.09716,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52165,-0.02074,0.04528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.61246,0.20645,0.17297],"force_p95":0.09554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33112,"mean_force":0.05949,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60389,0.22353,0.17521]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":937.0,"contact_point_centroid":[0.6007,0.2424,0.17632],"force_p95":0.09486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3217,"mean_force":0.05865,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.60391,0.22354,0.17524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9986.0,"contact_point_centroid":[0.52642,-0.00167,0.1088],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30633,"mean_force":0.0485,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52531,-0.02084,0.10636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9141.0,"contact_point_centroid":[0.52593,-0.04007,0.11038],"force_p95":0.0736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30462,"mean_force":0.05194,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52539,-0.02084,0.10728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3281.0,"contact_point_centroid":[0.60183,0.23869,0.24675],"force_p95":0.10751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2925,"mean_force":0.06945,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60497,0.21985,0.24578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3478.0,"contact_point_centroid":[0.61395,0.203,0.24399],"force_p95":0.10624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26318,"mean_force":0.06639,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60498,0.21988,0.24519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15528.0,"contact_point_centroid":[0.57043,0.07567,0.23734],"force_p95":0.08473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18108,"mean_force":0.05827,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5657,0.09407,0.23636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02133,-0.00205],"force_p95":0.13793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17232,"mean_force":0.12686,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52387,-0.02077,0.04541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15913.0,"contact_point_centroid":[0.56448,0.1132,0.23784],"force_p95":0.08564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16357,"mean_force":0.05653,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56577,0.09429,0.2365]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51251,-0.00828,0.24815]},{"body_a":"world","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52785,-0.01908,0.12301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5801.0,"contact_point_centroid":[0.52323,-0.00152,0.0469],"force_p95":0.06436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10068,"mean_force":0.03805,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52263,-0.02075,0.04396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5142.0,"contact_point_centroid":[0.52314,-0.04006,0.04708],"force_p95":0.06902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07876,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52263,-0.02075,0.04397]}],"total_contact_groups":15},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59671,0.22214,0.02629],"final_tcp_position":[0.60621,0.22435,0.18079],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":51.47648,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":51.47648,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.52719,-0.01734,0.19398],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53126,-0.02087,0.05417],"tcp_start":[0.52719,-0.01734,0.19398],"tcp_to_object_dist_end":0.02874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02107,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31668,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13741,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12743.0,"raw_peak_contact_force":0.17232,"tcp_end":[0.5226,-0.02075,0.04393],"tcp_start":[0.53126,-0.02087,0.05417],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":445.0,"n_steps_budget":930.0,"object_pos_end":[0.54469,-0.02143,0.15326],"object_pos_start":[0.53696,-0.02107,0.02579],"object_to_goal_dist_end":0.26331,"object_to_goal_dist_start":0.31668,"object_z_max":0.15301,"peak_contact_force":0.07264,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19205.0,"raw_peak_contact_force":0.47024,"tcp_end":[0.53208,-0.02098,0.17407],"tcp_start":[0.5226,-0.02075,0.04393],"tcp_to_object_dist_end":0.02434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.61391,0.22015,0.28169],"object_pos_start":[0.54469,-0.02143,0.15326],"object_to_goal_dist_end":0.07475,"object_to_goal_dist_start":0.26331,"object_z_max":0.28157,"peak_contact_force":0.086,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31441.0,"raw_peak_contact_force":0.18108,"tcp_end":[0.60472,0.21585,0.3076],"tcp_start":[0.53208,-0.02098,0.17407],"tcp_to_object_dist_end":0.02783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.61169,0.22845,0.15212],"object_pos_start":[0.61391,0.22015,0.28169],"object_to_goal_dist_end":0.05531,"object_to_goal_dist_start":0.07475,"object_z_max":0.28171,"peak_contact_force":0.08507,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6759.0,"raw_peak_contact_force":0.2925,"subtask_id":"place_subtask","tcp_end":[0.60621,0.22435,0.18079],"tcp_start":[0.60472,0.21585,0.3076],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59671,0.22214,0.02629],"object_pos_start":[0.61169,0.22845,0.15212],"object_to_goal_dist_end":0.18172,"object_to_goal_dist_start":0.05531,"object_z_max":0.15212,"peak_contact_force":0.18886,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2087.0,"raw_peak_contact_force":1.49447,"tcp_end":[0.60028,0.22206,0.19958],"tcp_start":[0.60621,0.22435,0.18079],"tcp_to_object_dist_end":0.17332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90964,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.10195,"approach_obj.pre_grasp_z_offset":0.18572,"descend_grasp.grasp_z_offset":0.02019,"descend_place.place_z_offset":-0.03637,"lift_obj.lift_z_offset":0.15832,"release_obj.release_time":0.53149},"optimized_scores":{"best_composite_score":0.19808,"best_fitness_score":0.64808,"best_task_score":0.36764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":206.0,"contact_point_centroid":[0.61731,0.15822,-0.00635],"force_p95":1.12876,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42658,"mean_force":0.33817,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62131,0.15989,0.16635]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.54265,-0.02829,-0.00135],"force_p95":0.41813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47471,"mean_force":0.10749,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53013,-0.02836,0.04513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":934.0,"contact_point_centroid":[0.6236,0.18011,0.1541],"force_p95":0.10323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33968,"mean_force":0.06088,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62527,0.16104,0.15363]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":957.0,"contact_point_centroid":[0.63245,0.14326,0.1523],"force_p95":0.10076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3337,"mean_force":0.06059,"phase_index":6.0,"phase_name":"release_obj","phase_type":"release","tcp_position_centroid":[0.62526,0.16104,0.15362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9642.0,"contact_point_centroid":[0.53476,-0.00933,0.10443],"force_p95":0.07636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30424,"mean_force":0.04806,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53376,-0.02848,0.10191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8496.0,"contact_point_centroid":[0.53379,-0.04771,0.1056],"force_p95":0.07557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30155,"mean_force":0.05313,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53378,-0.02848,0.10207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2725.0,"contact_point_centroid":[0.62449,0.17651,0.21549],"force_p95":0.11636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28232,"mean_force":0.07154,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62594,0.15749,0.21481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2823.0,"contact_point_centroid":[0.63323,0.13991,0.21252],"force_p95":0.11722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26299,"mean_force":0.06906,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62598,0.1576,0.21327]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02927,-0.00208],"force_p95":0.14527,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19122,"mean_force":0.12893,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.5323,-0.02841,0.04522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13275.0,"contact_point_centroid":[0.58476,0.04399,0.21357],"force_p95":0.0849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17373,"mean_force":0.05645,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58132,0.06277,0.21213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13629.0,"contact_point_centroid":[0.58045,0.08129,0.2135],"force_p95":0.08445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16761,"mean_force":0.05461,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58113,0.06234,0.21191]},{"body_a":"world","body_b":"grasp_target","contact_count":676.0,"contact_point_centroid":[0.5456,-0.02923,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51536,-0.0107,0.26537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5795.0,"contact_point_centroid":[0.53176,-0.00916,0.04667],"force_p95":0.06548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13352,"mean_force":0.03809,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53105,-0.02838,0.04373]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53498,-0.02553,0.1404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.53126,-0.04768,0.04718],"force_p95":0.07126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07553,"mean_force":0.04446,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53105,-0.02838,0.04373]}],"total_contact_groups":15},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61803,0.15941,0.02766],"final_tcp_position":[0.62782,0.16164,0.15925],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":52.84455,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":170.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":52.84455,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":676.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53283,-0.02254,0.22906],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53975,-0.02859,0.05423],"tcp_start":[0.53283,-0.02254,0.22906],"tcp_to_object_dist_end":0.02881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54556,-0.02885,0.02569],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26084,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14442,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12557.0,"raw_peak_contact_force":0.19122,"tcp_end":[0.53102,-0.02838,0.04369],"tcp_start":[0.53975,-0.02859,0.05423],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":422.0,"n_steps_budget":900.0,"object_pos_end":[0.55292,-0.02932,0.14445],"object_pos_start":[0.54556,-0.02885,0.02569],"object_to_goal_dist_end":0.21254,"object_to_goal_dist_start":0.26084,"object_z_max":0.1442,"peak_contact_force":0.07502,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18220.0,"raw_peak_contact_force":0.47471,"tcp_end":[0.54049,-0.02869,0.16491],"tcp_start":[0.53102,-0.02838,0.04369],"tcp_to_object_dist_end":0.02395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.63553,0.1573,0.23969],"object_pos_start":[0.55292,-0.02932,0.14445],"object_to_goal_dist_end":0.06328,"object_to_goal_dist_start":0.21254,"object_z_max":0.23958,"peak_contact_force":0.08664,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26904.0,"raw_peak_contact_force":0.17373,"tcp_end":[0.62523,0.15391,0.2643],"tcp_start":[0.54049,-0.02869,0.16491],"tcp_to_object_dist_end":0.0269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.63569,0.16519,0.13204],"object_pos_start":[0.63553,0.1573,0.23969],"object_to_goal_dist_end":0.04497,"object_to_goal_dist_start":0.06328,"object_z_max":0.2397,"peak_contact_force":0.08862,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5548.0,"raw_peak_contact_force":0.28232,"subtask_id":"place_subtask","tcp_end":[0.62782,0.16164,0.15925],"tcp_start":[0.62523,0.15391,0.2643],"tcp_to_object_dist_end":0.02855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61803,0.15941,0.02766],"object_pos_start":[0.63569,0.16519,0.13204],"object_to_goal_dist_end":0.1501,"object_to_goal_dist_start":0.04497,"object_z_max":0.13204,"peak_contact_force":0.17847,"phase_name":"release_obj","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2097.0,"raw_peak_contact_force":1.42658,"tcp_end":[0.62121,0.15987,0.17789],"tcp_start":[0.62782,0.16164,0.15925],"tcp_to_object_dist_end":0.15026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```