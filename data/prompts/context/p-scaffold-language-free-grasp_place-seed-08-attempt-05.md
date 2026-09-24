## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1855 | 0.56 | ✅ accepted |
| 4 | approach → descend → grasp → lift → push → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | grasp_success | pose_tolerance | pose_tolerance | time_limit | 7 | 0.2678 | 0.54 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.0818 | 0.26 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0682 | 0.30 | ❌ rejected |
| 1 | approach → descend → grasp → lift → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.0773 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.56 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.185) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_to_goal
  target_entity: object
  weight: 0.2
- id: hold_at_goal
  target_entity: object
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
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
    orientation:
      mode: keep_current
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - -0.005
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.35
      binds_to:
      - path: generator.speed
        mode: replace
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    transport_z_offset_delta:
      type: scalar
      range:
      - -0.03
      - 0.07
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: hold_1
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
    orientation:
      mode: keep_current
  parameters:
    hold_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: hold_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)
    - transport_z_offset_delta: status=consumed; consumers=target.offset.z (replace)
- **hold_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.185
- **task_score** (E): 0.564
- **fitness_score**: 0.755  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0998 |
| descend_1 | 1.00 | 1.00 | 0.1682 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1328 |
| transport_1 | 1.00 | 1.00 | 0.2227 |
| hold_1 | 1.00 | 1.00 | 0.0159 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.518, -0.001, 0.212) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / time_limit | (0.518, -0.001, 0.212)→(0.516, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.044)→(0.508, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 42.667 | 0.141 | 0.173 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.034)→(0.517, -0.001, 0.167) | (0.522, -0.001, 0.026)→(0.534, -0.001, 0.150) | 0.290→0.229 | 1.00 / 22.000 | 0.112 | 0.512 |
| transport_1 | approach | 1.00 / step_budget | (0.517, -0.001, 0.167)→(0.608, 0.199, 0.197) | (0.534, -0.001, 0.150)→(0.618, 0.202, 0.114) | 0.229→0.092 | 1.00 / 15.333 | 0.181 | 0.707 |
| hold_1 | grasp | 1.00 / step_budget | (0.608, 0.199, 0.197)→(0.602, 0.198, 0.182) | (0.618, 0.202, 0.114)→(0.614, 0.202, 0.107) | 0.092→0.099 | 1.00 / 15.667 | 0.123 | 0.277 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.738
- phase_score: 0.650
- phase_breakdown.transport_to_goal_score: 0.799
- phase_breakdown.reach_above_object_score: 0.244
- phase_breakdown.hold_at_goal_score: 0.754
- phase_breakdown.reach_object_score: 0.710
- phase_breakdown.lift_object_score: 0.640
- grasp_place_fitness: 0.838

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.838
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.738
- **Median Q (composite search score)**: 0.247
- **K-run variance**: 0.0104
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.291


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06034,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1699,"descend_1.grasp_offset_z":0.0141,"grasp_1.grasp_duration":1.6575,"hold_1.hold_duration":1.59681,"lift_1.lift_height":0.18804,"transport_1.transport_speed":0.65898,"transport_1.transport_xy_offset_x":0.00674,"transport_1.transport_xy_offset_y":0.01379,"transport_1.transport_z_offset_delta":-0.00077},"optimized_scores":{"best_composite_score":0.2465,"best_fitness_score":0.8165,"best_task_score":0.67697},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.4805,0.0468,-0.0014],"force_p95":0.50761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5727,"mean_force":0.12025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4684,0.04724,0.03117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7212.0,"contact_point_centroid":[0.47373,0.06646,0.10587],"force_p95":0.11113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28433,"mean_force":0.07449,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47141,0.04723,0.10352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9292.0,"contact_point_centroid":[0.47488,0.02868,0.10259],"force_p95":0.10099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27431,"mean_force":0.06039,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47125,0.04722,0.10151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5470.0,"contact_point_centroid":[0.57897,0.24656,0.20575],"force_p95":0.0988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23704,"mean_force":0.07613,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.57444,0.22743,0.20722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5178.0,"contact_point_centroid":[0.5337,0.15952,0.20636],"force_p95":0.12777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22915,"mean_force":0.09529,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52899,0.14047,0.20538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6357.0,"contact_point_centroid":[0.53677,0.12361,0.20465],"force_p95":0.13301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22484,"mean_force":0.08139,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52957,0.14151,0.20553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5729.0,"contact_point_centroid":[0.58151,0.20928,0.20478],"force_p95":0.0933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2238,"mean_force":0.07258,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.5744,0.22741,0.20712]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04867,-0.00212],"force_p95":0.15637,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21475,"mean_force":0.1315,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47072,0.04748,0.03085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5145.0,"contact_point_centroid":[0.47121,0.02836,0.03088],"force_p95":0.07329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18466,"mean_force":0.04215,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46951,0.04737,0.02962]},{"body_a":"world","body_b":"grasp_target","contact_count":2048.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48928,0.022,0.24996]},{"body_a":"world","body_b":"grasp_target","contact_count":3728.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47765,0.0465,0.11143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4210.0,"contact_point_centroid":[0.46939,0.06668,0.03207],"force_p95":0.08791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09713,"mean_force":0.05205,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46951,0.04737,0.02963]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57932,0.22799,0.17203],"final_tcp_position":[0.57891,0.22891,0.21897],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.5727,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2048.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.48049,0.04479,0.20203],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17607,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47764,0.04816,0.03789],"tcp_start":[0.48049,0.04479,0.20203],"tcp_to_object_dist_end":0.01292,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04793,0.02559],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29078,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15448,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11155.0,"raw_peak_contact_force":0.21475,"subtask_id":"reach_object","tcp_end":[0.46948,0.04736,0.02959],"tcp_start":[0.47764,0.04816,0.03789],"tcp_to_object_dist_end":0.01381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.04863,0.18024],"object_pos_start":[0.48268,0.04793,0.02559],"object_to_goal_dist_end":0.20586,"object_to_goal_dist_start":0.29078,"object_z_max":0.17999,"peak_contact_force":0.11737,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16581.0,"raw_peak_contact_force":0.5727,"subtask_id":"lift_object","tcp_end":[0.47838,0.04754,0.19434],"tcp_start":[0.46948,0.04736,0.02959],"tcp_to_object_dist_end":0.0226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.58381,0.22978,0.18892],"object_pos_start":[0.49601,0.04863,0.18024],"object_to_goal_dist_end":0.04162,"object_to_goal_dist_start":0.20586,"object_z_max":0.18891,"peak_contact_force":0.09549,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11535.0,"raw_peak_contact_force":0.22915,"subtask_id":"transport_to_goal","tcp_end":[0.57891,0.22891,0.21897],"tcp_start":[0.47838,0.04754,0.19434],"tcp_to_object_dist_end":0.03046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57932,0.22799,0.17203],"object_pos_start":[0.58381,0.22978,0.18892],"object_to_goal_dist_end":0.05852,"object_to_goal_dist_start":0.04162,"object_z_max":0.18892,"peak_contact_force":0.12293,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11199.0,"raw_peak_contact_force":0.23704,"subtask_id":"hold_at_goal","tcp_end":[0.57357,0.22704,0.20492],"tcp_start":[0.57891,0.22891,0.21897],"tcp_to_object_dist_end":0.0334,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06796,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18777,"descend_1.grasp_offset_z":0.00104,"grasp_1.grasp_duration":2.01744,"hold_1.hold_duration":1.84297,"lift_1.lift_height":0.14169,"transport_1.transport_speed":0.60599,"transport_1.transport_xy_offset_x":0.01341,"transport_1.transport_xy_offset_y":-0.0028,"transport_1.transport_z_offset_delta":-0.01022},"optimized_scores":{"best_composite_score":0.04181,"best_fitness_score":0.61181,"best_task_score":0.27585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.63344,0.21812,-0.01009],"force_p95":1.43818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6482,"mean_force":0.73268,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61416,0.20635,0.18491]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53493,-0.02154,-0.00132],"force_p95":0.4453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50561,"mean_force":0.10393,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5217,-0.02101,0.03575]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.63598,0.22218,-0.00219],"force_p95":0.12566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29473,"mean_force":0.11988,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.61037,0.20947,0.17306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6616.0,"contact_point_centroid":[0.52776,-0.00243,0.085],"force_p95":0.10443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28274,"mean_force":0.06405,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52454,-0.02111,0.08354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5470.0,"contact_point_centroid":[0.52752,-0.04018,0.08753],"force_p95":0.1093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28145,"mean_force":0.07444,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52469,-0.02111,0.08506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4535.0,"contact_point_centroid":[0.56882,0.05309,0.16182],"force_p95":0.15879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27307,"mean_force":0.10454,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56366,0.07194,0.16077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6183.0,"contact_point_centroid":[0.57217,0.09542,0.16186],"force_p95":0.11666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22229,"mean_force":0.07899,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56571,0.07741,0.16175]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02138,-0.00203],"force_p95":0.13244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14187,"mean_force":0.12513,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52402,-0.02105,0.03588]},{"body_a":"world","body_b":"grasp_target","contact_count":3876.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51687,-0.01144,0.25043]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53052,-0.02091,0.11442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5320.0,"contact_point_centroid":[0.52362,-0.00198,0.03656],"force_p95":0.06928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09798,"mean_force":0.041,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52274,-0.02103,0.03442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4147.0,"contact_point_centroid":[0.52353,-0.04032,0.03716],"force_p95":0.08125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09771,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52274,-0.02103,0.03442]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1774.0,"contact_point_centroid":[0.61078,0.20934,0.1743],"force_p95":0.01168,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01055,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.61,0.20931,0.17215]}],"total_contact_groups":13},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.63598,0.22214,0.01602],"final_tcp_position":[0.61568,0.21091,0.18566],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.6482,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3876.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.5324,-0.02063,0.21389],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18793,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53128,-0.02116,0.04431],"tcp_start":[0.5324,-0.02063,0.21389],"tcp_to_object_dist_end":0.01917,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02136,0.02588],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31687,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13257,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11267.0,"raw_peak_contact_force":0.14187,"subtask_id":"reach_object","tcp_end":[0.52271,-0.02103,0.03438],"tcp_start":[0.53128,-0.02116,0.04431],"tcp_to_object_dist_end":0.01655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":397.0,"n_steps_budget":840.0,"object_pos_end":[0.54848,-0.02178,0.13288],"object_pos_start":[0.5369,-0.02136,0.02588],"object_to_goal_dist_end":0.26767,"object_to_goal_dist_start":0.31687,"object_z_max":0.13264,"peak_contact_force":0.10651,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12164.0,"raw_peak_contact_force":0.50561,"subtask_id":"lift_object","tcp_end":[0.53156,-0.02127,0.14843],"tcp_start":[0.52271,-0.02103,0.03438],"tcp_to_object_dist_end":0.02299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.6353,0.21789,0.00126],"object_pos_start":[0.54848,-0.02178,0.13288],"object_to_goal_dist_end":0.20789,"object_to_goal_dist_start":0.26767,"object_z_max":0.14888,"peak_contact_force":0.31894,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10807.0,"raw_peak_contact_force":1.6482,"subtask_id":"transport_to_goal","tcp_end":[0.61568,0.21091,0.18566],"tcp_start":[0.53156,-0.02127,0.14843],"tcp_to_object_dist_end":0.18557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63598,0.22214,0.01602],"object_pos_start":[0.6353,0.21789,0.00126],"object_to_goal_dist_end":0.19319,"object_to_goal_dist_start":0.20789,"object_z_max":0.01675,"peak_contact_force":0.12263,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3574.0,"raw_peak_contact_force":0.29473,"subtask_id":"hold_at_goal","tcp_end":[0.60943,0.2091,0.17077],"tcp_start":[0.61568,0.21091,0.18566],"tcp_to_object_dist_end":0.15755,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06731,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19323,"descend_1.grasp_offset_z":0.01229,"grasp_1.grasp_duration":1.58269,"hold_1.hold_duration":1.96758,"lift_1.lift_height":0.15162,"transport_1.transport_speed":0.53033,"transport_1.transport_xy_offset_x":0.00577,"transport_1.transport_xy_offset_y":0.00708,"transport_1.transport_z_offset_delta":0.01986},"optimized_scores":{"best_composite_score":0.26812,"best_fitness_score":0.83812,"best_task_score":0.73776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.54362,-0.02894,-0.00135],"force_p95":0.40775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45736,"mean_force":0.09495,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53027,-0.0287,0.04081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3698.0,"contact_point_centroid":[0.62844,0.17546,0.16777],"force_p95":0.13036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30023,"mean_force":0.10785,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.62372,0.15759,0.17278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5624.0,"contact_point_centroid":[0.5361,-0.0479,0.09447],"force_p95":0.11054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28884,"mean_force":0.07578,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53331,-0.02881,0.09196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6919.0,"contact_point_centroid":[0.53652,-0.01018,0.09183],"force_p95":0.10502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28142,"mean_force":0.06449,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53316,-0.0288,0.09046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3760.0,"contact_point_centroid":[0.62699,0.13924,0.16866],"force_p95":0.13219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25012,"mean_force":0.10382,"phase_index":5.0,"phase_name":"hold_1","phase_type":"grasp","tcp_position_centroid":[0.62368,0.15758,0.17269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5880.0,"contact_point_centroid":[0.58971,0.04945,0.17051],"force_p95":0.13224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24338,"mean_force":0.08699,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58515,0.06831,0.17021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6373.0,"contact_point_centroid":[0.58752,0.07899,0.16875],"force_p95":0.124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23212,"mean_force":0.08189,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5815,0.06071,0.169]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5456,-0.02929,-0.00204],"force_p95":0.13649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16155,"mean_force":0.12623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53265,-0.02876,0.04105]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52018,-0.0148,0.25565]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53876,-0.02842,0.11992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5311.0,"contact_point_centroid":[0.53236,-0.00968,0.04161],"force_p95":0.07144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11076,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53137,-0.02873,0.03954]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4159.0,"contact_point_centroid":[0.53197,-0.04801,0.04237],"force_p95":0.08263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09491,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53138,-0.02873,0.03954]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62691,0.1568,0.13242],"final_tcp_position":[0.62922,0.15863,0.18547],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.45736,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.54009,-0.02778,0.22038],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19445,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53987,-0.02895,0.0497],"tcp_start":[0.54009,-0.02778,0.22038],"tcp_to_object_dist_end":0.02436,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02917,0.02582],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26102,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13644,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11270.0,"raw_peak_contact_force":0.16155,"subtask_id":"reach_object","tcp_end":[0.53134,-0.02873,0.0395],"tcp_start":[0.53987,-0.02895,0.0497],"tcp_to_object_dist_end":0.01969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":416.0,"n_steps_budget":870.0,"object_pos_end":[0.55603,-0.0297,0.1379],"object_pos_start":[0.54551,-0.02917,0.02582],"object_to_goal_dist_end":0.21284,"object_to_goal_dist_start":0.26102,"object_z_max":0.13766,"peak_contact_force":0.11274,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12623.0,"raw_peak_contact_force":0.45736,"subtask_id":"lift_object","tcp_end":[0.5403,-0.02903,0.15831],"tcp_start":[0.53134,-0.02873,0.0395],"tcp_to_object_dist_end":0.02577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.63356,0.15864,0.15157],"object_pos_start":[0.55603,-0.0297,0.1379],"object_to_goal_dist_end":0.02613,"object_to_goal_dist_start":0.21284,"object_z_max":0.15155,"peak_contact_force":0.12736,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12253.0,"raw_peak_contact_force":0.24338,"subtask_id":"transport_to_goal","tcp_end":[0.62922,0.15863,0.18547],"tcp_start":[0.5403,-0.02903,0.15831],"tcp_to_object_dist_end":0.03418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62691,0.1568,0.13242],"object_pos_start":[0.63356,0.15864,0.15157],"object_to_goal_dist_end":0.04562,"object_to_goal_dist_start":0.02613,"object_z_max":0.15157,"peak_contact_force":0.12386,"phase_name":"hold_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7458.0,"raw_peak_contact_force":0.30023,"subtask_id":"hold_at_goal","tcp_end":[0.62277,0.15731,0.17055],"tcp_start":[0.62922,0.15863,0.18547],"tcp_to_object_dist_end":0.03836,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```