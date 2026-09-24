## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1381 | 0.54 | ✅ accepted |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0217 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0812 | 0.21 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1328 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1513 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=0.138) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.4
- id: reach_goal
  weight: 0.6
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
    - 0.1
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.0
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    grasp_height:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
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
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.002
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_goal
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
    - 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp_hold
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: reach_goal
- id: descend_place
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
    - 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    place_height:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: place_still_holding
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: abort
  subtask_id: reach_goal
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
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - grasp_height: status=consumed; consumers=target.offset.z (replace)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.002]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_hold, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=place_still_holding, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=1.0
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.138
- **task_score** (E): 0.536
- **fitness_score**: 0.738  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1177 |
| descend_grasp | 1.00 | 1.00 | 0.1389 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1049 |
| transport_goal | 0.00 | 0.00 | 0.0963 |
| descend_place | 0.00 | 1.00 | 0.0344 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.000, 0.188) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.000, 0.188)→(0.492, 0.001, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 45.000 | 0.141 | 0.191 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.049)→(0.484, 0.000, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 26.000 | 0.101 | 0.505 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.040)→(0.481, 0.000, 0.145) | (0.497, 0.001, 0.026)→(0.495, 0.001, 0.123) | 0.266→0.224 | 1.00 / 16.333 | 0.045 | 0.195 |
| transport_goal | approach | 0.00 / guard_failure | (0.481, 0.001, 0.146)→(0.511, 0.085, 0.169) | (0.495, 0.001, 0.123)→(0.500, 0.028, 0.140) | 0.224→0.191 | 0.00 / 0.000 | 0.000 | 0.247 |
| descend_place | descend | 0.00 / guard_failure | (0.511, 0.085, 0.169)→(0.530, 0.112, 0.174) | (0.519, 0.087, 0.137)→(0.537, 0.110, 0.133) | 0.131→0.106 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.813
- phase_score: 0.467
- phase_breakdown.reach_goal_score: 0.415
- phase_breakdown.reach_object_score: 0.546
- grasp_place_fitness: 0.875

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.875
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.813
- **Median Q (composite search score)**: 0.113
- **K-run variance**: 0.0106
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.301


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86207,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14632,"descend_grasp.grasp_height":0.01697,"descend_place.place_height":0.0014,"lift_object.lift_height":0.10504,"lift_object.lift_speed":0.13554,"release_object.release_duration":0.65168,"transport_goal.arc_height":0.01172,"transport_goal.transport_height":0.02771,"transport_goal.transport_speed":0.07213},"optimized_scores":{"best_composite_score":0.1134,"best_fitness_score":0.7134,"best_task_score":0.49272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.51065,-0.02207,-0.00126],"force_p95":0.24171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45557,"mean_force":0.07699,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49906,-0.02241,0.044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8056.0,"contact_point_centroid":[0.49932,-0.0034,0.0851],"force_p95":0.10299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31671,"mean_force":0.06729,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49664,-0.02234,0.08271]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8589.0,"contact_point_centroid":[0.49927,-0.04121,0.08276],"force_p95":0.1014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29139,"mean_force":0.06403,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49665,-0.02234,0.081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.52722,0.08512,0.19279],"force_p95":0.19773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25714,"mean_force":0.11585,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5209,0.0666,0.19476]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1685.0,"contact_point_centroid":[0.52765,0.05037,0.19365],"force_p95":0.11496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22141,"mean_force":0.07409,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5212,0.06793,0.19483]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02289,-0.00205],"force_p95":0.13793,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1721,"mean_force":0.12679,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50178,-0.02248,0.04386]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12062.0,"contact_point_centroid":[0.51203,0.03556,0.16569],"force_p95":0.10355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16782,"mean_force":0.07796,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50597,0.01683,0.16463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13028.0,"contact_point_centroid":[0.5122,-0.00086,0.16613],"force_p95":0.09448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15195,"mean_force":0.07187,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50628,0.01777,0.16534]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.5137,-0.02302,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50334,-0.00985,0.24242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.50112,-0.00324,0.04535],"force_p95":0.07744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12917,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50062,-0.02245,0.04258]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50745,-0.02146,0.11739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.50118,-0.04153,0.04441],"force_p95":0.06958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0879,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50062,-0.02245,0.04258]}],"total_contact_groups":12},"final_pose_error":0.08378,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53194,0.07274,0.15451],"final_tcp_position":[0.52395,0.07846,0.19596],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.45557,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50874,-0.02038,0.18434],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13514,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.1721,"subtask_id":"reach_object","tcp_end":[0.50873,-0.02264,0.05164],"tcp_start":[0.50874,-0.02038,0.18434],"tcp_to_object_dist_end":0.0261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02244,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26539,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.0859,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16791.0,"raw_peak_contact_force":0.45557,"tcp_end":[0.50059,-0.02245,0.04255],"tcp_start":[0.50873,-0.02264,0.05164],"tcp_to_object_dist_end":0.0212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.51016,-0.02229,0.11113],"object_pos_start":[0.51361,-0.02244,0.02581],"object_to_goal_dist_end":0.21089,"object_to_goal_dist_start":0.26539,"object_z_max":0.111,"peak_contact_force":0.13404,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25090.0,"raw_peak_contact_force":0.16782,"tcp_end":[0.49661,-0.02233,0.13478],"tcp_start":[0.50059,-0.02245,0.04255],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52524,0.05799,0.16417],"object_pos_start":[0.51016,-0.02229,0.11113],"object_to_goal_dist_end":0.1138,"object_to_goal_dist_start":0.21089,"object_z_max":0.16413,"peak_contact_force":0.0,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2641.0,"raw_peak_contact_force":0.25714,"subtask_id":"reach_goal","tcp_end":[0.51958,0.05775,0.19563],"tcp_start":[0.49661,-0.02233,0.13478],"tcp_to_object_dist_end":0.03197,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.53194,0.07274,0.15451],"object_pos_start":[0.52524,0.05799,0.16417],"object_to_goal_dist_end":0.10617,"object_to_goal_dist_start":0.1138,"object_z_max":0.16417,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.52395,0.07846,0.19596],"tcp_start":[0.51958,0.05775,0.19563],"tcp_to_object_dist_end":0.0426,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04717,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.16172,"descend_grasp.grasp_height":0.01547,"descend_place.place_height":0.01426,"lift_object.lift_height":0.14242,"lift_object.lift_speed":0.2179,"release_object.release_duration":0.25676,"transport_goal.arc_height":0.01425,"transport_goal.transport_height":0.02995,"transport_goal.transport_speed":0.03894},"optimized_scores":{"best_composite_score":0.27497,"best_fitness_score":0.87497,"best_task_score":0.81319},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.49896,0.04291,-0.0012],"force_p95":0.28912,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52571,"mean_force":0.06833,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48708,0.04329,0.04343]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8547.0,"contact_point_centroid":[0.48729,0.06203,0.09456],"force_p95":0.10706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32447,"mean_force":0.06618,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48485,0.04309,0.09267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8286.0,"contact_point_centroid":[0.48756,0.0242,0.09901],"force_p95":0.10413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31932,"mean_force":0.06713,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48484,0.04309,0.09672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7672.0,"contact_point_centroid":[0.51811,0.09915,0.17553],"force_p95":0.13464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25712,"mean_force":0.0944,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51257,0.1176,0.1763]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04488,-0.00214],"force_p95":0.15969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22474,"mean_force":0.13268,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48969,0.04353,0.04266]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.557,0.22771,0.16886],"force_p95":0.19745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20975,"mean_force":0.12608,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55199,0.21413,0.17598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8279.0,"contact_point_centroid":[0.5178,0.13515,0.17514],"force_p95":0.13571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18802,"mean_force":0.08802,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51224,0.11682,0.17628]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49805,0.019,0.24971]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49588,0.04166,0.12392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5044.0,"contact_point_centroid":[0.48841,0.02418,0.04452],"force_p95":0.07008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11569,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48854,0.04343,0.04143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5511.0,"contact_point_centroid":[0.48824,0.06274,0.04394],"force_p95":0.06978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07227,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48855,0.04343,0.04144]}],"total_contact_groups":11},"final_pose_error":0.03613,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55669,0.21966,0.13043],"final_tcp_position":[0.55189,0.21436,0.1758],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.52571,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49777,0.0394,0.19917],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15447,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12355.0,"raw_peak_contact_force":0.22474,"subtask_id":"reach_object","tcp_end":[0.49649,0.04415,0.05009],"tcp_start":[0.49777,0.0394,0.19917],"tcp_to_object_dist_end":0.02454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04386,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24312,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1069,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16967.0,"raw_peak_contact_force":0.52571,"tcp_end":[0.48852,0.04343,0.0414],"tcp_start":[0.49649,0.04415,0.05009],"tcp_to_object_dist_end":0.02029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4998,0.04374,0.1447],"object_pos_start":[0.50114,0.04386,0.02552],"object_to_goal_dist_end":0.21126,"object_to_goal_dist_start":0.24312,"object_z_max":0.14453,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15951.0,"raw_peak_contact_force":0.25712,"tcp_end":[0.48504,0.04311,0.16919],"tcp_start":[0.48852,0.04343,0.0414],"tcp_to_object_dist_end":0.0286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.5,0.0441,0.14441],"object_pos_start":[0.4998,0.04374,0.1447],"object_to_goal_dist_end":0.21086,"object_to_goal_dist_start":0.21126,"object_z_max":0.14867,"peak_contact_force":0.0,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":0.20975,"subtask_id":"reach_goal","tcp_end":[0.552,0.21407,0.17601],"tcp_start":[0.48523,0.04365,0.16923],"tcp_to_object_dist_end":0.18053,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55669,0.21966,0.13043],"object_pos_start":[0.55655,0.21882,0.13159],"object_to_goal_dist_end":0.03102,"object_to_goal_dist_start":0.03116,"object_z_max":0.13159,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.55189,0.21436,0.1758],"tcp_start":[0.552,0.21407,0.17601],"tcp_to_object_dist_end":0.04593,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81553,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13942,"descend_grasp.grasp_height":0.00929,"descend_place.place_height":0.00886,"lift_object.lift_height":0.10669,"lift_object.lift_speed":0.17016,"release_object.release_duration":0.69502,"transport_goal.arc_height":0.05931,"transport_goal.transport_height":0.0275,"transport_goal.transport_speed":0.08785},"optimized_scores":{"best_composite_score":0.02594,"best_fitness_score":0.62594,"best_task_score":0.30248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.47299,-0.01956,-0.00124],"force_p95":0.33871,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53253,"mean_force":0.08659,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4627,-0.01961,0.03786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8344.0,"contact_point_centroid":[0.46233,-0.00057,0.07915],"force_p95":0.10292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29912,"mean_force":0.06481,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46031,-0.01954,0.07691]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8817.0,"contact_point_centroid":[0.46232,-0.03848,0.07751],"force_p95":0.10192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29029,"mean_force":0.0621,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46031,-0.01954,0.07576]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6963.0,"contact_point_centroid":[0.49237,-0.00486,0.14099],"force_p95":0.12369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27388,"mean_force":0.08674,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.48652,0.01332,0.14119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6112.0,"contact_point_centroid":[0.49033,0.0295,0.14081],"force_p95":0.15489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24529,"mean_force":0.09857,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.4844,0.01105,0.1405]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.13559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17558,"mean_force":0.12618,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46518,-0.01967,0.03754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":349.0,"contact_point_centroid":[0.46551,3e-05,0.13463],"force_p95":0.11826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1602,"mean_force":0.09164,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.46024,-0.01863,0.13265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":390.0,"contact_point_centroid":[0.46559,-0.03716,0.13464],"force_p95":0.1143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15069,"mean_force":0.08306,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.46024,-0.01858,0.13272]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48734,-0.00855,0.24022]},{"body_a":"world","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47242,-0.01876,0.11109]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.46377,-0.0004,0.03904],"force_p95":0.0657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09664,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01964,0.03645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5392.0,"contact_point_centroid":[0.46365,-0.03889,0.03854],"force_p95":0.06467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08493,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46408,-0.01964,0.03645]}],"total_contact_groups":12},"final_pose_error":0.17274,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52285,0.03819,0.11426],"final_tcp_position":[0.51405,0.04199,0.15066],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.53253,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47553,-0.01779,0.1791],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13402,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12267.0,"raw_peak_contact_force":0.17558,"subtask_id":"reach_object","tcp_end":[0.47183,-0.01982,0.04423],"tcp_start":[0.47553,-0.01779,0.1791],"tcp_to_object_dist_end":0.01873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01971,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.11165,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":17291.0,"raw_peak_contact_force":0.53253,"tcp_end":[0.46405,-0.01964,0.03642],"tcp_start":[0.47183,-0.01982,0.04423],"tcp_to_object_dist_end":0.016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":528.0,"n_steps_budget":600.0,"object_pos_end":[0.47529,-0.0195,0.11226],"object_pos_start":[0.47606,-0.01971,0.02584],"object_to_goal_dist_end":0.24971,"object_to_goal_dist_start":0.28827,"object_z_max":0.11214,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":739.0,"raw_peak_contact_force":0.1602,"tcp_end":[0.46023,-0.01953,0.13091],"tcp_start":[0.46405,-0.01964,0.03642],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":1000.0,"object_pos_end":[0.47536,-0.01949,0.1123],"object_pos_start":[0.47529,-0.0195,0.11226],"object_to_goal_dist_end":0.24965,"object_to_goal_dist_start":0.24971,"object_z_max":0.11556,"peak_contact_force":0.0,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13075.0,"raw_peak_contact_force":0.27388,"subtask_id":"reach_goal","tcp_end":[0.46035,-0.01733,0.13489],"tcp_start":[0.46027,-0.01861,0.13275],"tcp_to_object_dist_end":0.02721,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.52285,0.03819,0.11426],"object_pos_start":[0.47547,-0.01725,0.11568],"object_to_goal_dist_end":0.17936,"object_to_goal_dist_start":0.24694,"object_z_max":0.1224,"peak_contact_force":0.12262,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.51405,0.04199,0.15066],"tcp_start":[0.46035,-0.01733,0.13489],"tcp_to_object_dist_end":0.03764,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```