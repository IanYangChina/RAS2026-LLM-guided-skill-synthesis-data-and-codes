## Search State

- **Seed**: 8
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | contact_detected | pose_tolerance | 5 | -0.1211 | 0.04 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 4 | -0.1264 | 0.00 | ✅ accepted |
| 2 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 6 | 0.0679 | 0.00 | ✅ accepted |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ❌ rejected |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.121) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_box
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_and_contact
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
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
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_offset_behind:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
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
  subtask_id: contact_box
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 25.0
      default: 20.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_and_contact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_behind: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=20.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: -0.121
- **task_score** (E): 0.039
- **fitness_score**: 0.129  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_and_contact | 1.00 | 1.00 | 0.2680 |
| push_to_goal | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_and_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.533, 0.023, 0.041) | (0.526, -0.001, 0.025)→(0.528, 0.000, 0.024) | 0.156→0.157 | 1.00 / 4.000 | 180.563 | 197.762 |
| push_to_goal | push | 0.00 / guard_failure | (0.530, 0.018, 0.039)→(0.530, 0.018, 0.039) | (0.528, 0.000, 0.024)→(0.527, -0.005, 0.024) | 0.157→0.153 | 1.00 / 4.333 | 89.342 | 90.907 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.120
- lateral_force_integral: None
- approach_alignment: 0.478
- goal_progress: 0.118
- terminal_score: 0.118
- phase_score: 0.219
- phase_breakdown.contact_box_score: 0.460
- phase_breakdown.push_to_goal_score: 0.115

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.178
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.118
- **Median Q (composite search score)**: -0.141
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.426


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47826,"average_solve_count":23.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_contact.approach_offset_behind":0.02013,"approach_and_contact.approach_speed":0.29841,"push_to_goal.push_force_limit":16.15451,"push_to_goal.push_speed":0.05729,"push_to_goal.push_stroke":0.26923},"optimized_scores":{"best_composite_score":-0.14103,"best_fitness_score":0.10897,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.4905,0.06964,0.04741],"force_p95":286.97806,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":287.63163,"mean_force":250.40302,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.4788,0.07107,0.04811]},{"body_a":"world","body_b":"push_box","contact_count":2373.0,"contact_point_centroid":[0.47959,0.05877,-2e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":186.43064,"mean_force":3.63847,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.48776,0.03403,0.17618]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49352,0.07,0.04563],"force_p95":99.57053,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.80531,"mean_force":97.45752,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48204,0.07315,0.0452]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.48873,0.06736,-0.00082],"force_p95":74.7954,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.61625,"mean_force":32.73251,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48204,0.07315,0.0452]}],"total_contact_groups":4},"final_pose_error":0.283,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48138,0.06007,0.024],"final_tcp_position":[0.48224,0.07323,0.04525],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":287.63163,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.48142,0.06004,0.02398],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.21087,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":281.78079,"phase_name":"approach_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2405.0,"raw_peak_contact_force":287.63163,"subtask_id":"contact_box","tcp_end":[0.48197,0.07312,0.04519],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.4814,0.06006,0.02399],"object_pos_start":[0.48142,0.06004,0.02398],"object_to_goal_dist_end":0.21089,"object_to_goal_dist_start":0.21087,"object_z_max":0.02399,"peak_contact_force":95.10974,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":99.80531,"subtask_id":"push_to_goal","tcp_end":[0.48224,0.07323,0.04525],"tcp_start":[0.48212,0.07318,0.04521],"tcp_to_object_dist_end":0.02502,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.5,"average_solve_count":24.0,"average_success_count":24.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_contact.approach_offset_behind":0.02014,"approach_and_contact.approach_speed":0.27752,"push_to_goal.push_force_limit":21.74645,"push_to_goal.push_speed":0.03644,"push_to_goal.push_stroke":0.23393},"optimized_scores":{"best_composite_score":-0.15046,"best_fitness_score":0.09954,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.55754,-0.00742,0.04733],"force_p95":260.72125,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":261.06642,"mean_force":220.50243,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.54594,-0.00544,0.04803]},{"body_a":"world","body_b":"push_box","contact_count":2476.0,"contact_point_centroid":[0.54495,-0.02535,-2e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.36309,"mean_force":3.65282,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.51984,-0.00288,0.1759]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.56257,-0.00917,0.04542],"force_p95":118.78432,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.64832,"mean_force":111.00831,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55142,-0.00494,0.0451]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.55469,-0.01749,-0.00077],"force_p95":87.05947,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.27327,"mean_force":37.34595,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55142,-0.00494,0.0451]}],"total_contact_groups":4},"final_pose_error":0.25431,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54763,-0.02446,0.02427],"final_tcp_position":[0.55152,-0.00494,0.04513],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":261.06642,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.54766,-0.02445,0.02426],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13429,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":259.66305,"phase_name":"approach_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2514.0,"raw_peak_contact_force":261.06642,"subtask_id":"contact_box","tcp_end":[0.55137,-0.00495,0.04509],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54765,-0.02445,0.02426],"object_pos_start":[0.54766,-0.02445,0.02426],"object_to_goal_dist_end":0.13429,"object_to_goal_dist_start":0.13429,"object_z_max":0.02426,"peak_contact_force":119.64832,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":119.64832,"subtask_id":"push_to_goal","tcp_end":[0.55152,-0.00494,0.04513],"tcp_start":[0.55146,-0.00494,0.0451],"tcp_to_object_dist_end":0.02883,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16981,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_contact.approach_offset_behind":0.04096,"approach_and_contact.approach_speed":0.1711,"push_to_goal.push_force_limit":18.11688,"push_to_goal.push_speed":0.04049,"push_to_goal.push_stroke":0.24693},"optimized_scores":{"best_composite_score":-0.0717,"best_fitness_score":0.1783,"best_task_score":0.11799},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.56267,-0.01493,0.03925],"force_p95":27.95154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.26663,"mean_force":6.02007,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.56056,-0.00299,0.02917]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.56107,-0.01021,0.04966],"force_p95":44.46015,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.587,"mean_force":28.95983,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.56037,0.00163,0.04976]},{"body_a":"world","body_b":"push_box","contact_count":3991.0,"contact_point_centroid":[0.55474,-0.03515,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.21292,"mean_force":0.28909,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.53058,0.00083,0.16783]},{"body_a":"world","body_b":"push_box","contact_count":82.0,"contact_point_centroid":[0.55042,-0.0437,-6e-05],"force_p95":9.78385,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.92803,"mean_force":2.23334,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.56021,-0.00417,0.02923]}],"total_contact_groups":4},"final_pose_error":0.26741,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55058,-0.04977,0.02477],"final_tcp_position":[0.55519,-0.01302,0.02735],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":53.26663,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55478,-0.03533,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12708,"object_to_goal_dist_start":0.12728,"object_z_max":0.02501,"peak_contact_force":0.24529,"phase_name":"approach_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3997.0,"raw_peak_contact_force":44.587,"subtask_id":"contact_box","tcp_end":[0.56485,0.00178,0.03167],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.55057,-0.04953,0.02467],"object_pos_start":[0.55478,-0.03533,0.02499],"object_to_goal_dist_end":0.11248,"object_to_goal_dist_start":0.12708,"object_z_max":0.02523,"peak_contact_force":53.26663,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":108.0,"raw_peak_contact_force":53.26663,"subtask_id":"push_to_goal","tcp_end":[0.55519,-0.01302,0.02735],"tcp_start":[0.55522,-0.01276,0.02738],"tcp_to_object_dist_end":0.0369,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```