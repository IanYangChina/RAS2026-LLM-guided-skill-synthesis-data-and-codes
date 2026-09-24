## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0534 | 0.23 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2025 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1653 | 0.31 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1203 | 0.15 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2145 | 0.15 | ❌ rejected |

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

## Current Skill (Q=0.053) — your mutation base

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

- **Composite score**: 0.053
- **task_score** (E): 0.234
- **fitness_score**: 0.573  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1485 |
| descend_grasp | 1.00 | 1.00 | 0.1038 |
| grasp_phase | 1.00 | 1.00 | 0.0132 |
| lift_obj | 1.00 | 1.00 | 0.1140 |
| approach_goal | 1.00 | 0.67 | 0.2539 |
| descend_place | 1.00 | 1.00 | 0.0822 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.010, 0.163) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.518, 0.010, 0.163)→(0.517, 0.002, 0.060) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.517, 0.002, 0.060)→(0.508, 0.002, 0.050) | (0.522, -0.001, 0.026)→(0.522, 0.001, 0.025) | 0.289→0.288 | 1.00 / 34.000 | 0.178 | 0.209 |
| lift_obj | lift | 1.00 / step_budget | (0.508, 0.002, 0.050)→(0.517, 0.001, 0.164) | (0.522, 0.001, 0.025)→(0.525, 0.000, 0.134) | 0.288→0.235 | 1.00 / 26.667 | 0.141 | 0.384 |
| approach_goal | approach | 1.00 / step_budget | (0.517, 0.001, 0.164)→(0.599, 0.190, 0.310) | (0.525, 0.000, 0.134)→(0.564, 0.106, 0.092) | 0.235→0.174 | 0.67 / 5.333 | 0.083 | 1.655 |
| descend_place | descend | 1.00 / step_budget | (0.599, 0.190, 0.310)→(0.603, 0.202, 0.229) | (0.564, 0.106, 0.092)→(0.567, 0.106, 0.023) | 0.174→0.219 | 1.00 / 8.000 | 0.130 | 0.679 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.287
- phase_score: 0.444
- phase_breakdown.place_subtask_score: 0.491
- phase_breakdown.approach_subtask_score: 0.258
- grasp_place_fitness: 0.602

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.602
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.287
- **Median Q (composite search score)**: 0.043
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_grasp.grasp_z_offset
- **Final σ (mean)**: 0.405


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12658,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.051,"approach_goal.goal_approach_arc_height":0.10821,"approach_obj.approach_arc_height":0.12525,"approach_obj.pre_grasp_z_offset":0.12344,"descend_grasp.grasp_z_offset":0.02003,"descend_place.place_z_offset":0.00283,"grasp_phase.grasp_time":0.44457,"lift_obj.lift_z_offset":0.17987},"optimized_scores":{"best_composite_score":0.03604,"best_fitness_score":0.55604,"best_task_score":0.19867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":742.0,"contact_point_centroid":[0.53758,0.10769,-0.00407],"force_p95":0.90778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.5546,"mean_force":0.2064,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5542,0.18309,0.31917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.48448,0.07847,0.25936],"force_p95":0.14763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37056,"mean_force":0.10905,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48231,0.05981,0.26306]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.48074,0.04963,-0.00135],"force_p95":0.29456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33464,"mean_force":0.06258,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46913,0.04906,0.05289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5081.0,"contact_point_centroid":[0.47239,0.06783,0.11448],"force_p95":0.14255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33426,"mean_force":0.08884,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.4722,0.04895,0.11675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6290.0,"contact_point_centroid":[0.47372,0.03069,0.1109],"force_p95":0.12176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27094,"mean_force":0.07187,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47192,0.04894,0.11301]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4957.0,"contact_point_centroid":[0.48675,0.04273,0.2579],"force_p95":0.1419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24723,"mean_force":0.09649,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48256,0.06028,0.26211]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04886,-0.00204],"force_p95":0.13994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1606,"mean_force":0.12624,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47125,0.04931,0.05268]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.4827,0.04873,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.49186,0.04888,0.24631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2925.0,"contact_point_centroid":[0.47058,0.06837,0.05025],"force_p95":0.1124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13169,"mean_force":0.07082,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04919,0.05148]},{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.53711,0.10654,-0.00199],"force_p95":0.12674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12762,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5739,0.21865,0.27256]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47914,0.05507,0.11504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4243.0,"contact_point_centroid":[0.47187,0.03049,0.05019],"force_p95":0.0892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09533,"mean_force":0.05114,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.4701,0.04919,0.05148]},{"body_a":"left_finger","body_b":"right_finger","contact_count":728.0,"contact_point_centroid":[0.55616,0.18662,0.3199],"force_p95":0.01304,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01079,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55634,0.18679,0.3176]},{"body_a":"left_finger","body_b":"right_finger","contact_count":341.0,"contact_point_centroid":[0.57364,0.21835,0.27513],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57388,0.21861,0.27278]}],"total_contact_groups":14},"final_pose_error":0.01967,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53712,0.10655,0.02602],"final_tcp_position":[0.57615,0.22261,0.25107],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.5546,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.48194,0.06021,0.16963],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47835,0.0501,0.06032],"tcp_start":[0.48194,0.06021,0.16963],"tcp_to_object_dist_end":0.0346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48254,0.04947,0.0258],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28973,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1388,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8968.0,"raw_peak_contact_force":0.1606,"tcp_end":[0.47007,0.04919,0.05145],"tcp_start":[0.47835,0.0501,0.06032],"tcp_to_object_dist_end":0.02852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":430.0,"n_steps_budget":960.0,"object_pos_end":[0.48504,0.04896,0.15505],"object_pos_start":[0.48254,0.04947,0.0258],"object_to_goal_dist_end":0.21778,"object_to_goal_dist_start":0.28973,"object_z_max":0.15478,"peak_contact_force":0.14149,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11447.0,"raw_peak_contact_force":0.33464,"tcp_end":[0.47808,0.0491,0.1864],"tcp_start":[0.47007,0.04919,0.05145],"tcp_to_object_dist_end":0.03211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.53712,0.10656,0.02602],"object_pos_start":[0.48504,0.04896,0.15505],"object_to_goal_dist_end":0.24241,"object_to_goal_dist_start":0.21778,"object_z_max":0.29005,"peak_contact_force":0.12762,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10556.0,"raw_peak_contact_force":2.5546,"tcp_end":[0.57254,0.21514,0.29232],"tcp_start":[0.47808,0.0491,0.1864],"tcp_to_object_dist_end":0.28975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.53712,0.10655,0.02602],"object_pos_start":[0.53712,0.10656,0.02602],"object_to_goal_dist_end":0.24242,"object_to_goal_dist_start":0.24241,"object_z_max":0.02602,"peak_contact_force":0.12298,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":661.0,"raw_peak_contact_force":0.12762,"subtask_id":"place_subtask","tcp_end":[0.57615,0.22261,0.25107],"tcp_start":[0.57254,0.21514,0.29232],"tcp_to_object_dist_end":0.2562,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81622,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.14872,"approach_goal.goal_approach_arc_height":0.0502,"approach_obj.approach_arc_height":0.18132,"approach_obj.pre_grasp_z_offset":0.0502,"descend_grasp.grasp_z_offset":0.02,"descend_place.place_z_offset":0.01656,"grasp_phase.grasp_time":0.85808,"lift_obj.lift_z_offset":0.14693},"optimized_scores":{"best_composite_score":0.08154,"best_fitness_score":0.60154,"best_task_score":0.28728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":495.0,"contact_point_centroid":[0.61967,0.18331,-0.00501],"force_p95":1.12694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78816,"mean_force":0.24089,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60425,0.21576,0.27795]},{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.5348,-0.01383,-0.00192],"force_p95":0.36342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47837,"mean_force":0.08121,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.5211,-0.01425,0.04939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8683.0,"contact_point_centroid":[0.55493,0.07651,0.24969],"force_p95":0.14983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35649,"mean_force":0.10001,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55325,0.05753,0.25281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7020.0,"contact_point_centroid":[0.52628,-0.0339,0.09947],"force_p95":0.10026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34916,"mean_force":0.0582,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52521,-0.01538,0.09828]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53731,-0.02096,-0.00251],"force_p95":0.2646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31612,"mean_force":0.15824,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52326,-0.01419,0.04851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5237.0,"contact_point_centroid":[0.52781,0.00359,0.09626],"force_p95":0.13872,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30585,"mean_force":0.07611,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52509,-0.01536,0.09729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13486.0,"contact_point_centroid":[0.5553,0.03567,0.24711],"force_p95":0.12154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2873,"mean_force":0.06923,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55185,0.05326,0.24839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3469.0,"contact_point_centroid":[0.52493,0.00478,0.04656],"force_p95":0.1044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15705,"mean_force":0.05973,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52203,-0.01418,0.04707]},{"body_a":"world","body_b":"grasp_target","contact_count":2008.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51452,0.03525,0.19166]},{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53025,-0.00847,0.07187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5226.0,"contact_point_centroid":[0.52326,-0.03369,0.04862],"force_p95":0.10165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10615,"mean_force":0.04792,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52206,-0.01418,0.0471]},{"body_a":"left_finger","body_b":"right_finger","contact_count":455.0,"contact_point_centroid":[0.60408,0.21628,0.27517],"force_p95":0.01356,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01109,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60449,0.21656,0.27307]}],"total_contact_groups":12},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61922,0.18273,0.02603],"final_tcp_position":[0.60614,0.22193,0.24227],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.78816,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53073,-0.00315,0.08508],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":78.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":312.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5307,-0.01396,0.05737],"tcp_start":[0.53073,-0.00315,0.08508],"tcp_to_object_dist_end":0.03282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5374,-0.01688,0.02422],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3142,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.25142,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10495.0,"raw_peak_contact_force":0.31612,"tcp_end":[0.52201,-0.01418,0.04704],"tcp_start":[0.5307,-0.01396,0.05737],"tcp_to_object_dist_end":0.02766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":364.0,"n_steps_budget":810.0,"object_pos_end":[0.54283,-0.01891,0.12485],"object_pos_start":[0.5374,-0.01688,0.02422],"object_to_goal_dist_end":0.26873,"object_to_goal_dist_start":0.3142,"object_z_max":0.1246,"peak_contact_force":0.14608,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12354.0,"raw_peak_contact_force":0.47837,"tcp_end":[0.53193,-0.01656,0.15201],"tcp_start":[0.52201,-0.01418,0.04704],"tcp_to_object_dist_end":0.02935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61188,0.18355,0.23495],"object_pos_start":[0.54283,-0.01891,0.12485],"object_to_goal_dist_end":0.0521,"object_to_goal_dist_start":0.26873,"object_z_max":0.30342,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22169.0,"raw_peak_contact_force":0.35649,"tcp_end":[0.60186,0.20523,0.34493],"tcp_start":[0.53193,-0.01656,0.15201],"tcp_to_object_dist_end":0.11254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.61922,0.18273,0.02603],"object_pos_start":[0.61188,0.18355,0.23495],"object_to_goal_dist_end":0.1871,"object_to_goal_dist_start":0.0521,"object_z_max":0.23495,"peak_contact_force":0.14329,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":950.0,"raw_peak_contact_force":1.78816,"subtask_id":"place_subtask","tcp_end":[0.60614,0.22193,0.24227],"tcp_start":[0.60186,0.20523,0.34493],"tcp_to_object_dist_end":0.22015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21341,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.10654,"approach_goal.goal_approach_arc_height":0.1297,"approach_obj.approach_arc_height":0.11204,"approach_obj.pre_grasp_z_offset":0.18659,"descend_grasp.grasp_z_offset":0.02371,"descend_place.place_z_offset":-0.00289,"grasp_phase.grasp_time":0.66342,"lift_obj.lift_z_offset":0.14769},"optimized_scores":{"best_composite_score":0.04261,"best_fitness_score":0.56261,"best_task_score":0.21753},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1971.0,"contact_point_centroid":[0.54332,0.02551,-0.00276],"force_p95":0.37637,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05357,"mean_force":0.16812,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58162,0.06133,0.31759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2115.0,"contact_point_centroid":[0.53459,-0.05641,0.18728],"force_p95":0.16646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37231,"mean_force":0.1216,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53326,-0.03787,0.1912]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.54313,-0.02886,-0.0014],"force_p95":0.28933,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33838,"mean_force":0.07155,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53092,-0.02871,0.05443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4042.0,"contact_point_centroid":[0.53443,-0.04746,0.0983],"force_p95":0.12999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31954,"mean_force":0.09222,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53413,-0.0288,0.10106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4427.0,"contact_point_centroid":[0.53521,-0.01042,0.09796],"force_p95":0.12197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3001,"mean_force":0.08251,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53413,-0.0288,0.10112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2935.0,"contact_point_centroid":[0.53601,-0.02054,0.18976],"force_p95":0.14423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28955,"mean_force":0.09154,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53304,-0.03818,0.19403]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54556,-0.02926,-0.00208],"force_p95":0.14199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14939,"mean_force":0.12895,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53303,-0.02877,0.05441]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.5456,-0.02923,-0.00182],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1233,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.5239,-0.01615,0.27423]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.53958,-0.02838,0.14959]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.5438,0.02877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62532,0.15506,0.24326]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3502.0,"contact_point_centroid":[0.53393,-0.01003,0.05064],"force_p95":0.09862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10602,"mean_force":0.0625,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53181,-0.02874,0.05293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3198.0,"contact_point_centroid":[0.53317,-0.04765,0.05119],"force_p95":0.10193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10357,"mean_force":0.06688,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53181,-0.02874,0.05293]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2257.0,"contact_point_centroid":[0.57964,0.05787,0.31936],"force_p95":0.01143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01614,"mean_force":0.01051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57997,0.05793,0.31714]},{"body_a":"left_finger","body_b":"right_finger","contact_count":754.0,"contact_point_centroid":[0.62501,0.15487,0.2455],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01031,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62532,0.15506,0.24325]}],"total_contact_groups":14},"final_pose_error":0.01957,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.5438,0.02877,0.01602],"final_tcp_position":[0.62788,0.16073,0.19249],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":2.05357,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":724.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.54088,-0.02788,0.23566],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54058,-0.02897,0.06377],"tcp_start":[0.54088,-0.02788,0.23566],"tcp_to_object_dist_end":0.03809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02912,0.02551],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26117,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14343,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8500.0,"raw_peak_contact_force":0.14939,"tcp_end":[0.53178,-0.02874,0.05289],"tcp_start":[0.54058,-0.02897,0.06377],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":354.0,"n_steps_budget":780.0,"object_pos_end":[0.54706,-0.02946,0.12148],"object_pos_start":[0.54548,-0.02912,0.02551],"object_to_goal_dist_end":0.21959,"object_to_goal_dist_start":0.26117,"object_z_max":0.12124,"peak_contact_force":0.13438,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8555.0,"raw_peak_contact_force":0.33838,"tcp_end":[0.54015,-0.02896,0.15398],"tcp_start":[0.53178,-0.02874,0.05289],"tcp_to_object_dist_end":0.03323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.5438,0.02877,0.01602],"object_pos_start":[0.54706,-0.02946,0.12148],"object_to_goal_dist_end":0.22881,"object_to_goal_dist_start":0.21959,"object_z_max":0.2045,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9278.0,"raw_peak_contact_force":2.05357,"tcp_end":[0.62401,0.14984,0.29226],"tcp_start":[0.54015,-0.02896,0.15398],"tcp_to_object_dist_end":0.31208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.5438,0.02877,0.01602],"object_pos_start":[0.5438,0.02877,0.01602],"object_to_goal_dist_end":0.22881,"object_to_goal_dist_start":0.22881,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1450.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_subtask","tcp_end":[0.62788,0.16073,0.19249],"tcp_start":[0.62401,0.14984,0.29226],"tcp_to_object_dist_end":0.23585,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```