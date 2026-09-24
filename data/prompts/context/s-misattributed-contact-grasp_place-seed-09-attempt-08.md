## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0087 | 0.19 | ❌ rejected |
| 7 | approach → descend → grasp → pull → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0152 | 0.24 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | -0.2526 | 0.17 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.2863 | 0.14 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.3197 | 0.14 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=-0.009) — your mutation base

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
  weight: 0.3
- id: place_object
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp
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
  - id: grasp_bilateral
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: pull_up
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    pull_up_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: pull_object_follows
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_object_lost
    when: after_phase
    predicate: object_lifted
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: reach_object
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_object
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: place_object
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **pull_up** (`pull`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - pull_up_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=pull_object_follows, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_object_lost, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: -0.009
- **task_score** (E): 0.188
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1208 |
| descend_to_grasp | 1.00 | 1.00 | 0.1468 |
| grasp | 1.00 | 1.00 | 0.0126 |
| pull_up | 1.00 | 1.00 | 0.0216 |
| lift | 1.00 | 1.00 | 0.0894 |
| approach_goal | 1.00 | 1.00 | 0.2640 |
| descend_place | 1.00 | 1.00 | 0.1258 |
| release_object | 1.00 | 1.00 | 0.0194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.000, 0.186) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.512, 0.000, 0.186)→(0.510, -0.015, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.169 | 0.261 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.015, 0.040)→(0.502, -0.015, 0.030) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 38.000 | 0.079 | 0.510 |
| pull_up | pull | 1.00 / step_budget | (0.497, -0.015, 0.052)→(0.493, -0.015, 0.073) | (0.515, -0.015, 0.025)→(0.509, -0.015, 0.044) | 0.269→0.262 | 1.00 / 14.000 | 0.146 | 1.020 |
| lift | lift | 1.00 / step_budget | (0.486, -0.014, 0.252)→(0.484, -0.014, 0.341) | (0.503, -0.015, 0.063)→(0.499, -0.015, 0.150) | 0.257→0.246 | 1.00 / 8.333 | 3249.669 | 1.409 |
| approach_goal | approach | 1.00 / step_budget | (0.484, -0.014, 0.341)→(0.608, 0.170, 0.313) | (0.504, -0.009, 0.166)→(0.514, 0.014, 0.016) | 0.238→0.253 | 1.00 / 8.333 | 3249.647 | 0.123 |
| descend_place | descend | 1.00 / step_budget | (0.608, 0.170, 0.313)→(0.613, 0.178, 0.188) | (0.514, 0.014, 0.016)→(0.514, 0.014, 0.016) | 0.253→0.253 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.613, 0.178, 0.188)→(0.607, 0.177, 0.206) | (0.514, 0.014, 0.016)→(0.514, 0.014, 0.016) | 0.253→0.253 | 1.00 / 4.000 | 27.129 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.227
- phase_score: 0.000
- phase_breakdown.reach_object_score: 0.002
- phase_breakdown.place_object_score: 0.000
- grasp_place_fitness: 0.592

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.592
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.227
- **Median Q (composite search score)**: -0.005
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.333


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38854,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09414,"approach_object.approach_arc_height":0.11487,"approach_object.approach_speed":0.04724,"descend_to_grasp.descend_speed":0.06177,"lift.lift_height":0.09419,"lift.lift_speed":0.05581,"pull_up.pull_up_speed":0.04005,"release_object.release_timeout":0.33131},"optimized_scores":{"best_composite_score":-0.03305,"best_fitness_score":0.54695,"best_task_score":0.14094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2219.0,"contact_point_centroid":[0.53015,0.01968,-0.0026],"force_p95":0.16464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33731,"mean_force":0.15103,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5655,0.12728,0.32522]},{"body_a":"world","body_b":"grasp_target","contact_count":239.0,"contact_point_centroid":[0.53061,-0.01739,-0.00131],"force_p95":0.35649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51949,"mean_force":0.11615,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52057,-0.01904,0.03146]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53712,-0.02091,-0.00221],"force_p95":0.18341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2649,"mean_force":0.13841,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52402,-0.0191,0.03105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12354.0,"contact_point_centroid":[0.51717,-0.03796,0.05226],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26155,"mean_force":0.05268,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.51637,-0.01895,0.05032]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10824.0,"contact_point_centroid":[0.51714,0.00021,0.0537],"force_p95":0.08436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25792,"mean_force":0.05811,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.51623,-0.01895,0.05112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11790.0,"contact_point_centroid":[0.50989,-0.03761,0.16982],"force_p95":0.10836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24818,"mean_force":0.06526,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50735,-0.01876,0.16865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":375.0,"contact_point_centroid":[0.5127,0.00804,0.29176],"force_p95":0.2131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24604,"mean_force":0.14975,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50715,-0.01005,0.29636]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11250.0,"contact_point_centroid":[0.50987,0.00016,0.16674],"force_p95":0.11309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23555,"mean_force":0.06741,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50748,-0.01877,0.1653]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":561.0,"contact_point_centroid":[0.51288,-0.02523,0.29156],"force_p95":0.15911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18999,"mean_force":0.10822,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50796,-0.00783,0.2965]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3624.0,"contact_point_centroid":[0.52451,0.00012,0.03274],"force_p95":0.08994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15564,"mean_force":0.05736,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5228,-0.01908,0.02967]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13648,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5139,0.01335,0.24343]},{"body_a":"world","body_b":"grasp_target","contact_count":1436.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5293,-0.01158,0.11356]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.53002,0.01965,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60472,0.21819,0.288]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53002,0.01965,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60295,0.22224,0.22524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.52389,-0.03824,0.03155],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08594,"mean_force":0.04581,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5228,-0.01908,0.02968]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2231.0,"contact_point_centroid":[0.56806,0.13214,0.32868],"force_p95":0.01116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0159,"mean_force":0.01059,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56762,0.13214,0.32637]}],"total_contact_groups":18},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53002,0.01965,0.01602],"final_tcp_position":[0.60658,0.22372,0.22654],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":81.14227,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52956,-0.00419,0.18706],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.16927,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10361.0,"raw_peak_contact_force":0.2649,"subtask_id":"reach_object","tcp_end":[0.53149,-0.01915,0.03973],"tcp_start":[0.52956,-0.00419,0.18706],"tcp_to_object_dist_end":0.01495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.01918,0.02532],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31546,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.07935,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":23417.0,"raw_peak_contact_force":0.51949,"tcp_end":[0.52277,-0.01907,0.02964],"tcp_start":[0.53149,-0.01915,0.03973],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":624.0,"n_steps_budget":600.0,"object_pos_end":[0.53111,-0.01899,0.04405],"object_pos_start":[0.53694,-0.01918,0.02532],"object_to_goal_dist_end":0.30634,"object_to_goal_dist_start":0.31546,"object_z_max":0.06194,"peak_contact_force":0.15112,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":23040.0,"raw_peak_contact_force":0.24818,"tcp_end":[0.51321,-0.01889,0.07216],"tcp_start":[0.5179,-0.01898,0.05095],"tcp_to_object_dist_end":0.03332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.51914,-0.01886,0.13424],"object_pos_start":[0.5245,-0.019,0.06198],"object_to_goal_dist_end":0.27292,"object_to_goal_dist_start":0.299,"object_z_max":0.27505,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5386.0,"raw_peak_contact_force":2.33731,"subtask_id":"reach_object","tcp_end":[0.50389,-0.0187,0.29589],"tcp_start":[0.50627,-0.01874,0.22142],"tcp_to_object_dist_end":0.16236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.53002,0.01965,0.01602],"object_pos_start":[0.51732,-0.01863,0.27528],"object_to_goal_dist_end":0.29392,"object_to_goal_dist_start":0.27196,"object_z_max":0.27542,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1679.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.6032,0.21313,0.34585],"tcp_start":[0.50389,-0.0187,0.29589],"tcp_to_object_dist_end":0.38934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.53002,0.01965,0.01602],"object_pos_start":[0.53002,0.01965,0.01602],"object_to_goal_dist_end":0.29392,"object_to_goal_dist_start":0.29392,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60658,0.22372,0.22654],"tcp_start":[0.6032,0.21313,0.34585],"tcp_to_object_dist_end":0.30303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53002,0.01965,0.01602],"object_pos_start":[0.53002,0.01965,0.01602],"object_to_goal_dist_end":0.29392,"object_to_goal_dist_start":0.29392,"object_z_max":0.01602,"peak_contact_force":81.14227,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.60181,0.22167,0.24466],"tcp_start":[0.60658,0.22372,0.22654],"tcp_to_object_dist_end":0.31344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41587,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.05451,"approach_object.approach_arc_height":0.05617,"approach_object.approach_speed":0.05901,"descend_to_grasp.descend_speed":0.07992,"lift.lift_height":0.07113,"lift.lift_speed":0.07367,"pull_up.pull_up_speed":0.02351,"release_object.release_timeout":0.48587},"optimized_scores":{"best_composite_score":-0.00501,"best_fitness_score":0.57499,"best_task_score":0.1965},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2310.0,"contact_point_centroid":[0.54278,0.00502,-0.00253],"force_p95":0.15068,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76758,"mean_force":0.14492,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58245,0.08938,0.27984]},{"body_a":"world","body_b":"grasp_target","contact_count":313.0,"contact_point_centroid":[0.53876,-0.02482,-0.00138],"force_p95":0.34782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48877,"mean_force":0.11376,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52874,-0.0264,0.03081]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54573,-0.02875,-0.00225],"force_p95":0.19653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27754,"mean_force":0.14185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53262,-0.02652,0.03037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12348.0,"contact_point_centroid":[0.5259,-0.00711,0.05254],"force_p95":0.0851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26184,"mean_force":0.05934,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52475,-0.02627,0.04984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14628.0,"contact_point_centroid":[0.52575,-0.04526,0.05071],"force_p95":0.0787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25825,"mean_force":0.05237,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.52493,-0.02628,0.04881]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.52195,0.00357,0.22559],"force_p95":0.21521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24743,"mean_force":0.1533,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51666,-0.01451,0.22957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7809.0,"contact_point_centroid":[0.51861,-0.04474,0.13929],"force_p95":0.11395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24321,"mean_force":0.07064,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51535,-0.02596,0.13843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7321.0,"contact_point_centroid":[0.51862,-0.00712,0.13897],"force_p95":0.11923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23125,"mean_force":0.07402,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51539,-0.02596,0.13775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":887.0,"contact_point_centroid":[0.52229,-0.02981,0.22561],"force_p95":0.16253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19095,"mean_force":0.1116,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51783,-0.01241,0.23031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3577.0,"contact_point_centroid":[0.53317,-0.00729,0.03208],"force_p95":0.09185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16174,"mean_force":0.0579,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53139,-0.02648,0.02894]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52007,0.02151,0.23613]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53898,-0.01824,0.10931]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54272,0.00507,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62607,0.15759,0.25609]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54272,0.00507,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62397,0.16055,0.19407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.53258,-0.04572,0.03085],"force_p95":0.08085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08677,"mean_force":0.04647,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5314,-0.02648,0.02895]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2286.0,"contact_point_centroid":[0.58619,0.09431,0.2847],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01595,"mean_force":0.01052,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58566,0.09431,0.28237]}],"total_contact_groups":18},"final_pose_error":0.01943,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54272,0.00507,0.01602],"final_tcp_position":[0.62829,0.16177,0.19555],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.76758,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.54008,-0.01011,0.17846],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.18008,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10292.0,"raw_peak_contact_force":0.27754,"subtask_id":"reach_object","tcp_end":[0.54023,-0.02665,0.03937],"tcp_start":[0.54008,-0.01011,0.17846],"tcp_to_object_dist_end":0.01463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02667,0.02518],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25954,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.08228,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":27289.0,"raw_peak_contact_force":0.48877,"tcp_end":[0.53136,-0.02648,0.02891],"tcp_start":[0.54023,-0.02665,0.03937],"tcp_to_object_dist_end":0.01465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":735.0,"n_steps_budget":810.0,"object_pos_end":[0.53936,-0.02636,0.04307],"object_pos_start":[0.54552,-0.02667,0.02518],"object_to_goal_dist_end":0.25149,"object_to_goal_dist_start":0.25954,"object_z_max":0.06086,"peak_contact_force":0.16332,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":15130.0,"raw_peak_contact_force":0.24321,"tcp_end":[0.52164,-0.02617,0.07149],"tcp_start":[0.52639,-0.02632,0.05027],"tcp_to_object_dist_end":0.03349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":534.0,"n_steps_budget":630.0,"object_pos_end":[0.53022,-0.02602,0.11099],"object_pos_start":[0.53253,-0.02628,0.0609],"object_to_goal_dist_end":0.22659,"object_to_goal_dist_start":0.24512,"object_z_max":0.20711,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6059.0,"raw_peak_contact_force":1.76758,"subtask_id":"reach_object","tcp_end":[0.51069,-0.0258,0.22644],"tcp_start":[0.51385,-0.02591,0.1749],"tcp_to_object_dist_end":0.1171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":777.0,"n_steps_budget":1000.0,"object_pos_end":[0.54272,0.00507,0.01602],"object_pos_start":[0.52551,-0.02561,0.20733],"object_to_goal_dist_end":0.24406,"object_to_goal_dist_start":0.22079,"object_z_max":0.21056,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62449,0.15385,0.31271],"tcp_start":[0.51069,-0.0258,0.22644],"tcp_to_object_dist_end":0.34182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.54272,0.00507,0.01602],"object_pos_start":[0.54272,0.00507,0.01602],"object_to_goal_dist_end":0.24406,"object_to_goal_dist_start":0.24406,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62829,0.16177,0.19555],"tcp_start":[0.62449,0.15385,0.31271],"tcp_to_object_dist_end":0.25319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54272,0.00507,0.01602],"object_pos_start":[0.54272,0.00507,0.01602],"object_to_goal_dist_end":0.24406,"object_to_goal_dist_start":0.24406,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62257,0.16007,0.21345],"tcp_start":[0.62829,0.16177,0.19555],"tcp_to_object_dist_end":0.2634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60174,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.14335,"approach_object.approach_arc_height":0.10512,"approach_object.approach_speed":0.07554,"descend_to_grasp.descend_speed":0.06792,"lift.lift_height":0.16195,"lift.lift_speed":0.0336,"pull_up.pull_up_speed":0.04698,"release_object.release_timeout":0.59513},"optimized_scores":{"best_composite_score":0.01195,"best_fitness_score":0.59195,"best_task_score":0.22713},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1087.0,"contact_point_centroid":[0.46783,0.01523,-0.00346],"force_p95":0.72786,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56987,"mean_force":0.20446,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43799,0.00131,0.44797]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.45794,0.00231,-0.00129],"force_p95":0.44989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52066,"mean_force":0.116,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.44974,0.00147,0.03435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13939.0,"contact_point_centroid":[0.44032,0.02044,0.1859],"force_p95":0.09727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34808,"mean_force":0.05675,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43927,0.00136,0.18408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14361.0,"contact_point_centroid":[0.44038,-0.01766,0.18798],"force_p95":0.09429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30899,"mean_force":0.05562,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43923,0.00136,0.18632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8622.0,"contact_point_centroid":[0.44577,0.02059,0.05462],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24404,"mean_force":0.04941,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.44598,0.00143,0.05302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8358.0,"contact_point_centroid":[0.44605,-0.01776,0.05508],"force_p95":0.07603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24324,"mean_force":0.05117,"phase_index":3.0,"phase_name":"pull_up","phase_type":"pull","tcp_position_centroid":[0.44593,0.00143,0.05327]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4629,0.00014,-0.00215],"force_p95":0.16374,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24073,"mean_force":0.13361,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45239,0.0015,0.03377]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.46286,-7e-05,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48354,0.02319,0.24919]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46104,0.00865,0.11611]},{"body_a":"world","body_b":"grasp_target","contact_count":2428.0,"contact_point_centroid":[0.46831,0.01855,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51637,0.07035,0.39076]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.46831,0.01855,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59948,0.14549,0.21137]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46831,0.01855,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59897,0.14855,0.14036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4794.0,"contact_point_centroid":[0.45127,0.02074,0.03495],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12202,"mean_force":0.04501,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45132,0.00149,0.03275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5513.0,"contact_point_centroid":[0.45078,-0.01779,0.03438],"force_p95":0.06792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07565,"mean_force":0.04094,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45132,0.00149,0.03275]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1242.0,"contact_point_centroid":[0.43828,0.00132,0.44805],"force_p95":0.01259,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01652,"mean_force":0.01077,"phase_index":4.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43797,0.00131,0.44571]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2576.0,"contact_point_centroid":[0.51668,0.07023,0.39319],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.0105,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51623,0.07022,0.39096]}],"total_contact_groups":18},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.46831,0.01855,0.01602],"final_tcp_position":[0.60414,0.1499,0.14095],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.76305,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46518,0.01558,0.1917],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.15727,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12107.0,"raw_peak_contact_force":0.24073,"subtask_id":"reach_object","tcp_end":[0.45906,0.00165,0.04032],"tcp_start":[0.46518,0.01558,0.1917],"tcp_to_object_dist_end":0.01489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,0.00126,0.0255],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23249,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.07472,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17153.0,"raw_peak_contact_force":0.52066,"tcp_end":[0.45129,0.00149,0.03272],"tcp_start":[0.45906,0.00165,0.04032],"tcp_to_object_dist_end":0.01357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":412.0,"n_steps_budget":600.0,"object_pos_end":[0.4578,0.00117,0.04567],"object_pos_start":[0.46277,0.00126,0.0255],"object_to_goal_dist_end":0.22821,"object_to_goal_dist_start":0.23249,"object_z_max":0.06487,"peak_contact_force":0.12263,"phase_name":"pull_up","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":30629.0,"raw_peak_contact_force":2.56987,"tcp_end":[0.44293,0.0014,0.07472],"tcp_start":[0.44704,0.00144,0.05375],"tcp_to_object_dist_end":0.03263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1237.0,"n_steps_budget":1000.0,"object_pos_end":[0.44702,0.00131,0.20463],"object_pos_start":[0.45262,0.00127,0.06495],"object_to_goal_dist_end":0.23744,"object_to_goal_dist_start":0.226,"object_z_max":0.31709,"peak_contact_force":9748.76305,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5004.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.43851,0.00131,0.50104],"tcp_start":[0.43847,0.00135,0.35909],"tcp_to_object_dist_end":0.29654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.46831,0.01855,0.01602],"object_pos_start":[0.46831,0.01855,0.01602],"object_to_goal_dist_end":0.22233,"object_to_goal_dist_start":0.22233,"object_z_max":0.01602,"peak_contact_force":9748.69674,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1997.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59621,0.14159,0.28046],"tcp_start":[0.43851,0.00131,0.50104],"tcp_to_object_dist_end":0.31848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.46831,0.01855,0.01602],"object_pos_start":[0.46831,0.01855,0.01602],"object_to_goal_dist_end":0.22233,"object_to_goal_dist_start":0.22233,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60414,0.1499,0.14095],"tcp_start":[0.59621,0.14159,0.28046],"tcp_to_object_dist_end":0.22652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46831,0.01855,0.01602],"object_pos_start":[0.46831,0.01855,0.01602],"object_to_goal_dist_end":0.22233,"object_to_goal_dist_start":0.22233,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":988.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59723,0.14803,0.16016],"tcp_start":[0.60414,0.1499,0.14095],"tcp_to_object_dist_end":0.23273,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```