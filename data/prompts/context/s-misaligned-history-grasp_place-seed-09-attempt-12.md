## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | time_limit | time_limit | time_limit | 11  | 0.4055 | 0.92 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4497 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.4498 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.3674 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.1856 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.186) — your mutation base

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
    tolerance: 0.03
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
    tolerance: 0.04
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
    tolerance: 0.03
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
    tolerance: 0.025
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.03
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.025
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.186
- **task_score** (E): 0.196
- **fitness_score**: 0.484  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1475 |
| descend_to_grasp | 1.00 | 1.00 | 0.1139 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.0943 |
| transport_to_goal | 1.00 | 1.00 | 0.0975 |
| descend_to_goal | 1.00 | 1.00 | 0.0442 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.158) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 13.278 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.158)→(0.509, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.509, -0.016, 0.044)→(0.501, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.333 | 0.147 | 0.194 |
| lift | lift | 1.00 / time_limit | (0.501, -0.016, 0.035)→(0.497, -0.016, 0.129) | (0.515, -0.016, 0.026)→(0.506, -0.016, 0.108) | 0.270→0.242 | 1.00 / 22.667 | 0.121 | 0.530 |
| transport_to_goal | approach | 1.00 / time_limit | (0.497, -0.016, 0.129)→(0.521, 0.021, 0.214) | (0.506, -0.016, 0.108)→(0.519, 0.015, 0.016) | 0.242→0.253 | 1.00 / 8.000 | 0.123 | 1.556 |
| descend_to_goal | descend | 1.00 / time_limit | (0.521, 0.021, 0.214)→(0.539, 0.055, 0.196) | (0.519, 0.015, 0.016)→(0.519, 0.015, 0.016) | 0.253→0.253 | 1.00 / 8.000 | 3249.759 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.261
- phase_score: 0.203
- phase_breakdown.reach_pre_grasp_score: 0.555
- phase_breakdown.reach_goal_pre_place_score: 0.043
- phase_breakdown.place_score: 0.060
- grasp_place_fitness: 0.610

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.610
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.261
- **Median Q (composite search score)**: -0.143
- **K-run variance**: 0.0154
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40698,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.05371,"descend_to_goal.max_time":8.87641,"descend_to_goal.place_z_offset":-0.04079,"descend_to_goal.speed":0.01062,"descend_to_grasp.speed":0.07851,"lift.lift_height":0.19041,"lift.max_time":3.84696,"lift.speed":0.08256,"transport_to_goal.arc_height":0.21099,"transport_to_goal.max_time":7.23108,"transport_to_goal.speed":0.0651},"optimized_scores":{"best_composite_score":-0.14254,"best_fitness_score":0.52746,"best_task_score":0.11514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3290.0,"contact_point_centroid":[0.52665,-0.02042,-0.00228],"force_p95":0.12979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53232,"mean_force":0.13845,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51551,-0.01649,0.20183]},{"body_a":"world","body_b":"grasp_target","contact_count":270.0,"contact_point_centroid":[0.53368,-0.01963,-0.00133],"force_p95":0.23952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48445,"mean_force":0.08878,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51947,-0.02015,0.03884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12146.0,"contact_point_centroid":[0.52161,-0.00137,0.09115],"force_p95":0.12644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29995,"mean_force":0.08037,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51753,-0.0201,0.08951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13349.0,"contact_point_centroid":[0.52156,-0.03871,0.08998],"force_p95":0.11376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29326,"mean_force":0.07463,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51754,-0.0201,0.08893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":614.0,"contact_point_centroid":[0.52152,-0.00214,0.1615],"force_p95":0.20418,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24501,"mean_force":0.12566,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51591,-0.02021,0.16628]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02113,-0.0021],"force_p95":0.15185,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21616,"mean_force":0.13034,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52309,-0.02022,0.03902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.52105,-0.03794,0.16187],"force_p95":0.128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21516,"mean_force":0.09998,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51563,-0.02023,0.16661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4089.0,"contact_point_centroid":[0.52311,-0.00099,0.0403],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13906,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52186,-0.0202,0.03761]},{"body_a":"world","body_b":"grasp_target","contact_count":868.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13721,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51244,-0.00801,0.23169]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52752,-0.01908,0.08708]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52668,-0.02025,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.523,0.01064,0.2183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.52304,-0.03931,0.03939],"force_p95":0.07179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0789,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.0202,0.03762]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3272.0,"contact_point_centroid":[0.51594,-0.01621,0.20612],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51563,-0.01621,0.20376]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4304.0,"contact_point_centroid":[0.52337,0.01061,0.22069],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52299,0.01062,0.2183]}],"total_contact_groups":14},"final_pose_error":0.22117,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52668,-0.02025,0.01602],"final_tcp_position":[0.52931,0.02735,0.2134],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9749.03312,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.52708,-0.01705,0.1574],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53006,-0.02034,0.04713],"tcp_start":[0.52708,-0.01705,0.1574],"tcp_to_object_dist_end":0.02225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02031,0.02565],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31615,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14646,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10851.0,"raw_peak_contact_force":0.21616,"tcp_end":[0.52183,-0.02019,0.03758],"tcp_start":[0.53006,-0.02034,0.04713],"tcp_to_object_dist_end":0.01925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52581,-0.02023,0.14006],"object_pos_start":[0.53695,-0.02031,0.02565],"object_to_goal_dist_end":0.2705,"object_to_goal_dist_start":0.31615,"object_z_max":0.13991,"peak_contact_force":0.1337,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25765.0,"raw_peak_contact_force":0.48445,"tcp_end":[0.51779,-0.0201,0.16511],"tcp_start":[0.52183,-0.02019,0.03758],"tcp_to_object_dist_end":0.02631,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52668,-0.02025,0.01602],"object_pos_start":[0.52581,-0.02023,0.14006],"object_to_goal_dist_end":0.32424,"object_to_goal_dist_start":0.2705,"object_z_max":0.14135,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7944.0,"raw_peak_contact_force":1.53232,"subtask_id":"reach_goal_pre_place","tcp_end":[0.51845,-0.0094,0.22947],"tcp_start":[0.51779,-0.0201,0.16511],"tcp_to_object_dist_end":0.21389,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52668,-0.02025,0.01602],"object_pos_start":[0.52668,-0.02025,0.01602],"object_to_goal_dist_end":0.32424,"object_to_goal_dist_start":0.32424,"object_z_max":0.01602,"peak_contact_force":9749.03312,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8304.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.52931,0.02735,0.2134],"tcp_start":[0.51845,-0.0094,0.22947],"tcp_to_object_dist_end":0.20306,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6875,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.08671,"descend_to_goal.max_time":6.29195,"descend_to_goal.place_z_offset":0.01948,"descend_to_goal.speed":0.06662,"descend_to_grasp.speed":0.07777,"lift.lift_height":0.20081,"lift.max_time":9.6154,"lift.speed":0.03657,"transport_to_goal.arc_height":0.28544,"transport_to_goal.max_time":13.67398,"transport_to_goal.speed":0.14839},"optimized_scores":{"best_composite_score":-0.35456,"best_fitness_score":0.31544,"best_task_score":0.21238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.55553,0.01578,-0.00251],"force_p95":0.25888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39683,"mean_force":0.15108,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54047,0.00715,0.19177]},{"body_a":"world","body_b":"grasp_target","contact_count":588.0,"contact_point_centroid":[0.54196,-0.02658,-0.00159],"force_p95":0.1993,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35945,"mean_force":0.10032,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52597,-0.02714,0.04734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4523.0,"contact_point_centroid":[0.52824,-0.04034,0.12095],"force_p95":0.13511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35655,"mean_force":0.10073,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52379,-0.02222,0.12399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12743.0,"contact_point_centroid":[0.52765,-0.00832,0.06829],"force_p95":0.13548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30189,"mean_force":0.07875,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5249,-0.0271,0.06922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16484.0,"contact_point_centroid":[0.52764,-0.04543,0.06962],"force_p95":0.10423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28045,"mean_force":0.06201,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52486,-0.0271,0.0691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4286.0,"contact_point_centroid":[0.52957,-0.0032,0.12411],"force_p95":0.13585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27193,"mean_force":0.10325,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5242,-0.02133,0.12772]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5457,-0.02912,-0.00217],"force_p95":0.16888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22658,"mean_force":0.13513,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5306,-0.02728,0.04777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4409.0,"contact_point_centroid":[0.531,-0.0081,0.04755],"force_p95":0.08625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13958,"mean_force":0.05276,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52939,-0.02724,0.04631]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51604,-0.01116,0.23056]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53479,-0.02593,0.09253]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55562,0.01607,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56135,0.04852,0.20368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5141.0,"contact_point_centroid":[0.53199,-0.04629,0.04893],"force_p95":0.07808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08202,"mean_force":0.04416,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,-0.02724,0.04632]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1522.0,"contact_point_centroid":[0.54215,0.00947,0.19772],"force_p95":0.01184,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01551,"mean_force":0.01065,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54182,0.00948,0.1953]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4284.0,"contact_point_centroid":[0.56174,0.04848,0.20592],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.56133,0.04848,0.20368]}],"total_contact_groups":14},"final_pose_error":0.10952,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55562,0.01607,0.01602],"final_tcp_position":[0.57499,0.07201,0.20015],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.39683,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":860.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.53413,-0.02349,0.15663],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53758,-0.02749,0.05616],"tcp_start":[0.53413,-0.02349,0.15663],"tcp_to_object_dist_end":0.03124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54587,-0.02785,0.02532],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26021,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.16765,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11350.0,"raw_peak_contact_force":0.22658,"tcp_end":[0.52936,-0.02724,0.04628],"tcp_start":[0.53758,-0.02749,0.05616],"tcp_to_object_dist_end":0.02669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53067,-0.02884,0.07046],"object_pos_start":[0.54587,-0.02785,0.02532],"object_to_goal_dist_end":0.24356,"object_to_goal_dist_start":0.26021,"object_z_max":0.07039,"peak_contact_force":0.13311,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29815.0,"raw_peak_contact_force":0.35945,"tcp_end":[0.52481,-0.02709,0.10187],"tcp_start":[0.52936,-0.02724,0.04628],"tcp_to_object_dist_end":0.032,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55562,0.01607,0.01602],"object_pos_start":[0.53067,-0.02884,0.07046],"object_to_goal_dist_end":0.23241,"object_to_goal_dist_start":0.24356,"object_z_max":0.121,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12011.0,"raw_peak_contact_force":1.39683,"subtask_id":"reach_goal_pre_place","tcp_end":[0.5504,0.02434,0.21323],"tcp_start":[0.52481,-0.02709,0.10187],"tcp_to_object_dist_end":0.19745,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55562,0.01607,0.01602],"object_pos_start":[0.55562,0.01607,0.01602],"object_to_goal_dist_end":0.23241,"object_to_goal_dist_start":0.23241,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8284.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.57499,0.07201,0.20015],"tcp_start":[0.5504,0.02434,0.21323],"tcp_to_object_dist_end":0.19341,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53571,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.07522,"descend_to_goal.max_time":5.92337,"descend_to_goal.place_z_offset":-0.01854,"descend_to_goal.speed":0.0359,"descend_to_grasp.speed":0.06294,"lift.lift_height":0.15484,"lift.max_time":5.0506,"lift.speed":0.06365,"transport_to_goal.arc_height":0.24989,"transport_to_goal.max_time":6.18218,"transport_to_goal.speed":0.12155},"optimized_scores":{"best_composite_score":-0.05956,"best_fitness_score":0.61044,"best_task_score":0.26073},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.47492,0.04791,-0.00293],"force_p95":0.51227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73769,"mean_force":0.17003,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48511,0.03864,0.19078]},{"body_a":"world","body_b":"grasp_target","contact_count":309.0,"contact_point_centroid":[0.45872,-9e-05,-0.00124],"force_p95":0.37205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74736,"mean_force":0.1094,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4488,-0.00025,0.02272]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17550.0,"contact_point_centroid":[0.44795,0.01884,0.06983],"force_p95":0.08308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30339,"mean_force":0.05819,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44699,-0.00025,0.06779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18941.0,"contact_point_centroid":[0.44782,-0.01927,0.06796],"force_p95":0.0825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28046,"mean_force":0.05457,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.447,-0.00025,0.06604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9183.0,"contact_point_centroid":[0.4572,0.02855,0.14426],"force_p95":0.12816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24892,"mean_force":0.07597,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4544,0.00995,0.14496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8513.0,"contact_point_centroid":[0.45639,-0.00955,0.14262],"force_p95":0.14029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24207,"mean_force":0.07871,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45363,0.0092,0.14342]},{"body_a":"world","body_b":"grasp_target","contact_count":808.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48457,-4e-05,0.23241]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-5e-05,-0.00201],"force_p95":0.12816,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13808,"mean_force":0.12421,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4522,-0.0002,0.02257]},{"body_a":"world","body_b":"grasp_target","contact_count":2984.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46151,-0.0001,0.09041]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47453,0.04802,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.50274,0.05769,0.18286]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45108,0.01906,0.02383],"force_p95":0.07363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4511,-0.00022,0.02153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45097,-0.01929,0.02341],"force_p95":0.06453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08392,"mean_force":0.04268,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4511,-0.00022,0.02153]},{"body_a":"left_finger","body_b":"right_finger","contact_count":784.0,"contact_point_centroid":[0.48733,0.04043,0.19475],"force_p95":0.01339,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48704,0.04043,0.19264]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4220.0,"contact_point_centroid":[0.50305,0.05772,0.18505],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.50277,0.05771,0.18283]}],"total_contact_groups":14},"final_pose_error":0.14882,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.47453,0.04802,0.01602],"final_tcp_position":[0.51205,0.06632,0.1746],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":39.58773,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":39.58773,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":808.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46791,-7e-05,0.15904],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":746.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2984.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45863,-0.00012,0.02865],"tcp_start":[0.46791,-7e-05,0.15904],"tcp_to_object_dist_end":0.00498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,-5e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23322,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12823,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.13808,"tcp_end":[0.45107,-0.00022,0.0215],"tcp_start":[0.45863,-0.00012,0.02865],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46259,-0.0002,0.11464],"object_pos_start":[0.46271,-5e-05,0.02593],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.23322,"object_z_max":0.11453,"peak_contact_force":0.09541,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36800.0,"raw_peak_contact_force":0.74736,"tcp_end":[0.44696,-0.00024,0.12087],"tcp_start":[0.45107,-0.00022,0.0215],"tcp_to_object_dist_end":0.01683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47453,0.04802,0.01602],"object_pos_start":[0.46259,-0.0002,0.11464],"object_to_goal_dist_end":0.20164,"object_to_goal_dist_start":0.21274,"object_z_max":0.15338,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19464.0,"raw_peak_contact_force":1.73769,"subtask_id":"reach_goal_pre_place","tcp_end":[0.49386,0.04676,0.19838],"tcp_start":[0.44696,-0.00024,0.12087],"tcp_to_object_dist_end":0.18339,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47453,0.04802,0.01602],"object_pos_start":[0.47453,0.04802,0.01602],"object_to_goal_dist_end":0.20164,"object_to_goal_dist_start":0.20164,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8220.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.51205,0.06632,0.1746],"tcp_start":[0.49386,0.04676,0.19838],"tcp_to_object_dist_end":0.16399,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```