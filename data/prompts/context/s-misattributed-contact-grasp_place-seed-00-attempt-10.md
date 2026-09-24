## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1328 | 0.33 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1513 | 0.36 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1151 | 0.28 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1379 | 0.22 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.2321 | 0.23 | ❌ rejected |

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

## Current Skill (Q=0.133) — your mutation base

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

- **Composite score**: 0.133
- **task_score** (E): 0.326
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1361 |
| descend_grasp | 1.00 | 1.00 | 0.1198 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1098 |
| transport_goal | 1.00 | 1.00 | 0.2024 |
| descend_place | 1.00 | 1.00 | 0.0226 |
| release_object | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.169) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_grasp | descend | 1.00 / step_budget | (0.494, 0.001, 0.169)→(0.492, 0.001, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 44.667 | 0.141 | 0.191 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.049)→(0.484, 0.000, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 23.000 | 0.106 | 0.490 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.040)→(0.480, 0.000, 0.150) | (0.497, 0.001, 0.026)→(0.493, 0.001, 0.128) | 0.266→0.222 | 1.00 / 10.000 | 0.150 | 1.145 |
| transport_goal | approach | 1.00 / step_budget | (0.480, 0.000, 0.150)→(0.569, 0.166, 0.190) | (0.493, 0.001, 0.128)→(0.568, 0.144, 0.045) | 0.222→0.149 | 1.00 / 8.333 | 0.123 | 0.440 |
| descend_place | descend | 1.00 / step_budget | (0.569, 0.166, 0.190)→(0.579, 0.182, 0.192) | (0.568, 0.144, 0.045)→(0.565, 0.146, 0.019) | 0.149→0.174 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.579, 0.182, 0.192)→(0.573, 0.180, 0.213) | (0.565, 0.146, 0.019)→(0.565, 0.146, 0.019) | 0.174→0.174 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.442
- phase_score: 0.681
- phase_breakdown.reach_goal_score: 0.774
- phase_breakdown.reach_object_score: 0.543
- grasp_place_fitness: 0.689

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.689
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.442
- **Median Q (composite search score)**: 0.125
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.205


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7563,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13364,"descend_grasp.grasp_height":0.01372,"descend_place.place_height":0.01219,"lift_object.lift_height":0.10775,"release_object.release_duration":0.30806,"transport_goal.transport_height":0.03065,"transport_goal.transport_speed":0.25806},"optimized_scores":{"best_composite_score":0.08433,"best_fitness_score":0.58433,"best_task_score":0.22726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2134.0,"contact_point_centroid":[0.5313,0.07091,-0.0024],"force_p95":0.16306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47389,"mean_force":0.14741,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.53122,0.09209,0.20644]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.51072,-0.022,-0.00113],"force_p95":0.37904,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5103,"mean_force":0.07128,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49899,-0.02242,0.04091]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9099.0,"contact_point_centroid":[0.49881,-0.0034,0.08361],"force_p95":0.10517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32423,"mean_force":0.06728,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4964,-0.02234,0.08153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3605.0,"contact_point_centroid":[0.50792,-0.01346,0.14928],"force_p95":0.16595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30535,"mean_force":0.0959,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.50235,0.00505,0.14891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9857.0,"contact_point_centroid":[0.49891,-0.04117,0.0817],"force_p95":0.10089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2936,"mean_force":0.06304,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49642,-0.02234,0.08022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4048.0,"contact_point_centroid":[0.50891,0.02611,0.1506],"force_p95":0.13075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26579,"mean_force":0.08626,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.5031,0.00778,0.15051]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02288,-0.00205],"force_p95":0.13824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17205,"mean_force":0.12686,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50169,-0.02249,0.04046]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.5137,-0.02302,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50333,-0.00999,0.23605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.50106,-0.00325,0.04195],"force_p95":0.07746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12823,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50052,-0.02246,0.03918]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50742,-0.02157,0.10954]},{"body_a":"world","body_b":"grasp_target","contact_count":444.0,"contact_point_centroid":[0.5314,0.07131,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54681,0.13985,0.23007]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5314,0.07131,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5455,0.14525,0.22999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.50111,-0.04154,0.04101],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08914,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50053,-0.02246,0.03918]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2065.0,"contact_point_centroid":[0.53285,0.09627,0.21158],"force_p95":0.01144,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.53265,0.09627,0.20924]},{"body_a":"left_finger","body_b":"right_finger","contact_count":486.0,"contact_point_centroid":[0.54724,0.13982,0.23243],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.0102,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5468,0.13981,0.23009]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.54778,0.14596,0.22768],"force_p95":0.01087,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54768,0.14595,0.2253]}],"total_contact_groups":16},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5314,0.07131,0.01602],"final_tcp_position":[0.54888,0.14608,0.2278],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.47389,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50876,-0.02058,0.17186],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13525,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10811.0,"raw_peak_contact_force":0.17205,"subtask_id":"reach_object","tcp_end":[0.50867,-0.02265,0.04822],"tcp_start":[0.50876,-0.02058,0.17186],"tcp_to_object_dist_end":0.02277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02242,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26539,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.09939,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19092.0,"raw_peak_contact_force":0.5103,"tcp_end":[0.50049,-0.02245,0.03915],"tcp_start":[0.50867,-0.02265,0.04822],"tcp_to_object_dist_end":0.0187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50982,-0.02223,0.11441],"object_pos_start":[0.5136,-0.02242,0.02581],"object_to_goal_dist_end":0.20921,"object_to_goal_dist_start":0.26539,"object_z_max":0.1143,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11852.0,"raw_peak_contact_force":1.47389,"tcp_end":[0.49647,-0.02234,0.13493],"tcp_start":[0.50049,-0.02245,0.03915],"tcp_to_object_dist_end":0.02448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5314,0.07131,0.01602],"object_pos_start":[0.50982,-0.02223,0.11441],"object_to_goal_dist_end":0.22225,"object_to_goal_dist_start":0.20921,"object_z_max":0.14236,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":930.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54522,0.13314,0.2339],"tcp_start":[0.49647,-0.02234,0.13493],"tcp_to_object_dist_end":0.2269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":111.0,"n_steps_budget":1000.0,"object_pos_end":[0.5314,0.07131,0.01602],"object_pos_start":[0.5314,0.07131,0.01602],"object_to_goal_dist_end":0.22225,"object_to_goal_dist_start":0.22225,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.54888,0.14608,0.2278],"tcp_start":[0.54522,0.13314,0.2339],"tcp_to_object_dist_end":0.22527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5314,0.07131,0.01602],"object_pos_start":[0.5314,0.07131,0.01602],"object_to_goal_dist_end":0.22225,"object_to_goal_dist_start":0.22225,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.54427,0.14486,0.25025],"tcp_start":[0.54888,0.14608,0.2278],"tcp_to_object_dist_end":0.24584,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.864,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.12393,"descend_grasp.grasp_height":0.01521,"descend_place.place_height":0.02084,"lift_object.lift_height":0.1302,"release_object.release_duration":0.56177,"transport_goal.transport_height":1e-05,"transport_goal.transport_speed":0.23976},"optimized_scores":{"best_composite_score":0.18932,"best_fitness_score":0.68932,"best_task_score":0.44165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3094.0,"contact_point_centroid":[0.54792,0.23174,-0.00221],"force_p95":0.13515,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06662,"mean_force":0.13269,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55643,0.23597,0.14968]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.49845,0.04269,-0.00122],"force_p95":0.3176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48327,"mean_force":0.07113,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48688,0.04327,0.0431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.5569,0.20835,0.13467],"force_p95":0.30564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34482,"mean_force":0.0778,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5532,0.22619,0.14008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11691.0,"contact_point_centroid":[0.48687,0.06201,0.09326],"force_p95":0.10453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30795,"mean_force":0.06588,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48444,0.04305,0.09137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.55665,0.24383,0.13424],"force_p95":0.22544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28986,"mean_force":0.08029,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55321,0.22618,0.14009]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11736.0,"contact_point_centroid":[0.48717,0.02424,0.09603],"force_p95":0.09965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27785,"mean_force":0.06487,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48441,0.04305,0.09425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9979.0,"contact_point_centroid":[0.52145,0.11183,0.14797],"force_p95":0.135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23321,"mean_force":0.09163,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51593,0.13036,0.14826]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04488,-0.00214],"force_p95":0.15984,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22516,"mean_force":0.13273,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48957,0.04352,0.04246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11110.0,"contact_point_centroid":[0.52055,0.14792,0.14741],"force_p95":0.12767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20628,"mean_force":0.08365,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.5156,0.12951,0.14835]},{"body_a":"world","body_b":"grasp_target","contact_count":1776.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49782,0.01978,0.23089]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49566,0.04226,0.10547]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54789,0.23175,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55618,0.2406,0.16]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5043.0,"contact_point_centroid":[0.48833,0.02417,0.04442],"force_p95":0.0704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1157,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48843,0.04342,0.04124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5513.0,"contact_point_centroid":[0.48816,0.06273,0.04384],"force_p95":0.06989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07272,"mean_force":0.04091,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48844,0.04342,0.04124]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2881.0,"contact_point_centroid":[0.55738,0.2368,0.15297],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01633,"mean_force":0.01064,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55686,0.23677,0.15073]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.55934,0.2419,0.1581],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55885,0.24186,0.15597]}],"total_contact_groups":16},"final_pose_error":0.01022,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54789,0.23175,0.02602],"final_tcp_position":[0.56017,0.24242,0.15864],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.06662,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49749,0.04064,0.16184],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15453,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12356.0,"raw_peak_contact_force":0.22516,"subtask_id":"reach_object","tcp_end":[0.49637,0.04413,0.04989],"tcp_start":[0.49749,0.04064,0.16184],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04385,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24313,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.10869,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":23569.0,"raw_peak_contact_force":0.48327,"tcp_end":[0.4884,0.04341,0.04121],"tcp_start":[0.49637,0.04413,0.04989],"tcp_to_object_dist_end":0.0202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.49685,0.04343,0.13605],"object_pos_start":[0.50114,0.04385,0.02552],"object_to_goal_dist_end":0.21274,"object_to_goal_dist_start":0.24313,"object_z_max":0.13594,"peak_contact_force":0.19998,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21089.0,"raw_peak_contact_force":0.23321,"tcp_end":[0.48463,0.04308,0.15969],"tcp_start":[0.4884,0.04341,0.04121],"tcp_to_object_dist_end":0.02662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55725,0.22602,0.10278],"object_pos_start":[0.49685,0.04343,0.13605],"object_to_goal_dist_end":0.0484,"object_to_goal_dist_start":0.21274,"object_z_max":0.13608,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6188.0,"raw_peak_contact_force":1.06662,"subtask_id":"reach_goal","tcp_end":[0.5535,0.22577,0.14042],"tcp_start":[0.48463,0.04308,0.15969],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":1000.0,"object_pos_end":[0.54789,0.23175,0.02602],"object_pos_start":[0.55725,0.22602,0.10278],"object_to_goal_dist_end":0.12258,"object_to_goal_dist_start":0.0484,"object_z_max":0.10278,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.56017,0.24242,0.15864],"tcp_start":[0.5535,0.22577,0.14042],"tcp_to_object_dist_end":0.13362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54789,0.23175,0.02602],"object_pos_start":[0.54789,0.23175,0.02602],"object_to_goal_dist_end":0.12258,"object_to_goal_dist_start":0.12258,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.55462,0.23985,0.17984],"tcp_start":[0.56017,0.24242,0.15864],"tcp_to_object_dist_end":0.15419,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8629,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13228,"descend_grasp.grasp_height":0.01314,"descend_place.place_height":0.00982,"lift_object.lift_height":0.12626,"release_object.release_duration":0.5645,"transport_goal.transport_height":0.0216,"transport_goal.transport_speed":0.31976},"optimized_scores":{"best_composite_score":0.12462,"best_fitness_score":0.62462,"best_task_score":0.30803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":320.0,"contact_point_centroid":[0.61448,0.13361,-0.005],"force_p95":1.03985,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7293,"mean_force":0.26714,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.60224,0.13149,0.19516]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.47318,-0.01942,-0.00111],"force_p95":0.35887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47605,"mean_force":0.0648,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46272,-0.0196,0.04205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8746.0,"contact_point_centroid":[0.52347,0.02471,0.1702],"force_p95":0.13628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2932,"mean_force":0.08989,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51747,0.04332,0.16962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9861.0,"contact_point_centroid":[0.52365,0.06198,0.17001],"force_p95":0.12044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28941,"mean_force":0.08017,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51775,0.04359,0.16971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11124.0,"contact_point_centroid":[0.46259,-0.00061,0.09251],"force_p95":0.10444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28799,"mean_force":0.0658,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46024,-0.01953,0.09049]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11587.0,"contact_point_centroid":[0.46271,-0.03841,0.09174],"force_p95":0.10069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28239,"mean_force":0.06386,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46025,-0.01953,0.09008]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00204],"force_p95":0.13551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17551,"mean_force":0.12622,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46522,-0.01966,0.0414]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48719,-0.00863,0.23656]},{"body_a":"world","body_b":"grasp_target","contact_count":2708.0,"contact_point_centroid":[0.61506,0.13355,-0.00198],"force_p95":0.12352,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12963,"mean_force":0.12266,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61969,0.15053,0.19077]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47233,-0.01881,0.10954]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61506,0.13355,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62294,0.1562,0.19103]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5078.0,"contact_point_centroid":[0.46379,-0.00041,0.04285],"force_p95":0.06575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09756,"mean_force":0.04286,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01964,0.0403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5148.0,"contact_point_centroid":[0.46404,-0.03888,0.04227],"force_p95":0.06641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08392,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46412,-0.01964,0.0403]},{"body_a":"left_finger","body_b":"right_finger","contact_count":87.0,"contact_point_centroid":[0.6072,0.13581,0.19871],"force_p95":0.01473,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01507,"mean_force":0.01272,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.6064,0.1358,0.19641]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2871.0,"contact_point_centroid":[0.62014,0.15053,0.19296],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01311,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61967,0.15051,0.19077]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62605,0.15699,0.1899],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62553,0.15698,0.18774]}],"total_contact_groups":16},"final_pose_error":0.0103,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61506,0.13355,0.01602],"final_tcp_position":[0.62683,0.15732,0.19081],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.7293,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47532,-0.01791,0.17192],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13402,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12026.0,"raw_peak_contact_force":0.17551,"subtask_id":"reach_object","tcp_end":[0.47183,-0.01981,0.0481],"tcp_start":[0.47532,-0.01791,0.17192],"tcp_to_object_dist_end":0.02251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01975,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28829,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.10865,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":22838.0,"raw_peak_contact_force":0.47605,"tcp_end":[0.46409,-0.01963,0.04027],"tcp_start":[0.47183,-0.01981,0.0481],"tcp_to_object_dist_end":0.01876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.47304,-0.01943,0.13262],"object_pos_start":[0.47607,-0.01975,0.02583],"object_to_goal_dist_end":0.24553,"object_to_goal_dist_start":0.28829,"object_z_max":0.13251,"peak_contact_force":0.1259,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19014.0,"raw_peak_contact_force":1.7293,"tcp_end":[0.46037,-0.01952,0.15525],"tcp_start":[0.46409,-0.01963,0.04027],"tcp_to_object_dist_end":0.02593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61506,0.13354,0.01665],"object_pos_start":[0.47304,-0.01943,0.13262],"object_to_goal_dist_end":0.17601,"object_to_goal_dist_start":0.24553,"object_z_max":0.15443,"peak_contact_force":0.12263,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5579.0,"raw_peak_contact_force":0.12963,"subtask_id":"reach_goal","tcp_end":[0.60864,0.13789,0.19706],"tcp_start":[0.46037,-0.01952,0.15525],"tcp_to_object_dist_end":0.18058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.61506,0.13355,0.01602],"object_pos_start":[0.61506,0.13354,0.01665],"object_to_goal_dist_end":0.17663,"object_to_goal_dist_start":0.17601,"object_z_max":0.01665,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.62683,0.15732,0.19081],"tcp_start":[0.60864,0.13789,0.19706],"tcp_to_object_dist_end":0.17679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61506,0.13355,0.01602],"object_pos_start":[0.61506,0.13355,0.01602],"object_to_goal_dist_end":0.17663,"object_to_goal_dist_start":0.17663,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.62145,0.15573,0.21034],"tcp_start":[0.62683,0.15732,0.19081],"tcp_to_object_dist_end":0.19569,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```