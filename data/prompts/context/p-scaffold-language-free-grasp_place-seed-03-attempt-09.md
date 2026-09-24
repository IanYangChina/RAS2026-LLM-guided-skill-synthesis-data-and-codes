## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0774 | 0.47 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1243 | 0.45 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2455 | 0.46 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.2493 | 0.46 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1512 | 0.46 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605988) | final destination targets |
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

## Current Skill (Q=0.077) — your mutation base

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
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: transport_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_at_goal
  target_entity: object
  weight: 0.3
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
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
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: grasp_object
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
    orientation:
      mode: keep_current
  subtask_id: grasp_object
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: transport_1
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
    - 0.15
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
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_to_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_goal
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
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
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
  subtask_id: place_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.077
- **task_score** (E): 0.469
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1575 |
| descend_1 | 1.00 | 1.00 | 0.1085 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1853 |
| transport_1 | 1.00 | 0.67 | 0.2380 |
| descend_2 | 0.33 | 0.67 | 0.0000 |
| release_1 | 1.00 | 1.00 | 0.0202 |
| retract_1 | 1.00 | 1.00 | 0.0300 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 27.056 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.148)→(0.505, 0.001, 0.040) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.001, 0.040)→(0.497, 0.001, 0.031) | (0.511, 0.002, 0.026)→(0.511, 0.001, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.143 | 0.193 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.031)→(0.507, 0.001, 0.216) | (0.511, 0.001, 0.026)→(0.520, 0.001, 0.204) | 0.246→0.229 | 1.00 / 34.333 | 0.088 | 0.585 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.001, 0.216)→(0.615, 0.168, 0.276) | (0.520, 0.001, 0.204)→(0.624, 0.172, 0.219) | 0.229→0.082 | 0.67 / 23.000 | 0.053 | 0.187 |
| descend_2 | descend | 0.33 / step_budget | (0.615, 0.168, 0.276)→(0.615, 0.168, 0.276) | (0.624, 0.172, 0.219)→(0.624, 0.172, 0.219) | 0.082→0.082 | 0.67 / 23.000 | 0.054 | 0.000 |
| release_1 | release | 1.00 / step_budget | (0.615, 0.168, 0.276)→(0.612, 0.166, 0.296) | (0.624, 0.172, 0.219)→(0.621, 0.174, 0.014) | 0.082→0.125 | 1.00 / 4.000 | 0.159 | 2.098 |
| retract_1 | retract | 1.00 / step_budget | (0.612, 0.166, 0.296)→(0.619, 0.174, 0.323) | (0.621, 0.174, 0.014)→(0.619, 0.175, 0.020) | 0.125→0.119 | 1.00 / 3.333 | 0.146 | 0.172 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.577
- phase_score: 0.509
- phase_breakdown.place_at_goal_score: 0.026
- phase_breakdown.transport_to_goal_score: 0.749
- phase_breakdown.reach_object_score: 0.672
- phase_breakdown.grasp_object_score: 0.658
- phase_breakdown.lift_object_score: 0.851
- grasp_place_fitness: 0.751

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.751
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.577
- **Median Q (composite search score)**: 0.109
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.355


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.05181,"average_mean_iterations":13.39637,"average_solve_count":386.0,"average_success_count":366.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06974,"descend_1.speed":0.05919,"descend_2.descend_z_offset":0.05347,"descend_2.speed":0.04265,"lift_1.lift_height":0.28215,"lift_1.speed":0.03039,"retract_1.speed":0.0339,"transport_1.speed":0.06608,"transport_1.transport_height":0.09117},"optimized_scores":{"best_composite_score":0.10894,"best_fitness_score":0.73894,"best_task_score":0.51783},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.62223,0.20015,-0.00761],"force_p95":1.31839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89564,"mean_force":0.4059,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61186,0.19215,0.21331]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45604,-0.02536,-0.00141],"force_p95":0.66158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72523,"mean_force":0.20435,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44577,-0.02564,0.02249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18387.0,"contact_point_centroid":[0.44891,-0.0447,0.15472],"force_p95":0.07235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27448,"mean_force":0.04981,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44912,-0.02553,0.15324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18400.0,"contact_point_centroid":[0.44909,-0.00636,0.1588],"force_p95":0.07151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27166,"mean_force":0.04946,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44929,-0.02553,0.15702]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02613,-0.00205],"force_p95":0.13812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19145,"mean_force":0.12701,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44786,-0.02571,0.02246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.6168,0.17461,0.19815],"force_p95":0.07722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14984,"mean_force":0.04598,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61542,0.19369,0.19758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1265.0,"contact_point_centroid":[0.61645,0.21292,0.19804],"force_p95":0.07941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14682,"mean_force":0.04679,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61535,0.19366,0.19743]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48072,-0.01079,0.2261]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.62362,0.19933,-0.00198],"force_p95":0.12572,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12983,"mean_force":0.11969,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61828,0.19881,0.25675]},{"body_a":"world","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45605,-0.02419,0.08574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13420.0,"contact_point_centroid":[0.53415,0.06275,0.2448],"force_p95":0.08769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11878,"mean_force":0.05773,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53369,0.08188,0.24399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14725.0,"contact_point_centroid":[0.5374,0.10488,0.24316],"force_p95":0.07692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10838,"mean_force":0.05243,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53667,0.08592,0.24241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4811.0,"contact_point_centroid":[0.44678,-0.00647,0.02381],"force_p95":0.06768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09236,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44676,-0.02567,0.02144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.44663,-0.04491,0.02329],"force_p95":0.06646,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08664,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44676,-0.02567,0.02144]}],"total_contact_groups":14},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62362,0.19933,0.01602],"final_tcp_position":[0.62614,0.20558,0.29475],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.89564,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46125,-0.02249,0.14895],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2996.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.45424,-0.02594,0.02846],"tcp_start":[0.46125,-0.02249,0.14895],"tcp_to_object_dist_end":0.00498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45842,-0.02566,0.02582],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13548,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11783.0,"raw_peak_contact_force":0.19145,"subtask_id":"grasp_object","tcp_end":[0.44673,-0.02567,0.02141],"tcp_start":[0.45424,-0.02594,0.02846],"tcp_to_object_dist_end":0.01249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.46824,-0.02571,0.2846],"object_pos_start":[0.45842,-0.02566,0.02582],"object_to_goal_dist_end":0.33165,"object_to_goal_dist_start":0.30328,"object_z_max":0.28432,"peak_contact_force":0.078,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36867.0,"raw_peak_contact_force":0.72523,"subtask_id":"lift_object","tcp_end":[0.45544,-0.02556,0.28825],"tcp_start":[0.44673,-0.02567,0.02141],"tcp_to_object_dist_end":0.01331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.62767,0.19367,0.18973],"object_pos_start":[0.46824,-0.02571,0.2846],"object_to_goal_dist_end":0.07704,"object_to_goal_dist_start":0.33165,"object_z_max":0.28477,"peak_contact_force":0.07456,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28145.0,"raw_peak_contact_force":0.11878,"subtask_id":"transport_to_goal","tcp_end":[0.61706,0.19366,0.20152],"tcp_start":[0.45544,-0.02556,0.28825],"tcp_to_object_dist_end":0.01586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.62767,0.19367,0.18973],"object_pos_start":[0.62767,0.19367,0.18973],"object_to_goal_dist_end":0.07704,"object_to_goal_dist_start":0.07704,"peak_contact_force":0.07479,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.61706,0.19366,0.20152],"tcp_start":[0.61706,0.19366,0.20152],"tcp_to_object_dist_end":0.01586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62335,0.19709,0.01293],"object_pos_start":[0.62767,0.19367,0.18973],"object_to_goal_dist_end":0.10203,"object_to_goal_dist_start":0.07704,"object_z_max":0.18973,"peak_contact_force":0.07239,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2607.0,"raw_peak_contact_force":1.89564,"subtask_id":"place_at_goal","tcp_end":[0.61183,0.19214,0.22077],"tcp_start":[0.61706,0.19366,0.20152],"tcp_to_object_dist_end":0.20822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.62362,0.19933,0.01602],"object_pos_start":[0.62335,0.19709,0.01293],"object_to_goal_dist_end":0.09872,"object_to_goal_dist_start":0.10203,"object_z_max":0.01674,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12983,"subtask_id":"place_at_goal","tcp_end":[0.62614,0.20558,0.29475],"tcp_start":[0.61183,0.19214,0.22077],"tcp_to_object_dist_end":0.27881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":101.0,"average_failure_rate":0.27978,"average_mean_iterations":58.1856,"average_solve_count":361.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0608,"descend_1.speed":0.0959,"descend_2.descend_z_offset":0.05798,"descend_2.speed":0.02345,"lift_1.lift_height":0.16685,"lift_1.speed":0.06076,"retract_1.speed":0.04873,"transport_1.speed":0.05601,"transport_1.transport_height":0.20518},"optimized_scores":{"best_composite_score":0.00201,"best_fitness_score":0.63201,"best_task_score":0.31109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.65118,0.16101,-0.00485],"force_p95":1.13581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.65852,"mean_force":0.24683,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63371,0.14101,0.36614]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.54144,0.0005,-0.00137],"force_p95":0.52297,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62656,"mean_force":0.14245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5284,0.00083,0.02836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9019.0,"contact_point_centroid":[0.53413,-0.01818,0.09746],"force_p95":0.09978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30547,"mean_force":0.06283,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.532,0.00073,0.09592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9120.0,"contact_point_centroid":[0.53367,0.01969,0.09461],"force_p95":0.10346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29539,"mean_force":0.06245,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53177,0.00073,0.09294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10618.0,"contact_point_centroid":[0.58308,0.04401,0.25323],"force_p95":0.13644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28111,"mean_force":0.0852,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57956,0.0625,0.25442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11213.0,"contact_point_centroid":[0.58464,0.0822,0.25544],"force_p95":0.13074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21106,"mean_force":0.08114,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58047,0.06383,0.25623]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00099,-0.00203],"force_p95":0.13195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15885,"mean_force":0.12531,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53068,0.00088,0.02866]},{"body_a":"world","body_b":"grasp_target","contact_count":1280.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.13566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51604,0.00044,0.225]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.65087,0.16091,-0.00201],"force_p95":0.12386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12399,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63452,0.14164,0.38419]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53511,0.00096,0.07974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53059,-0.01834,0.02989],"force_p95":0.0761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1135,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00086,0.02722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.5305,0.01994,0.02902],"force_p95":0.06814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09622,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52942,0.00086,0.02722]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65087,0.16091,0.016],"final_tcp_position":[0.63626,0.14337,0.38388],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":40.08616,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":40.08616,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5347,0.00093,0.14749],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53782,0.00101,0.03695],"tcp_start":[0.5347,0.00093,0.14749],"tcp_to_object_dist_end":0.01271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54416,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12991,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15885,"subtask_id":"grasp_object","tcp_end":[0.52939,0.00086,0.02718],"tcp_start":[0.53782,0.00101,0.03695],"tcp_to_object_dist_end":0.01483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.55601,0.00071,0.16438],"object_pos_start":[0.54416,0.00073,0.02588],"object_to_goal_dist_end":0.18405,"object_to_goal_dist_start":0.25052,"object_z_max":0.16413,"peak_contact_force":0.10637,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18226.0,"raw_peak_contact_force":0.62656,"subtask_id":"lift_object","tcp_end":[0.53922,0.00067,0.17338],"tcp_start":[0.52939,0.00086,0.02718],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64636,0.15394,0.23125],"object_pos_start":[0.55601,0.00071,0.16438],"object_to_goal_dist_end":0.04038,"object_to_goal_dist_start":0.18405,"object_z_max":0.32599,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21831.0,"raw_peak_contact_force":0.28111,"subtask_id":"transport_to_goal","tcp_end":[0.63521,0.14148,0.36447],"tcp_start":[0.53922,0.00067,0.17338],"tcp_to_object_dist_end":0.13427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.64636,0.15394,0.23125],"object_pos_start":[0.64636,0.15394,0.23125],"object_to_goal_dist_end":0.04038,"object_to_goal_dist_start":0.04038,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.63521,0.14148,0.36447],"tcp_start":[0.63521,0.14148,0.36447],"tcp_to_object_dist_end":0.13427,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65088,0.16082,0.01597],"object_pos_start":[0.64636,0.15394,0.23125],"object_to_goal_dist_end":0.17518,"object_to_goal_dist_start":0.04038,"object_z_max":0.23125,"peak_contact_force":0.12402,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":560.0,"raw_peak_contact_force":2.65852,"subtask_id":"place_at_goal","tcp_end":[0.63376,0.14097,0.38386],"tcp_start":[0.63521,0.14148,0.36447],"tcp_to_object_dist_end":0.36882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":600.0,"object_pos_end":[0.65087,0.16091,0.016],"object_pos_start":[0.65088,0.16082,0.01597],"object_to_goal_dist_end":0.17515,"object_to_goal_dist_start":0.17518,"object_z_max":0.016,"peak_contact_force":0.12333,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12399,"subtask_id":"place_at_goal","tcp_end":[0.63626,0.14337,0.38388],"tcp_start":[0.63376,0.14097,0.38386],"tcp_to_object_dist_end":0.36858,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":32.0,"average_failure_rate":0.11636,"average_mean_iterations":26.16364,"average_solve_count":275.0,"average_success_count":243.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07232,"descend_1.speed":0.05136,"descend_2.descend_z_offset":0.05317,"descend_2.speed":0.0677,"lift_1.lift_height":0.18011,"lift_1.speed":0.0434,"retract_1.speed":0.06524,"transport_1.speed":0.06482,"transport_1.transport_height":0.16933},"optimized_scores":{"best_composite_score":0.1214,"best_fitness_score":0.7514,"best_task_score":0.57735},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.57826,0.16395,-0.01106],"force_p95":1.65447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74111,"mean_force":0.61341,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58988,0.16639,0.27831]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.52716,0.02844,-0.00154],"force_p95":0.38137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40225,"mean_force":0.13167,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51458,0.02865,0.04571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11169.0,"contact_point_centroid":[0.51919,0.04786,0.1146],"force_p95":0.07995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27087,"mean_force":0.05183,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51863,0.02877,0.11246]},{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.58759,0.16427,-0.00475],"force_p95":0.19506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26242,"mean_force":0.11542,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59155,0.16836,0.28618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9784.0,"contact_point_centroid":[0.51942,0.00959,0.1152],"force_p95":0.08164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24332,"mean_force":0.05699,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5187,0.02877,0.11313]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03062,-0.00217],"force_p95":0.16798,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23011,"mean_force":0.13478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51677,0.0288,0.04587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":990.0,"contact_point_centroid":[0.5951,0.18649,0.25927],"force_p95":0.08751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22034,"mean_force":0.05417,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59256,0.16752,0.25973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":946.0,"contact_point_centroid":[0.5945,0.14856,0.25864],"force_p95":0.08632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18592,"mean_force":0.05396,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59254,0.16751,0.25968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10416.0,"contact_point_centroid":[0.55913,0.07837,0.22225],"force_p95":0.08519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15968,"mean_force":0.05573,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55795,0.09736,0.22189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10370.0,"contact_point_centroid":[0.55982,0.11624,0.22261],"force_p95":0.08387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15591,"mean_force":0.05572,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5579,0.09726,0.22184]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5103,0.01264,0.22518]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4559.0,"contact_point_centroid":[0.51654,0.00955,0.04701],"force_p95":0.07446,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12749,"mean_force":0.04706,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51557,0.02872,0.04449]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52208,0.02816,0.08469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5058.0,"contact_point_centroid":[0.51665,0.04803,0.04627],"force_p95":0.07519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07773,"mean_force":0.04436,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51558,0.02872,0.0445]}],"total_contact_groups":14},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58182,0.16445,0.02934],"final_tcp_position":[0.59445,0.1719,0.29079],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":40.9591,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":40.9591,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52285,0.02629,0.14779],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.52356,0.02924,0.05377],"tcp_start":[0.52285,0.02629,0.14779],"tcp_to_object_dist_end":0.02865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53049,0.02938,0.02541],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1622,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11417.0,"raw_peak_contact_force":0.23011,"subtask_id":"grasp_object","tcp_end":[0.51554,0.02872,0.04446],"tcp_start":[0.52356,0.02924,0.05377],"tcp_to_object_dist_end":0.02422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.53479,0.02941,0.16287],"object_pos_start":[0.53049,0.02938,0.02541],"object_to_goal_dist_end":0.17236,"object_to_goal_dist_start":0.18478,"object_z_max":0.16262,"peak_contact_force":0.07967,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21051.0,"raw_peak_contact_force":0.40225,"subtask_id":"lift_object","tcp_end":[0.52576,0.02909,0.18633],"tcp_start":[0.51554,0.02872,0.04446],"tcp_to_object_dist_end":0.02514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.59864,0.16763,0.23529],"object_pos_start":[0.53479,0.02941,0.16287],"object_to_goal_dist_end":0.12771,"object_to_goal_dist_start":0.17236,"object_z_max":0.23519,"peak_contact_force":0.08578,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20786.0,"raw_peak_contact_force":0.15968,"subtask_id":"transport_to_goal","tcp_end":[0.59378,0.16744,0.263],"tcp_start":[0.52576,0.02909,0.18633],"tcp_to_object_dist_end":0.02813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.59864,0.16763,0.23529],"object_pos_start":[0.59864,0.16763,0.23529],"object_to_goal_dist_end":0.12771,"object_to_goal_dist_start":0.12771,"peak_contact_force":0.08584,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.59378,0.16744,0.263],"tcp_start":[0.59378,0.16744,0.263],"tcp_to_object_dist_end":0.02813,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58824,0.1652,0.01164],"object_pos_start":[0.59864,0.16763,0.23529],"object_to_goal_dist_end":0.09827,"object_to_goal_dist_start":0.12771,"object_z_max":0.2353,"peak_contact_force":0.28102,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2064.0,"raw_peak_contact_force":1.74111,"subtask_id":"place_at_goal","tcp_end":[0.58986,0.16638,0.28362],"tcp_start":[0.59378,0.16744,0.263],"tcp_to_object_dist_end":0.27198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.58182,0.16445,0.02934],"object_pos_start":[0.58824,0.1652,0.01164],"object_to_goal_dist_end":0.0824,"object_to_goal_dist_start":0.09827,"object_z_max":0.02985,"peak_contact_force":0.19102,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":118.0,"raw_peak_contact_force":0.26242,"subtask_id":"place_at_goal","tcp_end":[0.59445,0.1719,0.29079],"tcp_start":[0.58986,0.16638,0.28362],"tcp_to_object_dist_end":0.26186,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```