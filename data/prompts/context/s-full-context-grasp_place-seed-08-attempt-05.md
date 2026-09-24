## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5552 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.5550 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.1419 | 0.31 | ✅ accepted |
| 2 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |
| 1 | pull → insert → descend → contact → release | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | force_exceeded | time_limit | 5 | 0.0851 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.555) — your mutation base

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

- **Composite score**: 0.555
- **task_score** (E): 1.000
- **fitness_score**: 0.975  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_obj | 1.00 | 1.00 | 0.1929 |
| descend_grasp | 1.00 | 1.00 | 0.0702 |
| grasp_phase | 1.00 | 1.00 | 0.0127 |
| lift_obj | 1.00 | 1.00 | 0.1145 |
| approach_goal | 1.00 | 1.00 | 0.2832 |
| descend_place | 1.00 | 1.00 | 0.1067 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_obj | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.001, 0.113) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.515, -0.001, 0.113)→(0.516, -0.001, 0.043) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_phase | grasp | 1.00 / step_budget | (0.516, -0.001, 0.043)→(0.508, -0.001, 0.033) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 43.000 | 0.142 | 0.172 |
| lift_obj | lift | 1.00 / step_budget | (0.508, -0.001, 0.033)→(0.516, -0.001, 0.147) | (0.522, -0.001, 0.026)→(0.529, -0.001, 0.137) | 0.290→0.236 | 1.00 / 37.667 | 0.082 | 0.607 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.147)→(0.603, 0.198, 0.328) | (0.529, -0.001, 0.137)→(0.614, 0.202, 0.312) | 0.236→0.108 | 1.00 / 34.333 | 0.090 | 0.139 |
| descend_place | descend | 1.00 / step_budget | (0.603, 0.198, 0.328)→(0.604, 0.204, 0.221) | (0.614, 0.202, 0.312)→(0.614, 0.208, 0.203) | 0.108→0.007 | 1.00 / 31.000 | 0.087 | 0.221 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.700
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.643
- phase_breakdown.place_subtask_score: 0.688
- phase_breakdown.approach_subtask_score: 0.466
- grasp_place_fitness: 0.976

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.556
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.534


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87135,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.11471,"approach_obj.pre_grasp_z_offset":0.06269,"descend_grasp.grasp_z_offset":0.02005,"descend_place.place_z_offset":-0.00106,"grasp_phase.grasp_time":0.77494,"lift_obj.lift_z_offset":0.12821},"optimized_scores":{"best_composite_score":0.55433,"best_fitness_score":0.97433,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48035,0.0471,-0.00142],"force_p95":0.46732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55656,"mean_force":0.10226,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.46869,0.04711,0.03667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5457.0,"contact_point_centroid":[0.47171,0.06641,0.08671],"force_p95":0.08712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31989,"mean_force":0.06083,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47186,0.04719,0.08415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6831.0,"contact_point_centroid":[0.47373,0.02827,0.08559],"force_p95":0.08396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29078,"mean_force":0.05033,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.47186,0.04719,0.08415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2050.0,"contact_point_centroid":[0.57223,0.24132,0.29421],"force_p95":0.09905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23216,"mean_force":0.07025,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57641,0.22282,0.291]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.0487,-0.00213],"force_p95":0.15793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21423,"mean_force":0.13204,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.47083,0.04735,0.03639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2523.0,"contact_point_centroid":[0.58423,0.20557,0.29137],"force_p95":0.0968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19146,"mean_force":0.06035,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57639,0.22279,0.29142]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5257.0,"contact_point_centroid":[0.47116,0.02822,0.03642],"force_p95":0.07308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19039,"mean_force":0.04136,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46962,0.04723,0.03516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18636.0,"contact_point_centroid":[0.5303,0.11653,0.23191],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14792,"mean_force":0.05135,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52541,0.13484,0.23072]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.48997,0.02074,0.20691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15559.0,"contact_point_centroid":[0.52282,0.15414,0.23446],"force_p95":0.08898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13713,"mean_force":0.06009,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52567,0.13532,0.23125]},{"body_a":"world","body_b":"grasp_target","contact_count":2120.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4776,0.04574,0.06991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4210.0,"contact_point_centroid":[0.46944,0.06655,0.03759],"force_p95":0.08824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0962,"mean_force":0.05201,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.46962,0.04723,0.03516]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58827,0.23054,0.22943],"final_tcp_position":[0.57795,0.22566,0.24864],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.55656,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.48098,0.04276,0.11149],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2120.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47766,0.04801,0.04342],"tcp_start":[0.48098,0.04276,0.11149],"tcp_to_object_dist_end":0.01813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04796,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29078,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15568,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11267.0,"raw_peak_contact_force":0.21423,"tcp_end":[0.46959,0.04723,0.03513],"tcp_start":[0.47766,0.04801,0.04342],"tcp_to_object_dist_end":0.01625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":321.0,"n_steps_budget":750.0,"object_pos_end":[0.49032,0.04846,0.12295],"object_pos_start":[0.48271,0.04796,0.02556],"object_to_goal_dist_end":0.2291,"object_to_goal_dist_start":0.29078,"object_z_max":0.12268,"peak_contact_force":0.08492,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12366.0,"raw_peak_contact_force":0.55656,"tcp_end":[0.4774,0.04749,0.13469],"tcp_start":[0.46959,0.04723,0.03513],"tcp_to_object_dist_end":0.01748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.58727,0.22518,0.31192],"object_pos_start":[0.49032,0.04846,0.12295],"object_to_goal_dist_end":0.0817,"object_to_goal_dist_start":0.2291,"object_z_max":0.31175,"peak_contact_force":0.09224,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34195.0,"raw_peak_contact_force":0.14792,"tcp_end":[0.57549,0.22029,0.32835],"tcp_start":[0.4774,0.04749,0.13469],"tcp_to_object_dist_end":0.0208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.58827,0.23054,0.22943],"object_pos_start":[0.58727,0.22518,0.31192],"object_to_goal_dist_end":0.00671,"object_to_goal_dist_start":0.0817,"object_z_max":0.31198,"peak_contact_force":0.09034,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4573.0,"raw_peak_contact_force":0.23216,"subtask_id":"place_subtask","tcp_end":[0.57795,0.22566,0.24864],"tcp_start":[0.57549,0.22029,0.32835],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91579,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.14745,"approach_obj.pre_grasp_z_offset":0.06572,"descend_grasp.grasp_z_offset":0.02063,"descend_place.place_z_offset":-0.0065,"grasp_phase.grasp_time":0.37401,"lift_obj.lift_z_offset":0.1572},"optimized_scores":{"best_composite_score":0.55559,"best_fitness_score":0.97559,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.5343,-0.02115,-0.00134],"force_p95":0.51684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62967,"mean_force":0.13039,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52202,-0.02103,0.03387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9448.0,"contact_point_centroid":[0.52656,-0.00215,0.09782],"force_p95":0.0769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32976,"mean_force":0.05076,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52543,-0.02116,0.09593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7946.0,"contact_point_centroid":[0.52565,-0.04035,0.09908],"force_p95":0.08143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3278,"mean_force":0.0584,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.52544,-0.02116,0.09623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3135.0,"contact_point_centroid":[0.60183,0.23909,0.2853],"force_p95":0.09543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23593,"mean_force":0.06602,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60569,0.22057,0.28231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3309.0,"contact_point_centroid":[0.61397,0.20336,0.28222],"force_p95":0.09048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17486,"mean_force":0.0633,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6057,0.22062,0.2815]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02142,-0.00203],"force_p95":0.1342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14993,"mean_force":0.12555,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52432,-0.02106,0.03404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17558.0,"contact_point_centroid":[0.57261,0.08388,0.25356],"force_p95":0.08371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14623,"mean_force":0.05749,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5684,0.10238,0.25216]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51333,-0.00912,0.20788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17910.0,"contact_point_centroid":[0.56466,0.11478,0.24961],"force_p95":0.08592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13123,"mean_force":0.05614,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56636,0.09597,0.24734]},{"body_a":"world","body_b":"grasp_target","contact_count":3504.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52887,-0.02018,0.06937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5328.0,"contact_point_centroid":[0.52386,-0.00197,0.03465],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09819,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52303,-0.02104,0.03257]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4155.0,"contact_point_centroid":[0.52238,-0.0403,0.03561],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08833,"mean_force":0.05169,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.52304,-0.02104,0.03257]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61556,0.22913,0.20111],"final_tcp_position":[0.60673,0.22458,0.22028],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.62967,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.52894,-0.0188,0.11346],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3504.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53156,-0.02117,0.04242],"tcp_start":[0.52894,-0.0188,0.11346],"tcp_to_object_dist_end":0.01729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53689,-0.02144,0.02587],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31693,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13437,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11283.0,"raw_peak_contact_force":0.14993,"tcp_end":[0.523,-0.02104,0.03254],"tcp_start":[0.53156,-0.02117,0.04242],"tcp_to_object_dist_end":0.01541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":450.0,"n_steps_budget":960.0,"object_pos_end":[0.54495,-0.02187,0.15396],"object_pos_start":[0.53689,-0.02144,0.02587],"object_to_goal_dist_end":0.26352,"object_to_goal_dist_start":0.31693,"object_z_max":0.1537,"peak_contact_force":0.07922,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17472.0,"raw_peak_contact_force":0.62967,"tcp_end":[0.53194,-0.02134,0.16378],"tcp_start":[0.523,-0.02104,0.03254],"tcp_to_object_dist_end":0.01631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.61644,0.22168,0.32313],"object_pos_start":[0.54495,-0.02187,0.15396],"object_to_goal_dist_end":0.11604,"object_to_goal_dist_start":0.26352,"object_z_max":0.32299,"peak_contact_force":0.0887,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35468.0,"raw_peak_contact_force":0.14623,"tcp_end":[0.60543,0.21709,0.33885],"tcp_start":[0.53194,-0.02134,0.16378],"tcp_to_object_dist_end":0.01973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.61556,0.22913,0.20111],"object_pos_start":[0.61644,0.22168,0.32313],"object_to_goal_dist_end":0.00832,"object_to_goal_dist_start":0.11604,"object_z_max":0.32316,"peak_contact_force":0.08405,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6444.0,"raw_peak_contact_force":0.23593,"subtask_id":"place_subtask","tcp_end":[0.60673,0.22458,0.22028],"tcp_start":[0.60543,0.21709,0.33885],"tcp_to_object_dist_end":0.02159,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9116,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z_offset":0.15587,"approach_obj.pre_grasp_z_offset":0.06565,"descend_grasp.grasp_z_offset":0.0204,"descend_place.place_z_offset":-0.00124,"grasp_phase.grasp_time":0.45506,"lift_obj.lift_z_offset":0.13678},"optimized_scores":{"best_composite_score":0.5558,"best_fitness_score":0.9758,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54174,-0.02888,-0.00133],"force_p95":0.54551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63447,"mean_force":0.14437,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53056,-0.02875,0.03318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6842.0,"contact_point_centroid":[0.53375,-0.04803,0.0892],"force_p95":0.08321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33611,"mean_force":0.05914,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53388,-0.02883,0.08626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8291.0,"contact_point_centroid":[0.53495,-0.00982,0.08808],"force_p95":0.07891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32803,"mean_force":0.05046,"phase_index":3.0,"phase_name":"lift_obj","phase_type":"lift","tcp_position_centroid":[0.53388,-0.02883,0.0862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3019.0,"contact_point_centroid":[0.6248,0.1778,0.26018],"force_p95":0.0971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19364,"mean_force":0.06955,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62727,0.15901,0.25728]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3487.0,"contact_point_centroid":[0.63364,0.14107,0.25923],"force_p95":0.09128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16738,"mean_force":0.06221,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62724,0.15893,0.25869]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02928,-0.00204],"force_p95":0.13592,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15051,"mean_force":0.12584,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53276,-0.0288,0.03339]},{"body_a":"world","body_b":"grasp_target","contact_count":1496.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_obj","phase_type":"approach","tcp_position_centroid":[0.51702,-0.01252,0.20759]},{"body_a":"world","body_b":"grasp_target","contact_count":3636.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5369,-0.02761,0.06955]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16145.0,"contact_point_centroid":[0.5872,0.05021,0.23441],"force_p95":0.08054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12204,"mean_force":0.05692,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58435,0.06907,0.23254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17281.0,"contact_point_centroid":[0.58023,0.08155,0.22856],"force_p95":0.08037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11925,"mean_force":0.05379,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58122,0.06264,0.22636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5307.0,"contact_point_centroid":[0.53244,-0.00972,0.03391],"force_p95":0.07152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10788,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53147,-0.02877,0.03188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4159.0,"contact_point_centroid":[0.53202,-0.04806,0.03473],"force_p95":0.08316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09812,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_phase","phase_type":"grasp","tcp_position_centroid":[0.53147,-0.02877,0.03188]}],"total_contact_groups":12},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63876,0.16573,0.17745],"final_tcp_position":[0.62865,0.16234,0.19499],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.63447,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_obj","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1496.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_subtask","tcp_end":[0.53653,-0.02578,0.11304],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3636.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54007,-0.02899,0.04201],"tcp_start":[0.53653,-0.02578,0.11304],"tcp_to_object_dist_end":0.01692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02915,0.02584],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.261,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13597,"phase_name":"grasp_phase","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11266.0,"raw_peak_contact_force":0.15051,"tcp_end":[0.53144,-0.02877,0.03184],"tcp_start":[0.54007,-0.02899,0.04201],"tcp_to_object_dist_end":0.01527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":390.0,"n_steps_budget":840.0,"object_pos_end":[0.55312,-0.02953,0.13497],"object_pos_start":[0.54548,-0.02915,0.02584],"object_to_goal_dist_end":0.21431,"object_to_goal_dist_start":0.261,"object_z_max":0.13473,"peak_contact_force":0.08126,"phase_name":"lift_obj","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15211.0,"raw_peak_contact_force":0.63447,"tcp_end":[0.54015,-0.02899,0.14355],"tcp_start":[0.53144,-0.02877,0.03184],"tcp_to_object_dist_end":0.01556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.63837,0.15949,0.30228],"object_pos_start":[0.55312,-0.02953,0.13497],"object_to_goal_dist_end":0.1256,"object_to_goal_dist_start":0.21431,"object_z_max":0.30213,"peak_contact_force":0.09003,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33426.0,"raw_peak_contact_force":0.12204,"tcp_end":[0.62676,0.15599,0.31612],"tcp_start":[0.54015,-0.02899,0.14355],"tcp_to_object_dist_end":0.0184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.63876,0.16573,0.17745],"object_pos_start":[0.63837,0.15949,0.30228],"object_to_goal_dist_end":0.006,"object_to_goal_dist_start":0.1256,"object_z_max":0.30232,"peak_contact_force":0.08551,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6506.0,"raw_peak_contact_force":0.19364,"subtask_id":"place_subtask","tcp_end":[0.62865,0.16234,0.19499],"tcp_start":[0.62676,0.15599,0.31612],"tcp_to_object_dist_end":0.02053,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```