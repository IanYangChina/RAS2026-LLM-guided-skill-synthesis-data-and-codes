## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1019 | 0.30 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.0718 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0852 | 0.34 | ✅ accepted |
| 7 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 6 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

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

## Current Skill (Q=-0.102) — your mutation base

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

- **Composite score**: -0.102
- **task_score** (E): 0.301
- **fitness_score**: 0.628  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1713 |
| descend_1 | 1.00 | 1.00 | 0.0957 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 1.00 | 1.00 | 0.1158 |
| approach_goal | 0.00 | 1.00 | 0.0016 |
| descend_goal | 0.00 | 1.00 | 0.1589 |
| release_1 | 1.00 | 1.00 | 0.0581 |
| retract_1 | 1.00 | 1.00 | 0.1069 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.133) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.133)→(0.521, 0.005, 0.037) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.136 | 0.183 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.037)→(0.512, 0.005, 0.027) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 21.333 | 524.463 | 0.724 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.027)→(0.508, 0.005, 0.143) | (0.526, 0.005, 0.026)→(0.527, 0.005, 0.130) | 0.249→0.205 | 1.00 / 19.333 | 55984.202 | 0.457 |
| approach_goal | approach | 0.00 / guard_failure | (0.581, 0.021, 0.105)→(0.583, 0.021, 0.104) | (0.527, 0.005, 0.130)→(0.600, 0.023, 0.093) | 0.205→0.195 | 1.00 / 12.000 | 562.316 | 1074.258 |
| descend_goal | descend | 0.00 / step_budget | (0.583, 0.021, 0.104)→(0.602, 0.129, 0.154) | (0.604, 0.024, 0.091)→(0.592, 0.088, 0.034) | 0.197→0.188 | 1.00 / 3.333 | 2.932 | 251.701 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.129, 0.154)→(0.617, 0.132, 0.157) | (0.592, 0.088, 0.034)→(0.613, 0.090, 0.019) | 0.188→0.202 | 1.00 / 4.000 | 0.123 | 0.155 |
| retract_1 | retract | 1.00 / step_budget | (0.617, 0.132, 0.157)→(0.616, 0.132, 0.263) | (0.613, 0.090, 0.019)→(0.611, 0.089, 0.019) | 0.202→0.202 | 1.00 / 4.000 | 0.123 | 0.138 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.529
- phase_score: 0.220
- phase_breakdown.lift_clearance_score: 0.405
- phase_breakdown.reach_pregrasp_score: 0.241
- phase_breakdown.place_score: 0.133
- grasp_place_fitness: 0.742

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.529
- **Median Q (composite search score)**: -0.140
- **K-run variance**: 0.0067
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.19048,"average_mean_iterations":43.21429,"average_solve_count":126.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08173,"approach_1.approach_speed":0.20681,"approach_goal.approach_goal_height":0.21957,"approach_goal.approach_goal_speed":0.28741,"descend_1.descend_speed":0.15136,"descend_1.descend_z_offset":0.00102,"descend_goal.descend_goal_speed":0.14808,"lift_1.lift_height":0.16014,"lift_1.lift_speed":0.18107,"retract_1.retract_height":0.13958,"retract_1.retract_speed":0.1419},"optimized_scores":{"best_composite_score":-0.13988,"best_fitness_score":0.59012,"best_task_score":0.22667},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":83.0,"contact_point_centroid":[0.66605,-0.06589,-0.00221],"force_p95":827.80929,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":997.67512,"mean_force":264.47943,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59934,-0.04364,-0.00884]},{"body_a":"world","body_b":"link5","contact_count":856.0,"contact_point_centroid":[0.60814,0.13337,-0.00026],"force_p95":268.44038,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":860.35314,"mean_force":222.66963,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57586,-0.04194,0.19218]},{"body_a":"world","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.70026,-0.04388,-0.00071],"force_p95":506.66464,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":545.88735,"mean_force":203.24776,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57303,-0.09045,0.06214]},{"body_a":"world","body_b":"link5","contact_count":82.0,"contact_point_centroid":[0.57622,0.13562,-0.00013],"force_p95":120.75626,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.11219,"mean_force":68.46583,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64706,0.10314,0.28777]},{"body_a":"world","body_b":"right_finger","contact_count":799.0,"contact_point_centroid":[0.59631,-0.02106,-0.01263],"force_p95":26.34088,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.03676,"mean_force":11.42571,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60241,-0.0379,-0.01268]},{"body_a":"world","body_b":"left_finger","contact_count":868.0,"contact_point_centroid":[0.60993,-0.05433,-0.01182],"force_p95":19.01774,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.86132,"mean_force":9.66783,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60154,-0.03944,-0.01129]},{"body_a":"grasp_target","body_b":"hand","contact_count":305.0,"contact_point_centroid":[0.60837,0.0032,0.03105],"force_p95":1.55021,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.78271,"mean_force":0.75328,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56835,-0.06389,0.07417]},{"body_a":"grasp_target","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.60969,0.01705,0.03284],"force_p95":1.33824,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.23937,"mean_force":0.48396,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55243,-0.08093,0.11539]},{"body_a":"world","body_b":"grasp_target","contact_count":3505.0,"contact_point_centroid":[0.58548,0.03396,-0.00351],"force_p95":0.84238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.10039,"mean_force":0.23967,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.58181,-0.03803,0.17653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":538.0,"contact_point_centroid":[0.58542,0.03046,0.14991],"force_p95":0.46651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.93818,"mean_force":0.23976,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58207,0.0114,0.15395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":49.0,"contact_point_centroid":[0.65352,-0.00367,0.06498],"force_p95":0.86863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.91124,"mean_force":0.4898,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.64593,0.01331,0.07083]},{"body_a":"world","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.54088,0.00072,-0.00112],"force_p95":0.5585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82795,"mean_force":0.09024,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52814,0.00083,0.02665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":571.0,"contact_point_centroid":[0.59072,-0.00602,0.14819],"force_p95":0.51038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73252,"mean_force":0.23326,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58453,0.01158,0.15197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":35.0,"contact_point_centroid":[0.6491,0.0336,0.06617],"force_p95":0.52359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54354,"mean_force":0.33996,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.6464,0.01387,0.07259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7392.0,"contact_point_centroid":[0.52915,-0.01803,0.08763],"force_p95":0.11475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38296,"mean_force":0.07592,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52562,0.00079,0.08568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7760.0,"contact_point_centroid":[0.52918,0.01955,0.08493],"force_p95":0.1129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36522,"mean_force":0.07288,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52565,0.00079,0.08322]}],"total_contact_groups":25},"final_pose_error":0.02998,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57278,0.0427,0.01602],"final_tcp_position":[0.64866,0.10295,0.42241],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.53704,0.00099,0.1184],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1298,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16051,"subtask_id":"reach_pregrasp","tcp_end":[0.53829,0.00102,0.03499],"tcp_start":[0.53704,0.00099,0.1184],"tcp_to_object_dist_end":0.0108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1846,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15266.0,"raw_peak_contact_force":0.82795,"tcp_end":[0.52957,0.00086,0.02489],"tcp_start":[0.53829,0.00102,0.03499],"tcp_to_object_dist_end":0.01462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.54618,0.00089,0.15627],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.1903,"object_to_goal_dist_start":0.25053,"object_z_max":0.15611,"peak_contact_force":0.76449,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1109.0,"raw_peak_contact_force":0.93818,"subtask_id":"lift_clearance","tcp_end":[0.52599,0.0008,0.16842],"tcp_start":[0.52957,0.00086,0.02489],"tcp_to_object_dist_end":0.02356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.67793,0.02083,0.07683],"object_pos_start":[0.54618,0.00089,0.15627],"object_to_goal_dist_end":0.18115,"object_to_goal_dist_start":0.1903,"object_z_max":0.15649,"peak_contact_force":262.44326,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10132.0,"raw_peak_contact_force":997.67512,"subtask_id":"place","tcp_end":[0.64822,0.0161,0.08175],"tcp_start":[0.64822,0.0161,0.08175],"tcp_to_object_dist_end":0.03049,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57278,0.0427,0.01602],"object_pos_start":[0.67784,0.02038,0.07318],"object_to_goal_dist_end":0.22264,"object_to_goal_dist_start":0.1838,"object_z_max":0.07318,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1110.0,"raw_peak_contact_force":241.11219,"subtask_id":"place","tcp_end":[0.64604,0.09852,0.28728],"tcp_start":[0.64822,0.0161,0.08175],"tcp_to_object_dist_end":0.28647,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57278,0.0427,0.01602],"object_pos_start":[0.57278,0.0427,0.01602],"object_to_goal_dist_end":0.22264,"object_to_goal_dist_start":0.22264,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":952.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.64722,0.10205,0.31275],"tcp_start":[0.64604,0.09852,0.28728],"tcp_to_object_dist_end":0.31163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":238.0,"n_steps_budget":630.0,"object_pos_end":[0.57278,0.0427,0.01602],"object_pos_start":[0.57278,0.0427,0.01602],"object_to_goal_dist_end":0.22264,"object_to_goal_dist_start":0.22264,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.64866,0.10295,0.42241],"tcp_start":[0.64722,0.10205,0.31275],"tcp_to_object_dist_end":0.41778,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.32787,"average_mean_iterations":68.45902,"average_solve_count":122.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10713,"approach_1.approach_speed":0.40246,"approach_goal.approach_goal_height":0.1996,"approach_goal.approach_goal_speed":0.41794,"descend_1.descend_speed":0.28143,"descend_1.descend_z_offset":0.00509,"descend_goal.descend_goal_speed":0.16983,"lift_1.lift_height":0.12333,"lift_1.lift_speed":0.1526,"retract_1.retract_height":0.09486,"retract_1.retract_speed":0.14656},"optimized_scores":{"best_composite_score":0.01167,"best_fitness_score":0.74167,"best_task_score":0.52914},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":31.0,"contact_point_centroid":[0.65166,0.26846,-0.00651],"force_p95":1992.04149,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2225.09863,"mean_force":545.56264,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55464,0.24444,0.00048]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.69675,0.06188,-0.00536],"force_p95":1805.21855,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1861.89938,"mean_force":1588.42081,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.565,0.27119,0.0666]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.70662,0.0612,-0.00138],"force_p95":434.46064,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":490.1187,"mean_force":180.95012,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59419,0.27229,0.11674]},{"body_a":"world","body_b":"right_finger","contact_count":246.0,"contact_point_centroid":[0.56349,0.24393,-0.00816],"force_p95":35.54186,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.80332,"mean_force":11.51603,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55476,0.23795,-0.00592]},{"body_a":"world","body_b":"left_finger","contact_count":194.0,"contact_point_centroid":[0.54511,0.22768,-0.00583],"force_p95":39.38828,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.79434,"mean_force":11.28146,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55454,0.23706,-0.00869]},{"body_a":"grasp_target","body_b":"hand","contact_count":65.0,"contact_point_centroid":[0.61625,0.20662,0.03078],"force_p95":3.26578,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.81654,"mean_force":1.22284,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55926,0.24331,0.02204]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.61174,0.184,-0.01153],"force_p95":2.38268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.09102,"mean_force":0.95333,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56003,0.24129,0.02314]},{"body_a":"grasp_target","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.62334,0.17442,0.01406],"force_p95":2.84343,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.85315,"mean_force":1.34795,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56308,0.26975,0.05996]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.52736,0.02907,-0.00124],"force_p95":0.42374,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67688,"mean_force":0.10239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51485,0.02946,0.03126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":440.0,"contact_point_centroid":[0.54427,0.0425,0.12591],"force_p95":0.44269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67376,"mean_force":0.23454,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.54081,0.06239,0.12671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.53318,0.06101,0.13471],"force_p95":0.37003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60577,"mean_force":0.13508,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.52603,0.04334,0.1339]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59824,0.20359,-0.00214],"force_p95":0.15982,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52915,"mean_force":0.12125,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59408,0.27298,0.12339]},{"body_a":"grasp_target","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.622,0.18088,0.02547],"force_p95":0.51137,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52546,"mean_force":0.3103,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5753,0.27016,0.08866]},{"body_a":"grasp_target","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.62698,0.19524,0.02585],"force_p95":0.43146,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43146,"mean_force":0.43146,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57152,0.27088,0.08075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7738.0,"contact_point_centroid":[0.51547,0.01043,0.07735],"force_p95":0.1096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3471,"mean_force":0.07155,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51245,0.0293,0.07516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8286.0,"contact_point_centroid":[0.51543,0.04814,0.07493],"force_p95":0.1069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33975,"mean_force":0.06807,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51248,0.02931,0.07314]}],"total_contact_groups":24},"final_pose_error":0.02966,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59822,0.20363,0.01602],"final_tcp_position":[0.59212,0.27317,0.20866],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":2225.09863,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.52412,0.02809,0.14423],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14788,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10847.0,"raw_peak_contact_force":0.22726,"subtask_id":"reach_pregrasp","tcp_end":[0.52499,0.03014,0.03917],"tcp_start":[0.52412,0.02809,0.14423],"tcp_to_object_dist_end":0.01427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53039,0.02959,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18455,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.11251,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16185.0,"raw_peak_contact_force":0.67688,"tcp_end":[0.51652,0.02958,0.02954],"tcp_start":[0.52499,0.03014,0.03917],"tcp_to_object_dist_end":0.01442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53026,0.02951,0.12406],"object_pos_start":[0.53039,0.02959,0.02563],"object_to_goal_dist_end":0.166,"object_to_goal_dist_start":0.18455,"object_z_max":0.12391,"peak_contact_force":0.11264,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"lift_clearance","tcp_end":[0.51259,0.02932,0.13854],"tcp_start":[0.51652,0.02958,0.02954],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.53026,0.02951,0.12406],"object_pos_start":[0.53026,0.02951,0.12406],"object_to_goal_dist_end":0.166,"object_to_goal_dist_start":0.166,"peak_contact_force":1424.28241,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1383.0,"raw_peak_contact_force":2225.09863,"subtask_id":"place","tcp_end":[0.51259,0.02932,0.13854],"tcp_start":[0.51259,0.02932,0.13854],"tcp_to_object_dist_end":0.02284,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.59936,0.20058,0.00862],"object_pos_start":[0.53026,0.02951,0.12406],"object_to_goal_dist_end":0.1019,"object_to_goal_dist_start":0.166,"object_z_max":0.12416,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":918.0,"raw_peak_contact_force":490.1187,"subtask_id":"place","tcp_end":[0.57152,0.27088,0.08075],"tcp_start":[0.51259,0.02932,0.13854],"tcp_to_object_dist_end":0.1045,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59822,0.20363,0.01602],"object_pos_start":[0.59936,0.20058,0.00862],"object_to_goal_dist_end":0.09547,"object_to_goal_dist_start":0.1019,"object_z_max":0.01675,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":600.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59371,0.27356,0.14342],"tcp_start":[0.57152,0.27088,0.08075],"tcp_to_object_dist_end":0.1454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":150.0,"n_steps_budget":600.0,"object_pos_end":[0.59822,0.20363,0.01602],"object_pos_start":[0.59822,0.20363,0.01602],"object_to_goal_dist_end":0.09547,"object_to_goal_dist_start":0.09547,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.59212,0.27317,0.20866],"tcp_start":[0.59371,0.27356,0.14342],"tcp_to_object_dist_end":0.2049,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":47.0,"average_failure_rate":0.35878,"average_mean_iterations":75.63359,"average_solve_count":131.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09601,"approach_1.approach_speed":0.20752,"approach_goal.approach_goal_height":0.16244,"approach_goal.approach_goal_speed":0.49123,"descend_1.descend_speed":0.18351,"descend_1.descend_z_offset":0.00185,"descend_goal.descend_goal_speed":0.21727,"lift_1.lift_height":0.10731,"lift_1.lift_speed":0.23823,"retract_1.retract_height":0.17518,"retract_1.retract_speed":0.31693},"optimized_scores":{"best_composite_score":-0.17753,"best_fitness_score":0.55247,"best_task_score":0.14725},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":2281.0,"contact_point_centroid":[0.61031,0.03706,-0.00646],"force_p95":6.16586,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.87129,"mean_force":2.37612,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6125,0.01914,-0.00818]},{"body_a":"world","body_b":"left_finger","contact_count":2299.0,"contact_point_centroid":[0.61361,0.00108,-0.00656],"force_p95":6.18491,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.63695,"mean_force":2.396,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61253,0.01913,-0.00811]},{"body_a":"grasp_target","body_b":"hand","contact_count":168.0,"contact_point_centroid":[0.65269,0.01733,0.04602],"force_p95":1.26595,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.25928,"mean_force":0.53339,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61274,0.01911,-0.00346]},{"body_a":"world","body_b":"grasp_target","contact_count":651.0,"contact_point_centroid":[0.6635,0.02193,-0.0056],"force_p95":1.0544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.97686,"mean_force":0.33971,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61397,0.01911,-0.00322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.63258,0.00304,0.06337],"force_p95":0.43692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88469,"mean_force":0.2307,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62571,0.02055,0.06727]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":229.0,"contact_point_centroid":[0.62891,0.04062,0.06288],"force_p95":0.4408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67936,"mean_force":0.27476,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62585,0.02054,0.06735]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.50035,-0.01525,-0.00123],"force_p95":0.44669,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66675,"mean_force":0.10341,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48903,-0.01532,0.0291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":422.0,"contact_point_centroid":[0.5245,0.0196,0.1132],"force_p95":0.34454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43382,"mean_force":0.16291,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5198,0.00077,0.11237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7760.0,"contact_point_centroid":[0.48916,0.00366,0.07028],"force_p95":0.10866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33542,"mean_force":0.07004,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48655,-0.01528,0.06801]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":474.0,"contact_point_centroid":[0.52269,-0.019,0.11455],"force_p95":0.26797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33129,"mean_force":0.16069,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51598,-0.00055,0.11354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8523.0,"contact_point_centroid":[0.48921,-0.03411,0.06853],"force_p95":0.10369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30889,"mean_force":0.06477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48657,-0.01528,0.06685]},{"body_a":"world","body_b":"grasp_target","contact_count":1134.0,"contact_point_centroid":[0.66397,0.02199,-0.00205],"force_p95":0.14716,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21888,"mean_force":0.12683,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60538,0.01871,0.08692]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01552,-0.00203],"force_p95":0.13272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16165,"mean_force":0.12551,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49174,-0.01536,0.02893]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49887,-0.00701,0.21735]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49789,-0.01485,0.08509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.49113,0.00386,0.03045],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11544,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49057,-0.01534,0.0277]}],"total_contact_groups":17},"final_pose_error":0.02972,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.66332,0.02193,0.02602],"final_tcp_position":[0.60579,0.01867,0.15916],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.49959,-0.01431,0.1349],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13031,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.16165,"subtask_id":"reach_pregrasp","tcp_end":[0.49872,-0.01544,0.03635],"tcp_start":[0.49959,-0.01431,0.1349],"tcp_to_object_dist_end":0.01152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01521,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31207,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":1573.09317,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16425.0,"raw_peak_contact_force":0.66675,"tcp_end":[0.49054,-0.01534,0.02767],"tcp_start":[0.49872,-0.01544,0.03635],"tcp_to_object_dist_end":0.01327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":531.0,"n_steps_budget":600.0,"object_pos_end":[0.50429,-0.01514,0.11054],"object_pos_start":[0.50368,-0.01521,0.02588],"object_to_goal_dist_end":0.25845,"object_to_goal_dist_start":0.31207,"object_z_max":0.11042,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":896.0,"raw_peak_contact_force":0.43382,"subtask_id":"lift_clearance","tcp_end":[0.48652,-0.01527,0.12226],"tcp_start":[0.49054,-0.01534,0.02767],"tcp_to_object_dist_end":0.02128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.59325,0.01931,0.0788],"object_pos_start":[0.50429,-0.01514,0.11054],"object_to_goal_dist_end":0.2387,"object_to_goal_dist_start":0.25845,"object_z_max":0.11059,"peak_contact_force":0.22217,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place","tcp_end":[0.58762,0.01851,0.09256],"tcp_start":[0.58307,0.01794,0.09395],"tcp_to_object_dist_end":0.01489,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.60293,0.02069,0.07599],"object_pos_start":[0.60293,0.02069,0.07599],"object_to_goal_dist_end":0.24019,"object_to_goal_dist_start":0.24019,"peak_contact_force":8.55016,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5849.0,"raw_peak_contact_force":23.87129,"subtask_id":"place","tcp_end":[0.58762,0.01851,0.09256],"tcp_start":[0.58762,0.01851,0.09256],"tcp_to_object_dist_end":0.02266,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.66945,0.0225,0.02645],"object_pos_start":[0.60293,0.02069,0.07599],"object_to_goal_dist_end":0.28837,"object_to_goal_dist_start":0.24019,"object_z_max":0.07599,"peak_contact_force":0.12268,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1134.0,"raw_peak_contact_force":0.21888,"tcp_end":[0.60931,0.01902,0.01349],"tcp_start":[0.58762,0.01851,0.09256],"tcp_to_object_dist_end":0.06162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":600.0,"object_pos_end":[0.66332,0.02193,0.02602],"object_pos_start":[0.66945,0.0225,0.02645],"object_to_goal_dist_end":0.28734,"object_to_goal_dist_start":0.28837,"object_z_max":0.02655,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.60579,0.01867,0.15916],"tcp_start":[0.60931,0.01902,0.01349],"tcp_to_object_dist_end":0.14508,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```