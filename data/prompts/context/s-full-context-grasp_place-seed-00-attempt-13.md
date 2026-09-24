## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1563 | 0.31 | ❌ rejected |
| 12 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0958 | 0.32 | ❌ rejected |
| 11 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0627 | 0.32 | ❌ rejected |
| 10 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0851 | 0.34 | ❌ rejected |
| 9 | approach → approach → grasp → lift → approach → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0597 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.156) — your mutation base

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

- **Composite score**: -0.156
- **task_score** (E): 0.307
- **fitness_score**: 0.624  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1114 |
| descend_to_grasp | 1.00 | 1.00 | 0.1448 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.67 | 0.2525 |
| transport_to_goal | 0.67 | 1.00 | 0.0556 |
| descend_to_place | 1.00 | 1.00 | 0.2171 |
| release_object | 1.00 | 1.00 | 0.0211 |
| retract_from_place | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.194) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.494, 0.001, 0.194)→(0.492, 0.001, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.049)→(0.484, 0.000, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.333 | 0.143 | 0.197 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.040)→(0.482, 0.000, 0.293) | (0.497, 0.001, 0.026)→(0.490, 0.007, 0.235) | 0.266→0.236 | 0.67 / 28.333 | 0.046 | 0.484 |
| transport_to_goal | approach | 0.67 / step_budget | (0.557, 0.124, 0.433)→(0.577, 0.174, 0.437) | (0.490, 0.007, 0.235)→(0.551, 0.137, 0.021) | 0.236→0.185 | 1.00 / 8.000 | 90993.519 | 2.470 |
| descend_to_place | approach | 1.00 / step_budget | (0.577, 0.174, 0.437)→(0.580, 0.183, 0.220) | (0.550, 0.136, 0.021)→(0.554, 0.133, 0.019) | 0.186→0.187 | 1.00 / 8.667 | 91001.729 | 0.169 |
| release_object | release | 1.00 / step_budget | (0.580, 0.183, 0.220)→(0.575, 0.181, 0.241) | (0.554, 0.133, 0.019)→(0.554, 0.133, 0.019) | 0.187→0.187 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_place | retract | 1.00 / step_budget | (0.575, 0.181, 0.241)→(0.574, 0.181, 0.371) | (0.554, 0.133, 0.019)→(0.554, 0.133, 0.019) | 0.187→0.187 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.443
- phase_score: 0.022
- phase_breakdown.reach_object_score: 0.072
- phase_breakdown.place_goal_score: 0.000
- grasp_place_fitness: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.691
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.443
- **Median Q (composite search score)**: -0.157
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.397


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50641,"average_solve_count":312.0,"average_success_count":312.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.28522,"descend_to_grasp.descend_offset":0.01476,"descend_to_grasp.speed":0.05907,"descend_to_place.place_z_offset":0.02044,"descend_to_place.speed":0.04778,"grasp_object.max_duration":1.11246,"lift_object.lift_height":0.2402,"lift_object.speed":0.11829,"release_object.release_duration":0.47218,"retract_from_place.speed":0.08946,"transport_to_goal.arc_height":0.11581,"transport_to_goal.speed":0.08949},"optimized_scores":{"best_composite_score":-0.22294,"best_fitness_score":0.55706,"best_task_score":0.1752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5809.0,"contact_point_centroid":[0.50275,-0.00065,-0.00219],"force_p95":0.12329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09306,"mean_force":0.13201,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50347,-0.00145,0.41071]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.5111,-0.02208,-0.00133],"force_p95":0.47019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49321,"mean_force":0.1116,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49927,-0.02235,0.04169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7964.0,"contact_point_centroid":[0.50082,-0.00351,0.12759],"force_p95":0.13117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35397,"mean_force":0.08096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49705,-0.02227,0.12587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8260.0,"contact_point_centroid":[0.50073,-0.04102,0.12281],"force_p95":0.13118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29793,"mean_force":0.07704,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49704,-0.02227,0.12139]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02288,-0.00206],"force_p95":0.14013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18194,"mean_force":0.12739,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50172,-0.0224,0.04162]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5137,-0.02302,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50338,-0.00924,0.24749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.50108,-0.00317,0.0431],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13155,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50055,-0.02237,0.04034]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.50711,-0.02089,0.1204]},{"body_a":"world","body_b":"grasp_target","contact_count":2648.0,"contact_point_centroid":[0.5027,-0.00066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55094,0.1445,0.36528]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5027,-0.00066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54786,0.14901,0.25324]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.5027,-0.00066,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.54523,0.1481,0.33775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.50113,-0.04146,0.04217],"force_p95":0.06992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08171,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50056,-0.02237,0.04034]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6083.0,"contact_point_centroid":[0.50421,-0.00041,0.4167],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50383,-0.00041,0.4144]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2853.0,"contact_point_centroid":[0.55144,0.14451,0.36757],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55094,0.1445,0.36525]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.55001,0.14964,0.25059],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54976,0.14963,0.24847]}],"total_contact_groups":15},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5027,-0.00066,0.01602],"final_tcp_position":[0.54584,0.14819,0.40362],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":2.09306,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50838,-0.01931,0.19322],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50868,-0.02256,0.04937],"tcp_start":[0.50838,-0.01931,0.19322],"tcp_to_object_dist_end":0.02389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02237,0.02578],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26537,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13687,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.18194,"tcp_end":[0.50052,-0.02237,0.0403],"tcp_start":[0.50868,-0.02256,0.04937],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.50926,-0.00237,0.12926],"object_pos_start":[0.51361,-0.02237,0.02578],"object_to_goal_dist_end":0.18529,"object_to_goal_dist_start":0.26537,"object_z_max":0.20921,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16302.0,"raw_peak_contact_force":0.49321,"tcp_end":[0.49785,-0.02229,0.26069],"tcp_start":[0.50052,-0.02237,0.0403],"tcp_to_object_dist_end":0.13341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1489.0,"n_steps_budget":1000.0,"object_pos_end":[0.5027,-0.00066,0.01602],"object_pos_start":[0.50926,-0.00237,0.12926],"object_to_goal_dist_end":0.26128,"object_to_goal_dist_start":0.18529,"object_z_max":0.12926,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11892.0,"raw_peak_contact_force":2.09306,"subtask_id":"place_goal","tcp_end":[0.55044,0.13929,0.47895],"tcp_start":[0.50777,0.01022,0.462],"tcp_to_object_dist_end":0.48597,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.5027,-0.00066,0.01602],"object_pos_start":[0.5027,-0.00066,0.01602],"object_to_goal_dist_end":0.26128,"object_to_goal_dist_start":0.26128,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5501.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55113,0.14998,0.25164],"tcp_start":[0.55044,0.13929,0.47895],"tcp_to_object_dist_end":0.28383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5027,-0.00066,0.01602],"object_pos_start":[0.5027,-0.00066,0.01602],"object_to_goal_dist_end":0.26128,"object_to_goal_dist_start":0.26128,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5468,0.14864,0.2735],"tcp_start":[0.55113,0.14998,0.25164],"tcp_to_object_dist_end":0.30088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.5027,-0.00066,0.01602],"object_pos_start":[0.5027,-0.00066,0.01602],"object_to_goal_dist_end":0.26128,"object_to_goal_dist_start":0.26128,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.54584,0.14819,0.40362],"tcp_start":[0.5468,0.14864,0.2735],"tcp_to_object_dist_end":0.41744,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32464,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.18616,"descend_to_grasp.descend_offset":0.01393,"descend_to_grasp.speed":0.11175,"descend_to_place.place_z_offset":0.02819,"descend_to_place.speed":0.05199,"grasp_object.max_duration":1.28102,"lift_object.lift_height":0.30755,"lift_object.speed":0.03319,"release_object.release_duration":0.57701,"retract_from_place.speed":0.0862,"transport_to_goal.arc_height":0.17258,"transport_to_goal.speed":0.14585},"optimized_scores":{"best_composite_score":-0.08861,"best_fitness_score":0.69139,"best_task_score":0.44309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":280.0,"contact_point_centroid":[0.55967,0.23184,-0.00866],"force_p95":1.58636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53822,"mean_force":0.41061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55456,0.22003,0.40974]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49833,0.04297,-0.0015],"force_p95":0.45919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49862,"mean_force":0.13917,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48735,0.04316,0.0413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18930.0,"contact_point_centroid":[0.48569,0.06211,0.18131],"force_p95":0.07932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30762,"mean_force":0.05449,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48532,0.04298,0.1791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8232.0,"contact_point_centroid":[0.50301,0.0599,0.3841],"force_p95":0.13204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28226,"mean_force":0.07619,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49922,0.07862,0.38416]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19096.0,"contact_point_centroid":[0.48586,0.02389,0.18522],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26444,"mean_force":0.05366,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48533,0.04298,0.18282]},{"body_a":"world","body_b":"grasp_target","contact_count":2311.0,"contact_point_centroid":[0.56505,0.22731,-0.00208],"force_p95":0.20035,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26215,"mean_force":0.12894,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55984,0.2379,0.28592]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04486,-0.00215],"force_p95":0.16338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22974,"mean_force":0.13362,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48963,0.04338,0.04126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8781.0,"contact_point_centroid":[0.50386,0.09846,0.38498],"force_p95":0.11953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22744,"mean_force":0.072,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49968,0.0798,0.38503]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50118,0.04505,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49831,0.0182,0.24709]},{"body_a":"world","body_b":"grasp_target","contact_count":1772.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49586,0.04086,0.1198]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56574,0.22686,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55677,0.24062,0.18442]},{"body_a":"world","body_b":"grasp_target","contact_count":1960.0,"contact_point_centroid":[0.56574,0.22686,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.55324,0.2388,0.2689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.48838,0.02403,0.04317],"force_p95":0.07078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11736,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04328,0.04003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5526.0,"contact_point_centroid":[0.4882,0.0626,0.04257],"force_p95":0.07049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07314,"mean_force":0.04092,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4885,0.04328,0.04004]},{"body_a":"left_finger","body_b":"right_finger","contact_count":341.0,"contact_point_centroid":[0.55674,0.22453,0.4084],"force_p95":0.01444,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01589,"mean_force":0.01148,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55623,0.22451,0.40627]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2574.0,"contact_point_centroid":[0.56033,0.23779,0.2922],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.55982,0.23775,0.28995]}],"total_contact_groups":17},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56574,0.22686,0.02602],"final_tcp_position":[0.55377,0.23894,0.33462],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":272980.31251,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49786,0.03794,0.19273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":443.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49645,0.04399,0.04869],"tcp_start":[0.49786,0.03794,0.19273],"tcp_to_object_dist_end":0.02318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04373,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24325,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15748,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12363.0,"raw_peak_contact_force":0.22974,"tcp_end":[0.48846,0.04327,0.04],"tcp_start":[0.49645,0.04399,0.04869],"tcp_to_object_dist_end":0.01928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":988.0,"n_steps_budget":1000.0,"object_pos_end":[0.49308,0.04301,0.30626],"object_pos_start":[0.50114,0.04373,0.02548],"object_to_goal_dist_end":0.26697,"object_to_goal_dist_start":0.24325,"object_z_max":0.30599,"peak_contact_force":0.06937,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38114.0,"raw_peak_contact_force":0.49862,"tcp_end":[0.48644,0.04307,0.32771],"tcp_start":[0.48846,0.04327,0.04],"tcp_to_object_dist_end":0.02245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.55482,0.23737,0.03099],"object_pos_start":[0.49308,0.04301,0.30626],"object_to_goal_dist_end":0.11642,"object_to_goal_dist_start":0.26697,"object_z_max":0.39452,"peak_contact_force":272980.31251,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17634.0,"raw_peak_contact_force":2.53822,"subtask_id":"place_goal","tcp_end":[0.55943,0.23365,0.39723],"tcp_start":[0.55897,0.23158,0.4006],"tcp_to_object_dist_end":0.36629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.56574,0.22686,0.02602],"object_pos_start":[0.55463,0.23603,0.03033],"object_to_goal_dist_end":0.1221,"object_to_goal_dist_start":0.11719,"object_z_max":0.03033,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4885.0,"raw_peak_contact_force":0.26215,"subtask_id":"place_goal","tcp_end":[0.56073,0.24247,0.18367],"tcp_start":[0.55943,0.23365,0.39723],"tcp_to_object_dist_end":0.15851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56574,0.22686,0.02602],"object_pos_start":[0.56574,0.22686,0.02602],"object_to_goal_dist_end":0.1221,"object_to_goal_dist_start":0.1221,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.5554,0.23992,0.20432],"tcp_start":[0.56073,0.24247,0.18367],"tcp_to_object_dist_end":0.17907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.56574,0.22686,0.02602],"object_pos_start":[0.56574,0.22686,0.02602],"object_to_goal_dist_end":0.1221,"object_to_goal_dist_start":0.1221,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1960.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55377,0.23894,0.33462],"tcp_start":[0.5554,0.23992,0.20432],"tcp_to_object_dist_end":0.30907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50435,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.19695,"descend_to_grasp.descend_offset":0.01318,"descend_to_grasp.speed":0.07345,"descend_to_place.place_z_offset":0.02662,"descend_to_place.speed":0.0622,"grasp_object.max_duration":1.33653,"lift_object.lift_height":0.26911,"lift_object.speed":0.03638,"release_object.release_duration":0.51906,"retract_from_place.speed":0.09816,"transport_to_goal.arc_height":0.05326,"transport_to_goal.speed":0.15148},"optimized_scores":{"best_composite_score":-0.15742,"best_fitness_score":0.62258,"best_task_score":0.30412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":658.0,"contact_point_centroid":[0.59086,0.1711,-0.00452],"force_p95":1.33966,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.77753,"mean_force":0.25961,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60622,0.13246,0.43511]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.47237,-0.01939,-0.00143],"force_p95":0.44938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46082,"mean_force":0.17985,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46321,-0.01955,0.04149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9982.0,"contact_point_centroid":[0.49873,0.03567,0.35758],"force_p95":0.12127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36583,"mean_force":0.07523,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49509,0.01702,0.35747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16995.0,"contact_point_centroid":[0.46107,-0.03858,0.16791],"force_p95":0.07486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26854,"mean_force":0.05137,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46101,-0.01947,0.16598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16168.0,"contact_point_centroid":[0.46114,-0.0003,0.16442],"force_p95":0.07529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26712,"mean_force":0.05337,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46099,-0.01947,0.16223]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9757.0,"contact_point_centroid":[0.49559,-0.00455,0.35294],"force_p95":0.12202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21584,"mean_force":0.07464,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49236,0.01416,0.35317]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02007,-0.00205],"force_p95":0.13757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17867,"mean_force":0.12667,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46528,-0.01959,0.04151]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.47616,-0.02015,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48844,-0.00799,0.24844]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.59378,0.17295,-0.00199],"force_p95":0.12269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12308,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.6249,0.1529,0.3307]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.47316,-0.0182,0.12062]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59378,0.17295,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62413,0.15633,0.22507]},{"body_a":"world","body_b":"grasp_target","contact_count":2060.0,"contact_point_centroid":[0.59378,0.17295,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.62121,0.15527,0.30893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.46424,-0.00035,0.04282],"force_p95":0.06781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09881,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46419,-0.01957,0.04041]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46409,-0.03878,0.04234],"force_p95":0.06657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08394,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46419,-0.01957,0.04041]},{"body_a":"left_finger","body_b":"right_finger","contact_count":864.0,"contact_point_centroid":[0.60419,0.12985,0.43716],"force_p95":0.01286,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01916,"mean_force":0.01075,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60371,0.12985,0.43493]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2337.0,"contact_point_centroid":[0.62548,0.15291,0.33318],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"approach","tcp_position_centroid":[0.62489,0.1529,0.33093]}],"total_contact_groups":17},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.59378,0.17295,0.01602],"final_tcp_position":[0.62195,0.1554,0.37462],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273010.21675,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47709,-0.01677,0.19456],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1904.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47189,-0.01974,0.04821],"tcp_start":[0.47709,-0.01677,0.19456],"tcp_to_object_dist_end":0.02261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01968,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13572,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11788.0,"raw_peak_contact_force":0.17867,"tcp_end":[0.46416,-0.01956,0.04038],"tcp_start":[0.47189,-0.01974,0.04821],"tcp_to_object_dist_end":0.01882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.46875,-0.01945,0.26991],"object_pos_start":[0.47607,-0.01968,0.02581],"object_to_goal_dist_end":0.25447,"object_to_goal_dist_start":0.28826,"object_z_max":0.26962,"peak_contact_force":0.06954,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33245.0,"raw_peak_contact_force":0.46082,"tcp_end":[0.46177,-0.01949,0.28963],"tcp_start":[0.46416,-0.01956,0.04038],"tcp_to_object_dist_end":0.02093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1108.0,"n_steps_budget":1000.0,"object_pos_end":[0.5943,0.17332,0.01702],"object_pos_start":[0.46875,-0.01945,0.26991],"object_to_goal_dist_end":0.17749,"object_to_goal_dist_start":0.25447,"object_z_max":0.38317,"peak_contact_force":0.12312,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21261.0,"raw_peak_contact_force":2.77753,"subtask_id":"place_goal","tcp_end":[0.622,0.14876,0.43535],"tcp_start":[0.60402,0.13015,0.43501],"tcp_to_object_dist_end":0.41996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.59378,0.17295,0.01602],"object_pos_start":[0.59374,0.17294,0.01602],"object_to_goal_dist_end":0.17855,"object_to_goal_dist_start":0.17855,"object_z_max":0.01602,"peak_contact_force":273004.94191,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4533.0,"raw_peak_contact_force":0.12308,"subtask_id":"place_goal","tcp_end":[0.62778,0.15744,0.22561],"tcp_start":[0.622,0.14876,0.43535],"tcp_to_object_dist_end":0.2129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59378,0.17295,0.01602],"object_pos_start":[0.59378,0.17295,0.01602],"object_to_goal_dist_end":0.17855,"object_to_goal_dist_start":0.17855,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62291,0.1559,0.24441],"tcp_start":[0.62778,0.15744,0.22561],"tcp_to_object_dist_end":0.23087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":960.0,"object_pos_end":[0.59378,0.17295,0.01602],"object_pos_start":[0.59378,0.17295,0.01602],"object_to_goal_dist_end":0.17855,"object_to_goal_dist_start":0.17855,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2060.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62195,0.1554,0.37462],"tcp_start":[0.62291,0.1559,0.24441],"tcp_to_object_dist_end":0.36013,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```