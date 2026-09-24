## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | time_limit | 10 | 0.0382 | 0.45 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0611 | 0.46 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0616 | 0.46 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0002 | 0.37 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1009 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.038) — your mutation base

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

- **Composite score**: 0.038
- **task_score** (E): 0.451
- **fitness_score**: 0.688  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1383 |
| descend_to_object | 1.00 | 1.00 | 0.1123 |
| close_gripper | 1.00 | 1.00 | 0.0127 |
| lift_object | 1.00 | 1.00 | 0.0942 |
| move_to_goal | 1.00 | 1.00 | 0.2047 |
| release_object | 1.00 | 1.00 | 0.0209 |
| retract_after_place | 1.00 | 1.00 | 0.0817 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.168) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 1.00 / step_budget | (0.506, 0.002, 0.168)→(0.506, 0.002, 0.056) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 19.533 | 0.123 |
| close_gripper | grasp | 1.00 / step_budget | (0.506, 0.002, 0.056)→(0.498, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 41.333 | 0.146 | 0.194 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.046)→(0.506, 0.002, 0.140) | (0.511, 0.002, 0.026)→(0.521, 0.002, 0.116) | 0.246→0.214 | 1.00 / 25.333 | 0.104 | 0.410 |
| move_to_goal | approach | 1.00 / step_budget | (0.506, 0.002, 0.140)→(0.616, 0.169, 0.172) | (0.521, 0.002, 0.116)→(0.612, 0.163, 0.101) | 0.214→0.050 | 1.00 / 13.667 | 0.130 | 0.656 |
| release_object | release | 1.00 / step_budget | (0.616, 0.169, 0.172)→(0.610, 0.168, 0.193) | (0.612, 0.163, 0.101)→(0.610, 0.161, 0.019) | 0.050→0.123 | 1.00 / 3.333 | 0.243 | 1.054 |
| retract_after_place | retract | 1.00 / time_limit | (0.610, 0.168, 0.193)→(0.623, 0.180, 0.272) | (0.610, 0.161, 0.019)→(0.608, 0.164, 0.019) | 0.123→0.124 | 1.00 / 4.000 | 0.123 | 0.236 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.558
- phase_score: 0.528
- phase_breakdown.place_at_goal_score: 0.407
- phase_breakdown.approach_grasp_score: 0.810
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.558
- **Median Q (composite search score)**: 0.055
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_object.grasp_offset_z
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37037,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.33017,"descend_to_object.descend_speed":0.27364,"descend_to_object.grasp_offset_z":0.01,"lift_object.lift_offset_z":0.12972,"lift_object.lift_speed":0.18687,"move_to_goal.goal_offset_z":0.0606,"move_to_goal.goal_speed":0.22527,"release_object.release_max_time":0.0813,"retract_after_place.retract_max_time":0.10305,"retract_after_place.retract_speed":0.30628},"optimized_scores":{"best_composite_score":0.05475,"best_fitness_score":0.70475,"best_task_score":0.48537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":306.0,"contact_point_centroid":[0.59811,0.17358,-0.00469],"force_p95":1.09743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37091,"mean_force":0.27529,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.60986,0.1847,0.1629]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.4573,-0.02498,-0.00141],"force_p95":0.34655,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39854,"mean_force":0.07267,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44719,-0.02506,0.04948]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6644.0,"contact_point_centroid":[0.51565,0.03933,0.14256],"force_p95":0.15504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33177,"mean_force":0.09082,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51367,0.05742,0.14492]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5993.0,"contact_point_centroid":[0.51464,0.07437,0.14254],"force_p95":0.16199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30835,"mean_force":0.0952,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.51267,0.05612,0.14471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4789.0,"contact_point_centroid":[0.45048,-0.00599,0.0917],"force_p95":0.09744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3021,"mean_force":0.06154,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44949,-0.02511,0.09094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5305.0,"contact_point_centroid":[0.45026,-0.04415,0.0914],"force_p95":0.09119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29647,"mean_force":0.0568,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44946,-0.02511,0.09052]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.02623,-0.0021],"force_p95":0.15173,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20782,"mean_force":0.13025,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44919,-0.02514,0.04903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.44907,-0.00589,0.04898],"force_p95":0.07972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14752,"mean_force":0.05213,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44817,-0.0251,0.04805]},{"body_a":"world","body_b":"grasp_target","contact_count":952.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13699,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48136,-0.01058,0.23556]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59823,0.17482,-0.00197],"force_p95":0.12813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12969,"mean_force":0.12275,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61399,0.19485,0.16475]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45836,-0.02361,0.11283]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.59822,0.17482,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61749,0.19951,0.21263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4961.0,"contact_point_centroid":[0.44824,-0.0442,0.04913],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0735,"mean_force":0.04415,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.44818,-0.0251,0.04805]},{"body_a":"left_finger","body_b":"right_finger","contact_count":79.0,"contact_point_centroid":[0.61693,0.19336,0.16629],"force_p95":0.01521,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01556,"mean_force":0.01326,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.61645,0.19335,0.16411]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.61688,0.19598,0.16372],"force_p95":0.01172,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01328,"mean_force":0.01031,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61673,0.19597,0.16135]}],"total_contact_groups":15},"final_pose_error":0.01547,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59822,0.17482,0.01602],"final_tcp_position":[0.62605,0.20613,0.24934],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.37091,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.46241,-0.022,0.16889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":848.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45581,-0.02537,0.05581],"tcp_start":[0.46241,-0.022,0.16889],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02545,0.02563],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30312,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14876,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10859.0,"raw_peak_contact_force":0.20782,"tcp_end":[0.44815,-0.0251,0.04802],"tcp_start":[0.45581,-0.02537,0.05581],"tcp_to_object_dist_end":0.02468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":268.0,"n_steps_budget":600.0,"object_pos_end":[0.46809,-0.0256,0.11134],"object_pos_start":[0.45851,-0.02545,0.02563],"object_to_goal_dist_end":0.28449,"object_to_goal_dist_start":0.30312,"object_z_max":0.11106,"peak_contact_force":0.10206,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10170.0,"raw_peak_contact_force":0.39854,"subtask_id":"approach_grasp","tcp_end":[0.45368,-0.02523,0.13616],"tcp_start":[0.44815,-0.0251,0.04802],"tcp_to_object_dist_end":0.0287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.59821,0.17491,0.01659],"object_pos_start":[0.46809,-0.0256,0.11134],"object_to_goal_dist_end":0.10789,"object_to_goal_dist_start":0.28449,"object_z_max":0.1198,"peak_contact_force":0.12785,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13022.0,"raw_peak_contact_force":1.37091,"subtask_id":"place_at_goal","tcp_end":[0.61825,0.19596,0.16442],"tcp_start":[0.45368,-0.02523,0.13616],"tcp_to_object_dist_end":0.15066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59822,0.17482,0.01602],"object_pos_start":[0.59821,0.17491,0.01659],"object_to_goal_dist_end":0.10843,"object_to_goal_dist_start":0.10789,"object_z_max":0.01659,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12969,"tcp_end":[0.61237,0.19421,0.18412],"tcp_start":[0.61825,0.19596,0.16442],"tcp_to_object_dist_end":0.1698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.59822,0.17482,0.01602],"object_pos_start":[0.59822,0.17482,0.01602],"object_to_goal_dist_end":0.10843,"object_to_goal_dist_start":0.10843,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62605,0.20613,0.24934],"tcp_start":[0.61237,0.19421,0.18412],"tcp_to_object_dist_end":0.23705,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.33489,"descend_to_object.descend_speed":0.34294,"descend_to_object.grasp_offset_z":0.01,"lift_object.lift_offset_z":0.13822,"lift_object.lift_speed":0.19723,"move_to_goal.goal_offset_z":0.02576,"move_to_goal.goal_speed":0.29893,"release_object.release_max_time":0.12026,"retract_after_place.retract_max_time":0.33101,"retract_after_place.retract_speed":0.15705},"optimized_scores":{"best_composite_score":-0.03091,"best_fitness_score":0.61909,"best_task_score":0.31008},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.63282,0.14704,-0.00988],"force_p95":1.37049,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69672,"mean_force":0.60196,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63241,0.14632,0.21494]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54263,0.00055,-0.00133],"force_p95":0.39596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43086,"mean_force":0.08328,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52871,0.00084,0.04539]},{"body_a":"world","body_b":"grasp_target","contact_count":2279.0,"contact_point_centroid":[0.65427,0.14582,-0.00199],"force_p95":0.12567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32388,"mean_force":0.12295,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.6367,0.15075,0.26629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4688.0,"contact_point_centroid":[0.53539,-0.01807,0.09126],"force_p95":0.11392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31294,"mean_force":0.07582,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53207,0.00077,0.0891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":557.0,"contact_point_centroid":[0.64114,0.16573,0.19571],"force_p95":0.13843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29153,"mean_force":0.09238,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63588,0.14744,0.19962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4852.0,"contact_point_centroid":[0.53523,0.01956,0.08978],"force_p95":0.11217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28552,"mean_force":0.07399,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53194,0.00077,0.08772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":555.0,"contact_point_centroid":[0.64109,0.12922,0.19605],"force_p95":0.13549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28476,"mean_force":0.08699,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63584,0.14743,0.19952]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5615.0,"contact_point_centroid":[0.58902,0.05025,0.17039],"force_p95":0.13667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22466,"mean_force":0.08911,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5834,0.06884,0.17002]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5982.0,"contact_point_centroid":[0.59141,0.09065,0.17157],"force_p95":0.12717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2088,"mean_force":0.08478,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.58568,0.07216,0.17142]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00104,-0.00203],"force_p95":0.13201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15377,"mean_force":0.12535,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.53087,0.00089,0.04547]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51606,0.00045,0.23431]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.53545,0.00096,0.11124]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4124.0,"contact_point_centroid":[0.53066,-0.01833,0.04683],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10068,"mean_force":0.05171,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00087,0.04409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4869.0,"contact_point_centroid":[0.53064,0.01994,0.04596],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09367,"mean_force":0.04475,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00087,0.04409]}],"total_contact_groups":14},"final_pose_error":0.01785,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65435,0.14586,0.01602],"final_tcp_position":[0.64482,0.15664,0.32353],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":58.3551,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.53434,0.00092,0.16718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":58.3551,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5384,0.00102,0.05475],"tcp_start":[0.53434,0.00092,0.16718],"tcp_to_object_dist_end":0.02933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00077,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25049,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13045,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15377,"tcp_end":[0.52967,0.00087,0.04406],"tcp_start":[0.5384,0.00102,0.05475],"tcp_to_object_dist_end":0.02329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":338.0,"n_steps_budget":600.0,"object_pos_end":[0.55447,0.00077,0.12187],"object_pos_start":[0.54421,0.00077,0.02587],"object_to_goal_dist_end":0.1955,"object_to_goal_dist_start":0.25049,"object_z_max":0.12163,"peak_contact_force":0.10038,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9617.0,"raw_peak_contact_force":0.43086,"subtask_id":"approach_grasp","tcp_end":[0.5388,0.00072,0.14498],"tcp_start":[0.52967,0.00087,0.04406],"tcp_to_object_dist_end":0.02792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.64272,0.14788,0.16883],"object_pos_start":[0.55447,0.00077,0.12187],"object_to_goal_dist_end":0.02499,"object_to_goal_dist_start":0.1955,"object_z_max":0.16876,"peak_contact_force":0.13532,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11597.0,"raw_peak_contact_force":0.22466,"subtask_id":"place_at_goal","tcp_end":[0.63762,0.14741,0.20355],"tcp_start":[0.5388,0.00072,0.14498],"tcp_to_object_dist_end":0.0351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.65109,0.14304,0.01499],"object_pos_start":[0.64272,0.14788,0.16883],"object_to_goal_dist_end":0.17679,"object_to_goal_dist_start":0.02499,"object_z_max":0.16883,"peak_contact_force":0.34034,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1230.0,"raw_peak_contact_force":1.69672,"tcp_end":[0.63238,0.14631,0.22291],"tcp_start":[0.63762,0.14741,0.20355],"tcp_to_object_dist_end":0.20878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.65435,0.14586,0.01602],"object_pos_start":[0.65109,0.14304,0.01499],"object_to_goal_dist_end":0.17564,"object_to_goal_dist_start":0.17679,"object_z_max":0.01631,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2279.0,"raw_peak_contact_force":0.32388,"tcp_end":[0.64482,0.15664,0.32353],"tcp_start":[0.63238,0.14631,0.22291],"tcp_to_object_dist_end":0.30785,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26733,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.28427,"descend_to_object.descend_speed":0.20993,"descend_to_object.grasp_offset_z":0.01164,"lift_object.lift_offset_z":0.13238,"lift_object.lift_speed":0.15236,"move_to_goal.goal_offset_z":0.05057,"move_to_goal.goal_speed":0.17615,"release_object.release_max_time":0.12611,"retract_after_place.retract_max_time":0.35369,"retract_after_place.retract_speed":0.36401},"optimized_scores":{"best_composite_score":0.09066,"best_fitness_score":0.74066,"best_task_score":0.55796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.58099,0.16599,-0.00589],"force_p95":1.0092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33628,"mean_force":0.33356,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58511,0.16288,0.15962]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.52893,0.02889,-0.00144],"force_p95":0.37516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4009,"mean_force":0.07663,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51565,0.02897,0.04775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4442.0,"contact_point_centroid":[0.56173,0.07675,0.14245],"force_p95":0.13353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37373,"mean_force":0.08971,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55617,0.09542,0.14201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":638.0,"contact_point_centroid":[0.59338,0.1829,0.14327],"force_p95":0.14241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34978,"mean_force":0.08721,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58916,0.16432,0.14593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.59411,0.14608,0.14271],"force_p95":0.12737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31716,"mean_force":0.08786,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58918,0.16433,0.14595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4985.0,"contact_point_centroid":[0.52111,0.04794,0.08756],"force_p95":0.10937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28372,"mean_force":0.06784,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51856,0.02902,0.08608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4645.0,"contact_point_centroid":[0.52076,0.0101,0.08743],"force_p95":0.11224,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26949,"mean_force":0.0706,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51857,0.02902,0.08628]},{"body_a":"world","body_b":"grasp_target","contact_count":2143.0,"contact_point_centroid":[0.57263,0.16985,-0.002],"force_p95":0.14719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26212,"mean_force":0.12421,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58949,0.16912,0.20365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4890.0,"contact_point_centroid":[0.56225,0.11487,0.14228],"force_p95":0.12522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23704,"mean_force":0.0823,"phase_index":4.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55662,0.09639,0.14207]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03067,-0.00214],"force_p95":0.16254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22085,"mean_force":0.13315,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51776,0.02913,0.04757]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51044,0.01247,0.23436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4329.0,"contact_point_centroid":[0.5171,0.00986,0.04787],"force_p95":0.07706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13283,"mean_force":0.04946,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51661,0.02905,0.04625]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.52301,0.02764,0.11217]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51732,0.04825,0.04783],"force_p95":0.0744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07575,"mean_force":0.04417,"phase_index":2.0,"phase_name":"close_gripper","phase_type":"grasp","tcp_position_centroid":[0.51662,0.02905,0.04626]}],"total_contact_groups":14},"final_pose_error":0.01514,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57236,0.17005,0.02602],"final_tcp_position":[0.5974,0.17648,0.24367],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.33628,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_grasp","tcp_end":[0.52269,0.02582,0.16733],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":816.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5251,0.02958,0.0564],"tcp_start":[0.52269,0.02582,0.16733],"tcp_to_object_dist_end":0.03088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.0296,0.02549],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18458,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15873,"phase_name":"close_gripper","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11145.0,"raw_peak_contact_force":0.22085,"tcp_end":[0.51658,0.02905,0.04622],"tcp_start":[0.5251,0.02958,0.0564],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":308.0,"n_steps_budget":600.0,"object_pos_end":[0.54004,0.02975,0.11439],"object_pos_start":[0.53047,0.0296,0.02549],"object_to_goal_dist_end":0.16115,"object_to_goal_dist_start":0.18458,"object_z_max":0.11415,"peak_contact_force":0.10854,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9714.0,"raw_peak_contact_force":0.4009,"subtask_id":"approach_grasp","tcp_end":[0.52501,0.02927,0.13885],"tcp_start":[0.51658,0.02905,0.04622],"tcp_to_object_dist_end":0.02872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.59592,0.16477,0.11691],"object_pos_start":[0.54004,0.02975,0.11439],"object_to_goal_dist_end":0.01732,"object_to_goal_dist_start":0.16115,"object_z_max":0.1169,"peak_contact_force":0.12541,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9332.0,"raw_peak_contact_force":0.37373,"subtask_id":"place_at_goal","tcp_end":[0.59118,0.16428,0.14938],"tcp_start":[0.52501,0.02927,0.13885],"tcp_to_object_dist_end":0.03282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58136,0.16546,0.02679],"object_pos_start":[0.59592,0.16477,0.11691],"object_to_goal_dist_end":0.08478,"object_to_goal_dist_start":0.01732,"object_z_max":0.11691,"peak_contact_force":0.265,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1376.0,"raw_peak_contact_force":1.33628,"tcp_end":[0.58502,0.16286,0.17051],"tcp_start":[0.59118,0.16428,0.14938],"tcp_to_object_dist_end":0.14379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.57236,0.17005,0.02602],"object_pos_start":[0.58136,0.16546,0.02679],"object_to_goal_dist_end":0.08752,"object_to_goal_dist_start":0.08478,"object_z_max":0.02702,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2143.0,"raw_peak_contact_force":0.26212,"tcp_end":[0.5974,0.17648,0.24367],"tcp_start":[0.58502,0.16286,0.17051],"tcp_to_object_dist_end":0.21918,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```