## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0217 | 0.29 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0812 | 0.21 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1328 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1513 | 0.36 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1151 | 0.28 | ✅ accepted |

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

## Current Skill (Q=0.022) — your mutation base

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
  - id: transport_object_lifted
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
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
  guards:
  - id: place_still_holding
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
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
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_object_lifted, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=place_still_holding, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.022
- **task_score** (E): 0.289
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1493 |
| descend_grasp | 1.00 | 1.00 | 0.1147 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1582 |
| transport_goal | 0.00 | 1.00 | 0.1307 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.155) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 27.129 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.001, 0.155)→(0.492, 0.001, 0.041) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 43.667 | 0.142 | 0.199 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.041)→(0.484, 0.000, 0.032) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 15.333 | 0.155 | 0.596 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.032)→(0.480, 0.000, 0.190) | (0.497, 0.000, 0.026)→(0.490, 0.001, 0.168) | 0.266→0.215 | 1.00 / 26.333 | 55984.142 | 0.689 |
| transport_goal | approach | 0.00 / guard_failure | (0.480, 0.000, 0.190)→(0.560, 0.040, 0.096) | (0.490, 0.001, 0.168)→(0.557, 0.042, 0.077) | 0.215→0.187 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.324
- phase_score: 0.312
- phase_breakdown.reach_goal_score: 0.215
- phase_breakdown.reach_object_score: 0.457
- grasp_place_fitness: 0.639

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.639
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.324
- **Median Q (composite search score)**: 0.018
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: lift_object.lift_height
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.36449,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.07909,"descend_grasp.grasp_height":0.00499,"descend_place.descend_tolerance":0.02992,"descend_place.place_height":0.01793,"lift_object.lift_height":0.18584,"release_object.release_duration":0.75906,"transport_goal.transport_height":0.08574,"transport_goal.transport_speed":0.14295,"transport_goal.transport_tolerance":0.04991},"optimized_scores":{"best_composite_score":0.00821,"best_fitness_score":0.60821,"best_task_score":0.26178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.51069,-0.02205,-0.00113],"force_p95":0.46931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63431,"mean_force":0.08536,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49848,-0.02239,0.03191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.54189,-0.02277,0.16508],"force_p95":0.38414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57731,"mean_force":0.20962,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.54094,-0.00648,0.16923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":421.0,"contact_point_centroid":[0.538,0.01041,0.15839],"force_p95":0.30967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42085,"mean_force":0.14808,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.54005,-0.00616,0.16309]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12726.0,"contact_point_centroid":[0.4994,-0.00357,0.09907],"force_p95":0.1294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33509,"mean_force":0.07787,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49591,-0.02231,0.09799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13583.0,"contact_point_centroid":[0.49948,-0.04097,0.09714],"force_p95":0.12579,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30796,"mean_force":0.07398,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49593,-0.02231,0.09642]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02284,-0.00205],"force_p95":0.13926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18104,"mean_force":0.12714,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50121,-0.02246,0.03148]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.5137,-0.02302,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50326,-0.01043,0.20846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.50074,-0.00323,0.03295],"force_p95":0.07756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12286,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50002,-0.02243,0.0302]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50732,-0.02189,0.07805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.50076,-0.04152,0.03201],"force_p95":0.06964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0839,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50002,-0.02243,0.0302]}],"total_contact_groups":10},"final_pose_error":0.25172,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55899,0.01156,0.07788],"final_tcp_position":[0.56199,0.00798,0.10119],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.63431,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50871,-0.02123,0.11756],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13563,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10812.0,"raw_peak_contact_force":0.18104,"subtask_id":"reach_object","tcp_end":[0.50827,-0.02262,0.0392],"tcp_start":[0.50871,-0.02123,0.11756],"tcp_to_object_dist_end":0.01426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51357,-0.02235,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26534,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15662,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":26444.0,"raw_peak_contact_force":0.63431,"tcp_end":[0.49999,-0.02243,0.03017],"tcp_start":[0.50827,-0.02262,0.0392],"tcp_to_object_dist_end":0.01426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5058,-0.02224,0.16792],"object_pos_start":[0.51357,-0.02235,0.02581],"object_to_goal_dist_end":0.1884,"object_to_goal_dist_start":0.26534,"object_z_max":0.16775,"peak_contact_force":0.38066,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":985.0,"raw_peak_contact_force":0.57731,"tcp_end":[0.49629,-0.02231,0.19044],"tcp_start":[0.49999,-0.02243,0.03017],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":59.0,"n_steps_budget":1000.0,"object_pos_end":[0.55899,0.01156,0.07788],"object_pos_start":[0.5058,-0.02224,0.16792],"object_to_goal_dist_end":0.20104,"object_to_goal_dist_start":0.1884,"object_z_max":0.16833,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.56199,0.00798,0.10119],"tcp_start":[0.49629,-0.02231,0.19044],"tcp_to_object_dist_end":0.02377,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30476,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12313,"descend_grasp.grasp_height":0.00663,"descend_place.descend_tolerance":0.02082,"descend_place.place_height":0.02407,"lift_object.lift_height":0.19999,"release_object.release_duration":0.58911,"transport_goal.transport_height":0.08366,"transport_goal.transport_speed":0.13507,"transport_goal.transport_tolerance":0.04127},"optimized_scores":{"best_composite_score":0.03879,"best_fitness_score":0.63879,"best_task_score":0.32406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.53256,0.08111,0.16077],"force_p95":0.40967,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.96343,"mean_force":0.21723,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.5308,0.06567,0.16337]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.49826,0.0421,-0.00122],"force_p95":0.40477,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58513,"mean_force":0.08268,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48676,0.04328,0.03442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":434.0,"contact_point_centroid":[0.53639,0.05256,0.15685],"force_p95":0.33829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51941,"mean_force":0.15617,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.53834,0.06869,0.16165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13560.0,"contact_point_centroid":[0.48769,0.06182,0.10006],"force_p95":0.12538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32218,"mean_force":0.07406,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48432,0.04307,0.09892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13050.0,"contact_point_centroid":[0.48769,0.02432,0.10233],"force_p95":0.12461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3146,"mean_force":0.07578,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48431,0.04307,0.10099]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04476,-0.00214],"force_p95":0.16441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23956,"mean_force":0.13369,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48945,0.04354,0.03378]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4066.0,"contact_point_centroid":[0.48876,0.0242,0.03537],"force_p95":0.08247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15188,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48829,0.04343,0.03256]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49781,0.01977,0.23059]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49561,0.04227,0.10061]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5218.0,"contact_point_centroid":[0.48846,0.06259,0.03474],"force_p95":0.07203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08476,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4883,0.04343,0.03256]}],"total_contact_groups":10},"final_pose_error":0.20853,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54713,0.09274,0.07517],"final_tcp_position":[0.55389,0.09021,0.09095],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49748,0.04062,0.16116],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15687,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11084.0,"raw_peak_contact_force":0.23956,"subtask_id":"reach_object","tcp_end":[0.49633,0.04416,0.04118],"tcp_start":[0.49748,0.04062,0.16116],"tcp_to_object_dist_end":0.01594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.0435,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24344,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16669,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":26748.0,"raw_peak_contact_force":0.58513,"tcp_end":[0.48826,0.04343,0.03253],"tcp_start":[0.49633,0.04416,0.04118],"tcp_to_object_dist_end":0.01463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49344,0.04326,0.17307],"object_pos_start":[0.50111,0.0435,0.02551],"object_to_goal_dist_end":0.21534,"object_to_goal_dist_start":0.24344,"object_z_max":0.17289,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":914.0,"raw_peak_contact_force":0.96343,"tcp_end":[0.48467,0.0431,0.19652],"tcp_start":[0.48826,0.04343,0.03253],"tcp_to_object_dist_end":0.02504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.54713,0.09274,0.07517],"object_pos_start":[0.49344,0.04326,0.17307],"object_to_goal_dist_end":0.16902,"object_to_goal_dist_start":0.21534,"object_z_max":0.1735,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.55389,0.09021,0.09095],"tcp_start":[0.48467,0.0431,0.19652],"tcp_to_object_dist_end":0.01736,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26733,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1475,"descend_grasp.grasp_height":0.0066,"descend_place.descend_tolerance":0.02618,"descend_place.place_height":0.00389,"lift_object.lift_height":0.16157,"release_object.release_duration":0.99617,"transport_goal.transport_height":0.05215,"transport_goal.transport_speed":0.25957,"transport_goal.transport_tolerance":0.04635},"optimized_scores":{"best_composite_score":0.01808,"best_fitness_score":0.61808,"best_task_score":0.28164},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.47319,-0.01922,-0.0011],"force_p95":0.39493,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5685,"mean_force":0.07273,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46267,-0.01962,0.03538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":653.0,"contact_point_centroid":[0.52379,-0.01706,0.15762],"force_p95":0.38017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52725,"mean_force":0.19802,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.521,0.00153,0.16148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":628.0,"contact_point_centroid":[0.52036,0.01913,0.15796],"force_p95":0.34132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49093,"mean_force":0.17482,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51998,0.00121,0.16186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13034.0,"contact_point_centroid":[0.46335,-0.00072,0.09958],"force_p95":0.11228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2983,"mean_force":0.07159,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4602,-0.01954,0.09792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13777.0,"contact_point_centroid":[0.46323,-0.03833,0.09837],"force_p95":0.10938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28947,"mean_force":0.06849,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4602,-0.01954,0.09696]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02005,-0.00204],"force_p95":0.13548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17541,"mean_force":0.12615,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46518,-0.01968,0.03473]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48751,-0.00846,0.24428]},{"body_a":"world","body_b":"grasp_target","contact_count":1852.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47254,-0.01869,0.11362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5073.0,"contact_point_centroid":[0.46376,-0.00041,0.03624],"force_p95":0.06565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09521,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46407,-0.01965,0.03364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5394.0,"contact_point_centroid":[0.46364,-0.0389,0.03574],"force_p95":0.06462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08558,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46407,-0.01965,0.03364]}],"total_contact_groups":10},"final_pose_error":0.21163,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.5657,0.02072,0.07762],"final_tcp_position":[0.56553,0.02073,0.09631],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":81.14225,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47576,-0.01765,0.18707],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13385,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12267.0,"raw_peak_contact_force":0.17541,"subtask_id":"reach_object","tcp_end":[0.47182,-0.01983,0.0414],"tcp_start":[0.47576,-0.01765,0.18707],"tcp_to_object_dist_end":0.01599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01971,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14257,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":26937.0,"raw_peak_contact_force":0.5685,"tcp_end":[0.46404,-0.01965,0.03361],"tcp_start":[0.47182,-0.01983,0.0414],"tcp_to_object_dist_end":0.0143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.4721,-0.0195,0.16206],"object_pos_start":[0.47605,-0.01971,0.02584],"object_to_goal_dist_end":0.24103,"object_to_goal_dist_start":0.28827,"object_z_max":0.16197,"peak_contact_force":0.3156,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1281.0,"raw_peak_contact_force":0.52725,"tcp_end":[0.46053,-0.01954,0.18374],"tcp_start":[0.46404,-0.01965,0.03361],"tcp_to_object_dist_end":0.02458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.5657,0.02072,0.07762],"object_pos_start":[0.4721,-0.0195,0.16206],"object_to_goal_dist_end":0.19007,"object_to_goal_dist_start":0.24103,"object_z_max":0.16216,"peak_contact_force":0.12262,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_goal","tcp_end":[0.56553,0.02073,0.09631],"tcp_start":[0.46053,-0.01954,0.18374],"tcp_to_object_dist_end":0.01869,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```