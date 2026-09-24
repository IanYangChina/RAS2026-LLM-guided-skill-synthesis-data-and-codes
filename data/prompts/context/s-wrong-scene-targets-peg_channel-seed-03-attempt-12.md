## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → rotate → push | linear_cartesian | linear_cartesian | joint_interpolation | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 7 | 0.1144 | 0.29 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1042 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | -0.3027 | 0.00 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5249 | 0.15 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.3304 | 0.14 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.114) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_pre_push
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: insertion
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind_peg
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
    - 0.05
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
  subtask_id: reach_pre_push
- id: descend_to_peg_height
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_pre_push
- id: align_for_push
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_push
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
    push_force_limit:
      type: scalar
      range:
      - 30.0
      - 45.0
      default: 40.0
      binds_to:
      - path: guards.force_limit_guard.threshold
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
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg_height** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **align_for_push** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_limit: status=consumed; consumers=guards.force_limit_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]

## Design Metrics

- **Composite score**: 0.114
- **task_score** (E): 0.292
- **fitness_score**: 0.441  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.2045 |
| descend_to_peg_height | 0.33 | 1.00 | 0.0651 |
| align_for_push | 1.00 | 1.00 | 0.0208 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.138, 0.108) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| descend_to_peg_height | descend | 0.33 / step_budget | (0.505, 0.138, 0.108)→(0.496, 0.132, 0.045) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 22.270 | 22.273 |
| align_for_push | rotate | 1.00 / step_budget | (0.496, 0.132, 0.045)→(0.488, 0.151, 0.042) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.362 | 39.901 |
| push_through_channel | push | 0.00 / guard_failure | (0.486, 0.004, 0.039)→(0.486, 0.004, 0.039) | (0.502, 0.082, 0.034)→(0.503, -0.035, 0.036) | 0.162→0.052 | 1.00 / 3.000 | 44.260 | 71.349 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.546
- phase_score: 0.744
- phase_breakdown.reach_pre_push_score: 0.254
- phase_breakdown.insertion_score: 0.954

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.665
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: 0.160
- **K-run variance**: 0.0188
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_through_channel.push_distance
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18182,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_for_push.align_speed":0.12664,"approach_behind_peg.approach_speed":0.19857,"descend_to_peg_height.descend_force":17.64408,"push_through_channel.push_distance":0.16563,"push_through_channel.push_force_limit":42.16377,"push_through_channel.push_speed":0.07881,"push_through_channel.push_timeout":3.91663},"optimized_scores":{"best_composite_score":-0.07139,"best_fitness_score":0.08861,"best_task_score":0.0004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":404.0,"contact_point_centroid":[0.475,0.11402,0.05997],"force_p95":115.83707,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.57561,"mean_force":100.10043,"phase_index":2.0,"phase_name":"align_for_push","phase_type":"rotate","tcp_position_centroid":[0.47918,0.11733,0.05935]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.475,0.12,0.05997],"force_p95":99.37828,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.38925,"mean_force":63.15047,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4775,0.12477,0.05956]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.10083,0.05998],"force_p95":65.68904,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.68904,"mean_force":65.68904,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.47986,0.11167,0.0593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.49446,0.05906,0.00933],"force_p95":0.61189,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58948,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.48256,0.15623,0.19649]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49856,0.19689,0.29274]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.4942,0.0592,0.00939],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54589,"phase_index":2.0,"phase_name":"align_for_push","phase_type":"rotate","tcp_position_centroid":[0.47918,0.11735,0.05935]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.49417,0.05872,0.00939],"force_p95":0.55041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54618,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.47264,0.11433,0.08171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.48062,0.05087,0.00939],"force_p95":0.54863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5487,"mean_force":0.54588,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47751,0.12478,0.05957]}],"total_contact_groups":8},"final_pose_error":0.16556,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49413,0.05875,0.03394],"final_tcp_position":[0.47748,0.12473,0.05953],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":118.57561,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":367.0,"n_steps_budget":750.0,"object_pos_end":[0.49407,0.05887,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54924,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_push","tcp_end":[0.46783,0.1177,0.10746],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":336.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.05895,0.03389],"object_pos_start":[0.49407,0.05887,0.03385],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.13914,"object_z_max":0.03389,"peak_contact_force":65.68904,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":65.68904,"subtask_id":"reach_pre_push","tcp_end":[0.4799,0.11166,0.05918],"tcp_start":[0.46783,0.1177,0.10746],"tcp_to_object_dist_end":0.0602,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":421.0,"n_steps_budget":600.0,"object_pos_end":[0.49392,0.059,0.03394],"object_pos_start":[0.49427,0.05895,0.03389],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.1392,"object_z_max":0.03394,"peak_contact_force":0.0,"phase_name":"align_for_push","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":825.0,"raw_peak_contact_force":118.57561,"subtask_id":"reach_pre_push","tcp_end":[0.47755,0.12481,0.05962],"tcp_start":[0.4799,0.11166,0.05918],"tcp_to_object_dist_end":0.07251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.49401,0.05878,0.03394],"object_pos_start":[0.49392,0.059,0.03394],"object_to_goal_dist_end":0.13904,"object_to_goal_dist_start":0.13927,"object_z_max":0.03394,"peak_contact_force":87.3344,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":102.38925,"subtask_id":"insertion","tcp_end":[0.47748,0.12473,0.05953],"tcp_start":[0.47748,0.12473,0.05954],"tcp_to_object_dist_end":0.07265,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.25676,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_for_push.align_speed":0.14272,"approach_behind_peg.approach_speed":0.29263,"descend_to_peg_height.descend_force":15.78351,"push_through_channel.push_distance":0.2339,"push_through_channel.push_force_limit":38.73788,"push_through_channel.push_speed":0.14632,"push_through_channel.push_timeout":6.2298},"optimized_scores":{"best_composite_score":0.16011,"best_fitness_score":0.57011,"best_task_score":0.32856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":495.0,"contact_point_centroid":[0.49874,0.01334,0.04063],"force_p95":21.85981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.77228,"mean_force":6.38709,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49103,0.02367,0.02913]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.5083,-0.10041,0.06026],"force_p95":52.01204,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.22384,"mean_force":27.84014,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49072,-0.0557,0.02886]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50644,0.02522,0.00968],"force_p95":15.23206,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.1052,"mean_force":3.62372,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4914,0.07117,0.02949]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":558.0,"contact_point_centroid":[0.5252,-0.00575,0.03208],"force_p95":13.86062,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.17782,"mean_force":3.51438,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49103,0.0198,0.02914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":322.0,"contact_point_centroid":[0.50552,0.08083,0.00934],"force_p95":0.57576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59415,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.51473,0.16681,0.19685]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50082,0.19756,0.2926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50593,0.0809,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51627,0.13394,0.07254]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50603,0.08097,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":2.0,"phase_name":"align_for_push","phase_type":"rotate","tcp_position_centroid":[0.49848,0.14211,0.03446]}],"total_contact_groups":8},"final_pose_error":0.0258,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50818,-0.08168,0.0366],"final_tcp_position":[0.49057,-0.05681,0.02869],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":56.77228,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":351.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54628,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":358.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_pre_push","tcp_end":[0.52878,0.13763,0.1076],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":295.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":295.0,"raw_peak_contact_force":0.55023,"subtask_id":"reach_pre_push","tcp_end":[0.50518,0.1308,0.03867],"tcp_start":[0.52878,0.13763,0.1076],"tcp_to_object_dist_end":0.05015,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":290.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"align_for_push","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":290.0,"raw_peak_contact_force":0.55007,"subtask_id":"reach_pre_push","tcp_end":[0.49491,0.15216,0.0337],"tcp_start":[0.50518,0.1308,0.03867],"tcp_to_object_dist_end":0.07215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":905.0,"n_steps_budget":990.0,"object_pos_end":[0.50824,-0.08151,0.03668],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.00901,"object_to_goal_dist_start":0.1611,"object_z_max":0.03719,"peak_contact_force":23.23844,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1594.0,"raw_peak_contact_force":56.77228,"subtask_id":"insertion","tcp_end":[0.49057,-0.05681,0.02869],"tcp_start":[0.49062,-0.05674,0.02874],"tcp_to_object_dist_end":0.03141,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26923,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_for_push.align_speed":0.11081,"approach_behind_peg.approach_speed":0.22161,"descend_to_peg_height.descend_force":11.21542,"push_through_channel.push_distance":0.25,"push_through_channel.push_force_limit":34.83575,"push_through_channel.push_speed":0.14891,"push_through_channel.push_timeout":5.79092},"optimized_scores":{"best_composite_score":0.2546,"best_fitness_score":0.6646,"best_task_score":0.54563},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":536.0,"contact_point_centroid":[0.49698,0.02812,0.03782],"force_p95":19.84503,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.88524,"mean_force":6.84899,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48845,0.03771,0.02862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.5074,-0.10034,0.05984],"force_p95":35.91467,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.63356,"mean_force":15.08868,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48854,-0.05603,0.02866]},{"body_a":"peg","body_b":"channel_base_body","contact_count":620.0,"contact_point_centroid":[0.50665,0.03608,0.00972],"force_p95":14.40719,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.76955,"mean_force":4.14585,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48875,0.07963,0.02887]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":648.0,"contact_point_centroid":[0.52522,0.0146,0.03029],"force_p95":11.11563,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.38558,"mean_force":3.49199,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48845,0.03832,0.02861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.50551,0.10473,0.00936],"force_p95":0.60073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58256,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50954,0.178,0.19752]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50047,0.19845,0.29345]},{"body_a":"peg","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5203,-0.01702,0.06404],"force_p95":2.22728,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.22728,"mean_force":2.22728,"phase_index":3.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48842,-0.00268,0.02864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":308.0,"contact_point_centroid":[0.5057,0.1046,0.00939],"force_p95":0.57541,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.5464,"phase_index":1.0,"phase_name":"descend_to_peg_height","phase_type":"descend","tcp_position_centroid":[0.51033,0.15602,0.07252]},{"body_a":"peg","body_b":"channel_base_body","contact_count":310.0,"contact_point_centroid":[0.5059,0.10454,0.00939],"force_p95":0.57568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57608,"mean_force":0.54629,"phase_index":2.0,"phase_name":"align_for_push","phase_type":"rotate","tcp_position_centroid":[0.49632,0.16542,0.03387]}],"total_contact_groups":9},"final_pose_error":0.01849,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50728,-0.08164,0.03586],"final_tcp_position":[0.48848,-0.05711,0.02859],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":54.88524,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":339.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.10458,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18478,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54077,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":344.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_pre_push","tcp_end":[0.51892,0.15882,0.10846],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":308.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.50596,0.10458,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18478,"object_z_max":0.03384,"peak_contact_force":0.57582,"phase_name":"descend_to_peg_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":308.0,"raw_peak_contact_force":0.57865,"subtask_id":"reach_pre_push","tcp_end":[0.50372,0.15395,0.0382],"tcp_start":[0.51892,0.15882,0.10846],"tcp_to_object_dist_end":0.04949,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,0.10472,0.03384],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.54254,"phase_name":"align_for_push","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":310.0,"raw_peak_contact_force":0.57608,"subtask_id":"reach_pre_push","tcp_end":[0.49232,0.17538,0.03314],"tcp_start":[0.50372,0.15395,0.0382],"tcp_to_object_dist_end":0.07196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.50735,-0.08151,0.03593],"object_pos_start":[0.50589,0.10472,0.03384],"object_to_goal_dist_end":0.00854,"object_to_goal_dist_start":0.18491,"object_z_max":0.03746,"peak_contact_force":22.20746,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1818.0,"raw_peak_contact_force":54.88524,"subtask_id":"insertion","tcp_end":[0.48848,-0.05711,0.02859],"tcp_start":[0.48851,-0.05704,0.02863],"tcp_to_object_dist_end":0.03171,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```