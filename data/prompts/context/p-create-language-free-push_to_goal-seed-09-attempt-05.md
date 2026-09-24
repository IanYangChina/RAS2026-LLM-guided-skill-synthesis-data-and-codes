## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0177 | 0.47 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1632 | 0.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0217 | 0.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3449 | 0.62 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3320 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

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
| `object` | offset from object initial position (0.5444299044764102, -0.025581934909493356, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
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

## Current Skill (Q=-0.018) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
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
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
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
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.018
- **task_score** (E): 0.468
- **fitness_score**: 0.322  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1490 |
| descend_1 | 1.00 | 1.00 | 0.1155 |
| contact_1 | 1.00 | 1.00 | 0.0421 |
| push_1 | 0.00 | 0.67 | 0.0003 |
| retract_1 | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.018, 0.160) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.514, 0.018, 0.160)→(0.514, 0.019, 0.044) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | push | 1.00 / step_budget | (0.514, 0.019, 0.044)→(0.514, -0.016, 0.022) | (0.518, -0.020, 0.025)→(0.525, -0.053, 0.025) | 0.139→0.111 | 1.00 / 3.000 | 8.675 | 15.978 |
| push_1 | push | 0.00 / guard_failure | (0.515, -0.049, 0.019)→(0.515, -0.050, 0.019) | (0.525, -0.053, 0.025)→(0.531, -0.085, 0.025) | 0.111→0.078 | 0.67 / 1.333 | 6.574 | 33.749 |
| retract_1 | retract | 1.00 / step_budget | (0.515, -0.050, 0.019)→(0.512, -0.050, 0.107) | (0.531, -0.086, 0.025)→(0.530, -0.091, 0.025) | 0.077→0.071 | 1.00 / 4.000 | 0.245 | 2.342 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.742
- lateral_force_integral: None
- approach_alignment: 0.637
- goal_progress: 0.742
- terminal_score: 0.742
- phase_score: 0.465
- phase_breakdown.reach_contact_score: 0.114
- phase_breakdown.push_to_goal_score: 0.615

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.576
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.742
- **Median Q (composite search score)**: -0.114
- **K-run variance**: 0.0327
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.248


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18713,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12621,"approach_1.speed":0.04313,"push_1.force_threshold":20.20195,"push_1.push_distance":0.20038,"push_1.push_speed":0.01015},"optimized_scores":{"best_composite_score":-0.11382,"best_fitness_score":0.22618,"best_task_score":0.3828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.55875,-0.08481,-6e-05],"force_p95":12.44592,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.80484,"mean_force":4.17742,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5371,-0.02589,0.02023]},{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.54495,-0.03848,0.04809],"force_p95":15.99729,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.7295,"mean_force":5.19195,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53655,-0.02674,0.02004]},{"body_a":"attachment","body_b":"push_box","contact_count":415.0,"contact_point_centroid":[0.54317,-0.0173,0.04819],"force_p95":13.48158,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.69301,"mean_force":7.64583,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.53813,-0.0054,0.02946]},{"body_a":"world","body_b":"push_box","contact_count":982.0,"contact_point_centroid":[0.54824,-0.05525,-4e-05],"force_p95":6.89151,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.80508,"mean_force":3.59265,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.53794,-0.00162,0.03171]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.56959,-0.04085,0.05194],"force_p95":3.00103,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.19056,"mean_force":1.03863,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53327,-0.03275,0.01912]},{"body_a":"world","body_b":"push_box","contact_count":2133.0,"contact_point_centroid":[0.54496,-0.08196,-2e-05],"force_p95":0.2464,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02518,"mean_force":0.25619,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52726,-0.03813,0.06248]},{"body_a":"world","body_b":"push_box","contact_count":2176.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51753,0.00639,0.22907]},{"body_a":"world","body_b":"push_box","contact_count":872.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53795,0.01351,0.10227]}],"total_contact_groups":8},"final_pose_error":0.0125,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54496,-0.08198,0.02499],"final_tcp_position":[0.52742,-0.03804,0.10663],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":20.80484,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53763,0.01309,0.15824],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":840.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53962,0.014,0.04422],"tcp_start":[0.53763,0.01309,0.15824],"tcp_to_object_dist_end":0.04427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.55086,-0.05763,0.02546],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.10545,"object_to_goal_dist_start":0.13211,"object_z_max":0.02554,"peak_contact_force":8.46339,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1397.0,"raw_peak_contact_force":15.69301,"subtask_id":"reach_contact","tcp_end":[0.53999,-0.02151,0.0214],"tcp_start":[0.53962,0.014,0.04422],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":43.0,"n_steps_budget":1000.0,"object_pos_end":[0.54913,-0.07205,0.02569],"object_pos_start":[0.55086,-0.05763,0.02546],"object_to_goal_dist_end":0.09214,"object_to_goal_dist_start":0.10545,"object_z_max":0.0263,"peak_contact_force":1.49853,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":75.0,"raw_peak_contact_force":20.80484,"subtask_id":"push_to_goal","tcp_end":[0.53099,-0.0382,0.0186],"tcp_start":[0.53104,-0.03783,0.01866],"tcp_to_object_dist_end":0.03906,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":630.0,"object_pos_end":[0.54496,-0.08198,0.02499],"object_pos_start":[0.54889,-0.07329,0.02565],"object_to_goal_dist_end":0.08154,"object_to_goal_dist_start":0.09097,"object_z_max":0.02565,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2133.0,"raw_peak_contact_force":2.02518,"tcp_end":[0.52742,-0.03804,0.10663],"tcp_start":[0.53099,-0.0382,0.0186],"tcp_to_object_dist_end":0.09436,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19186,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13687,"approach_1.speed":0.03998,"push_1.force_threshold":19.46862,"push_1.push_distance":0.1303,"push_1.push_speed":0.0385},"optimized_scores":{"best_composite_score":-0.17482,"best_fitness_score":0.16518,"best_task_score":0.27901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.58103,-0.04752,0.05154],"force_p95":58.48067,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.08152,"mean_force":18.34473,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54352,-0.04043,0.01897]},{"body_a":"world","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.56909,-0.09383,-6e-05],"force_p95":22.52937,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.34568,"mean_force":6.73503,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5476,-0.0342,0.02008]},{"body_a":"attachment","body_b":"push_box","contact_count":410.0,"contact_point_centroid":[0.55317,-0.02669,0.04792],"force_p95":13.28522,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.6423,"mean_force":7.00563,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54826,-0.01477,0.02924]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.55423,-0.04589,0.0429],"force_p95":13.38053,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.85867,"mean_force":3.95893,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54764,-0.03399,0.02005]},{"body_a":"world","body_b":"push_box","contact_count":984.0,"contact_point_centroid":[0.5589,-0.06386,-4e-05],"force_p95":6.88828,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.8061,"mean_force":3.27746,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54805,-0.01079,0.03161]},{"body_a":"world","body_b":"push_box","contact_count":2164.0,"contact_point_centroid":[0.55986,-0.08038,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.48782,"mean_force":0.2529,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53901,-0.04219,0.06184]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.58049,-0.04896,0.05115],"force_p95":2.15278,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.228,"mean_force":1.48431,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54267,-0.0425,0.01874]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.55247,-0.0545,0.05092],"force_p95":1.75346,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.85909,"mean_force":0.83392,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54249,-0.04275,0.0187]},{"body_a":"world","body_b":"push_box","contact_count":2128.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52211,0.00215,0.23395]},{"body_a":"world","body_b":"push_box","contact_count":940.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54767,0.00454,0.10721]}],"total_contact_groups":10},"final_pose_error":0.01274,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55978,-0.08037,0.02499],"final_tcp_position":[0.53914,-0.04209,0.10659],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":64.08152,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.547,0.00442,0.16815],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":900.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":940.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.54975,0.00471,0.04425],"tcp_start":[0.547,0.00442,0.16815],"tcp_to_object_dist_end":0.04449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.56206,-0.0672,0.02526],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.10348,"object_to_goal_dist_start":0.12728,"object_z_max":0.02547,"peak_contact_force":8.9552,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1394.0,"raw_peak_contact_force":14.6423,"subtask_id":"reach_contact","tcp_end":[0.5501,-0.0311,0.02108],"tcp_start":[0.54975,0.00471,0.04425],"tcp_to_object_dist_end":0.03826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.56053,-0.07654,0.02559],"object_pos_start":[0.56206,-0.0672,0.02526],"object_to_goal_dist_end":0.09519,"object_to_goal_dist_start":0.10348,"object_z_max":0.02607,"peak_contact_force":18.22248,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":65.0,"raw_peak_contact_force":64.08152,"subtask_id":"push_to_goal","tcp_end":[0.54277,-0.04228,0.0188],"tcp_start":[0.54281,-0.04196,0.01884],"tcp_to_object_dist_end":0.03919,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":630.0,"object_pos_end":[0.55978,-0.08037,0.02499],"object_pos_start":[0.56067,-0.07729,0.02551],"object_to_goal_dist_end":0.09177,"object_to_goal_dist_start":0.0947,"object_z_max":0.02552,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2171.0,"raw_peak_contact_force":3.48782,"tcp_end":[0.53914,-0.04209,0.10659],"tcp_start":[0.54277,-0.04228,0.0188],"tcp_to_object_dist_end":0.09246,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30556,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11869,"approach_1.speed":0.06964,"push_1.force_threshold":15.33398,"push_1.push_distance":0.16958,"push_1.push_speed":0.0355},"optimized_scores":{"best_composite_score":0.23559,"best_fitness_score":0.57559,"best_task_score":0.74159},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":420.0,"contact_point_centroid":[0.45535,0.00765,0.04761],"force_p95":14.5775,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.59885,"mean_force":7.71556,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.4508,0.01952,0.03105]},{"body_a":"attachment","body_b":"push_box","contact_count":107.0,"contact_point_centroid":[0.46408,-0.03978,0.03375],"force_p95":7.17563,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.36079,"mean_force":2.18833,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45995,-0.02795,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":103.0,"contact_point_centroid":[0.47396,-0.08833,-8e-05],"force_p95":7.74832,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.10541,"mean_force":2.91844,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46101,-0.03131,0.02051]},{"body_a":"world","body_b":"push_box","contact_count":952.0,"contact_point_centroid":[0.45944,-0.03139,-5e-05],"force_p95":7.27954,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.74583,"mean_force":3.76299,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.4508,0.02281,0.03294]},{"body_a":"world","body_b":"push_box","contact_count":2131.0,"contact_point_centroid":[0.48626,-0.11211,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51175,"mean_force":0.25163,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46859,-0.06844,0.06441]},{"body_a":"world","body_b":"push_box","contact_count":2040.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47793,0.01764,0.22682]},{"body_a":"world","body_b":"push_box","contact_count":872.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45401,0.03757,0.09959]}],"total_contact_groups":7},"final_pose_error":0.0114,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48617,-0.11203,0.02499],"final_tcp_position":[0.46866,-0.06837,0.10856],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":17.59885,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45638,0.03629,0.15296],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":810.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.45276,0.03899,0.04443],"tcp_start":[0.45638,0.03629,0.15296],"tcp_to_object_dist_end":0.04372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":502.0,"n_steps_budget":600.0,"object_pos_end":[0.46063,-0.03271,0.02543],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.12372,"object_to_goal_dist_start":0.1564,"object_z_max":0.02552,"peak_contact_force":8.60561,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1372.0,"raw_peak_contact_force":17.59885,"subtask_id":"reach_contact","tcp_end":[0.45169,0.00351,0.02292],"tcp_start":[0.45276,0.03899,0.04443],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.48382,-0.10522,0.02501],"object_pos_start":[0.46063,-0.03271,0.02543],"object_to_goal_dist_end":0.04761,"object_to_goal_dist_start":0.12372,"object_z_max":0.02632,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":210.0,"raw_peak_contact_force":16.36079,"subtask_id":"push_to_goal","tcp_end":[0.4719,-0.06875,0.01948],"tcp_start":[0.47197,-0.06846,0.01952],"tcp_to_object_dist_end":0.03877,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.48617,-0.11203,0.02499],"object_pos_start":[0.48409,-0.1062,0.02524],"object_to_goal_dist_end":0.04042,"object_to_goal_dist_start":0.0466,"object_z_max":0.02536,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2131.0,"raw_peak_contact_force":1.51175,"tcp_end":[0.46866,-0.06837,0.10856],"tcp_start":[0.4719,-0.06875,0.01948],"tcp_to_object_dist_end":0.0959,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```