## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.2631 | 0.15 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | -0.1647 | 0.16 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 1 | 0.1420 | 0.30 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1349 | 0.19 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2254 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.263) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_grasp_standoff
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_place_standoff
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.7
phases:
- id: approach_object
  type: approach
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
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_grasp_standoff
- id: descend_object
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
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: grasp_object
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
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.01
    - 0.0
    - 0.0
- id: lift_object
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
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current
- id: approach_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_retained
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: reach_place_standoff
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
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
    orientation:
      mode: keep_current
- id: retract_goal
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
    - 0.05
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=1, strategy=offset_target, offset=[0.01, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_retained, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_goal** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.263
- **task_score** (E): 0.151
- **fitness_score**: 0.167  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1546 |
| descend_object | 1.00 | 1.00 | 0.0002 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1358 |
| approach_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.443, -0.003, 0.161) | (0.515, -0.017, 0.030)→(0.488, -0.018, 0.019) | 0.268→0.287 | 1.00 / 5.000 | 353.175 | 1415.049 |
| descend_object | descend | 1.00 / force_exceeded | (0.443, -0.003, 0.161)→(0.443, -0.004, 0.161) | (0.488, -0.018, 0.019)→(0.488, -0.018, 0.019) | 0.287→0.287 | 1.00 / 5.000 | 272.494 | 214.635 |
| grasp_object | grasp | 1.00 / step_budget | (0.443, -0.003, 0.160)→(0.443, -0.003, 0.160) | (0.488, -0.018, 0.019)→(0.488, -0.018, 0.019) | 0.287→0.287 | 1.00 / 9.667 | 91052.716 | 207.197 |
| lift_object | lift | 1.00 / step_budget | (0.443, -0.003, 0.160)→(0.442, -0.003, 0.295) | (0.488, -0.018, 0.019)→(0.488, -0.018, 0.019) | 0.287→0.287 | 1.00 / 8.667 | 182004.818 | 152.112 |
| approach_goal | approach | 0.00 / guard_failure | (0.442, -0.003, 0.295)→(0.442, -0.003, 0.295) | (0.488, -0.018, 0.019)→(0.488, -0.018, 0.019) | 0.287→0.287 | 1.00 / 8.667 | 94266.023 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.170
- phase_score: 0.087
- phase_breakdown.reach_place_standoff_score: 0.005
- phase_breakdown.reach_grasp_standoff_score: 0.278
- grasp_place_fitness: 0.179

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.179
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.173
- **Median Q (composite search score)**: -0.261
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.48276,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.arc_height":0.1472,"approach_goal.speed":0.29349,"approach_object.arc_height":0.1132,"approach_object.speed":0.23018,"descend_goal.speed":0.13324,"descend_object.force_threshold":5.30159,"descend_object.speed":0.06961,"lift_object.speed":0.08448,"retract_goal.speed":0.18561},"optimized_scores":{"best_composite_score":-0.27795,"best_fitness_score":0.15205,"best_task_score":0.10856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":846.0,"contact_point_centroid":[0.64834,0.01958,-0.00041],"force_p95":466.45908,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1428.45478,"mean_force":250.52482,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42974,0.01462,0.15898]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68673,0.02388,-6e-05],"force_p95":339.69324,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":339.69324,"mean_force":339.69324,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.4612,-0.03034,0.15225]},{"body_a":"world","body_b":"link6","contact_count":500.0,"contact_point_centroid":[0.68727,0.02433,-0.00012],"force_p95":73.3219,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.89364,"mean_force":69.98161,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46124,-0.03007,0.15134]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.68733,0.02435,-0.00011],"force_p95":167.32427,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.88776,"mean_force":120.41028,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46122,-0.03004,0.15126]},{"body_a":"grasp_target","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.50705,-0.01767,0.03926],"force_p95":3.21705,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.34898,"mean_force":0.86727,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39213,0.01273,0.09119]},{"body_a":"grasp_target","body_b":"hand","contact_count":117.0,"contact_point_centroid":[0.49401,-0.02629,0.0494],"force_p95":2.56219,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.22824,"mean_force":0.9505,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39077,0.01254,0.08655]},{"body_a":"world","body_b":"grasp_target","contact_count":3661.0,"contact_point_centroid":[0.50543,-0.02105,-0.00214],"force_p95":0.22695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.13923,"mean_force":0.15065,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44296,0.01345,0.16997]},{"body_a":"grasp_target","body_b":"link6","contact_count":111.0,"contact_point_centroid":[0.54067,-0.00183,0.02718],"force_p95":0.78468,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.96943,"mean_force":0.4435,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38913,0.01274,0.09336]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49963,-0.02136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.4612,-0.03034,0.15225]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.49963,-0.02136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46124,-0.03007,0.15134]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49963,-0.02136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45983,-0.02989,0.21844]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49963,-0.02136,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46035,-0.03018,0.28783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":570.0,"contact_point_centroid":[0.46323,-0.02936,0.14987],"force_p95":0.0131,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01059,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46123,-0.03003,0.15123]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4413.0,"contact_point_centroid":[0.46187,-0.02926,0.21748],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01013,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45983,-0.02989,0.21877]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.46282,-0.02876,0.28479],"force_p95":0.00953,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00953,"mean_force":0.00953,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46035,-0.03018,0.28783]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53334,0.01143,-0.0033],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37981,0.01169,0.04981]}],"total_contact_groups":16},"final_pose_error":0.299,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.49963,-0.02136,0.01602],"final_tcp_position":[0.46036,-0.03019,0.28789],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273008.68219,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49963,-0.02136,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.33307,"object_to_goal_dist_start":0.31446,"object_z_max":0.03171,"peak_contact_force":248.18929,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4893.0,"raw_peak_contact_force":1428.45478,"subtask_id":"reach_grasp_standoff","tcp_end":[0.4612,-0.03034,0.15225],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14183,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49963,-0.02136,0.01602],"object_pos_start":[0.49963,-0.02136,0.01602],"object_to_goal_dist_end":0.33307,"object_to_goal_dist_start":0.33307,"object_z_max":0.01602,"peak_contact_force":339.69324,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":339.69324,"tcp_end":[0.46124,-0.03049,0.15214],"tcp_start":[0.4612,-0.03034,0.15225],"tcp_to_object_dist_end":0.14172,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.49963,-0.02136,0.01602],"object_pos_start":[0.49963,-0.02136,0.01602],"object_to_goal_dist_end":0.33307,"object_to_goal_dist_start":0.33307,"object_z_max":0.01602,"peak_contact_force":68.85451,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3070.0,"raw_peak_contact_force":252.89364,"tcp_end":[0.46123,-0.03004,0.15123],"tcp_start":[0.46123,-0.03003,0.15123],"tcp_to_object_dist_end":0.14082,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49963,-0.02136,0.01602],"object_pos_start":[0.49963,-0.02136,0.01602],"object_to_goal_dist_end":0.33307,"object_to_goal_dist_start":0.33307,"object_z_max":0.01602,"peak_contact_force":273008.68219,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8417.0,"raw_peak_contact_force":175.88776,"tcp_end":[0.46035,-0.03018,0.28783],"tcp_start":[0.46123,-0.03004,0.15123],"tcp_to_object_dist_end":0.27477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49963,-0.02136,0.01602],"object_pos_start":[0.49963,-0.02136,0.01602],"object_to_goal_dist_end":0.33307,"object_to_goal_dist_start":0.33307,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place_standoff","tcp_end":[0.46036,-0.03019,0.28789],"tcp_start":[0.46035,-0.03018,0.28783],"tcp_to_object_dist_end":0.27484,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.43902,"average_solve_count":41.0,"average_success_count":41.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.arc_height":0.16591,"approach_goal.speed":0.21687,"approach_object.arc_height":0.13587,"approach_object.speed":0.11695,"descend_goal.speed":0.10203,"descend_object.force_threshold":6.79027,"descend_object.speed":0.13879,"lift_object.speed":0.20748,"retract_goal.speed":0.18589},"optimized_scores":{"best_composite_score":-0.26075,"best_fitness_score":0.16925,"best_task_score":0.17343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":865.0,"contact_point_centroid":[0.64257,0.01527,-0.00042],"force_p95":434.04785,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1400.76855,"mean_force":245.56534,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42658,0.01263,0.16224]},{"body_a":"world","body_b":"link6","contact_count":500.0,"contact_point_centroid":[0.68041,0.00181,-0.00012],"force_p95":71.42959,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.99353,"mean_force":68.74171,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4648,0.00708,0.16731]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67903,0.00168,-0.00021],"force_p95":232.66855,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.66855,"mean_force":232.66855,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.46494,0.00703,0.16907]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.68043,0.00159,-0.0001],"force_p95":165.66116,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":167.00888,"mean_force":52.70947,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46473,0.00701,0.16724]},{"body_a":"grasp_target","body_b":"link6","contact_count":333.0,"contact_point_centroid":[0.54632,-0.0161,0.0423],"force_p95":1.17011,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.24317,"mean_force":0.38319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40453,0.01071,0.1278]},{"body_a":"grasp_target","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.52834,-0.02606,0.04787],"force_p95":1.84838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91043,"mean_force":0.57554,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40365,0.01057,0.12485]},{"body_a":"world","body_b":"grasp_target","contact_count":3398.0,"contact_point_centroid":[0.54162,-0.03269,-0.00277],"force_p95":0.47262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.53069,"mean_force":0.18447,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44079,0.01198,0.17405]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.4984,-0.03431,0.02965],"force_p95":1.84948,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.16023,"mean_force":0.88683,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38877,0.00794,0.05362]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.54388,-0.03098,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.46494,0.00703,0.16907]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.54388,-0.03098,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4648,0.00708,0.16731]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.54388,-0.03098,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46367,0.00695,0.23065]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.54388,-0.03098,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46412,0.00702,0.30119]},{"body_a":"left_finger","body_b":"right_finger","contact_count":572.0,"contact_point_centroid":[0.46677,0.007,0.1657],"force_p95":0.01346,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01056,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46478,0.00707,0.16718]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2401.0,"contact_point_centroid":[0.46552,0.00688,0.22943],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.0101,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46367,0.00695,0.23091]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5.0,"contact_point_centroid":[0.46826,0.007,0.30072],"force_p95":0.00936,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00936,"mean_force":0.00936,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46412,0.00702,0.30119]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53331,0.01378,-0.00305],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37973,0.0079,0.05016]}],"total_contact_groups":16},"final_pose_error":0.23236,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54388,-0.03098,0.02602],"final_tcp_position":[0.46414,0.00702,0.30126],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":273005.64901,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54388,-0.03098,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.2628,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":613.11354,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5061.0,"raw_peak_contact_force":1400.76855,"subtask_id":"reach_grasp_standoff","tcp_end":[0.46494,0.00703,0.16907],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16775,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54388,-0.03098,0.02602],"object_pos_start":[0.54388,-0.03098,0.02602],"object_to_goal_dist_end":0.2628,"object_to_goal_dist_start":0.2628,"object_z_max":0.02602,"peak_contact_force":263.46238,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":232.66855,"tcp_end":[0.46493,0.00694,0.16875],"tcp_start":[0.46494,0.00703,0.16907],"tcp_to_object_dist_end":0.16746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.54388,-0.03098,0.02602],"object_pos_start":[0.54388,-0.03098,0.02602],"object_to_goal_dist_end":0.2628,"object_to_goal_dist_start":0.2628,"object_z_max":0.02602,"peak_contact_force":85.17381,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3072.0,"raw_peak_contact_force":283.99353,"tcp_end":[0.46478,0.00707,0.16718],"tcp_start":[0.46478,0.00707,0.16718],"tcp_to_object_dist_end":0.16623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.54388,-0.03098,0.02602],"object_pos_start":[0.54388,-0.03098,0.02602],"object_to_goal_dist_end":0.2628,"object_to_goal_dist_start":0.2628,"object_z_max":0.02602,"peak_contact_force":273005.64901,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4577.0,"raw_peak_contact_force":167.00888,"tcp_end":[0.46412,0.00702,0.30119],"tcp_start":[0.46478,0.00707,0.16718],"tcp_to_object_dist_end":0.28901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54388,-0.03098,0.02602],"object_pos_start":[0.54388,-0.03098,0.02602],"object_to_goal_dist_end":0.2628,"object_to_goal_dist_start":0.2628,"object_z_max":0.02602,"peak_contact_force":9749.39856,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place_standoff","tcp_end":[0.46414,0.00702,0.30126],"tcp_start":[0.46412,0.00702,0.30119],"tcp_to_object_dist_end":0.28906,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.5,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.arc_height":0.11589,"approach_goal.speed":0.14763,"approach_object.arc_height":0.19772,"approach_object.speed":0.39834,"descend_goal.speed":0.13377,"descend_object.force_threshold":8.2571,"descend_object.speed":0.14764,"lift_object.speed":0.12764,"retract_goal.speed":0.28498},"optimized_scores":{"best_composite_score":-0.25063,"best_fitness_score":0.17937,"best_task_score":0.16988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.62949,0.01438,-0.00046],"force_p95":206.23219,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1415.92464,"mean_force":204.17794,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39035,0.01274,0.12622]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52466,0.0137,-0.00313],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":456.15136,"mean_force":21.72149,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37077,0.00782,0.04948]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.62466,0.01558,-0.0001],"force_p95":109.66313,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.43886,"mean_force":81.03273,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40363,0.01284,0.1602]},{"body_a":"world","body_b":"link6","contact_count":500.0,"contact_point_centroid":[0.62447,0.01562,-0.00014],"force_p95":78.38067,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.70378,"mean_force":72.45367,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.40356,0.01286,0.16031]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62363,0.01554,-0.00024],"force_p95":71.54458,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.54458,"mean_force":71.54458,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.40318,0.01283,0.16072]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.44342,-0.00944,0.04197],"force_p95":3.48515,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.85886,"mean_force":1.56594,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38158,0.00785,0.05133]},{"body_a":"world","body_b":"grasp_target","contact_count":3926.0,"contact_point_centroid":[0.42682,-0.00168,-0.00213],"force_p95":0.13751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3045,"mean_force":0.13819,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40229,0.01199,0.13554]},{"body_a":"grasp_target","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.47437,0.00486,0.00822],"force_p95":0.25375,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25685,"mean_force":0.11976,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36977,0.00778,0.04716]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.42181,-0.00192,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.40318,0.01283,0.16072]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.42181,-0.00192,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.40356,0.01286,0.16031]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.42181,-0.00192,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40198,0.01271,0.22629]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.42181,-0.00192,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4026,0.01274,0.29706]},{"body_a":"left_finger","body_b":"right_finger","contact_count":547.0,"contact_point_centroid":[0.40546,0.01286,0.15897],"force_p95":0.01306,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01098,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.40364,0.01285,0.16017]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2886.0,"contact_point_centroid":[0.40384,0.01273,0.22487],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01056,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40198,0.01271,0.22606]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4.0,"contact_point_centroid":[0.40444,0.01275,0.29605],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01096,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4026,0.01274,0.29706]}],"total_contact_groups":15},"final_pose_error":0.26139,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.42181,-0.00192,0.01602],"final_tcp_position":[0.4026,0.01274,0.2971],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":273048.54842,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42181,-0.00192,0.01602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2659,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":198.2207,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4885.0,"raw_peak_contact_force":1415.92464,"subtask_id":"reach_grasp_standoff","tcp_end":[0.40318,0.01283,0.16072],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14664,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.42181,-0.00192,0.01602],"object_pos_start":[0.42181,-0.00192,0.01602],"object_to_goal_dist_end":0.2659,"object_to_goal_dist_start":0.2659,"object_z_max":0.01602,"peak_contact_force":214.32535,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":71.54458,"tcp_end":[0.40318,0.01283,0.1607],"tcp_start":[0.40318,0.01283,0.16072],"tcp_to_object_dist_end":0.14662,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.42181,-0.00192,0.01602],"object_pos_start":[0.42181,-0.00192,0.01602],"object_to_goal_dist_end":0.2659,"object_to_goal_dist_start":0.2659,"object_z_max":0.01602,"peak_contact_force":273004.12064,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3047.0,"raw_peak_contact_force":84.70378,"tcp_end":[0.40364,0.01284,0.16016],"tcp_start":[0.40364,0.01284,0.16017],"tcp_to_object_dist_end":0.14604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":684.0,"n_steps_budget":750.0,"object_pos_end":[0.42181,-0.00192,0.01602],"object_pos_start":[0.42181,-0.00192,0.01602],"object_to_goal_dist_end":0.2659,"object_to_goal_dist_start":0.2659,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5626.0,"raw_peak_contact_force":113.43886,"tcp_end":[0.4026,0.01274,0.29706],"tcp_start":[0.40364,0.01284,0.16016],"tcp_to_object_dist_end":0.28207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.42181,-0.00192,0.01602],"object_pos_start":[0.42181,-0.00192,0.01602],"object_to_goal_dist_end":0.2659,"object_to_goal_dist_start":0.2659,"object_z_max":0.01602,"peak_contact_force":273048.54842,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_place_standoff","tcp_end":[0.4026,0.01274,0.2971],"tcp_start":[0.4026,0.01274,0.29706],"tcp_to_object_dist_end":0.28212,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```