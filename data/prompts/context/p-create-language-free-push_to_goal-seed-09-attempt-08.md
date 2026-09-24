## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3787 | 0.72 | ✅ accepted |
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0546 | 0.01 | ❌ rejected |
| 6 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3488 | 0.67 | ✅ accepted |
| 5 | approach → descend → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0177 | 0.47 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1632 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.723, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.379) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
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
    - 0.05
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
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
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

- **Composite score**: 0.379
- **task_score** (E): 0.723
- **fitness_score**: 0.669  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1361 |
| descend_1 | 1.00 | 1.00 | 0.1416 |
| contact_1 | 1.00 | 1.00 | 0.0318 |
| push_1 | 1.00 | 1.00 | 0.1369 |
| retract_1 | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.027, 0.175) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.027, 0.175)→(0.514, 0.029, 0.034) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | push | 1.00 / step_budget | (0.514, 0.029, 0.034)→(0.513, -0.001, 0.024) | (0.518, -0.020, 0.025)→(0.519, -0.038, 0.025) | 0.139→0.123 | 1.00 / 2.333 | 6.110 | 42.642 |
| push_1 | push | 1.00 / step_budget | (0.513, -0.001, 0.024)→(0.499, -0.131, 0.021) | (0.519, -0.038, 0.025)→(0.529, -0.151, 0.026) | 0.123→0.038 | 1.00 / 3.667 | 19.628 | 50.949 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.131, 0.021)→(0.496, -0.131, 0.109) | (0.529, -0.151, 0.026)→(0.527, -0.151, 0.025) | 0.038→0.037 | 1.00 / 4.000 | 0.245 | 19.688 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.764
- goal_progress: 0.872
- terminal_score: 0.872
- phase_score: 0.766
- phase_breakdown.reach_contact_score: 0.539
- phase_breakdown.push_to_goal_score: 0.863

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.808
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.872
- **Median Q (composite search score)**: 0.441
- **K-run variance**: 0.0214
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37838,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1234,"approach_1.speed":0.06982,"contact_1.contact_speed":0.0335,"push_1.push_speed":0.05376},"optimized_scores":{"best_composite_score":0.44079,"best_fitness_score":0.73079,"best_task_score":0.81087},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":394.0,"contact_point_centroid":[0.54419,-0.12259,-0.0001],"force_p95":39.28005,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.56045,"mean_force":13.68777,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51799,-0.07329,0.02043]},{"body_a":"world","body_b":"push_box","contact_count":1765.0,"contact_point_centroid":[0.52764,-0.16262,-2e-05],"force_p95":0.52649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.44276,"mean_force":0.34209,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49943,-0.12999,0.07175]},{"body_a":"attachment","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.52748,-0.08807,0.04637],"force_p95":39.70404,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.612,"mean_force":11.63126,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51652,-0.07766,0.02016]},{"body_a":"push_box","body_b":"link7","contact_count":126.0,"contact_point_centroid":[0.54385,-0.11304,0.05378],"force_p95":39.29424,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.13395,"mean_force":22.67066,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50957,-0.10314,0.02043]},{"body_a":"push_box","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.5394,-0.13932,0.0549],"force_p95":32.54825,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.96571,"mean_force":7.41694,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5026,-0.13101,0.02207]},{"body_a":"attachment","body_b":"push_box","contact_count":109.0,"contact_point_centroid":[0.51481,-0.13687,0.05465],"force_p95":0.90759,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.79431,"mean_force":1.06701,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50003,-0.13026,0.03583]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.54119,-0.00866,0.0362],"force_p95":12.41267,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.02672,"mean_force":4.05105,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.53865,0.00296,0.0257]},{"body_a":"world","body_b":"push_box","contact_count":232.0,"contact_point_centroid":[0.54465,-0.02916,-2e-05],"force_p95":5.50611,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.19975,"mean_force":0.93949,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.53855,0.01494,0.02921]},{"body_a":"world","body_b":"push_box","contact_count":2116.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51761,0.01088,0.22758]},{"body_a":"world","body_b":"push_box","contact_count":1512.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53749,0.02301,0.09419]}],"total_contact_groups":10},"final_pose_error":0.01222,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52311,-0.15949,0.02499],"final_tcp_position":[0.49957,-0.12999,0.11008],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":57.56045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53769,0.02225,0.15538],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":840.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53958,0.02392,0.03349],"tcp_start":[0.53769,0.02225,0.15538],"tcp_to_object_dist_end":0.05046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":89.0,"n_steps_budget":960.0,"object_pos_end":[0.54362,-0.04325,0.02518],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.11532,"object_to_goal_dist_start":0.13211,"object_z_max":0.02521,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":271.0,"raw_peak_contact_force":39.02672,"subtask_id":"reach_contact","tcp_end":[0.53916,-0.00647,0.02353],"tcp_start":[0.53958,0.02392,0.03349],"tcp_to_object_dist_end":0.03708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.52783,-0.16091,0.02865],"object_pos_start":[0.54362,-0.04325,0.02518],"object_to_goal_dist_end":0.03011,"object_to_goal_dist_start":0.11532,"object_z_max":0.0289,"peak_contact_force":57.55395,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":767.0,"raw_peak_contact_force":57.56045,"subtask_id":"push_to_goal","tcp_end":[0.50296,-0.13073,0.02179],"tcp_start":[0.53916,-0.00647,0.02353],"tcp_to_object_dist_end":0.0397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.52311,-0.15949,0.02499],"object_pos_start":[0.52783,-0.16091,0.02865],"object_to_goal_dist_end":0.02499,"object_to_goal_dist_start":0.03011,"object_z_max":0.02912,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1883.0,"raw_peak_contact_force":53.44276,"tcp_end":[0.49957,-0.12999,0.11008],"tcp_start":[0.50296,-0.13073,0.02179],"tcp_to_object_dist_end":0.09309,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42353,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19024,"approach_1.speed":0.09095,"contact_1.contact_speed":0.04404,"push_1.push_speed":0.04822},"optimized_scores":{"best_composite_score":0.17698,"best_fitness_score":0.46698,"best_task_score":0.48694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":121.0,"contact_point_centroid":[0.53979,-0.07667,0.04868],"force_p95":39.30472,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.03693,"mean_force":9.34716,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52741,-0.06668,0.01969]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.54958,-0.01853,0.02902],"force_p95":36.74906,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.91156,"mean_force":9.97,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54898,-0.00669,0.02555]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.56899,-0.06053,0.05189],"force_p95":31.05736,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.31475,"mean_force":19.19121,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53164,-0.05492,0.01939]},{"body_a":"world","body_b":"push_box","contact_count":563.0,"contact_point_centroid":[0.56012,-0.1082,-9e-05],"force_p95":16.77998,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.83636,"mean_force":2.97634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52158,-0.08214,0.01977]},{"body_a":"world","body_b":"push_box","contact_count":243.0,"contact_point_centroid":[0.55581,-0.0387,-2e-05],"force_p95":11.95534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.25788,"mean_force":1.71566,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.54891,0.00409,0.02877]},{"body_a":"world","body_b":"push_box","contact_count":1404.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52186,0.00643,0.25908]},{"body_a":"world","body_b":"push_box","contact_count":2260.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54685,0.0138,0.12595]},{"body_a":"world","body_b":"push_box","contact_count":2184.0,"contact_point_centroid":[0.55934,-0.12273,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24518,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49936,-0.13045,0.0628]}],"total_contact_groups":8},"final_pose_error":0.01223,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55934,-0.12273,0.02499],"final_tcp_position":[0.49945,-0.13033,0.10797],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":53.03693,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":351.0,"n_steps_budget":720.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.5459,0.01312,0.21932],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.54988,0.01458,0.03351],"tcp_start":[0.5459,0.01312,0.21932],"tcp_to_object_dist_end":0.05062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":89.0,"n_steps_budget":720.0,"object_pos_end":[0.55763,-0.0533,0.02513],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.11257,"object_to_goal_dist_start":0.12728,"object_z_max":0.02518,"peak_contact_force":2.32934,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":278.0,"raw_peak_contact_force":37.91156,"subtask_id":"reach_contact","tcp_end":[0.5496,-0.01611,0.02342],"tcp_start":[0.54988,0.01458,0.03351],"tcp_to_object_dist_end":0.03809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.55935,-0.12272,0.02489],"object_pos_start":[0.55763,-0.0533,0.02513],"object_to_goal_dist_end":0.06532,"object_to_goal_dist_start":0.11257,"object_z_max":0.02671,"peak_contact_force":0.24315,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":700.0,"raw_peak_contact_force":53.03693,"subtask_id":"push_to_goal","tcp_end":[0.50286,-0.13108,0.01969],"tcp_start":[0.5496,-0.01611,0.02342],"tcp_to_object_dist_end":0.05734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.55934,-0.12273,0.02499],"object_pos_start":[0.55935,-0.12272,0.02489],"object_to_goal_dist_end":0.0653,"object_to_goal_dist_start":0.06532,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49945,-0.13033,0.10797],"tcp_start":[0.50286,-0.13108,0.01969],"tcp_to_object_dist_end":0.10262,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06809,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11744,"approach_1.speed":0.05035,"contact_1.contact_speed":0.02616,"push_1.push_speed":0.04649},"optimized_scores":{"best_composite_score":0.51836,"best_fitness_score":0.80836,"best_task_score":0.87177},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.45374,0.01694,0.0397],"force_p95":40.38126,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.98701,"mean_force":6.52622,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.45095,0.02853,0.02745]},{"body_a":"attachment","body_b":"push_box","contact_count":343.0,"contact_point_centroid":[0.47337,-0.06752,0.03426],"force_p95":32.94543,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.25031,"mean_force":5.38536,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47009,-0.05567,0.02147]},{"body_a":"world","body_b":"push_box","contact_count":480.0,"contact_point_centroid":[0.4794,-0.10397,-7e-05],"force_p95":17.98948,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.39723,"mean_force":4.35456,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47011,-0.05562,0.02153]},{"body_a":"world","body_b":"push_box","contact_count":243.0,"contact_point_centroid":[0.45541,-0.00272,-3e-05],"force_p95":9.15562,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.28248,"mean_force":1.3002,"phase_index":2.0,"phase_name":"contact_1","phase_type":"push","tcp_position_centroid":[0.45096,0.03971,0.03048]},{"body_a":"world","body_b":"push_box","contact_count":2143.0,"contact_point_centroid":[0.49962,-0.17045,-1e-05],"force_p95":0.24556,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.37478,"mean_force":0.25271,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48835,-0.13183,0.06438]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.49752,-0.14469,0.04967],"force_p95":2.82048,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.2261,"mean_force":0.80708,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49026,-0.13273,0.02255]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47777,0.02219,0.22584]},{"body_a":"world","body_b":"push_box","contact_count":1560.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45313,0.0472,0.09263]}],"total_contact_groups":8},"final_pose_error":0.01201,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49958,-0.17005,0.02499],"final_tcp_position":[0.48846,-0.13177,0.10875],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":50.98701,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45619,0.04556,0.15125],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":390.0,"n_steps_budget":810.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1560.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.45201,0.04906,0.03424],"tcp_start":[0.45619,0.04556,0.15125],"tcp_to_object_dist_end":0.05013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":89.0,"n_steps_budget":1000.0,"object_pos_end":[0.45494,-0.01694,0.02491],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.14048,"object_to_goal_dist_start":0.1564,"object_z_max":0.02542,"peak_contact_force":16.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":282.0,"raw_peak_contact_force":50.98701,"subtask_id":"reach_contact","tcp_end":[0.45133,0.01928,0.02537],"tcp_start":[0.45201,0.04906,0.03424],"tcp_to_object_dist_end":0.0364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.49967,-0.16918,0.02513],"object_pos_start":[0.45494,-0.01694,0.02491],"object_to_goal_dist_end":0.01918,"object_to_goal_dist_start":0.14048,"object_z_max":0.02585,"peak_contact_force":1.08725,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":823.0,"raw_peak_contact_force":42.25031,"subtask_id":"push_to_goal","tcp_end":[0.4918,-0.13254,0.02027],"tcp_start":[0.45133,0.01928,0.02537],"tcp_to_object_dist_end":0.03779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.49958,-0.17005,0.02499],"object_pos_start":[0.49967,-0.16918,0.02513],"object_to_goal_dist_end":0.02006,"object_to_goal_dist_start":0.01918,"object_z_max":0.02541,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2152.0,"raw_peak_contact_force":5.37478,"tcp_end":[0.48846,-0.13177,0.10875],"tcp_start":[0.4918,-0.13254,0.02027],"tcp_to_object_dist_end":0.09277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```