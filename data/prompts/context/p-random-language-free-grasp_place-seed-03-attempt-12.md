## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0611 | 0.46 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0616 | 0.46 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0002 | 0.37 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1009 | 0.27 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2004 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.46 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.061) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: place_at_goal
  target_entity: object
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
    - 0.12
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_grasp
- id: descend_to_object
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
    - 0.025
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
- id: close_gripper
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
- id: lift_object
  type: lift
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_offset_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: approach_grasp
- id: move_to_goal
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
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    goal_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_at_goal
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
    - 0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    place_offset_z:
      type: scalar
      range:
      - 0.005
      - 0.035
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
- id: release_object
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
- id: retract_after_place
  type: retract
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
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.025], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **close_gripper** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_offset_z: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.061
- **task_score** (E): 0.456
- **fitness_score**: 0.691  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1383 |
| descend_to_object | 1.00 | 1.00 | 0.1126 |
| close_gripper | 1.00 | 1.00 | 0.0127 |
| lift_object | 1.00 | 1.00 | 0.1216 |
| move_to_goal | 1.00 | 0.67 | 0.1903 |
| descend_to_place | 1.00 | 1.00 | 0.0710 |
| release_object | 1.00 | 1.00 | 0.0202 |
| retract_after_place | 1.00 | 1.00 | 0.0713 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 19.490 | 0.123 |
| close_gripper | grasp | 1.00 / step_budget | (0.506, 0.002, 0.055)→(0.498, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 41.667 | 0.145 | 0.195 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.046)→(0.506, 0.002, 0.167) | (0.511, 0.002, 0.026)→(0.522, 0.002, 0.142) | 0.246→0.214 | 1.00 / 23.333 | 0.111 | 0.415 |
| move_to_goal | approach | 1.00 / step_budget | (0.506, 0.002, 0.167)→(0.604, 0.146, 0.234) | (0.522, 0.002, 0.142)→(0.616, 0.155, 0.076) | 0.214→0.111 | 0.67 / 6.000 | 0.646 | 0.960 |
| descend_to_place | descend | 1.00 / step_budget | (0.604, 0.146, 0.234)→(0.618, 0.172, 0.169) | (0.616, 0.155, 0.076)→(0.628, 0.177, 0.016) | 0.111→0.122 | 1.00 / 8.000 | 3249.667 | 1.752 |
| release_object | release | 1.00 / step_budget | (0.618, 0.172, 0.169)→(0.612, 0.171, 0.188) | (0.628, 0.177, 0.016)→(0.628, 0.177, 0.016) | 0.122→0.122 | 1.00 / 4.000 | 0.123 | 0.124 |
| retract_after_place | retract | 1.00 / step_budget | (0.612, 0.171, 0.188)→(0.621, 0.179, 0.259) | (0.628, 0.177, 0.016)→(0.628, 0.177, 0.016) | 0.122→0.122 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.539
- phase_score: 0.195
- phase_breakdown.place_at_goal_score: 0.110
- phase_breakdown.approach_grasp_score: 0.392
- grasp_place_fitness: 0.733

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.539
- **Median Q (composite search score)**: 0.091
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26667,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.34286,"descend_to_object.descend_speed":0.17597,"descend_to_object.grasp_offset_z":0.01047,"descend_to_place.descend_place_speed":0.13699,"descend_to_place.place_offset_z":0.01761,"lift_object.lift_offset_z":0.15611,"lift_object.lift_speed":0.10821,"move_to_goal.goal_speed":0.2167,"retract_after_place.retract_speed":0.15974},"optimized_scores":{"best_composite_score":0.09103,"best_fitness_score":0.72103,"best_task_score":0.5184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":397.0,"contact_point_centroid":[0.63803,0.21313,-0.00466],"force_p95":0.9117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81772,"mean_force":0.23693,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61565,0.19187,0.15851]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2758.0,"contact_point_centroid":[0.52576,0.04625,0.18399],"force_p95":0.18887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50011,"mean_force":0.10858,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52289,0.06469,0.1864]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.45668,-0.02495,-0.00144],"force_p95":0.36004,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37541,"mean_force":0.08181,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44718,-0.02507,0.04959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.60159,0.15511,0.21061],"force_p95":0.30489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36741,"mean_force":0.17912,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60377,0.17263,0.21597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":205.0,"contact_point_centroid":[0.60132,0.19021,0.20711],"force_p95":0.2531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35077,"mean_force":0.14205,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6043,0.17419,0.21235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2525.0,"contact_point_centroid":[0.52705,0.08449,0.18411],"force_p95":0.17292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32358,"mean_force":0.10642,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52415,0.06637,0.18687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5793.0,"contact_point_centroid":[0.4507,-0.00603,0.10167],"force_p95":0.10508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28021,"mean_force":0.0647,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4493,-0.02511,0.10093]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6482.0,"contact_point_centroid":[0.45044,-0.0441,0.10164],"force_p95":0.09858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2792,"mean_force":0.0592,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4493,-0.02511,0.1008]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.0021],"force_p95":0.15166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20763,"mean_force":0.13022,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44916,-0.02515,0.04921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.44903,-0.0059,0.0491],"force_p95":0.07964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14738,"mean_force":0.05214,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44814,-0.02511,0.04822]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48136,-0.01058,0.23556]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63838,0.21274,-0.00198],"force_p95":0.12444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1247,"mean_force":0.12291,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.616,0.19809,0.13908]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45835,-0.02362,0.11267]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.63838,0.21274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61856,0.20097,0.19539]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4961.0,"contact_point_centroid":[0.4482,-0.0442,0.04925],"force_p95":0.07126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07344,"mean_force":0.04413,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44815,-0.02511,0.04823]},{"body_a":"left_finger","body_b":"right_finger","contact_count":184.0,"contact_point_centroid":[0.61873,0.19614,0.15035],"force_p95":0.01565,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01211,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61862,0.19613,0.14806]}],"total_contact_groups":17},"final_pose_error":0.02965,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63838,0.21274,0.01602],"final_tcp_position":[0.62464,0.20514,0.23514],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.81772,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.46241,-0.022,0.16889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":848.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45578,-0.02537,0.05598],"tcp_start":[0.46241,-0.022,0.16889],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02546,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30313,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14872,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.20763,"tcp_end":[0.44812,-0.02511,0.0482],"tcp_start":[0.45578,-0.02537,0.05598],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":346.0,"n_steps_budget":780.0,"object_pos_end":[0.46852,-0.02564,0.13695],"object_pos_start":[0.45851,-0.02546,0.02563],"object_to_goal_dist_end":0.28518,"object_to_goal_dist_start":0.30313,"object_z_max":0.13667,"peak_contact_force":0.10572,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12349.0,"raw_peak_contact_force":0.37541,"subtask_id":"approach_grasp","tcp_end":[0.45406,-0.02525,0.16227],"tcp_start":[0.44812,-0.02511,0.0482],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.60398,0.17012,0.1774],"object_pos_start":[0.46852,-0.02564,0.13695],"object_to_goal_dist_end":0.07836,"object_to_goal_dist_start":0.28518,"object_z_max":0.17734,"peak_contact_force":0.20378,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5283.0,"raw_peak_contact_force":0.50011,"subtask_id":"place_at_goal","tcp_end":[0.60304,0.17102,0.21628],"tcp_start":[0.45406,-0.02525,0.16227],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.6384,0.21276,0.0163],"object_pos_start":[0.60398,0.17012,0.1774],"object_to_goal_dist_end":0.09827,"object_to_goal_dist_start":0.07836,"object_z_max":0.17741,"peak_contact_force":0.12403,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":850.0,"raw_peak_contact_force":1.81772,"tcp_end":[0.62103,0.19961,0.13973],"tcp_start":[0.60304,0.17102,0.21628],"tcp_to_object_dist_end":0.12533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63838,0.21274,0.01602],"object_pos_start":[0.6384,0.21276,0.0163],"object_to_goal_dist_end":0.09855,"object_to_goal_dist_start":0.09827,"object_z_max":0.0163,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.1247,"tcp_end":[0.61428,0.19742,0.1585],"tcp_start":[0.62103,0.19961,0.13973],"tcp_to_object_dist_end":0.14532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":181.0,"n_steps_budget":600.0,"object_pos_end":[0.63838,0.21274,0.01602],"object_pos_start":[0.63838,0.21274,0.01602],"object_to_goal_dist_end":0.09855,"object_to_goal_dist_start":0.09855,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":724.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62464,0.20514,0.23514],"tcp_start":[0.61428,0.19742,0.1585],"tcp_to_object_dist_end":0.21969,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19841,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.36066,"descend_to_object.descend_speed":0.22919,"descend_to_object.grasp_offset_z":0.01028,"descend_to_place.descend_place_speed":0.09761,"descend_to_place.place_offset_z":0.02709,"lift_object.lift_offset_z":0.15578,"lift_object.lift_speed":0.12799,"move_to_goal.goal_speed":0.23001,"retract_after_place.retract_speed":0.296},"optimized_scores":{"best_composite_score":-0.01078,"best_fitness_score":0.61922,"best_task_score":0.31085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.66907,0.14969,-0.00352],"force_p95":1.96143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99019,"mean_force":1.67614,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.62727,0.12704,0.27444]},{"body_a":"world","body_b":"grasp_target","contact_count":516.0,"contact_point_centroid":[0.6436,0.15096,-0.00424],"force_p95":0.74768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63982,"mean_force":0.19393,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63343,0.13863,0.25243]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54238,0.00081,-0.00132],"force_p95":0.39815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42476,"mean_force":0.08259,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52868,0.00084,0.04565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":986.0,"contact_point_centroid":[0.56187,0.00524,0.1823],"force_p95":0.19036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36566,"mean_force":0.10416,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55544,0.0239,0.18187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5456.0,"contact_point_centroid":[0.53609,-0.01805,0.10064],"force_p95":0.11199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30927,"mean_force":0.07561,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53224,0.00076,0.09827]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5588.0,"contact_point_centroid":[0.5357,0.01958,0.09839],"force_p95":0.11134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28176,"mean_force":0.07423,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53206,0.00077,0.09622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.56404,0.04521,0.18454],"force_p95":0.16518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25018,"mean_force":0.09162,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55742,0.02677,0.18435]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00104,-0.00203],"force_p95":0.13201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15378,"mean_force":0.12535,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.53088,0.00089,0.04571]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51606,0.00045,0.23431]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64369,0.15107,-0.00199],"force_p95":0.12302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12361,"mean_force":0.12266,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6357,0.14816,0.22575]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53545,0.00096,0.11135]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.64369,0.15107,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.63833,0.15138,0.277]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4124.0,"contact_point_centroid":[0.53066,-0.01833,0.04706],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10077,"mean_force":0.05172,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00087,0.04433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4869.0,"contact_point_centroid":[0.53064,0.01994,0.04619],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09364,"mean_force":0.04475,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00087,0.04433]},{"body_a":"left_finger","body_b":"right_finger","contact_count":380.0,"contact_point_centroid":[0.6353,0.14143,0.24646],"force_p95":0.01491,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01128,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63496,0.14142,0.24424]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.6381,0.14894,0.22463],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63787,0.14892,0.22239]}],"total_contact_groups":16},"final_pose_error":0.02976,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64369,0.15107,0.01602],"final_tcp_position":[0.64339,0.15535,0.31178],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.75381,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.53434,0.00092,0.16718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":58.2253,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5384,0.00102,0.05497],"tcp_start":[0.53434,0.00092,0.16718],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25048,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13046,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15378,"tcp_end":[0.52967,0.00087,0.04429],"tcp_start":[0.5384,0.00102,0.05497],"tcp_to_object_dist_end":0.02347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":393.0,"n_steps_budget":690.0,"object_pos_end":[0.55496,0.0008,0.13852],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.18997,"object_to_goal_dist_start":0.25048,"object_z_max":0.13828,"peak_contact_force":0.11834,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11122.0,"raw_peak_contact_force":0.42476,"subtask_id":"approach_grasp","tcp_end":[0.53912,0.00072,0.16233],"tcp_start":[0.52967,0.00087,0.04429],"tcp_to_object_dist_end":0.02859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.64715,0.14835,0.01379],"object_pos_start":[0.55496,0.0008,0.13852],"object_to_goal_dist_end":0.17758,"object_to_goal_dist_start":0.18997,"object_z_max":0.18618,"peak_contact_force":1.73339,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2118.0,"raw_peak_contact_force":1.99019,"subtask_id":"place_at_goal","tcp_end":[0.62831,0.1286,0.27584],"tcp_start":[0.53912,0.00072,0.16233],"tcp_to_object_dist_end":0.26347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":130.0,"n_steps_budget":1000.0,"object_pos_end":[0.64369,0.15106,0.01601],"object_pos_start":[0.64715,0.14835,0.01379],"object_to_goal_dist_end":0.17528,"object_to_goal_dist_start":0.17758,"object_z_max":0.01668,"peak_contact_force":9748.75381,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":896.0,"raw_peak_contact_force":1.63982,"tcp_end":[0.63946,0.14892,0.22667],"tcp_start":[0.62831,0.1286,0.27584],"tcp_to_object_dist_end":0.21071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64369,0.15107,0.01602],"object_pos_start":[0.64369,0.15106,0.01601],"object_to_goal_dist_end":0.17527,"object_to_goal_dist_start":0.17528,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12361,"tcp_end":[0.63446,0.14774,0.24502],"tcp_start":[0.63946,0.14892,0.22667],"tcp_to_object_dist_end":0.22922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":600.0,"object_pos_end":[0.64369,0.15107,0.01602],"object_pos_start":[0.64369,0.15107,0.01602],"object_to_goal_dist_end":0.17527,"object_to_goal_dist_start":0.17527,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":632.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64339,0.15535,0.31178],"tcp_start":[0.63446,0.14774,0.24502],"tcp_to_object_dist_end":0.29579,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94853,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.42075,"descend_to_object.descend_speed":0.23546,"descend_to_object.grasp_offset_z":0.01001,"descend_to_place.descend_place_speed":0.06032,"descend_to_place.place_offset_z":0.0254,"lift_object.lift_offset_z":0.17044,"lift_object.lift_speed":0.13181,"move_to_goal.goal_speed":0.18841,"retract_after_place.retract_speed":0.32806},"optimized_scores":{"best_composite_score":0.10302,"best_fitness_score":0.73302,"best_task_score":0.53929},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":716.0,"contact_point_centroid":[0.60161,0.16793,-0.00355],"force_p95":0.8242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79939,"mean_force":0.19653,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58683,0.1541,0.17223]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.52829,0.02824,-0.00145],"force_p95":0.41117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44404,"mean_force":0.0861,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51551,0.02897,0.04629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":399.0,"contact_point_centroid":[0.53944,0.02343,0.1793],"force_p95":0.24329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39114,"mean_force":0.14038,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53279,0.04234,0.18005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6902.0,"contact_point_centroid":[0.5223,0.04782,0.10624],"force_p95":0.10638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29906,"mean_force":0.06744,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51888,0.02902,0.10379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5892.0,"contact_point_centroid":[0.52211,0.01008,0.1044],"force_p95":0.11428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29827,"mean_force":0.07602,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51879,0.02901,0.10285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.54171,0.06468,0.18002],"force_p95":0.17314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27461,"mean_force":0.0986,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53497,0.04675,0.18118]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03063,-0.00214],"force_p95":0.16149,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22242,"mean_force":0.13289,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51773,0.02913,0.04611]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51044,0.01247,0.23436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.51712,0.00987,0.04692],"force_p95":0.0776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13668,"mean_force":0.04936,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51658,0.02905,0.04479]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60187,0.16847,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58869,0.16774,0.14185]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52301,0.02764,0.11143]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.60187,0.16847,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59052,0.17088,0.19397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5019.0,"contact_point_centroid":[0.5173,0.04827,0.04663],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07629,"mean_force":0.04429,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51659,0.02905,0.0448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":543.0,"contact_point_centroid":[0.58874,0.15811,0.16501],"force_p95":0.01422,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01107,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58849,0.15809,0.16279]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.59178,0.16878,0.13976],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01025,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59153,0.16875,0.13763]}],"total_contact_groups":15},"final_pose_error":0.02987,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60187,0.16847,0.01602],"final_tcp_position":[0.59575,0.17514,0.22899],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.79939,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.52269,0.02582,0.16733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":824.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5251,0.02959,0.05496],"tcp_start":[0.52269,0.02582,0.16733],"tcp_to_object_dist_end":0.02946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02955,0.0255],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18461,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1568,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11148.0,"raw_peak_contact_force":0.22242,"tcp_end":[0.51655,0.02905,0.04476],"tcp_start":[0.5251,0.02959,0.05496],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":428.0,"n_steps_budget":750.0,"object_pos_end":[0.54127,0.02986,0.15135],"object_pos_start":[0.53047,0.02955,0.0255],"object_to_goal_dist_end":0.16619,"object_to_goal_dist_start":0.18461,"object_z_max":0.1511,"peak_contact_force":0.10882,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12874.0,"raw_peak_contact_force":0.44404,"subtask_id":"approach_grasp","tcp_end":[0.52574,0.02927,0.1766],"tcp_start":[0.51655,0.02905,0.04476],"tcp_to_object_dist_end":0.02965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.59759,0.1473,0.03822],"object_pos_start":[0.54127,0.02986,0.15135],"object_to_goal_dist_end":0.07665,"object_to_goal_dist_start":0.16619,"object_z_max":0.1575,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":959.0,"raw_peak_contact_force":0.39114,"subtask_id":"place_at_goal","tcp_end":[0.58121,0.13762,0.2084],"tcp_start":[0.52574,0.02927,0.1766],"tcp_to_object_dist_end":0.17124,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.60187,0.16847,0.01602],"object_pos_start":[0.59759,0.1473,0.03822],"object_to_goal_dist_end":0.09263,"object_to_goal_dist_start":0.07665,"object_z_max":0.03822,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1259.0,"raw_peak_contact_force":1.79939,"tcp_end":[0.5935,0.16893,0.14129],"tcp_start":[0.58121,0.13762,0.2084],"tcp_to_object_dist_end":0.12555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60187,0.16847,0.01602],"object_pos_start":[0.60187,0.16847,0.01602],"object_to_goal_dist_end":0.09262,"object_to_goal_dist_start":0.09263,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.58697,0.16716,0.16171],"tcp_start":[0.5935,0.16893,0.14129],"tcp_to_object_dist_end":0.14646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":155.0,"n_steps_budget":600.0,"object_pos_end":[0.60187,0.16847,0.01602],"object_pos_start":[0.60187,0.16847,0.01602],"object_to_goal_dist_end":0.09262,"object_to_goal_dist_start":0.09262,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":620.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59575,0.17514,0.22899],"tcp_start":[0.58697,0.16716,0.16171],"tcp_to_object_dist_end":0.21316,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```