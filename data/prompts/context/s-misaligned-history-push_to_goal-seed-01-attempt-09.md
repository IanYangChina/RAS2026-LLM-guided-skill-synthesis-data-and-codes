## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.2061 | 0.55 | ✅ accepted |
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | 0.2042 | 0.54 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.3527 | 0.00 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 9  | 0.1999 | 0.52 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3  | 0.2165 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.758, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.216) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: push_goal
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
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_behind_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_object
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
    - 0.025
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_z:
      type: scalar
      range:
      - 0.02
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
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
    push_stroke:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_behind_y: status=consumed; consumers=target.offset.y (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.025], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.216
- **task_score** (E): 0.758
- **fitness_score**: 0.546  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1768 |
| descend_1 | 1.00 | 1.00 | 0.0856 |
| push_1 | 0.67 | 1.00 | 0.1739 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.473, 0.040, 0.134) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.473, 0.040, 0.134)→(0.471, 0.048, 0.049) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.471, 0.048, 0.049)→(0.497, -0.122, 0.046) | (0.474, -0.001, 0.025)→(0.507, -0.125, 0.028) | 0.154→0.043 | 1.00 / 2.333 | 25.631 | 51.616 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.924
- lateral_force_integral: None
- approach_alignment: 0.743
- goal_progress: 0.890
- terminal_score: 0.890
- phase_score: 0.480
- phase_breakdown.push_goal_score: 0.586
- phase_breakdown.reach_object_score: 0.233

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.644
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.890
- **Median Q (composite search score)**: 0.297
- **K-run variance**: 0.0160
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83019,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08133,"approach_1.lateral_behind_y":0.03087,"descend_1.contact_z":0.02009,"descend_1.descend_speed":0.01001,"push_1.push_speed":0.09593,"push_1.push_stroke":0.29813},"optimized_scores":{"best_composite_score":0.03795,"best_fitness_score":0.36795,"best_task_score":0.54745},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":654.0,"contact_point_centroid":[0.50374,-0.00981,0.05222],"force_p95":21.17086,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.94119,"mean_force":6.20576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49423,-0.00224,0.04294]},{"body_a":"world","body_b":"push_box","contact_count":1553.0,"contact_point_centroid":[0.52937,-0.01899,-6e-05],"force_p95":11.4168,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.14083,"mean_force":3.12761,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49444,0.01008,0.04314]},{"body_a":"world","body_b":"push_box","contact_count":2500.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49826,0.03879,0.21552]},{"body_a":"world","body_b":"push_box","contact_count":2632.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49633,0.09003,0.08669]}],"total_contact_groups":4},"final_pose_error":0.15755,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52739,-0.06193,0.02966],"final_tcp_position":[0.49456,-0.08672,0.04357],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":27.94119,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2500.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49813,0.07874,0.13193],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2632.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49731,0.10151,0.04625],"tcp_start":[0.49813,0.07874,0.13193],"tcp_to_object_dist_end":0.05216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52739,-0.06193,0.02966],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.09235,"object_to_goal_dist_start":0.20406,"object_z_max":0.02987,"peak_contact_force":1.05571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2207.0,"raw_peak_contact_force":27.94119,"subtask_id":"push_goal","tcp_end":[0.49456,-0.08672,0.04357],"tcp_start":[0.49731,0.10151,0.04625],"tcp_to_object_dist_end":0.04343,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74153,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.03539,"approach_1.lateral_behind_y":0.0494,"descend_1.contact_z":0.02405,"descend_1.descend_speed":0.0188,"push_1.push_speed":0.09414,"push_1.push_stroke":0.13845},"optimized_scores":{"best_composite_score":0.31399,"best_fitness_score":0.64399,"best_task_score":0.88951},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":847.0,"contact_point_centroid":[0.48984,-0.07868,0.0488],"force_p95":87.04261,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.84379,"mean_force":54.00678,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48541,-0.07151,0.04936]},{"body_a":"world","body_b":"push_box","contact_count":1934.0,"contact_point_centroid":[0.48726,-0.09378,-0.00023],"force_p95":62.64432,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.58402,"mean_force":24.11637,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48294,-0.05927,0.04947]},{"body_a":"world","body_b":"push_box","contact_count":2296.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4848,0.01122,0.21776]},{"body_a":"world","body_b":"push_box","contact_count":2236.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46785,0.02411,0.09241]}],"total_contact_groups":4},"final_pose_error":0.01642,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48856,-0.14213,0.02823],"final_tcp_position":[0.50254,-0.14278,0.05058],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":102.84379,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47065,0.02305,0.13467],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46768,0.02534,0.0523],"tcp_start":[0.47065,0.02305,0.13467],"tcp_to_object_dist_end":0.05667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48856,-0.14213,0.02823],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01426,"object_to_goal_dist_start":0.12903,"object_z_max":0.03462,"peak_contact_force":74.26565,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2781.0,"raw_peak_contact_force":102.84379,"subtask_id":"push_goal","tcp_end":[0.50254,-0.14278,0.05058],"tcp_start":[0.46768,0.02534,0.0523],"tcp_to_object_dist_end":0.02637,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02151,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15042,"approach_1.lateral_behind_y":0.05206,"descend_1.contact_z":0.02058,"descend_1.descend_speed":0.07752,"push_1.push_speed":0.08385,"push_1.push_stroke":0.12918},"optimized_scores":{"best_composite_score":0.29746,"best_fitness_score":0.62746,"best_task_score":0.83638},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":683.0,"contact_point_centroid":[0.47265,-0.07901,0.04802],"force_p95":18.18149,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.06175,"mean_force":6.78811,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47071,-0.0672,0.04549]},{"body_a":"world","body_b":"push_box","contact_count":1422.0,"contact_point_centroid":[0.4765,-0.10664,-4e-05],"force_p95":10.03323,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.63598,"mean_force":3.72636,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46616,-0.05189,0.04585]},{"body_a":"world","body_b":"push_box","contact_count":1988.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47543,0.00915,0.21761]},{"body_a":"world","body_b":"push_box","contact_count":1892.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44785,0.01847,0.0909]}],"total_contact_groups":4},"final_pose_error":0.01668,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50593,-0.17009,0.02665],"final_tcp_position":[0.49262,-0.1367,0.04514],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":24.06175,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":780.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45124,0.01877,0.13454],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":720.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.44681,0.01826,0.04912],"tcp_start":[0.45124,0.01877,0.13454],"tcp_to_object_dist_end":0.05548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,-0.17009,0.02665],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.02101,"object_to_goal_dist_start":0.12843,"object_z_max":0.02684,"peak_contact_force":1.57303,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2105.0,"raw_peak_contact_force":24.06175,"subtask_id":"push_goal","tcp_end":[0.49262,-0.1367,0.04514],"tcp_start":[0.44681,0.01826,0.04912],"tcp_to_object_dist_end":0.04043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```