## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0986 | 0.25 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | time_limit | 10 | 0.0382 | 0.45 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0611 | 0.46 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0616 | 0.46 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0002 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.099) — your mutation base

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

- **Composite score**: -0.099
- **task_score** (E): 0.247
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1383 |
| descend_to_object | 1.00 | 1.00 | 0.1083 |
| close_gripper | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1517 |
| move_above_goal | 1.00 | 1.00 | 0.2374 |
| descend_to_place | 1.00 | 1.00 | 0.1800 |
| release_object | 1.00 | 1.00 | 0.0201 |
| retract_after_place | 1.00 | 1.00 | 0.1272 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.060) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| close_gripper | grasp | 1.00 / step_budget | (0.506, 0.002, 0.060)→(0.498, 0.002, 0.050) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 36.000 | 0.145 | 0.192 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.050)→(0.507, 0.002, 0.201) | (0.511, 0.002, 0.026)→(0.517, 0.002, 0.171) | 0.246→0.218 | 1.00 / 17.333 | 0.134 | 0.358 |
| move_above_goal | approach | 1.00 / step_budget | (0.507, 0.002, 0.201)→(0.611, 0.157, 0.341) | (0.517, 0.002, 0.171)→(0.547, 0.027, 0.016) | 0.218→0.215 | 1.00 / 8.333 | 0.123 | 1.930 |
| descend_to_place | descend | 1.00 / step_budget | (0.611, 0.157, 0.341)→(0.621, 0.178, 0.162) | (0.547, 0.027, 0.016)→(0.547, 0.027, 0.016) | 0.215→0.215 | 1.00 / 8.333 | 91002.645 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.621, 0.178, 0.162)→(0.615, 0.176, 0.181) | (0.547, 0.027, 0.016)→(0.547, 0.027, 0.016) | 0.215→0.215 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.615, 0.176, 0.181)→(0.624, 0.180, 0.308) | (0.547, 0.027, 0.016)→(0.547, 0.027, 0.016) | 0.215→0.215 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.332
- phase_score: 0.057
- phase_breakdown.place_at_goal_score: 0.016
- phase_breakdown.approach_grasp_score: 0.154
- grasp_place_fitness: 0.618

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.618
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.332
- **Median Q (composite search score)**: -0.104
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.396


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89904,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.35379,"descend_to_object.descend_speed":0.36409,"descend_to_object.grasp_offset_z":0.01004,"descend_to_place.descend_place_speed":0.10738,"descend_to_place.place_offset_z":0.01631,"lift_object.lift_offset_z":0.16718,"lift_object.lift_speed":0.05811,"move_above_goal.arc_height":0.05043,"move_above_goal.goal_speed":0.10666,"retract_after_place.retract_speed":0.22115},"optimized_scores":{"best_composite_score":-0.10369,"best_fitness_score":0.57631,"best_task_score":0.22856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1299.0,"contact_point_centroid":[0.52323,0.04102,-0.00288],"force_p95":0.43157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01715,"mean_force":0.1618,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.5565,0.1122,0.29468]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.45628,-0.02455,-0.00145],"force_p95":0.33467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38035,"mean_force":0.09274,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44732,-0.02507,0.04948]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1762.0,"contact_point_centroid":[0.47157,-0.02588,0.2009],"force_p95":0.1513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29276,"mean_force":0.08702,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.46556,-0.00749,0.20064]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7803.0,"contact_point_centroid":[0.45017,-0.04407,0.10742],"force_p95":0.10014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2718,"mean_force":0.05994,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44919,-0.02509,0.10659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6873.0,"contact_point_centroid":[0.45066,-0.00601,0.10799],"force_p95":0.10558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26722,"mean_force":0.06601,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44923,-0.02509,0.10726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.47022,0.00917,0.19844],"force_p95":0.16898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25027,"mean_force":0.09616,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.4641,-0.00949,0.1978]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.0021],"force_p95":0.15173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2078,"mean_force":0.13025,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44919,-0.02514,0.04907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.44907,-0.00589,0.04901],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14751,"mean_force":0.05214,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44817,-0.0251,0.04809]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48136,-0.01058,0.23556]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45836,-0.02361,0.11285]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.52314,0.04105,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61764,0.19417,0.22421]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52314,0.04105,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61962,0.2027,0.1393]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.52314,0.04105,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62126,0.20388,0.22014]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4961.0,"contact_point_centroid":[0.44824,-0.0442,0.04916],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07349,"mean_force":0.04414,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44818,-0.0251,0.04809]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1216.0,"contact_point_centroid":[0.56296,0.12027,0.30064],"force_p95":0.01219,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01063,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.5627,0.12027,0.29833]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1706.0,"contact_point_centroid":[0.61789,0.1941,0.22713],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01254,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61758,0.1941,0.22488]}],"total_contact_groups":17},"final_pose_error":0.02992,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52314,0.04105,0.01602],"final_tcp_position":[0.62685,0.20657,0.28442],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273007.68846,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.46241,-0.022,0.16889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":848.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45581,-0.02537,0.05584],"tcp_start":[0.46241,-0.022,0.16889],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02545,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14877,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.2078,"tcp_end":[0.44815,-0.0251,0.04806],"tcp_start":[0.45581,-0.02537,0.05584],"tcp_to_object_dist_end":0.02471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.46838,-0.02563,0.14802],"object_pos_start":[0.45851,-0.02545,0.02563],"object_to_goal_dist_end":0.28635,"object_to_goal_dist_start":0.30312,"object_z_max":0.14775,"peak_contact_force":0.10652,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14758.0,"raw_peak_contact_force":0.38035,"subtask_id":"approach_grasp","tcp_end":[0.45388,-0.02523,0.17352],"tcp_start":[0.44815,-0.0251,0.04806],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.52314,0.04105,0.01602],"object_pos_start":[0.46838,-0.02563,0.14802],"object_to_goal_dist_end":0.22139,"object_to_goal_dist_start":0.28635,"object_z_max":0.1999,"peak_contact_force":0.12263,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5753.0,"raw_peak_contact_force":2.01715,"subtask_id":"place_at_goal","tcp_end":[0.61245,0.18486,0.30894],"tcp_start":[0.45388,-0.02523,0.17352],"tcp_to_object_dist_end":0.33832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.52314,0.04105,0.01602],"object_pos_start":[0.52314,0.04105,0.01602],"object_to_goal_dist_end":0.22139,"object_to_goal_dist_start":0.22139,"object_z_max":0.01602,"peak_contact_force":273007.68846,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3310.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62451,0.2044,0.14002],"tcp_start":[0.61245,0.18486,0.30894],"tcp_to_object_dist_end":0.22877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52314,0.04105,0.01602],"object_pos_start":[0.52314,0.04105,0.01602],"object_to_goal_dist_end":0.22139,"object_to_goal_dist_start":0.22139,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61789,0.20202,0.15866],"tcp_start":[0.62451,0.2044,0.14002],"tcp_to_object_dist_end":0.23502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":267.0,"n_steps_budget":600.0,"object_pos_end":[0.52314,0.04105,0.01602],"object_pos_start":[0.52314,0.04105,0.01602],"object_to_goal_dist_end":0.22139,"object_to_goal_dist_start":0.22139,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62685,0.20657,0.28442],"tcp_start":[0.61789,0.20202,0.15866],"tcp_to_object_dist_end":0.33195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.345,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.26611,"descend_to_object.descend_speed":0.18864,"descend_to_object.grasp_offset_z":0.01359,"descend_to_place.descend_place_speed":0.07306,"descend_to_place.place_offset_z":0.01469,"lift_object.lift_offset_z":0.20088,"lift_object.lift_speed":0.10741,"move_above_goal.arc_height":0.13781,"move_above_goal.goal_speed":0.11503,"retract_after_place.retract_speed":0.15175},"optimized_scores":{"best_composite_score":-0.13034,"best_fitness_score":0.54966,"best_task_score":0.17938},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.55605,-0.00748,-0.00249],"force_p95":0.19101,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.91064,"mean_force":0.14698,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.55658,0.02569,0.36489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.54743,0.0183,0.20109],"force_p95":0.34055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4018,"mean_force":0.1977,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.53981,0.00086,0.20772]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.54268,0.00078,-0.00137],"force_p95":0.32646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37494,"mean_force":0.07389,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52868,0.00085,0.04887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7269.0,"contact_point_centroid":[0.5362,0.01959,0.11705],"force_p95":0.1305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28211,"mean_force":0.07767,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53202,0.00084,0.1163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7060.0,"contact_point_centroid":[0.53619,-0.01793,0.11872],"force_p95":0.12627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2671,"mean_force":0.07923,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5322,0.00084,0.11826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.54548,-0.01576,0.20379],"force_p95":0.20795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24857,"mean_force":0.08949,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.53889,0.00034,0.20854]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00109,-0.00203],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15291,"mean_force":0.12542,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.53091,0.00089,0.04906]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51606,0.00045,0.23431]},{"body_a":"world","body_b":"grasp_target","contact_count":796.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53546,0.00096,0.11308]},{"body_a":"world","body_b":"grasp_target","contact_count":1708.0,"contact_point_centroid":[0.55622,-0.0075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63721,0.14427,0.30722]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55622,-0.0075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63923,0.15373,0.21509]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.55622,-0.0075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.64106,0.15493,0.2962]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4439.0,"contact_point_centroid":[0.53039,-0.01831,0.04896],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09884,"mean_force":0.04866,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00087,0.04768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4802.0,"contact_point_centroid":[0.53072,0.02001,0.04895],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0855,"mean_force":0.04523,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.52974,0.00087,0.04768]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2000.0,"contact_point_centroid":[0.56049,0.03079,0.3781],"force_p95":0.01121,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01481,"mean_force":0.01055,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56023,0.03078,0.37571]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1844.0,"contact_point_centroid":[0.63764,0.1443,0.3094],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63722,0.14428,0.30707]}],"total_contact_groups":17},"final_pose_error":0.0296,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55622,-0.0075,0.01602],"final_tcp_position":[0.64597,0.15709,0.36156],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.91064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.53434,0.00092,0.16718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":796.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53839,0.00102,0.05834],"tcp_start":[0.53434,0.00092,0.16718],"tcp_to_object_dist_end":0.03286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00095,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25038,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13201,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11041.0,"raw_peak_contact_force":0.15291,"tcp_end":[0.52971,0.00087,0.04764],"tcp_start":[0.53839,0.00102,0.05834],"tcp_to_object_dist_end":0.02617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.55097,0.00064,0.17687],"object_pos_start":[0.54422,0.00095,0.02586],"object_to_goal_dist_end":0.18529,"object_to_goal_dist_start":0.25038,"object_z_max":0.1768,"peak_contact_force":0.18235,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14408.0,"raw_peak_contact_force":0.37494,"subtask_id":"approach_grasp","tcp_end":[0.53983,0.00089,0.20749],"tcp_start":[0.52971,0.00087,0.04764],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.55622,-0.0075,0.01602],"object_pos_start":[0.55097,0.00064,0.17687],"object_to_goal_dist_end":0.25774,"object_to_goal_dist_start":0.18529,"object_z_max":0.17687,"peak_contact_force":0.12263,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4157.0,"raw_peak_contact_force":1.91064,"subtask_id":"place_at_goal","tcp_end":[0.63208,0.1343,0.39983],"tcp_start":[0.53983,0.00089,0.20749],"tcp_to_object_dist_end":0.41614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.55622,-0.0075,0.01602],"object_pos_start":[0.55622,-0.0075,0.01602],"object_to_goal_dist_end":0.25774,"object_to_goal_dist_start":0.25774,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3552.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6431,0.15479,0.21609],"tcp_start":[0.63208,0.1343,0.39983],"tcp_to_object_dist_end":0.27187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55622,-0.0075,0.01602],"object_pos_start":[0.55622,-0.0075,0.01602],"object_to_goal_dist_end":0.25774,"object_to_goal_dist_start":0.25774,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63793,0.15329,0.2343],"tcp_start":[0.6431,0.15479,0.21609],"tcp_to_object_dist_end":0.28316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":660.0,"object_pos_end":[0.55622,-0.0075,0.01602],"object_pos_start":[0.55622,-0.0075,0.01602],"object_to_goal_dist_end":0.25774,"object_to_goal_dist_start":0.25774,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64597,0.15709,0.36156],"tcp_start":[0.63793,0.15329,0.2343],"tcp_to_object_dist_end":0.39312,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74038,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.308,"descend_to_object.descend_speed":0.31031,"descend_to_object.grasp_offset_z":0.01981,"descend_to_place.descend_place_speed":0.05706,"descend_to_place.place_offset_z":0.01269,"lift_object.lift_offset_z":0.21713,"lift_object.lift_speed":0.06747,"move_above_goal.arc_height":0.13971,"move_above_goal.goal_speed":0.1916,"retract_after_place.retract_speed":0.21391},"optimized_scores":{"best_composite_score":-0.06188,"best_fitness_score":0.61812,"best_task_score":0.3324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":623.0,"contact_point_centroid":[0.56027,0.04698,-0.00402],"force_p95":1.10496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86291,"mean_force":0.22297,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56549,0.1079,0.31691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5985.0,"contact_point_centroid":[0.52257,0.01073,0.13107],"force_p95":0.13505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31798,"mean_force":0.09936,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51927,0.02904,0.13447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5901.0,"contact_point_centroid":[0.52288,0.04737,0.13304],"force_p95":0.13995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30215,"mean_force":0.10013,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51946,0.02905,0.13656]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.52829,0.02878,-0.00145],"force_p95":0.26256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29586,"mean_force":0.06393,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51563,0.02892,0.05587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":395.0,"contact_point_centroid":[0.53247,0.04881,0.22932],"force_p95":0.17493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25069,"mean_force":0.11288,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.52612,0.03059,0.23321]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03069,-0.00213],"force_p95":0.16136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21507,"mean_force":0.13198,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51785,0.02908,0.05584]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":437.0,"contact_point_centroid":[0.5327,0.01272,0.23106],"force_p95":0.1575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20494,"mean_force":0.10299,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.52623,0.03092,0.23509]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51044,0.01247,0.23436]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.56052,0.04767,-0.00199],"force_p95":0.12265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12301,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59128,0.16333,0.2212]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52304,0.02761,0.1164]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56052,0.04767,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59127,0.17335,0.13108]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.56052,0.04767,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59266,0.17451,0.21332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2434.0,"contact_point_centroid":[0.5183,0.01032,0.05178],"force_p95":0.10452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11768,"mean_force":0.082,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51672,0.029,0.05452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.51779,0.04769,0.05119],"force_p95":0.10027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1004,"mean_force":0.07326,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51672,0.029,0.05453]},{"body_a":"left_finger","body_b":"right_finger","contact_count":563.0,"contact_point_centroid":[0.56939,0.11475,0.32124],"force_p95":0.01344,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01476,"mean_force":0.01085,"phase_index":4.0,"phase_name":"move_above_goal","phase_type":"approach","tcp_position_centroid":[0.56901,0.11474,0.31887]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2011.0,"contact_point_centroid":[0.59159,0.16334,0.22352],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01056,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59128,0.16332,0.22125]}],"total_contact_groups":17},"final_pose_error":0.02998,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56052,0.04767,0.01602],"final_tcp_position":[0.59807,0.17701,0.27836],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.86291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.52269,0.02582,0.16733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":760.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52509,0.02953,0.0647],"tcp_start":[0.52269,0.02582,0.16733],"tcp_to_object_dist_end":0.03908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02964,0.02557],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18451,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1557,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7058.0,"raw_peak_contact_force":0.21507,"tcp_end":[0.51669,0.029,0.05448],"tcp_start":[0.52509,0.02953,0.0647],"tcp_to_object_dist_end":0.03204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.53243,0.0296,0.18706],"object_pos_start":[0.53047,0.02964,0.02557],"object_to_goal_dist_end":0.18223,"object_to_goal_dist_start":0.18451,"object_z_max":0.1868,"peak_contact_force":0.11452,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11975.0,"raw_peak_contact_force":0.31798,"subtask_id":"approach_grasp","tcp_end":[0.52627,0.02937,0.22341],"tcp_start":[0.51669,0.029,0.05448],"tcp_to_object_dist_end":0.03687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.56052,0.04767,0.01601],"object_pos_start":[0.53243,0.0296,0.18706],"object_to_goal_dist_end":0.16522,"object_to_goal_dist_start":0.18223,"object_z_max":0.2121,"peak_contact_force":0.12304,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2018.0,"raw_peak_contact_force":1.86291,"subtask_id":"place_at_goal","tcp_end":[0.58815,0.15258,0.3133],"tcp_start":[0.52627,0.02937,0.22341],"tcp_to_object_dist_end":0.31647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.56052,0.04767,0.01602],"object_pos_start":[0.56052,0.04767,0.01601],"object_to_goal_dist_end":0.16521,"object_to_goal_dist_start":0.16522,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3919.0,"raw_peak_contact_force":0.12301,"tcp_end":[0.59622,0.17485,0.13066],"tcp_start":[0.58815,0.15258,0.3133],"tcp_to_object_dist_end":0.1749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56052,0.04767,0.01602],"object_pos_start":[0.56052,0.04767,0.01602],"object_to_goal_dist_end":0.16521,"object_to_goal_dist_start":0.16521,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5895,0.17275,0.1509],"tcp_start":[0.59622,0.17485,0.13066],"tcp_to_object_dist_end":0.18622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":600.0,"object_pos_end":[0.56052,0.04767,0.01602],"object_pos_start":[0.56052,0.04767,0.01602],"object_to_goal_dist_end":0.16521,"object_to_goal_dist_start":0.16521,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59807,0.17701,0.27836],"tcp_start":[0.5895,0.17275,0.1509],"tcp_to_object_dist_end":0.29489,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```