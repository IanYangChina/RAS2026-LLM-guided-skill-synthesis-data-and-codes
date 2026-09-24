## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2344 | 0.03 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1404 | 0.11 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3360 | 0.32 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | time_limit | force_exceeded | pose_tolerance | 9 | 0.1497 | 0.06 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1753 | 0.33 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.234) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_progress
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
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
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
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_peg
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_progress
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_peg, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.234
- **task_score** (E): 0.032
- **fitness_score**: 0.059  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_align | 1.00 | 1.00 | 0.1788 |
| descend_align | 0.67 | 1.00 | 0.0930 |
| push_through | 0.00 | 1.00 | 0.0001 |
| retract_after | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_align | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.139, 0.136) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.549 | 3.954 |
| descend_align | descend | 0.67 / force_exceeded | (0.506, 0.139, 0.136)→(0.501, 0.088, 0.062) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.667 | 12.968 | 12.972 |
| push_through | push | 0.00 / guard_failure | (0.501, 0.071, 0.059)→(0.501, 0.071, 0.059) | (0.502, 0.082, 0.034)→(0.502, 0.076, 0.036) | 0.162→0.156 | 1.00 / 2.000 | 21.918 | 58.220 |
| retract_after | retract | 1.00 / step_budget | (0.501, 0.071, 0.059)→(0.499, 0.071, 0.140) | (0.502, 0.075, 0.036)→(0.501, 0.066, 0.031) | 0.156→0.147 | 1.00 / 1.333 | 0.573 | 39.023 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.005
- alignment_error: None
- force_efficiency: 0.066
- terminal_score: 0.003
- phase_score: 0.050
- phase_breakdown.reach_peg_score: 0.161
- phase_breakdown.push_progress_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.116
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.092
- **Median Q (composite search score)**: -0.180
- **K-run variance**: 0.0060
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: descend_align.speed
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9434,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.13209,"approach_align.speed":0.04353,"descend_align.contact_force":3.68015,"descend_align.speed":0.05083,"push_through.lateral_adjust":0.00263,"push_through.push_distance":0.17025,"push_through.speed":0.02705,"retract_after.speed":0.04148},"optimized_scores":{"best_composite_score":-0.34437,"best_fitness_score":0.11563,"best_task_score":0.09245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,0.0066,0.05998],"force_p95":75.33058,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.6231,"mean_force":70.74762,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48613,0.01065,0.05826]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.00608,0.05997],"force_p95":56.8063,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.31206,"mean_force":51.5744,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.4862,0.00993,0.05824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.49581,0.04731,0.00955],"force_p95":36.05186,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.85887,"mean_force":13.25569,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48501,0.035,0.06049]},{"body_a":"attachment","body_b":"peg","contact_count":79.0,"contact_point_centroid":[0.49147,0.03709,0.05926],"force_p95":35.96082,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.39946,"mean_force":20.17033,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48525,0.02826,0.05975]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.49464,0.05882,0.00932],"force_p95":0.66784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60265,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.48344,0.15852,0.23848]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.49849,0.19705,0.29553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.49469,0.02069,0.00848],"force_p95":0.857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.67233,"mean_force":0.60373,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.48367,0.00995,0.09802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49418,0.05896,0.00939],"force_p95":0.5503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54597,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.47638,0.08837,0.12166]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.03973,0.02408],"force_p95":0.42525,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42525,"mean_force":0.42525,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.48336,0.01007,0.13838]}],"total_contact_groups":9},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49354,0.01519,0.02406],"final_tcp_position":[0.48337,0.01007,0.13869],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":75.6231,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05896,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54843,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":294.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.46967,0.12193,0.18668],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05917,0.03397],"object_pos_start":[0.49422,0.05896,0.03384],"object_to_goal_dist_end":0.13942,"object_to_goal_dist_start":0.13922,"object_z_max":0.03397,"peak_contact_force":0.5416,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_peg","tcp_end":[0.48507,0.05731,0.064],"tcp_start":[0.46967,0.12193,0.18668],"tcp_to_object_dist_end":0.03145,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.49541,0.04241,0.04066],"object_pos_start":[0.49422,0.05917,0.03397],"object_to_goal_dist_end":0.12249,"object_to_goal_dist_start":0.13942,"object_z_max":0.04068,"peak_contact_force":63.92184,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":207.0,"raw_peak_contact_force":75.6231,"subtask_id":"push_progress","tcp_end":[0.48618,0.01016,0.05823],"tcp_start":[0.48615,0.01037,0.05824],"tcp_to_object_dist_end":0.03786,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.49354,0.01519,0.02406],"object_pos_start":[0.49541,0.042,0.0407],"object_to_goal_dist_end":0.09673,"object_to_goal_dist_start":0.12208,"object_z_max":0.04076,"peak_contact_force":0.61963,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":260.0,"raw_peak_contact_force":57.31206,"tcp_end":[0.48337,0.01007,0.13869],"tcp_start":[0.48618,0.01016,0.05823],"tcp_to_object_dist_end":0.1152,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75424,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.05155,"approach_align.speed":0.0787,"descend_align.contact_force":2.25088,"descend_align.speed":0.08,"push_through.lateral_adjust":-0.00251,"push_through.push_distance":0.12893,"push_through.speed":0.03662,"retract_after.speed":0.07143},"optimized_scores":{"best_composite_score":-0.17975,"best_fitness_score":0.03025,"best_task_score":0.0013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.5066,0.06781,0.00938],"force_p95":48.23052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.3615,"mean_force":27.50877,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51146,0.09178,0.05986]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.52254,0.08745,0.0585],"force_p95":47.71372,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.73989,"mean_force":27.08569,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51146,0.09178,0.05986]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50516,0.08021,0.00939],"force_p95":0.6155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.91687,"mean_force":0.8121,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.50854,0.09043,0.09856]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.52193,0.08691,0.05852],"force_p95":24.70263,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.61265,"mean_force":5.7732,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.51066,0.09073,0.05983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50594,0.0809,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.23516,"mean_force":0.59883,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.51883,0.11471,0.08254]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52264,0.08776,0.05873],"force_p95":18.59939,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.59939,"mean_force":18.59939,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.51172,0.09244,0.06035]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.50562,0.08091,0.00935],"force_p95":0.56485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58823,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.51434,0.16711,0.19856]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50058,0.19798,0.29402]}],"total_contact_groups":8},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50528,0.08017,0.03383],"final_tcp_position":[0.5082,0.0904,0.13991],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":52.3615,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54621,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52861,0.13763,0.10897],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":359.0,"n_steps_budget":870.0,"object_pos_end":[0.50602,0.08087,0.03379],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":19.23516,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":360.0,"raw_peak_contact_force":19.23516,"subtask_id":"reach_peg","tcp_end":[0.51171,0.09232,0.06024],"tcp_start":[0.52861,0.13763,0.10897],"tcp_to_object_dist_end":0.02939,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50573,0.0805,0.03386],"object_pos_start":[0.50602,0.08087,0.03379],"object_to_goal_dist_end":0.16072,"object_to_goal_dist_start":0.1611,"object_z_max":0.03391,"peak_contact_force":1.03004,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":52.3615,"subtask_id":"push_progress","tcp_end":[0.51123,0.09097,0.05954],"tcp_start":[0.51123,0.09106,0.05958],"tcp_to_object_dist_end":0.02827,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":870.0,"object_pos_end":[0.50528,0.08017,0.03383],"object_pos_start":[0.50575,0.08035,0.03394],"object_to_goal_dist_end":0.16038,"object_to_goal_dist_start":0.16057,"object_z_max":0.03403,"peak_contact_force":0.54578,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":269.0,"raw_peak_contact_force":35.91687,"tcp_end":[0.5082,0.0904,0.13991],"tcp_start":[0.51123,0.09097,0.05954],"tcp_to_object_dist_end":0.10661,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99408,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.approach_height":0.05501,"approach_align.speed":0.04632,"descend_align.contact_force":3.88135,"descend_align.speed":0.06928,"push_through.lateral_adjust":-0.00072,"push_through.push_distance":0.12813,"push_through.speed":0.03404,"retract_after.speed":0.04978},"optimized_scores":{"best_composite_score":-0.17904,"best_fitness_score":0.03096,"best_task_score":0.00251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49625,0.09274,0.00943],"force_p95":44.95728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.67631,"mean_force":25.6072,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50709,0.11284,0.06008]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.51895,0.1127,0.05865],"force_p95":44.49607,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.13223,"mean_force":25.20113,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50709,0.11284,0.06008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50451,0.1038,0.00941],"force_p95":0.67574,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.84153,"mean_force":0.83945,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.5042,0.11129,0.09853]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.51813,0.1113,0.05874],"force_p95":22.20265,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.53643,"mean_force":5.40532,"phase_index":3.0,"phase_name":"retract_after","phase_type":"retract","tcp_position_centroid":[0.50627,0.11162,0.06011]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50605,0.10456,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.12791,"mean_force":0.59331,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.51168,0.13579,0.08478]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51923,0.1134,0.05885],"force_p95":18.63665,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.63665,"mean_force":18.63665,"phase_index":1.0,"phase_name":"descend_align","phase_type":"descend","tcp_position_centroid":[0.50736,0.11352,0.0606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.50543,0.10471,0.00936],"force_p95":0.58323,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57771,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.50908,0.17837,0.20169]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.5001,0.19881,0.29554]}],"total_contact_groups":8},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50508,0.10381,0.0338],"final_tcp_position":[0.50396,0.11127,0.14007],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":46.67631,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55165,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":393.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51874,0.15893,0.11338],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":395.0,"n_steps_budget":990.0,"object_pos_end":[0.50588,0.10455,0.03384],"object_pos_start":[0.506,0.10468,0.03384],"object_to_goal_dist_end":0.18474,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":19.12791,"phase_name":"descend_align","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":396.0,"raw_peak_contact_force":19.12791,"subtask_id":"reach_peg","tcp_end":[0.50735,0.11341,0.06048],"tcp_start":[0.51874,0.15893,0.11338],"tcp_to_object_dist_end":0.02811,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50549,0.10417,0.03403],"object_pos_start":[0.50588,0.10455,0.03384],"object_to_goal_dist_end":0.18435,"object_to_goal_dist_start":0.18474,"object_z_max":0.03406,"peak_contact_force":0.80064,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":46.67631,"subtask_id":"push_progress","tcp_end":[0.50684,0.11193,0.05973],"tcp_start":[0.50687,0.11204,0.05979],"tcp_to_object_dist_end":0.02689,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.50508,0.10381,0.0338],"object_pos_start":[0.50553,0.10401,0.03408],"object_to_goal_dist_end":0.18399,"object_to_goal_dist_start":0.18419,"object_z_max":0.03462,"peak_contact_force":0.55483,"phase_name":"retract_after","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":287.0,"raw_peak_contact_force":23.84153,"tcp_end":[0.50396,0.11127,0.14007],"tcp_start":[0.50684,0.11193,0.05973],"tcp_to_object_dist_end":0.10654,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```