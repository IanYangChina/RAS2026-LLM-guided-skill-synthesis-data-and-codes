## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0803 | 0.45 | ✅ accepted |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1433 | 0.07 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2087 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1741 | 0.44 | ✅ accepted |
| 4 | approach → push → retract | arc_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1091 | 0.01 | ✅ accepted |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.4792366731926673, 0.05847322120055107, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.4792366731926673, 0.05847322120055107, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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

## Current Skill (Q=0.080) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: backend_approach
  anchor: object
  offset:
  - 0.0
  - -0.08
  - 0.0
  weight: 0.2
- id: establish_contact
  anchor: object
  metric: contact
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_behind
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - -0.08
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: backend_approach
- id: make_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: probe_contact
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: establish_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 22.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - -0.005
    - 0.0
  subtask_id: push_to_goal
- id: retract_away
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, -0.08, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **make_contact** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=replace_offset_projection, sign=negative}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=probe_contact, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=22.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, -0.005, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.080
- **task_score** (E): 0.452
- **fitness_score**: 0.407  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 0.33 | 0.2887 |
| make_contact | 0.33 | 1.00 | 0.0016 |
| push_to_goal | 0.33 | 1.00 | 0.0627 |
| retract_away | 1.00 | 1.00 | 0.0792 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.527, -0.062, 0.024) | (0.526, -0.001, 0.025)→(0.530, -0.075, 0.030) | 0.156→0.100 | 0.33 / 1.000 | 13.898 | 142.379 |
| make_contact | contact | 0.33 / guard_failure | (0.527, -0.062, 0.024)→(0.526, -0.062, 0.023) | (0.530, -0.075, 0.030)→(0.529, -0.076, 0.029) | 0.100→0.100 | 1.00 / 1.667 | 20.242 | 5.206 |
| push_to_goal | push | 0.33 / guard_failure | (0.526, -0.062, 0.023)→(0.520, -0.116, 0.017) | (0.529, -0.076, 0.029)→(0.528, -0.084, 0.025) | 0.100→0.093 | 1.00 / 4.667 | 33.186 | 38.900 |
| retract_away | retract | 1.00 / step_budget | (0.495, -0.158, 0.022)→(0.496, -0.146, 0.100) | (0.482, 0.021, 0.025)→(0.482, 0.021, 0.025) | 0.172→0.172 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.181
- lateral_force_integral: None
- approach_alignment: 0.793
- goal_progress: 0.181
- terminal_score: 0.181
- phase_score: 0.383
- phase_breakdown.establish_contact_score: 1.000
- phase_breakdown.backend_approach_score: 0.676
- phase_breakdown.push_to_goal_score: 0.079

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.486
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.635
- **Median Q (composite search score)**: 0.076
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.275


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65584,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.12334,"approach_behind.arc_height":0.19032,"make_contact.contact_force_threshold":11.40998,"make_contact.contact_speed":0.03105,"push_to_goal.push_distance":0.18283,"push_to_goal.push_speed":0.04544,"retract_away.retract_height":0.09434},"optimized_scores":{"best_composite_score":0.14186,"best_fitness_score":0.30186,"best_task_score":0.1808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":102.0,"contact_point_centroid":[0.48884,0.02523,0.04536],"force_p95":215.20815,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":232.22202,"mean_force":157.06463,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48318,0.0165,0.04507]},{"body_a":"world","body_b":"push_box","contact_count":2418.0,"contact_point_centroid":[0.47932,0.05645,-6e-05],"force_p95":50.1638,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.34344,"mean_force":6.90298,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48891,0.05705,0.17215]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.48143,0.00694,0.03375],"force_p95":9.43551,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.38851,"mean_force":1.96538,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48176,-0.00496,0.03366]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.48531,0.00414,0.03588],"force_p95":8.81469,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.61934,"mean_force":2.61526,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.48397,-0.00738,0.03581]},{"body_a":"world","body_b":"push_box","contact_count":44.0,"contact_point_centroid":[0.46993,0.04322,-8e-05],"force_p95":3.34367,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.79013,"mean_force":1.39701,"phase_index":1.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.48278,-0.00606,0.03471]},{"body_a":"world","body_b":"push_box","contact_count":960.0,"contact_point_centroid":[0.48176,0.02185,-0.00011],"force_p95":0.54407,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.11751,"mean_force":0.31387,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48819,-0.08816,0.02605]},{"body_a":"world","body_b":"push_box","contact_count":1004.0,"contact_point_centroid":[0.48185,0.02066,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_away","phase_type":"retract","tcp_position_centroid":[0.49424,-0.14766,0.05986]}],"total_contact_groups":7},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48185,0.02066,0.02499],"final_tcp_position":[0.49611,-0.14644,0.10034],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":232.22202,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.48066,0.03464,0.03493],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.18591,"object_to_goal_dist_start":0.2095,"object_z_max":0.03484,"peak_contact_force":41.6952,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":232.22202,"subtask_id":"backend_approach","tcp_end":[0.48468,-0.00666,0.03656],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.4803,0.03512,0.03343],"object_pos_start":[0.48066,0.03464,0.03493],"object_to_goal_dist_end":0.18636,"object_to_goal_dist_start":0.18591,"object_z_max":0.03562,"peak_contact_force":60.56805,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":57.0,"raw_peak_contact_force":15.61934,"subtask_id":"establish_contact","tcp_end":[0.48198,-0.00481,0.034],"tcp_start":[0.48468,-0.00666,0.03656],"tcp_to_object_dist_end":0.03997,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.48185,0.02066,0.02499],"object_pos_start":[0.4803,0.03512,0.03343],"object_to_goal_dist_end":0.17163,"object_to_goal_dist_start":0.18636,"object_z_max":0.03343,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":971.0,"raw_peak_contact_force":17.38851,"subtask_id":"push_to_goal","tcp_end":[0.49521,-0.15759,0.02199],"tcp_start":[0.48198,-0.00481,0.034],"tcp_to_object_dist_end":0.17878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":630.0,"object_pos_end":[0.48185,0.02066,0.02499],"object_pos_start":[0.48185,0.02066,0.02499],"object_to_goal_dist_end":0.17163,"object_to_goal_dist_start":0.17163,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_away","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49611,-0.14644,0.10034],"tcp_start":[0.49521,-0.15759,0.02199],"tcp_to_object_dist_end":0.18386,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13793,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.17004,"approach_behind.arc_height":0.14391,"make_contact.contact_force_threshold":9.08646,"make_contact.contact_speed":0.03166,"push_to_goal.push_distance":0.19891,"push_to_goal.push_speed":0.05064,"retract_away.retract_height":0.10216},"optimized_scores":{"best_composite_score":0.07614,"best_fitness_score":0.48614,"best_task_score":0.63454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":158.0,"contact_point_centroid":[0.54977,-0.052,0.04643],"force_p95":48.89105,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.34445,"mean_force":17.20717,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54169,-0.04079,0.01838]},{"body_a":"world","body_b":"push_box","contact_count":2581.0,"contact_point_centroid":[0.54554,-0.03014,-2e-05],"force_p95":5.99203,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.78905,"mean_force":2.03614,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52012,0.05046,0.15608]},{"body_a":"push_box","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.56932,-0.07955,0.05149],"force_p95":45.61318,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.16741,"mean_force":19.02252,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54262,-0.06002,0.01567]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56071,-0.10823,0.0492],"force_p95":47.31873,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.31873,"mean_force":47.31873,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52757,-0.0931,0.01492]},{"body_a":"world","body_b":"push_box","contact_count":71.0,"contact_point_centroid":[0.54687,-0.13373,-0.00024],"force_p95":2.53896,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.74528,"mean_force":1.30208,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53435,-0.0906,0.01613]}],"total_contact_groups":5},"final_pose_error":0.18254,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5452,-0.13304,0.02453],"final_tcp_position":[0.52698,-0.09335,0.01485],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":79.34445,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.54872,-0.12848,0.02741],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.05331,"object_to_goal_dist_start":0.13211,"object_z_max":0.03064,"peak_contact_force":0.0,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2853.0,"raw_peak_contact_force":79.34445,"subtask_id":"backend_approach","tcp_end":[0.54219,-0.08723,0.01787],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54855,-0.12905,0.02718],"object_pos_start":[0.54872,-0.12848,0.02741],"object_to_goal_dist_end":0.05293,"object_to_goal_dist_start":0.05331,"object_z_max":0.02741,"peak_contact_force":0.0,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"establish_contact","tcp_end":[0.54219,-0.08752,0.01788],"tcp_start":[0.54219,-0.08723,0.01787],"tcp_to_object_dist_end":0.04303,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.5452,-0.13304,0.02453],"object_pos_start":[0.54855,-0.12905,0.02718],"object_to_goal_dist_end":0.04828,"object_to_goal_dist_start":0.05293,"object_z_max":0.02718,"peak_contact_force":47.31873,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":72.0,"raw_peak_contact_force":47.31873,"subtask_id":"push_to_goal","tcp_end":[0.52698,-0.09335,0.01485],"tcp_start":[0.54219,-0.08752,0.01788],"tcp_to_object_dist_end":0.04474,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55472,-0.03508,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.32692,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.20629,"approach_behind.arc_height":0.15878,"make_contact.contact_force_threshold":17.74752,"make_contact.contact_speed":0.04158,"push_to_goal.push_distance":0.22582,"push_to_goal.push_speed":0.05095,"retract_away.retract_height":0.11746},"optimized_scores":{"best_composite_score":0.02297,"best_fitness_score":0.43297,"best_task_score":0.5414},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2554.0,"contact_point_centroid":[0.55585,-0.03972,-2e-05],"force_p95":8.13319,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.56981,"mean_force":2.56533,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52656,0.0453,0.15004]},{"body_a":"attachment","body_b":"push_box","contact_count":141.0,"contact_point_centroid":[0.56105,-0.0613,0.04316],"force_p95":79.38961,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.41301,"mean_force":28.58919,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.55283,-0.05045,0.01774]},{"body_a":"push_box","body_b":"link7","contact_count":96.0,"contact_point_centroid":[0.5796,-0.08041,0.05124],"force_p95":64.71542,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.3828,"mean_force":26.29489,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.55365,-0.06072,0.01516]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.57194,-0.10931,0.04857],"force_p95":51.9938,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.9938,"mean_force":51.9938,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53724,-0.09789,0.01462]},{"body_a":"world","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.56075,-0.1429,-0.00035],"force_p95":2.4169,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.61296,"mean_force":1.45299,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54336,-0.09639,0.01565]}],"total_contact_groups":5},"final_pose_error":0.20841,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55736,-0.13924,0.02407],"final_tcp_position":[0.53661,-0.09805,0.01456],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":115.56981,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":772.0,"n_steps_budget":930.0,"object_pos_end":[0.55951,-0.13216,0.02738],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.06217,"object_to_goal_dist_start":0.12728,"object_z_max":0.02785,"peak_contact_force":0.0,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2791.0,"raw_peak_contact_force":115.56981,"subtask_id":"backend_approach","tcp_end":[0.55335,-0.09309,0.01773],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55948,-0.13274,0.02729],"object_pos_start":[0.55951,-0.13216,0.02738],"object_to_goal_dist_end":0.06198,"object_to_goal_dist_start":0.06217,"object_z_max":0.02738,"peak_contact_force":0.15716,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"establish_contact","tcp_end":[0.55332,-0.09347,0.01773],"tcp_start":[0.55335,-0.09309,0.01773],"tcp_to_object_dist_end":0.04088,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":33.0,"n_steps_budget":1000.0,"object_pos_end":[0.55736,-0.13924,0.02407],"object_pos_start":[0.55948,-0.13274,0.02729],"object_to_goal_dist_end":0.05837,"object_to_goal_dist_start":0.06198,"object_z_max":0.02729,"peak_contact_force":51.9938,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":65.0,"raw_peak_contact_force":51.9938,"subtask_id":"push_to_goal","tcp_end":[0.53661,-0.09805,0.01456],"tcp_start":[0.55332,-0.09347,0.01773],"tcp_to_object_dist_end":0.04709,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```