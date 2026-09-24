## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3876 | 0.66 | ❌ rejected |
| 13 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2800 | 0.00 | ❌ rejected |
| 12 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | force_exceeded | 9 | 0.3584 | 0.43 | ❌ rejected |
| 11 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | force_threshold_switch | pose_tolerance | force_exceeded | force_exceeded | force_exceeded | 10 | 0.5682 | 0.28 | ❌ rejected |
| 10 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.7412 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.45027790005723495, -0.03158273920846803, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.45027790005723495, -0.03158273920846803, 0.025]
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.945, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.388) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_object
  anchor: object
  metric: contact
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
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
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
    approach_standoff:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: contact_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_lateral_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.01
      binds_to:
      - path: retry.offset.x
        mode: replace
      - path: retry.offset.y
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: contact_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: -0.12
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_offset:
      type: scalar
      range:
      - -0.25
      - -0.05
      default: -0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: -0.01
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_fine_offset:
      type: scalar
      range:
      - -0.03
      - -0.005
      default: -0.01
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_fine_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_standoff: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_lateral_offset: status=consumed; consumers=retry.offset.x (replace), retry.offset.y (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=-0.12, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **push_2** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=-0.01, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_fine_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_fine_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.388
- **task_score** (E): 0.661
- **fitness_score**: 0.748  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1769 |
| descend_1 | 1.00 | 1.00 | 0.1696 |
| push_1 | 1.00 | 1.00 | 0.0962 |
| push_2 | 1.00 | 1.00 | 0.1761 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.110, 0.170) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.110, 0.170)→(0.528, -0.008, 0.045) | (0.513, 0.002, 0.025)→(0.518, 0.006, 0.024) | 0.160→0.164 | 1.00 / 3.667 | 240.216 | 250.702 |
| push_1 | push | 1.00 / step_budget | (0.528, -0.008, 0.045)→(0.537, 0.080, 0.037) | (0.518, 0.006, 0.024)→(0.528, 0.035, 0.034) | 0.164→0.199 | 1.00 / 2.333 | 71.277 | 193.613 |
| push_2 | push | 1.00 / step_budget | (0.537, 0.080, 0.037)→(0.506, -0.084, 0.023) | (0.528, 0.035, 0.034)→(0.488, -0.095, 0.025) | 0.199→0.057 | 1.00 / 1.333 | 0.604 | 80.723 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.761
- lateral_force_integral: None
- approach_alignment: 0.618
- goal_progress: 0.746
- terminal_score: 0.746
- phase_score: 0.872
- phase_breakdown.push_to_goal_score: 0.818
- phase_breakdown.contact_object_score: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.822
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.746
- **Median Q (composite search score)**: 0.434
- **K-run variance**: 0.0074
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.306


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45028,-0.03158,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07759,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0934,"approach_1.approach_standoff":0.09913,"push_1.push_offset":0.24122,"push_1.push_speed":0.15876,"push_2.push_fine_offset":0.05042,"push_2.push_fine_speed":0.16768},"optimized_scores":{"best_composite_score":0.46206,"best_fitness_score":0.82206,"best_task_score":0.7464},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":178.0,"contact_point_centroid":[0.47223,-0.04507,0.0468],"force_p95":252.05014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":258.0847,"mean_force":187.16184,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46329,-0.04973,0.04678]},{"body_a":"attachment","body_b":"push_box","contact_count":398.0,"contact_point_centroid":[0.4679,-0.00753,0.04715],"force_p95":161.12701,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.24621,"mean_force":138.44261,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46483,0.0024,0.04597]},{"body_a":"world","body_b":"push_box","contact_count":1709.0,"contact_point_centroid":[0.45388,-0.03192,-0.00017],"force_p95":126.2449,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":156.7228,"mean_force":19.8298,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46902,-0.07735,0.07667]},{"body_a":"world","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.4563,-0.00206,-0.00058],"force_p95":112.21917,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.16148,"mean_force":59.38672,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46353,0.00364,0.04529]},{"body_a":"attachment","body_b":"push_box","contact_count":254.0,"contact_point_centroid":[0.45306,-0.02283,0.03818],"force_p95":33.51596,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.96028,"mean_force":4.52647,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.45031,-0.01126,0.02494]},{"body_a":"world","body_b":"push_box","contact_count":373.0,"contact_point_centroid":[0.46257,-0.05656,-9e-05],"force_p95":18.00637,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.49915,"mean_force":3.58149,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.44969,-0.00928,0.02502]},{"body_a":"world","body_b":"push_box","contact_count":2852.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49226,-0.05726,0.21101]}],"total_contact_groups":7},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49662,-0.11762,0.026],"final_tcp_position":[0.47404,-0.08537,0.02286],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":258.0847,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2852.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.48613,-0.1153,0.12417],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":488.0,"n_steps_budget":840.0,"object_pos_end":[0.45422,-0.02661,0.02509],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.13161,"object_to_goal_dist_start":0.12843,"object_z_max":0.02614,"peak_contact_force":247.95225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1887.0,"raw_peak_contact_force":258.0847,"subtask_id":"contact_object","tcp_end":[0.47195,-0.0413,0.04348],"tcp_start":[0.48613,-0.1153,0.12417],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":436.0,"n_steps_budget":600.0,"object_pos_end":[0.43848,0.01777,0.0314],"object_pos_start":[0.45422,-0.02661,0.02509],"object_to_goal_dist_end":0.17881,"object_to_goal_dist_start":0.13161,"object_z_max":0.03579,"peak_contact_force":0.45604,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1335.0,"raw_peak_contact_force":174.24621,"subtask_id":"push_to_goal","tcp_end":[0.42893,0.0617,0.02941],"tcp_start":[0.47195,-0.0413,0.04348],"tcp_to_object_dist_end":0.045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":366.0,"n_steps_budget":660.0,"object_pos_end":[0.49662,-0.11762,0.026],"object_pos_start":[0.43848,0.01777,0.0314],"object_to_goal_dist_end":0.03257,"object_to_goal_dist_start":0.17881,"object_z_max":0.0314,"peak_contact_force":0.27495,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":627.0,"raw_peak_contact_force":46.96028,"subtask_id":"push_to_goal","tcp_end":[0.47404,-0.08537,0.02286],"tcp_start":[0.42893,0.0617,0.02941],"tcp_to_object_dist_end":0.0395,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55317,0.00136,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92405,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16567,"approach_1.approach_standoff":0.19102,"push_1.push_offset":0.24688,"push_1.push_speed":0.15512,"push_2.push_fine_offset":0.04857,"push_2.push_fine_speed":0.0959},"optimized_scores":{"best_composite_score":0.43405,"best_fitness_score":0.79405,"best_task_score":0.71991},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":219.0,"contact_point_centroid":[0.56097,-0.01904,0.04699],"force_p95":243.69021,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.8671,"mean_force":185.84291,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54984,-0.02264,0.04741]},{"body_a":"attachment","body_b":"push_box","contact_count":453.0,"contact_point_centroid":[0.58498,0.01941,0.04651],"force_p95":199.08669,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":210.10471,"mean_force":176.39447,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.58604,0.02864,0.04464]},{"body_a":"world","body_b":"push_box","contact_count":827.0,"contact_point_centroid":[0.58439,0.02167,-0.00095],"force_p95":183.84979,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":194.09423,"mean_force":97.46517,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5844,0.02477,0.04494]},{"body_a":"world","body_b":"push_box","contact_count":3857.0,"contact_point_centroid":[0.55461,0.00096,-0.0001],"force_p95":74.31171,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.37782,"mean_force":10.87558,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51826,-0.08513,0.1053]},{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.5522,-0.02632,0.02847],"force_p95":22.81888,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.67874,"mean_force":5.75729,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.55907,-0.01676,0.02788]},{"body_a":"world","body_b":"push_box","contact_count":528.0,"contact_point_centroid":[0.5464,-0.03815,-0.00029],"force_p95":9.58853,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.84333,"mean_force":2.67779,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.56674,-0.00052,0.02946]},{"body_a":"world","body_b":"push_box","contact_count":3176.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49285,-0.08513,0.2435]}],"total_contact_groups":7},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49367,-0.10551,0.02512],"final_tcp_position":[0.52638,-0.08779,0.02306],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":244.8671,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3176.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.48763,-0.16929,0.19103],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.24696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55952,0.0064,0.024],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16734,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":235.41126,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4076.0,"raw_peak_contact_force":244.8671,"subtask_id":"contact_object","tcp_end":[0.56335,-0.01187,0.04508],"tcp_start":[0.48763,-0.16929,0.19103],"tcp_to_object_dist_end":0.02816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":453.0,"n_steps_budget":600.0,"object_pos_end":[0.58953,0.02972,0.03318],"object_pos_start":[0.55952,0.0064,0.024],"object_to_goal_dist_end":0.20095,"object_to_goal_dist_start":0.16734,"object_z_max":0.03399,"peak_contact_force":97.98741,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1280.0,"raw_peak_contact_force":210.10471,"subtask_id":"push_to_goal","tcp_end":[0.60459,0.075,0.03961],"tcp_start":[0.56335,-0.01187,0.04508],"tcp_to_object_dist_end":0.04815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.49367,-0.10551,0.02512],"object_pos_start":[0.58953,0.02972,0.03318],"object_to_goal_dist_end":0.04493,"object_to_goal_dist_start":0.20095,"object_z_max":0.03318,"peak_contact_force":0.0,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":724.0,"raw_peak_contact_force":85.67874,"subtask_id":"push_to_goal","tcp_end":[0.52638,-0.08779,0.02306],"tcp_start":[0.60459,0.075,0.03961],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.5366,0.03695,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68462,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16241,"approach_1.approach_standoff":0.09069,"push_1.push_offset":0.25847,"push_1.push_speed":0.05332,"push_2.push_fine_offset":0.05441,"push_2.push_fine_speed":0.1291},"optimized_scores":{"best_composite_score":0.26671,"best_fitness_score":0.62671,"best_task_score":0.51573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.54972,0.02608,0.0469],"force_p95":247.8921,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":249.15372,"mean_force":204.09117,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53791,0.02532,0.04734]},{"body_a":"attachment","body_b":"push_box","contact_count":568.0,"contact_point_centroid":[0.56622,0.05854,0.04594],"force_p95":195.94116,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.489,"mean_force":180.75966,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56472,0.06868,0.04448]},{"body_a":"world","body_b":"push_box","contact_count":1035.0,"contact_point_centroid":[0.56493,0.05235,-0.001],"force_p95":185.43513,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.62172,"mean_force":100.01395,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56365,0.06566,0.04472]},{"body_a":"world","body_b":"push_box","contact_count":2590.0,"contact_point_centroid":[0.53784,0.03627,-0.0001],"force_p95":95.67524,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":158.54587,"mean_force":11.33373,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52334,-0.00647,0.10869]},{"body_a":"attachment","body_b":"push_box","contact_count":202.0,"contact_point_centroid":[0.53882,0.00932,0.0355],"force_p95":105.1453,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.53023,"mean_force":18.64786,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.54678,0.01681,0.0312]},{"body_a":"world","body_b":"push_box","contact_count":683.0,"contact_point_centroid":[0.51745,-0.01467,-0.00045],"force_p95":14.89363,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.2345,"mean_force":5.99425,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.54407,0.0086,0.03039]},{"body_a":"world","body_b":"push_box","contact_count":1568.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50629,-0.02259,0.24699]}],"total_contact_groups":7},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4751,-0.06117,0.02504],"final_tcp_position":[0.51647,-0.07835,0.02423],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":249.15372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":810.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.51448,-0.04652,0.19395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.54159,0.03922,0.02385],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19374,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":237.28583,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2730.0,"raw_peak_contact_force":249.15372,"subtask_id":"contact_object","tcp_end":[0.5474,0.03027,0.04514],"tcp_start":[0.51448,-0.04652,0.19395],"tcp_to_object_dist_end":0.02381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":568.0,"n_steps_budget":900.0,"object_pos_end":[0.5556,0.05817,0.03629],"object_pos_start":[0.54159,0.03922,0.02385],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.19374,"object_z_max":0.03622,"peak_contact_force":115.38849,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1603.0,"raw_peak_contact_force":196.489,"subtask_id":"push_to_goal","tcp_end":[0.57662,0.10432,0.04063],"tcp_start":[0.5474,0.03027,0.04514],"tcp_to_object_dist_end":0.0509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.4751,-0.06117,0.02504],"object_pos_start":[0.5556,0.05817,0.03629],"object_to_goal_dist_end":0.09226,"object_to_goal_dist_start":0.21576,"object_z_max":0.03645,"peak_contact_force":1.53701,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":885.0,"raw_peak_contact_force":109.53023,"subtask_id":"push_to_goal","tcp_end":[0.51647,-0.07835,0.02423],"tcp_start":[0.57662,0.10432,0.04063],"tcp_to_object_dist_end":0.0448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```