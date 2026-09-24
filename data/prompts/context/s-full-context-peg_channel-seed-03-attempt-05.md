## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.4240 | 0.19 | ✅ accepted |
| 4 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 5 | -0.0362 | 0.00 | ❌ rejected |
| 3 | approach → rotate → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.0534 | 0.06 | ❌ rejected |
| 2 | approach → rotate → descend → push | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.4315 | 0.19 | ✅ accepted |
| 1 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.424) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.2
- id: push_insertion
  target_entity: object
  metric: goal_progress
  weight: 0.8
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
    - 0.03
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  subtask_id: approach_pre_contact
- id: rotate_1
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.1
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  subtask_id: approach_pre_contact
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
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
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
  guards:
  - id: contact_made
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: approach_pre_contact
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings: none
- **rotate_1** (`rotate`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_made, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.424
- **task_score** (E): 0.190
- **fitness_score**: 0.384  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1668 |
| rotate_1 | 1.00 | 1.00 | 0.0172 |
| descend_1 | 1.00 | 1.00 | 0.0974 |
| push_1 | 1.00 | 1.00 | 0.1719 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.122, 0.156) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.544 | 3.954 |
| rotate_1 | rotate | 1.00 / step_budget | (0.505, 0.122, 0.156)→(0.498, 0.137, 0.151) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.547 | 0.560 |
| descend_1 | descend | 1.00 / force_exceeded | (0.498, 0.137, 0.151)→(0.497, 0.110, 0.059) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 29.100 | 29.100 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.110, 0.059)→(0.499, -0.060, 0.039) | (0.502, 0.081, 0.034)→(0.500, -0.015, 0.031) | 0.162→0.066 | 1.00 / 1.667 | 26.452 | 110.479 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.553
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.171
- phase_score: 0.540
- phase_breakdown.push_insertion_score: 0.629
- phase_breakdown.approach_pre_contact_score: 0.183

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.393
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.223
- **Median Q (composite search score)**: 0.422
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58261,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_force_threshold":15.75037,"descend_1.descend_speed":0.05366,"push_1.push_speed":0.10279},"optimized_scores":{"best_composite_score":0.43266,"best_fitness_score":0.39266,"best_task_score":0.17126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":44.0,"contact_point_centroid":[0.47499,0.08367,0.05988],"force_p95":125.35835,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.28041,"mean_force":101.5237,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48446,0.07832,0.05574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.49816,0.00019,0.00896],"force_p95":81.38566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.78814,"mean_force":45.93107,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49076,0.01346,0.04815]},{"body_a":"attachment","body_b":"peg","contact_count":345.0,"contact_point_centroid":[0.49956,0.00635,0.04467],"force_p95":81.08494,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.40861,"mean_force":55.00298,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49173,0.0056,0.04737]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.09548,0.06],"force_p95":44.84818,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.84818,"mean_force":44.84818,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48274,0.08688,0.05683]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":87.0,"contact_point_centroid":[0.47496,0.0077,0.02759],"force_p95":20.0919,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.60464,"mean_force":13.71976,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49654,-0.03221,0.04396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.49447,0.05889,0.00933],"force_p95":0.62041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48275,0.14791,0.22172]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49845,0.19642,0.2945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":866.0,"contact_point_centroid":[0.49431,0.05891,0.00939],"force_p95":0.5505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84209,"mean_force":0.54741,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47192,0.10008,0.09893]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.48814,0.07602,0.05891],"force_p95":0.66978,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73487,"mean_force":0.41691,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48257,0.08699,0.05726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":86.0,"contact_point_centroid":[0.49402,0.05908,0.00939],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55101,"mean_force":0.54632,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.46497,0.10768,0.15212]}],"total_contact_groups":10},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4953,-0.02956,0.03083],"final_tcp_position":[0.50109,-0.06041,0.04247],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":130.28041,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.0589,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54255,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_pre_contact","tcp_end":[0.46838,0.10187,0.15499],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":86.0,"n_steps_budget":600.0,"object_pos_end":[0.49418,0.05886,0.03386],"object_pos_start":[0.4942,0.0589,0.03385],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13915,"object_z_max":0.03386,"peak_contact_force":0.5416,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":86.0,"raw_peak_contact_force":0.55101,"subtask_id":"approach_pre_contact","tcp_end":[0.46223,0.11579,0.15103],"tcp_start":[0.46838,0.10187,0.15499],"tcp_to_object_dist_end":0.13413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":866.0,"n_steps_budget":1000.0,"object_pos_end":[0.49411,0.05867,0.03393],"object_pos_start":[0.49418,0.05886,0.03386],"object_to_goal_dist_end":0.13893,"object_to_goal_dist_start":0.13912,"object_z_max":0.03397,"peak_contact_force":44.84818,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":44.84818,"subtask_id":"approach_pre_contact","tcp_end":[0.48277,0.08685,0.05675],"tcp_start":[0.46223,0.11579,0.15103],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.4953,-0.02956,0.03083],"object_pos_start":[0.49411,0.05867,0.03393],"object_to_goal_dist_end":0.05148,"object_to_goal_dist_start":0.13893,"object_z_max":0.04014,"peak_contact_force":78.71951,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":890.0,"raw_peak_contact_force":130.28041,"subtask_id":"push_insertion","tcp_end":[0.50109,-0.06041,0.04247],"tcp_start":[0.48277,0.08685,0.05675],"tcp_to_object_dist_end":0.03348,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20886,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_force_threshold":17.4753,"descend_1.descend_speed":0.026,"push_1.push_speed":0.09756},"optimized_scores":{"best_composite_score":0.41733,"best_fitness_score":0.37733,"best_task_score":0.17543},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50434,0.02483,0.00899],"force_p95":61.86018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.36891,"mean_force":10.77684,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50084,0.02327,0.04706]},{"body_a":"attachment","body_b":"peg","contact_count":100.0,"contact_point_centroid":[0.5076,0.01901,0.0456],"force_p95":64.64139,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.05107,"mean_force":39.03237,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50153,0.01242,0.047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":497.0,"contact_point_centroid":[0.50598,0.08091,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.23222,"mean_force":0.5904,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51267,0.12391,0.10435]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50978,0.09844,0.05876],"force_p95":21.79943,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.79943,"mean_force":21.79943,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50619,0.10983,0.05978]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.50543,0.08092,0.00934],"force_p95":0.58131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59763,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51432,0.15832,0.22177]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50064,0.19696,0.29419]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.5253,-0.02039,0.05998],"force_p95":0.84333,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9766,"mean_force":0.25915,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49739,-0.05676,0.03786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50633,0.08068,0.00938],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54675,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.52449,0.12823,0.15135]}],"total_contact_groups":8},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,-0.01501,0.03816],"final_tcp_position":[0.4972,-0.06048,0.03742],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":66.36891,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55013,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":336.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_pre_contact","tcp_end":[0.52825,0.12161,0.15498],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54814,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":87.0,"raw_peak_contact_force":0.55023,"subtask_id":"approach_pre_contact","tcp_end":[0.52129,0.13747,0.15005],"tcp_start":[0.52825,0.12161,0.15498],"tcp_to_object_dist_end":0.13022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08085,0.03377],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16108,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":22.23222,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":498.0,"raw_peak_contact_force":22.23222,"subtask_id":"approach_pre_contact","tcp_end":[0.50616,0.10979,0.05961],"tcp_start":[0.52129,0.13747,0.15005],"tcp_to_object_dist_end":0.03879,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,-0.01501,0.03816],"object_pos_start":[0.50598,0.08085,0.03377],"object_to_goal_dist_end":0.06528,"object_to_goal_dist_start":0.16108,"object_z_max":0.04082,"peak_contact_force":0.02492,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":499.0,"raw_peak_contact_force":66.36891,"subtask_id":"push_insertion","tcp_end":[0.4972,-0.06048,0.03742],"tcp_start":[0.50616,0.10979,0.05961],"tcp_to_object_dist_end":0.04629,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80469,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_force_threshold":18.76589,"descend_1.descend_speed":0.06898,"push_1.push_speed":0.07029},"optimized_scores":{"best_composite_score":0.42189,"best_fitness_score":0.38189,"best_task_score":0.22307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.50846,0.0425,0.00861],"force_p95":133.32041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.78917,"mean_force":81.70208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50419,0.04458,0.05344]},{"body_a":"attachment","body_b":"peg","contact_count":483.0,"contact_point_centroid":[0.5133,0.0589,0.05457],"force_p95":132.99453,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.29425,"mean_force":94.00939,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50501,0.05832,0.05542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":471.0,"contact_point_centroid":[0.506,0.10465,0.00939],"force_p95":0.57564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.21987,"mean_force":0.58806,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50593,0.14581,0.10563]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50899,0.12231,0.05883],"force_p95":19.75368,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.75368,"mean_force":19.75368,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50341,0.1328,0.06049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50546,0.10473,0.00936],"force_p95":0.61114,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58776,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50913,0.16968,0.22312]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5003,0.19786,0.29475]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.4749,0.02289,0.02777],"force_p95":0.57373,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58738,"mean_force":0.41863,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49919,-0.03858,0.04136]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50532,0.10467,0.00939],"force_p95":0.57445,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54656,"phase_index":1.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.51428,0.14954,0.15332]}],"total_contact_groups":8},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49778,-0.00059,0.02418],"final_tcp_position":[0.49731,-0.06051,0.03771],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":134.78917,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.10458,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53971,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":305.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_pre_contact","tcp_end":[0.51839,0.14301,0.15706],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":600.0,"object_pos_end":[0.506,0.10468,0.03384],"object_pos_start":[0.50596,0.10458,0.03383],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":0.55165,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":88.0,"raw_peak_contact_force":0.57941,"subtask_id":"approach_pre_contact","tcp_end":[0.51075,0.15857,0.15214],"tcp_start":[0.51839,0.14301,0.15706],"tcp_to_object_dist_end":0.13008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10457,0.03384],"object_pos_start":[0.506,0.10468,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18489,"object_z_max":0.03384,"peak_contact_force":20.21987,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":472.0,"raw_peak_contact_force":20.21987,"subtask_id":"approach_pre_contact","tcp_end":[0.5034,0.13276,0.06033],"tcp_start":[0.51075,0.15857,0.15214],"tcp_to_object_dist_end":0.03876,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,-0.00059,0.02418],"object_pos_start":[0.50597,0.10457,0.03384],"object_to_goal_dist_end":0.081,"object_to_goal_dist_start":0.18477,"object_z_max":0.03908,"peak_contact_force":0.61175,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1053.0,"raw_peak_contact_force":134.78917,"subtask_id":"push_insertion","tcp_end":[0.49731,-0.06051,0.03771],"tcp_start":[0.5034,0.13276,0.06033],"tcp_to_object_dist_end":0.06143,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```