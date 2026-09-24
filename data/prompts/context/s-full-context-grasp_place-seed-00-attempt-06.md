## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2102 | 0.30 | ❌ rejected |
| 5 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1505 | 0.32 | ✅ accepted |
| 4 | approach → approach → grasp → lift → approach → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6552 | 0.17 | ❌ rejected |
| 3 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1694 | 0.19 | ✅ accepted |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.210) — your mutation base

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
      distance: 0.15
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
      - 0.05
      - 0.25
      default: 0.15
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
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
    release_time:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_after_release
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
    - 0.15
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_release** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.210
- **task_score** (E): 0.296
- **fitness_score**: 0.620  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1115 |
| descend_to_grasp | 1.00 | 1.00 | 0.1466 |
| grasp_object | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1220 |
| approach_goal | 0.67 | 1.00 | 0.1208 |
| descend_to_goal | 1.00 | 1.00 | 0.1135 |
| release_object | 1.00 | 1.00 | 0.0208 |
| retract_after_release | 0.67 | 1.00 | 0.2546 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.193) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | approach | 1.00 / step_budget | (0.494, 0.001, 0.193)→(0.492, 0.001, 0.047) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.492, 0.001, 0.047)→(0.484, 0.000, 0.038) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 43.000 | 0.144 | 0.199 |
| lift_object | lift | 1.00 / step_budget | (0.484, 0.000, 0.038)→(0.481, 0.000, 0.160) | (0.497, 0.000, 0.026)→(0.493, 0.000, 0.144) | 0.266→0.217 | 1.00 / 33.333 | 0.087 | 0.496 |
| approach_goal | approach | 0.67 / step_budget | (0.518, 0.106, 0.259)→(0.575, 0.177, 0.332) | (0.493, 0.000, 0.144)→(0.563, 0.127, 0.184) | 0.217→0.109 | 1.00 / 13.667 | 182004.075 | 1.430 |
| descend_to_goal | approach | 1.00 / step_budget | (0.575, 0.177, 0.332)→(0.579, 0.211, 0.225) | (0.566, 0.136, 0.105)→(0.569, 0.147, 0.075) | 0.160→0.134 | 1.00 / 12.333 | 3249.711 | 0.169 |
| release_object | release | 1.00 / step_budget | (0.579, 0.211, 0.225)→(0.575, 0.210, 0.245) | (0.569, 0.147, 0.075)→(0.566, 0.146, 0.018) | 0.134→0.184 | 1.00 / 3.667 | 0.142 | 0.698 |
| retract_after_release | retract | 0.67 / step_budget | (0.575, 0.210, 0.245)→(0.576, 0.210, 0.499) | (0.566, 0.146, 0.018)→(0.562, 0.147, 0.019) | 0.184→0.184 | 1.00 / 4.000 | 0.123 | 0.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.328
- phase_score: 0.506
- phase_breakdown.reach_object_score: 0.067
- phase_breakdown.place_goal_score: 0.695
- grasp_place_fitness: 0.638

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.638
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.328
- **Median Q (composite search score)**: -0.203
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51246,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.06608,"approach_goal.speed":0.067,"descend_to_goal.place_offset_y":0.03235,"descend_to_goal.place_offset_z":0.03272,"descend_to_goal.speed":0.04554,"descend_to_grasp.descend_offset":0.01589,"descend_to_grasp.speed":0.14526,"grasp_object.max_duration":0.53451,"lift_object.lift_height":0.13834,"lift_object.speed":0.05966,"release_object.release_time":0.88375,"retract_after_release.retract_height":0.13538,"retract_after_release.speed":0.19769},"optimized_scores":{"best_composite_score":-0.23566,"best_fitness_score":0.59434,"best_task_score":0.25214},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1445.0,"contact_point_centroid":[0.55357,0.13483,-0.00299],"force_p95":0.4268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2764,"mean_force":0.1647,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54429,0.12969,0.34784]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51071,-0.02212,-0.0014],"force_p95":0.3983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46254,"mean_force":0.12424,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49935,-0.02235,0.04254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13615.0,"contact_point_centroid":[0.51456,0.01148,0.21973],"force_p95":0.11544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32809,"mean_force":0.06894,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5111,0.03016,0.21882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7644.0,"contact_point_centroid":[0.49732,-0.00314,0.10176],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30575,"mean_force":0.05741,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49685,-0.02227,0.09923]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8078.0,"contact_point_centroid":[0.49729,-0.04134,0.09948],"force_p95":0.08054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28778,"mean_force":0.05518,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49686,-0.02227,0.09731]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12769.0,"contact_point_centroid":[0.51576,0.05217,0.22404],"force_p95":0.10786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24147,"mean_force":0.07301,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51218,0.03338,0.22268]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02289,-0.00206],"force_p95":0.1401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18184,"mean_force":0.12739,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50166,-0.0224,0.04264]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.5137,-0.02302,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50322,-0.00921,0.24757]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.50104,-0.00316,0.04412],"force_p95":0.07776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13199,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.50049,-0.02237,0.04136]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.5072,-0.02089,0.12098]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.55353,0.13471,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55078,0.16194,0.32053]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55353,0.13471,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54809,0.17762,0.2638]},{"body_a":"world","body_b":"grasp_target","contact_count":3136.0,"contact_point_centroid":[0.55353,0.13471,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.54688,0.17691,0.41553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.50109,-0.04146,0.04318],"force_p95":0.06991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08133,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5005,-0.02237,0.04136]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1408.0,"contact_point_centroid":[0.54527,0.13105,0.35239],"force_p95":0.01194,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.0107,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54481,0.13104,0.35012]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1570.0,"contact_point_centroid":[0.55132,0.16186,0.323],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.55078,0.16185,0.32087]}],"total_contact_groups":17},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55353,0.13471,0.01602],"final_tcp_position":[0.54885,0.1775,0.54946],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273006.5134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.5083,-0.01931,0.1932],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50861,-0.02256,0.0504],"tcp_start":[0.5083,-0.01931,0.1932],"tcp_to_object_dist_end":0.02491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02238,0.02578],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26537,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13689,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.18184,"tcp_end":[0.50046,-0.02237,0.04132],"tcp_start":[0.50861,-0.02256,0.0504],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,-0.02236,0.1413],"object_pos_start":[0.51361,-0.02238,0.02578],"object_to_goal_dist_end":0.19752,"object_to_goal_dist_start":0.26537,"object_z_max":0.14103,"peak_contact_force":0.08084,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15806.0,"raw_peak_contact_force":0.46254,"tcp_end":[0.49685,-0.02226,0.16027],"tcp_start":[0.50046,-0.02237,0.04132],"tcp_to_object_dist_end":0.02151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1444.0,"n_steps_budget":1000.0,"object_pos_end":[0.54612,0.10798,0.25016],"object_pos_start":[0.50697,-0.02236,0.1413],"object_to_goal_dist_end":0.05258,"object_to_goal_dist_start":0.19752,"object_z_max":0.27051,"peak_contact_force":273006.5134,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29237.0,"raw_peak_contact_force":2.2764,"subtask_id":"place_goal","tcp_end":[0.55124,0.14724,0.37798],"tcp_start":[0.5354,0.1017,0.30509],"tcp_to_object_dist_end":0.13381,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.55353,0.13471,0.01602],"object_pos_start":[0.55353,0.13471,0.01602],"object_to_goal_dist_end":0.20667,"object_to_goal_dist_start":0.20667,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3046.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55118,0.17859,0.26238],"tcp_start":[0.55124,0.14724,0.37798],"tcp_to_object_dist_end":0.25025,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55353,0.13471,0.01602],"object_pos_start":[0.55353,0.13471,0.01602],"object_to_goal_dist_end":0.20667,"object_to_goal_dist_start":0.20667,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54711,0.1772,0.28396],"tcp_start":[0.55118,0.17859,0.26238],"tcp_to_object_dist_end":0.27136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":784.0,"n_steps_budget":900.0,"object_pos_end":[0.55353,0.13471,0.01602],"object_pos_start":[0.55353,0.13471,0.01602],"object_to_goal_dist_end":0.20667,"object_to_goal_dist_start":0.20667,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3136.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54885,0.1775,0.54946],"tcp_start":[0.54711,0.1772,0.28396],"tcp_to_object_dist_end":0.53517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05056,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.12658,"approach_goal.speed":0.21231,"descend_to_goal.place_offset_y":0.04221,"descend_to_goal.place_offset_z":0.03295,"descend_to_goal.speed":0.13907,"descend_to_grasp.descend_offset":0.01062,"descend_to_grasp.speed":0.07541,"grasp_object.max_duration":1.45493,"lift_object.lift_height":0.11357,"lift_object.speed":0.12332,"release_object.release_time":0.42918,"retract_after_release.retract_height":0.11073,"retract_after_release.speed":0.21679},"optimized_scores":{"best_composite_score":-0.20302,"best_fitness_score":0.62698,"best_task_score":0.30729},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3060.0,"contact_point_centroid":[0.52823,0.13121,-0.0023],"force_p95":0.13032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7926,"mean_force":0.13852,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54169,0.19341,0.24964]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.49866,0.04266,-0.00145],"force_p95":0.54485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56695,"mean_force":0.12863,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48705,0.04316,0.03798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4472.0,"contact_point_centroid":[0.48699,0.02394,0.08006],"force_p95":0.11079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32557,"mean_force":0.0689,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48489,0.04295,0.07746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.48692,0.06191,0.0784],"force_p95":0.10762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32421,"mean_force":0.06486,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4849,0.04295,0.07648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3136.0,"contact_point_centroid":[0.49969,0.05515,0.15274],"force_p95":0.17039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26375,"mean_force":0.09652,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49401,0.07368,0.15175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3555.0,"contact_point_centroid":[0.50033,0.09376,0.15333],"force_p95":0.13593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26091,"mean_force":0.08838,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4946,0.07534,0.153]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04477,-0.00215],"force_p95":0.16722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23734,"mean_force":0.13417,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48948,0.04339,0.03776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3861.0,"contact_point_centroid":[0.48921,0.02402,0.03949],"force_p95":0.08576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15647,"mean_force":0.05474,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48833,0.04329,0.03654]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.50118,0.04505,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49831,0.01817,0.24716]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.49574,0.04089,0.11801]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.52819,0.13121,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.56058,0.2599,0.24388]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52819,0.13121,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55701,0.27822,0.186]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.52819,0.13121,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.55458,0.27657,0.3247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5468.0,"contact_point_centroid":[0.48816,0.06239,0.03908],"force_p95":0.0709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08077,"mean_force":0.04098,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48834,0.04329,0.03654]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3004.0,"contact_point_centroid":[0.54429,0.19869,0.25628],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54381,0.19866,0.25401]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1464.0,"contact_point_centroid":[0.56108,0.25995,0.24607],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01271,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.56058,0.25991,0.24385]}],"total_contact_groups":17},"final_pose_error":0.02094,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52819,0.13121,0.01602],"final_tcp_position":[0.55614,0.27724,0.44548],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273005.60695,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49788,0.03801,0.19255],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.49636,0.04401,0.04519],"tcp_start":[0.49788,0.03801,0.19255],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.0435,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24344,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15851,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11129.0,"raw_peak_contact_force":0.23734,"tcp_end":[0.4883,0.04328,0.03651],"tcp_start":[0.49636,0.04401,0.04519],"tcp_to_object_dist_end":0.01692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":289.0,"n_steps_budget":600.0,"object_pos_end":[0.50155,0.04327,0.11467],"object_pos_start":[0.50113,0.0435,0.02548],"object_to_goal_dist_end":0.21359,"object_to_goal_dist_start":0.24344,"object_z_max":0.11441,"peak_contact_force":0.10768,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9461.0,"raw_peak_contact_force":0.56695,"tcp_end":[0.48461,0.04293,0.13044],"tcp_start":[0.4883,0.04328,0.03651],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1167.0,"n_steps_budget":1000.0,"object_pos_end":[0.52819,0.13121,0.01602],"object_pos_start":[0.50155,0.04327,0.11467],"object_to_goal_dist_end":0.17699,"object_to_goal_dist_start":0.21359,"object_z_max":0.15297,"peak_contact_force":273005.60695,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12755.0,"raw_peak_contact_force":1.7926,"subtask_id":"place_goal","tcp_end":[0.56138,0.24205,0.30249],"tcp_start":[0.55885,0.23527,0.28207],"tcp_to_object_dist_end":0.30895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.52819,0.13121,0.01602],"object_pos_start":[0.52819,0.13121,0.01602],"object_to_goal_dist_end":0.17699,"object_to_goal_dist_start":0.17699,"object_z_max":0.01602,"peak_contact_force":9748.89079,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.56088,0.28012,0.18566],"tcp_start":[0.56138,0.24205,0.30249],"tcp_to_object_dist_end":0.22808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52819,0.13121,0.01602],"object_pos_start":[0.52819,0.13121,0.01602],"object_to_goal_dist_end":0.17699,"object_to_goal_dist_start":0.17699,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55568,0.27741,0.20568],"tcp_start":[0.56088,0.28012,0.18566],"tcp_to_object_dist_end":0.24104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":695.0,"n_steps_budget":780.0,"object_pos_end":[0.52819,0.13121,0.01602],"object_pos_start":[0.52819,0.13121,0.01602],"object_to_goal_dist_end":0.17699,"object_to_goal_dist_start":0.17699,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55614,0.27724,0.44548],"tcp_start":[0.55568,0.27741,0.20568],"tcp_to_object_dist_end":0.45447,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.03321,"average_mean_iterations":10.13653,"average_solve_count":271.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.speed":0.11097,"approach_goal.speed":0.20534,"descend_to_goal.place_offset_y":0.02315,"descend_to_goal.place_offset_z":0.03166,"descend_to_goal.speed":0.06576,"descend_to_grasp.descend_offset":0.01006,"descend_to_grasp.speed":0.102,"grasp_object.max_duration":1.20519,"lift_object.lift_height":0.17268,"lift_object.speed":0.03444,"release_object.release_time":0.64419,"retract_after_release.retract_height":0.19088,"retract_after_release.speed":0.14023},"optimized_scores":{"best_composite_score":-0.1918,"best_fitness_score":0.6382,"best_task_score":0.32849},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.60627,0.17391,-0.00778],"force_p95":1.33937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84852,"mean_force":0.40623,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62087,0.17395,0.23722]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47241,-0.0194,-0.0015],"force_p95":0.44392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45875,"mean_force":0.2097,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46321,-0.01956,0.03811]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":739.0,"contact_point_centroid":[0.62294,0.15637,0.21799],"force_p95":0.1052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32567,"mean_force":0.06961,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62392,0.17515,0.22138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.6238,0.19374,0.21742],"force_p95":0.10353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32167,"mean_force":0.06891,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62395,0.17516,0.22148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3785.0,"contact_point_centroid":[0.61811,0.17498,0.26759],"force_p95":0.12534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26319,"mean_force":0.08002,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.61782,0.1566,0.27104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10316.0,"contact_point_centroid":[0.46101,-0.03863,0.11424],"force_p95":0.07519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25115,"mean_force":0.05233,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4608,-0.01948,0.11238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10310.0,"contact_point_centroid":[0.46099,-0.00033,0.11433],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24968,"mean_force":0.05216,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46079,-0.01948,0.11242]},{"body_a":"world","body_b":"grasp_target","contact_count":3680.0,"contact_point_centroid":[0.60468,0.17512,-0.00203],"force_p95":0.13196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23328,"mean_force":0.12358,"phase_index":7.0,"phase_name":"retract_after_release","phase_type":"retract","tcp_position_centroid":[0.62024,0.17353,0.37374]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.61745,0.13726,0.26962],"force_p95":0.13532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22911,"mean_force":0.09698,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"approach","tcp_position_centroid":[0.61757,0.15597,0.27264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20004.0,"contact_point_centroid":[0.53505,0.0793,0.25267],"force_p95":0.08211,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21993,"mean_force":0.05091,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53485,0.06027,0.2514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17882.0,"contact_point_centroid":[0.53523,0.041,0.25291],"force_p95":0.09013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19872,"mean_force":0.05629,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53475,0.06014,0.25133]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00205],"force_p95":0.13778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17863,"mean_force":0.12672,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46533,-0.0196,0.03841]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48845,-0.00798,0.24852]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"approach","tcp_position_centroid":[0.4733,-0.01822,0.11899]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4835.0,"contact_point_centroid":[0.46427,-0.00036,0.0397],"force_p95":0.06782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10234,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46423,-0.01958,0.03731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5152.0,"contact_point_centroid":[0.46413,-0.0388,0.03923],"force_p95":0.06656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08471,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46424,-0.01958,0.03731]}],"total_contact_groups":16},"final_pose_error":0.08232,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60429,0.17514,0.02602],"final_tcp_position":[0.62326,0.17441,0.5034],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.84852,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":988.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47712,-0.01679,0.19449],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47198,-0.01975,0.04511],"tcp_start":[0.47712,-0.01679,0.19449],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01967,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13584,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11787.0,"raw_peak_contact_force":0.17863,"tcp_end":[0.4642,-0.01958,0.03728],"tcp_start":[0.47198,-0.01975,0.04511],"tcp_to_object_dist_end":0.0165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.46973,-0.0195,0.17623],"object_pos_start":[0.47606,-0.01967,0.02581],"object_to_goal_dist_end":0.24138,"object_to_goal_dist_start":0.28826,"object_z_max":0.17594,"peak_contact_force":0.07378,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20712.0,"raw_peak_contact_force":0.45875,"tcp_end":[0.46097,-0.01947,0.19036],"tcp_start":[0.4642,-0.01958,0.03728],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61538,0.14076,0.2844],"object_pos_start":[0.46973,-0.0195,0.17623],"object_to_goal_dist_end":0.0975,"object_to_goal_dist_start":0.24138,"object_z_max":0.28433,"peak_contact_force":0.10572,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37886.0,"raw_peak_contact_force":0.21993,"subtask_id":"place_goal","tcp_end":[0.61204,0.14032,0.31637],"tcp_start":[0.46097,-0.01947,0.19036],"tcp_to_object_dist_end":0.03215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.62548,0.17541,0.19208],"object_pos_start":[0.61538,0.14076,0.2844],"object_to_goal_dist_end":0.0174,"object_to_goal_dist_start":0.0975,"object_z_max":0.2844,"peak_contact_force":0.11883,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6781.0,"raw_peak_contact_force":0.26319,"subtask_id":"place_goal","tcp_end":[0.62567,0.17542,0.22599],"tcp_start":[0.61204,0.14032,0.31637],"tcp_to_object_dist_end":0.03391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61554,0.17274,0.02212],"object_pos_start":[0.62548,0.17541,0.19208],"object_to_goal_dist_end":0.16919,"object_to_goal_dist_start":0.0174,"object_z_max":0.19208,"peak_contact_force":0.18191,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1706.0,"raw_peak_contact_force":1.84852,"tcp_end":[0.62085,0.17395,0.2448],"tcp_start":[0.62567,0.17542,0.22599],"tcp_to_object_dist_end":0.22275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.60429,0.17514,0.02602],"object_pos_start":[0.61554,0.17274,0.02212],"object_to_goal_dist_end":0.16699,"object_to_goal_dist_start":0.16919,"object_z_max":0.02804,"peak_contact_force":0.12263,"phase_name":"retract_after_release","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3680.0,"raw_peak_contact_force":0.23328,"tcp_end":[0.62326,0.17441,0.5034],"tcp_start":[0.62085,0.17395,0.2448],"tcp_to_object_dist_end":0.47776,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```