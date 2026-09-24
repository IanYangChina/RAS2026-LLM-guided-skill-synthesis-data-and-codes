## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1151 | 0.28 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1379 | 0.22 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2321 | 0.23 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1538 | 0.26 | ✅ accepted |
| 4 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1730 | 0.17 | ❌ rejected |

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

## Current Skill (Q=0.115) — your mutation base

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
- id: transport_goal
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
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grip_during_transport
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
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
    - 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    place_height:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
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
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grip_during_transport, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.115
- **task_score** (E): 0.284
- **fitness_score**: 0.615  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1495 |
| descend_grasp | 1.00 | 1.00 | 0.1103 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 0.67 | 0.0949 |
| transport_goal | 0.00 | 0.67 | 0.0593 |
| descend_place | 0.33 | 1.00 | 0.1119 |
| release_object | 1.00 | 1.00 | 0.0232 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.000, 0.155) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.000, 0.155)→(0.492, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 45.000 | 0.141 | 0.193 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.045)→(0.484, 0.000, 0.036) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 23.000 | 524.436 | 0.547 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.036)→(0.480, 0.000, 0.131) | (0.497, 0.001, 0.026)→(0.495, 0.001, 0.113) | 0.266→0.225 | 0.67 / 12.667 | 0.003 | 0.306 |
| transport_goal | approach | 0.00 / guard_failure | (0.480, 0.000, 0.131)→(0.505, 0.039, 0.165) | (0.495, 0.001, 0.113)→(0.495, 0.001, 0.113) | 0.225→0.225 | 0.67 / 5.333 | 0.082 | 1.250 |
| descend_place | descend | 0.33 / step_budget | (0.505, 0.039, 0.165)→(0.552, 0.135, 0.183) | (0.517, 0.041, 0.138)→(0.540, 0.100, 0.028) | 0.171→0.186 | 1.00 / 4.000 | 0.123 | 0.531 |
| release_object | release | 1.00 / step_budget | (0.552, 0.135, 0.183)→(0.547, 0.134, 0.205) | (0.540, 0.100, 0.028)→(0.543, 0.105, 0.016) | 0.186→0.195 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.399
- phase_score: 0.350
- phase_breakdown.reach_goal_score: 0.210
- phase_breakdown.reach_object_score: 0.560
- grasp_place_fitness: 0.666

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.399
- **Median Q (composite search score)**: 0.097
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93103,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.08071,"descend_grasp.grasp_height":0.00425,"descend_place.place_height":0.01206,"lift_object.lift_height":0.10693,"release_object.release_duration":0.7685,"transport_goal.transport_height":0.1586,"transport_goal.transport_speed":0.43237},"optimized_scores":{"best_composite_score":0.08167,"best_fitness_score":0.58167,"best_task_score":0.20806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3668.0,"contact_point_centroid":[0.52227,0.042,-0.00225],"force_p95":0.12805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63451,"mean_force":0.13545,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52225,0.07132,0.19063]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.51054,-0.0219,-0.00113],"force_p95":0.47114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65144,"mean_force":0.08635,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49854,-0.02239,0.03141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.50345,-0.02731,0.14004],"force_p95":0.1882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38883,"mean_force":0.1092,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.49797,-0.00879,0.14021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8898.0,"contact_point_centroid":[0.49857,-0.00342,0.07364],"force_p95":0.10776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33545,"mean_force":0.06889,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4959,-0.02232,0.0717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9638.0,"contact_point_centroid":[0.49869,-0.0411,0.07218],"force_p95":0.10231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30839,"mean_force":0.06457,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49593,-0.02232,0.0708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.50384,0.0097,0.13999],"force_p95":0.17188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28297,"mean_force":0.09836,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.49802,-0.00863,0.14042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.51035,0.02899,0.16388],"force_p95":0.20928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24948,"mean_force":0.0539,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50502,0.01367,0.16936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7.0,"contact_point_centroid":[0.51226,-0.00406,0.16174],"force_p95":0.16416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1943,"mean_force":0.07053,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5048,0.01238,0.16898]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02284,-0.00205],"force_p95":0.13913,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18085,"mean_force":0.12711,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50127,-0.02246,0.03097]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.5137,-0.02302,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50326,-0.01042,0.20925]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50733,-0.02188,0.07864]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52228,0.04203,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53384,0.11282,0.21267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.50079,-0.00323,0.03244],"force_p95":0.07754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12224,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50009,-0.02243,0.02969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.5008,-0.04153,0.03151],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08508,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50009,-0.02243,0.0297]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3645.0,"contact_point_centroid":[0.52367,0.07438,0.19425],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01553,"mean_force":0.01053,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52332,0.07438,0.19199]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.53639,0.1134,0.21007],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53618,0.1134,0.20767]}],"total_contact_groups":16},"final_pose_error":0.04812,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.52228,0.04203,0.01602],"final_tcp_position":[0.5374,0.11351,0.20993],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50872,-0.02121,0.11915],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13551,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10811.0,"raw_peak_contact_force":0.18085,"subtask_id":"reach_object","tcp_end":[0.50835,-0.02262,0.0387],"tcp_start":[0.50872,-0.02121,0.11915],"tcp_to_object_dist_end":0.01377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02235,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26534,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":1573.09317,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":18672.0,"raw_peak_contact_force":0.65144,"tcp_end":[0.50006,-0.02243,0.02966],"tcp_start":[0.50835,-0.02262,0.0387],"tcp_to_object_dist_end":0.01405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.51208,-0.02221,0.11158],"object_pos_start":[0.51357,-0.02235,0.02581],"object_to_goal_dist_end":0.2102,"object_to_goal_dist_start":0.26534,"object_z_max":0.11148,"peak_contact_force":0.01017,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4032.0,"raw_peak_contact_force":0.38883,"tcp_end":[0.49595,-0.02231,0.1247],"tcp_start":[0.50006,-0.02243,0.02966],"tcp_to_object_dist_end":0.02079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.51215,-0.02221,0.11161],"object_pos_start":[0.51208,-0.02221,0.11158],"object_to_goal_dist_end":0.21016,"object_to_goal_dist_start":0.2102,"object_z_max":0.14547,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7409.0,"raw_peak_contact_force":1.63451,"subtask_id":"reach_goal","tcp_end":[0.50476,0.01227,0.16888],"tcp_start":[0.49601,-0.02231,0.12477],"tcp_to_object_dist_end":0.06725,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52228,0.04203,0.01602],"object_pos_start":[0.51846,0.01344,0.14547],"object_to_goal_dist_end":0.23549,"object_to_goal_dist_start":0.16195,"object_z_max":0.14547,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.5374,0.11351,0.20993],"tcp_start":[0.50476,0.01227,0.16888],"tcp_to_object_dist_end":0.20722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52228,0.04203,0.01602],"object_pos_start":[0.52228,0.04203,0.01602],"object_to_goal_dist_end":0.23549,"object_to_goal_dist_start":0.23549,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53249,0.1125,0.23314],"tcp_start":[0.5374,0.11351,0.20993],"tcp_to_object_dist_end":0.2285,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88496,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13472,"descend_grasp.grasp_height":0.01675,"descend_place.place_height":0.01564,"lift_object.lift_height":0.10719,"release_object.release_duration":0.57932,"transport_goal.transport_height":0.20147,"transport_goal.transport_speed":0.35151},"optimized_scores":{"best_composite_score":0.16639,"best_fitness_score":0.66639,"best_task_score":0.39919},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":717.0,"contact_point_centroid":[0.55367,0.20229,-0.00312],"force_p95":0.72425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34862,"mean_force":0.1859,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52744,0.17265,0.15339]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.49859,0.04285,-0.00121],"force_p95":0.28608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46656,"mean_force":0.06877,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48695,0.04327,0.04463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9913.0,"contact_point_centroid":[0.48642,0.06206,0.08515],"force_p95":0.10406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30567,"mean_force":0.06324,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4845,0.04306,0.08331]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9838.0,"contact_point_centroid":[0.48673,0.0242,0.08764],"force_p95":0.09771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27561,"mean_force":0.06249,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48448,0.04306,0.08574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10574.0,"contact_point_centroid":[0.51259,0.09328,0.14734],"force_p95":0.13127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26913,"mean_force":0.08185,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50663,0.11196,0.14664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11903.0,"contact_point_centroid":[0.51402,0.13374,0.14726],"force_p95":0.09768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25734,"mean_force":0.07432,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50799,0.11529,0.14683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04489,-0.00213],"force_p95":0.15927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22328,"mean_force":0.13257,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48962,0.04353,0.04399]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1144.0,"contact_point_centroid":[0.49097,0.0303,0.14466],"force_p95":0.09837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1702,"mean_force":0.07109,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.48521,0.04884,0.1419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.49056,0.06779,0.14384],"force_p95":0.10035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16637,"mean_force":0.07903,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.48523,0.04895,0.14197]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49788,0.01958,0.23631]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49573,0.04211,0.1115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5047.0,"contact_point_centroid":[0.48837,0.02418,0.0459],"force_p95":0.07016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11356,"mean_force":0.04295,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04342,0.04276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5511.0,"contact_point_centroid":[0.4882,0.06274,0.04532],"force_p95":0.06978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07209,"mean_force":0.04088,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04342,0.04277]}],"total_contact_groups":13},"final_pose_error":0.07886,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55382,0.20286,0.01602],"final_tcp_position":[0.53198,0.17401,0.1503],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.34862,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49757,0.04032,0.17258],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15416,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12358.0,"raw_peak_contact_force":0.22328,"subtask_id":"reach_object","tcp_end":[0.49641,0.04414,0.05142],"tcp_start":[0.49757,0.04032,0.17258],"tcp_to_object_dist_end":0.02586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04388,0.02553],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2431,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.10343,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19892.0,"raw_peak_contact_force":0.46656,"tcp_end":[0.48846,0.04342,0.04273],"tcp_start":[0.49641,0.04414,0.05142],"tcp_to_object_dist_end":0.02138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49723,0.04338,0.11477],"object_pos_start":[0.50114,0.04388,0.02553],"object_to_goal_dist_end":0.21479,"object_to_goal_dist_start":0.2431,"object_z_max":0.11465,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.1702,"tcp_end":[0.48452,0.04307,0.1382],"tcp_start":[0.48846,0.04342,0.04273],"tcp_to_object_dist_end":0.02666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.49735,0.04342,0.11485],"object_pos_start":[0.49723,0.04338,0.11477],"object_to_goal_dist_end":0.2147,"object_to_goal_dist_start":0.21479,"object_z_max":0.12312,"peak_contact_force":0.0,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22477.0,"raw_peak_contact_force":0.26913,"subtask_id":"reach_goal","tcp_end":[0.48717,0.05624,0.14777],"tcp_start":[0.48459,0.04313,0.13835],"tcp_to_object_dist_end":0.03676,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54557,0.18813,0.05099],"object_pos_start":[0.49965,0.0564,0.12326],"object_to_goal_dist_end":0.11291,"object_to_goal_dist_start":0.20066,"object_z_max":0.12331,"peak_contact_force":0.1227,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":717.0,"raw_peak_contact_force":1.34862,"subtask_id":"reach_goal","tcp_end":[0.53198,0.17401,0.1503],"tcp_start":[0.48717,0.05624,0.14777],"tcp_to_object_dist_end":0.10123,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55382,0.20286,0.01602],"object_pos_start":[0.54557,0.18813,0.05099],"object_to_goal_dist_end":0.13775,"object_to_goal_dist_start":0.11291,"object_z_max":0.05099,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52623,0.17222,0.17341],"tcp_start":[0.53198,0.17401,0.1503],"tcp_to_object_dist_end":0.1627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97368,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13394,"descend_grasp.grasp_height":0.0095,"descend_place.place_height":0.01494,"lift_object.lift_height":0.10509,"release_object.release_duration":0.64369,"transport_goal.transport_height":0.08725,"transport_goal.transport_speed":0.45619},"optimized_scores":{"best_composite_score":0.09714,"best_fitness_score":0.59714,"best_task_score":0.24545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3724.0,"contact_point_centroid":[0.55194,0.07087,-0.00224],"force_p95":0.12557,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84493,"mean_force":0.13445,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56022,0.09007,0.18235]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.47333,-0.01925,-0.0011],"force_p95":0.39142,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52176,"mean_force":0.06914,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46266,-0.01961,0.03848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4169.0,"contact_point_centroid":[0.49034,0.0271,0.14977],"force_p95":0.13659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35791,"mean_force":0.08369,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.48456,0.00881,0.1491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3432.0,"contact_point_centroid":[0.48823,-0.01169,0.14881],"force_p95":0.16571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32856,"mean_force":0.09874,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.48282,0.00694,0.14773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9770.0,"contact_point_centroid":[0.46217,-0.00057,0.08098],"force_p95":0.10056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29175,"mean_force":0.06299,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46017,-0.01954,0.07903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10340.0,"contact_point_centroid":[0.46197,-0.03847,0.07953],"force_p95":0.10035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28575,"mean_force":0.06035,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46017,-0.01954,0.07787]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17563,"mean_force":0.12619,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46517,-0.01967,0.03782]},{"body_a":"world","body_b":"grasp_target","contact_count":1528.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48724,-0.0086,0.23748]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47234,-0.0188,0.10858]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55193,0.07087,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58413,0.11741,0.1895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.46376,-0.00039,0.03933],"force_p95":0.06571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09676,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46407,-0.01964,0.03672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5392.0,"contact_point_centroid":[0.46364,-0.03889,0.03883],"force_p95":0.06469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08489,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46407,-0.01964,0.03673]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3711.0,"contact_point_centroid":[0.56258,0.09211,0.18497],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56221,0.09211,0.18271]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.58692,0.11804,0.18758],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00998,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58674,0.11803,0.18533]}],"total_contact_groups":14},"final_pose_error":0.06202,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.55193,0.07087,0.01602],"final_tcp_position":[0.58805,0.11823,0.188],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.84493,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47538,-0.01788,0.17363],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13404,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12267.0,"raw_peak_contact_force":0.17563,"subtask_id":"reach_object","tcp_end":[0.47182,-0.01982,0.04451],"tcp_start":[0.47538,-0.01788,0.17363],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01972,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.11195,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":20240.0,"raw_peak_contact_force":0.52176,"tcp_end":[0.46404,-0.01964,0.03669],"tcp_start":[0.47182,-0.01982,0.04451],"tcp_to_object_dist_end":0.0162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.47425,-0.01953,0.11281],"object_pos_start":[0.47606,-0.01972,0.02583],"object_to_goal_dist_end":0.25021,"object_to_goal_dist_start":0.28827,"object_z_max":0.11271,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7601.0,"raw_peak_contact_force":0.35791,"tcp_end":[0.46015,-0.01953,0.13069],"tcp_start":[0.46404,-0.01964,0.03669],"tcp_to_object_dist_end":0.02276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.47431,-0.01952,0.11284],"object_pos_start":[0.47425,-0.01953,0.11281],"object_to_goal_dist_end":0.25015,"object_to_goal_dist_start":0.25021,"object_z_max":0.14972,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7435.0,"raw_peak_contact_force":1.84493,"subtask_id":"reach_goal","tcp_end":[0.52283,0.04893,0.17967],"tcp_start":[0.46021,-0.01953,0.13075],"tcp_to_object_dist_end":0.10726,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55193,0.07087,0.01602],"object_pos_start":[0.53412,0.05378,0.14479],"object_to_goal_dist_end":0.2107,"object_to_goal_dist_start":0.15041,"object_z_max":0.14479,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.58805,0.11823,0.188],"tcp_start":[0.52283,0.04893,0.17967],"tcp_to_object_dist_end":0.18201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55193,0.07087,0.01602],"object_pos_start":[0.55193,0.07087,0.01602],"object_to_goal_dist_end":0.2107,"object_to_goal_dist_start":0.2107,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.58262,0.11704,0.2094],"tcp_start":[0.58805,0.11823,0.188],"tcp_to_object_dist_end":0.20117,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```