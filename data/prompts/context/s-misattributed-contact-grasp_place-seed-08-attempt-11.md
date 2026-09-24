## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 17 | -0.3793 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.0259 | 0.65 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 14 | 0.1019 | 0.90 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.3259 | 0.89 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.2579 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.379) — your mutation base

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

- **Composite score**: -0.379
- **task_score** (E): 0.286
- **fitness_score**: 0.621  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1321 |
| descend_1 | 1.00 | 1.00 | 0.1376 |
| grasp_1 | 1.00 | 1.00 | 0.0131 |
| lift_1 | 1.00 | 1.00 | 0.0992 |
| move_above_goal | 1.00 | 1.00 | 0.2764 |
| place_at_goal | 1.00 | 1.00 | 0.0540 |
| release | 1.00 | 1.00 | 0.0196 |
| retract | 1.00 | 1.00 | 0.0371 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.175) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.175)→(0.517, -0.001, 0.038) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 40.667 | 0.154 | 0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.038)→(0.508, -0.001, 0.028) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.290 | 1.00 / 23.667 | 66.278 | 0.736 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.028)→(0.516, -0.001, 0.127) | (0.522, -0.001, 0.026)→(0.534, -0.001, 0.123) | 0.290→0.237 | 1.00 / 6.333 | 91008.142 | 2.214 |
| move_above_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.127)→(0.599, 0.217, 0.271) | (0.534, -0.001, 0.123)→(0.617, 0.190, 0.015) | 0.237→0.191 | 1.00 / 8.000 | 0.138 | 0.719 |
| place_at_goal | descend | 1.00 / step_budget | (0.599, 0.217, 0.271)→(0.610, 0.209, 0.223) | (0.617, 0.190, 0.015)→(0.613, 0.196, 0.016) | 0.191→0.189 | 1.00 / 4.000 | 0.123 | 0.137 |
| release | release | 1.00 / step_budget | (0.610, 0.209, 0.223)→(0.605, 0.207, 0.242) | (0.613, 0.196, 0.016)→(0.613, 0.195, 0.016) | 0.189→0.190 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.605, 0.207, 0.242)→(0.603, 0.206, 0.279) | (0.613, 0.195, 0.016)→(0.613, 0.195, 0.016) | 0.190→0.190 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.340
- phase_score: 0.506
- phase_breakdown.reach_goal_score: 0.595
- phase_breakdown.reach_object_score: 0.373
- grasp_place_fitness: 0.646

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.646
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.340
- **Median Q (composite search score)**: -0.384
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.332


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97917,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.height_approach":0.137,"approach_1.speed":0.1547,"descend_1.descend_z":-0.00984,"descend_1.speed":0.08485,"lift_1.lift_height":0.1366,"lift_1.speed":0.128,"move_above_goal.above_goal_x":-0.00559,"move_above_goal.above_goal_y":-0.01362,"move_above_goal.above_goal_z":0.07374,"move_above_goal.speed":0.37542,"place_at_goal.place_x":0.00082,"place_at_goal.place_y":0.00057,"place_at_goal.place_z":-0.00074,"place_at_goal.speed":0.07057,"release.release_time":0.59771,"retract.post_release_z":0.03052,"retract.speed":0.14193},"optimized_scores":{"best_composite_score":-0.39956,"best_fitness_score":0.60044,"best_task_score":0.23922},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":13.0,"contact_point_centroid":[0.60119,0.20648,-0.00613],"force_p95":2.17588,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18134,"mean_force":1.78521,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56509,0.19792,0.28002]},{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.58401,0.21703,-0.0064],"force_p95":1.3253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9042,"mean_force":0.31675,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57051,0.20921,0.26024]},{"body_a":"world","body_b":"grasp_target","contact_count":63.0,"contact_point_centroid":[0.47994,0.0457,-0.00164],"force_p95":0.72271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76962,"mean_force":0.2239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46972,0.04618,0.02811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3103.0,"contact_point_centroid":[0.51214,0.11651,0.18249],"force_p95":0.15975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39818,"mean_force":0.0977,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.50665,0.09808,0.18142]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3665.0,"contact_point_centroid":[0.47321,0.02683,0.07849],"force_p95":0.10078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36602,"mean_force":0.06145,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47252,0.04599,0.07598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2741.0,"contact_point_centroid":[0.51229,0.07998,0.18354],"force_p95":0.17966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34604,"mean_force":0.10551,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.50691,0.09852,0.18188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4059.0,"contact_point_centroid":[0.4732,0.06508,0.07802],"force_p95":0.09316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34039,"mean_force":0.05717,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47253,0.04599,0.07609]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04823,-0.00222],"force_p95":0.18832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27482,"mean_force":0.13977,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47186,0.04642,0.0279]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57892,0.22332,-0.00196],"force_p95":0.13673,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16636,"mean_force":0.12351,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57107,0.21618,0.243]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49129,0.0192,0.24335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3599.0,"contact_point_centroid":[0.47175,0.02706,0.03011],"force_p95":0.09134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12754,"mean_force":0.05772,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47078,0.04632,0.02682]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48009,0.04343,0.11043]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.57892,0.22334,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5691,0.21529,0.26729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5379.0,"contact_point_centroid":[0.47046,0.0655,0.02903],"force_p95":0.07513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08146,"mean_force":0.04258,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47079,0.04632,0.02683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.57165,0.21158,0.2567],"force_p95":0.01462,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01174,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.57163,0.21157,0.25468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.573,0.21717,0.24072],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57295,0.21716,0.23862]}],"total_contact_groups":16},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57892,0.22334,0.01602],"final_tcp_position":[0.56841,0.21494,0.27375],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":198.61505,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1160.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48295,0.04001,0.18479],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.17229,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10778.0,"raw_peak_contact_force":0.27482,"subtask_id":"reach_object","tcp_end":[0.47889,0.04709,0.03529],"tcp_start":[0.48295,0.04001,0.18479],"tcp_to_object_dist_end":0.01016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48263,0.0463,0.02528],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29203,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":198.61505,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7787.0,"raw_peak_contact_force":0.76962,"subtask_id":"reach_object","tcp_end":[0.47076,0.04631,0.02679],"tcp_start":[0.47889,0.04709,0.03529],"tcp_to_object_dist_end":0.01197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":204.0,"n_steps_budget":690.0,"object_pos_end":[0.49513,0.04608,0.12952],"object_pos_start":[0.48263,0.0463,0.02528],"object_to_goal_dist_end":0.22611,"object_to_goal_dist_start":0.29203,"object_z_max":0.12903,"peak_contact_force":1.92534,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5857.0,"raw_peak_contact_force":2.18134,"subtask_id":"reach_object","tcp_end":[0.47753,0.04594,0.13234],"tcp_start":[0.47076,0.04631,0.02679],"tcp_to_object_dist_end":0.01783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.59131,0.2083,0.01144],"object_pos_start":[0.49513,0.04608,0.12952],"object_to_goal_dist_end":0.22021,"object_to_goal_dist_start":0.22611,"object_z_max":0.223,"peak_contact_force":0.16818,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":1.9042,"subtask_id":"reach_goal","tcp_end":[0.56586,0.19932,0.28141],"tcp_start":[0.47753,0.04594,0.13234],"tcp_to_object_dist_end":0.27131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.57829,0.22426,0.01698],"object_pos_start":[0.59131,0.2083,0.01144],"object_to_goal_dist_end":0.21359,"object_to_goal_dist_start":0.22021,"object_z_max":0.01758,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.16636,"subtask_id":"reach_goal","tcp_end":[0.57451,0.21735,0.24279],"tcp_start":[0.56586,0.19932,0.28141],"tcp_to_object_dist_end":0.22595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57892,0.22334,0.01602],"object_pos_start":[0.57829,0.22426,0.01698],"object_to_goal_dist_end":0.21456,"object_to_goal_dist_start":0.21359,"object_z_max":0.01698,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":220.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56999,0.21563,0.26292],"tcp_start":[0.57451,0.21735,0.24279],"tcp_to_object_dist_end":0.24718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":600.0,"object_pos_end":[0.57892,0.22334,0.01602],"object_pos_start":[0.57892,0.22334,0.01602],"object_to_goal_dist_end":0.21456,"object_to_goal_dist_start":0.21456,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.56841,0.21494,0.27375],"tcp_start":[0.56999,0.21563,0.26292],"tcp_to_object_dist_end":0.25808,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10563,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.height_approach":0.13181,"approach_1.speed":0.15283,"descend_1.descend_z":-0.00568,"descend_1.speed":0.18832,"lift_1.lift_height":0.12005,"lift_1.speed":0.17022,"move_above_goal.above_goal_x":-0.00155,"move_above_goal.above_goal_y":0.05716,"move_above_goal.above_goal_z":0.07681,"move_above_goal.speed":0.48714,"place_at_goal.place_x":0.02986,"place_at_goal.place_y":0.00027,"place_at_goal.place_z":0.01108,"place_at_goal.speed":0.03492,"release.release_time":0.48883,"retract.post_release_z":0.07341,"retract.speed":0.16712},"optimized_scores":{"best_composite_score":-0.38437,"best_fitness_score":0.61563,"best_task_score":0.27776},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":409.0,"contact_point_centroid":[0.61591,0.21164,-0.00459],"force_p95":1.0142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23498,"mean_force":0.24609,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.59481,0.2355,0.24937]},{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.53374,-0.02006,-0.00149],"force_p95":0.55558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70625,"mean_force":0.20784,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52168,-0.02049,0.03004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2963.0,"contact_point_centroid":[0.55356,0.03765,0.15593],"force_p95":0.17033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40306,"mean_force":0.10208,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.54829,0.05626,0.15407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3064.0,"contact_point_centroid":[0.52609,-0.00128,0.07293],"force_p95":0.1039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37227,"mean_force":0.0651,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52494,-0.02041,0.07036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3421.0,"contact_point_centroid":[0.5261,-0.03941,0.07078],"force_p95":0.09898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33725,"mean_force":0.05988,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52479,-0.02041,0.06901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3517.0,"contact_point_centroid":[0.5562,0.08404,0.16055],"force_p95":0.14,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30574,"mean_force":0.09238,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.55064,0.0657,0.15893]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.0211,-0.00207],"force_p95":0.14497,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2065,"mean_force":0.12869,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52382,-0.02053,0.0303]},{"body_a":"world","body_b":"grasp_target","contact_count":936.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5129,-0.00849,0.24031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4086.0,"contact_point_centroid":[0.52349,-0.0013,0.03173],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13004,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52264,-0.02051,0.02896]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.61539,0.21151,-0.00198],"force_p95":0.12545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12695,"mean_force":0.12311,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61178,0.25332,0.2458]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61539,0.2115,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62188,0.2367,0.22436]},{"body_a":"world","body_b":"grasp_target","contact_count":980.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52874,-0.01911,0.10942]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.61539,0.2115,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61873,0.23527,0.26969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4938.0,"contact_point_centroid":[0.52351,-0.03961,0.03082],"force_p95":0.07052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08519,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52264,-0.02051,0.02897]},{"body_a":"left_finger","body_b":"right_finger","contact_count":243.0,"contact_point_centroid":[0.59822,0.2479,0.25826],"force_p95":0.01469,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01154,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.59815,0.24788,0.25605]},{"body_a":"left_finger","body_b":"right_finger","contact_count":494.0,"contact_point_centroid":[0.6119,0.25331,0.24795],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.6118,0.2533,0.24575]}],"total_contact_groups":17},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61539,0.2115,0.01602],"final_tcp_position":[0.61852,0.23512,0.29717],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.23498,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":980.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52783,-0.01764,0.17911],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14034,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10824.0,"raw_peak_contact_force":0.2065,"subtask_id":"reach_object","tcp_end":[0.53149,-0.02066,0.03936],"tcp_start":[0.52783,-0.01764,0.17911],"tcp_to_object_dist_end":0.01446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02045,0.02574],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31622,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.10648,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6547.0,"raw_peak_contact_force":0.70625,"subtask_id":"reach_object","tcp_end":[0.52261,-0.0205,0.02893],"tcp_start":[0.53149,-0.02066,0.03936],"tcp_to_object_dist_end":0.01465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":180.0,"n_steps_budget":600.0,"object_pos_end":[0.5484,-0.0203,0.1126],"object_pos_start":[0.5369,-0.02045,0.02574],"object_to_goal_dist_end":0.27268,"object_to_goal_dist_start":0.31622,"object_z_max":0.11215,"peak_contact_force":0.12705,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7132.0,"raw_peak_contact_force":2.23498,"subtask_id":"reach_object","tcp_end":[0.53057,-0.02037,0.1168],"tcp_start":[0.52261,-0.0205,0.02893],"tcp_to_object_dist_end":0.01832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.61545,0.21139,0.01625],"object_pos_start":[0.5484,-0.0203,0.1126],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.27268,"object_z_max":0.18717,"peak_contact_force":0.12263,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":0.12695,"subtask_id":"reach_goal","tcp_end":[0.60211,0.26357,0.26439],"tcp_start":[0.53057,-0.02037,0.1168],"tcp_to_object_dist_end":0.25392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.61539,0.21151,0.01602],"object_pos_start":[0.61545,0.21139,0.01625],"object_to_goal_dist_end":0.19215,"object_to_goal_dist_start":0.19193,"object_z_max":0.01625,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_goal","tcp_end":[0.62511,0.23899,0.22541],"tcp_start":[0.60211,0.26357,0.26439],"tcp_to_object_dist_end":0.21141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61539,0.2115,0.01602],"object_pos_start":[0.61539,0.21151,0.01602],"object_to_goal_dist_end":0.19215,"object_to_goal_dist_start":0.19215,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62066,0.23618,0.24353],"tcp_start":[0.62511,0.23899,0.22541],"tcp_to_object_dist_end":0.22891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":600.0,"object_pos_end":[0.61539,0.2115,0.01602],"object_pos_start":[0.61539,0.2115,0.01602],"object_to_goal_dist_end":0.19215,"object_to_goal_dist_start":0.19215,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":936.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.61852,0.23512,0.29717],"tcp_start":[0.62066,0.23618,0.24353],"tcp_to_object_dist_end":0.28216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71585,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.height_approach":0.11501,"approach_1.speed":0.1841,"descend_1.descend_z":-0.0062,"descend_1.speed":0.05052,"lift_1.lift_height":0.13443,"lift_1.speed":0.10096,"move_above_goal.above_goal_x":0.00574,"move_above_goal.above_goal_y":0.0411,"move_above_goal.above_goal_z":0.11096,"move_above_goal.speed":0.3916,"place_at_goal.place_x":0.00064,"place_at_goal.place_y":0.001,"place_at_goal.place_z":0.00623,"place_at_goal.speed":0.04892,"release.release_time":0.44398,"retract.post_release_z":0.06639,"retract.speed":0.11722},"optimized_scores":{"best_composite_score":-0.35386,"best_fitness_score":0.64614,"best_task_score":0.33988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":347.0,"contact_point_centroid":[0.64469,0.15154,-0.0052],"force_p95":1.08307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.22429,"mean_force":0.27091,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.62039,0.16646,0.25347]},{"body_a":"world","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.54253,-0.02785,-0.00149],"force_p95":0.60654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73083,"mean_force":0.19189,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52968,-0.02803,0.02898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3265.0,"contact_point_centroid":[0.53483,-0.00891,0.07508],"force_p95":0.1132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36971,"mean_force":0.07206,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53272,-0.02794,0.07246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2455.0,"contact_point_centroid":[0.56693,0.00959,0.16578],"force_p95":0.1705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35235,"mean_force":0.10195,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56142,0.02822,0.16411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3622.0,"contact_point_centroid":[0.5349,-0.04684,0.07333],"force_p95":0.10772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34616,"mean_force":0.0672,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53263,-0.02794,0.07151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2999.0,"contact_point_centroid":[0.56981,0.0531,0.16972],"force_p95":0.14339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2859,"mean_force":0.09191,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56411,0.03476,0.16818]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02896,-0.00211],"force_p95":0.1546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22806,"mean_force":0.13114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53187,-0.02811,0.02921]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51682,-0.01204,0.23123]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4070.0,"contact_point_centroid":[0.53171,-0.00886,0.03059],"force_p95":0.07949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13792,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53066,-0.02807,0.02783]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.6441,0.15126,-0.00196],"force_p95":0.12537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12574,"mean_force":0.12308,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62897,0.18092,0.23674]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53652,-0.02652,0.10059]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6441,0.15126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62535,0.17033,0.20062]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.6441,0.15126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62179,0.16918,0.24274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4974.0,"contact_point_centroid":[0.5317,-0.0472,0.02968],"force_p95":0.07216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0853,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53066,-0.02807,0.02783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":184.0,"contact_point_centroid":[0.62494,0.17684,0.26254],"force_p95":0.01476,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01189,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.62491,0.17683,0.26025]},{"body_a":"left_finger","body_b":"right_finger","contact_count":527.0,"contact_point_centroid":[0.62896,0.18095,0.23917],"force_p95":0.01109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01058,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62898,0.18094,0.23683]}],"total_contact_groups":17},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.6441,0.15126,0.01602],"final_tcp_position":[0.62131,0.16899,0.2667],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273022.37357,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53578,-0.02485,0.16148],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1479,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10844.0,"raw_peak_contact_force":0.22806,"subtask_id":"reach_object","tcp_end":[0.53956,-0.02832,0.03844],"tcp_start":[0.53578,-0.02485,0.16148],"tcp_to_object_dist_end":0.01384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02805,0.02564],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2603,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.11122,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6953.0,"raw_peak_contact_force":0.73083,"subtask_id":"reach_object","tcp_end":[0.53063,-0.02806,0.02779],"tcp_start":[0.53956,-0.02832,0.03844],"tcp_to_object_dist_end":0.01501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":217.0,"n_steps_budget":840.0,"object_pos_end":[0.55906,-0.02785,0.12709],"object_pos_start":[0.54548,-0.02805,0.02564],"object_to_goal_dist_end":0.21235,"object_to_goal_dist_start":0.2603,"object_z_max":0.12664,"peak_contact_force":273022.37357,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5985.0,"raw_peak_contact_force":2.22429,"subtask_id":"reach_object","tcp_end":[0.53928,-0.0279,0.13108],"tcp_start":[0.53063,-0.02806,0.02779],"tcp_to_object_dist_end":0.02018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.6441,0.15118,0.01655],"object_pos_start":[0.55906,-0.02785,0.12709],"object_to_goal_dist_end":0.16135,"object_to_goal_dist_start":0.21235,"object_z_max":0.19196,"peak_contact_force":0.12263,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12574,"subtask_id":"reach_goal","tcp_end":[0.62923,0.18712,0.26693],"tcp_start":[0.53928,-0.0279,0.13108],"tcp_to_object_dist_end":0.25338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.6441,0.15126,0.01602],"object_pos_start":[0.6441,0.15118,0.01655],"object_to_goal_dist_end":0.16187,"object_to_goal_dist_start":0.16135,"object_z_max":0.01655,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62947,0.17198,0.20168],"tcp_start":[0.62923,0.18712,0.26693],"tcp_to_object_dist_end":0.18739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6441,0.15126,0.01602],"object_pos_start":[0.6441,0.15126,0.01602],"object_to_goal_dist_end":0.16187,"object_to_goal_dist_start":0.16187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":792.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62395,0.16989,0.22007],"tcp_start":[0.62947,0.17198,0.20168],"tcp_to_object_dist_end":0.20589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":600.0,"object_pos_end":[0.6441,0.15126,0.01602],"object_pos_start":[0.6441,0.15126,0.01602],"object_to_goal_dist_end":0.16187,"object_to_goal_dist_start":0.16187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62131,0.16899,0.2667],"tcp_start":[0.62395,0.16989,0.22007],"tcp_to_object_dist_end":0.25234,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```