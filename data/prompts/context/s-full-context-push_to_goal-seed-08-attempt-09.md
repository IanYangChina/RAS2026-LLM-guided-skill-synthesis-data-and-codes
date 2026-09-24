## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.0751 | 0.26 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.4109 | 0.82 | ❌ rejected |
| 7 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.4223 | 0.91 | ✅ accepted |
| 6 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5144 | 0.82 | ❌ rejected |
| 5 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5316 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.905, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.075) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.05
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.1
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    y_offset_approach:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: pre_contact
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
  parameters:
    force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
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
    y_offset_descend:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.1]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - y_offset_approach: status=consumed; consumers=target.offset.y (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - y_offset_descend: status=consumed; consumers=target.offset.y (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.075
- **task_score** (E): 0.262
- **fitness_score**: 0.283  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1854 |
| descend_contact | 1.00 | 0.67 | 0.1008 |
| push_to_goal | 0.67 | 1.00 | 0.0608 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.055, 0.138) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_contact | descend | 1.00 / step_budget | (0.520, 0.055, 0.138)→(0.524, 0.045, 0.039) | (0.526, -0.001, 0.025)→(0.525, -0.004, 0.026) | 0.156→0.153 | 0.67 / 2.667 | 0.164 | 82.075 |
| push_to_goal | push | 0.67 / force_exceeded | (0.524, 0.045, 0.039)→(0.517, -0.013, 0.031) | (0.525, -0.004, 0.026)→(0.531, -0.047, 0.027) | 0.153→0.112 | 1.00 / 3.333 | 32.544 | 14.366 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.344
- lateral_force_integral: None
- approach_alignment: 0.569
- goal_progress: 0.283
- terminal_score: 0.283
- phase_score: 0.349
- phase_breakdown.push_goal_score: 0.283
- phase_breakdown.pre_contact_score: 0.501

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.393
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.397
- **Median Q (composite search score)**: 0.036
- **K-run variance**: 0.0123
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42982,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_tolerance":0.02025,"approach_above.speed":0.33802,"approach_above.y_offset_approach":0.0975,"descend_contact.descend_tolerance":0.01437,"descend_contact.speed_descend":0.04271,"descend_contact.y_offset_descend":0.05867,"push_to_goal.force_threshold_push":19.6746,"push_to_goal.speed_push":0.06704},"optimized_scores":{"best_composite_score":-0.03678,"best_fitness_score":0.39322,"best_task_score":0.39722},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":678.0,"contact_point_centroid":[0.48506,0.0418,0.04243],"force_p95":13.75714,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.20101,"mean_force":4.40388,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47743,0.05343,0.03038]},{"body_a":"world","body_b":"push_box","contact_count":2027.0,"contact_point_centroid":[0.48458,0.02783,-3e-05],"force_p95":6.61369,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.15084,"mean_force":1.80782,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47525,0.08033,0.03195]},{"body_a":"world","body_b":"push_box","contact_count":1568.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48771,0.07899,0.23032]},{"body_a":"world","body_b":"push_box","contact_count":1132.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.4756,0.13321,0.09036]}],"total_contact_groups":4},"final_pose_error":0.16274,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49585,-0.02379,0.0261],"final_tcp_position":[0.48124,0.01162,0.02833],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":18.20101,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47793,0.14522,0.14198],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.47534,0.12052,0.03808],"tcp_start":[0.47793,0.14522,0.14198],"tcp_to_object_dist_end":0.06354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49585,-0.02379,0.0261],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.12629,"object_to_goal_dist_start":0.2095,"object_z_max":0.02621,"peak_contact_force":1.11871,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2705.0,"raw_peak_contact_force":18.20101,"subtask_id":"push_goal","tcp_end":[0.48124,0.01162,0.02833],"tcp_start":[0.47534,0.12052,0.03808],"tcp_to_object_dist_end":0.03837,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2449,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_tolerance":0.0134,"approach_above.speed":0.18181,"approach_above.y_offset_approach":0.03911,"descend_contact.descend_tolerance":0.00957,"descend_contact.speed_descend":0.09033,"descend_contact.y_offset_descend":0.02621,"push_to_goal.force_threshold_push":17.51757,"push_to_goal.speed_push":0.19838},"optimized_scores":{"best_composite_score":0.0362,"best_fitness_score":0.13287,"best_task_score":0.10568},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.55385,-0.00063,0.04669],"force_p95":240.43591,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":245.73316,"mean_force":185.40163,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.54521,0.00635,0.04806]},{"body_a":"world","body_b":"push_box","contact_count":1420.0,"contact_point_centroid":[0.54623,-0.02436,-0.00014],"force_p95":115.23465,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.66546,"mean_force":14.76012,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.53876,0.01031,0.08273]},{"body_a":"world","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.54782,-0.04714,-0.00024],"force_p95":1.85125,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17723,"mean_force":1.07629,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54547,0.0036,0.03323]},{"body_a":"world","body_b":"push_box","contact_count":1676.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51725,0.01774,0.21956]}],"total_contact_groups":4},"final_pose_error":0.15948,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54019,-0.0389,0.02437],"final_tcp_position":[0.54483,0.00285,0.03266],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":245.73316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":630.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.53724,0.01733,0.13562],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":399.0,"n_steps_budget":780.0,"object_pos_end":[0.54138,-0.0364,0.0284],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12095,"object_to_goal_dist_start":0.13211,"object_z_max":0.0288,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1530.0,"raw_peak_contact_force":245.73316,"subtask_id":"pre_contact","tcp_end":[0.54732,0.00507,0.03512],"tcp_start":[0.53724,0.01733,0.13562],"tcp_to_object_dist_end":0.04243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":18.0,"n_steps_budget":600.0,"object_pos_end":[0.54019,-0.0389,0.02437],"object_pos_start":[0.54138,-0.0364,0.0284],"object_to_goal_dist_end":0.11815,"object_to_goal_dist_start":0.12095,"object_z_max":0.0284,"peak_contact_force":73.79444,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":2.17723,"subtask_id":"push_goal","tcp_end":[0.54483,0.00285,0.03266],"tcp_start":[0.54732,0.00507,0.03512],"tcp_to_object_dist_end":0.04282,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78205,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_tolerance":0.01659,"approach_above.speed":0.3065,"approach_above.y_offset_approach":0.0305,"descend_contact.descend_tolerance":0.01998,"descend_contact.speed_descend":0.07737,"descend_contact.y_offset_descend":0.04629,"push_to_goal.force_threshold_push":20.29709,"push_to_goal.speed_push":0.05976},"optimized_scores":{"best_composite_score":0.22591,"best_fitness_score":0.32258,"best_task_score":0.28344},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":84.0,"contact_point_centroid":[0.56939,-0.04991,0.05806],"force_p95":18.44362,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.71954,"mean_force":14.04757,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52646,-0.05146,0.03177]},{"body_a":"world","body_b":"push_box","contact_count":1375.0,"contact_point_centroid":[0.56197,-0.06657,-5e-05],"force_p95":10.28417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.74506,"mean_force":3.50461,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5367,-0.01867,0.03561]},{"body_a":"attachment","body_b":"push_box","contact_count":569.0,"contact_point_centroid":[0.54407,-0.03811,0.05085],"force_p95":11.79427,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.15912,"mean_force":5.53388,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53381,-0.027,0.0343]},{"body_a":"world","body_b":"push_box","contact_count":1444.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.52202,0.0099,0.21953]},{"body_a":"world","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.54682,0.00492,0.09142]}],"total_contact_groups":5},"final_pose_error":0.09897,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55658,-0.07862,0.02967],"final_tcp_position":[0.52584,-0.05471,0.03185],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":22.71954,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.54617,0.0016,0.13732],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":930.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":728.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.54923,0.00896,0.04389],"tcp_start":[0.54617,0.0016,0.13732],"tcp_to_object_dist_end":0.04823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.55658,-0.07862,0.02967],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.09121,"object_to_goal_dist_start":0.12728,"object_z_max":0.02967,"peak_contact_force":22.71954,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2028.0,"raw_peak_contact_force":22.71954,"subtask_id":"push_goal","tcp_end":[0.52584,-0.05471,0.03185],"tcp_start":[0.54923,0.00896,0.04389],"tcp_to_object_dist_end":0.039,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```