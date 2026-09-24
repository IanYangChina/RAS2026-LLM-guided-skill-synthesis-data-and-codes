## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2582 | 0.37 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.3187 | 0.00 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0487 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0111 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.5366 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.258) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
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
    entity: push_box
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
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
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
  subtask_id: reach_goal
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.258
- **task_score** (E): 0.366
- **fitness_score**: 0.568  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1835 |
| descend_1 | 1.00 | 1.00 | 0.0825 |
| push_1 | 1.00 | 1.00 | 0.1418 |
| retract_1 | 1.00 | 1.00 | 0.0846 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.001, 0.125) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.521, -0.001, 0.125)→(0.539, -0.001, 0.045) | (0.526, -0.001, 0.025)→(0.531, -0.001, 0.024) | 0.156→0.157 | 1.00 / 3.667 | 231.228 | 244.947 |
| push_1 | push | 1.00 / step_budget | (0.539, -0.001, 0.045)→(0.503, -0.131, 0.023) | (0.531, -0.001, 0.024)→(0.533, -0.056, 0.025) | 0.157→0.101 | 1.00 / 4.000 | 0.268 | 159.285 |
| retract_1 | retract | 1.00 / step_budget | (0.503, -0.131, 0.023)→(0.500, -0.131, 0.108) | (0.533, -0.056, 0.025)→(0.533, -0.056, 0.025) | 0.101→0.101 | 1.00 / 4.000 | 0.245 | 0.263 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.410
- lateral_force_integral: None
- approach_alignment: 0.755
- goal_progress: 0.402
- terminal_score: 0.402
- phase_score: 0.701
- phase_breakdown.push_to_goal_score: 0.675
- phase_breakdown.reach_pre_contact_score: 0.858
- phase_breakdown.descend_to_box_score: 0.624

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.581
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.402
- **Median Q (composite search score)**: 0.265
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.451


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05556,"average_solve_count":270.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09214,"approach_1.speed":0.05472,"descend_1.speed":0.08125,"push_1.push_speed":0.01014,"retract_1.speed":0.03967},"optimized_scores":{"best_composite_score":0.23771,"best_fitness_score":0.54771,"best_task_score":0.30714},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":129.0,"contact_point_centroid":[0.49541,0.05781,0.04649],"force_p95":264.08335,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":264.45278,"mean_force":226.40288,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48354,0.05793,0.04667]},{"body_a":"attachment","body_b":"push_box","contact_count":294.0,"contact_point_centroid":[0.50741,0.03554,0.04652],"force_p95":155.0188,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":158.76224,"mean_force":130.23957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49992,0.02697,0.04615]},{"body_a":"world","body_b":"push_box","contact_count":1220.0,"contact_point_centroid":[0.51812,0.0102,-0.00045],"force_p95":147.71488,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.11523,"mean_force":31.96774,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49644,-0.04777,0.0332]},{"body_a":"world","body_b":"push_box","contact_count":1446.0,"contact_point_centroid":[0.48055,0.0586,-0.00018],"force_p95":125.83122,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.43306,"mean_force":20.54188,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47783,0.05603,0.0755]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48808,0.02646,0.21281]},{"body_a":"world","body_b":"push_box","contact_count":3844.0,"contact_point_centroid":[0.52385,-0.00682,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49228,-0.13008,0.06689]}],"total_contact_groups":6},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52385,-0.00682,0.02499],"final_tcp_position":[0.49243,-0.13004,0.11253],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":264.45278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.47759,0.05397,0.12577],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":374.0,"n_steps_budget":780.0,"object_pos_end":[0.48452,0.05916,0.02448],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20973,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":241.07228,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1575.0,"raw_peak_contact_force":264.45278,"subtask_id":"descend_to_box","tcp_end":[0.49327,0.05929,0.04455],"tcp_start":[0.47759,0.05397,0.12577],"tcp_to_object_dist_end":0.0219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.52385,-0.00682,0.02499],"object_pos_start":[0.48452,0.05916,0.02448],"object_to_goal_dist_end":0.14516,"object_to_goal_dist_start":0.20973,"object_z_max":0.04238,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1514.0,"raw_peak_contact_force":158.76224,"subtask_id":"push_to_goal","tcp_end":[0.49576,-0.13082,0.02185],"tcp_start":[0.49327,0.05929,0.04455],"tcp_to_object_dist_end":0.12718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.52385,-0.00682,0.02499],"object_pos_start":[0.52385,-0.00682,0.02499],"object_to_goal_dist_end":0.14516,"object_to_goal_dist_start":0.14516,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3844.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49243,-0.13004,0.11253],"tcp_start":[0.49576,-0.13082,0.02185],"tcp_to_object_dist_end":0.15439,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76577,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09125,"approach_1.speed":0.09517,"descend_1.speed":0.05615,"push_1.push_speed":0.04905,"retract_1.speed":0.01979},"optimized_scores":{"best_composite_score":0.26542,"best_fitness_score":0.57542,"best_task_score":0.38908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":181.0,"contact_point_centroid":[0.56087,-0.02544,0.0467],"force_p95":233.25936,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":233.81817,"mean_force":204.15701,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54901,-0.02554,0.04699]},{"body_a":"attachment","body_b":"push_box","contact_count":353.0,"contact_point_centroid":[0.55884,-0.04968,0.04707],"force_p95":159.27078,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":160.26947,"mean_force":133.65227,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55013,-0.05627,0.04692]},{"body_a":"world","body_b":"push_box","contact_count":1656.0,"contact_point_centroid":[0.54568,-0.0257,-0.00021],"force_p95":112.04003,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.26716,"mean_force":22.67112,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54196,-0.02482,0.0707]},{"body_a":"world","body_b":"push_box","contact_count":999.0,"contact_point_centroid":[0.54554,-0.05467,-0.00059],"force_p95":104.38657,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.14355,"mean_force":47.81894,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54343,-0.0668,0.04309]},{"body_a":"world","body_b":"push_box","contact_count":2424.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51787,-0.01168,0.21159]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53409,-0.07684,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24504,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5024,-0.13031,0.05978]}],"total_contact_groups":6},"final_pose_error":0.02732,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53409,-0.07684,0.02499],"final_tcp_position":[0.50252,-0.13026,0.09693],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":233.81817,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.53797,-0.02376,0.12344],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.54946,-0.02588,0.02397],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13361,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":225.74602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1837.0,"raw_peak_contact_force":233.81817,"subtask_id":"descend_to_box","tcp_end":[0.55822,-0.0261,0.04519],"tcp_start":[0.53797,-0.02376,0.12344],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.53412,-0.07676,0.02447],"object_pos_start":[0.54946,-0.02588,0.02397],"object_to_goal_dist_end":0.0808,"object_to_goal_dist_start":0.13361,"object_z_max":0.03562,"peak_contact_force":0.24592,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1352.0,"raw_peak_contact_force":160.26947,"subtask_id":"push_to_goal","tcp_end":[0.50605,-0.13104,0.02401],"tcp_start":[0.55822,-0.0261,0.04519],"tcp_to_object_dist_end":0.06111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53409,-0.07684,0.02499],"object_pos_start":[0.53412,-0.07676,0.02447],"object_to_goal_dist_end":0.08071,"object_to_goal_dist_start":0.0808,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50252,-0.13026,0.09693],"tcp_start":[0.50605,-0.13104,0.02401],"tcp_to_object_dist_end":0.095,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77695,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09546,"approach_1.speed":0.05124,"descend_1.speed":0.07094,"push_1.push_speed":0.01859,"retract_1.speed":0.04819},"optimized_scores":{"best_composite_score":0.27133,"best_fitness_score":0.58133,"best_task_score":0.40169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.56992,-0.03481,0.04684],"force_p95":236.18416,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":236.57017,"mean_force":204.58756,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55807,-0.03492,0.04722]},{"body_a":"attachment","body_b":"push_box","contact_count":409.0,"contact_point_centroid":[0.56438,-0.05965,0.047],"force_p95":157.76583,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":158.82261,"mean_force":131.04094,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55535,-0.06565,0.04701]},{"body_a":"world","body_b":"push_box","contact_count":1519.0,"contact_point_centroid":[0.55559,-0.03529,-0.00018],"force_p95":110.93316,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.37036,"mean_force":20.1549,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5512,-0.03394,0.0735]},{"body_a":"world","body_b":"push_box","contact_count":1084.0,"contact_point_centroid":[0.55508,-0.0621,-0.00058],"force_p95":92.33623,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.80851,"mean_force":50.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55098,-0.07063,0.0444]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53994,-0.08516,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29906,"mean_force":0.24503,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50441,-0.13131,0.06899]},{"body_a":"world","body_b":"push_box","contact_count":2704.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52257,-0.01606,0.21309]}],"total_contact_groups":6},"final_pose_error":0.01063,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53994,-0.08516,0.02499],"final_tcp_position":[0.50459,-0.13127,0.11442],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":236.57017,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54768,-0.03263,0.12683],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":382.0,"n_steps_budget":900.0,"object_pos_end":[0.55943,-0.03543,0.02384],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12908,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":226.86467,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1666.0,"raw_peak_contact_force":236.57017,"subtask_id":"descend_to_box","tcp_end":[0.56656,-0.0356,0.04538],"tcp_start":[0.54768,-0.03263,0.12683],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.53994,-0.0852,0.0242],"object_pos_start":[0.55943,-0.03543,0.02384],"object_to_goal_dist_end":0.07613,"object_to_goal_dist_start":0.12908,"object_z_max":0.03537,"peak_contact_force":0.31386,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1493.0,"raw_peak_contact_force":158.82261,"subtask_id":"push_to_goal","tcp_end":[0.508,-0.13202,0.02447],"tcp_start":[0.56656,-0.0356,0.04538],"tcp_to_object_dist_end":0.05668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53994,-0.08516,0.02499],"object_pos_start":[0.53994,-0.0852,0.0242],"object_to_goal_dist_end":0.07616,"object_to_goal_dist_start":0.07613,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.29906,"tcp_end":[0.50459,-0.13127,0.11442],"tcp_start":[0.508,-0.13202,0.02447],"tcp_to_object_dist_end":0.10665,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```