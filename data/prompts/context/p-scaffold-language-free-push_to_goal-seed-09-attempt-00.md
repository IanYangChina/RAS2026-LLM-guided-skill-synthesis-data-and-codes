## Search State

- **Seed**: 9
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6768 | 0.81 | ✅ accepted |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.677) — your mutation base

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

- **Composite score**: 0.677
- **task_score** (E): 0.813
- **fitness_score**: 0.765  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2785 |
| contact_1 | 0.67 | 1.00 | 0.0431 |
| push_1 | 1.00 | 1.00 | 0.1350 |
| retract_1 | 0.00 | 1.00 | 0.1518 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.061, 0.033) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.513, 0.061, 0.033)→(0.513, 0.019, 0.022) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.667 | 14.761 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.513, 0.019, 0.022)→(0.503, -0.110, 0.026) | (0.518, -0.020, 0.025)→(0.523, -0.141, 0.029) | 0.139→0.027 | 1.00 / 3.000 | 73.664 | 95.630 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.110, 0.026)→(0.498, 0.029, 0.087) | (0.523, -0.141, 0.029)→(0.518, -0.137, 0.025) | 0.027→0.024 | 1.00 / 4.000 | 0.245 | 56.133 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.808
- lateral_force_integral: None
- approach_alignment: 0.442
- goal_progress: 0.745
- terminal_score: 0.745
- phase_score: 0.746
- phase_breakdown.contact_score: 0.757
- phase_breakdown.push_score: 0.709
- phase_breakdown.approach_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.815
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.971
- **Median Q (composite search score)**: 0.757
- **K-run variance**: 0.0149
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.528


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7546,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.192,"contact_1.speed":0.0392,"push_1.push_speed":0.08645,"retract_1.retract_height":0.16393,"retract_1.speed":0.07451},"optimized_scores":{"best_composite_score":0.76865,"best_fitness_score":0.74531,"best_task_score":0.74502},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":937.0,"contact_point_centroid":[0.55392,-0.06482,0.05425],"force_p95":109.01837,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.25296,"mean_force":69.59612,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52166,-0.04856,0.02325]},{"body_a":"attachment","body_b":"push_box","contact_count":957.0,"contact_point_centroid":[0.54026,-0.05631,0.05243],"force_p95":89.57634,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.18263,"mean_force":48.40171,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.522,-0.04733,0.02319]},{"body_a":"world","body_b":"push_box","contact_count":1852.0,"contact_point_centroid":[0.54739,-0.09793,-0.0003],"force_p95":75.56975,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.23072,"mean_force":45.27242,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52177,-0.04858,0.02336]},{"body_a":"push_box","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.5486,-0.11743,0.05617],"force_p95":71.18368,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.19716,"mean_force":30.70276,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50729,-0.10607,0.02975]},{"body_a":"world","body_b":"push_box","contact_count":3652.0,"contact_point_centroid":[0.52846,-0.13128,-3e-05],"force_p95":0.29093,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.84103,"mean_force":0.5343,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50207,-0.03385,0.05951]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.52978,-0.10792,0.05929],"force_p95":51.77445,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.52111,"mean_force":17.10103,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50645,-0.10227,0.03054]},{"body_a":"world","body_b":"push_box","contact_count":3720.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51729,0.04386,0.17039]},{"body_a":"world","body_b":"push_box","contact_count":2712.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53648,0.03275,0.02414]}],"total_contact_groups":8},"final_pose_error":0.13846,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52779,-0.13097,0.02499],"final_tcp_position":[0.50024,0.02638,0.08764],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":126.25296,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53811,0.05607,0.03239],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":678.0,"n_steps_budget":930.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":23.91292,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2712.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53854,0.01139,0.02095],"tcp_start":[0.53811,0.05607,0.03239],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.53521,-0.13928,0.03115],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03731,"object_to_goal_dist_start":0.13211,"object_z_max":0.03116,"peak_contact_force":108.72293,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3746.0,"raw_peak_contact_force":126.25296,"tcp_end":[0.50842,-0.11047,0.02881],"tcp_start":[0.53854,0.01139,0.02095],"tcp_to_object_dist_end":0.03942,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52779,-0.13097,0.02499],"object_pos_start":[0.53521,-0.13928,0.03115],"object_to_goal_dist_end":0.03369,"object_to_goal_dist_start":0.03731,"object_z_max":0.03495,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3790.0,"raw_peak_contact_force":80.19716,"tcp_end":[0.50024,0.02638,0.08764],"tcp_start":[0.50842,-0.11047,0.02881],"tcp_to_object_dist_end":0.17159,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76471,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06288,"contact_1.speed":0.04147,"push_1.push_speed":0.08595,"retract_1.retract_height":0.08694,"retract_1.speed":0.0965},"optimized_scores":{"best_composite_score":0.75732,"best_fitness_score":0.73399,"best_task_score":0.72401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":908.0,"contact_point_centroid":[0.56109,-0.06931,0.05388],"force_p95":111.15756,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.95529,"mean_force":70.64918,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52727,-0.05329,0.02327]},{"body_a":"world","body_b":"push_box","contact_count":1860.0,"contact_point_centroid":[0.55337,-0.10085,-0.0003],"force_p95":78.97165,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.25229,"mean_force":43.6911,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52784,-0.05182,0.02319]},{"body_a":"push_box","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.54947,-0.11676,0.05641],"force_p95":73.37704,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.3289,"mean_force":27.1091,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5081,-0.10583,0.02998]},{"body_a":"attachment","body_b":"push_box","contact_count":926.0,"contact_point_centroid":[0.54598,-0.06134,0.05397],"force_p95":75.69742,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.88399,"mean_force":43.52428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52766,-0.05223,0.0232]},{"body_a":"world","body_b":"push_box","contact_count":3673.0,"contact_point_centroid":[0.53055,-0.1317,-3e-05],"force_p95":0.27106,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.92938,"mean_force":0.49203,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50253,-0.02832,0.06221]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.53128,-0.10847,0.05973],"force_p95":48.19188,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.17557,"mean_force":17.17637,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50752,-0.10321,0.03054]},{"body_a":"world","body_b":"push_box","contact_count":3752.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52219,0.03965,0.16907]},{"body_a":"world","body_b":"push_box","contact_count":2596.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54642,0.02396,0.02365]}],"total_contact_groups":8},"final_pose_error":0.12544,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52987,-0.13152,0.02499],"final_tcp_position":[0.50031,0.03815,0.09322],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":130.95529,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54794,0.04702,0.03174],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":649.0,"n_steps_budget":870.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":20.12425,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2596.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54871,0.00188,0.0206],"tcp_start":[0.54794,0.04702,0.03174],"tcp_to_object_dist_end":0.0377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.53723,-0.13799,0.03099],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.03957,"object_to_goal_dist_start":0.12728,"object_z_max":0.03098,"peak_contact_force":111.83463,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3694.0,"raw_peak_contact_force":130.95529,"tcp_end":[0.50932,-0.11032,0.02906],"tcp_start":[0.54871,0.00188,0.0206],"tcp_to_object_dist_end":0.03934,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52987,-0.13152,0.02499],"object_pos_start":[0.53723,-0.13799,0.03099],"object_to_goal_dist_end":0.03513,"object_to_goal_dist_start":0.03957,"object_z_max":0.03486,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3790.0,"raw_peak_contact_force":87.3289,"tcp_end":[0.50031,0.03815,0.09322],"tcp_start":[0.50932,-0.11032,0.02906],"tcp_to_object_dist_end":0.18524,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48352,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.082,"contact_1.speed":0.01897,"push_1.push_speed":0.09999,"retract_1.retract_height":0.16883,"retract_1.speed":0.07079},"optimized_scores":{"best_composite_score":0.50453,"best_fitness_score":0.81453,"best_task_score":0.97139},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":865.0,"contact_point_centroid":[0.47539,-0.04809,0.02883],"force_p95":15.50202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.68231,"mean_force":4.1433,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47054,-0.03621,0.02039]},{"body_a":"world","body_b":"push_box","contact_count":1794.0,"contact_point_centroid":[0.4717,-0.06969,-4e-05],"force_p95":8.09098,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.24843,"mean_force":2.39696,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46787,-0.02604,0.0207]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.48323,0.00479,0.05012],"force_p95":13.87409,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.80102,"mean_force":5.22,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45332,0.02493,0.02102]},{"body_a":"world","body_b":"push_box","contact_count":3990.0,"contact_point_centroid":[0.49602,-0.14793,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87435,"mean_force":0.24619,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49014,-0.04199,0.04925]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49185,-0.12155,0.02014],"force_p95":0.41862,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43594,"mean_force":0.26267,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49184,-0.10958,0.02009]},{"body_a":"world","body_b":"push_box","contact_count":3640.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47735,0.05545,0.17352]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45051,0.06079,0.02731]}],"total_contact_groups":7},"final_pose_error":0.1463,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49602,-0.14795,0.02499],"final_tcp_position":[0.49219,0.02129,0.08088],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":29.68231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3640.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.45384,0.08031,0.03462],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45076,0.04521,0.02443],"tcp_start":[0.45384,0.08031,0.03462],"tcp_to_object_dist_end":0.04554,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49579,-0.14641,0.02513],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.00553,"object_to_goal_dist_start":0.1564,"object_z_max":0.02527,"peak_contact_force":0.43436,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2703.0,"raw_peak_contact_force":29.68231,"tcp_end":[0.49185,-0.10952,0.0201],"tcp_start":[0.45076,0.04521,0.02443],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,-0.14795,0.02499],"object_pos_start":[0.49579,-0.14641,0.02513],"object_to_goal_dist_end":0.00448,"object_to_goal_dist_start":0.00553,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3992.0,"raw_peak_contact_force":0.87435,"tcp_end":[0.49219,0.02129,0.08088],"tcp_start":[0.49185,-0.10952,0.0201],"tcp_to_object_dist_end":0.17827,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```