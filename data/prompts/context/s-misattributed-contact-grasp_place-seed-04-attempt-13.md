## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1069 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0834 | 0.34 | ✅ accepted |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1938 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1019 | 0.30 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0718 | 0.31 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=-0.107) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pregrasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place
  target_entity: object
  weight: 0.5
phases:
- id: approach_1
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
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pregrasp
- id: descend_1
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
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.015
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pregrasp
- id: grasp_1
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
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
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
    tolerance: 0.01
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
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place
- id: descend_goal
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_goal_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place
- id: release_1
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
- id: retract_1
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
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
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.005], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_goal_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.107
- **task_score** (E): 0.293
- **fitness_score**: 0.623  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1718 |
| descend_1 | 1.00 | 1.00 | 0.0914 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1015 |
| approach_goal | 1.00 | 1.00 | 0.1990 |
| descend_goal | 1.00 | 1.00 | 0.0416 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.0958 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.132) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.132)→(0.521, 0.005, 0.041) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.137 | 0.182 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.041)→(0.512, 0.005, 0.031) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 22.000 | 0.113 | 0.631 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.031)→(0.508, 0.005, 0.133) | (0.526, 0.005, 0.026)→(0.525, 0.005, 0.117) | 0.249→0.208 | 1.00 / 8.000 | 0.123 | 1.443 |
| approach_goal | approach | 1.00 / step_budget | (0.508, 0.005, 0.133)→(0.597, 0.155, 0.222) | (0.525, 0.005, 0.117)→(0.551, 0.086, 0.016) | 0.208→0.199 | 1.00 / 8.000 | 3249.655 | 0.123 |
| descend_goal | descend | 1.00 / step_budget | (0.597, 0.155, 0.222)→(0.605, 0.169, 0.184) | (0.551, 0.086, 0.016)→(0.551, 0.086, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.605, 0.169, 0.184)→(0.599, 0.167, 0.204) | (0.551, 0.086, 0.016)→(0.551, 0.086, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.599, 0.167, 0.204)→(0.598, 0.166, 0.300) | (0.551, 0.086, 0.016)→(0.551, 0.086, 0.016) | 0.199→0.199 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.472
- phase_score: 0.558
- phase_breakdown.lift_clearance_score: 0.372
- phase_breakdown.reach_pregrasp_score: 0.244
- phase_breakdown.place_score: 0.820
- grasp_place_fitness: 0.712

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.712
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.472
- **Median Q (composite search score)**: -0.132
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.265


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11048,"approach_1.approach_speed":0.261,"approach_goal.approach_goal_height":0.05042,"approach_goal.approach_goal_speed":0.325,"descend_1.descend_speed":0.14606,"descend_1.descend_z_offset":0.00762,"descend_goal.descend_goal_speed":0.21698,"lift_1.lift_height":0.10849,"lift_1.lift_speed":0.17843,"retract_1.retract_height":0.11534,"retract_1.retract_speed":0.29738},"optimized_scores":{"best_composite_score":-0.13216,"best_fitness_score":0.59784,"best_task_score":0.24412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2697.0,"contact_point_centroid":[0.56891,0.06884,-0.00229],"force_p95":0.14719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35316,"mean_force":0.14125,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59421,0.09315,0.18674]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.54078,0.00075,-0.00124],"force_p95":0.35198,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61079,"mean_force":0.097,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5282,0.00083,0.03286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7529.0,"contact_point_centroid":[0.52887,-0.01807,0.07316],"force_p95":0.10959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33177,"mean_force":0.07296,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52574,0.00079,0.07104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8042.0,"contact_point_centroid":[0.52898,0.01958,0.07181],"force_p95":0.10555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31838,"mean_force":0.06907,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52578,0.00079,0.06996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1939.0,"contact_point_centroid":[0.53967,-0.00317,0.13228],"force_p95":0.19006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28641,"mean_force":0.11297,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53426,0.01526,0.13268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2386.0,"contact_point_centroid":[0.54093,0.03487,0.13253],"force_p95":0.15977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28167,"mean_force":0.09536,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53525,0.01679,0.13349]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1559,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53122,0.00089,0.03293]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51726,0.00048,0.2227]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5364,0.00099,0.09373]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.56875,0.06941,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.63474,0.14565,0.20473]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56875,0.06941,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63565,0.15116,0.19012]},{"body_a":"world","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.56875,0.06941,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63237,0.15013,0.25054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53095,-0.01833,0.03419],"force_p95":0.07617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11706,"mean_force":0.05176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52998,0.00087,0.03149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.5309,0.01994,0.03331],"force_p95":0.06821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0953,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52998,0.00087,0.03149]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2655.0,"contact_point_centroid":[0.59763,0.09697,0.19171],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01628,"mean_force":0.01055,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59722,0.09697,0.18947]},{"body_a":"left_finger","body_b":"right_finger","contact_count":536.0,"contact_point_centroid":[0.63523,0.14568,0.20699],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.63476,0.14567,0.20468]}],"total_contact_groups":17},"final_pose_error":0.02989,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56875,0.06941,0.01602],"final_tcp_position":[0.63243,0.15008,0.29481],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.35316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.53685,0.00098,0.14683],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1302,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.1559,"subtask_id":"reach_pregrasp","tcp_end":[0.53858,0.00103,0.04158],"tcp_start":[0.53685,0.00098,0.14683],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00074,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25052,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.11168,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15737.0,"raw_peak_contact_force":0.61079,"tcp_end":[0.52995,0.00087,0.03146],"tcp_start":[0.53858,0.00103,0.04158],"tcp_to_object_dist_end":0.01529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":537.0,"n_steps_budget":600.0,"object_pos_end":[0.54204,0.00081,0.11108],"object_pos_start":[0.54418,0.00074,0.02587],"object_to_goal_dist_end":0.20563,"object_to_goal_dist_start":0.25052,"object_z_max":0.11096,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9677.0,"raw_peak_contact_force":1.35316,"subtask_id":"lift_clearance","tcp_end":[0.52577,0.0008,0.12633],"tcp_start":[0.52995,0.00087,0.03146],"tcp_to_object_dist_end":0.02229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56875,0.06941,0.01602],"object_pos_start":[0.54204,0.00081,0.11108],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.20563,"object_z_max":0.12061,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.63099,0.13965,0.21991],"tcp_start":[0.52577,0.0008,0.12633],"tcp_to_object_dist_end":0.22445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.56875,0.06941,0.01602],"object_pos_start":[0.56875,0.06941,0.01602],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.21152,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.63973,0.15213,0.19062],"tcp_start":[0.63099,0.13965,0.21991],"tcp_to_object_dist_end":0.20583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56875,0.06941,0.01602],"object_pos_start":[0.56875,0.06941,0.01602],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.21152,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":772.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63417,0.1507,0.20931],"tcp_start":[0.63973,0.15213,0.19062],"tcp_to_object_dist_end":0.21965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":600.0,"object_pos_end":[0.56875,0.06941,0.01602],"object_pos_start":[0.56875,0.06941,0.01602],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.21152,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.63243,0.15008,0.29481],"tcp_start":[0.63417,0.1507,0.20931],"tcp_to_object_dist_end":0.29713,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22689,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08157,"approach_1.approach_speed":0.24651,"approach_goal.approach_goal_height":0.07178,"approach_goal.approach_goal_speed":0.38502,"descend_1.descend_speed":0.2032,"descend_1.descend_z_offset":0.00574,"descend_goal.descend_goal_speed":0.26684,"lift_1.lift_height":0.11794,"lift_1.lift_speed":0.18507,"retract_1.retract_height":0.14528,"retract_1.retract_speed":0.24413},"optimized_scores":{"best_composite_score":-0.01764,"best_fitness_score":0.71236,"best_task_score":0.47174},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1946.0,"contact_point_centroid":[0.56683,0.12329,-0.00244],"force_p95":0.19963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36362,"mean_force":0.14662,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57076,0.13261,0.15884]},{"body_a":"world","body_b":"grasp_target","contact_count":167.0,"contact_point_centroid":[0.52719,0.02908,-0.00124],"force_p95":0.39653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64394,"mean_force":0.10164,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51455,0.02941,0.03173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8094.0,"contact_point_centroid":[0.5153,0.04809,0.07327],"force_p95":0.10817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33421,"mean_force":0.06954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51223,0.02926,0.07144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7674.0,"contact_point_centroid":[0.51535,0.01041,0.0758],"force_p95":0.10968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33194,"mean_force":0.07215,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51219,0.02926,0.07364]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3547.0,"contact_point_centroid":[0.53127,0.03919,0.13683],"force_p95":0.1717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27763,"mean_force":0.11042,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52613,0.05749,0.13783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4297.0,"contact_point_centroid":[0.53245,0.07776,0.13668],"force_p95":0.14207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23917,"mean_force":0.09341,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52737,0.0597,0.13837]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03052,-0.00211],"force_p95":0.15571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22836,"mean_force":0.13146,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51752,0.02961,0.03149]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.51724,0.01033,0.03287],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14367,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51631,0.02953,0.03012]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51105,0.01404,0.20854]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52327,0.02916,0.07897]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.56693,0.12356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59139,0.16886,0.14072]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56693,0.12356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58957,0.17261,0.11425]},{"body_a":"world","body_b":"grasp_target","contact_count":948.0,"contact_point_centroid":[0.56693,0.12356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5853,0.17116,0.19056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4980.0,"contact_point_centroid":[0.51718,0.04868,0.03192],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0872,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51631,0.02953,0.03013]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1785.0,"contact_point_centroid":[0.57364,0.13684,0.16233],"force_p95":0.01188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01068,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57331,0.13683,0.16006]},{"body_a":"left_finger","body_b":"right_finger","contact_count":734.0,"contact_point_centroid":[0.59172,0.1689,0.14288],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01055,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59139,0.16887,0.14064]}],"total_contact_groups":17},"final_pose_error":0.02956,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56693,0.12356,0.01602],"final_tcp_position":[0.58545,0.17115,0.24986],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.71935,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.52419,0.02839,0.11882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14866,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10849.0,"raw_peak_contact_force":0.22836,"subtask_id":"reach_pregrasp","tcp_end":[0.52474,0.03009,0.03972],"tcp_start":[0.52419,0.02839,0.11882],"tcp_to_object_dist_end":0.01487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.02956,0.02562],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18457,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.11287,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15935.0,"raw_peak_contact_force":0.64394,"tcp_end":[0.51628,0.02953,0.03009],"tcp_start":[0.52474,0.03009,0.03972],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5296,0.02949,0.11917],"object_pos_start":[0.5304,0.02956,0.02562],"object_to_goal_dist_end":0.16591,"object_to_goal_dist_start":0.18457,"object_z_max":0.11904,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11575.0,"raw_peak_contact_force":1.36362,"subtask_id":"lift_clearance","tcp_end":[0.51228,0.02927,0.13405],"tcp_start":[0.51628,0.02953,0.03009],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56693,0.12356,0.01602],"object_pos_start":[0.5296,0.02949,0.11917],"object_to_goal_dist_end":0.1127,"object_to_goal_dist_start":0.16591,"object_z_max":0.12054,"peak_contact_force":9748.71935,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1430.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.58995,0.16454,0.16802],"tcp_start":[0.51228,0.02927,0.13405],"tcp_to_object_dist_end":0.1591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.56693,0.12356,0.01602],"object_pos_start":[0.56693,0.12356,0.01602],"object_to_goal_dist_end":0.1127,"object_to_goal_dist_start":0.1127,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.59467,0.17411,0.11367],"tcp_start":[0.58995,0.16454,0.16802],"tcp_to_object_dist_end":0.11341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56693,0.12356,0.01602],"object_pos_start":[0.56693,0.12356,0.01602],"object_to_goal_dist_end":0.1127,"object_to_goal_dist_start":0.1127,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":948.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58768,0.17199,0.13404],"tcp_start":[0.59467,0.17411,0.11367],"tcp_to_object_dist_end":0.12925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.56693,0.12356,0.01602],"object_pos_start":[0.56693,0.12356,0.01602],"object_to_goal_dist_end":0.1127,"object_to_goal_dist_start":0.1127,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.58545,0.17115,0.24986],"tcp_start":[0.58768,0.17199,0.13404],"tcp_to_object_dist_end":0.23935,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09135,"approach_1.approach_speed":0.28837,"approach_goal.approach_goal_height":0.0581,"approach_goal.approach_goal_speed":0.37746,"descend_1.descend_speed":0.17413,"descend_1.descend_z_offset":0.00576,"descend_goal.descend_goal_speed":0.14497,"lift_1.lift_height":0.11905,"lift_1.lift_speed":0.22378,"retract_1.retract_height":0.11558,"retract_1.retract_speed":0.24389},"optimized_scores":{"best_composite_score":-0.17095,"best_fitness_score":0.55905,"best_task_score":0.16368},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2604.0,"contact_point_centroid":[0.51672,0.06395,-0.00242],"force_p95":0.20674,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61093,"mean_force":0.14724,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54238,0.10281,0.22952]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.50101,-0.01515,-0.00115],"force_p95":0.39372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63934,"mean_force":0.09507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48905,-0.01531,0.03334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1950.0,"contact_point_centroid":[0.49761,-0.01776,0.14652],"force_p95":0.18168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37634,"mean_force":0.10749,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49204,0.00078,0.14687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7959.0,"contact_point_centroid":[0.48924,0.00367,0.07795],"force_p95":0.10795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35316,"mean_force":0.06935,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48668,-0.01527,0.07568]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.48932,-0.03411,0.07612],"force_p95":0.10338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32058,"mean_force":0.06507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4867,-0.01527,0.07442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2418.0,"contact_point_centroid":[0.49837,0.01979,0.14689],"force_p95":0.15847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29564,"mean_force":0.09036,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49238,0.00156,0.14745]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01553,-0.00203],"force_p95":0.13322,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16076,"mean_force":0.12559,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49178,-0.01534,0.03294]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49885,-0.00704,0.21492]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49791,-0.01486,0.08482]},{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.5167,0.06538,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57533,0.1697,0.2611]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5167,0.06538,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57725,0.17904,0.24838]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.5167,0.06538,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57502,0.17809,0.30972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49117,0.00387,0.03446],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11917,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49062,-0.01533,0.03171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4886.0,"contact_point_centroid":[0.49122,-0.03441,0.03354],"force_p95":0.06858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08931,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49062,-0.01533,0.03171]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2692.0,"contact_point_centroid":[0.54375,0.10483,0.23349],"force_p95":0.01116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54339,0.10483,0.23118]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57959,0.17987,0.24658],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57921,0.17985,0.24432]}],"total_contact_groups":17},"final_pose_error":0.02959,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5167,0.06538,0.01602],"final_tcp_position":[0.5752,0.17807,0.35419],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.61093,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.49955,-0.01435,0.13017],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13089,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.16076,"subtask_id":"reach_pregrasp","tcp_end":[0.49873,-0.01543,0.04038],"tcp_start":[0.49955,-0.01435,0.13017],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01521,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.11421,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16722.0,"raw_peak_contact_force":0.63934,"tcp_end":[0.49059,-0.01533,0.03168],"tcp_start":[0.49873,-0.01543,0.04038],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":541.0,"n_steps_budget":600.0,"object_pos_end":[0.50378,-0.01522,0.12153],"object_pos_start":[0.50369,-0.01521,0.02587],"object_to_goal_dist_end":0.253,"object_to_goal_dist_start":0.31207,"object_z_max":0.12139,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9664.0,"raw_peak_contact_force":1.61093,"subtask_id":"lift_clearance","tcp_end":[0.48675,-0.01526,0.13723],"tcp_start":[0.49059,-0.01533,0.03168],"tcp_to_object_dist_end":0.02316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5167,0.06538,0.01602],"object_pos_start":[0.50378,-0.01522,0.12153],"object_to_goal_dist_end":0.27148,"object_to_goal_dist_start":0.253,"object_z_max":0.13928,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1243.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.5713,0.16028,0.27662],"tcp_start":[0.48675,-0.01526,0.13723],"tcp_to_object_dist_end":0.28266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.5167,0.06538,0.01602],"object_pos_start":[0.5167,0.06538,0.01602],"object_to_goal_dist_end":0.27148,"object_to_goal_dist_start":0.27148,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place","tcp_end":[0.58043,0.17998,0.24742],"tcp_start":[0.5713,0.16028,0.27662],"tcp_to_object_dist_end":0.26597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5167,0.06538,0.01602],"object_pos_start":[0.5167,0.06538,0.01602],"object_to_goal_dist_end":0.27148,"object_to_goal_dist_start":0.27148,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":736.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57616,0.17859,0.26818],"tcp_start":[0.58043,0.17998,0.24742],"tcp_to_object_dist_end":0.28274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":600.0,"object_pos_end":[0.5167,0.06538,0.01602],"object_pos_start":[0.5167,0.06538,0.01602],"object_to_goal_dist_end":0.27148,"object_to_goal_dist_start":0.27148,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.5752,0.17807,0.35419],"tcp_start":[0.57616,0.17859,0.26818],"tcp_to_object_dist_end":0.36122,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```