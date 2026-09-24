## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0898 | 0.33 | ❌ rejected |
| 7 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1336 | 0.47 | ✅ accepted |
| 6 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2102 | 0.30 | ❌ rejected |
| 5 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1505 | 0.32 | ✅ accepted |
| 4 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6552 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.090) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  weight: 0.7
phases:
- id: approach_above
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
    - 0.15
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_to_grasp
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: grasp_object
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
  parameters:
    max_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
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
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
- id: approach_goal
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
    - 0.25
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: descend_to_goal
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_grasp** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.090
- **task_score** (E): 0.333
- **fitness_score**: 0.640  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1114 |
| descend_to_grasp | 1.00 | 1.00 | 0.1483 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1414 |
| approach_goal | 1.00 | 0.67 | 0.2569 |
| descend_to_goal | 1.00 | 1.00 | 0.1266 |
| release_object | 1.00 | 1.00 | 0.0213 |
| retract | 1.00 | 1.00 | 0.1932 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.194) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.494, 0.001, 0.194)→(0.492, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.045)→(0.484, 0.000, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 43.000 | 0.144 | 0.200 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.037)→(0.481, 0.000, 0.178) | (0.497, 0.000, 0.026)→(0.491, 0.000, 0.164) | 0.266→0.223 | 1.00 / 37.000 | 22.215 | 0.493 |
| approach_goal | approach | 1.00 / step_budget | (0.481, 0.000, 0.178)→(0.576, 0.175, 0.321) | (0.491, 0.000, 0.164)→(0.585, 0.170, 0.187) | 0.223→0.140 | 0.67 / 14.667 | 91003.035 | 0.916 |
| descend_to_goal | approach | 1.00 / step_budget | (0.576, 0.175, 0.321)→(0.579, 0.183, 0.195) | (0.585, 0.170, 0.187)→(0.584, 0.176, 0.067) | 0.140→0.122 | 1.00 / 14.000 | 91001.778 | 0.807 |
| release_object | release | 1.00 / step_budget | (0.579, 0.183, 0.195)→(0.574, 0.181, 0.215) | (0.584, 0.176, 0.067)→(0.584, 0.176, 0.019) | 0.122→0.168 | 1.00 / 4.000 | 0.111 | 0.634 |
| retract | retract | 1.00 / step_budget | (0.574, 0.181, 0.215)→(0.573, 0.180, 0.408) | (0.584, 0.176, 0.019)→(0.584, 0.177, 0.019) | 0.168→0.168 | 1.00 / 4.000 | 0.123 | 0.131 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.415
- phase_score: 0.595
- phase_breakdown.reach_object_score: 0.067
- phase_breakdown.place_goal_score: 0.821
- grasp_place_fitness: 0.681

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.681
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.415
- **Median Q (composite search score)**: -0.090
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.438


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6867,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.1335,"approach_goal.speed":0.18181,"descend_to_goal.speed":0.1456,"descend_to_grasp.descend_offset":0.01056,"descend_to_grasp.speed":0.06476,"grasp_object.max_duration":1.71518,"lift_object.lift_height":0.11284,"lift_object.speed":0.03311,"release_object.max_duration":0.30582,"retract.retract_height":0.23757,"retract.speed":0.1297},"optimized_scores":{"best_composite_score":-0.13063,"best_fitness_score":0.59937,"best_task_score":0.25151},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":606.0,"contact_point_centroid":[0.55757,0.13119,-0.0042],"force_p95":0.99997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29372,"mean_force":0.22401,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54502,0.12855,0.33381]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.5097,-0.0221,-0.00153],"force_p95":0.43224,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45464,"mean_force":0.20157,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49931,-0.02236,0.03688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8124.0,"contact_point_centroid":[0.51414,0.04789,0.19764],"force_p95":0.10753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33335,"mean_force":0.06874,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51082,0.02921,0.19626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7094.0,"contact_point_centroid":[0.51241,0.00607,0.19227],"force_p95":0.12798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27855,"mean_force":0.07559,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50945,0.02497,0.19053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6834.0,"contact_point_centroid":[0.49661,-0.00309,0.08317],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26495,"mean_force":0.05251,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49675,-0.02228,0.08081]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7173.0,"contact_point_centroid":[0.49647,-0.04144,0.08299],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25177,"mean_force":0.05078,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49675,-0.02228,0.08108]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02286,-0.00206],"force_p95":0.14018,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18224,"mean_force":0.12739,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50161,-0.02241,0.03739]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50338,-0.00924,0.24749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.50101,-0.00318,0.03887],"force_p95":0.07773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12896,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50044,-0.02238,0.03611]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.55751,0.13089,-0.00199],"force_p95":0.12277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12333,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55,0.14641,0.29345]},{"body_a":"world","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50709,-0.02089,0.11824]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55751,0.13089,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54717,0.14878,0.23255]},{"body_a":"world","body_b":"grasp_target","contact_count":2900.0,"contact_point_centroid":[0.55751,0.13089,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54475,0.14793,0.3605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.50105,-0.04147,0.03794],"force_p95":0.06986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08019,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50044,-0.02238,0.03611]},{"body_a":"left_finger","body_b":"right_finger","contact_count":529.0,"contact_point_centroid":[0.5464,0.13144,0.34001],"force_p95":0.0137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.0109,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54602,0.13143,0.3378]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1386.0,"contact_point_centroid":[0.55049,0.14641,0.29567],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55,0.14641,0.29347]}],"total_contact_groups":17},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55751,0.13089,0.01602],"final_tcp_position":[0.54612,0.14821,0.47048],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273009.0208,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50838,-0.01931,0.19322],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50862,-0.02257,0.04513],"tcp_start":[0.50838,-0.01931,0.19322],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.02235,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26535,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13668,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.18224,"tcp_end":[0.50041,-0.02238,0.03608],"tcp_start":[0.50862,-0.02257,0.04513],"tcp_to_object_dist_end":0.01673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.50724,-0.02221,0.11736],"object_pos_start":[0.51359,-0.02235,0.02579],"object_to_goal_dist_end":0.20826,"object_to_goal_dist_start":0.26535,"object_z_max":0.11709,"peak_contact_force":28.12934,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14099.0,"raw_peak_contact_force":0.45464,"tcp_end":[0.49653,-0.02227,0.12942],"tcp_start":[0.50041,-0.02238,0.03608],"tcp_to_object_dist_end":0.01613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.55749,0.13092,0.01599],"object_pos_start":[0.50724,-0.02221,0.11736],"object_to_goal_dist_end":0.20707,"object_to_goal_dist_start":0.20826,"object_z_max":0.25772,"peak_contact_force":273009.0208,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16353.0,"raw_peak_contact_force":2.29372,"subtask_id":"place_goal","tcp_end":[0.55019,0.14349,0.3544],"tcp_start":[0.49653,-0.02227,0.12942],"tcp_to_object_dist_end":0.33872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.55751,0.13089,0.01602],"object_pos_start":[0.55749,0.13092,0.01599],"object_to_goal_dist_end":0.20704,"object_to_goal_dist_start":0.20707,"object_z_max":0.01602,"peak_contact_force":273005.08945,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2690.0,"raw_peak_contact_force":0.12333,"subtask_id":"place_goal","tcp_end":[0.55072,0.14981,0.23091],"tcp_start":[0.55019,0.14349,0.3544],"tcp_to_object_dist_end":0.21583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55751,0.13089,0.01602],"object_pos_start":[0.55751,0.13089,0.01602],"object_to_goal_dist_end":0.20704,"object_to_goal_dist_start":0.20704,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54597,0.14839,0.25283],"tcp_start":[0.55072,0.14981,0.23091],"tcp_to_object_dist_end":0.23774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.55751,0.13089,0.01602],"object_pos_start":[0.55751,0.13089,0.01602],"object_to_goal_dist_end":0.20704,"object_to_goal_dist_start":0.20704,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2900.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54612,0.14821,0.47048],"tcp_start":[0.54597,0.14839,0.25283],"tcp_to_object_dist_end":0.45493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54789,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.18423,"approach_goal.speed":0.08275,"descend_to_goal.speed":0.0659,"descend_to_grasp.descend_offset":0.0104,"descend_to_grasp.speed":0.06613,"grasp_object.max_duration":1.42216,"lift_object.lift_height":0.13082,"lift_object.speed":0.04765,"release_object.max_duration":0.30214,"retract.retract_height":0.15347,"retract.speed":0.11386},"optimized_scores":{"best_composite_score":-0.04896,"best_fitness_score":0.68104,"best_task_score":0.41516},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.58074,0.23938,-0.00326],"force_p95":0.60411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08429,"mean_force":0.17787,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55846,0.23828,0.20272]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49721,0.04278,-0.00153],"force_p95":0.49836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52763,"mean_force":0.18375,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48729,0.04317,0.03766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12103.0,"contact_point_centroid":[0.5164,0.14356,0.20423],"force_p95":0.10724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3119,"mean_force":0.06389,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51429,0.12456,0.2027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8374.0,"contact_point_centroid":[0.48423,0.06212,0.09215],"force_p95":0.076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30238,"mean_force":0.0501,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48478,0.04294,0.09061]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7884.0,"contact_point_centroid":[0.48459,0.02372,0.09166],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28474,"mean_force":0.05178,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48479,0.04294,0.08945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12028.0,"contact_point_centroid":[0.51898,0.11171,0.20874],"force_p95":0.1035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23978,"mean_force":0.06392,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51664,0.13053,0.20698]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04477,-0.00216],"force_p95":0.16818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23886,"mean_force":0.13437,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48951,0.04339,0.03766]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3830.0,"contact_point_centroid":[0.48931,0.02401,0.03943],"force_p95":0.08603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16157,"mean_force":0.05522,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48837,0.04328,0.03644]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49831,0.0182,0.24709]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49573,0.04085,0.11805]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58067,0.23964,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55569,0.23993,0.15585]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.58067,0.23964,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55178,0.23801,0.24199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5532.0,"contact_point_centroid":[0.4881,0.06238,0.03905],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08096,"mean_force":0.04051,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48838,0.04328,0.03644]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1014.0,"contact_point_centroid":[0.55913,0.23874,0.19897],"force_p95":0.01276,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01077,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55863,0.23871,0.19677]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.55874,0.2412,0.15381],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55827,0.24116,0.15156]}],"total_contact_groups":15},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.58067,0.23964,0.01602],"final_tcp_position":[0.55227,0.23814,0.30938],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":38.43602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49786,0.03794,0.19273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49641,0.044,0.04509],"tcp_start":[0.49786,0.03794,0.19273],"tcp_to_object_dist_end":0.01969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.0435,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24345,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15886,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11162.0,"raw_peak_contact_force":0.23886,"tcp_end":[0.48834,0.04328,0.03641],"tcp_start":[0.49641,0.044,0.04509],"tcp_to_object_dist_end":0.01683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.49494,0.04296,0.13417],"object_pos_start":[0.50114,0.0435,0.02548],"object_to_goal_dist_end":0.2139,"object_to_goal_dist_start":0.24345,"object_z_max":0.13389,"peak_contact_force":38.43602,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16346.0,"raw_peak_contact_force":0.52763,"tcp_end":[0.48469,0.04293,0.14758],"tcp_start":[0.48834,0.04328,0.03641],"tcp_to_object_dist_end":0.01688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":802.0,"n_steps_budget":1000.0,"object_pos_end":[0.57375,0.23056,0.24423],"object_pos_start":[0.49494,0.04296,0.13417],"object_to_goal_dist_end":0.09894,"object_to_goal_dist_start":0.2139,"object_z_max":0.25362,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24131.0,"raw_peak_contact_force":0.3119,"subtask_id":"place_goal","tcp_end":[0.55804,0.23378,0.28156],"tcp_start":[0.48469,0.04293,0.14758],"tcp_to_object_dist_end":0.04062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.58067,0.23964,0.01602],"object_pos_start":[0.57375,0.23056,0.24423],"object_to_goal_dist_end":0.13187,"object_to_goal_dist_start":0.09894,"object_z_max":0.24423,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2106.0,"raw_peak_contact_force":2.08429,"subtask_id":"place_goal","tcp_end":[0.56005,0.24189,0.15508],"tcp_start":[0.55804,0.23378,0.28156],"tcp_to_object_dist_end":0.1406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58067,0.23964,0.01602],"object_pos_start":[0.58067,0.23964,0.01602],"object_to_goal_dist_end":0.13187,"object_to_goal_dist_start":0.13187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55415,0.23918,0.17577],"tcp_start":[0.56005,0.24189,0.15508],"tcp_to_object_dist_end":0.16194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":840.0,"object_pos_end":[0.58067,0.23964,0.01602],"object_pos_start":[0.58067,0.23964,0.01602],"object_to_goal_dist_end":0.13187,"object_to_goal_dist_start":0.13187,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55227,0.23814,0.30938],"tcp_start":[0.55415,0.23918,0.17577],"tcp_to_object_dist_end":0.29473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66909,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.2003,"approach_goal.speed":0.0932,"descend_to_goal.speed":0.09784,"descend_to_grasp.descend_offset":0.01058,"descend_to_grasp.speed":0.15661,"grasp_object.max_duration":1.29608,"lift_object.lift_height":0.23917,"lift_object.speed":0.05185,"release_object.max_duration":0.39999,"retract.retract_height":0.24817,"retract.speed":0.09854},"optimized_scores":{"best_composite_score":-0.08997,"best_fitness_score":0.64003,"best_task_score":0.33326},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":228.0,"contact_point_centroid":[0.61504,0.16056,-0.00641],"force_p95":1.00311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65683,"mean_force":0.31306,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62135,0.15525,0.20869]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.47335,-0.01965,-0.0014],"force_p95":0.42591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49728,"mean_force":0.12514,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46305,-0.01955,0.03887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14322.0,"contact_point_centroid":[0.46114,-0.03857,0.14557],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28029,"mean_force":0.05333,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46085,-0.01948,0.14345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13684.0,"contact_point_centroid":[0.46117,-0.00035,0.14689],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27953,"mean_force":0.05521,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46085,-0.01948,0.14442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":665.0,"contact_point_centroid":[0.625,0.17524,0.18984],"force_p95":0.13497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23499,"mean_force":0.08172,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62489,0.15639,0.19385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":819.0,"contact_point_centroid":[0.62393,0.13785,0.19022],"force_p95":0.10424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21892,"mean_force":0.06716,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62491,0.15639,0.19387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5161.0,"contact_point_centroid":[0.62178,0.17047,0.27308],"force_p95":0.11591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21477,"mean_force":0.0663,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.62232,0.15166,0.27368]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5400.0,"contact_point_centroid":[0.6218,0.13298,0.26772],"force_p95":0.10845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20507,"mean_force":0.06636,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.6226,0.15199,0.26838]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00205],"force_p95":0.13783,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17874,"mean_force":0.12674,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46526,-0.0196,0.03886]},{"body_a":"world","body_b":"grasp_target","contact_count":3564.0,"contact_point_centroid":[0.61498,0.16054,-0.00198],"force_p95":0.124,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14725,"mean_force":0.12197,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61984,0.15466,0.33008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13083.0,"contact_point_centroid":[0.54079,0.08329,0.29208],"force_p95":0.08501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14315,"mean_force":0.05589,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53947,0.06427,0.29019]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.47616,-0.02015,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48844,-0.00799,0.24844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13123.0,"contact_point_centroid":[0.54208,0.0466,0.2926],"force_p95":0.08292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13755,"mean_force":0.05648,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54078,0.06563,0.29082]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47329,-0.01821,0.11938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.46421,-0.00036,0.04019],"force_p95":0.06783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10292,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46416,-0.01957,0.03776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46407,-0.03879,0.03971],"force_p95":0.0666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08469,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46416,-0.01957,0.03777]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61498,0.16054,0.02602],"final_tcp_position":[0.62161,0.15502,0.44549],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.65683,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47709,-0.01677,0.19456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4719,-0.01975,0.04557],"tcp_start":[0.47709,-0.01677,0.19456],"tcp_to_object_dist_end":0.02001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01967,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13589,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11787.0,"raw_peak_contact_force":0.17874,"tcp_end":[0.46413,-0.01957,0.03774],"tcp_start":[0.4719,-0.01975,0.04557],"tcp_to_object_dist_end":0.01687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.46994,-0.01945,0.23979],"object_pos_start":[0.47606,-0.01967,0.02581],"object_to_goal_dist_end":0.2459,"object_to_goal_dist_start":0.28826,"object_z_max":0.23951,"peak_contact_force":0.07928,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28087.0,"raw_peak_contact_force":0.49728,"tcp_end":[0.46145,-0.01949,0.25725],"tcp_start":[0.46413,-0.01957,0.03774],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.62248,0.14821,0.30179],"object_pos_start":[0.46994,-0.01945,0.23979],"object_to_goal_dist_end":0.11267,"object_to_goal_dist_start":0.2459,"object_z_max":0.30175,"peak_contact_force":0.0847,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26206.0,"raw_peak_contact_force":0.14315,"subtask_id":"place_goal","tcp_end":[0.62032,0.14843,0.32754],"tcp_start":[0.46145,-0.01949,0.25725],"tcp_to_object_dist_end":0.02584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.61454,0.15628,0.1691],"object_pos_start":[0.62248,0.14821,0.30179],"object_to_goal_dist_end":0.02704,"object_to_goal_dist_start":0.11267,"object_z_max":0.30179,"peak_contact_force":0.12116,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10561.0,"raw_peak_contact_force":0.21477,"subtask_id":"place_goal","tcp_end":[0.62683,0.15688,0.19845],"tcp_start":[0.62032,0.14843,0.32754],"tcp_to_object_dist_end":0.03183,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61373,0.15815,0.02502],"object_pos_start":[0.61454,0.15628,0.1691],"object_to_goal_dist_end":0.16595,"object_to_goal_dist_start":0.02704,"object_z_max":0.1691,"peak_contact_force":0.08755,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1712.0,"raw_peak_contact_force":1.65683,"tcp_end":[0.62131,0.15524,0.21731],"tcp_start":[0.62683,0.15688,0.19845],"tcp_to_object_dist_end":0.19246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.61498,0.16054,0.02602],"object_pos_start":[0.61373,0.15815,0.02502],"object_to_goal_dist_end":0.16482,"object_to_goal_dist_start":0.16595,"object_z_max":0.02665,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3564.0,"raw_peak_contact_force":0.14725,"tcp_end":[0.62161,0.15502,0.44549],"tcp_start":[0.62131,0.15524,0.21731],"tcp_to_object_dist_end":0.41956,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```