## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.5549 | 0.48 | ❌ rejected |
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4863 | 0.50 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3469 | 0.65 | ✅ accepted |
| 0 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.4974 | 0.27 | ✅ accepted |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.555) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.1
  weight: 0.3
- id: push_to_goal
  weight: 0.7
phases:
- id: approach_lateral
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
    - 0.04
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    approach_y_offset:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset.y
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_pre_contact
- id: push_to_goal
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
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.15
    - 0.3
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_lateral** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.04, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.04, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **retract** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.15, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.555
- **task_score** (E): 0.484
- **fitness_score**: 0.615  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1548 |
| descend_contact | 1.00 | 1.00 | 0.1069 |
| push_to_goal | 1.00 | 1.00 | 0.1907 |
| retract | 1.00 | 1.00 | 0.2005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.002, 0.154) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_contact | descend | 1.00 / force_exceeded | (0.509, 0.002, 0.154)→(0.509, 0.032, 0.052) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.509, 0.032, 0.052)→(0.496, -0.150, 0.023) | (0.513, 0.002, 0.025)→(0.536, -0.075, 0.025) | 0.160→0.084 | 1.00 / 4.000 | 0.282 | 131.775 |
| retract | retract | 1.00 / step_budget | (0.496, -0.150, 0.023)→(0.496, -0.150, 0.223) | (0.536, -0.075, 0.025)→(0.536, -0.075, 0.025) | 0.084→0.084 | 1.00 / 4.000 | 0.245 | 0.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.675
- lateral_force_integral: None
- approach_alignment: 0.911
- goal_progress: 0.583
- terminal_score: 0.583
- phase_score: 0.742
- phase_breakdown.push_to_goal_score: 0.964
- phase_breakdown.reach_pre_contact_score: 0.223

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.678
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.583
- **Median Q (composite search score)**: 0.540
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.389


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
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57396,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_z_offset":0.09518,"descend_contact.contact_force_threshold":8.33782,"descend_contact.contact_y_offset":0.02485,"push_to_goal.push_extension":0.02062,"push_to_goal.push_speed":0.05685},"optimized_scores":{"best_composite_score":0.61827,"best_fitness_score":0.67827,"best_task_score":0.58264},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":408.0,"contact_point_centroid":[0.47806,-0.05275,0.04717],"force_p95":177.39651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.93571,"mean_force":142.42114,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47285,-0.06113,0.04696]},{"body_a":"world","body_b":"push_box","contact_count":853.0,"contact_point_centroid":[0.48496,-0.0583,-0.00073],"force_p95":169.21999,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":181.97701,"mean_force":68.9198,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47485,-0.07079,0.04399]},{"body_a":"world","body_b":"push_box","contact_count":912.0,"contact_point_centroid":[0.50736,-0.09691,-4e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33452,"mean_force":0.24424,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49712,-0.15098,0.1189]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.47524,-0.01424,0.21502]},{"body_a":"world","body_b":"push_box","contact_count":1708.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.44793,-0.02131,0.09003]}],"total_contact_groups":5},"final_pose_error":0.04919,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50736,-0.09691,0.02499],"final_tcp_position":[0.49849,-0.151,0.22505],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.45114,-0.02911,0.12967],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":427.0,"n_steps_budget":690.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.44704,-0.01336,0.05237],"tcp_start":[0.45114,-0.02911,0.12967],"tcp_to_object_dist_end":0.03305,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50737,-0.09698,0.02403],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.05354,"object_to_goal_dist_start":0.12843,"object_z_max":0.03536,"peak_contact_force":0.3561,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1261.0,"raw_peak_contact_force":186.93571,"subtask_id":"push_to_goal","tcp_end":[0.49894,-0.15126,0.02423],"tcp_start":[0.44704,-0.01336,0.05237],"tcp_to_object_dist_end":0.05493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,-0.09691,0.02499],"object_pos_start":[0.50737,-0.09698,0.02403],"object_to_goal_dist_end":0.0536,"object_to_goal_dist_start":0.05354,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":912.0,"raw_peak_contact_force":0.33452,"tcp_end":[0.49849,-0.151,0.22505],"tcp_start":[0.49894,-0.15126,0.02423],"tcp_to_object_dist_end":0.20743,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4686,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_z_offset":0.14685,"descend_contact.contact_force_threshold":10.91103,"descend_contact.contact_y_offset":0.04308,"push_to_goal.push_extension":0.02002,"push_to_goal.push_speed":0.04363},"optimized_scores":{"best_composite_score":0.54006,"best_fitness_score":0.60006,"best_task_score":0.47433},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":594.0,"contact_point_centroid":[0.54615,-0.01931,0.04782],"force_p95":160.71404,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.4197,"mean_force":118.14366,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53629,-0.02224,0.04843]},{"body_a":"world","body_b":"push_box","contact_count":2113.0,"contact_point_centroid":[0.54609,-0.032,-0.00038],"force_p95":103.16132,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.1618,"mean_force":33.59706,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53072,-0.03561,0.04447]},{"body_a":"world","body_b":"push_box","contact_count":1792.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.52151,0.00057,0.23869]},{"body_a":"world","body_b":"push_box","contact_count":2748.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.54514,0.01832,0.11132]},{"body_a":"world","body_b":"push_box","contact_count":908.0,"contact_point_centroid":[0.53798,-0.07471,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24524,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49297,-0.14913,0.11698]}],"total_contact_groups":5},"final_pose_error":0.04988,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53798,-0.07471,0.02499],"final_tcp_position":[0.49436,-0.14908,0.22279],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":870.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1792.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54543,0.00117,0.17784],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":687.0,"n_steps_budget":990.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2748.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.54742,0.03493,0.05173],"tcp_start":[0.54543,0.00117,0.17784],"tcp_to_object_dist_end":0.0433,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.53798,-0.07471,0.02498],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.08433,"object_to_goal_dist_start":0.16043,"object_z_max":0.03507,"peak_contact_force":0.24513,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2707.0,"raw_peak_contact_force":162.4197,"subtask_id":"push_to_goal","tcp_end":[0.49482,-0.14931,0.02267],"tcp_start":[0.54742,0.03493,0.05173],"tcp_to_object_dist_end":0.08622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.53798,-0.07471,0.02499],"object_pos_start":[0.53798,-0.07471,0.02498],"object_to_goal_dist_end":0.08433,"object_to_goal_dist_start":0.08433,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":908.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49436,-0.14908,0.22279],"tcp_start":[0.49482,-0.14931,0.02267],"tcp_to_object_dist_end":0.21577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43043,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_z_offset":0.12247,"descend_contact.contact_force_threshold":9.93162,"descend_contact.contact_y_offset":0.04962,"push_to_goal.push_extension":0.02034,"push_to_goal.push_speed":0.02423},"optimized_scores":{"best_composite_score":0.50639,"best_fitness_score":0.56639,"best_task_score":0.39611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":151.0,"contact_point_centroid":[0.52608,0.00612,0.04981],"force_p95":35.95092,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.97084,"mean_force":10.40072,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52,0.01686,0.04064]},{"body_a":"world","body_b":"push_box","contact_count":1482.0,"contact_point_centroid":[0.55757,-0.04542,-7e-05],"force_p95":7.82588,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.96827,"mean_force":1.39585,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50689,-0.06981,0.03077]},{"body_a":"world","body_b":"push_box","contact_count":2032.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51418,0.01651,0.22718]},{"body_a":"world","body_b":"push_box","contact_count":2568.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.52951,0.05366,0.09975]},{"body_a":"world","body_b":"push_box","contact_count":908.0,"contact_point_centroid":[0.56168,-0.05289,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49322,-0.15015,0.1165]}],"total_contact_groups":5},"final_pose_error":0.04959,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.56168,-0.05289,0.02499],"final_tcp_position":[0.49457,-0.15013,0.22236],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.53059,0.03373,0.15456],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":642.0,"n_steps_budget":900.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2568.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.53119,0.07329,0.0507],"tcp_start":[0.53059,0.03373,0.15456],"tcp_to_object_dist_end":0.04484,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.56168,-0.05289,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.11504,"object_to_goal_dist_start":0.1905,"object_z_max":0.02708,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1633.0,"raw_peak_contact_force":45.97084,"subtask_id":"push_to_goal","tcp_end":[0.49503,-0.15033,0.02194],"tcp_start":[0.53119,0.07329,0.0507],"tcp_to_object_dist_end":0.11809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.56168,-0.05289,0.02499],"object_pos_start":[0.56168,-0.05289,0.02499],"object_to_goal_dist_end":0.11504,"object_to_goal_dist_start":0.11504,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":908.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49457,-0.15013,0.22236],"tcp_start":[0.49503,-0.15033,0.02194],"tcp_to_object_dist_end":0.23003,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```