## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5249 | 0.15 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.3304 | 0.14 | ✅ accepted |
| 7 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.4598 | 0.00 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.1064 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0593 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.46685193337148995, -0.10105515947231203, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, -0.10105515947231203, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.46685193337148995, 0.058944840527687975, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.46685193337148995, 0.058944840527687975, 0.04]
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
  frozen_object_starts: {'peg': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.46685193337148995, -0.10105515947231203, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.525) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: insertion
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_peg
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_to_peg_side
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - -0.01
    offset_along_axis:
      distance: 0.03
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force:
      type: scalar
      range:
      - 5.0
      - 35.0
      default: 10
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_peg
- id: push_through_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg_side** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, -0.01], offset_along_axis={axis=world_z, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]

## Design Metrics

- **Composite score**: 0.525
- **task_score** (E): 0.150
- **fitness_score**: 0.305  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2519 |
| descend_to_peg_side | 1.00 | 1.00 | 0.0253 |
| push_through_channel | 1.00 | 1.00 | 0.1362 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.137, 0.058) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.333 | 169.094 | 182.573 |
| descend_to_peg_side | descend | 1.00 / force_exceeded | (0.505, 0.137, 0.058)→(0.497, 0.135, 0.035) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 96.833 | 96.833 |
| push_through_channel | push | 1.00 / time_limit | (0.497, 0.135, 0.035)→(0.496, -0.001, 0.038) | (0.502, 0.082, 0.034)→(0.502, 0.026, 0.035) | 0.162→0.106 | 1.00 / 3.333 | 280.152 | 474.464 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.647
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.335
- phase_score: 0.575
- phase_breakdown.reach_peg_score: 0.614
- phase_breakdown.insertion_score: 0.559

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.479
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.335
- **Median Q (composite search score)**: 0.535
- **K-run variance**: 0.0214
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.351


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
{"anchors":[{"name":"object","value":[0.46685,-0.10106,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.10106,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.76364,"average_solve_count":55.0,"average_success_count":55.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.32307,"descend_to_peg_side.descend_force":20.79597,"push_through_channel.push_distance":0.2475,"push_through_channel.push_speed":0.15163,"push_through_channel.push_timeout":3.69537},"optimized_scores":{"best_composite_score":0.34088,"best_fitness_score":0.12088,"best_task_score":0.00052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":92.0,"contact_point_centroid":[0.47306,-0.10015,0.065],"force_p95":533.80803,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":603.60721,"mean_force":290.26897,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47248,-0.08821,0.06043]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47489,0.10722,0.05913],"force_p95":539.63321,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":540.06289,"mean_force":449.87141,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.46741,0.11656,0.05932]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":784.0,"contact_point_centroid":[0.47499,0.00014,0.05995],"force_p95":271.50303,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":468.91384,"mean_force":157.71523,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47059,0.01117,0.06058]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47486,0.10662,0.05892],"force_p95":124.54314,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.54314,"mean_force":124.54314,"phase_index":1.0,"phase_name":"descend_to_peg_side","phase_type":"descend","tcp_position_centroid":[0.4679,0.11634,0.05881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":394.0,"contact_point_centroid":[0.4945,0.05907,0.00934],"force_p95":0.59621,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58333,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48195,0.15504,0.16951]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49868,0.19723,0.29226]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49406,0.05891,0.00939],"force_p95":0.55042,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54586,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47059,0.0118,0.0606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.47614,0.05913,0.00939],"force_p95":0.54489,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54489,"mean_force":0.54489,"phase_index":1.0,"phase_name":"descend_to_peg_side","phase_type":"descend","tcp_position_centroid":[0.4679,0.11634,0.05881]}],"total_contact_groups":8},"final_pose_error":0.04357,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49415,0.05869,0.034],"final_tcp_position":[0.47275,-0.0879,0.06045],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":603.60721,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.49402,0.05896,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13922,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":506.19684,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":440.0,"raw_peak_contact_force":540.06289,"subtask_id":"reach_peg","tcp_end":[0.4679,0.11634,0.05881],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49403,0.05891,0.03386],"object_pos_start":[0.49402,0.05896,0.03386],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.13922,"object_z_max":0.03386,"peak_contact_force":124.54314,"phase_name":"descend_to_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":124.54314,"subtask_id":"reach_peg","tcp_end":[0.46799,0.11633,0.05886],"tcp_start":[0.4679,0.11634,0.05881],"tcp_to_object_dist_end":0.06782,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.49415,0.05869,0.034],"object_pos_start":[0.49403,0.05891,0.03386],"object_to_goal_dist_end":0.13895,"object_to_goal_dist_start":0.13918,"object_z_max":0.034,"peak_contact_force":266.75077,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1867.0,"raw_peak_contact_force":603.60721,"subtask_id":"insertion","tcp_end":[0.47275,-0.0879,0.06045],"tcp_start":[0.46799,0.11633,0.05886],"tcp_to_object_dist_end":0.15049,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,-0.07909,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,-0.07909,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13433,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.47476,"descend_to_peg_side.descend_force":28.95083,"push_through_channel.push_distance":0.21925,"push_through_channel.push_speed":0.13385,"push_through_channel.push_timeout":3.00762},"optimized_scores":{"best_composite_score":0.53483,"best_fitness_score":0.31483,"best_task_score":0.11364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":808.0,"contact_point_centroid":[0.52504,0.08145,0.05999],"force_p95":366.62508,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.70867,"mean_force":200.39704,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50809,0.0848,0.02546]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":769.0,"contact_point_centroid":[0.54515,0.07667,0.05995],"force_p95":347.63552,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.18514,"mean_force":183.55645,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50846,0.08856,0.02533]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54978,0.11999,0.05993],"force_p95":75.35762,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.35762,"mean_force":75.35762,"phase_index":1.0,"phase_name":"descend_to_peg_side","phase_type":"descend","tcp_position_centroid":[0.51483,0.13284,0.02427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":903.0,"contact_point_centroid":[0.50454,0.0459,0.00962],"force_p95":7.02354,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.57479,"mean_force":1.57409,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50858,0.09002,0.02533]},{"body_a":"peg","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.52114,0.06551,0.06302],"force_p95":33.77629,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.17649,"mean_force":7.89595,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50749,0.09525,0.02507]},{"body_a":"attachment","body_b":"peg","contact_count":406.0,"contact_point_centroid":[0.50856,0.05271,0.04493],"force_p95":8.84963,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.8832,"mean_force":2.11016,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50709,0.06567,0.02589]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":182.0,"contact_point_centroid":[0.52518,0.04838,0.03356],"force_p95":1.63714,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.61617,"mean_force":0.50761,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50742,0.08184,0.02526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50555,0.08091,0.00935],"force_p95":0.56159,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58651,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51476,0.16624,0.17126]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50073,0.19783,0.29204]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50597,0.08075,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54675,"phase_index":1.0,"phase_name":"descend_to_peg_side","phase_type":"descend","tcp_position_centroid":[0.52125,0.13421,0.04063]}],"total_contact_groups":10},"final_pose_error":0.13619,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50576,0.01844,0.03592],"final_tcp_position":[0.50637,0.04947,0.02736],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":435.70867,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":413.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55002,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":420.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52895,0.13626,0.058],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":143.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":75.35762,"phase_name":"descend_to_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":144.0,"raw_peak_contact_force":75.35762,"subtask_id":"reach_peg","tcp_end":[0.51477,0.13283,0.02406],"tcp_start":[0.52895,0.13626,0.058],"tcp_to_object_dist_end":0.05356,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,0.01844,0.03592],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.0987,"object_to_goal_dist_start":0.16113,"object_z_max":0.0377,"peak_contact_force":341.38549,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3116.0,"raw_peak_contact_force":435.70867,"subtask_id":"insertion","tcp_end":[0.50637,0.04947,0.02736],"tcp_start":[0.51477,0.13283,0.02406],"tcp_to_object_dist_end":0.03219,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31343,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.30792,"descend_to_peg_side.descend_force":13.74604,"push_through_channel.push_distance":0.22681,"push_through_channel.push_speed":0.1454,"push_through_channel.push_timeout":7.52129},"optimized_scores":{"best_composite_score":0.69906,"best_fitness_score":0.47906,"best_task_score":0.33497},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":847.0,"contact_point_centroid":[0.54462,0.06971,0.05996],"force_p95":272.734,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.07491,"mean_force":167.854,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50797,0.08391,0.02418]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":580.0,"contact_point_centroid":[0.52503,0.06136,0.06],"force_p95":223.30288,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.39883,"mean_force":151.13501,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50786,0.06276,0.0247]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.555,0.11999,0.05996],"force_p95":90.59684,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.59684,"mean_force":90.59684,"phase_index":1.0,"phase_name":"descend_to_peg_side","phase_type":"descend","tcp_position_centroid":[0.50866,0.15505,0.02157]},{"body_a":"peg","body_b":"channel_base_body","contact_count":835.0,"contact_point_centroid":[0.50456,0.04414,0.00949],"force_p95":11.56894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.53814,"mean_force":2.45346,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50798,0.08505,0.02415]},{"body_a":"peg","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.52084,0.0247,0.06279],"force_p95":33.8551,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.41486,"mean_force":7.3592,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50783,0.05187,0.02475]},{"body_a":"attachment","body_b":"peg","contact_count":223.0,"contact_point_centroid":[0.50758,0.07428,0.03448],"force_p95":3.372,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.97012,"mean_force":0.83928,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50793,0.08598,0.02446]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":121.0,"contact_point_centroid":[0.52523,0.01644,0.05166],"force_p95":10.26684,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.78538,"mean_force":2.78631,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50783,0.05336,0.02466]},{"body_a":"peg","body_b":"channel_base_body","contact_count":376.0,"contact_point_centroid":[0.50554,0.10474,0.00936],"force_p95":0.58311,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57641,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50947,0.17763,0.17227]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50039,0.19863,0.29313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50563,0.10432,0.00939],"force_p95":0.57516,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54633,"phase_index":1.0,"phase_name":"descend_to_peg_side","phase_type":"descend","tcp_position_centroid":[0.51294,0.15606,0.03938]}],"total_contact_groups":10},"final_pose_error":0.10652,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50625,0.00118,0.03414],"final_tcp_position":[0.50754,0.03467,0.02544],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":384.07491,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":403.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10461,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53472,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":408.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51892,0.15781,0.05862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":164.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50599,0.10461,0.03384],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18481,"object_z_max":0.03384,"peak_contact_force":90.59684,"phase_name":"descend_to_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":165.0,"raw_peak_contact_force":90.59684,"subtask_id":"reach_peg","tcp_end":[0.50864,0.15505,0.02138],"tcp_start":[0.51892,0.15781,0.05862],"tcp_to_object_dist_end":0.05192,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.50625,0.00118,0.03414],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.08163,"object_to_goal_dist_start":0.18492,"object_z_max":0.03878,"peak_contact_force":232.31997,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2791.0,"raw_peak_contact_force":384.07491,"subtask_id":"insertion","tcp_end":[0.50754,0.03467,0.02544],"tcp_start":[0.50864,0.15505,0.02138],"tcp_to_object_dist_end":0.03462,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```