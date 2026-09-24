## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | -0.1647 | 0.16 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 1 | 0.1420 | 0.30 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1349 | 0.19 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.2254 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.1349 | 0.19 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.165) — your mutation base

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

- **Composite score**: -0.165
- **task_score** (E): 0.163
- **fitness_score**: 0.165  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1298 |
| descend_object | 0.00 | 1.00 | 0.0476 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1345 |
| approach_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.432, -0.005, 0.191) | (0.515, -0.017, 0.030)→(0.478, -0.020, 0.016) | 0.268→0.295 | 1.00 / 5.000 | 248.989 | 1575.103 |
| descend_object | descend | 0.00 / step_budget | (0.432, -0.005, 0.191)→(0.465, -0.021, 0.176) | (0.478, -0.020, 0.016)→(0.478, -0.020, 0.016) | 0.295→0.295 | 1.00 / 5.000 | 400.528 | 927.475 |
| grasp_object | grasp | 1.00 / step_budget | (0.465, -0.021, 0.174)→(0.465, -0.021, 0.174) | (0.478, -0.020, 0.016)→(0.478, -0.020, 0.016) | 0.295→0.295 | 1.00 / 9.667 | 182025.392 | 210.247 |
| lift_object | lift | 0.00 / step_budget | (0.419, 0.077, 0.213)→(0.415, 0.122, 0.284) | (0.478, -0.020, 0.016)→(0.466, -0.019, 0.014) | 0.295→0.300 | 1.00 / 9.667 | 169.237 | 419.369 |
| approach_goal | approach | 0.00 / guard_failure | (0.415, 0.122, 0.284)→(0.415, 0.122, 0.284) | (0.447, 0.044, 0.014)→(0.447, 0.044, 0.014) | 0.279→0.279 | 1.00 / 10.667 | 237372.300 | 323.034 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.197
- phase_score: 0.016
- phase_breakdown.reach_place_standoff_score: 0.007
- phase_breakdown.reach_grasp_standoff_score: 0.035
- grasp_place_fitness: 0.183

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.183
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.197
- **Median Q (composite search score)**: -0.149
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.294


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.1,"average_mean_iterations":26.94444,"average_solve_count":90.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.13654,"approach_object.speed":0.13884,"descend_object.speed":0.25288},"optimized_scores":{"best_composite_score":-0.19806,"best_fitness_score":0.13194,"best_task_score":0.09862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":884.0,"contact_point_centroid":[0.63188,-0.00127,-0.00047],"force_p95":386.78344,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1695.36512,"mean_force":228.93756,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41917,-0.00369,0.16731]},{"body_a":"world","body_b":"link6","contact_count":576.0,"contact_point_centroid":[0.62843,-0.00942,-0.00021],"force_p95":631.93323,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":918.65606,"mean_force":298.12756,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.43634,-0.01358,0.19932]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.46352,-0.00587,-1e-05],"force_p95":663.20607,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":663.20607,"mean_force":663.20607,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36492,0.2097,0.11869]},{"body_a":"world","body_b":"link6","contact_count":1667.0,"contact_point_centroid":[0.55981,-0.04302,-0.00018],"force_p95":320.04134,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":366.39532,"mean_force":214.69013,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38669,0.10046,0.13264]},{"body_a":"world","body_b":"hand","contact_count":441.0,"contact_point_centroid":[0.47292,0.13723,-0.00014],"force_p95":243.5512,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.65378,"mean_force":125.50463,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.37015,0.18102,0.10001]},{"body_a":"world","body_b":"link6","contact_count":499.0,"contact_point_centroid":[0.67166,-0.02387,-0.00012],"force_p95":74.61045,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.9261,"mean_force":69.72323,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.02317,0.17726]},{"body_a":"world","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.44733,0.15342,-9e-05],"force_p95":29.18313,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.18313,"mean_force":29.18313,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36492,0.2097,0.11869]},{"body_a":"grasp_target","body_b":"link7","contact_count":200.0,"contact_point_centroid":[0.51222,-0.01977,0.0378],"force_p95":3.07482,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.3081,"mean_force":0.66111,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38888,-0.00134,0.10524]},{"body_a":"grasp_target","body_b":"link6","contact_count":143.0,"contact_point_centroid":[0.53644,-0.02075,0.03284],"force_p95":1.04257,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.25676,"mean_force":0.56928,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38505,-0.00129,0.10184]},{"body_a":"world","body_b":"grasp_target","contact_count":3636.0,"contact_point_centroid":[0.50867,-0.02732,-0.00211],"force_p95":0.23313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33505,"mean_force":0.14841,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43177,-0.00352,0.17729]},{"body_a":"grasp_target","body_b":"hand","contact_count":110.0,"contact_point_centroid":[0.49049,-0.02537,0.04984],"force_p95":2.50825,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.27071,"mean_force":0.93124,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38422,-0.00122,0.08852]},{"body_a":"grasp_target","body_b":"link6","contact_count":1572.0,"contact_point_centroid":[0.5111,-0.03053,0.02295],"force_p95":0.97499,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.96803,"mean_force":0.63442,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38144,0.11296,0.12846]},{"body_a":"world","body_b":"grasp_target","contact_count":6996.0,"contact_point_centroid":[0.4876,-0.02765,-0.00361],"force_p95":0.49735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08758,"mean_force":0.25123,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.38643,0.10227,0.13182]},{"body_a":"grasp_target","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.47156,-0.00961,0.01388],"force_p95":0.93037,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.93037,"mean_force":0.93037,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36492,0.2097,0.11869]},{"body_a":"grasp_target","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.51822,-0.00347,0.03518],"force_p95":0.19874,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84747,"mean_force":0.10206,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39761,0.05124,0.13454]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.46739,-0.0212,-0.00549],"force_p95":0.47284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48579,"mean_force":0.34511,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36492,0.2097,0.11869]}],"total_contact_groups":22},"final_pose_error":0.28229,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.46631,-0.01829,0.00877],"final_tcp_position":[0.36505,0.20968,0.11884],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.12059,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,-0.02907,0.01602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.3375,"object_to_goal_dist_start":0.31446,"object_z_max":0.031,"peak_contact_force":362.92812,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4992.0,"raw_peak_contact_force":1695.36512,"subtask_id":"reach_grasp_standoff","tcp_end":[0.45621,-0.00862,0.20652],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19745,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,-0.02907,0.01602],"object_pos_start":[0.50393,-0.02907,0.01602],"object_to_goal_dist_end":0.3375,"object_to_goal_dist_start":0.3375,"object_z_max":0.01602,"peak_contact_force":366.49455,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2980.0,"raw_peak_contact_force":918.65606,"tcp_end":[0.46429,-0.0234,0.17875],"tcp_start":[0.45621,-0.00862,0.20652],"tcp_to_object_dist_end":0.16759,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.50393,-0.02907,0.01602],"object_pos_start":[0.50393,-0.02907,0.01602],"object_to_goal_dist_end":0.3375,"object_to_goal_dist_start":0.3375,"object_z_max":0.01602,"peak_contact_force":273004.12059,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3059.0,"raw_peak_contact_force":200.9261,"tcp_end":[0.46409,-0.0232,0.17713],"tcp_start":[0.46409,-0.02319,0.17713],"tcp_to_object_dist_end":0.16607,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1749.0,"n_steps_budget":930.0,"object_pos_end":[0.48394,-0.03316,0.01313],"object_pos_start":[0.50393,-0.02907,0.01602],"object_to_goal_dist_end":0.34899,"object_to_goal_dist_start":0.3375,"object_z_max":0.01602,"peak_contact_force":187.2062,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18289.0,"raw_peak_contact_force":366.39532,"tcp_end":[0.36492,0.2097,0.11869],"tcp_start":[0.37725,0.0759,0.165],"tcp_to_object_dist_end":0.29032,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46631,-0.01829,0.00877],"object_pos_start":[0.46631,-0.01829,0.00877],"object_to_goal_dist_end":0.34747,"object_to_goal_dist_start":0.34747,"object_z_max":0.00877,"peak_contact_force":167951.73011,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11.0,"raw_peak_contact_force":663.20607,"subtask_id":"reach_place_standoff","tcp_end":[0.36505,0.20968,0.11884],"tcp_start":[0.36492,0.2097,0.11869],"tcp_to_object_dist_end":0.27266,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.82022,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.05582,"approach_object.speed":0.08619,"descend_object.speed":0.13905},"optimized_scores":{"best_composite_score":-0.14688,"best_fitness_score":0.18312,"best_task_score":0.19683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.62994,-0.0027,-0.00048],"force_p95":204.89047,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1700.13145,"mean_force":201.32574,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40674,-0.0035,0.15224]},{"body_a":"world","body_b":"link6","contact_count":973.0,"contact_point_centroid":[0.6143,-0.01055,-0.00022],"force_p95":528.67766,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":945.07211,"mean_force":315.34291,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.42769,-0.01262,0.20433]},{"body_a":"world","body_b":"link6","contact_count":1152.0,"contact_point_centroid":[0.55615,-0.06704,-0.00013],"force_p95":302.06888,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.27046,"mean_force":244.39433,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45942,0.05673,0.20839]},{"body_a":"link5","body_b":"hand","contact_count":790.0,"contact_point_centroid":[0.40588,-0.03501,0.2748],"force_p95":294.92911,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.91905,"mean_force":207.65207,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46941,0.02821,0.31277]},{"body_a":"world","body_b":"link6","contact_count":498.0,"contact_point_centroid":[0.67572,-0.01785,-0.00013],"force_p95":73.11039,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.52694,"mean_force":69.72409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46476,-0.03124,0.17269]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.4088,-0.01367,0.32437],"force_p95":139.93889,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.93889,"mean_force":139.93889,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45461,0.06992,0.3657]},{"body_a":"grasp_target","body_b":"link6","contact_count":347.0,"contact_point_centroid":[0.5413,-0.01146,0.02719],"force_p95":1.12396,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.35536,"mean_force":0.23508,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39139,-0.00191,0.11889]},{"body_a":"grasp_target","body_b":"link7","contact_count":175.0,"contact_point_centroid":[0.51799,-0.00919,0.02982],"force_p95":3.28522,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.80963,"mean_force":0.73664,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38674,-0.00159,0.0983]},{"body_a":"world","body_b":"grasp_target","contact_count":3775.0,"contact_point_centroid":[0.51518,-0.03048,-0.00243],"force_p95":0.38323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.32479,"mean_force":0.16396,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41859,-0.00327,0.16104]},{"body_a":"grasp_target","body_b":"link6","contact_count":1229.0,"contact_point_centroid":[0.50484,-0.02033,0.02943],"force_p95":1.13955,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.63576,"mean_force":0.422,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46411,0.05651,0.24024]},{"body_a":"grasp_target","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.5036,-0.03121,0.03352],"force_p95":2.06274,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.57612,"mean_force":1.20451,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39121,-0.00139,0.04927]},{"body_a":"world","body_b":"grasp_target","contact_count":5741.0,"contact_point_centroid":[0.49491,-0.00135,-0.00291],"force_p95":0.5216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90048,"mean_force":0.21036,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45648,0.06456,0.2335]},{"body_a":"grasp_target","body_b":"link6","contact_count":283.0,"contact_point_centroid":[0.53889,-0.01513,0.03494],"force_p95":0.17417,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18613,"mean_force":0.12251,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.39499,-0.00833,0.18328]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50817,-0.03127,-0.00205],"force_p95":0.16747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17678,"mean_force":0.127,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.4285,-0.01285,0.20414]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.50778,-0.03141,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46476,-0.03124,0.17269]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.47116,0.07883,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45461,0.06992,0.3657]}],"total_contact_groups":20},"final_pose_error":0.24503,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.47116,0.07883,0.01602],"final_tcp_position":[0.45463,0.06998,0.36571],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":272137.63009,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50963,-0.0308,0.01602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.28175,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":193.56469,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5223.0,"raw_peak_contact_force":1700.13145,"subtask_id":"reach_grasp_standoff","tcp_end":[0.43483,-0.00681,0.20323],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20302,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50778,-0.03141,0.01602],"object_pos_start":[0.50963,-0.0308,0.01602],"object_to_goal_dist_end":0.28298,"object_to_goal_dist_start":0.28175,"object_z_max":0.01618,"peak_contact_force":442.42221,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5256.0,"raw_peak_contact_force":945.07211,"tcp_end":[0.4649,-0.03089,0.17418],"tcp_start":[0.43483,-0.00681,0.20323],"tcp_to_object_dist_end":0.16387,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.50778,-0.03141,0.01602],"object_pos_start":[0.50778,-0.03141,0.01602],"object_to_goal_dist_end":0.28298,"object_to_goal_dist_start":0.28298,"object_z_max":0.01602,"peak_contact_force":67.93402,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3051.0,"raw_peak_contact_force":235.52694,"tcp_end":[0.46474,-0.0313,0.17256],"tcp_start":[0.46474,-0.03129,0.17256],"tcp_to_object_dist_end":0.16235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1711.0,"n_steps_budget":930.0,"object_pos_end":[0.49274,-0.02514,0.01426],"object_pos_start":[0.50778,-0.03141,0.01602],"object_to_goal_dist_end":0.28673,"object_to_goal_dist_start":0.28298,"object_z_max":0.01974,"peak_contact_force":160.87479,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16188.0,"raw_peak_contact_force":395.27046,"tcp_end":[0.45461,0.06992,0.3657],"tcp_start":[0.45396,0.0697,0.23555],"tcp_to_object_dist_end":0.36606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47116,0.07883,0.01602],"object_pos_start":[0.47116,0.07883,0.01602],"object_to_goal_dist_end":0.24381,"object_to_goal_dist_start":0.24381,"object_z_max":0.01602,"peak_contact_force":272137.63009,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":139.93889,"subtask_id":"reach_place_standoff","tcp_end":[0.45463,0.06998,0.36571],"tcp_start":[0.45461,0.06992,0.3657],"tcp_to_object_dist_end":0.35019,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.45556,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.15824,"approach_object.speed":0.09279,"descend_object.speed":0.27345},"optimized_scores":{"best_composite_score":-0.14922,"best_fitness_score":0.18078,"best_task_score":0.19288},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62963,2e-05,-0.00046],"force_p95":198.50888,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1329.81125,"mean_force":199.31188,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39193,-0.00011,0.12937]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.62187,0.0036,-0.00022],"force_p95":547.80733,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":918.69826,"mean_force":284.02362,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.42134,-0.00028,0.18666]},{"body_a":"link5","body_b":"hand","contact_count":867.0,"contact_point_centroid":[0.39112,-0.01795,0.27686],"force_p95":355.60974,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.43994,"mean_force":232.69267,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43044,0.06342,0.31278]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52677,0.0044,-0.00294],"force_p95":22.3319,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.63808,"mean_force":22.3319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37123,-0.00025,0.05132]},{"body_a":"world","body_b":"link6","contact_count":1192.0,"contact_point_centroid":[0.54262,-0.03217,-0.00012],"force_p95":344.27538,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":400.23981,"mean_force":250.95569,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4291,0.07352,0.21232]},{"body_a":"world","body_b":"link6","contact_count":499.0,"contact_point_centroid":[0.67517,0.01169,-0.00012],"force_p95":72.85342,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.28835,"mean_force":69.28078,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46501,-0.00904,0.17295]},{"body_a":"link5","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.38234,0.0019,0.32792],"force_p95":165.95849,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.95849,"mean_force":165.95849,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.42516,0.08633,0.36886]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.44479,0.00205,0.04287],"force_p95":3.54946,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.74004,"mean_force":1.52887,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38165,-0.00021,0.05354]},{"body_a":"grasp_target","body_b":"link6","contact_count":574.0,"contact_point_centroid":[0.42648,0.03209,0.02327],"force_p95":1.61325,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.06009,"mean_force":0.66715,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43246,0.05415,0.29793]},{"body_a":"world","body_b":"grasp_target","contact_count":3921.0,"contact_point_centroid":[0.42657,-1e-05,-0.00212],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26973,"mean_force":0.13759,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40383,-8e-05,0.13844]},{"body_a":"world","body_b":"grasp_target","contact_count":6895.0,"contact_point_centroid":[0.41477,0.0242,-0.00264],"force_p95":0.50678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0784,"mean_force":0.17738,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.42777,0.07745,0.24604]},{"body_a":"grasp_target","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.47487,-0.00424,0.00832],"force_p95":0.30019,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30164,"mean_force":0.16768,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37027,-0.00026,0.04972]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.42141,0.0,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.42222,-0.00028,0.18691]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.42141,0.0,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46501,-0.00904,0.17295]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.4025,0.07197,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.42516,0.08633,0.36886]},{"body_a":"left_finger","body_b":"right_finger","contact_count":577.0,"contact_point_centroid":[0.46705,-0.0088,0.17107],"force_p95":0.01369,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01517,"mean_force":0.01046,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.465,-0.00906,0.17282]}],"total_contact_groups":18},"final_pose_error":0.27805,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.4025,0.07197,0.01602],"final_tcp_position":[0.42518,0.0864,0.36886],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":273004.12056,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42141,0.0,0.01602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.26507,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":190.47353,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4878.0,"raw_peak_contact_force":1329.81125,"subtask_id":"reach_grasp_standoff","tcp_end":[0.40448,-0.00011,0.16302],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14797,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42141,0.0,0.01602],"object_pos_start":[0.42141,0.0,0.01602],"object_to_goal_dist_end":0.26507,"object_to_goal_dist_start":0.26507,"object_z_max":0.01602,"peak_contact_force":392.66713,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4977.0,"raw_peak_contact_force":918.69826,"tcp_end":[0.46511,-0.00818,0.17417],"tcp_start":[0.40448,-0.00011,0.16302],"tcp_to_object_dist_end":0.16428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":100.0,"n_steps_budget":50.0,"object_pos_end":[0.42141,0.0,0.01602],"object_pos_start":[0.42141,0.0,0.01602],"object_to_goal_dist_end":0.26507,"object_to_goal_dist_start":0.26507,"object_z_max":0.01602,"peak_contact_force":273004.12056,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3076.0,"raw_peak_contact_force":194.28835,"tcp_end":[0.465,-0.00907,0.17282],"tcp_start":[0.465,-0.00906,0.17282],"tcp_to_object_dist_end":0.16299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1816.0,"n_steps_budget":960.0,"object_pos_end":[0.42141,0.0,0.01602],"object_pos_start":[0.42141,0.0,0.01602],"object_to_goal_dist_end":0.26507,"object_to_goal_dist_start":0.26507,"object_z_max":0.01614,"peak_contact_force":159.62938,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17280.0,"raw_peak_contact_force":496.43994,"tcp_end":[0.42516,0.08633,0.36886],"tcp_start":[0.42473,0.08621,0.23752],"tcp_to_object_dist_end":0.36327,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.4025,0.07197,0.01602],"object_pos_start":[0.4025,0.07197,0.01602],"object_to_goal_dist_end":0.24685,"object_to_goal_dist_start":0.24685,"object_z_max":0.01602,"peak_contact_force":272027.53985,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9.0,"raw_peak_contact_force":165.95849,"subtask_id":"reach_place_standoff","tcp_end":[0.42518,0.0864,0.36886],"tcp_start":[0.42516,0.08633,0.36886],"tcp_to_object_dist_end":0.35387,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```