## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 16 | -0.3364 | 0.28 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.0029 | 0.70 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17 | -0.3793 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.0259 | 0.65 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1019 | 0.90 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.336) — your mutation base

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

- **Composite score**: -0.336
- **task_score** (E): 0.281
- **fitness_score**: 0.614  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.950

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1519 |
| descend_1 | 1.00 | 1.00 | 0.1097 |
| grasp_1 | 1.00 | 1.00 | 0.0133 |
| lift_1 | 1.00 | 1.00 | 0.1150 |
| move_above_goal | 1.00 | 0.33 | 0.2564 |
| place_at_goal | 1.00 | 1.00 | 0.0463 |
| release_1 | 1.00 | 1.00 | 0.0194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.155) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.155)→(0.517, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 42.000 | 0.154 | 0.225 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.045)→(0.508, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 24.333 | 0.107 | 0.517 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.035)→(0.516, -0.001, 0.150) | (0.522, -0.001, 0.026)→(0.535, -0.001, 0.137) | 0.289→0.233 | 1.00 / 13.333 | 0.127 | 0.770 |
| move_above_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.150)→(0.597, 0.213, 0.259) | (0.535, -0.001, 0.137)→(0.596, 0.197, 0.151) | 0.233→0.097 | 0.33 / 2.667 | 3249.631 | 0.266 |
| place_at_goal | descend | 1.00 / step_budget | (0.597, 0.213, 0.259)→(0.605, 0.212, 0.216) | (0.596, 0.197, 0.151)→(0.598, 0.189, 0.106) | 0.097→0.104 | 1.00 / 4.000 | 0.123 | 1.330 |
| release_1 | release | 1.00 / step_budget | (0.605, 0.212, 0.216)→(0.600, 0.209, 0.235) | (0.598, 0.189, 0.106)→(0.600, 0.181, 0.016) | 0.104→0.193 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.340
- phase_score: 0.554
- phase_breakdown.reach_goal_score: 0.539
- phase_breakdown.reach_object_score: 0.576
- grasp_place_fitness: 0.643

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.643
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.340
- **Median Q (composite search score)**: -0.338
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.descend_offset_z
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74051,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10601,"approach_1.speed":0.10191,"descend_1.descend_offset_z":0.00041,"descend_1.speed":0.18389,"grasp_1.lateral_shift":0.01195,"lift_1.lift_height":0.14759,"lift_1.speed":0.09863,"move_above_goal.above_goal_x":-0.01348,"move_above_goal.above_goal_y":0.01631,"move_above_goal.above_goal_z":0.08291,"move_above_goal.speed":0.12203,"place_at_goal.place_x":0.01073,"place_at_goal.place_y":0.02206,"place_at_goal.place_z":0.00473,"place_at_goal.speed":0.05533,"release_1.release_duration":1.85426},"optimized_scores":{"best_composite_score":-0.3644,"best_fitness_score":0.5856,"best_task_score":0.22417},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":823.0,"contact_point_centroid":[0.54058,0.1785,-0.00345],"force_p95":0.71648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92455,"mean_force":0.19495,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.54061,0.18837,0.25869]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.48068,0.04608,-0.00165],"force_p95":0.4698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51387,"mean_force":0.14781,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46955,0.04608,0.03837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1761.0,"contact_point_centroid":[0.49574,0.09517,0.16763],"force_p95":0.1727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31677,"mean_force":0.10248,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.48971,0.07691,0.16678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3959.0,"contact_point_centroid":[0.47349,0.06516,0.08597],"force_p95":0.10482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30493,"mean_force":0.0617,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47212,0.04609,0.084]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3544.0,"contact_point_centroid":[0.47363,0.027,0.08638],"force_p95":0.10715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26257,"mean_force":0.06631,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47212,0.0461,0.08384]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1489.0,"contact_point_centroid":[0.4941,0.0548,0.16581],"force_p95":0.17147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2623,"mean_force":0.10514,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.48816,0.07322,0.16395]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48278,0.04847,-0.00222],"force_p95":0.18274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25528,"mean_force":0.13861,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47176,0.04632,0.0381]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49083,0.01995,0.22838]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.47068,0.02701,0.0395],"force_p95":0.07477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13651,"mean_force":0.0446,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47066,0.04621,0.03699]},{"body_a":"world","body_b":"grasp_target","contact_count":440.0,"contact_point_centroid":[0.53886,0.17919,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.56823,0.23436,0.27067]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47967,0.04413,0.10028]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53886,0.17919,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57621,0.24065,0.24646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5149.0,"contact_point_centroid":[0.47089,0.06559,0.03897],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08056,"mean_force":0.04423,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47067,0.04621,0.037]},{"body_a":"left_finger","body_b":"right_finger","contact_count":749.0,"contact_point_centroid":[0.54384,0.19437,0.26589],"force_p95":0.01299,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01568,"mean_force":0.01088,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.54341,0.19435,0.2637]},{"body_a":"left_finger","body_b":"right_finger","contact_count":466.0,"contact_point_centroid":[0.56867,0.23442,0.2729],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01052,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.56827,0.23439,0.27058]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57851,0.24167,0.24452],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57798,0.24163,0.24236]}],"total_contact_groups":16},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.53886,0.17919,0.01602],"final_tcp_position":[0.57948,0.24214,0.24697],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.89304,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":816.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48217,0.04148,0.15424],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17385,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11765.0,"raw_peak_contact_force":0.25528,"subtask_id":"reach_object","tcp_end":[0.47883,0.04697,0.04559],"tcp_start":[0.48217,0.04148,0.15424],"tcp_to_object_dist_end":0.02003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48266,0.04681,0.02525],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29173,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.11126,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7571.0,"raw_peak_contact_force":0.51387,"subtask_id":"reach_object","tcp_end":[0.47064,0.04621,0.03696],"tcp_start":[0.47883,0.04697,0.04559],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":213.0,"n_steps_budget":870.0,"object_pos_end":[0.49496,0.04682,0.12999],"object_pos_start":[0.48266,0.04681,0.02525],"object_to_goal_dist_end":0.22536,"object_to_goal_dist_start":0.29173,"object_z_max":0.12952,"peak_contact_force":0.12267,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4822.0,"raw_peak_contact_force":1.92455,"subtask_id":"reach_object","tcp_end":[0.47741,0.04634,0.14379],"tcp_start":[0.47064,0.04621,0.03696],"tcp_to_object_dist_end":0.02233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.53886,0.17918,0.01602],"object_pos_start":[0.49496,0.04682,0.12999],"object_to_goal_dist_end":0.2243,"object_to_goal_dist_start":0.22536,"object_z_max":0.17086,"peak_contact_force":9748.89304,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":906.0,"raw_peak_contact_force":0.12268,"subtask_id":"reach_goal","tcp_end":[0.55901,0.22722,0.29147],"tcp_start":[0.47741,0.04634,0.14379],"tcp_to_object_dist_end":0.28034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.53886,0.17919,0.01602],"object_pos_start":[0.53886,0.17918,0.01602],"object_to_goal_dist_end":0.2243,"object_to_goal_dist_start":0.2243,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.57948,0.24214,0.24697],"tcp_start":[0.55901,0.22722,0.29147],"tcp_to_object_dist_end":0.2428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53886,0.17919,0.01602],"object_pos_start":[0.53886,0.17919,0.01602],"object_to_goal_dist_end":0.2243,"object_to_goal_dist_start":0.2243,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.57521,0.24007,0.26615],"tcp_start":[0.57948,0.24214,0.24697],"tcp_to_object_dist_end":0.25998,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.815,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11384,"approach_1.speed":0.09463,"descend_1.descend_offset_z":0.00017,"descend_1.speed":0.14304,"grasp_1.lateral_shift":0.00896,"lift_1.lift_height":0.15566,"lift_1.speed":0.11247,"move_above_goal.above_goal_x":-0.00895,"move_above_goal.above_goal_y":0.0164,"move_above_goal.above_goal_z":0.06491,"move_above_goal.speed":0.0713,"place_at_goal.place_x":-0.00461,"place_at_goal.place_y":-0.00094,"place_at_goal.place_z":-0.01307,"place_at_goal.speed":0.04178,"release_1.release_duration":1.58464},"optimized_scores":{"best_composite_score":-0.33787,"best_fitness_score":0.61213,"best_task_score":0.27765},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":622.0,"contact_point_centroid":[0.61367,0.21061,-0.004],"force_p95":0.84165,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07721,"mean_force":0.20311,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59401,0.22216,0.2127]},{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.53506,-0.02048,-0.00149],"force_p95":0.48111,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5176,"mean_force":0.14005,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52125,-0.02047,0.03556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":337.0,"contact_point_centroid":[0.59989,0.24135,0.24133],"force_p95":0.19291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31172,"mean_force":0.14063,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.5944,0.2232,0.24631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3304.0,"contact_point_centroid":[0.52775,-0.00152,0.08736],"force_p95":0.11624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30537,"mean_force":0.07925,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52448,-0.02043,0.08489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.52785,-0.03921,0.08594],"force_p95":0.11265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28937,"mean_force":0.07472,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52443,-0.02043,0.08423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.59965,0.20541,0.24002],"force_p95":0.2121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27617,"mean_force":0.12188,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.59455,0.2232,0.24488]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02113,-0.00207],"force_p95":0.14459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19772,"mean_force":0.12854,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52361,-0.02052,0.03581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5523.0,"contact_point_centroid":[0.56581,0.11537,0.19967],"force_p95":0.12816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18983,"mean_force":0.09026,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56006,0.09692,0.19947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5552.0,"contact_point_centroid":[0.56518,0.07619,0.19892],"force_p95":0.12664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17878,"mean_force":0.09111,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.55953,0.09465,0.1986]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51312,-0.00868,0.23183]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.52346,-0.0013,0.03715],"force_p95":0.07836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12976,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5224,-0.0205,0.03445]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52894,-0.01932,0.1033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4933.0,"contact_point_centroid":[0.52342,-0.0396,0.03623],"force_p95":0.07047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08102,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52241,-0.0205,0.03445]}],"total_contact_groups":13},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61357,0.21054,0.016],"final_tcp_position":[0.59853,0.22411,0.2127],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.07721,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":840.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52841,-0.01805,0.16131],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1403,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.19772,"subtask_id":"reach_object","tcp_end":[0.5313,-0.02064,0.04495],"tcp_start":[0.52841,-0.01805,0.16131],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.0205,0.02574],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31626,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.10466,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6983.0,"raw_peak_contact_force":0.5176,"subtask_id":"reach_object","tcp_end":[0.52237,-0.0205,0.03441],"tcp_start":[0.5313,-0.02064,0.04495],"tcp_to_object_dist_end":0.01694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":244.0,"n_steps_budget":840.0,"object_pos_end":[0.55096,-0.02038,0.13955],"object_pos_start":[0.53692,-0.0205,0.02574],"object_to_goal_dist_end":0.26401,"object_to_goal_dist_start":0.31626,"object_z_max":0.13911,"peak_contact_force":0.12956,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11075.0,"raw_peak_contact_force":0.18983,"subtask_id":"reach_object","tcp_end":[0.53124,-0.02042,0.15236],"tcp_start":[0.52237,-0.0205,0.03441],"tcp_to_object_dist_end":0.02351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.60172,0.22164,0.23066],"object_pos_start":[0.55096,-0.02038,0.13955],"object_to_goal_dist_end":0.02553,"object_to_goal_dist_start":0.26401,"object_z_max":0.23049,"peak_contact_force":0.0,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":665.0,"raw_peak_contact_force":0.31172,"subtask_id":"reach_goal","tcp_end":[0.59371,0.2218,0.25421],"tcp_start":[0.53124,-0.02042,0.15236],"tcp_to_object_dist_end":0.02488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.60933,0.21607,0.15326],"object_pos_start":[0.60172,0.22164,0.23066],"object_to_goal_dist_end":0.05541,"object_to_goal_dist_start":0.02553,"object_z_max":0.23074,"peak_contact_force":0.12281,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":622.0,"raw_peak_contact_force":2.07721,"subtask_id":"reach_goal","tcp_end":[0.59853,0.22411,0.2127],"tcp_start":[0.59371,0.2218,0.25421],"tcp_to_object_dist_end":0.06095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61357,0.21054,0.016],"object_pos_start":[0.60933,0.21607,0.15326],"object_to_goal_dist_end":0.19221,"object_to_goal_dist_start":0.05541,"object_z_max":0.15326,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.59341,0.22187,0.23122],"tcp_start":[0.59853,0.22411,0.2127],"tcp_to_object_dist_end":0.21646,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57436,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10167,"approach_1.speed":0.13949,"descend_1.descend_offset_z":0.0,"descend_1.speed":0.10753,"grasp_1.lateral_shift":0.00925,"lift_1.lift_height":0.1565,"lift_1.speed":0.10468,"move_above_goal.above_goal_x":0.01807,"move_above_goal.above_goal_y":0.04618,"move_above_goal.above_goal_z":0.0703,"move_above_goal.speed":0.06343,"place_at_goal.place_x":0.00699,"place_at_goal.place_y":-0.00951,"place_at_goal.place_z":-0.00153,"place_at_goal.speed":0.05698,"release_1.release_duration":1.49592},"optimized_scores":{"best_composite_score":-0.30704,"best_fitness_score":0.64296,"best_task_score":0.33974},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":567.0,"contact_point_centroid":[0.64682,0.15382,-0.00417],"force_p95":1.02813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7902,"mean_force":0.2123,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63188,0.16668,0.19]},{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.54337,-0.02796,-0.00154],"force_p95":0.48144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51977,"mean_force":0.15127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52944,-0.028,0.03507]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":583.0,"contact_point_centroid":[0.64314,0.20127,0.21007],"force_p95":0.16901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36457,"mean_force":0.10868,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63801,0.18358,0.21487]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3387.0,"contact_point_centroid":[0.53602,-0.00903,0.08757],"force_p95":0.1163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2998,"mean_force":0.07888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53277,-0.02795,0.08505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3722.0,"contact_point_centroid":[0.53606,-0.04674,0.08591],"force_p95":0.11244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29246,"mean_force":0.07423,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5327,-0.02795,0.08421]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":403.0,"contact_point_centroid":[0.64331,0.16781,0.21387],"force_p95":0.21902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28474,"mean_force":0.13577,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.63823,0.18566,0.21868]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02901,-0.00211],"force_p95":0.15427,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22199,"mean_force":0.13104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5318,-0.02808,0.03533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5081.0,"contact_point_centroid":[0.59172,0.09485,0.18771],"force_p95":0.13434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19664,"mean_force":0.09336,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58599,0.07639,0.18766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5324.0,"contact_point_centroid":[0.5908,0.05591,0.18697],"force_p95":0.12865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19028,"mean_force":0.09142,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.58509,0.07432,0.18699]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.53179,-0.00883,0.03662],"force_p95":0.07982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14308,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53058,-0.02804,0.03392]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51696,-0.01221,0.22486]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53688,-0.02668,0.09694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4973.0,"contact_point_centroid":[0.53172,-0.04717,0.03569],"force_p95":0.07213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08149,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53059,-0.02804,0.03393]}],"total_contact_groups":13},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64682,0.15352,0.01599],"final_tcp_position":[0.63694,0.16886,0.1895],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.7902,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":776.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53607,-0.02515,0.14844],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14814,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10852.0,"raw_peak_contact_force":0.22199,"subtask_id":"reach_object","tcp_end":[0.53958,-0.02828,0.04474],"tcp_start":[0.53607,-0.02515,0.14844],"tcp_to_object_dist_end":0.01969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02811,0.02563],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26035,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.10507,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7177.0,"raw_peak_contact_force":0.51977,"subtask_id":"reach_object","tcp_end":[0.53055,-0.02804,0.03388],"tcp_start":[0.53958,-0.02828,0.04474],"tcp_to_object_dist_end":0.01709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":249.0,"n_steps_budget":900.0,"object_pos_end":[0.55951,-0.02795,0.14058],"object_pos_start":[0.54551,-0.02811,0.02563],"object_to_goal_dist_end":0.20953,"object_to_goal_dist_start":0.26035,"object_z_max":0.14014,"peak_contact_force":0.1282,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10405.0,"raw_peak_contact_force":0.19664,"subtask_id":"reach_object","tcp_end":[0.53972,-0.02798,0.15306],"tcp_start":[0.53055,-0.02804,0.03388],"tcp_to_object_dist_end":0.0234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.64716,0.18974,0.20649],"object_pos_start":[0.55951,-0.02795,0.14058],"object_to_goal_dist_end":0.04117,"object_to_goal_dist_start":0.20953,"object_z_max":0.20636,"peak_contact_force":0.0,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":986.0,"raw_peak_contact_force":0.36457,"subtask_id":"reach_goal","tcp_end":[0.63931,0.18996,0.23005],"tcp_start":[0.53972,-0.02798,0.15306],"tcp_to_object_dist_end":0.02484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.64595,0.17305,0.14859],"object_pos_start":[0.64716,0.18974,0.20649],"object_to_goal_dist_end":0.03225,"object_to_goal_dist_start":0.04117,"object_z_max":0.20654,"peak_contact_force":0.12336,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":567.0,"raw_peak_contact_force":1.7902,"subtask_id":"reach_goal","tcp_end":[0.63694,0.16886,0.1895],"tcp_start":[0.63931,0.18996,0.23005],"tcp_to_object_dist_end":0.0421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64682,0.15352,0.01599],"object_pos_start":[0.64595,0.17305,0.14859],"object_to_goal_dist_end":0.16193,"object_to_goal_dist_start":0.03225,"object_z_max":0.14859,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.63137,0.16649,0.20771],"tcp_start":[0.63694,0.16886,0.1895],"tcp_to_object_dist_end":0.19277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```