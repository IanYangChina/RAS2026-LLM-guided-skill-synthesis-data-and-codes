## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2624 | 0.13 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.5279 | 0.21 | ✅ accepted |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.262) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.15
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_peg
- id: descend_to_contact
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
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
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
  subtask_id: approach_peg
- id: push_along_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.262
- **task_score** (E): 0.132
- **fitness_score**: 0.272  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1397 |
| descend_to_contact | 1.00 | 1.00 | 0.1230 |
| align_lateral | 1.00 | 1.00 | 0.0124 |
| push_along_channel | 0.00 | 1.00 | 0.0433 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.141, 0.177) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.505, 0.141, 0.177)→(0.499, 0.109, 0.060) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 18.799 | 18.799 |
| align_lateral | push | 1.00 / step_budget | (0.499, 0.109, 0.060)→(0.505, 0.107, 0.049) | (0.502, 0.081, 0.034)→(0.502, 0.078, 0.036) | 0.162→0.158 | 1.00 / 2.333 | 109.531 | 211.825 |
| push_along_channel | push | 0.00 / step_budget | (0.505, 0.107, 0.049)→(0.519, 0.080, 0.065) | (0.502, 0.078, 0.036)→(0.497, 0.013, 0.024) | 0.158→0.095 | 1.00 / 3.000 | 318.776 | 1096.440 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.534
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.183
- phase_score: 0.520
- phase_breakdown.align_to_channel_score: 0.885
- phase_breakdown.approach_peg_score: 0.174
- phase_breakdown.push_to_goal_score: 0.582

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.385
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.183
- **Median Q (composite search score)**: 0.234
- **K-run variance**: 0.0069
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.283


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77982,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_distance":0.01728,"approach_behind.approach_height":0.11471,"descend_to_contact.descend_force_threshold":8.50342,"push_along_channel.push_distance":0.11903},"optimized_scores":{"best_composite_score":0.3753,"best_fitness_score":0.3853,"best_task_score":0.18324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":591.0,"contact_point_centroid":[0.52687,0.11846,0.0599],"force_p95":321.2168,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1519.75668,"mean_force":295.21137,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52333,0.06221,0.09244]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.5256,0.07597,0.05968],"force_p95":1368.67695,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1374.57485,"mean_force":685.3939,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50081,0.07175,0.0372]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49706,0.06957,0.04308],"force_p95":172.04478,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.39552,"mean_force":112.0041,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49705,0.08131,0.04273]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.49734,-0.02475,0.00805],"force_p95":0.94762,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.0613,"mean_force":2.01113,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52401,0.06214,0.09387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":48.0,"contact_point_centroid":[0.49559,0.0414,0.00974],"force_p95":17.82083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.62427,"mean_force":3.23425,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.4889,0.08534,0.0514]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49278,0.07302,0.05126],"force_p95":18.35671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.59194,"mean_force":13.62744,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.49044,0.08476,0.04956]},{"body_a":"peg","body_b":"channel_base_body","contact_count":684.0,"contact_point_centroid":[0.49415,0.05868,0.00939],"force_p95":0.55037,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.51825,"mean_force":0.57136,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47579,0.10352,0.11168]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.48941,0.07574,0.05924],"force_p95":10.06705,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.18516,"mean_force":9.004,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48489,0.08715,0.05804]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47498,-0.04411,0.02429],"force_p95":9.29432,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35766,"mean_force":2.91636,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52803,0.06196,0.09892]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.4946,0.05911,0.00932],"force_p95":0.66036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60096,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48303,0.15766,0.22939]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49833,0.19663,0.29437]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52502,-0.03977,0.0433],"force_p95":2.07652,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0983,"mean_force":1.88045,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50148,0.06277,0.0602]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47482,0.0513,0.05999],"force_p95":0.31868,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35279,"mean_force":0.1218,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.49307,0.08374,0.04611]}],"total_contact_groups":13},"final_pose_error":0.12829,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49323,-0.02643,0.02406],"final_tcp_position":[0.53037,0.06179,0.09885],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":1519.75668,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.49404,0.05891,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54735,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":302.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46909,0.12092,0.17033],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":684.0,"n_steps_budget":900.0,"object_pos_end":[0.4942,0.05849,0.03423],"object_pos_start":[0.49404,0.05891,0.03384],"object_to_goal_dist_end":0.13874,"object_to_goal_dist_start":0.13917,"object_z_max":0.03416,"peak_contact_force":10.51825,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":686.0,"raw_peak_contact_force":10.51825,"subtask_id":"approach_peg","tcp_end":[0.48506,0.08695,0.05732],"tcp_start":[0.46909,0.12092,0.17033],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":48.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.05445,0.03714],"object_pos_start":[0.4942,0.05849,0.03423],"object_to_goal_dist_end":0.13462,"object_to_goal_dist_start":0.13874,"object_z_max":0.03725,"peak_contact_force":18.32237,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":67.0,"raw_peak_contact_force":18.62427,"subtask_id":"align_to_channel","tcp_end":[0.49492,0.08311,0.04405],"tcp_start":[0.48506,0.08695,0.05732],"tcp_to_object_dist_end":0.0295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":617.0,"n_steps_budget":810.0,"object_pos_end":[0.49323,-0.02643,0.02406],"object_pos_start":[0.49383,0.05445,0.03714],"object_to_goal_dist_end":0.05631,"object_to_goal_dist_start":0.13462,"object_z_max":0.04098,"peak_contact_force":276.04422,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1199.0,"raw_peak_contact_force":1519.75668,"subtask_id":"push_to_goal","tcp_end":[0.53037,0.06179,0.09885],"tcp_start":[0.49492,0.08311,0.04405],"tcp_to_object_dist_end":0.12148,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78761,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_distance":0.01934,"approach_behind.approach_height":0.14246,"descend_to_contact.descend_force_threshold":5.494,"push_along_channel.push_distance":0.14054},"optimized_scores":{"best_composite_score":0.17803,"best_fitness_score":0.18803,"best_task_score":0.06454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":288.0,"contact_point_centroid":[0.53303,0.11989,0.05986],"force_p95":442.60788,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":990.39418,"mean_force":269.70072,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50761,0.08377,0.05334]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":459.0,"contact_point_centroid":[0.47496,0.11993,0.05107],"force_p95":535.04457,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":625.73254,"mean_force":487.1188,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51332,0.08086,0.04867]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":496.0,"contact_point_centroid":[0.52513,0.08227,0.04922],"force_p95":378.78545,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":606.85083,"mean_force":331.62623,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51326,0.08111,0.04911]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":122.0,"contact_point_centroid":[0.52524,0.10816,0.05989],"force_p95":413.07615,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":466.5448,"mean_force":325.45341,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.5097,0.108,0.05508]},{"body_a":"world","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.48895,0.14525,-7e-05],"force_p95":225.15537,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.53468,"mean_force":186.47915,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51335,0.08204,0.04685]},{"body_a":"attachment","body_b":"peg","contact_count":102.0,"contact_point_centroid":[0.50929,0.09653,0.05641],"force_p95":138.21724,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.44328,"mean_force":23.1751,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.50888,0.108,0.05615]},{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.50155,0.06909,0.00961],"force_p95":122.22477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.82407,"mean_force":15.11968,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.50933,0.10802,0.05571]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.50233,0.08855,0.05753],"force_p95":77.82243,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.8944,"mean_force":41.79025,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49489,0.0952,0.05463]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":67.0,"contact_point_centroid":[0.52528,0.06824,0.04745],"force_p95":73.9575,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.42175,"mean_force":23.42705,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49834,0.09334,0.05318]},{"body_a":"peg","body_b":"channel_base_body","contact_count":751.0,"contact_point_centroid":[0.50018,0.03312,0.00846],"force_p95":1.32398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.01722,"mean_force":1.27251,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51095,0.08275,0.05048]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.52541,0.07949,0.02785],"force_p95":26.81044,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.18893,"mean_force":4.88404,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.50994,0.10811,0.05536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":600.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.22821,"mean_force":0.59124,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51567,0.12478,0.12715]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51182,0.09783,0.05872],"force_p95":26.88049,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.88049,"mean_force":26.88049,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50629,0.1082,0.06096]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47489,0.02229,0.04424],"force_p95":3.18573,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3785,"mean_force":0.95624,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5093,0.08228,0.05278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50528,0.08081,0.00932],"force_p95":0.70082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.61806,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51414,0.16838,0.24287]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.501,0.19692,0.29434]}],"total_contact_groups":16},"final_pose_error":0.12492,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49773,0.02789,0.02414],"final_tcp_position":[0.51338,0.08246,0.04619],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":990.39418,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":900.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54584,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":250.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.52721,0.14178,0.1967],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08087,0.03377],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":27.22821,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":601.0,"raw_peak_contact_force":27.22821,"subtask_id":"approach_peg","tcp_end":[0.50628,0.10815,0.06074],"tcp_start":[0.52721,0.14178,0.1967],"tcp_to_object_dist_end":0.03836,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":147.0,"n_steps_budget":600.0,"object_pos_end":[0.50645,0.07872,0.03564],"object_pos_start":[0.50595,0.08087,0.03377],"object_to_goal_dist_end":0.15891,"object_to_goal_dist_start":0.1611,"object_z_max":0.03575,"peak_contact_force":309.85021,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":444.0,"raw_peak_contact_force":466.5448,"subtask_id":"align_to_channel","tcp_end":[0.50881,0.10785,0.05521],"tcp_start":[0.50628,0.10815,0.06074],"tcp_to_object_dist_end":0.03518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":784.0,"n_steps_budget":960.0,"object_pos_end":[0.49773,0.02789,0.02414],"object_pos_start":[0.50645,0.07872,0.03564],"object_to_goal_dist_end":0.10908,"object_to_goal_dist_start":0.15891,"object_z_max":0.0408,"peak_contact_force":431.56389,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2273.0,"raw_peak_contact_force":990.39418,"subtask_id":"push_to_goal","tcp_end":[0.51338,0.08246,0.04619],"tcp_start":[0.50881,0.10785,0.05521],"tcp_to_object_dist_end":0.0609,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77778,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_distance":0.01779,"approach_behind.approach_height":0.10684,"descend_to_contact.descend_force_threshold":8.91662,"push_along_channel.push_distance":0.13256},"optimized_scores":{"best_composite_score":0.23401,"best_fitness_score":0.24401,"best_task_score":0.14758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":324.0,"contact_point_centroid":[0.52504,0.10321,0.05033],"force_p95":207.7688,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":779.17033,"mean_force":144.96582,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51316,0.10237,0.04977]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.55426,0.11976,0.05938],"force_p95":700.23379,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":778.50291,"mean_force":392.4227,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50087,0.13245,0.02832]},{"body_a":"world","body_b":"link7","contact_count":649.0,"contact_point_centroid":[0.49587,0.16664,-9e-05],"force_p95":306.38894,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.24196,"mean_force":265.48023,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51165,0.10233,0.04804]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.49379,0.118,0.0099],"force_p95":313.15587,"geom_a":"pusher_tip","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.52942,"mean_force":284.73232,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49152,0.11249,0.02022]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.51006,0.12182,0.05769],"force_p95":143.93217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.30615,"mean_force":75.508,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.50625,0.13248,0.05867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.50951,0.10065,0.00887],"force_p95":127.61073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.51441,"mean_force":41.0921,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.50767,0.1321,0.05594]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52528,0.10265,0.04317],"force_p95":30.4748,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.61338,"mean_force":10.50786,"phase_index":2.0,"phase_name":"align_lateral","phase_type":"push","tcp_position_centroid":[0.50857,0.13201,0.05448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.5059,0.1046,0.00939],"force_p95":0.57554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.65196,"mean_force":0.58493,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51049,0.14638,0.11127]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51026,0.12193,0.05886],"force_p95":18.23374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.23374,"mean_force":18.23374,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50504,0.13251,0.06096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":714.0,"contact_point_centroid":[0.50062,0.04535,0.00836],"force_p95":0.96559,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.54525,"mean_force":0.74628,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51081,0.10462,0.0465]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.50355,0.11276,0.0347],"force_p95":14.35177,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.28103,"mean_force":2.68761,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50061,0.12137,0.02993]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52503,0.07819,0.02046],"force_p95":6.39873,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.07139,"mean_force":1.44975,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51307,0.11579,0.04803]},{"body_a":"peg","body_b":"channel_base_body","contact_count":248.0,"contact_point_centroid":[0.50545,0.1047,0.00935],"force_p95":0.63422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59191,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5091,0.1789,0.22689]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50038,0.19833,0.29464]}],"total_contact_groups":14},"final_pose_error":0.10931,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49881,0.03854,0.02417],"final_tcp_position":[0.51333,0.09665,0.04985],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":779.17033,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54624,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":280.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.5182,0.16067,0.16465],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":469.0,"n_steps_budget":870.0,"object_pos_end":[0.50588,0.10455,0.03383],"object_pos_start":[0.50592,0.10457,0.03384],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":18.65196,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":470.0,"raw_peak_contact_force":18.65196,"subtask_id":"approach_peg","tcp_end":[0.50502,0.13247,0.06079],"tcp_start":[0.5182,0.16067,0.16465],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":43.0,"n_steps_budget":600.0,"object_pos_end":[0.5071,0.10118,0.03442],"object_pos_start":[0.50588,0.10455,0.03383],"object_to_goal_dist_end":0.1814,"object_to_goal_dist_start":0.18475,"object_z_max":0.03435,"peak_contact_force":0.42084,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":101.0,"raw_peak_contact_force":150.30615,"subtask_id":"align_to_channel","tcp_end":[0.51132,0.13035,0.04814],"tcp_start":[0.50502,0.13247,0.06079],"tcp_to_object_dist_end":0.03251,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":742.0,"n_steps_budget":900.0,"object_pos_end":[0.49881,0.03854,0.02417],"object_pos_start":[0.5071,0.10118,0.03442],"object_to_goal_dist_end":0.1196,"object_to_goal_dist_start":0.1814,"object_z_max":0.04079,"peak_contact_force":248.72031,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1770.0,"raw_peak_contact_force":779.17033,"subtask_id":"push_to_goal","tcp_end":[0.51333,0.09665,0.04985],"tcp_start":[0.51132,0.13035,0.04814],"tcp_to_object_dist_end":0.06517,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```