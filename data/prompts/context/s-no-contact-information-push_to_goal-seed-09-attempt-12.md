## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.3102 | 0.58 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.0070 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.5517 | 0.46 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.5589 | 0.47 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.4973 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.310) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_object
  anchor: object
  offset:
  - 0.0
  - 0.06
  - 0.0
  weight: 0.3
- id: move_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_side
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.06
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset:
      type: scalar
      range:
      - 0.04
      - 0.08
      default: 0.06
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: contact_object
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.005
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_height_offset:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: move_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_side** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.06, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset: status=consumed; consumers=target.offset.y (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.005], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_height_offset: status=consumed; consumers=target.offset.z (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force, when=during_phase, predicate=force_below, on_failure=retry, threshold=20.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.310
- **task_score** (E): 0.579
- **fitness_score**: 0.610  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_side | 1.00 | 0.2745 |
| push | 1.00 | 0.1425 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.029, 0.032) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 |
| push | push | 1.00 / time_limit | (0.513, 0.029, 0.032)→(0.492, -0.108, 0.027) | (0.518, -0.020, 0.025)→(0.520, -0.101, 0.025) | 0.139→0.057 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.769
- approach_alignment: 0.625
- goal_progress: 0.768
- terminal_score: 0.768
- phase_score: 0.743
- phase_breakdown.move_to_goal_score: 0.768

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.753
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.768
- **Median Q (composite search score)**: 0.263
- **K-run variance**: 0.0106
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.410


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37681,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.17954,"approach_side.lateral_offset":0.05496,"push.push_distance":0.21563,"push.push_duration":5.45294,"push.push_height_offset":0.00544,"push.push_speed":0.09736},"optimized_scores":{"best_composite_score":0.26334,"best_fitness_score":0.56334,"best_task_score":0.50855},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":722.0,"contact_point_centroid":[0.52624,-0.06021,0.04965],"force_p95":12.06025,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.00164,"mean_force":3.11703,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51329,-0.05296,0.02548]},{"body_a":"world","body_b":"push_box","contact_count":1837.0,"contact_point_centroid":[0.55697,-0.06599,-3e-05],"force_p95":6.98055,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.16925,"mean_force":1.65633,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51687,-0.04056,0.02587]},{"body_a":"world","body_b":"push_box","contact_count":3804.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.51786,0.0136,0.16706]}],"total_contact_groups":3},"final_pose_error":0.10621,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53267,-0.09389,0.02465],"final_tcp_position":[0.49454,-0.125,0.02552],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"phases":[{"n_steps":951.0,"n_steps_budget":990.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"contact_object","tcp_end":[0.53848,0.02793,0.03045],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05412,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53267,-0.09389,0.02465],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06493,"object_to_goal_dist_start":0.13211,"object_z_max":0.02954,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"move_to_goal","tcp_end":[0.49454,-0.125,0.02552],"tcp_start":[0.53848,0.02793,0.03045],"tcp_to_object_dist_end":0.04922,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.39437,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.16782,"approach_side.lateral_offset":0.05124,"push.push_distance":0.17171,"push.push_duration":5.48016,"push.push_height_offset":0.00433,"push.push_speed":0.08686},"optimized_scores":{"best_composite_score":0.21417,"best_fitness_score":0.51417,"best_task_score":0.45947},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":737.0,"contact_point_centroid":[0.53322,-0.06424,0.05118],"force_p95":11.19438,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.46762,"mean_force":3.27902,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52038,-0.05637,0.02576]},{"body_a":"world","body_b":"push_box","contact_count":1841.0,"contact_point_centroid":[0.56623,-0.07239,-3e-05],"force_p95":7.69736,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.72205,"mean_force":1.74993,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52478,-0.044,0.02627]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.52254,0.00742,0.16743]}],"total_contact_groups":3},"final_pose_error":0.07336,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54048,-0.09437,0.02481],"final_tcp_position":[0.49969,-0.11933,0.02512],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"contact_object","tcp_end":[0.5481,0.01523,0.03167],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05118,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54048,-0.09437,0.02481],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.0688,"object_to_goal_dist_start":0.12728,"object_z_max":0.02943,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"move_to_goal","tcp_end":[0.49969,-0.11933,0.02512],"tcp_start":[0.5481,0.01523,0.03167],"tcp_to_object_dist_end":0.04782,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.34328,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.1895,"approach_side.lateral_offset":0.04483,"push.push_distance":0.20834,"push.push_duration":6.86941,"push.push_height_offset":0.00888,"push.push_speed":0.0775},"optimized_scores":{"best_composite_score":0.45296,"best_fitness_score":0.75296,"best_task_score":0.76835},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":808.0,"contact_point_centroid":[0.46906,-0.03245,0.04078],"force_p95":14.69852,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.11237,"mean_force":4.2854,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46615,-0.02053,0.02901]},{"body_a":"world","body_b":"push_box","contact_count":1618.0,"contact_point_centroid":[0.46829,-0.06001,-5e-05],"force_p95":7.14865,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.65877,"mean_force":2.49901,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46353,-0.00919,0.02927]},{"body_a":"world","body_b":"push_box","contact_count":3568.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.47658,0.02065,0.16837]}],"total_contact_groups":3},"final_pose_error":0.12505,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48739,-0.11603,0.02511],"final_tcp_position":[0.48097,-0.0795,0.02889],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"phases":[{"n_steps":892.0,"n_steps_budget":930.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"contact_object","tcp_end":[0.45373,0.04251,0.03263],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04331,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48739,-0.11603,0.02511],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.03623,"object_to_goal_dist_start":0.1564,"object_z_max":0.02542,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"move_to_goal","tcp_end":[0.48097,-0.0795,0.02889],"tcp_start":[0.45373,0.04251,0.03263],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```