## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 15 | -0.2407 | 0.38 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0853 | 0.36 | ✅ accepted |
| 2 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3630 | 0.36 | ✅ accepted |
| 1 | approach → descend → grasp → lift → push → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0495 | 0.27 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | 4 | 0.3628 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.241) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.15
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_descent
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.25
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.2
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
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
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object_approach
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_object_approach
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    transport_arc:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed_place:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: generator.speed
        mode: replace
    place_height:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_descent
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed_place: status=consumed; consumers=generator.speed (replace)
    - place_height: status=consumed; consumers=target.offset.z (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.241
- **task_score** (E): 0.379
- **fitness_score**: 0.659  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.900

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1341 |
| descend_1 | 1.00 | 1.00 | 0.1279 |
| grasp_1 | 1.00 | 1.00 | 0.0130 |
| lift_1 | 1.00 | 1.00 | 0.1836 |
| transport_1 | 1.00 | 1.00 | 0.2183 |
| descend_to_place | 1.00 | 0.67 | 0.0994 |
| release_1 | 1.00 | 1.00 | 0.0194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.005, 0.176) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.514, -0.005, 0.176)→(0.511, -0.014, 0.049) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.511, -0.014, 0.049)→(0.502, -0.014, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.015, 0.025) | 0.270→0.269 | 1.00 / 40.667 | 0.189 | 0.229 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.014, 0.039)→(0.511, -0.015, 0.222) | (0.515, -0.015, 0.025)→(0.520, -0.015, 0.204) | 0.269→0.230 | 1.00 / 38.667 | 0.077 | 0.464 |
| transport_1 | approach | 1.00 / step_budget | (0.511, -0.015, 0.222)→(0.598, 0.146, 0.331) | (0.520, -0.015, 0.204)→(0.613, 0.146, 0.309) | 0.230→0.146 | 1.00 / 24.000 | 0.133 | 0.167 |
| descend_to_place | descend | 1.00 / step_budget | (0.598, 0.146, 0.331)→(0.611, 0.173, 0.236) | (0.613, 0.146, 0.309)→(0.627, 0.167, 0.149) | 0.146→0.074 | 0.67 / 13.333 | 0.107 | 0.464 |
| release_1 | release | 1.00 / step_budget | (0.611, 0.173, 0.236)→(0.607, 0.171, 0.255) | (0.627, 0.167, 0.149)→(0.619, 0.161, 0.020) | 0.074→0.151 | 1.00 / 3.333 | 0.128 | 1.916 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.524
- phase_score: 0.350
- phase_breakdown.lift_clearance_score: 0.839
- phase_breakdown.reach_object_approach_score: 0.217
- phase_breakdown.approach_goal_score: 0.257
- phase_breakdown.place_descent_score: 0.517
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.724

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.724
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.524
- **Median Q (composite search score)**: -0.256
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20188,"average_solve_count":426.0,"average_success_count":426.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15504,"approach_1.arc_height":0.0809,"approach_1.speed":0.06216,"descend_1.descend_height":0.00067,"descend_1.descend_speed":0.03916,"descend_1.descend_tolerance":0.02383,"descend_to_place.descend_speed_place":0.03141,"descend_to_place.place_height":0.05867,"descend_to_place.place_tolerance":0.02052,"lift_1.lift_height":0.21222,"lift_1.lift_speed":0.019,"transport_1.transport_arc":0.10117,"transport_1.transport_height":0.12166,"transport_1.transport_speed":0.04083,"transport_1.transport_tolerance":0.06126},"optimized_scores":{"best_composite_score":-0.2903,"best_fitness_score":0.6097,"best_task_score":0.27393},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":751.0,"contact_point_centroid":[0.62698,0.19886,-0.00411],"force_p95":0.92771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.21544,"mean_force":0.20894,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60204,0.21386,0.27927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":369.0,"contact_point_centroid":[0.60406,0.20695,0.33651],"force_p95":0.30773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52947,"mean_force":0.1448,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59759,0.18802,0.33765]},{"body_a":"world","body_b":"grasp_target","contact_count":105.0,"contact_point_centroid":[0.53326,-0.01786,-0.00171],"force_p95":0.43082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45896,"mean_force":0.16697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52168,-0.01831,0.03621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":601.0,"contact_point_centroid":[0.60451,0.17149,0.33389],"force_p95":0.17413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34588,"mean_force":0.09526,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5979,0.18903,0.3351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12418.0,"contact_point_centroid":[0.52625,0.00069,0.12711],"force_p95":0.08459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28453,"mean_force":0.05643,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52571,-0.01847,0.12448]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53715,-0.02091,-0.00226],"force_p95":0.19799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27108,"mean_force":0.14198,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52404,-0.01834,0.03647]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13758.0,"contact_point_centroid":[0.52597,-0.03751,0.1244],"force_p95":0.0799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26871,"mean_force":0.05269,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52554,-0.01846,0.12232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4612.0,"contact_point_centroid":[0.55366,0.05803,0.30834],"force_p95":0.11097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16933,"mean_force":0.06974,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55113,0.03897,0.30614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3592.0,"contact_point_centroid":[0.5246,0.00088,0.03823],"force_p95":0.0921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16293,"mean_force":0.05783,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52283,-0.01832,0.0351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5678.0,"contact_point_centroid":[0.55395,0.02218,0.3084],"force_p95":0.0944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14324,"mean_force":0.05998,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55177,0.04097,0.30713]},{"body_a":"world","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51474,0.01979,0.24291]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53021,-0.01032,0.11798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.52404,-0.03756,0.03699],"force_p95":0.08129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08669,"mean_force":0.04623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52285,-0.01832,0.03512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.60345,0.21439,0.27552],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60311,0.21437,0.27345]}],"total_contact_groups":14},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62701,0.19917,0.01602],"final_tcp_position":[0.60503,0.21478,0.27999],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.21544,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.53079,-0.00268,0.18734],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.53172,-0.01836,0.04559],"tcp_start":[0.53079,-0.00268,0.18734],"tcp_to_object_dist_end":0.02049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53699,-0.01878,0.02514],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31525,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1825,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10316.0,"raw_peak_contact_force":0.27108,"tcp_end":[0.52281,-0.01832,0.03507],"tcp_start":[0.53172,-0.01836,0.04559],"tcp_to_object_dist_end":0.01732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.54225,-0.01884,0.20242],"object_pos_start":[0.53699,-0.01878,0.02514],"object_to_goal_dist_end":0.25586,"object_to_goal_dist_start":0.31525,"object_z_max":0.20217,"peak_contact_force":0.07947,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26281.0,"raw_peak_contact_force":0.45896,"subtask_id":"lift_clearance","tcp_end":[0.53283,-0.01869,0.2178],"tcp_start":[0.52281,-0.01832,0.03507],"tcp_to_object_dist_end":0.01803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.6144,0.18338,0.32922],"object_pos_start":[0.54225,-0.01884,0.20242],"object_to_goal_dist_end":0.1297,"object_to_goal_dist_start":0.25586,"object_z_max":0.34765,"peak_contact_force":0.14396,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10290.0,"raw_peak_contact_force":0.16933,"subtask_id":"approach_goal","tcp_end":[0.59763,0.18333,0.34771],"tcp_start":[0.53283,-0.01869,0.2178],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":143.0,"n_steps_budget":1000.0,"object_pos_end":[0.63061,0.1975,0.07018],"object_pos_start":[0.6144,0.18338,0.32922],"object_to_goal_dist_end":0.14198,"object_to_goal_dist_start":0.1297,"object_z_max":0.32922,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":970.0,"raw_peak_contact_force":0.52947,"subtask_id":"place_descent","tcp_end":[0.60503,0.21478,0.27999],"tcp_start":[0.59763,0.18333,0.34771],"tcp_to_object_dist_end":0.21207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62701,0.19917,0.01602],"object_pos_start":[0.63061,0.1975,0.07018],"object_to_goal_dist_end":0.19423,"object_to_goal_dist_start":0.14198,"object_z_max":0.07018,"peak_contact_force":0.12268,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":755.0,"raw_peak_contact_force":2.21544,"subtask_id":"place_goal","tcp_end":[0.60139,0.21345,0.29865],"tcp_start":[0.60503,0.21478,0.27999],"tcp_to_object_dist_end":0.28415,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12761,"average_solve_count":431.0,"average_success_count":431.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15969,"approach_1.arc_height":0.09785,"approach_1.speed":0.06321,"descend_1.descend_height":0.00114,"descend_1.descend_speed":0.03828,"descend_1.descend_tolerance":0.03863,"descend_to_place.descend_speed_place":0.0288,"descend_to_place.place_height":0.05085,"descend_to_place.place_tolerance":0.02316,"lift_1.lift_height":0.25569,"lift_1.lift_speed":0.03455,"transport_1.transport_arc":0.10778,"transport_1.transport_height":0.10733,"transport_1.transport_speed":0.04246,"transport_1.transport_tolerance":0.0315},"optimized_scores":{"best_composite_score":-0.25631,"best_fitness_score":0.64369,"best_task_score":0.33867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.63141,0.13794,-0.006],"force_p95":1.07903,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16906,"mean_force":0.28002,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62253,0.15526,0.2513]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.54181,-0.02915,-0.00142],"force_p95":0.46598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49466,"mean_force":0.1784,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53158,-0.02932,0.03678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":115.0,"contact_point_centroid":[0.63191,0.17466,0.23619],"force_p95":0.27134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40156,"mean_force":0.19918,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6261,0.1566,0.24161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1313.0,"contact_point_centroid":[0.62858,0.16367,0.28613],"force_p95":0.18308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35086,"mean_force":0.11457,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62256,0.14497,0.28707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1663.0,"contact_point_centroid":[0.62887,0.12732,0.28493],"force_p95":0.14842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29713,"mean_force":0.09062,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62272,0.14535,0.28562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17358.0,"contact_point_centroid":[0.53513,-0.01011,0.15077],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26835,"mean_force":0.05072,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53522,-0.02926,0.14882]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17500.0,"contact_point_centroid":[0.53499,-0.04841,0.1491],"force_p95":0.0736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2667,"mean_force":0.05055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53513,-0.02926,0.14735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":266.0,"contact_point_centroid":[0.6318,0.13981,0.23741],"force_p95":0.1889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2267,"mean_force":0.09555,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62591,0.15654,0.24111]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3819.0,"contact_point_centroid":[0.56872,0.04019,0.32714],"force_p95":0.11676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19032,"mean_force":0.07052,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56615,0.02114,0.32491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4730.0,"contact_point_centroid":[0.569,0.00377,0.32631],"force_p95":0.09814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16456,"mean_force":0.0604,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56683,0.02259,0.32511]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54559,-0.02933,-0.00202],"force_p95":0.13004,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14265,"mean_force":0.12505,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53387,-0.02939,0.03725]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.5456,-0.02923,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53317,-0.02234,0.26638]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54446,-0.03152,0.12895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4166.0,"contact_point_centroid":[0.53313,-0.04856,0.03847],"force_p95":0.07559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09998,"mean_force":0.05145,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53266,-0.02935,0.03583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.53317,-0.01028,0.03778],"force_p95":0.06766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09153,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53266,-0.02935,0.03583]}],"total_contact_groups":15},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63102,0.13822,0.01673],"final_tcp_position":[0.62712,0.15645,0.24489],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":2.16906,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.54909,-0.0334,0.20874],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.54168,-0.02967,0.04676],"tcp_start":[0.54909,-0.0334,0.20874],"tcp_to_object_dist_end":0.02111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02942,0.02589],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26118,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13117,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10790.0,"raw_peak_contact_force":0.14265,"tcp_end":[0.53262,-0.02936,0.03579],"tcp_start":[0.54168,-0.02967,0.04676],"tcp_to_object_dist_end":0.01623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.55027,-0.02926,0.24613],"object_pos_start":[0.54548,-0.02942,0.02589],"object_to_goal_dist_end":0.22207,"object_to_goal_dist_start":0.26118,"object_z_max":0.24588,"peak_contact_force":0.06885,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34951.0,"raw_peak_contact_force":0.49466,"subtask_id":"lift_clearance","tcp_end":[0.54203,-0.02932,0.26209],"tcp_start":[0.53262,-0.02936,0.03579],"tcp_to_object_dist_end":0.01796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.63602,0.13664,0.30426],"object_pos_start":[0.55027,-0.02926,0.24613],"object_to_goal_dist_end":0.13048,"object_to_goal_dist_start":0.22207,"object_z_max":0.34842,"peak_contact_force":0.15163,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8549.0,"raw_peak_contact_force":0.19032,"subtask_id":"approach_goal","tcp_end":[0.62046,0.13644,0.32336],"tcp_start":[0.54203,-0.02932,0.26209],"tcp_to_object_dist_end":0.02464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.6385,0.15662,0.22075],"object_pos_start":[0.63602,0.13664,0.30426],"object_to_goal_dist_end":0.04497,"object_to_goal_dist_start":0.13048,"object_z_max":0.30426,"peak_contact_force":0.22157,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2976.0,"raw_peak_contact_force":0.35086,"subtask_id":"place_descent","tcp_end":[0.62712,0.15645,0.24489],"tcp_start":[0.62046,0.13644,0.32336],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63102,0.13822,0.01673],"object_pos_start":[0.6385,0.15662,0.22075],"object_to_goal_dist_end":0.16241,"object_to_goal_dist_start":0.04497,"object_z_max":0.22075,"peak_contact_force":0.11726,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":705.0,"raw_peak_contact_force":2.16906,"subtask_id":"place_goal","tcp_end":[0.6225,0.15525,0.26313],"tcp_start":[0.62712,0.15645,0.24489],"tcp_to_object_dist_end":0.24713,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11392,"average_solve_count":395.0,"average_success_count":395.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09915,"approach_1.arc_height":0.09608,"approach_1.speed":0.0625,"descend_1.descend_height":0.00929,"descend_1.descend_speed":0.03126,"descend_1.descend_tolerance":0.02128,"descend_to_place.descend_speed_place":0.03486,"descend_to_place.place_height":0.04459,"descend_to_place.place_tolerance":0.02296,"lift_1.lift_height":0.18154,"lift_1.lift_speed":0.05575,"transport_1.transport_arc":0.04391,"transport_1.transport_height":0.21198,"transport_1.transport_speed":0.03445,"transport_1.transport_tolerance":0.06567},"optimized_scores":{"best_composite_score":-0.17551,"best_fitness_score":0.72449,"best_task_score":0.52413},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.59938,0.14513,-0.00987],"force_p95":1.27534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36316,"mean_force":0.57107,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5957,0.14488,0.19345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3337.0,"contact_point_centroid":[0.59404,0.15105,0.25137],"force_p95":0.111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51061,"mean_force":0.08295,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58876,0.13232,0.25128]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3458.0,"contact_point_centroid":[0.59375,0.11348,0.25337],"force_p95":0.11424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49024,"mean_force":0.07982,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58856,0.13209,0.25252]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.46064,0.00473,-0.00172],"force_p95":0.35636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4388,"mean_force":0.11392,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45002,0.00426,0.04782]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":831.0,"contact_point_centroid":[0.60459,0.12729,0.17901],"force_p95":0.10568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40567,"mean_force":0.06788,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59938,0.14604,0.17835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":834.0,"contact_point_centroid":[0.60449,0.16494,0.1783],"force_p95":0.10692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38278,"mean_force":0.06749,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59936,0.14603,0.17832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9664.0,"contact_point_centroid":[0.45315,-0.01544,0.11417],"force_p95":0.08902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27885,"mean_force":0.05447,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45295,0.00361,0.11269]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46299,0.00017,-0.00234],"force_p95":0.26824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27441,"mean_force":0.17852,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45203,0.00432,0.04709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8240.0,"contact_point_centroid":[0.45361,0.02278,0.11547],"force_p95":0.08694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26372,"mean_force":0.06065,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45306,0.00359,0.11442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.45166,0.02356,0.04739],"force_p95":0.09215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17535,"mean_force":0.06185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45098,0.00431,0.04608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4985.0,"contact_point_centroid":[0.50342,0.02713,0.2595],"force_p95":0.08505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14004,"mean_force":0.05353,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50262,0.04614,0.25853]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.46286,-7e-05,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48128,0.05013,0.2208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4450.0,"contact_point_centroid":[0.50366,0.06519,0.25898],"force_p95":0.08895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13476,"mean_force":0.05742,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50255,0.04607,0.25854]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45912,0.0124,0.09454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5683.0,"contact_point_centroid":[0.45178,-0.01505,0.04841],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09577,"mean_force":0.04721,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45099,0.00431,0.04609]}],"total_contact_groups":15},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.59823,0.14437,0.0264],"final_tcp_position":[0.60163,0.14641,0.18343],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.36316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object_approach","tcp_end":[0.46086,0.01962,0.13147],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":684.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object_approach","tcp_end":[0.45874,0.00456,0.05392],"tcp_start":[0.46086,0.01962,0.13147],"tcp_to_object_dist_end":0.02858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46291,0.00283,0.02481],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23168,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.25443,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11560.0,"raw_peak_contact_force":0.27441,"tcp_end":[0.45095,0.00431,0.04605],"tcp_start":[0.45874,0.00456,0.05392],"tcp_to_object_dist_end":0.02443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.46652,0.00195,0.162],"object_pos_start":[0.46291,0.00283,0.02481],"object_to_goal_dist_end":0.21211,"object_to_goal_dist_start":0.23168,"object_z_max":0.16172,"peak_contact_force":0.08292,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17996.0,"raw_peak_contact_force":0.4388,"subtask_id":"lift_clearance","tcp_end":[0.45861,0.00292,0.18708],"tcp_start":[0.45095,0.00431,0.04605],"tcp_to_object_dist_end":0.02632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.58733,0.11737,0.29472],"object_pos_start":[0.46652,0.00195,0.162],"object_to_goal_dist_end":0.17761,"object_to_goal_dist_start":0.21211,"object_z_max":0.29455,"peak_contact_force":0.10401,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9435.0,"raw_peak_contact_force":0.14004,"subtask_id":"approach_goal","tcp_end":[0.57712,0.1186,0.32056],"tcp_start":[0.45861,0.00292,0.18708],"tcp_to_object_dist_end":0.02782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.61102,0.14552,0.15541],"object_pos_start":[0.58733,0.11737,0.29472],"object_to_goal_dist_end":0.03404,"object_to_goal_dist_start":0.17761,"object_z_max":0.29477,"peak_contact_force":0.09953,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6795.0,"raw_peak_contact_force":0.51061,"subtask_id":"place_descent","tcp_end":[0.60163,0.14641,0.18343],"tcp_start":[0.57712,0.1186,0.32056],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59823,0.14437,0.0264],"object_pos_start":[0.61102,0.14552,0.15541],"object_to_goal_dist_end":0.0969,"object_to_goal_dist_start":0.03404,"object_z_max":0.15541,"peak_contact_force":0.14334,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1791.0,"raw_peak_contact_force":1.36316,"subtask_id":"place_goal","tcp_end":[0.59564,0.14487,0.20291],"tcp_start":[0.60163,0.14641,0.18343],"tcp_to_object_dist_end":0.17653,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```