## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.3326 | 0.28 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 2 | 0.3398 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1421 | 0.20 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 1 | 0.1420 | 0.30 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1129 | 0.17 | ❌ rejected |

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

## Current Skill (Q=0.333) — your mutation base

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

- **Composite score**: 0.333
- **task_score** (E): 0.281
- **fitness_score**: 0.613  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1811 |
| descend_object | 1.00 | 1.00 | 0.0858 |
| grasp_object | 1.00 | 1.00 | 0.0119 |
| lift_object | 1.00 | 1.00 | 0.0998 |
| approach_goal | 0.00 | 0.00 | 0.0522 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.012, 0.123) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_object | descend | 1.00 / step_budget | (0.503, -0.012, 0.123)→(0.508, -0.016, 0.037) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.508, -0.016, 0.037)→(0.500, -0.016, 0.029) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 38.000 | 0.148 | 0.205 |
| lift_object | lift | 1.00 / step_budget | (0.500, -0.016, 0.029)→(0.496, -0.016, 0.128) | (0.515, -0.016, 0.026)→(0.512, -0.016, 0.113) | 0.270→0.237 | 1.00 / 23.000 | 0.135 | 0.633 |
| approach_goal | approach | 0.00 / guard_failure | (0.496, -0.016, 0.128)→(0.522, 0.025, 0.140) | (0.512, -0.016, 0.113)→(0.532, 0.031, 0.080) | 0.237→0.199 | 0.00 / 0.000 | 0.000 | 0.290 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.422
- phase_score: 0.313
- phase_breakdown.reach_place_standoff_score: 0.059
- phase_breakdown.reach_grasp_standoff_score: 0.907
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.422
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.289


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9186,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.29773,"lift_object.lift_height":0.11174},"optimized_scores":{"best_composite_score":0.30199,"best_fitness_score":0.58199,"best_task_score":0.21223},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":223.0,"contact_point_centroid":[0.53284,-0.01991,-0.00126],"force_p95":0.40726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7175,"mean_force":0.10815,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51969,-0.02033,0.02516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2569.0,"contact_point_centroid":[0.5259,0.01901,0.12639],"force_p95":0.16858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32908,"mean_force":0.10094,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52227,0.00085,0.12986]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8826.0,"contact_point_centroid":[0.52117,-0.00149,0.06907],"force_p95":0.11161,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3211,"mean_force":0.07628,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51749,-0.02028,0.06713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9611.0,"contact_point_centroid":[0.52112,-0.03897,0.06765],"force_p95":0.10691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31326,"mean_force":0.07132,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51751,-0.02028,0.06624]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2439.0,"contact_point_centroid":[0.5254,-0.01864,0.1258],"force_p95":0.16735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27432,"mean_force":0.10291,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52186,-0.00041,0.12927]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02104,-0.00208],"force_p95":0.14864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22636,"mean_force":0.12964,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52308,-0.02039,0.02507]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51157,-0.00859,0.20609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.52311,-0.00117,0.02634],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12705,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52183,-0.02037,0.02366]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.52537,-0.01828,0.07541]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.52302,-0.03949,0.02544],"force_p95":0.07082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08776,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52183,-0.02037,0.02367]}],"total_contact_groups":10},"final_pose_error":0.23585,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54237,0.04557,0.07992],"final_tcp_position":[0.53409,0.03408,0.14648],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.7175,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.5229,-0.01552,0.1336],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10866,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53019,-0.02052,0.03313],"tcp_start":[0.5229,-0.01552,0.1336],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02029,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31612,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14272,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.22636,"tcp_end":[0.5218,-0.02037,0.02363],"tcp_start":[0.53019,-0.02052,0.03313],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.53614,-0.0203,0.11203],"object_pos_start":[0.53688,-0.02029,0.02572],"object_to_goal_dist_end":0.27591,"object_to_goal_dist_start":0.31612,"object_z_max":0.11193,"peak_contact_force":0.12005,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18660.0,"raw_peak_contact_force":0.7175,"tcp_end":[0.51757,-0.02027,0.12304],"tcp_start":[0.5218,-0.02037,0.02363],"tcp_to_object_dist_end":0.02158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.54237,0.04557,0.07992],"object_pos_start":[0.53614,-0.0203,0.11203],"object_to_goal_dist_end":0.23251,"object_to_goal_dist_start":0.27591,"object_z_max":0.11826,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5008.0,"raw_peak_contact_force":0.32908,"subtask_id":"reach_place_standoff","tcp_end":[0.53409,0.03408,0.14648],"tcp_start":[0.51757,-0.02027,0.12304],"tcp_to_object_dist_end":0.06805,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.10368,"lift_object.lift_height":0.1093},"optimized_scores":{"best_composite_score":0.28624,"best_fitness_score":0.56624,"best_task_score":0.20915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":350.0,"contact_point_centroid":[0.54284,-0.02666,-0.00176],"force_p95":0.21361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41584,"mean_force":0.10498,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52458,-0.02617,0.04297]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7595.0,"contact_point_centroid":[0.52828,-0.00749,0.08571],"force_p95":0.12074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36542,"mean_force":0.08602,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52301,-0.02611,0.08381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7883.0,"contact_point_centroid":[0.52829,-0.04468,0.08467],"force_p95":0.11526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36207,"mean_force":0.08519,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52303,-0.02611,0.08319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":251.0,"contact_point_centroid":[0.52946,-0.00629,0.13476],"force_p95":0.21682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25277,"mean_force":0.14797,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52321,-0.02449,0.13832]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54571,-0.02894,-0.00223],"force_p95":0.18856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24993,"mean_force":0.13898,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52854,-0.02627,0.04365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.52938,-0.04123,0.13451],"force_p95":0.15697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20446,"mean_force":0.09129,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52322,-0.02391,0.13813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3111.0,"contact_point_centroid":[0.53101,-0.00737,0.04575],"force_p95":0.10772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14579,"mean_force":0.0649,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52732,-0.02624,0.04221]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51364,-0.01086,0.21296]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.52961,-0.02312,0.09345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3410.0,"contact_point_centroid":[0.53162,-0.04524,0.04446],"force_p95":0.10291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10479,"mean_force":0.06402,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52733,-0.02624,0.04222]}],"total_contact_groups":10},"final_pose_error":0.23219,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.53598,-0.02547,0.07969],"final_tcp_position":[0.52367,-0.01932,0.13721],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.41584,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.52566,-0.01897,0.1509],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53549,-0.02646,0.05191],"tcp_start":[0.52566,-0.01897,0.1509],"tcp_to_object_dist_end":0.02793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54564,-0.02703,0.02526],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25972,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17535,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8321.0,"raw_peak_contact_force":0.24993,"tcp_end":[0.52729,-0.02624,0.04217],"tcp_start":[0.53549,-0.02646,0.05191],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.53467,-0.02597,0.11207],"object_pos_start":[0.54564,-0.02703,0.02526],"object_to_goal_dist_end":0.22424,"object_to_goal_dist_start":0.25972,"object_z_max":0.11198,"peak_contact_force":0.16825,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15828.0,"raw_peak_contact_force":0.41584,"tcp_end":[0.52318,-0.02611,0.13884],"tcp_start":[0.52729,-0.02624,0.04217],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":78.0,"n_steps_budget":1000.0,"object_pos_end":[0.53598,-0.02547,0.07969],"object_pos_start":[0.53467,-0.02597,0.11207],"object_to_goal_dist_end":0.23471,"object_to_goal_dist_start":0.22424,"object_z_max":0.1121,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":675.0,"raw_peak_contact_force":0.25277,"subtask_id":"reach_place_standoff","tcp_end":[0.52367,-0.01932,0.13721],"tcp_start":[0.52318,-0.02611,0.13884],"tcp_to_object_dist_end":0.05914,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.speed":0.24573,"lift_object.lift_height":0.11412},"optimized_scores":{"best_composite_score":0.40958,"best_fitness_score":0.68958,"best_task_score":0.42199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.45973,-2e-05,-0.00139],"force_p95":0.43239,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76689,"mean_force":0.12049,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44835,-0.00025,0.02128]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10533.0,"contact_point_centroid":[0.44895,0.01872,0.06493],"force_p95":0.10613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30902,"mean_force":0.06778,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44661,-0.00026,0.06285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4755.0,"contact_point_centroid":[0.47221,0.00481,0.12498],"force_p95":0.16315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28806,"mean_force":0.09417,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46866,0.02318,0.12677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11465.0,"contact_point_centroid":[0.44874,-0.0191,0.06195],"force_p95":0.10651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28338,"mean_force":0.06292,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44665,-0.00026,0.06041]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.4753,0.04397,0.12575],"force_p95":0.14924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26614,"mean_force":0.09644,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47136,0.02578,0.12745]},{"body_a":"world","body_b":"grasp_target","contact_count":3804.0,"contact_point_centroid":[0.46286,-7e-05,-0.00196],"force_p95":0.12508,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47875,-6e-05,0.18932]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46283,-4e-05,-0.00201],"force_p95":0.12748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13832,"mean_force":0.12422,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45165,-0.00021,0.02137]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_object","phase_type":"descend","tcp_position_centroid":[0.45761,-0.00013,0.05377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.45078,0.01907,0.02263],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09392,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00022,0.02033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45017,-0.01926,0.02268],"force_p95":0.0629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08318,"mean_force":0.04075,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45055,-0.00022,0.02033]}],"total_contact_groups":10},"final_pose_error":0.14138,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.51749,0.07312,0.07974],"final_tcp_position":[0.50861,0.06084,0.13741],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.76689,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_grasp_standoff","tcp_end":[0.46015,-0.0001,0.08407],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45806,-0.00013,0.02742],"tcp_start":[0.46015,-0.0001,0.08407],"tcp_to_object_dist_end":0.005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46271,1e-05,0.02593],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12737,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.13832,"tcp_end":[0.45052,-0.00022,0.0203],"tcp_start":[0.45806,-0.00013,0.02742],"tcp_to_object_dist_end":0.01343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":691.0,"n_steps_budget":720.0,"object_pos_end":[0.46663,-0.00031,0.1157],"object_pos_start":[0.46271,1e-05,0.02593],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.23317,"object_z_max":0.11561,"peak_contact_force":0.11601,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22290.0,"raw_peak_contact_force":0.76689,"tcp_end":[0.44667,-0.00024,0.12335],"tcp_start":[0.45052,-0.00022,0.0203],"tcp_to_object_dist_end":0.02138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.51749,0.07312,0.07974],"object_pos_start":[0.46663,-0.00031,0.1157],"object_to_goal_dist_end":0.12942,"object_to_goal_dist_start":0.21001,"object_z_max":0.11573,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9670.0,"raw_peak_contact_force":0.28806,"subtask_id":"reach_place_standoff","tcp_end":[0.50861,0.06084,0.13741],"tcp_start":[0.44667,-0.00024,0.12335],"tcp_to_object_dist_end":0.05963,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```