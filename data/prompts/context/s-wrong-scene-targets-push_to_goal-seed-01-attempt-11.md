## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1419 | 0.44 | ❌ rejected |
| 10 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0457 | 0.66 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3866 | 0.81 | ✅ accepted |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2024 | 0.73 | ✅ accepted |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2042 | 0.54 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5014185949640309, 0.05405564355911223, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5014185949640309, 0.05405564355911223, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.806, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.142) — your mutation base

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
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: align_behind
  type: align
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    behind_distance:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - -0.01
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retrieve
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.03
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **align_behind** (`align`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[-0.01, 0.0, 0.0]
- **retrieve** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.142
- **task_score** (E): 0.437
- **fitness_score**: 0.452  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2018 |
| align_behind | 1.00 | 1.00 | 0.0673 |
| push_to_goal | 1.00 | 1.00 | 0.1277 |
| retrieve | 1.00 | 1.00 | 0.0604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, -0.000, 0.104) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind | align | 1.00 / step_budget | (0.474, -0.000, 0.104)→(0.495, -0.019, 0.043) | (0.474, -0.001, 0.025)→(0.480, -0.006, 0.025) | 0.154→0.147 | 1.00 / 3.000 | 252.275 | 276.747 |
| push_to_goal | push | 1.00 / step_budget | (0.495, -0.019, 0.043)→(0.503, -0.143, 0.022) | (0.480, -0.006, 0.025)→(0.505, -0.060, 0.025) | 0.147→0.091 | 1.00 / 4.000 | 0.319 | 185.905 |
| retrieve | retract | 1.00 / step_budget | (0.503, -0.143, 0.022)→(0.498, -0.148, 0.077) | (0.505, -0.060, 0.025)→(0.505, -0.060, 0.025) | 0.091→0.091 | 1.00 / 4.000 | 0.245 | 0.301 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.603
- lateral_force_integral: None
- approach_alignment: 0.773
- goal_progress: 0.557
- terminal_score: 0.557
- phase_score: 0.468
- phase_breakdown.push_to_goal_score: 0.516
- phase_breakdown.reach_object_score: 0.354

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.503
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.557
- **Median Q (composite search score)**: 0.181
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.420


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50142,0.05406,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09005,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.arc_height":0.05263,"align_behind.behind_distance":0.02025,"approach_object.approach_z_offset":0.04161,"push_to_goal.push_distance":0.16563,"push_to_goal.push_speed":0.01621},"optimized_scores":{"best_composite_score":0.05127,"best_fitness_score":0.36127,"best_task_score":0.27422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":103.0,"contact_point_centroid":[0.51796,0.05095,0.04617],"force_p95":275.24002,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":276.77351,"mean_force":248.21898,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50625,0.04923,0.04607]},{"body_a":"world","body_b":"push_box","contact_count":604.0,"contact_point_centroid":[0.50578,0.05134,-0.00036],"force_p95":156.78088,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.02657,"mean_force":42.82385,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.5016,0.05102,0.05728]},{"body_a":"attachment","body_b":"push_box","contact_count":252.0,"contact_point_centroid":[0.5247,0.025,0.04642],"force_p95":155.60799,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.44019,"mean_force":127.06891,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51766,0.01629,0.04589]},{"body_a":"world","body_b":"push_box","contact_count":1057.0,"contact_point_centroid":[0.50589,0.01228,-0.00044],"force_p95":140.73506,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.41378,"mean_force":30.76544,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50955,-0.02854,0.03574]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49857,0.02354,0.19384]},{"body_a":"world","body_b":"push_box","contact_count":544.0,"contact_point_centroid":[0.5014,-0.0019,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.49702,-0.11465,0.04916]}],"total_contact_groups":6},"final_pose_error":0.02956,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5014,-0.0019,0.02499],"final_tcp_position":[0.49692,-0.13546,0.07945],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":276.77351,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49835,0.0483,0.08548],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":173.0,"n_steps_budget":600.0,"object_pos_end":[0.50654,0.05117,0.02458],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20128,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":239.00473,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":707.0,"raw_peak_contact_force":276.77351,"tcp_end":[0.51509,0.04416,0.04471],"tcp_start":[0.49835,0.0483,0.08548],"tcp_to_object_dist_end":0.02297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.5014,-0.0019,0.02499],"object_pos_start":[0.50654,0.05117,0.02458],"object_to_goal_dist_end":0.1481,"object_to_goal_dist_start":0.20128,"object_z_max":0.03527,"peak_contact_force":0.24523,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1309.0,"raw_peak_contact_force":156.44019,"subtask_id":"push_to_goal","tcp_end":[0.49924,-0.0948,0.02261],"tcp_start":[0.51509,0.04416,0.04471],"tcp_to_object_dist_end":0.09295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":136.0,"n_steps_budget":630.0,"object_pos_end":[0.5014,-0.0019,0.02499],"object_pos_start":[0.5014,-0.0019,0.02499],"object_to_goal_dist_end":0.1481,"object_to_goal_dist_start":0.1481,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":544.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49692,-0.13546,0.07945],"tcp_start":[0.49924,-0.0948,0.02261],"tcp_to_object_dist_end":0.14431,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47139,-0.02418,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15084,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.arc_height":0.11149,"align_behind.behind_distance":0.04416,"approach_object.approach_z_offset":0.08246,"push_to_goal.push_distance":0.14933,"push_to_goal.push_speed":0.02754},"optimized_scores":{"best_composite_score":0.19334,"best_fitness_score":0.50334,"best_task_score":0.55698},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":144.0,"contact_point_centroid":[0.49434,-0.03335,0.04613],"force_p95":260.40248,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":261.28983,"mean_force":240.97768,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48817,-0.04135,0.04511]},{"body_a":"world","body_b":"push_box","contact_count":928.0,"contact_point_centroid":[0.47912,-0.02556,-0.00033],"force_p95":205.47229,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.58374,"mean_force":38.02402,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.47794,-0.02583,0.07489]},{"body_a":"world","body_b":"push_box","contact_count":360.0,"contact_point_centroid":[0.50146,-0.0656,-0.00074],"force_p95":168.53327,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.20692,"mean_force":42.54655,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50184,-0.10915,0.03417]},{"body_a":"attachment","body_b":"push_box","contact_count":132.0,"contact_point_centroid":[0.50261,-0.06275,0.04477],"force_p95":176.85134,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.41965,"mean_force":112.70358,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50368,-0.07426,0.04342]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.49783,-0.07623,0.08322],"force_p95":7.4488,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.51182,"mean_force":3.43927,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50051,-0.12116,0.03027]},{"body_a":"world","body_b":"push_box","contact_count":440.0,"contact_point_centroid":[0.50725,-0.0933,-7e-05],"force_p95":0.25546,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41299,"mean_force":0.24438,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.4982,-0.15747,0.04644]},{"body_a":"world","body_b":"push_box","contact_count":1352.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48605,-0.01022,0.21486]}],"total_contact_groups":7},"final_pose_error":0.02984,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50725,-0.0933,0.02499],"final_tcp_position":[0.49751,-0.15284,0.0754],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":261.28983,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":338.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.4723,-0.02114,0.12683],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":300.0,"n_steps_budget":720.0,"object_pos_end":[0.47746,-0.03398,0.02558],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.11819,"object_to_goal_dist_start":0.12903,"object_z_max":0.02602,"peak_contact_force":249.69074,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1072.0,"raw_peak_contact_force":261.28983,"tcp_end":[0.49823,-0.05497,0.04244],"tcp_start":[0.4723,-0.02114,0.12683],"tcp_to_object_dist_end":0.034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50737,-0.09331,0.02417],"object_pos_start":[0.47746,-0.03398,0.02558],"object_to_goal_dist_end":0.05717,"object_to_goal_dist_start":0.11819,"object_z_max":0.04321,"peak_contact_force":0.46637,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":528.0,"raw_peak_contact_force":183.20692,"subtask_id":"push_to_goal","tcp_end":[0.50131,-0.16144,0.02247],"tcp_start":[0.49823,-0.05497,0.04244],"tcp_to_object_dist_end":0.06842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":110.0,"n_steps_budget":600.0,"object_pos_end":[0.50725,-0.0933,0.02499],"object_pos_start":[0.50737,-0.09331,0.02417],"object_to_goal_dist_end":0.05716,"object_to_goal_dist_start":0.05717,"object_z_max":0.02499,"peak_contact_force":0.24524,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":440.0,"raw_peak_contact_force":0.41299,"tcp_end":[0.49751,-0.15284,0.0754],"tcp_start":[0.50131,-0.16144,0.02247],"tcp_to_object_dist_end":0.07862,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45028,-0.03158,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20513,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.arc_height":0.14414,"align_behind.behind_distance":0.02652,"approach_object.approach_z_offset":0.05622,"push_to_goal.push_distance":0.16683,"push_to_goal.push_speed":0.02839},"optimized_scores":{"best_composite_score":0.18119,"best_fitness_score":0.49119,"best_task_score":0.48052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.47133,-0.03571,0.04663],"force_p95":290.80685,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":292.17762,"mean_force":249.88185,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.46343,-0.04187,0.04602]},{"body_a":"attachment","body_b":"push_box","contact_count":187.0,"contact_point_centroid":[0.4832,-0.06034,0.04569],"force_p95":200.95794,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.06794,"mean_force":128.59508,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48514,-0.07157,0.04403]},{"body_a":"world","body_b":"push_box","contact_count":578.0,"contact_point_centroid":[0.45664,-0.03235,-0.00026],"force_p95":182.51217,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":202.45083,"mean_force":34.08531,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.45607,-0.03335,0.06769]},{"body_a":"world","body_b":"push_box","contact_count":848.0,"contact_point_centroid":[0.49791,-0.07244,-0.00047],"force_p95":169.53477,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.38271,"mean_force":28.89787,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49513,-0.12373,0.03158]},{"body_a":"world","body_b":"push_box","contact_count":1580.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47646,-0.01369,0.20134]},{"body_a":"world","body_b":"push_box","contact_count":452.0,"contact_point_centroid":[0.50492,-0.08346,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24524,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.50238,-0.16566,0.04637]}],"total_contact_groups":6},"final_pose_error":0.03,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50492,-0.08346,0.02499],"final_tcp_position":[0.49948,-0.15647,0.07571],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":292.17762,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45285,-0.02814,0.10031],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":180.0,"n_steps_budget":600.0,"object_pos_end":[0.45605,-0.03566,0.0258],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.1225,"object_to_goal_dist_start":0.12843,"object_z_max":0.02633,"peak_contact_force":268.13019,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":656.0,"raw_peak_contact_force":292.17762,"tcp_end":[0.47186,-0.0473,0.04326],"tcp_start":[0.45285,-0.02814,0.10031],"tcp_to_object_dist_end":0.02628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50492,-0.08346,0.02499],"object_pos_start":[0.45605,-0.03566,0.0258],"object_to_goal_dist_end":0.06672,"object_to_goal_dist_start":0.1225,"object_z_max":0.0353,"peak_contact_force":0.24522,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1035.0,"raw_peak_contact_force":218.06794,"subtask_id":"push_to_goal","tcp_end":[0.50729,-0.17389,0.0216],"tcp_start":[0.47186,-0.0473,0.04326],"tcp_to_object_dist_end":0.09052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.50492,-0.08346,0.02499],"object_pos_start":[0.50492,-0.08346,0.02499],"object_to_goal_dist_end":0.06672,"object_to_goal_dist_start":0.06672,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":452.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49948,-0.15647,0.07571],"tcp_start":[0.50729,-0.17389,0.0216],"tcp_to_object_dist_end":0.08906,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```