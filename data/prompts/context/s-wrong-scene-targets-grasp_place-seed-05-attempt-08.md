## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1922 | 0.29 | ✅ accepted |
| 7 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.1719 | 0.22 | ❌ rejected |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.530500292374538, 0.030794078973649372, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.530500292374538, 0.030794078973649372, 0.03]
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.192) — your mutation base

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
  - 0.1
  weight: 0.3
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.4
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.15
    tolerance: 0.01
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
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: approach_goal
  type: approach
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_to_place
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
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: release
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
    - -0.05
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, -0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.192
- **task_score** (E): 0.290
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1659 |
| descend_to_grasp | 1.00 | 1.00 | 0.1046 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.1089 |
| approach_goal | 0.33 | 1.00 | 0.1106 |
| descend_to_place | 0.67 | 1.00 | 0.0687 |
| release | 1.00 | 1.00 | 0.0226 |
| retract | 1.00 | 1.00 | 0.0412 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.017, 0.138) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.510, 0.018, 0.033) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, 0.018, 0.033)→(0.502, 0.017, 0.025) | (0.516, 0.018, 0.026)→(0.515, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.333 | 0.145 | 0.214 |
| lift | lift | 1.00 / step_budget | (0.502, 0.017, 0.025)→(0.498, 0.017, 0.133) | (0.515, 0.017, 0.026)→(0.516, 0.017, 0.121) | 0.237→0.198 | 1.00 / 23.000 | 0.133 | 0.733 |
| approach_goal | approach | 0.33 / step_budget | (0.498, 0.017, 0.133)→(0.548, 0.098, 0.188) | (0.516, 0.017, 0.121)→(0.524, 0.081, 0.016) | 0.198→0.199 | 1.00 / 8.000 | 3249.718 | 1.438 |
| descend_to_place | descend | 0.67 / step_budget | (0.548, 0.098, 0.188)→(0.575, 0.138, 0.154) | (0.524, 0.081, 0.016)→(0.524, 0.081, 0.016) | 0.199→0.199 | 1.00 / 8.000 | 94251.427 | 0.123 |
| release | release | 1.00 / step_budget | (0.575, 0.138, 0.154)→(0.569, 0.136, 0.175) | (0.524, 0.081, 0.016)→(0.524, 0.081, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.569, 0.136, 0.175)→(0.566, 0.135, 0.134) | (0.524, 0.081, 0.016)→(0.524, 0.081, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.419
- phase_score: 0.295
- phase_breakdown.reach_object_score: 0.155
- phase_breakdown.reach_goal_score: 0.390
- phase_breakdown.lift_object_score: 0.308
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.419
- **Median Q (composite search score)**: 0.202
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.286


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.60153,0.17858,0.10809]},{"name":"goal","value":[0.5305,0.03079,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74834,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.1795,"approach_object.approach_speed":0.10275,"descend_to_grasp.descend_speed":0.06289,"descend_to_place.place_speed":0.0941,"lift.lift_height":0.1086},"optimized_scores":{"best_composite_score":0.25689,"best_fitness_score":0.68689,"best_task_score":0.4188},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2463.0,"contact_point_centroid":[0.54389,0.106,-0.00232],"force_p95":0.13536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36458,"mean_force":0.14042,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55784,0.11113,0.1637]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.52723,0.02849,-0.0012],"force_p95":0.49979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67654,"mean_force":0.09505,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51479,0.0294,0.02951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8829.0,"contact_point_centroid":[0.5151,0.01041,0.07216],"force_p95":0.1077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33162,"mean_force":0.06963,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51215,0.02924,0.07034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9206.0,"contact_point_centroid":[0.51522,0.04807,0.07106],"force_p95":0.10526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32821,"mean_force":0.06782,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51219,0.02924,0.06942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3169.0,"contact_point_centroid":[0.52573,0.06747,0.12861],"force_p95":0.16452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28234,"mean_force":0.09965,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52113,0.04944,0.13067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2571.0,"contact_point_centroid":[0.52534,0.02971,0.12856],"force_p95":0.18331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28207,"mean_force":0.11067,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52036,0.04802,0.13001]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0305,-0.00212],"force_p95":0.15733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23794,"mean_force":0.13194,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51765,0.0296,0.02911]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4063.0,"contact_point_centroid":[0.51732,0.01032,0.03048],"force_p95":0.08024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14385,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51642,0.02952,0.02773]},{"body_a":"world","body_b":"grasp_target","contact_count":2128.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51094,0.01386,0.21805]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52313,0.0293,0.07221]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54392,0.10614,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58661,0.16175,0.1365]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54392,0.10614,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59101,0.17443,0.10353]},{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.54392,0.10614,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58667,0.17308,0.10389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.51726,0.04867,0.02953],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08571,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51643,0.02952,0.02774]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2331.0,"contact_point_centroid":[0.56047,0.11484,0.16797],"force_p95":0.01171,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01587,"mean_force":0.01065,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56009,0.11483,0.16573]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4253.0,"contact_point_centroid":[0.58718,0.16182,0.13862],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58664,0.16179,0.13638]}],"total_contact_groups":17},"final_pose_error":0.00972,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54392,0.10614,0.01602],"final_tcp_position":[0.58482,0.17248,0.08191],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.90958,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52427,0.0282,0.13715],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52468,0.03007,0.03705],"tcp_start":[0.52427,0.0282,0.13715],"tcp_to_object_dist_end":0.01249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02952,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18462,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14985,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10847.0,"raw_peak_contact_force":0.23794,"tcp_end":[0.5164,0.02952,0.0277],"tcp_start":[0.52468,0.03007,0.03705],"tcp_to_object_dist_end":0.01415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.52889,0.02929,0.11176],"object_pos_start":[0.53039,0.02952,0.02561],"object_to_goal_dist_end":0.16607,"object_to_goal_dist_start":0.18462,"object_z_max":0.11166,"peak_contact_force":0.10108,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18177.0,"raw_peak_contact_force":0.67654,"subtask_id":"lift_object","tcp_end":[0.51222,0.02925,0.12397],"tcp_start":[0.5164,0.02952,0.0277],"tcp_to_object_dist_end":0.02066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54392,0.10614,0.01602],"object_pos_start":[0.52889,0.02929,0.11176],"object_to_goal_dist_end":0.13056,"object_to_goal_dist_start":0.16607,"object_z_max":0.11627,"peak_contact_force":9748.90958,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10534.0,"raw_peak_contact_force":1.36458,"subtask_id":"reach_goal","tcp_end":[0.57895,0.14601,0.18276],"tcp_start":[0.51222,0.02925,0.12397],"tcp_to_object_dist_end":0.17498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54392,0.10614,0.01602],"object_pos_start":[0.54392,0.10614,0.01602],"object_to_goal_dist_end":0.13056,"object_to_goal_dist_start":0.13056,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8253.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.596,0.17596,0.10256],"tcp_start":[0.57895,0.14601,0.18276],"tcp_to_object_dist_end":0.12279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54392,0.10614,0.01602],"object_pos_start":[0.54392,0.10614,0.01602],"object_to_goal_dist_end":0.13056,"object_to_goal_dist_start":0.13056,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58904,0.17379,0.12325],"tcp_start":[0.596,0.17596,0.10256],"tcp_to_object_dist_end":0.13458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.54392,0.10614,0.01602],"object_pos_start":[0.54392,0.10614,0.01602],"object_to_goal_dist_end":0.13056,"object_to_goal_dist_start":0.13056,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":496.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58482,0.17248,0.08191],"tcp_start":[0.58904,0.17379,0.12325],"tcp_to_object_dist_end":0.10206,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33171,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07505,"approach_object.approach_speed":0.06968,"descend_to_grasp.descend_speed":0.04066,"descend_to_place.place_speed":0.05139,"lift.lift_height":0.1349},"optimized_scores":{"best_composite_score":0.11812,"best_fitness_score":0.54812,"best_task_score":0.14429},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2842.0,"contact_point_centroid":[0.49525,0.03757,-0.00236],"force_p95":0.18756,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48413,"mean_force":0.14422,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50607,0.0312,0.18302]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.50075,-0.01524,-0.0011],"force_p95":0.694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8567,"mean_force":0.10646,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4892,-0.01542,0.01974]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10832.0,"contact_point_centroid":[0.48962,0.00347,0.07481],"force_p95":0.11179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30611,"mean_force":0.07279,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48654,-0.01537,0.07329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11465.0,"contact_point_centroid":[0.48925,-0.03416,0.07245],"force_p95":0.11737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28421,"mean_force":0.06936,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48658,-0.01537,0.07161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.49001,-0.02547,0.1414],"force_p95":0.17877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24507,"mean_force":0.10783,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48794,-0.00733,0.14558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1923.0,"contact_point_centroid":[0.49048,0.01133,0.14208],"force_p95":0.16973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24166,"mean_force":0.1081,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48821,-0.00653,0.14623]},{"body_a":"grasp_target","body_b":"hand","contact_count":69.0,"contact_point_centroid":[0.50602,0.00467,0.06017],"force_p95":0.06268,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23701,"mean_force":0.03146,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48831,-0.01541,0.02238]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50378,-0.0155,-0.00203],"force_p95":0.13024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15887,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49191,-0.01545,0.01927]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49884,-0.00697,0.21957]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49772,-0.01504,0.06743]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4955,0.03879,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52489,0.07394,0.20642]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4955,0.03879,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.53082,0.09175,0.21458]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.4955,0.03879,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5278,0.0912,0.21611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.49122,0.00376,0.02079],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09784,"mean_force":0.05162,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49071,-0.01544,0.01803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49127,-0.03452,0.01987],"force_p95":0.06776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09181,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49071,-0.01544,0.01803]},{"body_a":"grasp_target","body_b":"hand","contact_count":274.0,"contact_point_centroid":[0.50823,-0.02719,0.05583],"force_p95":0.01195,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03871,"mean_force":0.00478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49073,-0.01544,0.01805]}],"total_contact_groups":19},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.4955,0.03879,0.01602],"final_tcp_position":[0.52648,0.09095,0.19455],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273005.43388,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49966,-0.01428,0.13898],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4987,-0.01554,0.02634],"tcp_start":[0.49966,-0.01428,0.13898],"tcp_to_object_dist_end":0.00513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50363,-0.0153,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31214,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1305,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11071.0,"raw_peak_contact_force":0.15887,"tcp_end":[0.49068,-0.01544,0.018],"tcp_start":[0.4987,-0.01554,0.02634],"tcp_to_object_dist_end":0.01516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":754.0,"n_steps_budget":840.0,"object_pos_end":[0.50796,-0.01524,0.12973],"object_pos_start":[0.50363,-0.0153,0.02588],"object_to_goal_dist_end":0.24765,"object_to_goal_dist_start":0.31214,"object_z_max":0.12968,"peak_contact_force":0.18768,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22498.0,"raw_peak_contact_force":0.8567,"subtask_id":"lift_object","tcp_end":[0.48675,-0.01536,0.14097],"tcp_start":[0.49068,-0.01544,0.018],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4955,0.03879,0.01602],"object_pos_start":[0.50796,-0.01524,0.12973],"object_to_goal_dist_end":0.29038,"object_to_goal_dist_start":0.24765,"object_z_max":0.12973,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9357.0,"raw_peak_contact_force":1.48413,"subtask_id":"reach_goal","tcp_end":[0.51745,0.05364,0.20578],"tcp_start":[0.48675,-0.01536,0.14097],"tcp_to_object_dist_end":0.1916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4955,0.03879,0.01602],"object_pos_start":[0.4955,0.03879,0.01602],"object_to_goal_dist_end":0.29038,"object_to_goal_dist_start":0.29038,"object_z_max":0.01602,"peak_contact_force":273005.43388,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8299.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53439,0.09235,0.21172],"tcp_start":[0.51745,0.05364,0.20578],"tcp_to_object_dist_end":0.20659,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4955,0.03879,0.01602],"object_pos_start":[0.4955,0.03879,0.01602],"object_to_goal_dist_end":0.29038,"object_to_goal_dist_start":0.29038,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52948,0.09148,0.23512],"tcp_start":[0.53439,0.09235,0.21172],"tcp_to_object_dist_end":0.2279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.4955,0.03879,0.01602],"object_pos_start":[0.4955,0.03879,0.01602],"object_to_goal_dist_end":0.29038,"object_to_goal_dist_start":0.29038,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":524.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52648,0.09095,0.19455],"tcp_start":[0.52948,0.09148,0.23512],"tcp_to_object_dist_end":0.18856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50877,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07265,"approach_object.approach_speed":0.11576,"descend_to_grasp.descend_speed":0.04381,"descend_to_place.place_speed":0.09108,"lift.lift_height":0.1192},"optimized_scores":{"best_composite_score":0.20173,"best_fitness_score":0.63173,"best_task_score":0.30706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.53213,0.09689,-0.00242],"force_p95":0.18567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46428,"mean_force":0.14974,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53561,0.0825,0.16581]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.50938,0.03711,-0.00121],"force_p95":0.4628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66701,"mean_force":0.09129,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49743,0.03803,0.03005]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9635.0,"contact_point_centroid":[0.49787,0.01901,0.0776],"force_p95":0.10736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32979,"mean_force":0.0698,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49485,0.03783,0.07574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9990.0,"contact_point_centroid":[0.49794,0.05667,0.07602],"force_p95":0.10573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32761,"mean_force":0.06832,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49489,0.03783,0.07434]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03939,-0.00214],"force_p95":0.164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24457,"mean_force":0.13362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5002,0.03826,0.02949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4519.0,"contact_point_centroid":[0.51149,0.07188,0.14068],"force_p95":0.14267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.229,"mean_force":0.0949,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50749,0.05379,0.14355]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4304.0,"contact_point_centroid":[0.51084,0.03471,0.14032],"force_p95":0.15895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21982,"mean_force":0.09573,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5067,0.05291,0.14296]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4055.0,"contact_point_centroid":[0.4997,0.01897,0.03099],"force_p95":0.08138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14856,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03817,0.0282]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50276,0.01777,0.21869]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50594,0.03785,0.071]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5323,0.09737,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57018,0.11946,0.15766]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5323,0.09737,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59152,0.14361,0.14819]},{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.5323,0.09737,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58767,0.14259,0.14888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.49966,0.05734,0.03001],"force_p95":0.07398,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08694,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49901,0.03817,0.02821]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1733.0,"contact_point_centroid":[0.53744,0.08387,0.16913],"force_p95":0.01199,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01071,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53696,0.08385,0.16688]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4224.0,"contact_point_centroid":[0.57066,0.11946,0.15989],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57016,0.11944,0.15767]}],"total_contact_groups":17},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5323,0.09737,0.01602],"final_tcp_position":[0.58598,0.14213,0.12689],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.72349,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50767,0.0363,0.13782],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.507,0.03882,0.03689],"tcp_start":[0.50767,0.0363,0.13782],"tcp_to_object_dist_end":0.01222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.0382,0.02553],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15511,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10868.0,"raw_peak_contact_force":0.24457,"tcp_end":[0.49898,0.03816,0.02817],"tcp_start":[0.507,0.03882,0.03689],"tcp_to_object_dist_end":0.01369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.51117,0.03797,0.12167],"object_pos_start":[0.51241,0.0382,0.02553],"object_to_goal_dist_end":0.17943,"object_to_goal_dist_start":0.2135,"object_z_max":0.12156,"peak_contact_force":0.11066,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19764.0,"raw_peak_contact_force":0.66701,"subtask_id":"lift_object","tcp_end":[0.49498,0.03785,0.13532],"tcp_start":[0.49898,0.03816,0.02817],"tcp_to_object_dist_end":0.02118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5323,0.09737,0.01602],"object_pos_start":[0.51117,0.03797,0.12167],"object_to_goal_dist_end":0.17711,"object_to_goal_dist_start":0.17943,"object_z_max":0.12878,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12416.0,"raw_peak_contact_force":1.46428,"subtask_id":"reach_goal","tcp_end":[0.54663,0.09361,0.17461],"tcp_start":[0.49498,0.03785,0.13532],"tcp_to_object_dist_end":0.15928,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5323,0.09737,0.01602],"object_pos_start":[0.5323,0.09737,0.01602],"object_to_goal_dist_end":0.17711,"object_to_goal_dist_start":0.17711,"object_z_max":0.01602,"peak_contact_force":9748.72349,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8224.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59597,0.14473,0.14703],"tcp_start":[0.54663,0.09361,0.17461],"tcp_to_object_dist_end":0.15316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5323,0.09737,0.01602],"object_pos_start":[0.5323,0.09737,0.01602],"object_to_goal_dist_end":0.17711,"object_to_goal_dist_start":0.17711,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58978,0.14312,0.16798],"tcp_start":[0.59597,0.14473,0.14703],"tcp_to_object_dist_end":0.16878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.5323,0.09737,0.01602],"object_pos_start":[0.5323,0.09737,0.01602],"object_to_goal_dist_end":0.17711,"object_to_goal_dist_start":0.17711,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":496.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58598,0.14213,0.12689],"tcp_start":[0.58978,0.14312,0.16798],"tcp_to_object_dist_end":0.13106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```