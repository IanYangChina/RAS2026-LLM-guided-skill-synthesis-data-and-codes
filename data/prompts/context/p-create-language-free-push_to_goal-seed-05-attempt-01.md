## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6349 | 0.70 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6411 | 0.72 | ✅ accepted |

**Proposal policy**: task_score is 0.70 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.721, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.635) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: reach_push_goal
  offset:
  - 0.0
  - 0.025
  - 0.0
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
    entity: push_box
    offset:
    - 0.0
    - 0.1
    - 0.075
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: world_y
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.025
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
  subtask_id: reach_push_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.1
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.1, 0.075]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.025, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.1, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.635
- **task_score** (E): 0.705
- **fitness_score**: 0.695  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2288 |
| contact_1 | 1.00 | 1.00 | 0.0901 |
| push_1 | 1.00 | 1.00 | 0.1664 |
| retract_1 | 1.00 | 1.00 | 0.0696 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.115, 0.105) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, 0.115, 0.105)→(0.514, 0.059, 0.035) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 19.457 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.059, 0.035)→(0.498, -0.106, 0.021) | (0.519, 0.022, 0.025)→(0.532, -0.108, 0.025) | 0.173→0.055 | 1.00 / 2.333 | 0.383 | 46.780 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.106, 0.021)→(0.496, -0.100, 0.091) | (0.532, -0.108, 0.025)→(0.532, -0.110, 0.025) | 0.055→0.054 | 1.00 / 4.000 | 0.245 | 0.890 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.975
- lateral_force_integral: None
- approach_alignment: 0.715
- goal_progress: 0.857
- terminal_score: 0.857
- phase_score: 0.688
- phase_breakdown.reach_push_goal_score: 0.673
- phase_breakdown.reach_contact_score: 0.724

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.857
- **Median Q (composite search score)**: 0.639
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.297


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11765,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0155,"contact_1.contact_force":5.74046,"contact_1.contact_speed":0.04792,"push_1.push_speed":0.0669,"retract_1.retract_speed":0.04909},"optimized_scores":{"best_composite_score":0.56964,"best_fitness_score":0.62964,"best_task_score":0.5393},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":279.0,"contact_point_centroid":[0.5271,-0.01744,0.04846],"force_p95":30.42569,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.01548,"mean_force":5.84986,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51477,-0.01044,0.026]},{"body_a":"world","body_b":"push_box","contact_count":620.0,"contact_point_centroid":[0.55576,-0.04259,-8e-05],"force_p95":15.90838,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.68491,"mean_force":3.27956,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51201,-0.02756,0.02516]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54101,-0.02609,0.05776],"force_p95":9.2169,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.82634,"mean_force":4.90726,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50883,-0.04526,0.02387]},{"body_a":"world","body_b":"push_box","contact_count":2928.0,"contact_point_centroid":[0.53706,-0.07044,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24882,"mean_force":0.24517,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49602,-0.10237,0.05569]},{"body_a":"world","body_b":"push_box","contact_count":3748.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51474,0.06477,0.20032]},{"body_a":"world","body_b":"push_box","contact_count":3696.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52998,0.09863,0.06343]}],"total_contact_groups":6},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53706,-0.07044,0.02499],"final_tcp_position":[0.49642,-0.09974,0.09067],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":38.01548,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3748.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5314,0.12961,0.10395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":22.61819,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53146,0.07391,0.03428],"tcp_start":[0.5314,0.12961,0.10395],"tcp_to_object_dist_end":0.03845,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.53692,-0.07048,0.02484],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.08768,"object_to_goal_dist_start":0.1905,"object_z_max":0.02931,"peak_contact_force":0.24941,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":911.0,"raw_peak_contact_force":38.01548,"subtask_id":"reach_push_goal","tcp_end":[0.49918,-0.10572,0.02098],"tcp_start":[0.53146,0.07391,0.03428],"tcp_to_object_dist_end":0.05179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.53706,-0.07044,0.02499],"object_pos_start":[0.53692,-0.07048,0.02484],"object_to_goal_dist_end":0.08776,"object_to_goal_dist_start":0.08768,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2928.0,"raw_peak_contact_force":0.24882,"tcp_end":[0.49642,-0.09974,0.09067],"tcp_start":[0.49918,-0.10572,0.02098],"tcp_to_object_dist_end":0.08261,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87938,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07105,"contact_1.contact_force":10.4428,"contact_1.contact_speed":0.01806,"push_1.push_speed":0.04255,"retract_1.retract_speed":0.06948},"optimized_scores":{"best_composite_score":0.69555,"best_fitness_score":0.75555,"best_task_score":0.85673},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":213.0,"contact_point_centroid":[0.50223,-0.05133,0.04171],"force_p95":37.59346,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.85923,"mean_force":6.86927,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49702,-0.03965,0.02701]},{"body_a":"world","body_b":"push_box","contact_count":313.0,"contact_point_centroid":[0.51235,-0.08652,-7e-05],"force_p95":21.04221,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.95961,"mean_force":5.28872,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49731,-0.03317,0.02783]},{"body_a":"world","body_b":"push_box","contact_count":2386.0,"contact_point_centroid":[0.51853,-0.14616,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61187,"mean_force":0.25299,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,-0.10237,0.0565]},{"body_a":"world","body_b":"push_box","contact_count":2792.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49957,0.03738,0.20324]},{"body_a":"world","body_b":"push_box","contact_count":3816.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49903,0.04422,0.06603]}],"total_contact_groups":5},"final_pose_error":0.01042,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5184,-0.14611,0.02499],"final_tcp_position":[0.49625,-0.09978,0.09028],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":51.85923,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2792.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50102,0.07571,0.10749],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":14.99812,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3816.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.49993,0.01819,0.03481],"tcp_start":[0.50102,0.07571,0.10749],"tcp_to_object_dist_end":0.03856,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.51756,-0.14021,0.02542],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.02011,"object_to_goal_dist_start":0.13127,"object_z_max":0.02687,"peak_contact_force":0.15197,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":526.0,"raw_peak_contact_force":51.85923,"subtask_id":"reach_push_goal","tcp_end":[0.49644,-0.10582,0.02154],"tcp_start":[0.49993,0.01819,0.03481],"tcp_to_object_dist_end":0.04054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":612.0,"n_steps_budget":720.0,"object_pos_end":[0.5184,-0.14611,0.02499],"object_pos_start":[0.51756,-0.14021,0.02542],"object_to_goal_dist_end":0.01881,"object_to_goal_dist_start":0.02011,"object_z_max":0.02575,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2386.0,"raw_peak_contact_force":1.61187,"tcp_end":[0.49625,-0.09978,0.09028],"tcp_start":[0.49644,-0.10582,0.02154],"tcp_to_object_dist_end":0.08307,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12295,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05338,"contact_1.contact_force":8.07282,"contact_1.contact_speed":0.03189,"push_1.push_speed":0.06875,"retract_1.retract_speed":0.05664},"optimized_scores":{"best_composite_score":0.63945,"best_fitness_score":0.69945,"best_task_score":0.71798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":302.0,"contact_point_centroid":[0.50985,-0.00918,0.04331],"force_p95":34.64949,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.46572,"mean_force":7.42379,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50299,0.00146,0.02697]},{"body_a":"world","body_b":"push_box","contact_count":541.0,"contact_point_centroid":[0.53251,-0.05514,-9e-05],"force_p95":20.84818,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.82299,"mean_force":4.7834,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50208,-0.01629,0.02606]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53659,-0.05494,0.05613],"force_p95":19.23447,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.35663,"mean_force":7.17551,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49939,-0.06214,0.0233]},{"body_a":"world","body_b":"push_box","contact_count":2896.0,"contact_point_centroid":[0.54142,-0.11237,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.8089,"mean_force":0.24737,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49503,-0.10236,0.05598]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50451,0.06992,0.20038]},{"body_a":"world","body_b":"push_box","contact_count":2840.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50912,0.11044,0.06579]}],"total_contact_groups":6},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54134,-0.11236,0.02499],"final_tcp_position":[0.49632,-0.09974,0.09072],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":50.46572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51093,0.13974,0.10432],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":20.75501,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2840.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.51018,0.08465,0.03501],"tcp_start":[0.51093,0.13974,0.10432],"tcp_to_object_dist_end":0.03862,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.54085,-0.11205,0.02508],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.05576,"object_to_goal_dist_start":0.19823,"object_z_max":0.02814,"peak_contact_force":0.74815,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":846.0,"raw_peak_contact_force":50.46572,"subtask_id":"reach_push_goal","tcp_end":[0.49721,-0.10575,0.0211],"tcp_start":[0.51018,0.08465,0.03501],"tcp_to_object_dist_end":0.04427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":729.0,"n_steps_budget":870.0,"object_pos_end":[0.54134,-0.11236,0.02499],"object_pos_start":[0.54085,-0.11205,0.02508],"object_to_goal_dist_end":0.05591,"object_to_goal_dist_start":0.05576,"object_z_max":0.02508,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2896.0,"raw_peak_contact_force":0.8089,"tcp_end":[0.49632,-0.09974,0.09072],"tcp_start":[0.49721,-0.10575,0.0211],"tcp_to_object_dist_end":0.08067,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```