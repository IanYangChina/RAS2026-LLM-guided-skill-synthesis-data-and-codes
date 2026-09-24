## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6677 | 0.80 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0840 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1613 | 0.32 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6844 | 0.80 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2047 | 0.05 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.813, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.668) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.668
- **task_score** (E): 0.798
- **fitness_score**: 0.755  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2785 |
| contact_1 | 0.67 | 1.00 | 0.0438 |
| push_1 | 1.00 | 1.00 | 0.1331 |
| retract_1 | 0.00 | 1.00 | 0.1483 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.061, 0.033) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.513, 0.061, 0.033)→(0.513, 0.019, 0.022) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.667 | 13.825 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.513, 0.019, 0.022)→(0.503, -0.109, 0.026) | (0.518, -0.020, 0.025)→(0.520, -0.140, 0.029) | 0.139→0.030 | 1.00 / 4.000 | 78.566 | 96.721 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.109, 0.026)→(0.497, 0.027, 0.086) | (0.520, -0.140, 0.029)→(0.516, -0.136, 0.025) | 0.030→0.027 | 1.00 / 4.000 | 0.245 | 57.684 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.813
- lateral_force_integral: None
- approach_alignment: 0.437
- goal_progress: 0.749
- terminal_score: 0.749
- phase_score: 0.746
- phase_breakdown.contact_score: 0.757
- phase_breakdown.push_score: 0.709
- phase_breakdown.approach_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.783
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.920
- **Median Q (composite search score)**: 0.760
- **K-run variance**: 0.0190
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.353


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76101,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09482,"contact_1.speed":0.04087,"push_1.push_speed":0.08341,"retract_1.retract_height":0.09363,"retract_1.speed":0.08325},"optimized_scores":{"best_composite_score":0.77017,"best_fitness_score":0.74684,"best_task_score":0.7487},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":967.0,"contact_point_centroid":[0.55392,-0.06481,0.05425],"force_p95":109.14679,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.88959,"mean_force":69.86833,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52165,-0.04862,0.02326]},{"body_a":"attachment","body_b":"push_box","contact_count":988.0,"contact_point_centroid":[0.54006,-0.05639,0.05212],"force_p95":90.51314,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.70957,"mean_force":48.10009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52198,-0.04737,0.02319]},{"body_a":"push_box","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.5482,-0.11787,0.05615],"force_p95":80.65373,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.14524,"mean_force":31.92214,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50701,-0.1056,0.0297]},{"body_a":"world","body_b":"push_box","contact_count":1923.0,"contact_point_centroid":[0.54738,-0.09796,-0.0003],"force_p95":74.03786,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.40637,"mean_force":45.06439,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52179,-0.04842,0.02334]},{"body_a":"world","body_b":"push_box","contact_count":3632.0,"contact_point_centroid":[0.52833,-0.13157,-3e-05],"force_p95":0.37797,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.93255,"mean_force":0.55208,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5018,-0.03212,0.0601]},{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.53059,-0.1085,0.06033],"force_p95":60.36065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.50385,"mean_force":21.15071,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50647,-0.10319,0.0302]},{"body_a":"world","body_b":"push_box","contact_count":3720.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51729,0.04386,0.17039]},{"body_a":"world","body_b":"push_box","contact_count":2640.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53647,0.0329,0.02417]}],"total_contact_groups":8},"final_pose_error":0.13608,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52766,-0.13163,0.02499],"final_tcp_position":[0.50005,0.02859,0.08853],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":129.88959,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53811,0.05607,0.03239],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":660.0,"n_steps_budget":900.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":22.17596,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53855,0.01137,0.02095],"tcp_start":[0.53811,0.05607,0.03239],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.53462,-0.13894,0.03117],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03687,"object_to_goal_dist_start":0.13211,"object_z_max":0.03116,"peak_contact_force":108.99699,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3878.0,"raw_peak_contact_force":129.88959,"tcp_end":[0.5081,-0.11024,0.0286],"tcp_start":[0.53855,0.01137,0.02095],"tcp_to_object_dist_end":0.03916,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52766,-0.13163,0.02499],"object_pos_start":[0.53462,-0.13894,0.03117],"object_to_goal_dist_end":0.0332,"object_to_goal_dist_start":0.03687,"object_z_max":0.03509,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3760.0,"raw_peak_contact_force":90.14524,"tcp_end":[0.50005,0.02859,0.08853],"tcp_start":[0.5081,-0.11024,0.0286],"tcp_to_object_dist_end":0.17456,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68023,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0863,"contact_1.speed":0.02975,"push_1.push_speed":0.08236,"retract_1.retract_height":0.08416,"retract_1.speed":0.07289},"optimized_scores":{"best_composite_score":0.75983,"best_fitness_score":0.7365,"best_task_score":0.72435},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":966.0,"contact_point_centroid":[0.56096,-0.07007,0.05389],"force_p95":110.12511,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.21553,"mean_force":70.05733,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52717,-0.05357,0.02327]},{"body_a":"world","body_b":"push_box","contact_count":1975.0,"contact_point_centroid":[0.55352,-0.10148,-0.00031],"force_p95":76.65435,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.52383,"mean_force":43.32586,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52773,-0.05216,0.02321]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.53089,-0.1321,-3e-05],"force_p95":0.28308,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.48506,"mean_force":0.53177,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50256,-0.03437,0.05956]},{"body_a":"push_box","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.5496,-0.11726,0.05627],"force_p95":71.02039,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.06223,"mean_force":28.82312,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50798,-0.10662,0.02992]},{"body_a":"attachment","body_b":"push_box","contact_count":987.0,"contact_point_centroid":[0.54625,-0.06149,0.05443],"force_p95":73.73861,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.9714,"mean_force":43.18797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5276,-0.05241,0.02319]},{"body_a":"attachment","body_b":"push_box","contact_count":69.0,"contact_point_centroid":[0.53174,-0.10915,0.06051],"force_p95":50.13958,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.18702,"mean_force":17.71199,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50739,-0.10404,0.03042]},{"body_a":"world","body_b":"push_box","contact_count":3752.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52219,0.03965,0.16907]},{"body_a":"world","body_b":"push_box","contact_count":3540.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54639,0.02344,0.02349]}],"total_contact_groups":8},"final_pose_error":0.13927,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53021,-0.13216,0.02499],"final_tcp_position":[0.50061,0.02557,0.08745],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":130.21553,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04702,0.03174],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":19.0544,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3540.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54871,0.00191,0.02061],"tcp_start":[0.54794,0.04702,0.03174],"tcp_to_object_dist_end":0.03773,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.53705,-0.13872,0.03097],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.03918,"object_to_goal_dist_start":0.12728,"object_z_max":0.03097,"peak_contact_force":110.70215,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3928.0,"raw_peak_contact_force":130.21553,"tcp_end":[0.50911,-0.11089,0.02904],"tcp_start":[0.54871,0.00191,0.02061],"tcp_to_object_dist_end":0.03949,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53021,-0.13216,0.02499],"object_pos_start":[0.53705,-0.13872,0.03097],"object_to_goal_dist_end":0.03509,"object_to_goal_dist_start":0.03918,"object_z_max":0.03482,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3768.0,"raw_peak_contact_force":80.48506,"tcp_end":[0.50061,0.02557,0.08745],"tcp_start":[0.50911,-0.11089,0.02904],"tcp_to_object_dist_end":0.17221,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51111,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19547,"contact_1.speed":0.02042,"push_1.push_speed":0.09675,"retract_1.retract_height":0.15536,"retract_1.speed":0.07395},"optimized_scores":{"best_composite_score":0.47306,"best_fitness_score":0.78306,"best_task_score":0.92008},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":837.0,"contact_point_centroid":[0.47107,-0.04515,0.02313],"force_p95":16.18921,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.05756,"mean_force":4.24007,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46938,-0.03324,0.02021]},{"body_a":"world","body_b":"push_box","contact_count":1928.0,"contact_point_centroid":[0.46959,-0.06769,-5e-05],"force_p95":7.04583,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.38096,"mean_force":2.17755,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46761,-0.02638,0.02046]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.48102,0.01369,0.05009],"force_p95":12.06041,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.71058,"mean_force":4.38654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45159,0.02956,0.02081]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49004,-0.11758,0.02038],"force_p95":2.34905,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.42128,"mean_force":1.69895,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49061,-0.10564,0.02006]},{"body_a":"world","body_b":"push_box","contact_count":3974.0,"contact_point_centroid":[0.48894,-0.14419,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60118,"mean_force":0.24696,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48927,-0.03768,0.04994]},{"body_a":"world","body_b":"push_box","contact_count":3640.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47735,0.05545,0.17352]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45054,0.05973,0.02712]}],"total_contact_groups":7},"final_pose_error":0.14223,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48894,-0.14417,0.02499],"final_tcp_position":[0.49167,0.02538,0.08197],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":30.05756,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3640.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.45384,0.08031,0.03462],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45082,0.04313,0.02406],"tcp_start":[0.45384,0.08031,0.03462],"tcp_to_object_dist_end":0.04347,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48929,-0.14245,0.02493],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.0131,"object_to_goal_dist_start":0.1564,"object_z_max":0.02534,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2809.0,"raw_peak_contact_force":30.05756,"tcp_end":[0.49061,-0.10559,0.02007],"tcp_start":[0.45082,0.04313,0.02406],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48894,-0.14417,0.02499],"object_pos_start":[0.48929,-0.14245,0.02493],"object_to_goal_dist_end":0.0125,"object_to_goal_dist_start":0.0131,"object_z_max":0.02518,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3976.0,"raw_peak_contact_force":2.42128,"tcp_end":[0.49167,0.02538,0.08197],"tcp_start":[0.49061,-0.10559,0.02007],"tcp_to_object_dist_end":0.17889,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```