## Search State

- **Seed**: 9
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.1646 | 0.13 | ✅ accepted |
| 3 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.1650 | 0.13 | ❌ rejected |
| 2 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.1646 | 0.13 | ✅ accepted |
| 1 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.1649 | 0.13 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6  | -0.0199 | 0.38 | ✅ accepted |

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

## Current Skill (Q=-0.020) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal_pre_place
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: place
  weight: 0.4
phases:
- id: approach_above
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_timeout
    when: before_phase
    predicate: force_below
    threshold: 10.0
    on_failure: abort
  subtask_id: reach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_ok
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: bilateral
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
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
- id: transport_to_goal
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal_pre_place
- id: descend_to_goal
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place
- id: release
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
    - 0.0
  parameters:
    open_duration:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract
  type: retract
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_timeout, when=before_phase, predicate=force_below, on_failure=abort, threshold=10.0
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_ok, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - open_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.020
- **task_score** (E): 0.377
- **fitness_score**: 0.660  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1574 |
| descend_to_grasp | 1.00 | 1.00 | 0.1058 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1723 |
| transport_to_goal | 1.00 | 1.00 | 0.2235 |
| descend_to_goal | 1.00 | 1.00 | 0.0748 |
| release | 1.00 | 1.00 | 0.0200 |
| retract | 1.00 | 1.00 | 0.1314 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.148) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.015, 0.148)→(0.509, -0.016, 0.042) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.042)→(0.501, -0.016, 0.033) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.141 | 0.188 |
| lift | lift | 1.00 / step_budget | (0.501, -0.016, 0.033)→(0.498, -0.016, 0.206) | (0.515, -0.016, 0.026)→(0.508, -0.016, 0.193) | 0.270→0.233 | 1.00 / 37.000 | 0.080 | 0.529 |
| transport_to_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.206)→(0.607, 0.167, 0.256) | (0.508, -0.016, 0.193)→(0.618, 0.167, 0.235) | 0.233→0.068 | 1.00 / 27.000 | 0.135 | 0.135 |
| descend_to_goal | descend | 1.00 / step_budget | (0.607, 0.167, 0.256)→(0.612, 0.177, 0.182) | (0.618, 0.167, 0.235)→(0.622, 0.177, 0.160) | 0.068→0.013 | 1.00 / 26.000 | 0.108 | 0.431 |
| release | release | 1.00 / step_budget | (0.612, 0.177, 0.182)→(0.606, 0.175, 0.201) | (0.622, 0.177, 0.160)→(0.616, 0.175, 0.016) | 0.013→0.154 | 1.00 / 3.667 | 0.169 | 1.645 |
| retract | retract | 1.00 / step_budget | (0.606, 0.175, 0.201)→(0.604, 0.175, 0.332) | (0.616, 0.175, 0.016)→(0.612, 0.177, 0.019) | 0.154→0.150 | 1.00 / 4.000 | 0.123 | 0.182 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.492
- phase_score: 0.700
- phase_breakdown.reach_pre_grasp_score: 0.672
- phase_breakdown.reach_goal_pre_place_score: 0.672
- phase_breakdown.place_score: 0.741
- grasp_place_fitness: 0.726

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.726
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.492
- **Median Q (composite search score)**: -0.040
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02928,"average_solve_count":444.0,"average_success_count":444.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.03917,"descend_to_goal.speed":0.06617,"descend_to_grasp.speed":0.06326,"lift.lift_height":0.19845,"lift.speed":0.03892,"release.open_duration":0.34215,"retract.retract_height":0.19715,"retract.speed":0.05598,"transport_to_goal.arc_height":0.24959,"transport_to_goal.speed":0.04647},"optimized_scores":{"best_composite_score":-0.06576,"best_fitness_score":0.61424,"best_task_score":0.2959},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.59628,0.22154,-0.01002],"force_p95":1.47214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82522,"mean_force":0.57571,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60073,0.22019,0.23287]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2111.0,"contact_point_centroid":[0.60819,0.23492,0.25478],"force_p95":0.12786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47386,"mean_force":0.07996,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60342,0.21619,0.25449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2274.0,"contact_point_centroid":[0.60779,0.19729,0.25633],"force_p95":0.12838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42897,"mean_force":0.07679,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60336,0.216,0.25563]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53309,-0.02011,-0.0015],"force_p95":0.40131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41833,"mean_force":0.15719,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52062,-0.02029,0.0422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1018.0,"contact_point_centroid":[0.60748,0.20276,0.21516],"force_p95":0.09968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30457,"mean_force":0.066,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60368,0.2216,0.21496]},{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.5901,0.22202,-0.00206],"force_p95":0.145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29713,"mean_force":0.12327,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59928,0.2194,0.32855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1033.0,"contact_point_centroid":[0.60745,0.24048,0.2147],"force_p95":0.09577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2809,"mean_force":0.06394,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60368,0.2216,0.21495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11716.0,"contact_point_centroid":[0.51901,-0.00111,0.13352],"force_p95":0.08239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.271,"mean_force":0.05796,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51808,-0.02023,0.13111]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12520.0,"contact_point_centroid":[0.51898,-0.03927,0.12929],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26132,"mean_force":0.05528,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51808,-0.02023,0.12724]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02116,-0.00209],"force_p95":0.14817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20483,"mean_force":0.12945,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52301,-0.02033,0.04266]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4094.0,"contact_point_centroid":[0.52306,-0.0011,0.04394],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13856,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52179,-0.02031,0.04125]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51287,-0.00876,0.22529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16652.0,"contact_point_centroid":[0.55284,0.05086,0.29203],"force_p95":0.07983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13325,"mean_force":0.05402,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54995,0.0698,0.29056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15191.0,"contact_point_centroid":[0.5533,0.08876,0.29311],"force_p95":0.08503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12881,"mean_force":0.05885,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54992,0.06973,0.29131]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52808,-0.01965,0.08409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4946.0,"contact_point_centroid":[0.523,-0.03941,0.04302],"force_p95":0.0712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07473,"mean_force":0.04458,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52179,-0.02031,0.04126]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58959,0.22216,0.02602],"final_tcp_position":[0.60026,0.21968,0.41604],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.82522,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52844,-0.0183,0.14747],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52991,-0.02046,0.05073],"tcp_start":[0.52844,-0.0183,0.14747],"tcp_to_object_dist_end":0.02573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02043,0.02569],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31622,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14365,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10840.0,"raw_peak_contact_force":0.20483,"tcp_end":[0.52176,-0.02031,0.04122],"tcp_start":[0.52991,-0.02046,0.05073],"tcp_to_object_dist_end":0.02173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.52732,-0.02024,0.19912],"object_pos_start":[0.53696,-0.02043,0.02569],"object_to_goal_dist_end":0.26164,"object_to_goal_dist_start":0.31622,"object_z_max":0.19886,"peak_contact_force":0.08004,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24329.0,"raw_peak_contact_force":0.41833,"tcp_end":[0.51858,-0.02023,0.22006],"tcp_start":[0.52176,-0.02031,0.04122],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.61085,0.21024,0.26568],"object_pos_start":[0.52732,-0.02024,0.19912],"object_to_goal_dist_end":0.06084,"object_to_goal_dist_start":0.26164,"object_z_max":0.29824,"peak_contact_force":0.10071,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31843.0,"raw_peak_contact_force":0.13325,"subtask_id":"reach_goal_pre_place","tcp_end":[0.60236,0.21029,0.29178],"tcp_start":[0.51858,-0.02023,0.22006],"tcp_to_object_dist_end":0.02746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.61108,0.22149,0.19297],"object_pos_start":[0.61085,0.21024,0.26568],"object_to_goal_dist_end":0.01576,"object_to_goal_dist_start":0.06084,"object_z_max":0.26568,"peak_contact_force":0.10058,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4385.0,"raw_peak_contact_force":0.47386,"subtask_id":"place","tcp_end":[0.60562,0.2222,0.22009],"tcp_start":[0.60236,0.21029,0.29178],"tcp_to_object_dist_end":0.02768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60275,0.21698,0.01605],"object_pos_start":[0.61108,0.22149,0.19297],"object_to_goal_dist_end":0.19181,"object_to_goal_dist_start":0.01576,"object_z_max":0.19297,"peak_contact_force":0.30981,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2180.0,"raw_peak_contact_force":1.82522,"tcp_end":[0.60071,0.22018,0.23878],"tcp_start":[0.60562,0.2222,0.22009],"tcp_to_object_dist_end":0.22276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.58959,0.22216,0.02602],"object_pos_start":[0.60275,0.21698,0.01605],"object_to_goal_dist_end":0.18266,"object_to_goal_dist_start":0.19181,"object_z_max":0.02813,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3008.0,"raw_peak_contact_force":0.29713,"tcp_end":[0.60026,0.21968,0.41604],"tcp_start":[0.60071,0.22018,0.23878],"tcp_to_object_dist_end":0.39018,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02288,"average_solve_count":437.0,"average_success_count":437.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.03329,"descend_to_goal.speed":0.0581,"descend_to_grasp.speed":0.07929,"lift.lift_height":0.21855,"lift.speed":0.02419,"release.open_duration":0.3522,"retract.retract_height":0.13888,"retract.speed":0.04985,"transport_to_goal.arc_height":0.18559,"transport_to_goal.speed":0.04901},"optimized_scores":{"best_composite_score":-0.03993,"best_fitness_score":0.64007,"best_task_score":0.34168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":198.0,"contact_point_centroid":[0.63518,0.15996,-0.0068],"force_p95":1.28909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67945,"mean_force":0.38765,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62141,0.15872,0.20066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1650.0,"contact_point_centroid":[0.63019,0.17365,0.22982],"force_p95":0.13216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52142,"mean_force":0.0982,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62419,0.15493,0.22814]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.54153,-0.02768,-0.00154],"force_p95":0.42612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44171,"mean_force":0.17053,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5289,-0.02785,0.0388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.63061,0.13665,0.22892],"force_p95":0.12488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43258,"mean_force":0.08279,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.62422,0.15497,0.22785]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":749.0,"contact_point_centroid":[0.63108,0.17858,0.1847],"force_p95":0.1036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33583,"mean_force":0.06979,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62504,0.15991,0.18486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":649.0,"contact_point_centroid":[0.63065,0.14133,0.18539],"force_p95":0.11943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28587,"mean_force":0.07962,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62504,0.15991,0.18486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13153.0,"contact_point_centroid":[0.52744,-0.00865,0.14062],"force_p95":0.0829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26528,"mean_force":0.05751,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52641,-0.02776,0.13822]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14026.0,"contact_point_centroid":[0.52741,-0.0468,0.13593],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26346,"mean_force":0.05503,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5264,-0.02776,0.13392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54565,-0.02902,-0.00212],"force_p95":0.15692,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22161,"mean_force":0.13165,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53136,-0.02792,0.03933]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9493.0,"contact_point_centroid":[0.56584,0.05985,0.28308],"force_p95":0.10906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.152,"mean_force":0.07177,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56284,0.04092,0.28172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4080.0,"contact_point_centroid":[0.53149,-0.00867,0.04055],"force_p95":0.08024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14562,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53013,-0.02788,0.03787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11320.0,"contact_point_centroid":[0.56728,0.02472,0.28277],"force_p95":0.08957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14305,"mean_force":0.06176,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5642,0.04338,0.28219]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5164,-0.01202,0.22515]},{"body_a":"world","body_b":"grasp_target","contact_count":2120.0,"contact_point_centroid":[0.63865,0.16003,-0.00199],"force_p95":0.12358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12473,"mean_force":0.12128,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61918,0.15799,0.26695]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53596,-0.02693,0.08455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.5314,-0.04702,0.03963],"force_p95":0.07271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07904,"mean_force":0.04453,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53013,-0.02788,0.03788]}],"total_contact_groups":16},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63865,0.16003,0.01602],"final_tcp_position":[0.61973,0.15808,0.32746],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.67945,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53592,-0.02515,0.14691],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53844,-0.02814,0.04772],"tcp_start":[0.53592,-0.02515,0.14691],"tcp_to_object_dist_end":0.02288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54554,-0.02806,0.0256],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26032,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15062,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10864.0,"raw_peak_contact_force":0.22161,"tcp_end":[0.5301,-0.02788,0.03784],"tcp_start":[0.53844,-0.02814,0.04772],"tcp_to_object_dist_end":0.0197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.53608,-0.02781,0.21841],"object_pos_start":[0.54554,-0.02806,0.0256],"object_to_goal_dist_end":0.21962,"object_to_goal_dist_start":0.26032,"object_z_max":0.21815,"peak_contact_force":0.07957,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27275.0,"raw_peak_contact_force":0.44171,"tcp_end":[0.52707,-0.02778,0.23688],"tcp_start":[0.5301,-0.02788,0.03784],"tcp_to_object_dist_end":0.02055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.6321,0.15036,0.24123],"object_pos_start":[0.53608,-0.02781,0.21841],"object_to_goal_dist_end":0.06595,"object_to_goal_dist_start":0.21962,"object_z_max":0.28239,"peak_contact_force":0.11241,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20813.0,"raw_peak_contact_force":0.152,"subtask_id":"reach_goal_pre_place","tcp_end":[0.62293,0.15019,0.26528],"tcp_start":[0.52707,-0.02778,0.23688],"tcp_to_object_dist_end":0.02574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.63618,0.16053,0.16471],"object_pos_start":[0.6321,0.15036,0.24123],"object_to_goal_dist_end":0.0134,"object_to_goal_dist_start":0.06595,"object_z_max":0.24123,"peak_contact_force":0.12125,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3646.0,"raw_peak_contact_force":0.52142,"subtask_id":"place","tcp_end":[0.62716,0.16035,0.18988],"tcp_start":[0.62293,0.15019,0.26528],"tcp_to_object_dist_end":0.02674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63857,0.1599,0.01426],"object_pos_start":[0.63618,0.16053,0.16471],"object_to_goal_dist_end":0.16283,"object_to_goal_dist_start":0.0134,"object_z_max":0.16471,"peak_contact_force":0.09079,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1596.0,"raw_peak_contact_force":1.67945,"tcp_end":[0.62138,0.15871,0.20843],"tcp_start":[0.62716,0.16035,0.18988],"tcp_to_object_dist_end":0.19493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.63865,0.16003,0.01602],"object_pos_start":[0.63857,0.1599,0.01426],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.16283,"object_z_max":0.01651,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2120.0,"raw_peak_contact_force":0.12473,"tcp_end":[0.61973,0.15808,0.32746],"tcp_start":[0.62138,0.15871,0.20843],"tcp_to_object_dist_end":0.31203,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96543,"average_solve_count":376.0,"average_success_count":376.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05234,"descend_to_goal.speed":0.03487,"descend_to_grasp.speed":0.05055,"lift.lift_height":0.15864,"lift.speed":0.0507,"release.open_duration":0.39375,"retract.retract_height":0.11755,"retract.speed":0.05774,"transport_to_goal.arc_height":0.18544,"transport_to_goal.speed":0.04647},"optimized_scores":{"best_composite_score":0.04592,"best_fitness_score":0.72592,"best_task_score":0.49227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":281.0,"contact_point_centroid":[0.607,0.14788,-0.00505],"force_p95":0.81358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42896,"mean_force":0.25016,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59607,0.14729,0.14411]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.46039,-2e-05,-0.00137],"force_p95":0.62243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72683,"mean_force":0.18855,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44995,-0.00024,0.02235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2301.0,"contact_point_centroid":[0.60095,0.12591,0.17191],"force_p95":0.10517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29701,"mean_force":0.07692,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59815,0.14478,0.17266]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8184.0,"contact_point_centroid":[0.44777,0.01891,0.09253],"force_p95":0.07885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29281,"mean_force":0.05673,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44755,-0.00025,0.09012]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9066.0,"contact_point_centroid":[0.44766,-0.01929,0.08943],"force_p95":0.07621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27517,"mean_force":0.05194,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44756,-0.00025,0.08729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2636.0,"contact_point_centroid":[0.60121,0.16336,0.17418],"force_p95":0.09919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27355,"mean_force":0.06941,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59794,0.14458,0.1746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":837.0,"contact_point_centroid":[0.60306,0.16739,0.12815],"force_p95":0.11184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24198,"mean_force":0.06801,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60039,0.14853,0.13008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":829.0,"contact_point_centroid":[0.60329,0.12973,0.12834],"force_p95":0.11006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23547,"mean_force":0.06739,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60041,0.14854,0.13011]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.46286,-7e-05,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48272,-4e-05,0.22675]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13813,"mean_force":0.12421,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45209,-0.0002,0.02233]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.60786,0.14793,-0.00197],"force_p95":0.12377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12426,"mean_force":0.12234,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59309,0.14644,0.2028]},{"body_a":"world","body_b":"grasp_target","contact_count":3004.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46019,-0.00011,0.08611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13575.0,"contact_point_centroid":[0.50568,0.03608,0.21944],"force_p95":0.08664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11928,"mean_force":0.05791,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50396,0.055,0.2182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12389.0,"contact_point_centroid":[0.50896,0.077,0.22109],"force_p95":0.08894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10955,"mean_force":0.06262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50712,0.05796,0.21931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45099,0.01906,0.02365],"force_p95":0.07359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0939,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45099,-0.00022,0.02129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45087,-0.01929,0.02322],"force_p95":0.06454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08386,"mean_force":0.04269,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45099,-0.00022,0.02129]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60786,0.14793,0.01602],"final_tcp_position":[0.59324,0.14644,0.25255],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.42896,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46522,-8e-05,0.14972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3004.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45852,-0.00012,0.02842],"tcp_start":[0.46522,-8e-05,0.14972],"tcp_to_object_dist_end":0.00496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23322,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12825,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13813,"tcp_end":[0.45096,-0.00022,0.02126],"tcp_start":[0.45852,-0.00012,0.02842],"tcp_to_object_dist_end":0.01265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.46039,-0.00025,0.1608],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.21763,"object_to_goal_dist_start":0.23322,"object_z_max":0.16051,"peak_contact_force":0.08045,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17328.0,"raw_peak_contact_force":0.72683,"tcp_end":[0.44759,-0.00024,0.16024],"tcp_start":[0.45096,-0.00022,0.02126],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.61077,0.14121,0.19905],"object_pos_start":[0.46039,-0.00025,0.1608],"object_to_goal_dist_end":0.07774,"object_to_goal_dist_start":0.21763,"object_z_max":0.23794,"peak_contact_force":0.19084,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25964.0,"raw_peak_contact_force":0.11928,"subtask_id":"reach_goal_pre_place","tcp_end":[0.59576,0.14124,0.20952],"tcp_start":[0.44759,-0.00024,0.16024],"tcp_to_object_dist_end":0.0183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.61777,0.14917,0.12104],"object_pos_start":[0.61077,0.14121,0.19905],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.07774,"object_z_max":0.19905,"peak_contact_force":0.10203,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4937.0,"raw_peak_contact_force":0.29701,"subtask_id":"place","tcp_end":[0.60285,0.14908,0.1347],"tcp_start":[0.59576,0.14124,0.20952],"tcp_to_object_dist_end":0.02024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6079,0.14793,0.01634],"object_pos_start":[0.61777,0.14917,0.12104],"object_to_goal_dist_end":0.10598,"object_to_goal_dist_start":0.00855,"object_z_max":0.12104,"peak_contact_force":0.10541,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1947.0,"raw_peak_contact_force":1.42896,"tcp_end":[0.59598,0.14726,0.15456],"tcp_start":[0.60285,0.14908,0.1347],"tcp_to_object_dist_end":0.13873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.60786,0.14793,0.01602],"object_pos_start":[0.6079,0.14793,0.01634],"object_to_goal_dist_end":0.10631,"object_to_goal_dist_start":0.10598,"object_z_max":0.01648,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.12426,"tcp_end":[0.59324,0.14644,0.25255],"tcp_start":[0.59598,0.14726,0.15456],"tcp_to_object_dist_end":0.23699,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```