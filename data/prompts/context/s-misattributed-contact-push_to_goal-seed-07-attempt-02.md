## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | descend → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0063 | 0.59 | ✅ accepted |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.59 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.006) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_to_goal
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.7
phases:
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
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
    - 0.025
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.3
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_force:
      type: scalar
      range:
      - 10.0
      - 25.0
      default: 20.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    stroke:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
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
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_force: status=consumed; consumers=guards.force_limit.threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=20.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.006
- **task_score** (E): 0.592
- **fitness_score**: 0.416  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_1 | 1.00 | 1.00 | 0.1749 |
| approach_1 | 1.00 | 1.00 | 0.1174 |
| push_1 | 0.00 | 1.00 | 0.1915 |
| retract_1 | 1.00 | 1.00 | 0.0883 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_1 | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.025, 0.133) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 1.00 / step_budget | (0.509, 0.025, 0.133)→(0.516, 0.107, 0.052) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 2.000 | 2.693 | 23.159 |
| push_1 | push | 0.00 / step_budget | (0.516, 0.107, 0.052)→(0.494, -0.080, 0.046) | (0.513, 0.027, 0.025)→(0.525, -0.086, 0.029) | 0.180→0.080 | 1.00 / 4.000 | 0.245 | 4.451 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.080, 0.046)→(0.490, -0.079, 0.135) | (0.525, -0.086, 0.029)→(0.521, -0.085, 0.025) | 0.080→0.079 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.802
- goal_progress: 0.834
- terminal_score: 0.834
- phase_score: 0.593
- phase_breakdown.push_to_goal_score: 0.759
- phase_breakdown.reach_object_score: 0.205

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.689
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.834
- **Median Q (composite search score)**: -0.108
- **K-run variance**: 0.0375
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.373


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
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95868,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.08506,"approach_1.speed":0.13635,"descend_1.speed":0.14268,"push_1.max_force":24.9925,"push_1.speed":0.03481,"push_1.stroke":0.17016,"retract_1.speed":0.1239},"optimized_scores":{"best_composite_score":-0.10826,"best_fitness_score":0.30174,"best_task_score":0.47393},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":544.0,"contact_point_centroid":[0.51271,0.00099,0.05151],"force_p95":17.67235,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.23303,"mean_force":6.61722,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50525,0.00993,0.04664]},{"body_a":"world","body_b":"push_box","contact_count":1853.0,"contact_point_centroid":[0.53194,0.00171,-4e-05],"force_p95":10.39433,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.935,"mean_force":2.3793,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50793,0.04511,0.04712]},{"body_a":"world","body_b":"push_box","contact_count":1901.0,"contact_point_centroid":[0.53459,-0.05123,-3e-05],"force_p95":0.40981,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.94068,"mean_force":0.27509,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49689,-0.0641,0.09275]},{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.51166,-0.06675,0.0566],"force_p95":0.88334,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.32793,"mean_force":0.83831,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49824,-0.06451,0.05081]},{"body_a":"world","body_b":"push_box","contact_count":2120.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5045,0.02146,0.21664]},{"body_a":"world","body_b":"push_box","contact_count":1732.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5125,0.08375,0.09059]}],"total_contact_groups":6},"final_pose_error":0.01223,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53234,-0.05086,0.02499],"final_tcp_position":[0.49703,-0.06407,0.13452],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":24.23303,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":530.0,"n_steps_budget":810.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51075,0.04382,0.13311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":6.38409,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2397.0,"raw_peak_contact_force":24.23303,"subtask_id":"reach_object","tcp_end":[0.51665,0.12401,0.05181],"tcp_start":[0.51075,0.04382,0.13311],"tcp_to_object_dist_end":0.08094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53804,-0.05183,0.02944],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.10538,"object_to_goal_dist_start":0.19823,"object_z_max":0.0297,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1939.0,"raw_peak_contact_force":10.94068,"subtask_id":"push_to_goal","tcp_end":[0.50022,-0.0644,0.04632],"tcp_start":[0.51665,0.12401,0.05181],"tcp_to_object_dist_end":0.04328,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.53234,-0.05086,0.02499],"object_pos_start":[0.53804,-0.05183,0.02944],"object_to_goal_dist_end":0.10429,"object_to_goal_dist_start":0.10538,"object_z_max":0.02944,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2120.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49703,-0.06407,0.13452],"tcp_start":[0.50022,-0.0644,0.04632],"tcp_to_object_dist_end":0.11584,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49438,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.10143,"approach_1.speed":0.19682,"descend_1.speed":0.04364,"push_1.max_force":24.28639,"push_1.speed":0.05594,"push_1.stroke":0.17238,"retract_1.speed":0.13411},"optimized_scores":{"best_composite_score":-0.15182,"best_fitness_score":0.25818,"best_task_score":0.46963},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":495.0,"contact_point_centroid":[0.48222,0.01929,0.05095],"force_p95":18.41352,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.00866,"mean_force":6.83419,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47578,0.02895,0.04738]},{"body_a":"world","body_b":"push_box","contact_count":2002.0,"contact_point_centroid":[0.49486,0.02379,-4e-05],"force_p95":10.59456,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.45561,"mean_force":2.09628,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47088,0.07694,0.04789]},{"body_a":"world","body_b":"push_box","contact_count":1905.0,"contact_point_centroid":[0.51547,-0.04058,-3e-05],"force_p95":0.399,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34255,"mean_force":0.26814,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47967,-0.03791,0.09363]},{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.493,-0.04269,0.05627],"force_p95":0.89044,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.11558,"mean_force":0.60387,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4807,-0.03825,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":2436.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48819,0.02631,0.21686]},{"body_a":"world","body_b":"push_box","contact_count":1852.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47085,0.10186,0.09109]}],"total_contact_groups":6},"final_pose_error":0.01185,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51338,-0.03969,0.02499],"final_tcp_position":[0.47978,-0.03787,0.13546],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":23.00866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47772,0.05378,0.13363],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.744,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2497.0,"raw_peak_contact_force":23.00866,"subtask_id":"reach_object","tcp_end":[0.46631,0.15008,0.05207],"tcp_start":[0.47772,0.05378,0.13363],"tcp_to_object_dist_end":0.09639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51859,-0.04165,0.02949],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.11002,"object_to_goal_dist_start":0.2095,"object_z_max":0.02955,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1937.0,"raw_peak_contact_force":1.34255,"subtask_id":"push_to_goal","tcp_end":[0.48288,-0.03805,0.04689],"tcp_start":[0.46631,0.15008,0.05207],"tcp_to_object_dist_end":0.03988,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.51338,-0.03969,0.02499],"object_pos_start":[0.51859,-0.04165,0.02949],"object_to_goal_dist_end":0.11112,"object_to_goal_dist_start":0.11002,"object_z_max":0.02949,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2436.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47978,-0.03787,0.13546],"tcp_start":[0.48288,-0.03805,0.04689],"tcp_to_object_dist_end":0.11548,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44633,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.08419,"approach_1.speed":0.12307,"descend_1.speed":0.04265,"push_1.max_force":24.96833,"push_1.speed":0.06364,"push_1.stroke":0.30576,"retract_1.speed":0.17831},"optimized_scores":{"best_composite_score":0.27899,"best_fitness_score":0.68899,"best_task_score":0.83357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":581.0,"contact_point_centroid":[0.52511,-0.07369,0.04632],"force_p95":18.42608,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.23491,"mean_force":6.39825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52372,-0.06195,0.04553]},{"body_a":"world","body_b":"push_box","contact_count":1715.0,"contact_point_centroid":[0.53591,-0.08015,-3e-05],"force_p95":10.09459,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.27996,"mean_force":2.56717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53692,-0.02513,0.04592]},{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.50271,-0.14717,0.05329],"force_p95":0.92276,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.06965,"mean_force":0.62994,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49532,-0.13706,0.04982]},{"body_a":"world","body_b":"push_box","contact_count":1934.0,"contact_point_centroid":[0.51866,-0.16454,-2e-05],"force_p95":0.38549,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99513,"mean_force":0.26279,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4942,-0.13642,0.09126]},{"body_a":"world","body_b":"push_box","contact_count":2536.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5177,-0.01161,0.21606]},{"body_a":"world","body_b":"push_box","contact_count":1760.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55061,0.01174,0.08926]}],"total_contact_groups":6},"final_pose_error":0.01244,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51771,-0.16303,0.02499],"final_tcp_position":[0.49436,-0.13641,0.13359],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":22.23491,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.53791,-0.02366,0.13228],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":440.0,"n_steps_budget":630.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.95002,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":22.23491,"subtask_id":"reach_object","tcp_end":[0.56563,0.04684,0.05083],"tcp_start":[0.53791,-0.02366,0.13228],"tcp_to_object_dist_end":0.07976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51936,-0.16509,0.02781],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02471,"object_to_goal_dist_start":0.13211,"object_z_max":0.02786,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1962.0,"raw_peak_contact_force":1.06965,"subtask_id":"push_to_goal","tcp_end":[0.49754,-0.13715,0.04559],"tcp_start":[0.56563,0.04684,0.05083],"tcp_to_object_dist_end":0.03966,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.51771,-0.16303,0.02499],"object_pos_start":[0.51936,-0.16509,0.02781],"object_to_goal_dist_end":0.02199,"object_to_goal_dist_start":0.02471,"object_z_max":0.02783,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49436,-0.13641,0.13359],"tcp_start":[0.49754,-0.13715,0.04559],"tcp_to_object_dist_end":0.11422,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```