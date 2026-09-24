## Search State

- **Seed**: 9
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.3307 | 0.55 | ❌ rejected |
| 9 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4703 | 0.84 | ✅ accepted |
| 8 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3787 | 0.72 | ✅ accepted |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0546 | 0.01 | ❌ rejected |
| 6 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3488 | 0.67 | ✅ accepted |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.840, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.331) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
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
    - 0.02
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_contact
- id: contact_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
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
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **contact_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.331
- **task_score** (E): 0.552
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1434 |
| descend_1 | 1.00 | 1.00 | 0.1238 |
| contact_1 | 0.33 | 1.00 | 0.0325 |
| push_1 | 1.00 | 1.00 | 0.0708 |
| retract_1 | 1.00 | 1.00 | 0.0883 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.018, 0.167) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.513, -0.018, 0.167)→(0.516, 0.016, 0.052) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | push | 0.33 / step_budget | (0.516, 0.016, 0.052)→(0.514, -0.010, 0.035) | (0.518, -0.020, 0.025)→(0.519, -0.037, 0.025) | 0.139→0.121 | 1.00 / 2.000 | 19.218 | 24.647 |
| push_1 | push | 1.00 / force_exceeded | (0.514, -0.010, 0.035)→(0.512, -0.077, 0.031) | (0.519, -0.037, 0.025)→(0.526, -0.100, 0.025) | 0.121→0.060 | 1.00 / 3.667 | 23.586 | 28.757 |
| retract_1 | retract | 1.00 / step_budget | (0.512, -0.077, 0.031)→(0.509, -0.077, 0.119) | (0.526, -0.100, 0.025)→(0.526, -0.100, 0.025) | 0.060→0.060 | 1.00 / 4.000 | 0.245 | 16.898 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.800
- lateral_force_integral: None
- approach_alignment: 0.682
- goal_progress: 0.732
- terminal_score: 0.732
- phase_score: 0.699
- phase_breakdown.reach_contact_score: 0.744
- phase_breakdown.push_to_goal_score: 0.679

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.898
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.923
- **Median Q (composite search score)**: 0.458
- **K-run variance**: 0.0360
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: approach_1.approach_height
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1133,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19999,"approach_1.speed":0.02878,"contact_1.contact_force_threshold":25.45076,"contact_1.contact_speed":0.02602,"descend_1.behind_distance":0.05777,"push_1.push_force_threshold":22.10577,"push_1.push_speed":0.06504},"optimized_scores":{"best_composite_score":0.45771,"best_fitness_score":0.89771,"best_task_score":0.92262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":882.0,"contact_point_centroid":[0.52179,-0.07858,0.02247],"force_p95":10.82537,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.78964,"mean_force":3.51931,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52229,-0.06668,0.01975]},{"body_a":"world","body_b":"push_box","contact_count":1984.0,"contact_point_centroid":[0.52124,-0.10565,-4e-05],"force_p95":5.00691,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.02845,"mean_force":1.81652,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52369,-0.06249,0.01979]},{"body_a":"attachment","body_b":"push_box","contact_count":637.0,"contact_point_centroid":[0.54518,-0.01446,0.03184],"force_p95":8.16484,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.01256,"mean_force":4.45414,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54625,-0.00255,0.03159]},{"body_a":"world","body_b":"push_box","contact_count":3072.0,"contact_point_centroid":[0.54296,-0.03827,-3e-05],"force_p95":3.22416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.91221,"mean_force":1.1686,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54816,0.0037,0.03523]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51402,-0.12842,0.0504],"force_p95":3.72126,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.83515,"mean_force":2.69627,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50627,-0.11639,0.01981]},{"body_a":"world","body_b":"push_box","contact_count":2146.0,"contact_point_centroid":[0.50918,-0.15444,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.73338,"mean_force":0.25094,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50276,-0.11572,0.06369]},{"body_a":"world","body_b":"push_box","contact_count":1388.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51674,-0.01075,0.26438]},{"body_a":"world","body_b":"push_box","contact_count":2380.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54589,0.00103,0.13964]}],"total_contact_groups":8},"final_pose_error":0.01223,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50925,-0.15435,0.02499],"final_tcp_position":[0.50286,-0.1157,0.10811],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":17.78964,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1388.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53621,-0.02225,0.22924],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.55787,0.02502,0.05192],"tcp_start":[0.53621,-0.02225,0.22924],"tcp_to_object_dist_end":0.05888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53731,-0.05258,0.02502],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.10432,"object_to_goal_dist_start":0.13211,"object_z_max":0.02508,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3709.0,"raw_peak_contact_force":9.01256,"subtask_id":"reach_contact","tcp_end":[0.54262,-0.01598,0.02444],"tcp_start":[0.55787,0.02502,0.05192],"tcp_to_object_dist_end":0.03698,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50921,-0.15328,0.02518],"object_pos_start":[0.53731,-0.05258,0.02502],"object_to_goal_dist_end":0.00977,"object_to_goal_dist_start":0.10432,"object_z_max":0.02523,"peak_contact_force":2.27932,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2866.0,"raw_peak_contact_force":17.78964,"subtask_id":"push_to_goal","tcp_end":[0.50629,-0.11635,0.01983],"tcp_start":[0.54262,-0.01598,0.02444],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50925,-0.15435,0.02499],"object_pos_start":[0.50921,-0.15328,0.02518],"object_to_goal_dist_end":0.01022,"object_to_goal_dist_start":0.00977,"object_z_max":0.02531,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2148.0,"raw_peak_contact_force":3.83515,"tcp_end":[0.50286,-0.1157,0.10811],"tcp_start":[0.50629,-0.11635,0.01983],"tcp_to_object_dist_end":0.09189,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72816,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12841,"approach_1.speed":0.07151,"contact_1.contact_force_threshold":36.16702,"contact_1.contact_speed":0.02191,"descend_1.behind_distance":0.01067,"push_1.push_force_threshold":29.75587,"push_1.push_speed":0.06832},"optimized_scores":{"best_composite_score":0.06247,"best_fitness_score":0.10247,"best_task_score":0.00075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56495,-0.0262,0.04982],"force_p95":55.41804,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.12791,"mean_force":45.6921,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.55322,-0.02615,0.05221]},{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.56387,-0.02632,0.04975],"force_p95":42.51666,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.24753,"mean_force":10.1123,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55216,-0.02622,0.05195]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56473,-0.0262,0.04957],"force_p95":37.16137,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.71906,"mean_force":21.35141,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55301,-0.02616,0.05177]},{"body_a":"world","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.55664,-0.03508,-1e-05],"force_p95":27.86767,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.34919,"mean_force":5.52364,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.55347,-0.02616,0.05263]},{"body_a":"world","body_b":"push_box","contact_count":2151.0,"contact_point_centroid":[0.55412,-0.03509,-2e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.67682,"mean_force":0.32949,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54933,-0.02613,0.09463]},{"body_a":"world","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.55976,-0.03509,-5e-05],"force_p95":17.45894,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.07653,"mean_force":6.61164,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55299,-0.02616,0.05175]},{"body_a":"world","body_b":"push_box","contact_count":2164.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52237,-0.0158,0.22939]},{"body_a":"world","body_b":"push_box","contact_count":1328.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54936,-0.02929,0.10606]}],"total_contact_groups":8},"final_pose_error":0.01286,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55455,-0.0351,0.02499],"final_tcp_position":[0.54947,-0.02612,0.13914],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":56.12791,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2164.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.54729,-0.0322,0.15942],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":750.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.5538,-0.02619,0.05322],"tcp_start":[0.54729,-0.0322,0.15942],"tcp_to_object_dist_end":0.02962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":7.0,"n_steps_budget":870.0,"object_pos_end":[0.55479,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12732,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":56.12791,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":29.0,"raw_peak_contact_force":56.12791,"subtask_id":"reach_contact","tcp_end":[0.55311,-0.02616,0.05191],"tcp_start":[0.5538,-0.02619,0.05322],"tcp_to_object_dist_end":0.02841,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55469,-0.03508,0.02483],"object_pos_start":[0.55479,-0.03508,0.02499],"object_to_goal_dist_end":0.12727,"object_to_goal_dist_start":0.12732,"object_z_max":0.02499,"peak_contact_force":38.71906,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":38.71906,"subtask_id":"push_to_goal","tcp_end":[0.55285,-0.0262,0.05155],"tcp_start":[0.55311,-0.02616,0.05191],"tcp_to_object_dist_end":0.02821,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.55455,-0.0351,0.02499],"object_pos_start":[0.55469,-0.03508,0.02483],"object_to_goal_dist_end":0.12719,"object_to_goal_dist_start":0.12727,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":46.24753,"tcp_end":[0.54947,-0.02612,0.13914],"tcp_start":[0.55285,-0.0262,0.05155],"tcp_to_object_dist_end":0.11462,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46821,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0764,"approach_1.speed":0.07291,"contact_1.contact_force_threshold":36.22575,"contact_1.contact_speed":0.02401,"descend_1.behind_distance":0.05946,"push_1.push_force_threshold":20.84334,"push_1.push_speed":0.06791},"optimized_scores":{"best_composite_score":0.47195,"best_fitness_score":0.71195,"best_task_score":0.7319},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":737.0,"contact_point_centroid":[0.4703,-0.04535,0.04862],"force_p95":13.91403,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.76109,"mean_force":5.43874,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45934,-0.03477,0.02308]},{"body_a":"world","body_b":"push_box","contact_count":1509.0,"contact_point_centroid":[0.49708,-0.08281,-4e-05],"force_p95":8.8283,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.43097,"mean_force":3.16995,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46099,-0.03978,0.02299]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.50092,-0.04309,0.05496],"force_p95":10.84763,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.1266,"mean_force":6.13772,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46254,-0.0454,0.02262]},{"body_a":"attachment","body_b":"push_box","contact_count":681.0,"contact_point_centroid":[0.44726,0.01259,0.04947],"force_p95":7.28743,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.79971,"mean_force":4.48849,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.4429,0.02449,0.0341]},{"body_a":"world","body_b":"push_box","contact_count":2694.0,"contact_point_centroid":[0.45912,-0.01499,-3e-05],"force_p95":3.97568,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.94491,"mean_force":1.41732,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.44062,0.0312,0.03787]},{"body_a":"world","body_b":"push_box","contact_count":2176.0,"contact_point_centroid":[0.51421,-0.11055,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61161,"mean_force":0.24617,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47324,-0.08818,0.06544]},{"body_a":"world","body_b":"push_box","contact_count":2440.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47736,-6e-05,0.20585]},{"body_a":"world","body_b":"push_box","contact_count":1128.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44569,0.02364,0.08021]}],"total_contact_groups":8},"final_pose_error":0.01155,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51421,-0.11055,0.02499],"final_tcp_position":[0.47325,-0.08814,0.1105],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":29.76109,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2440.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45553,-0.00012,0.11129],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.43744,0.04877,0.05035],"tcp_start":[0.45553,-0.00012,0.11129],"tcp_to_object_dist_end":0.05791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46502,-0.02345,0.02506],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.13129,"object_to_goal_dist_start":0.1564,"object_z_max":0.02518,"peak_contact_force":1.52549,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3375.0,"raw_peak_contact_force":8.79971,"subtask_id":"reach_contact","tcp_end":[0.44747,0.01208,0.02753],"tcp_start":[0.43744,0.04877,0.05035],"tcp_to_object_dist_end":0.03971,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.51396,-0.11024,0.02491],"object_pos_start":[0.46502,-0.02345,0.02506],"object_to_goal_dist_end":0.04214,"object_to_goal_dist_start":0.13129,"object_z_max":0.02771,"peak_contact_force":29.76109,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2259.0,"raw_peak_contact_force":29.76109,"subtask_id":"push_to_goal","tcp_end":[0.47651,-0.08863,0.02157],"tcp_start":[0.44747,0.01208,0.02753],"tcp_to_object_dist_end":0.04337,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.51421,-0.11055,0.02499],"object_pos_start":[0.51396,-0.11024,0.02491],"object_to_goal_dist_end":0.04193,"object_to_goal_dist_start":0.04214,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.61161,"tcp_end":[0.47325,-0.08814,0.1105],"tcp_start":[0.47651,-0.08863,0.02157],"tcp_to_object_dist_end":0.09743,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```