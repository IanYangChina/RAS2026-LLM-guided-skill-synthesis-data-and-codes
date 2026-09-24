## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4703 | 0.84 | ✅ accepted |
| 8 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3787 | 0.72 | ✅ accepted |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0546 | 0.01 | ❌ rejected |
| 6 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3488 | 0.67 | ✅ accepted |
| 5 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0177 | 0.47 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.840, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.470) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
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
    offset:
    - 0.0
    - 0.0
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
    - 0.0
    - 0.02
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_contact
- id: contact_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
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
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **contact_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.470
- **task_score** (E): 0.840
- **fitness_score**: 0.810  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1641 |
| descend_1 | 1.00 | 1.00 | 0.1028 |
| contact_1 | 1.00 | 1.00 | 0.0293 |
| push_1 | 1.00 | 1.00 | 0.1378 |
| retract_1 | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.019, 0.145) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.513, -0.019, 0.145)→(0.521, 0.018, 0.051) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | push | 1.00 / step_budget | (0.521, 0.018, 0.051)→(0.517, -0.003, 0.033) | (0.518, -0.020, 0.025)→(0.515, -0.039, 0.025) | 0.139→0.120 | 1.00 / 2.000 | 0.442 | 64.746 |
| push_1 | push | 1.00 / step_budget | (0.517, -0.003, 0.033)→(0.499, -0.131, 0.021) | (0.515, -0.039, 0.025)→(0.500, -0.166, 0.025) | 0.120→0.019 | 1.00 / 2.333 | 7.151 | 45.376 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.131, 0.021)→(0.496, -0.131, 0.109) | (0.500, -0.166, 0.025)→(0.499, -0.169, 0.025) | 0.019→0.022 | 1.00 / 4.000 | 0.245 | 7.617 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.764
- goal_progress: 0.868
- terminal_score: 0.868
- phase_score: 0.804
- phase_breakdown.reach_contact_score: 0.672
- phase_breakdown.push_to_goal_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.829
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: 0.467
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: approach_1.speed
- **Final σ (mean)**: 0.447


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15668,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10835,"approach_1.speed":0.09036,"contact_1.contact_speed":0.03813,"descend_1.behind_distance":0.04701,"push_1.push_speed":0.02858},"optimized_scores":{"best_composite_score":0.46698,"best_fitness_score":0.80698,"best_task_score":0.83555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":25.0,"contact_point_centroid":[0.54885,-0.00839,0.04369],"force_p95":59.66989,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.88173,"mean_force":17.67239,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.549,0.00329,0.04003]},{"body_a":"attachment","body_b":"push_box","contact_count":287.0,"contact_point_centroid":[0.52238,-0.08323,0.03178],"force_p95":33.56145,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.85898,"mean_force":5.4282,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52163,-0.07142,0.02441]},{"body_a":"world","body_b":"push_box","contact_count":172.0,"contact_point_centroid":[0.54251,-0.03206,-0.0001],"force_p95":21.64306,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.63125,"mean_force":2.86936,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.55027,0.00657,0.04298]},{"body_a":"world","body_b":"push_box","contact_count":410.0,"contact_point_centroid":[0.52065,-0.1091,-0.00013],"force_p95":16.47169,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.25098,"mean_force":4.21786,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52298,-0.06734,0.02465]},{"body_a":"world","body_b":"push_box","contact_count":2163.0,"contact_point_centroid":[0.50523,-0.17107,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54592,"mean_force":0.24978,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49865,-0.12998,0.06448]},{"body_a":"world","body_b":"push_box","contact_count":2228.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51776,-0.01156,0.22022]},{"body_a":"world","body_b":"push_box","contact_count":1364.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54439,-0.00542,0.09434]}],"total_contact_groups":7},"final_pose_error":0.01221,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50529,-0.17107,0.02499],"final_tcp_position":[0.49877,-0.12988,0.10924],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":61.88173,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2228.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53783,-0.0236,0.14044],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":690.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.55357,0.01362,0.05029],"tcp_start":[0.53783,-0.0236,0.14044],"tcp_to_object_dist_end":0.04754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":71.0,"n_steps_budget":780.0,"object_pos_end":[0.53945,-0.04355,0.02452],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.11353,"object_to_goal_dist_start":0.13211,"object_z_max":0.02581,"peak_contact_force":0.91647,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":197.0,"raw_peak_contact_force":61.88173,"subtask_id":"reach_contact","tcp_end":[0.54569,-0.00725,0.03213],"tcp_start":[0.55357,0.01362,0.05029],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50542,-0.16773,0.02514],"object_pos_start":[0.53945,-0.04355,0.02452],"object_to_goal_dist_end":0.01854,"object_to_goal_dist_start":0.11353,"object_z_max":0.02621,"peak_contact_force":1.05145,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":697.0,"raw_peak_contact_force":48.85898,"subtask_id":"push_to_goal","tcp_end":[0.50217,-0.13062,0.02094],"tcp_start":[0.54569,-0.00725,0.03213],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.50529,-0.17107,0.02499],"object_pos_start":[0.50542,-0.16773,0.02514],"object_to_goal_dist_end":0.02173,"object_to_goal_dist_start":0.01854,"object_z_max":0.02514,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2163.0,"raw_peak_contact_force":1.54592,"tcp_end":[0.49877,-0.12988,0.10924],"tcp_start":[0.50217,-0.13062,0.02094],"tcp_to_object_dist_end":0.09401,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58228,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15047,"approach_1.speed":0.08846,"contact_1.contact_speed":0.03679,"descend_1.behind_distance":0.04561,"push_1.push_speed":0.06323},"optimized_scores":{"best_composite_score":0.45456,"best_fitness_score":0.79456,"best_task_score":0.81609},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":37.0,"contact_point_centroid":[0.56189,-0.01941,0.04455],"force_p95":66.94331,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.4485,"mean_force":19.37065,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.56185,-0.00772,0.04029]},{"body_a":"attachment","body_b":"push_box","contact_count":182.0,"contact_point_centroid":[0.52784,-0.08242,0.02884],"force_p95":20.02535,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.94434,"mean_force":3.16553,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53069,-0.07125,0.02487]},{"body_a":"world","body_b":"push_box","contact_count":153.0,"contact_point_centroid":[0.55261,-0.04276,-9e-05],"force_p95":30.55624,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.89523,"mean_force":4.95268,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.56392,-0.00351,0.04427]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49824,-0.14123,0.02234],"force_p95":19.86671,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.86671,"mean_force":19.86671,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50419,-0.13094,0.02096]},{"body_a":"world","body_b":"push_box","contact_count":391.0,"contact_point_centroid":[0.52162,-0.10606,-0.00021],"force_p95":6.61373,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.95671,"mean_force":1.92653,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53165,-0.06954,0.02524]},{"body_a":"world","body_b":"push_box","contact_count":2139.0,"contact_point_centroid":[0.48363,-0.16695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.36825,"mean_force":0.2602,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50065,-0.13028,0.06493]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52233,-0.01567,0.2399]},{"body_a":"world","body_b":"push_box","contact_count":1768.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55605,-0.01505,0.1151]}],"total_contact_groups":8},"final_pose_error":0.01225,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48384,-0.16693,0.02499],"final_tcp_position":[0.50078,-0.1302,0.10922],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":77.4485,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":471.0,"n_steps_budget":990.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.547,-0.03193,0.18073],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":900.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1768.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.56769,0.00251,0.05138],"tcp_start":[0.547,-0.03193,0.18073],"tcp_to_object_dist_end":0.04772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":71.0,"n_steps_budget":810.0,"object_pos_end":[0.54995,-0.05355,0.02549],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.10861,"object_to_goal_dist_start":0.12728,"object_z_max":0.02603,"peak_contact_force":0.41061,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":190.0,"raw_peak_contact_force":77.4485,"subtask_id":"reach_contact","tcp_end":[0.55783,-0.01701,0.03266],"tcp_start":[0.56769,0.00251,0.05138],"tcp_to_object_dist_end":0.03807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.48694,-0.16357,0.02469],"object_pos_start":[0.54995,-0.05355,0.02549],"object_to_goal_dist_end":0.01884,"object_to_goal_dist_start":0.10861,"object_z_max":0.0269,"peak_contact_force":20.26374,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":573.0,"raw_peak_contact_force":42.94434,"subtask_id":"push_to_goal","tcp_end":[0.50419,-0.13094,0.02096],"tcp_start":[0.55783,-0.01701,0.03266],"tcp_to_object_dist_end":0.0371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.48384,-0.16693,0.02499],"object_pos_start":[0.48694,-0.16357,0.02469],"object_to_goal_dist_end":0.02341,"object_to_goal_dist_start":0.01884,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2140.0,"raw_peak_contact_force":19.86671,"tcp_end":[0.50078,-0.1302,0.10922],"tcp_start":[0.50419,-0.13094,0.02096],"tcp_to_object_dist_end":0.09344,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09541,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07787,"approach_1.speed":0.02,"contact_1.contact_speed":0.04797,"descend_1.behind_distance":0.04825,"push_1.push_speed":0.03549},"optimized_scores":{"best_composite_score":0.48934,"best_fitness_score":0.82934,"best_task_score":0.86757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.44526,0.01623,0.04797],"force_p95":52.50927,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.90667,"mean_force":24.72597,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.4432,0.02807,0.04166]},{"body_a":"attachment","body_b":"push_box","contact_count":283.0,"contact_point_centroid":[0.47439,-0.07334,0.03941],"force_p95":34.47819,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.32457,"mean_force":6.60638,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46903,-0.06162,0.02523]},{"body_a":"world","body_b":"push_box","contact_count":175.0,"contact_point_centroid":[0.45724,-0.01133,-4e-05],"force_p95":23.32293,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.68744,"mean_force":3.59075,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.44239,0.03085,0.04397]},{"body_a":"world","body_b":"push_box","contact_count":375.0,"contact_point_centroid":[0.48357,-0.10975,-7e-05],"force_p95":19.93573,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.1004,"mean_force":5.67511,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46639,-0.05289,0.02589]},{"body_a":"world","body_b":"push_box","contact_count":2146.0,"contact_point_centroid":[0.508,-0.1695,-2e-05],"force_p95":0.24566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43883,"mean_force":0.25323,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48781,-0.1318,0.06505]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49991,-0.1444,0.05157],"force_p95":0.51412,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51412,"mean_force":0.51412,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49125,-0.1325,0.02098]},{"body_a":"world","body_b":"push_box","contact_count":2584.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47729,-6e-05,0.20664]},{"body_a":"world","body_b":"push_box","contact_count":1028.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44719,0.01869,0.08174]}],"total_contact_groups":8},"final_pose_error":0.012,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50798,-0.16911,0.02499],"final_tcp_position":[0.48791,-0.13174,0.10948],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":54.90667,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":646.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2584.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45546,-0.00012,0.11266],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.44037,0.0389,0.05146],"tcp_start":[0.45546,-0.00012,0.11266],"tcp_to_object_dist_end":0.04947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":81.0,"n_steps_budget":660.0,"object_pos_end":[0.45667,-0.01947,0.02618],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.13754,"object_to_goal_dist_start":0.1564,"object_z_max":0.02612,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":198.0,"raw_peak_contact_force":54.90667,"subtask_id":"reach_contact","tcp_end":[0.4471,0.01618,0.03273],"tcp_start":[0.44037,0.0389,0.05146],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,-0.16792,0.02585],"object_pos_start":[0.45667,-0.01947,0.02618],"object_to_goal_dist_end":0.01923,"object_to_goal_dist_start":0.13754,"object_z_max":0.02735,"peak_contact_force":0.13812,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":658.0,"raw_peak_contact_force":44.32457,"subtask_id":"push_to_goal","tcp_end":[0.49125,-0.1325,0.02098],"tcp_start":[0.4471,0.01618,0.03273],"tcp_to_object_dist_end":0.03904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.50798,-0.16911,0.02499],"object_pos_start":[0.50692,-0.16792,0.02585],"object_to_goal_dist_end":0.02071,"object_to_goal_dist_start":0.01923,"object_z_max":0.02585,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2147.0,"raw_peak_contact_force":1.43883,"tcp_end":[0.48791,-0.13174,0.10948],"tcp_start":[0.49125,-0.1325,0.02098],"tcp_to_object_dist_end":0.09454,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```