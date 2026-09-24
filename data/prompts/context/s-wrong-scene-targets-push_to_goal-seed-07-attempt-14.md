## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5826 | 0.84 | ✅ accepted |
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.4282 | 0.75 | ❌ rejected |
| 12 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5431 | 0.79 | ❌ rejected |
| 11 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5556 | 0.81 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5609 | 0.81 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.51501145599256, 0.047665656116349056, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.51501145599256, 0.047665656116349056, 0.025]
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.841, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.583) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
phases:
- id: approach_behind
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_pre_contact
- id: push_to_goal_phase
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.583
- **task_score** (E): 0.841
- **fitness_score**: 0.763  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2814 |
| push_to_goal_phase | 1.00 | 1.00 | 0.1631 |
| retract_1 | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.074, 0.033) | (0.513, 0.027, 0.025)→(0.513, 0.026, 0.025) | 0.180→0.179 | 1.00 / 4.000 | 0.295 | 154.313 |
| push_to_goal_phase | push | 1.00 / time_limit | (0.517, 0.074, 0.033)→(0.498, -0.086, 0.024) | (0.513, 0.026, 0.025)→(0.502, -0.122, 0.026) | 0.179→0.032 | 1.00 / 2.667 | 2.763 | 29.183 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.086, 0.024)→(0.494, -0.085, 0.065) | (0.502, -0.122, 0.026)→(0.502, -0.123, 0.025) | 0.032→0.031 | 1.00 / 4.000 | 0.245 | 1.501 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.708
- goal_progress: 0.952
- terminal_score: 0.952
- phase_score: 0.786
- phase_breakdown.reach_pre_contact_score: 0.211
- phase_breakdown.push_to_goal_score: 0.959

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.853
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.952
- **Median Q (composite search score)**: 0.549
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.338


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.04254,"push_to_goal_phase.push_distance":0.03022,"push_to_goal_phase.push_time":4.55006},"optimized_scores":{"best_composite_score":0.54929,"best_fitness_score":0.72929,"best_task_score":0.79621},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.52267,0.0737,0.04793],"force_p95":190.03535,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":225.79488,"mean_force":131.55164,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51508,0.08148,0.04996]},{"body_a":"world","body_b":"push_box","contact_count":3611.0,"contact_point_centroid":[0.51513,0.04812,-3e-05],"force_p95":0.38955,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.86737,"mean_force":2.30436,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50574,0.04168,0.1679]},{"body_a":"attachment","body_b":"push_box","contact_count":785.0,"contact_point_centroid":[0.51454,-0.00731,0.04214],"force_p95":17.89737,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.94567,"mean_force":5.24596,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.5062,0.00446,0.02638]},{"body_a":"world","body_b":"push_box","contact_count":1337.0,"contact_point_centroid":[0.51491,-0.04047,-6e-05],"force_p95":11.35329,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.58542,"mean_force":3.86224,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50717,0.01464,0.02705]},{"body_a":"push_box","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.535,-0.07204,0.0536],"force_p95":20.24994,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.11939,"mean_force":7.19153,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50221,-0.05669,0.02447]},{"body_a":"world","body_b":"push_box","contact_count":1301.0,"contact_point_centroid":[0.51066,-0.11923,-2e-05],"force_p95":0.46327,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18265,"mean_force":0.31559,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49708,-0.07483,0.04796]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53242,-0.09391,0.05347],"force_p95":1.5272,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.68064,"mean_force":0.98605,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5008,-0.07538,0.02372]},{"body_a":"attachment","body_b":"push_box","contact_count":173.0,"contact_point_centroid":[0.5086,-0.08651,0.05131],"force_p95":0.63777,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.48678,"mean_force":0.50556,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49751,-0.07492,0.03509]}],"total_contact_groups":8},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50863,-0.11053,0.02499],"final_tcp_position":[0.49698,-0.07479,0.06464],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":225.79488,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.51429,0.04492,0.02457],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19545,"object_to_goal_dist_start":0.19823,"object_z_max":0.02565,"peak_contact_force":0.37366,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3667.0,"raw_peak_contact_force":225.79488,"subtask_id":"reach_pre_contact","tcp_end":[0.51575,0.08658,0.03387],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51078,-0.11115,0.02729],"object_pos_start":[0.51429,0.04492,0.02457],"object_to_goal_dist_end":0.04038,"object_to_goal_dist_start":0.19545,"object_z_max":0.02797,"peak_contact_force":3.5467,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2195.0,"raw_peak_contact_force":26.94567,"subtask_id":"push_to_goal","tcp_end":[0.5009,-0.07518,0.02376],"tcp_start":[0.51575,0.08658,0.03387],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.50863,-0.11053,0.02499],"object_pos_start":[0.51078,-0.11115,0.02729],"object_to_goal_dist_end":0.0404,"object_to_goal_dist_start":0.04038,"object_z_max":0.02736,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1479.0,"raw_peak_contact_force":2.18265,"tcp_end":[0.49698,-0.07479,0.06464],"tcp_start":[0.5009,-0.07518,0.02376],"tcp_to_object_dist_end":0.05464,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.04211,"push_to_goal_phase.push_distance":0.06683,"push_to_goal_phase.push_time":2.11627},"optimized_scores":{"best_composite_score":0.52577,"best_fitness_score":0.70577,"best_task_score":0.77372},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":76.0,"contact_point_centroid":[0.48541,0.08529,0.04741],"force_p95":211.9388,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":236.89898,"mean_force":147.7922,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47736,0.09173,0.05014]},{"body_a":"world","body_b":"push_box","contact_count":3620.0,"contact_point_centroid":[0.4793,0.05922,-4e-05],"force_p95":0.42373,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.45034,"mean_force":3.36488,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48571,0.04702,0.16687]},{"body_a":"attachment","body_b":"push_box","contact_count":817.0,"contact_point_centroid":[0.48953,0.00493,0.0431],"force_p95":20.16483,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.17013,"mean_force":5.80264,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.47953,0.01658,0.02757]},{"body_a":"world","body_b":"push_box","contact_count":1272.0,"contact_point_centroid":[0.49308,-0.02933,-7e-05],"force_p95":11.5261,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.29705,"mean_force":4.41125,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.4788,0.02611,0.0281]},{"body_a":"push_box","body_b":"link7","contact_count":130.0,"contact_point_centroid":[0.51701,-0.0207,0.05368],"force_p95":13.4124,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.76552,"mean_force":2.90541,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.482,-0.00937,0.02666]},{"body_a":"world","body_b":"push_box","contact_count":1645.0,"contact_point_centroid":[0.50008,-0.10269,-2e-05],"force_p95":0.24795,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48225,"mean_force":0.25116,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48361,-0.06352,0.04563]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52362,-0.08739,0.05116],"force_p95":0.68669,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68669,"mean_force":0.68669,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48698,-0.06413,0.02473]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50176,-0.07576,0.0516],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48725,-0.06375,0.0248]}],"total_contact_groups":8},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50016,-0.10259,0.02499],"final_tcp_position":[0.4834,-0.06343,0.06561],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":236.89898,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.48009,0.05786,0.02472],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.20881,"object_to_goal_dist_start":0.2095,"object_z_max":0.0252,"peak_contact_force":0.2665,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3696.0,"raw_peak_contact_force":236.89898,"subtask_id":"reach_pre_contact","tcp_end":[0.47535,0.09721,0.03421],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49931,-0.10021,0.02592],"object_pos_start":[0.48009,0.05786,0.02472],"object_to_goal_dist_end":0.04981,"object_to_goal_dist_start":0.20881,"object_z_max":0.02755,"peak_contact_force":3.42403,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2219.0,"raw_peak_contact_force":33.17013,"subtask_id":"push_to_goal","tcp_end":[0.48725,-0.06375,0.0248],"tcp_start":[0.47535,0.09721,0.03421],"tcp_to_object_dist_end":0.03842,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":600.0,"object_pos_end":[0.50016,-0.10259,0.02499],"object_pos_start":[0.49931,-0.10021,0.02592],"object_to_goal_dist_end":0.04741,"object_to_goal_dist_start":0.04981,"object_z_max":0.02593,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1647.0,"raw_peak_contact_force":1.48225,"tcp_end":[0.4834,-0.06343,0.06561],"tcp_start":[0.48725,-0.06375,0.0248],"tcp_to_object_dist_end":0.05886,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.06865,"push_to_goal_phase.push_distance":0.07766,"push_to_goal_phase.push_time":1.88266},"optimized_scores":{"best_composite_score":0.6727,"best_fitness_score":0.8527,"best_task_score":0.95208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":557.0,"contact_point_centroid":[0.52627,-0.06049,0.02453],"force_p95":22.09148,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.43438,"mean_force":5.52718,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.52731,-0.04866,0.02389]},{"body_a":"world","body_b":"push_box","contact_count":2387.0,"contact_point_centroid":[0.52732,-0.07301,-0.00012],"force_p95":6.2395,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.7736,"mean_force":1.56407,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53322,-0.03175,0.02459]},{"body_a":"world","body_b":"push_box","contact_count":1841.0,"contact_point_centroid":[0.4959,-0.15495,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83947,"mean_force":0.24829,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50061,-0.11727,0.04302]},{"body_a":"world","body_b":"push_box","contact_count":3716.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52907,0.01839,0.16464]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50232,-0.12969,0.02333],"force_p95":0.09627,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10134,"mean_force":0.05067,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50432,-0.1179,0.02242]}],"total_contact_groups":5},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49596,-0.15487,0.02499],"final_tcp_position":[0.50042,-0.11716,0.06328],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":27.43438,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3716.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.56014,0.03696,0.03134],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49623,-0.15386,0.02507],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.00539,"object_to_goal_dist_start":0.13211,"object_z_max":0.0258,"peak_contact_force":1.31849,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2944.0,"raw_peak_contact_force":27.43438,"subtask_id":"push_to_goal","tcp_end":[0.50435,-0.11783,0.02243],"tcp_start":[0.56014,0.03696,0.03134],"tcp_to_object_dist_end":0.03702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.49596,-0.15487,0.02499],"object_pos_start":[0.49623,-0.15386,0.02507],"object_to_goal_dist_end":0.00633,"object_to_goal_dist_start":0.00539,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1843.0,"raw_peak_contact_force":0.83947,"tcp_end":[0.50042,-0.11716,0.06328],"tcp_start":[0.50435,-0.11783,0.02243],"tcp_to_object_dist_end":0.05393,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```