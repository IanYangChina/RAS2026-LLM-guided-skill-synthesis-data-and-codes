## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1783 | 0.40 | ✅ accepted |
| 2 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |
| 1 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.3700 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5444299044764102, -0.025581934909493356, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5444299044764102, -0.025581934909493356, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.178) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
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
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
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
    orientation:
      mode: none
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: push
  type: push
  generator: linear_cartesian
  control: admittance_control
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
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract
  type: retract
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
    - 0.2
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=task_goal_direction, distance=0.0, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **retract** (`retract`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.2]
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.178
- **task_score** (E): 0.401
- **fitness_score**: 0.488  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1338 |
| descend | 1.00 | 1.00 | 0.1297 |
| push | 1.00 | 1.00 | 0.2034 |
| retract | 0.00 | 1.00 | 0.1627 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.018, 0.176) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.514, -0.018, 0.176)→(0.529, -0.020, 0.047) | (0.518, -0.020, 0.025)→(0.522, -0.020, 0.024) | 0.139→0.139 | 1.00 / 4.667 | 247.163 | 270.243 |
| push | push | 1.00 / time_limit | (0.529, -0.020, 0.047)→(0.502, -0.209, 0.030) | (0.522, -0.020, 0.024)→(0.524, -0.073, 0.025) | 0.139→0.083 | 1.00 / 4.000 | 0.245 | 153.440 |
| retract | retract | 0.00 / step_budget | (0.502, -0.209, 0.030)→(0.518, -0.120, 0.159) | (0.524, -0.073, 0.025)→(0.524, -0.073, 0.025) | 0.083→0.083 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.451
- lateral_force_integral: None
- approach_alignment: 0.765
- goal_progress: 0.441
- terminal_score: 0.441
- phase_score: 0.561
- phase_breakdown.push_to_goal_score: 0.448
- phase_breakdown.approach_object_score: 0.827

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.513
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.441
- **Median Q (composite search score)**: 0.167
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.259


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04918,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.14113,"approach.approach_speed":0.17207,"descend.descend_speed":0.10837,"push.push_distance":0.16572,"push.push_speed":0.099},"optimized_scores":{"best_composite_score":0.16457,"best_fitness_score":0.47457,"best_task_score":0.38761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":113.0,"contact_point_centroid":[0.55808,-0.02528,0.04685],"force_p95":250.13357,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":254.71655,"mean_force":213.74933,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54666,-0.02543,0.04886]},{"body_a":"attachment","body_b":"push_box","contact_count":506.0,"contact_point_centroid":[0.55254,-0.05579,0.04669],"force_p95":132.9363,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.85298,"mean_force":94.67543,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54365,-0.06145,0.04794]},{"body_a":"world","body_b":"push_box","contact_count":1889.0,"contact_point_centroid":[0.54486,-0.02565,-0.00011],"force_p95":114.08261,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.72002,"mean_force":13.10568,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53927,-0.0244,0.098]},{"body_a":"world","body_b":"push_box","contact_count":2947.0,"contact_point_centroid":[0.53809,-0.06391,-0.00018],"force_p95":81.4033,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.8757,"mean_force":16.60964,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51961,-0.10755,0.03908]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.55766,-0.07585,0.06769],"force_p95":3.54174,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.60235,"mean_force":2.99628,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52287,-0.09782,0.03825]},{"body_a":"world","body_b":"push_box","contact_count":1672.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5176,-0.01134,0.23639]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53208,-0.07573,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50206,-0.1356,0.09969]}],"total_contact_groups":7},"final_pose_error":0.06032,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53208,-0.07573,0.02499],"final_tcp_position":[0.51834,-0.09956,0.17131],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":254.71655,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.53745,-0.02324,0.1727],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":870.0,"object_pos_end":[0.54865,-0.02581,0.02379],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13338,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":236.84353,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2002.0,"raw_peak_contact_force":254.71655,"tcp_end":[0.55478,-0.0259,0.04686],"tcp_start":[0.53745,-0.02324,0.1727],"tcp_to_object_dist_end":0.02388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53208,-0.07573,0.02499],"object_pos_start":[0.54865,-0.02581,0.02379],"object_to_goal_dist_end":0.0809,"object_to_goal_dist_start":0.13338,"object_z_max":0.0354,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3455.0,"raw_peak_contact_force":142.85298,"subtask_id":"push_to_goal","tcp_end":[0.48911,-0.17349,0.03077],"tcp_start":[0.55478,-0.0259,0.04686],"tcp_to_object_dist_end":0.10695,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53208,-0.07573,0.02499],"object_pos_start":[0.53208,-0.07573,0.02499],"object_to_goal_dist_end":0.0809,"object_to_goal_dist_start":0.0809,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51834,-0.09956,0.17131],"tcp_start":[0.48911,-0.17349,0.03077],"tcp_to_object_dist_end":0.14889,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55472,-0.03508,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18584,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.1491,"approach.approach_speed":0.18414,"descend.descend_speed":0.1966,"push.push_distance":0.26181,"push.push_speed":0.0973},"optimized_scores":{"best_composite_score":0.20334,"best_fitness_score":0.51334,"best_task_score":0.44145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.56646,-0.03449,0.0471],"force_p95":258.36394,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":268.06315,"mean_force":215.19282,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.55497,-0.03472,0.04895]},{"body_a":"attachment","body_b":"push_box","contact_count":521.0,"contact_point_centroid":[0.55644,-0.06479,0.0476],"force_p95":126.2003,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.78185,"mean_force":92.12199,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54721,-0.07038,0.04853]},{"body_a":"world","body_b":"push_box","contact_count":1677.0,"contact_point_centroid":[0.55519,-0.03514,-8e-05],"force_p95":100.82613,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.76855,"mean_force":9.92398,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54826,-0.03332,0.10514]},{"body_a":"world","body_b":"push_box","contact_count":2863.0,"contact_point_centroid":[0.54527,-0.07518,-0.00018],"force_p95":68.52078,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.25397,"mean_force":17.16222,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52044,-0.11273,0.04094]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.55695,-0.09128,0.06737],"force_p95":3.73699,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.47678,"mean_force":3.14798,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52023,-0.1104,0.03869]},{"body_a":"world","body_b":"push_box","contact_count":1724.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52227,-0.01561,0.23959]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53821,-0.09005,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5016,-0.14226,0.10316]}],"total_contact_groups":7},"final_pose_error":0.05572,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53821,-0.09005,0.02499],"final_tcp_position":[0.52258,-0.1096,0.17521],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":268.06315,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1724.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54696,-0.03192,0.17953],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":424.0,"n_steps_budget":600.0,"object_pos_end":[0.55843,-0.03534,0.02375],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.1287,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":243.65336,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1752.0,"raw_peak_contact_force":268.06315,"tcp_end":[0.56195,-0.03525,0.04677],"tcp_start":[0.54696,-0.03192,0.17953],"tcp_to_object_dist_end":0.02329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53821,-0.09005,0.02499],"object_pos_start":[0.55843,-0.03534,0.02375],"object_to_goal_dist_end":0.07109,"object_to_goal_dist_start":0.1287,"object_z_max":0.03525,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3417.0,"raw_peak_contact_force":139.78185,"subtask_id":"push_to_goal","tcp_end":[0.48378,-0.17672,0.03374],"tcp_start":[0.56195,-0.03525,0.04677],"tcp_to_object_dist_end":0.10272,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53821,-0.09005,0.02499],"object_pos_start":[0.53821,-0.09005,0.02499],"object_to_goal_dist_end":0.07109,"object_to_goal_dist_start":0.07109,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.52258,-0.1096,0.17521],"tcp_start":[0.48378,-0.17672,0.03374],"tcp_to_object_dist_end":0.15229,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45543,-9e-05,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86335,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_offset_z":0.14098,"approach.approach_speed":0.06611,"descend.descend_speed":0.06933,"push.push_distance":0.20586,"push.push_speed":0.181},"optimized_scores":{"best_composite_score":0.16713,"best_fitness_score":0.47713,"best_task_score":0.373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":178.0,"contact_point_centroid":[0.4722,-0.00014,0.04599],"force_p95":279.02757,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":287.94863,"mean_force":246.92406,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.46172,-0.00017,0.0497]},{"body_a":"attachment","body_b":"push_box","contact_count":289.0,"contact_point_centroid":[0.49069,-0.02549,0.04591],"force_p95":161.46003,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.6852,"mean_force":96.02102,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48279,-0.03129,0.04883]},{"body_a":"world","body_b":"push_box","contact_count":2340.0,"contact_point_centroid":[0.45617,-0.00013,-0.00018],"force_p95":128.20271,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.17798,"mean_force":19.10042,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45593,-0.00016,0.09647]},{"body_a":"world","body_b":"push_box","contact_count":3106.0,"contact_point_centroid":[0.49994,-0.04639,-0.00012],"force_p95":101.80418,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.05514,"mean_force":9.26943,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50601,-0.1597,0.03386]},{"body_a":"world","body_b":"push_box","contact_count":1672.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47858,-6e-05,0.23856]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50223,-0.05196,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52081,-0.2138,0.07476]}],"total_contact_groups":6},"final_pose_error":0.13874,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50223,-0.05196,0.02499],"final_tcp_position":[0.5127,-0.15231,0.12976],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":287.94863,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.45722,-0.00012,0.17561],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.45983,-0.0001,0.02365],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1552,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":260.99185,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2518.0,"raw_peak_contact_force":287.94863,"tcp_end":[0.47072,-0.00018,0.048],"tcp_start":[0.45722,-0.00012,0.17561],"tcp_to_object_dist_end":0.02667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50223,-0.05196,0.02499],"object_pos_start":[0.45983,-0.0001,0.02365],"object_to_goal_dist_end":0.09806,"object_to_goal_dist_start":0.1552,"object_z_max":0.03528,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3395.0,"raw_peak_contact_force":177.6852,"subtask_id":"push_to_goal","tcp_end":[0.53301,-0.27808,0.02437],"tcp_start":[0.47072,-0.00018,0.048],"tcp_to_object_dist_end":0.2282,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50223,-0.05196,0.02499],"object_pos_start":[0.50223,-0.05196,0.02499],"object_to_goal_dist_end":0.09806,"object_to_goal_dist_start":0.09806,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.5127,-0.15231,0.12976],"tcp_start":[0.53301,-0.27808,0.02437],"tcp_to_object_dist_end":0.14545,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```