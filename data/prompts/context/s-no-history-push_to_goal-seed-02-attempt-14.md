## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.728, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.368) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach
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
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend
  type: descend
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
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.3
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 1.0
      - 4.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.368
- **task_score** (E): 0.728
- **fitness_score**: 0.648  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1258 |
| descend | 1.00 | 1.00 | 0.1390 |
| push | 1.00 | 0.67 | 0.1786 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.016, 0.187) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.488, 0.016, 0.187)→(0.485, 0.019, 0.048) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 3.667 | 24.095 | 43.404 |
| push | push | 1.00 / time_limit | (0.485, 0.019, 0.048)→(0.495, -0.149, 0.032) | (0.492, -0.018, 0.025)→(0.520, -0.170, 0.030) | 0.139→0.038 | 0.67 / 1.667 | 13.536 | 79.344 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.720
- goal_progress: 0.738
- terminal_score: 0.738
- phase_score: 0.601
- phase_breakdown.push_goal_score: 0.837
- phase_breakdown.reach_object_score: 0.051

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.656
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.751
- **Median Q (composite search score)**: 0.369
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.430


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90816,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_z_offset":0.1484,"descend.descend_z":0.0002,"push.push_distance":0.18287,"push.push_max_time":3.63962,"push.push_speed":0.11015},"optimized_scores":{"best_composite_score":0.36854,"best_fitness_score":0.64854,"best_task_score":0.69593},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":749.0,"contact_point_centroid":[0.48653,-0.07928,0.04813],"force_p95":32.76761,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.7516,"mean_force":10.12645,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47581,-0.06786,0.03575]},{"body_a":"world","body_b":"push_box","contact_count":1326.0,"contact_point_centroid":[0.493,-0.10836,-0.0001],"force_p95":17.72071,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.87942,"mean_force":6.39223,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47318,-0.05621,0.03664]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.52317,-0.12795,0.05814],"force_p95":20.74921,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.3243,"mean_force":6.86423,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48812,-0.12044,0.03222]},{"body_a":"world","body_b":"push_box","contact_count":868.0,"contact_point_centroid":[0.47139,-0.02418,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48392,0.0057,0.24783]},{"body_a":"world","body_b":"push_box","contact_count":1160.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.46285,0.0131,0.11923]}],"total_contact_groups":5},"final_pose_error":0.18124,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50983,-0.18786,0.02799],"final_tcp_position":[0.49586,-0.15275,0.03009],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":63.7516,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":840.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":868.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.46717,0.01201,0.19241],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1160.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45988,0.01426,0.04489],"tcp_start":[0.46717,0.01201,0.19241],"tcp_to_object_dist_end":0.04479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50983,-0.18786,0.02799],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.03923,"object_to_goal_dist_start":0.12903,"object_z_max":0.02975,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2109.0,"raw_peak_contact_force":63.7516,"subtask_id":"push_goal","tcp_end":[0.49586,-0.15275,0.03009],"tcp_start":[0.45988,0.01426,0.04489],"tcp_to_object_dist_end":0.03785,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_z_offset":0.1264,"descend.descend_z":0.00379,"push.push_distance":0.17814,"push.push_max_time":1.38304,"push.push_speed":0.10615},"optimized_scores":{"best_composite_score":0.37582,"best_fitness_score":0.65582,"best_task_score":0.73839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1323.0,"contact_point_centroid":[0.48383,-0.11663,-8e-05],"force_p95":14.91134,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.34943,"mean_force":5.3828,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45938,-0.06408,0.0393]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.43397,-0.00672,0.04986],"force_p95":58.19188,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.55541,"mean_force":47.6996,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.43308,0.0051,0.0504]},{"body_a":"attachment","body_b":"push_box","contact_count":716.0,"contact_point_centroid":[0.47373,-0.08403,0.04975],"force_p95":24.14868,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.7288,"mean_force":7.83816,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46297,-0.07258,0.03853]},{"body_a":"push_box","body_b":"link7","contact_count":121.0,"contact_point_centroid":[0.52127,-0.13432,0.05774],"force_p95":18.11476,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.16837,"mean_force":8.10561,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48416,-0.12193,0.03438]},{"body_a":"world","body_b":"push_box","contact_count":965.0,"contact_point_centroid":[0.45025,-0.03166,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.77052,"mean_force":0.49261,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4369,0.00474,0.10979]},{"body_a":"world","body_b":"push_box","contact_count":1088.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47167,0.00213,0.2361]}],"total_contact_groups":6},"final_pose_error":0.1821,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51083,-0.18145,0.02977],"final_tcp_position":[0.49583,-0.14765,0.03253],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":59.34943,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.44213,0.00446,0.16947],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":242.0,"n_steps_budget":900.0,"object_pos_end":[0.45017,-0.03185,0.02503],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12823,"object_to_goal_dist_start":0.12843,"object_z_max":0.02501,"peak_contact_force":0.62937,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":970.0,"raw_peak_contact_force":58.55541,"tcp_end":[0.43302,0.00526,0.04854],"tcp_start":[0.44213,0.00446,0.16947],"tcp_to_object_dist_end":0.04716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51083,-0.18145,0.02977],"object_pos_start":[0.45017,-0.03185,0.02503],"object_to_goal_dist_end":0.0336,"object_to_goal_dist_start":0.12823,"object_z_max":0.03038,"peak_contact_force":33.48746,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2160.0,"raw_peak_contact_force":59.34943,"subtask_id":"push_goal","tcp_end":[0.49583,-0.14765,0.03253],"tcp_start":[0.43302,0.00526,0.04854],"tcp_to_object_dist_end":0.03708,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_z_offset":0.15959,"descend.descend_z":0.00627,"push.push_distance":0.25885,"push.push_max_time":3.45226,"push.push_speed":0.12424},"optimized_scores":{"best_composite_score":0.35843,"best_fitness_score":0.63843,"best_task_score":0.75076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":703.0,"contact_point_centroid":[0.53295,-0.06316,0.05037],"force_p95":21.78344,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.93118,"mean_force":7.77634,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52614,-0.05245,0.04003]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56393,0.0263,0.04993],"force_p95":71.41034,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.41034,"mean_force":71.41034,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.56081,0.03778,0.05086]},{"body_a":"world","body_b":"push_box","contact_count":1449.0,"contact_point_centroid":[0.54658,-0.09292,-8e-05],"force_p95":12.38396,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.45053,"mean_force":4.26592,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52707,-0.04984,0.04023]},{"body_a":"world","body_b":"push_box","contact_count":1112.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.57291,"mean_force":0.30969,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.55617,0.03505,0.12479]},{"body_a":"world","body_b":"push_box","contact_count":1000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52537,0.01564,0.24977]}],"total_contact_groups":5},"final_pose_error":0.25893,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53842,-0.14057,0.03082],"final_tcp_position":[0.49354,-0.14793,0.03446],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":114.93118,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":870.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.55336,0.0325,0.19805],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02498],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":71.41034,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1113.0,"raw_peak_contact_force":71.41034,"tcp_end":[0.56085,0.03781,0.05037],"tcp_start":[0.55336,0.0325,0.19805],"tcp_to_object_dist_end":0.04508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53842,-0.14057,0.03082],"object_pos_start":[0.55317,0.00136,0.02498],"object_to_goal_dist_end":0.03998,"object_to_goal_dist_start":0.16043,"object_z_max":0.03081,"peak_contact_force":7.12023,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2152.0,"raw_peak_contact_force":114.93118,"subtask_id":"push_goal","tcp_end":[0.49354,-0.14793,0.03446],"tcp_start":[0.56085,0.03781,0.05037],"tcp_to_object_dist_end":0.04563,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```