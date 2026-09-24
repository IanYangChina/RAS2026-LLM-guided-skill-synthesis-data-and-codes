## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.1582 | 0.24 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1127 | 0.25 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1085 | 0.24 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | -0.0692 | 0.22 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.1643 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.158) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_objective
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: placement_objective
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: approach_objective
- id: descend_to_grasp
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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  guards:
  - id: grasp_closed
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_to_goal
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
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: placement_objective
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_closed, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.158
- **task_score** (E): 0.240
- **fitness_score**: 0.488  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2168 |
| descend_to_grasp | 1.00 | 1.00 | 0.0241 |
| grasp | 1.00 | 1.00 | 0.0120 |
| lift | 1.00 | 1.00 | 0.0670 |
| transport_to_goal | 0.00 | 0.67 | 0.0024 |
| descend_to_place | 0.33 | 1.00 | 0.1122 |
| release | 1.00 | 1.00 | 0.0233 |
| retract | 1.00 | 1.00 | 0.0864 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.088) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.088)→(0.506, 0.002, 0.064) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.506, 0.002, 0.064)→(0.498, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 27.667 | 0.143 | 0.188 |
| lift | lift | 1.00 / step_budget | (0.496, 0.006, 0.079)→(0.502, 0.007, 0.145) | (0.511, 0.002, 0.026)→(0.507, 0.009, 0.083) | 0.246→0.223 | 1.00 / 13.667 | 90997.042 | 0.381 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.503, 0.009, 0.146)→(0.503, 0.011, 0.146) | (0.507, 0.009, 0.083)→(0.508, 0.011, 0.082) | 0.223→0.220 | 0.67 / 4.000 | 3249.532 | 0.194 |
| descend_to_place | descend | 0.33 / step_budget | (0.503, 0.011, 0.146)→(0.563, 0.103, 0.151) | (0.510, 0.015, 0.080)→(0.520, 0.029, 0.016) | 0.216→0.229 | 1.00 / 8.000 | 3249.602 | 0.919 |
| release | release | 1.00 / step_budget | (0.563, 0.103, 0.151)→(0.557, 0.102, 0.173) | (0.520, 0.029, 0.016)→(0.520, 0.029, 0.016) | 0.229→0.229 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.557, 0.102, 0.173)→(0.555, 0.101, 0.259) | (0.520, 0.029, 0.016)→(0.520, 0.029, 0.016) | 0.229→0.229 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.387
- phase_score: 0.271
- phase_breakdown.approach_objective_score: 0.820
- phase_breakdown.placement_objective_score: 0.036
- grasp_place_fitness: 0.646

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.646
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.387
- **Median Q (composite search score)**: 0.222
- **K-run variance**: 0.0259
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.232


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36111,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_offset_z":0.02697,"lift.lift_height":0.11163,"transport_to_goal.transport_speed":0.10111},"optimized_scores":{"best_composite_score":-0.06262,"best_fitness_score":0.26738,"best_task_score":0.13569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1710.0,"contact_point_centroid":[0.44509,-0.00966,-0.00223],"force_p95":0.31615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5606,"mean_force":0.13731,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44956,-0.02309,0.10942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2211.0,"contact_point_centroid":[0.44604,-0.04361,0.06465],"force_p95":0.12328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25089,"mean_force":0.07997,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44614,-0.02518,0.06886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.44566,-0.0065,0.06372],"force_p95":0.14813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24975,"mean_force":0.0937,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44608,-0.02518,0.06813]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4586,-0.02628,-0.00208],"force_p95":0.14686,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19803,"mean_force":0.12866,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44834,-0.02527,0.05866]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01207,0.19433]},{"body_a":"world","body_b":"grasp_target","contact_count":360.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45544,-0.02493,0.07765]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.44344,-0.00459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44217,-0.01014,0.13009]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.44344,-0.00459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.4855,0.04437,0.12786]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44344,-0.00459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5212,0.09035,0.13239]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.44344,-0.00459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51625,0.08947,0.1956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3148.0,"contact_point_centroid":[0.44541,-0.00633,0.05364],"force_p95":0.08588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09597,"mean_force":0.06634,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44729,-0.02523,0.05763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3474.0,"contact_point_centroid":[0.44572,-0.0441,0.05369],"force_p95":0.08317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08349,"mean_force":0.06102,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4473,-0.02523,0.05763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1304.0,"contact_point_centroid":[0.45043,-0.02231,0.12183],"force_p95":0.01213,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01537,"mean_force":0.01082,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45016,-0.02231,0.11955]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4218.0,"contact_point_centroid":[0.48596,0.04455,0.13014],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01299,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.48566,0.04455,0.12787]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.52431,0.0909,0.12923],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5241,0.0909,0.12695]},{"body_a":"left_finger","body_b":"right_finger","contact_count":10.0,"contact_point_centroid":[0.44264,-0.01015,0.13386],"force_p95":0.00955,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.00955,"mean_force":0.00953,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44217,-0.01014,0.13009]}],"total_contact_groups":16},"final_pose_error":0.01291,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.44344,-0.00459,0.01602],"final_tcp_position":[0.51638,0.08948,0.24063],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":272990.87356,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.45734,-0.02446,0.08964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":360.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45459,-0.02549,0.06492],"tcp_start":[0.45734,-0.02446,0.08964],"tcp_to_object_dist_end":0.03911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45853,-0.02564,0.02571],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30324,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14554,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8422.0,"raw_peak_contact_force":0.19803,"tcp_end":[0.44727,-0.02523,0.0576],"tcp_start":[0.45459,-0.02549,0.06492],"tcp_to_object_dist_end":0.03382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":631.0,"n_steps_budget":600.0,"object_pos_end":[0.44344,-0.00459,0.01602],"object_pos_start":[0.45853,-0.02564,0.02571],"object_to_goal_dist_end":0.2996,"object_to_goal_dist_start":0.30324,"object_z_max":0.04387,"peak_contact_force":272990.87356,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7129.0,"raw_peak_contact_force":0.5606,"tcp_end":[0.44217,-0.01017,0.13009],"tcp_start":[0.4435,-0.01132,0.1304],"tcp_to_object_dist_end":0.11422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.44344,-0.00459,0.01602],"object_pos_start":[0.44344,-0.00459,0.01602],"object_to_goal_dist_end":0.2996,"object_to_goal_dist_start":0.2996,"object_z_max":0.01602,"peak_contact_force":9748.5605,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.44213,-0.01006,0.13008],"tcp_start":[0.44216,-0.01011,0.1301],"tcp_to_object_dist_end":0.1142,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44344,-0.00459,0.01602],"object_pos_start":[0.44344,-0.00459,0.01602],"object_to_goal_dist_end":0.2996,"object_to_goal_dist_start":0.2996,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8218.0,"raw_peak_contact_force":0.12263,"subtask_id":"placement_objective","tcp_end":[0.52559,0.09103,0.1291],"tcp_start":[0.44213,-0.01006,0.13008],"tcp_to_object_dist_end":0.16935,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44344,-0.00459,0.01602],"object_pos_start":[0.44344,-0.00459,0.01602],"object_to_goal_dist_end":0.2996,"object_to_goal_dist_start":0.2996,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51947,0.09003,0.15315],"tcp_start":[0.52559,0.09103,0.1291],"tcp_to_object_dist_end":0.18314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.44344,-0.00459,0.01602],"object_pos_start":[0.44344,-0.00459,0.01602],"object_to_goal_dist_end":0.2996,"object_to_goal_dist_start":0.2996,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51638,0.08948,0.24063],"tcp_start":[0.51947,0.09003,0.15315],"tcp_to_object_dist_end":0.2542,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71014,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_offset_z":0.03935,"lift.lift_height":0.13434,"transport_to_goal.transport_speed":0.09811},"optimized_scores":{"best_composite_score":0.22157,"best_fitness_score":0.55157,"best_task_score":0.19703},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3744.0,"contact_point_centroid":[0.56767,0.00857,-0.00219],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32375,"mean_force":0.13428,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56436,0.04506,0.16379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5448.0,"contact_point_centroid":[0.53566,-0.01739,0.09267],"force_p95":0.13863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28379,"mean_force":0.10313,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53196,0.00081,0.09612]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.54309,0.0006,-0.00111],"force_p95":0.20649,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27063,"mean_force":0.04636,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52821,0.00084,0.05502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5520.0,"contact_point_centroid":[0.53585,0.01902,0.093],"force_p95":0.13676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26427,"mean_force":0.10162,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.532,0.00081,0.09628]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":283.0,"contact_point_centroid":[0.54618,-0.0152,0.14411],"force_p95":0.17483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21775,"mean_force":0.10409,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53954,0.00253,0.14825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.54608,0.02008,0.14411],"force_p95":0.18076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19532,"mean_force":0.12853,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53947,0.00215,0.1481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.54712,-0.01115,0.14206],"force_p95":0.16822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16822,"mean_force":0.02724,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5399,0.00506,0.14915]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54432,0.00109,-0.00203],"force_p95":0.13244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15345,"mean_force":0.1252,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5306,0.00089,0.05479]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54431,0.00113,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51744,0.00049,0.19253]},{"body_a":"world","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53687,0.00099,0.07551]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56773,0.00865,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58109,0.07378,0.18055]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.56773,0.00865,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57669,0.0731,0.24174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.53066,-0.01788,0.05063],"force_p95":0.09721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09981,"mean_force":0.07619,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,0.00087,0.05336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2940.0,"contact_point_centroid":[0.53026,0.01955,0.05038],"force_p95":0.09174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09184,"mean_force":0.06993,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5294,0.00087,0.05336]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3663.0,"contact_point_centroid":[0.5664,0.04745,0.16717],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01059,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56601,0.04745,0.16496]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.5841,0.07426,0.17835],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.58382,0.07426,0.17623]}],"total_contact_groups":16},"final_pose_error":0.01435,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56773,0.00865,0.01602],"final_tcp_position":[0.57694,0.07311,0.28646],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.56046,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.5373,0.00099,0.08712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":332.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53766,0.00101,0.06343],"tcp_start":[0.5373,0.00099,0.08712],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54423,0.00089,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13143,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7412.0,"raw_peak_contact_force":0.15345,"tcp_end":[0.52937,0.00087,0.05332],"tcp_start":[0.53766,0.00101,0.06343],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.5456,0.00106,0.11145],"object_pos_start":[0.54423,0.00089,0.02588],"object_to_goal_dist_end":0.2035,"object_to_goal_dist_start":0.25039,"object_z_max":0.11133,"peak_contact_force":0.13146,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11119.0,"raw_peak_contact_force":0.28379,"tcp_end":[0.53923,0.00082,0.14739],"tcp_start":[0.52937,0.00087,0.05332],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":39.0,"n_steps_budget":1000.0,"object_pos_end":[0.548,0.00304,0.11085],"object_pos_start":[0.5456,0.00106,0.11145],"object_to_goal_dist_end":0.20101,"object_to_goal_dist_start":0.2035,"object_z_max":0.11211,"peak_contact_force":0.03597,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":0.21775,"tcp_end":[0.53989,0.00491,0.14917],"tcp_start":[0.53989,0.00441,0.14905],"tcp_to_object_dist_end":0.03921,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56773,0.00865,0.01602],"object_pos_start":[0.54876,0.00268,0.10921],"object_to_goal_dist_end":0.24366,"object_to_goal_dist_start":0.20157,"object_z_max":0.10921,"peak_contact_force":9748.56046,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7423.0,"raw_peak_contact_force":1.32375,"subtask_id":"placement_objective","tcp_end":[0.58511,0.07423,0.17874],"tcp_start":[0.53989,0.00491,0.14917],"tcp_to_object_dist_end":0.17629,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56773,0.00865,0.01602],"object_pos_start":[0.56773,0.00865,0.01602],"object_to_goal_dist_end":0.24366,"object_to_goal_dist_start":0.24366,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5795,0.07352,0.20058],"tcp_start":[0.58511,0.07423,0.17874],"tcp_to_object_dist_end":0.19598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.56773,0.00865,0.01602],"object_pos_start":[0.56773,0.00865,0.01602],"object_to_goal_dist_end":0.24366,"object_to_goal_dist_start":0.24366,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57694,0.07311,0.28646],"tcp_start":[0.5795,0.07352,0.20058],"tcp_to_object_dist_end":0.27817,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73288,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_place.place_offset_z":0.04074,"lift.lift_height":0.14515,"transport_to_goal.transport_speed":0.10882},"optimized_scores":{"best_composite_score":0.31578,"best_fitness_score":0.64578,"best_task_score":0.38734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.54928,0.08346,-0.00221],"force_p95":0.12398,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30984,"mean_force":0.13266,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55679,0.10082,0.14829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6361.0,"contact_point_centroid":[0.52244,0.01089,0.09901],"force_p95":0.1319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29979,"mean_force":0.09806,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51867,0.02918,0.10254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6428.0,"contact_point_centroid":[0.52269,0.04748,0.1003],"force_p95":0.13563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27621,"mean_force":0.09724,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51885,0.02919,0.10386]},{"body_a":"world","body_b":"grasp_target","contact_count":155.0,"contact_point_centroid":[0.52923,0.02869,-0.0012],"force_p95":0.20745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26768,"mean_force":0.04607,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51497,0.0291,0.05604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":434.0,"contact_point_centroid":[0.53313,0.0499,0.15421],"force_p95":0.20934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2411,"mean_force":0.11777,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52637,0.03299,0.15871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":230.0,"contact_point_centroid":[0.53268,0.01276,0.1538],"force_p95":0.16293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22017,"mean_force":0.11928,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52595,0.03099,0.15834]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.0307,-0.00212],"force_p95":0.15773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21168,"mean_force":0.13108,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51735,0.02927,0.05552]},{"body_a":"world","body_b":"grasp_target","contact_count":2736.0,"contact_point_centroid":[0.5305,0.03079,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51101,0.0142,0.19279]},{"body_a":"world","body_b":"grasp_target","contact_count":336.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52372,0.02914,0.07592]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54936,0.08349,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57502,0.14265,0.14561]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.54936,0.08349,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57018,0.14132,0.2067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2449.0,"contact_point_centroid":[0.51778,0.01051,0.0514],"force_p95":0.10465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11401,"mean_force":0.08158,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51618,0.0292,0.05415]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2822.0,"contact_point_centroid":[0.51727,0.04787,0.05084],"force_p95":0.10011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10026,"mean_force":0.0732,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51619,0.0292,0.05416]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3747.0,"contact_point_centroid":[0.55876,0.10372,0.15012],"force_p95":0.01113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01568,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55828,0.10371,0.14794]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57847,0.1435,0.14343],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57796,0.14349,0.14134]}],"total_contact_groups":15},"final_pose_error":0.01452,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.54936,0.08349,0.01602],"final_tcp_position":[0.57038,0.14134,0.25141],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.30984,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_objective","tcp_end":[0.52437,0.02866,0.08754],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52427,0.02971,0.06376],"tcp_start":[0.52437,0.02866,0.08754],"tcp_to_object_dist_end":0.03826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02975,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1844,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15252,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7071.0,"raw_peak_contact_force":0.21168,"tcp_end":[0.51615,0.0292,0.05411],"tcp_start":[0.52427,0.02971,0.06376],"tcp_to_object_dist_end":0.03189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53227,0.02976,0.12112],"object_pos_start":[0.53047,0.02975,0.02562],"object_to_goal_dist_end":0.16467,"object_to_goal_dist_start":0.1844,"object_z_max":0.12101,"peak_contact_force":0.12171,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12944.0,"raw_peak_contact_force":0.29979,"tcp_end":[0.52573,0.02946,0.15818],"tcp_start":[0.51615,0.0292,0.05411],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.53351,0.03357,0.12057],"object_pos_start":[0.53227,0.02976,0.12112],"object_to_goal_dist_end":0.16065,"object_to_goal_dist_start":0.16467,"object_z_max":0.12117,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":0.2411,"tcp_end":[0.52787,0.03921,0.16016],"tcp_start":[0.52625,0.03308,0.15855],"tcp_to_object_dist_end":0.04039,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54936,0.08349,0.01602],"object_pos_start":[0.53678,0.04616,0.11413],"object_to_goal_dist_end":0.14227,"object_to_goal_dist_start":0.14753,"object_z_max":0.11413,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7503.0,"raw_peak_contact_force":1.30984,"subtask_id":"placement_objective","tcp_end":[0.57945,0.14372,0.14397],"tcp_start":[0.52787,0.03921,0.16016],"tcp_to_object_dist_end":0.14458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54936,0.08349,0.01602],"object_pos_start":[0.54936,0.08349,0.01602],"object_to_goal_dist_end":0.14227,"object_to_goal_dist_start":0.14227,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57328,0.14216,0.16561],"tcp_start":[0.57945,0.14372,0.14397],"tcp_to_object_dist_end":0.16245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.54936,0.08349,0.01602],"object_pos_start":[0.54936,0.08349,0.01602],"object_to_goal_dist_end":0.14227,"object_to_goal_dist_start":0.14227,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57038,0.14134,0.25141],"tcp_start":[0.57328,0.14216,0.16561],"tcp_to_object_dist_end":0.2433,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```