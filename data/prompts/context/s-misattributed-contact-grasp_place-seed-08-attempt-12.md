## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.0029 | 0.70 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17 | -0.3793 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.0259 | 0.65 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1019 | 0.90 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.3259 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.70 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.904, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.003) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.4
- id: reach_goal
  target_entity: object
  weight: 0.6
phases:
- id: approach_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: lift_1
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
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: move_above_goal
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
    - 0.08
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    above_goal_x:
      type: scalar
      range:
      - -0.06
      - 0.06
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    above_goal_y:
      type: scalar
      range:
      - -0.06
      - 0.06
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    above_goal_z:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: place_at_goal
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
    orientation:
      mode: keep_current
  parameters:
    place_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    place_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    place_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **move_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - above_goal_x: status=consumed; consumers=target.offset.x (replace)
    - above_goal_y: status=consumed; consumers=target.offset.y (replace)
    - above_goal_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_x: status=consumed; consumers=target.offset.x (replace)
    - place_y: status=consumed; consumers=target.offset.y (replace)
    - place_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.003
- **task_score** (E): 0.697
- **fitness_score**: 0.817  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.820

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1521 |
| descend_1 | 1.00 | 1.00 | 0.1043 |
| grasp_1 | 1.00 | 1.00 | 0.0132 |
| lift_1 | 1.00 | 1.00 | 0.1387 |
| move_above_goal | 1.00 | 1.00 | 0.2315 |
| place_at_goal | 1.00 | 1.00 | 0.0494 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.154) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.154)→(0.516, -0.001, 0.050) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 42.333 | 0.154 | 0.222 |
| grasp_1 | grasp | 1.00 / step_budget | (0.516, -0.001, 0.050)→(0.508, -0.001, 0.040) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 27.000 | 524.437 | 0.478 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.040)→(0.517, -0.001, 0.179) | (0.522, -0.001, 0.026)→(0.534, -0.001, 0.160) | 0.289→0.227 | 1.00 / 18.333 | 0.123 | 0.901 |
| move_above_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.179)→(0.607, 0.190, 0.264) | (0.534, -0.001, 0.160)→(0.611, 0.178, 0.159) | 0.227→0.094 | 1.00 / 14.333 | 0.146 | 0.294 |
| place_at_goal | descend | 1.00 / step_budget | (0.607, 0.190, 0.264)→(0.602, 0.201, 0.221) | (0.611, 0.178, 0.159)→(0.617, 0.181, 0.134) | 0.094→0.081 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.331
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.695
- phase_breakdown.reach_goal_score: 0.565
- phase_breakdown.reach_object_score: 0.891
- grasp_place_fitness: 0.967

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.967
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.070
- **K-run variance**: 0.0258
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.descend_offset_z
- **Final σ (mean)**: 0.258


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79487,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1086,"approach_1.speed":0.15049,"descend_1.descend_offset_z":0.0,"descend_1.speed":0.14588,"lift_1.lift_height":0.1814,"lift_1.speed":0.06759,"move_above_goal.above_goal_x":-0.00606,"move_above_goal.above_goal_y":-0.02342,"move_above_goal.above_goal_z":0.08793,"move_above_goal.speed":0.16845,"place_at_goal.place_x":0.01093,"place_at_goal.place_y":-0.01396,"place_at_goal.place_z":0.00422,"place_at_goal.speed":0.04991},"optimized_scores":{"best_composite_score":0.07045,"best_fitness_score":0.89045,"best_task_score":0.83321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.47998,0.04608,-0.0017],"force_p95":0.47752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53361,"mean_force":0.19451,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46969,0.04609,0.03793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5920.0,"contact_point_centroid":[0.47315,0.06524,0.10543],"force_p95":0.08748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31113,"mean_force":0.05608,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47263,0.04611,0.10366]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5342.0,"contact_point_centroid":[0.47304,0.02692,0.10347],"force_p95":0.09064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26893,"mean_force":0.05974,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47246,0.04611,0.10107]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04847,-0.00222],"force_p95":0.18317,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25605,"mean_force":0.13872,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47174,0.04631,0.03775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1369.0,"contact_point_centroid":[0.57819,0.21491,0.2744],"force_p95":0.13141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24913,"mean_force":0.08625,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57205,0.1963,0.27396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1275.0,"contact_point_centroid":[0.5781,0.17768,0.27485],"force_p95":0.13305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22292,"mean_force":0.08901,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57203,0.19628,0.27402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4055.0,"contact_point_centroid":[0.52605,0.09896,0.23811],"force_p95":0.13424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20358,"mean_force":0.09217,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.52073,0.11773,0.23621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.52638,0.13684,0.23815],"force_p95":0.12024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17042,"mean_force":0.0808,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.52108,0.11834,0.23669]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49086,0.01988,0.22969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4866.0,"contact_point_centroid":[0.47059,0.027,0.03919],"force_p95":0.07421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13584,"mean_force":0.04421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47065,0.0462,0.03664]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47966,0.04403,0.10143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.47088,0.06559,0.03863],"force_p95":0.07682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08068,"mean_force":0.04422,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47066,0.0462,0.03665]}],"total_contact_groups":12},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.59169,0.20583,0.21942],"final_tcp_position":[0.58151,0.2054,0.24784],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.53361,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":840.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48217,0.04128,0.15703],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17401,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11819.0,"raw_peak_contact_force":0.25605,"subtask_id":"reach_object","tcp_end":[0.47882,0.04696,0.04525],"tcp_start":[0.48217,0.04128,0.15703],"tcp_to_object_dist_end":0.0197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48266,0.04682,0.02524],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29172,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.10324,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11332.0,"raw_peak_contact_force":0.53361,"subtask_id":"reach_object","tcp_end":[0.47062,0.0462,0.03661],"tcp_start":[0.47882,0.04696,0.04525],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,0.04658,0.16367],"object_pos_start":[0.48266,0.04682,0.02524],"object_to_goal_dist_end":0.21327,"object_to_goal_dist_start":0.29172,"object_z_max":0.1632,"peak_contact_force":0.09872,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8890.0,"raw_peak_contact_force":0.20358,"subtask_id":"reach_object","tcp_end":[0.47798,0.04639,0.17746],"tcp_start":[0.47062,0.0462,0.03661],"tcp_to_object_dist_end":0.02083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.57455,0.1888,0.26939],"object_pos_start":[0.49359,0.04658,0.16367],"object_to_goal_dist_end":0.05632,"object_to_goal_dist_start":0.21327,"object_z_max":0.26914,"peak_contact_force":0.12862,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.24913,"subtask_id":"reach_goal","tcp_end":[0.56443,0.18829,0.2968],"tcp_start":[0.47798,0.04639,0.17746],"tcp_to_object_dist_end":0.02922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":115.0,"n_steps_budget":1000.0,"object_pos_end":[0.59169,0.20583,0.21942],"object_pos_start":[0.57455,0.1888,0.26939],"object_to_goal_dist_end":0.02737,"object_to_goal_dist_start":0.05632,"object_z_max":0.2696,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.58151,0.2054,0.24784],"tcp_start":[0.56443,0.18829,0.2968],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08824,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10481,"approach_1.speed":0.12918,"descend_1.descend_offset_z":0.00927,"descend_1.speed":0.10616,"lift_1.lift_height":0.1846,"lift_1.speed":0.10552,"move_above_goal.above_goal_x":0.03552,"move_above_goal.above_goal_y":-0.00618,"move_above_goal.above_goal_z":0.08262,"move_above_goal.speed":0.21904,"place_at_goal.place_x":-0.01566,"place_at_goal.place_y":0.01187,"place_at_goal.place_z":-0.00498,"place_at_goal.speed":0.08393},"optimized_scores":{"best_composite_score":-0.2259,"best_fitness_score":0.5941,"best_task_score":0.25883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":430.0,"contact_point_centroid":[0.63027,0.16373,-0.00466],"force_p95":0.93033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23357,"mean_force":0.23621,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.62242,0.17426,0.26084]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.5354,-0.02025,-0.00152],"force_p95":0.38815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41712,"mean_force":0.12808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52141,-0.02043,0.04453]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3920.0,"contact_point_centroid":[0.52785,-0.00149,0.10531],"force_p95":0.11901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29224,"mean_force":0.07862,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52477,-0.02042,0.10289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4285.0,"contact_point_centroid":[0.5278,-0.03922,0.10296],"force_p95":0.11655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27626,"mean_force":0.07411,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52464,-0.02042,0.10125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2371.0,"contact_point_centroid":[0.56388,0.01774,0.20307],"force_p95":0.18069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25286,"mean_force":0.10669,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.55712,0.03635,0.202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2958.0,"contact_point_centroid":[0.56682,0.06138,0.20546],"force_p95":0.13384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.243,"mean_force":0.08377,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.5603,0.04338,0.20474]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02118,-0.00208],"force_p95":0.14472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19498,"mean_force":0.12865,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52372,-0.02047,0.04482]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51321,-0.00879,0.22716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.52354,-0.00124,0.04616],"force_p95":0.07843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13676,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52254,-0.02045,0.04345]},{"body_a":"world","body_b":"grasp_target","contact_count":508.0,"contact_point_centroid":[0.63038,0.16396,-0.00199],"force_p95":0.12475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12649,"mean_force":0.12301,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62063,0.21298,0.24409]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52901,-0.01937,0.10367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4931.0,"contact_point_centroid":[0.52352,-0.03955,0.04524],"force_p95":0.0706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07393,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52254,-0.02045,0.04346]},{"body_a":"left_finger","body_b":"right_finger","contact_count":258.0,"contact_point_centroid":[0.62855,0.18585,0.26804],"force_p95":0.01517,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01143,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.62798,0.18584,0.26587]},{"body_a":"left_finger","body_b":"right_finger","contact_count":544.0,"contact_point_centroid":[0.6211,0.21293,0.24651],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.01041,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6207,0.21292,0.24422]}],"total_contact_groups":14},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.63038,0.16396,0.01602],"final_tcp_position":[0.60418,0.22729,0.21447],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.23357,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52849,-0.01821,0.15237],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14094,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10830.0,"raw_peak_contact_force":0.19498,"subtask_id":"reach_object","tcp_end":[0.53129,-0.02059,0.05397],"tcp_start":[0.52849,-0.01821,0.15237],"tcp_to_object_dist_end":0.02854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02055,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3163,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.11605,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8271.0,"raw_peak_contact_force":0.41712,"subtask_id":"reach_object","tcp_end":[0.52251,-0.02045,0.04342],"tcp_start":[0.53129,-0.02059,0.05397],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":283.0,"n_steps_budget":990.0,"object_pos_end":[0.54975,-0.02052,0.15904],"object_pos_start":[0.53695,-0.02055,0.02572],"object_to_goal_dist_end":0.26009,"object_to_goal_dist_start":0.3163,"object_z_max":0.15859,"peak_contact_force":0.12661,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6017.0,"raw_peak_contact_force":2.23357,"subtask_id":"reach_object","tcp_end":[0.53176,-0.02046,0.18091],"tcp_start":[0.52251,-0.02045,0.04342],"tcp_to_object_dist_end":0.02833,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.63035,0.16385,0.01619],"object_pos_start":[0.54975,-0.02052,0.15904],"object_to_goal_dist_end":0.20261,"object_to_goal_dist_start":0.26009,"object_z_max":0.19607,"peak_contact_force":0.12264,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.12649,"subtask_id":"reach_goal","tcp_end":[0.63496,0.20056,0.27217],"tcp_start":[0.53176,-0.02046,0.18091],"tcp_to_object_dist_end":0.25863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.63038,0.16396,0.01602],"object_pos_start":[0.63035,0.16385,0.01619],"object_to_goal_dist_end":0.20274,"object_to_goal_dist_start":0.20261,"object_z_max":0.01619,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.60418,0.22729,0.21447],"tcp_start":[0.63496,0.20056,0.27217],"tcp_to_object_dist_end":0.20996,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87395,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10717,"approach_1.speed":0.14206,"descend_1.descend_offset_z":0.00721,"descend_1.speed":0.09121,"lift_1.lift_height":0.18132,"lift_1.speed":0.14249,"move_above_goal.above_goal_x":0.00074,"move_above_goal.above_goal_y":0.04051,"move_above_goal.above_goal_z":0.05998,"move_above_goal.speed":0.29207,"place_at_goal.place_x":-0.00959,"place_at_goal.place_y":-0.00709,"place_at_goal.place_z":0.01089,"place_at_goal.speed":0.08062},"optimized_scores":{"best_composite_score":0.14663,"best_fitness_score":0.96663,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":495.0,"contact_point_centroid":[0.62619,0.19683,0.21226],"force_p95":0.19324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50739,"mean_force":0.11269,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62145,0.17884,0.21411]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.54346,-0.02804,-0.0015],"force_p95":0.43354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48377,"mean_force":0.11991,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52917,-0.02794,0.04211]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":373.0,"contact_point_centroid":[0.62831,0.16122,0.21273],"force_p95":0.19281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41168,"mean_force":0.1271,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62154,0.1794,0.21524]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3646.0,"contact_point_centroid":[0.53675,-0.0091,0.10311],"force_p95":0.12025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3266,"mean_force":0.08203,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53305,-0.02795,0.10076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3886.0,"contact_point_centroid":[0.53672,-0.04671,0.10088],"force_p95":0.11975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30856,"mean_force":0.07925,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53292,-0.02795,0.09918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4344.0,"contact_point_centroid":[0.58787,0.09882,0.19995],"force_p95":0.13193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26479,"mean_force":0.08595,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58192,0.08029,0.19913]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4296.0,"contact_point_centroid":[0.58624,0.05646,0.19875],"force_p95":0.14743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24196,"mean_force":0.08852,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.57992,0.0751,0.19806]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02905,-0.00211],"force_p95":0.15393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21593,"mean_force":0.131,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53167,-0.02803,0.04234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.53171,-0.00878,0.04362],"force_p95":0.07981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14414,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53046,-0.02799,0.04093]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51678,-0.01207,0.228]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53666,-0.02657,0.10341]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4973.0,"contact_point_centroid":[0.53164,-0.04711,0.04269],"force_p95":0.07223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07625,"mean_force":0.04449,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53046,-0.02799,0.04094]}],"total_contact_groups":12},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62907,0.17387,0.16771],"final_tcp_position":[0.62073,0.17168,0.20189],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":772.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53589,-0.02499,0.15407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14842,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10863.0,"raw_peak_contact_force":0.21593,"subtask_id":"reach_object","tcp_end":[0.53935,-0.02823,0.05177],"tcp_start":[0.53589,-0.02499,0.15407],"tcp_to_object_dist_end":0.02652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02818,0.02562],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26039,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":1573.09317,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7600.0,"raw_peak_contact_force":0.48377,"subtask_id":"reach_object","tcp_end":[0.53043,-0.02799,0.04089],"tcp_start":[0.53935,-0.02823,0.05177],"tcp_to_object_dist_end":0.02149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":277.0,"n_steps_budget":750.0,"object_pos_end":[0.559,-0.02826,0.15755],"object_pos_start":[0.54554,-0.02818,0.02562],"object_to_goal_dist_end":0.20772,"object_to_goal_dist_start":0.26039,"object_z_max":0.15711,"peak_contact_force":0.14243,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8640.0,"raw_peak_contact_force":0.26479,"subtask_id":"reach_object","tcp_end":[0.54038,-0.02804,0.17777],"tcp_start":[0.53043,-0.02799,0.04089],"tcp_to_object_dist_end":0.02748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.62939,0.18196,0.19056],"object_pos_start":[0.559,-0.02826,0.15755],"object_to_goal_dist_end":0.02209,"object_to_goal_dist_start":0.20772,"object_z_max":0.19048,"peak_contact_force":0.18624,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":0.50739,"subtask_id":"reach_goal","tcp_end":[0.62231,0.18167,0.22262],"tcp_start":[0.54038,-0.02804,0.17777],"tcp_to_object_dist_end":0.03284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":51.0,"n_steps_budget":1000.0,"object_pos_end":[0.62907,0.17387,0.16771],"object_pos_start":[0.62939,0.18196,0.19056],"object_to_goal_dist_end":0.01338,"object_to_goal_dist_start":0.02209,"object_z_max":0.19056,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.62073,0.17168,0.20189],"tcp_start":[0.62231,0.18167,0.22262],"tcp_to_object_dist_end":0.03525,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```