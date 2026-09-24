## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.4159 | 0.23 | ✅ accepted |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 0 | 0.3911 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.416) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_1
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
    - 0.05
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_1
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
    - 0.0
    orientation:
      mode: keep_current
- id: grasp_1
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
    orientation:
      mode: keep_current
- id: lift_1
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
    orientation:
      mode: keep_current
- id: approach_2
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  guards:
  - id: check_grasp_before
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
  - id: monitor_grasp
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
  subtask_id: reach_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: reach_goal
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
    orientation:
      mode: keep_current
- id: retract_1
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
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=check_grasp_before, when=before_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
    - id=monitor_grasp, when=during_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.416
- **task_score** (E): 0.232
- **fitness_score**: 0.596  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2157 |
| descend_1 | 1.00 | 1.00 | 0.0547 |
| grasp_1 | 1.00 | 1.00 | 0.0111 |
| lift_1 | 1.00 | 1.00 | 0.1375 |
| approach_2 | 0.00 | 0.67 | 0.0242 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.089) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.476, -0.000, 0.089)→(0.474, -0.001, 0.035) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.035)→(0.466, -0.001, 0.027) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.667 | 0.145 | 0.218 |
| lift_1 | lift | 1.00 / step_budget | (0.466, -0.001, 0.027)→(0.474, -0.001, 0.164) | (0.479, -0.001, 0.026)→(0.490, -0.001, 0.147) | 0.278→0.242 | 1.00 / 19.667 | 0.163 | 0.638 |
| approach_2 | approach | 0.00 / guard_failure | (0.474, -0.001, 0.164)→(0.484, 0.020, 0.167) | (0.490, -0.001, 0.147)→(0.494, 0.020, 0.137) | 0.242→0.222 | 0.67 / 3.000 | 0.000 | 0.280 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.292
- phase_score: 0.261
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.reach_goal_score: 0.021
- grasp_place_fitness: 0.625

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.232
- **Median Q (composite search score)**: 0.416
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: no_parameters
- **Mean generations**: 0.0
- **Final σ (mean)**: 0.000


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79245,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.44478,"best_fitness_score":0.62478,"best_task_score":0.29233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.49904,0.04219,-0.00124],"force_p95":0.46752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65412,"mean_force":0.07792,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48641,0.04307,0.02772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12835.0,"contact_point_centroid":[0.49231,0.06167,0.08552],"force_p95":0.11687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31071,"mean_force":0.07025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48928,0.04285,0.08446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12173.0,"contact_point_centroid":[0.49247,0.02407,0.08705],"force_p95":0.11737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2993,"mean_force":0.07262,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48937,0.04285,0.0857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1385.0,"contact_point_centroid":[0.50082,0.07123,0.15964],"force_p95":0.14984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26162,"mean_force":0.10437,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49796,0.05357,0.16441]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04464,-0.00217],"force_p95":0.17271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26161,"mean_force":0.13585,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48887,0.04333,0.02702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1138.0,"contact_point_centroid":[0.50063,0.0339,0.15946],"force_p95":0.1624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24621,"mean_force":0.10599,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49765,0.05193,0.16409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3798.0,"contact_point_centroid":[0.48886,0.02403,0.02877],"force_p95":0.08583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15031,"mean_force":0.05503,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4877,0.04322,0.0258]},{"body_a":"world","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49744,0.0207,0.19347]},{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49533,0.04283,0.06127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4970.0,"contact_point_centroid":[0.48846,0.06238,0.02763],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08645,"mean_force":0.04534,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48771,0.04322,0.02581]}],"total_contact_groups":10},"final_pose_error":0.20826,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50928,0.06937,0.1328],"final_tcp_position":[0.50018,0.06361,0.16683],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.65412,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49698,0.0419,0.08836],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49579,0.04396,0.03437],"tcp_start":[0.49698,0.0419,0.08836],"tcp_to_object_dist_end":0.00999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04324,0.02545],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24368,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16046,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10568.0,"raw_peak_contact_force":0.26161,"tcp_end":[0.48767,0.04321,0.02577],"tcp_start":[0.49579,0.04396,0.03437],"tcp_to_object_dist_end":0.01341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.51154,0.04304,0.14526],"object_pos_start":[0.50108,0.04324,0.02545],"object_to_goal_dist_end":0.20864,"object_to_goal_dist_start":0.24368,"object_z_max":0.14518,"peak_contact_force":0.15899,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25154.0,"raw_peak_contact_force":0.65412,"tcp_end":[0.49671,0.04291,0.16347],"tcp_start":[0.48767,0.04321,0.02577],"tcp_to_object_dist_end":0.02348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.50928,0.06937,0.1328],"object_pos_start":[0.51154,0.04304,0.14526],"object_to_goal_dist_end":0.18448,"object_to_goal_dist_start":0.20864,"object_z_max":0.14527,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2523.0,"raw_peak_contact_force":0.26162,"subtask_id":"reach_goal","tcp_end":[0.50018,0.06361,0.16683],"tcp_start":[0.49671,0.04291,0.16347],"tcp_to_object_dist_end":0.03569,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78846,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.41312,"best_fitness_score":0.59312,"best_task_score":0.22637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.47374,-0.01901,-0.0011],"force_p95":0.47374,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63662,"mean_force":0.0671,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46238,-0.01955,0.02863]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1374.0,"contact_point_centroid":[0.48067,-0.02876,0.16217],"force_p95":0.16173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31325,"mean_force":0.11048,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47685,-0.01094,0.1667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11955.0,"contact_point_centroid":[0.46787,-0.00065,0.08739],"force_p95":0.11411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29089,"mean_force":0.07156,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46491,-0.01948,0.08575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12657.0,"contact_point_centroid":[0.46784,-0.03828,0.08649],"force_p95":0.1114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28441,"mean_force":0.06858,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46488,-0.01948,0.08523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1203.0,"contact_point_centroid":[0.48005,0.00663,0.16197],"force_p95":0.17941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26248,"mean_force":0.11544,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.47641,-0.01147,0.16639]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02002,-0.00205],"force_p95":0.13804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1882,"mean_force":0.12683,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46467,-0.0196,0.02794]},{"body_a":"world","body_b":"grasp_target","contact_count":2536.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48598,-0.00924,0.19431]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47148,-0.0192,0.06198]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46339,-0.00033,0.02992],"force_p95":0.06684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09316,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46355,-0.01958,0.02685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5403.0,"contact_point_centroid":[0.46326,-0.03884,0.0294],"force_p95":0.06515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08617,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46355,-0.01958,0.02685]}],"total_contact_groups":10},"final_pose_error":0.25073,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.49299,-0.00751,0.13799],"final_tcp_position":[0.48255,-0.00332,0.17047],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.63662,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47373,-0.01872,0.08959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":756.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47132,-0.01975,0.03456],"tcp_start":[0.47373,-0.01872,0.08959],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.01961,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13577,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12269.0,"raw_peak_contact_force":0.1882,"tcp_end":[0.46352,-0.01958,0.02682],"tcp_start":[0.47132,-0.01975,0.03456],"tcp_to_object_dist_end":0.01255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":844.0,"n_steps_budget":930.0,"object_pos_end":[0.48732,-0.01926,0.14728],"object_pos_start":[0.47603,-0.01961,0.02581],"object_to_goal_dist_end":0.23332,"object_to_goal_dist_start":0.28823,"object_z_max":0.1472,"peak_contact_force":0.16224,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24741.0,"raw_peak_contact_force":0.63662,"tcp_end":[0.47178,-0.0195,0.16414],"tcp_start":[0.46352,-0.01958,0.02682],"tcp_to_object_dist_end":0.02294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.49299,-0.00751,0.13799],"object_pos_start":[0.48732,-0.01926,0.14728],"object_to_goal_dist_end":0.22284,"object_to_goal_dist_start":0.23332,"object_z_max":0.14728,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2577.0,"raw_peak_contact_force":0.31325,"subtask_id":"reach_goal","tcp_end":[0.48255,-0.00332,0.17047],"tcp_start":[0.47178,-0.0195,0.16414],"tcp_to_object_dist_end":0.03437,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79439,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.38978,"best_fitness_score":0.56978,"best_task_score":0.17812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.45631,-0.02487,-0.00112],"force_p95":0.45815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62354,"mean_force":0.0651,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44545,-0.02547,0.02943]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12113.0,"contact_point_centroid":[0.45079,-0.00655,0.08836],"force_p95":0.11206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28201,"mean_force":0.07032,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44781,-0.02539,0.08666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12819.0,"contact_point_centroid":[0.45048,-0.04423,0.08729],"force_p95":0.10887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28091,"mean_force":0.0674,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44775,-0.02539,0.0858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1767.0,"contact_point_centroid":[0.46607,-0.02979,0.15953],"force_p95":0.15262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26372,"mean_force":0.10905,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.46198,-0.01163,0.16381]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.46559,0.0063,0.15942],"force_p95":0.16062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22995,"mean_force":0.10752,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.46184,-0.01181,0.16377]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02615,-0.00207],"force_p95":0.14276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20551,"mean_force":0.12812,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44765,-0.02555,0.02864]},{"body_a":"world","body_b":"grasp_target","contact_count":2556.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4779,-0.01207,0.19433]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45472,-0.02507,0.06216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5050.0,"contact_point_centroid":[0.44624,-0.0063,0.03017],"force_p95":0.06664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1022,"mean_force":0.04288,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44657,-0.02551,0.02762]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5184.0,"contact_point_centroid":[0.44648,-0.04478,0.02956],"force_p95":0.06751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08094,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44657,-0.02551,0.02762]}],"total_contact_groups":10},"final_pose_error":0.26618,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.47909,-0.0004,0.1394],"final_tcp_position":[0.47047,0.00094,0.16514],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.62354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45734,-0.02446,0.08964],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06366,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":764.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4541,-0.02578,0.03479],"tcp_start":[0.45734,-0.02446,0.08964],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02559,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30323,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13963,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12034.0,"raw_peak_contact_force":0.20551,"tcp_end":[0.44654,-0.02551,0.02759],"tcp_start":[0.4541,-0.02578,0.03479],"tcp_to_object_dist_end":0.01204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.46995,-0.02537,0.14789],"object_pos_start":[0.45844,-0.02559,0.02576],"object_to_goal_dist_end":0.28524,"object_to_goal_dist_start":0.30323,"object_z_max":0.14782,"peak_contact_force":0.16814,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25056.0,"raw_peak_contact_force":0.62354,"tcp_end":[0.45429,-0.02543,0.16444],"tcp_start":[0.44654,-0.02551,0.02759],"tcp_to_object_dist_end":0.02278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.47909,-0.0004,0.1394],"object_pos_start":[0.46995,-0.02537,0.14789],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.28524,"object_z_max":0.14789,"peak_contact_force":0.0,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3555.0,"raw_peak_contact_force":0.26372,"subtask_id":"reach_goal","tcp_end":[0.47047,0.00094,0.16514],"tcp_start":[0.45429,-0.02543,0.16444],"tcp_to_object_dist_end":0.02717,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```