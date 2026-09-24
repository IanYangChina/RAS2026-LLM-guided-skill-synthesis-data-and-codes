## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0749 | 0.16 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1682 | 0.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1108 | 0.20 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2454 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0374 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=0.075) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.075
- **task_score** (E): 0.155
- **fitness_score**: 0.185  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2175 |
| descend_1 | 1.00 | 1.00 | 0.0478 |
| push_1 | 0.00 | 1.00 | 0.0402 |
| retract_1 | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.103, 0.107) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.544 | 2.732 |
| descend_1 | descend | 1.00 / force_exceeded | (0.505, 0.103, 0.107)→(0.500, 0.099, 0.060) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 25.639 | 25.639 |
| push_1 | push | 0.00 / step_budget | (0.500, 0.099, 0.060)→(0.520, 0.077, 0.069) | (0.502, 0.098, 0.034)→(0.490, 0.078, 0.036) | 0.178→0.158 | 1.00 / 4.333 | 265.644 | 771.832 |
| retract_1 | retract | 1.00 / step_budget | (0.520, 0.077, 0.069)→(0.518, 0.077, 0.149) | (0.490, 0.078, 0.036)→(0.501, 0.064, 0.031) | 0.158→0.145 | 1.00 / 1.333 | 0.556 | 419.755 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.411
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.255
- phase_score: 0.246
- phase_breakdown.reach_peg_score: 0.453
- phase_breakdown.push_channel_score: 0.157

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.250
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.255
- **Median Q (composite search score)**: 0.113
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.305


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.53242,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04462,"descend_1.contact_force":4.49358,"descend_1.descend_speed":0.01012,"push_1.push_distance":0.07869,"push_1.push_speed":0.02008,"retract_1.retract_speed":0.06196},"optimized_scores":{"best_composite_score":0.1132,"best_fitness_score":0.2232,"best_task_score":0.20796},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":597.0,"contact_point_centroid":[0.52521,0.08202,0.05293],"force_p95":304.56205,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":880.069,"mean_force":177.03532,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51358,0.0811,0.05322]},{"body_a":"attachment","body_b":"peg","contact_count":960.0,"contact_point_centroid":[0.50541,0.09459,0.05216],"force_p95":209.07697,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":430.13198,"mean_force":136.94007,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51211,0.08227,0.05568]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":58.0,"contact_point_centroid":[0.52505,0.08168,0.0558],"force_p95":237.57283,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.78966,"mean_force":138.04451,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51313,0.08095,0.05589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":847.0,"contact_point_centroid":[0.48997,0.09461,0.00844],"force_p95":214.45801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":341.4512,"mean_force":91.25231,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51241,0.08394,0.05677]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.525,0.11996,0.06],"force_p95":309.37089,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.9156,"mean_force":200.87988,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51312,0.07941,0.0514]},{"body_a":"world","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.51082,0.1393,-5e-05],"force_p95":291.08109,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.38216,"mean_force":222.75943,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51313,0.07944,0.05141]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":814.0,"contact_point_centroid":[0.525,0.11992,0.05147],"force_p95":238.07314,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.45633,"mean_force":195.44731,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51233,0.07942,0.05477]},{"body_a":"world","body_b":"link7","contact_count":509.0,"contact_point_centroid":[0.51192,0.14159,-6e-05],"force_p95":235.58706,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.04249,"mean_force":216.12212,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51311,0.07937,0.05215]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":827.0,"contact_point_centroid":[0.47232,0.09099,0.03932],"force_p95":122.46413,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.80836,"mean_force":73.89336,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51225,0.07989,0.05477]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52692,0.10812,0.05739],"force_p95":142.33208,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.14868,"mean_force":26.60172,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51974,0.10538,0.06143]},{"body_a":"attachment","body_b":"peg","contact_count":141.0,"contact_point_centroid":[0.50329,0.08379,0.06333],"force_p95":141.85652,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":160.08158,"mean_force":86.00161,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51349,0.081,0.06531]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":215.0,"contact_point_centroid":[0.47337,0.08329,0.05887],"force_p95":138.44856,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.83218,"mean_force":58.41874,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51307,0.08044,0.07764]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.50369,0.11172,0.00941],"force_p95":0.59328,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.10793,"mean_force":0.63351,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50253,0.11454,0.08362]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51292,0.11247,0.0588],"force_p95":24.60513,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.60513,"mean_force":24.60513,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50106,0.113,0.06053]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.52522,0.08406,0.04015],"force_p95":17.47398,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.32689,"mean_force":4.90156,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51273,0.07964,0.09738]},{"body_a":"peg","body_b":"world","contact_count":18.0,"contact_point_centroid":[0.50513,0.09695,-0.00015],"force_p95":16.31729,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.87142,"mean_force":5.20115,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50858,0.10121,0.05697]}],"total_contact_groups":19},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50572,0.0785,0.03388],"final_tcp_position":[0.51142,0.079,0.13161],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":880.069,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11177,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54091,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":709.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.5061,0.11654,0.10758],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11175,0.03383],"object_pos_start":[0.50373,0.11177,0.03382],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19191,"object_z_max":0.03389,"peak_contact_force":25.10793,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":276.0,"raw_peak_contact_force":25.10793,"subtask_id":"reach_peg","tcp_end":[0.50106,0.11298,0.06037],"tcp_start":[0.5061,0.11654,0.10758],"tcp_to_object_dist_end":0.02671,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48481,0.08362,0.03513],"object_pos_start":[0.50373,0.11175,0.03383],"object_to_goal_dist_end":0.1644,"object_to_goal_dist_start":0.19189,"object_z_max":0.03523,"peak_contact_force":226.00112,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4596.0,"raw_peak_contact_force":880.069,"subtask_id":"push_channel","tcp_end":[0.51312,0.07939,0.0514],"tcp_start":[0.50106,0.11298,0.06037],"tcp_to_object_dist_end":0.03293,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.50572,0.0785,0.03388],"object_pos_start":[0.48481,0.08362,0.03513],"object_to_goal_dist_end":0.15872,"object_to_goal_dist_start":0.1644,"object_z_max":0.05345,"peak_contact_force":0.55071,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":571.0,"raw_peak_contact_force":358.78966,"tcp_end":[0.51142,0.079,0.13161],"tcp_start":[0.51312,0.07939,0.0514],"tcp_to_object_dist_end":0.09789,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95652,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0492,"descend_1.contact_force":6.24886,"descend_1.descend_speed":0.02972,"push_1.push_distance":0.09886,"push_1.push_speed":0.03707,"retract_1.retract_speed":0.05332},"optimized_scores":{"best_composite_score":0.13966,"best_fitness_score":0.24966,"best_task_score":0.25514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47498,0.11996,0.05976],"force_p95":819.51848,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":830.70174,"mean_force":564.2363,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51428,0.08202,0.06497]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":59.0,"contact_point_centroid":[0.52551,0.09098,0.05986],"force_p95":491.16096,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.44791,"mean_force":290.73102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5149,0.08998,0.06322]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52506,0.08311,0.05997],"force_p95":511.85069,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":521.51267,"mean_force":292.77899,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51429,0.08209,0.065]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.47477,0.11956,0.05982],"force_p95":346.71869,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.51315,"mean_force":199.024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5142,0.08155,0.0657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50427,0.11576,0.00889],"force_p95":237.20474,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":330.26215,"mean_force":119.19715,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51161,0.14495,0.04574]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50638,0.148,0.03813],"force_p95":251.27078,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":330.07594,"mean_force":132.87658,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51161,0.14495,0.04574]},{"body_a":"world","body_b":"link7","contact_count":680.0,"contact_point_centroid":[0.50015,0.22009,-3e-05],"force_p95":185.84795,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":255.41088,"mean_force":146.72889,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51202,0.15536,0.04247]},{"body_a":"peg","body_b":"world","contact_count":225.0,"contact_point_centroid":[0.49326,0.12248,-0.00131],"force_p95":147.77712,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.42361,"mean_force":71.223,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51057,0.14657,0.04064]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52507,0.11971,0.03795],"force_p95":127.97571,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.99668,"mean_force":95.79365,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51293,0.07999,0.06702]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":68.0,"contact_point_centroid":[0.47425,0.07023,0.05829],"force_p95":60.82032,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.52244,"mean_force":26.37971,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51397,0.08243,0.07589]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":576.0,"contact_point_centroid":[0.47484,0.10854,0.01998],"force_p95":65.34875,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.22521,"mean_force":13.67088,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5119,0.14279,0.04493]},{"body_a":"attachment","body_b":"peg","contact_count":55.0,"contact_point_centroid":[0.50502,0.08104,0.06554],"force_p95":70.24234,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.98554,"mean_force":31.42019,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51416,0.08254,0.07163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52688,0.11529,0.05505],"force_p95":61.59001,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.51158,"mean_force":23.96714,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51241,0.11323,0.05827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.49978,0.06757,0.00899],"force_p95":11.20736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.40384,"mean_force":1.84301,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51275,0.08165,0.11468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.49605,0.11901,0.00943],"force_p95":0.61283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.21455,"mean_force":0.60415,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48443,0.12144,0.08303]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49901,0.11792,0.05888],"force_p95":20.68072,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.68072,"mean_force":20.68072,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48732,0.12002,0.0606]}],"total_contact_groups":19},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50068,0.05327,0.02459],"final_tcp_position":[0.51259,0.08165,0.14524],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":830.70174,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11899,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54839,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":685.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48391,0.12348,0.10849],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.1195,0.03385],"object_pos_start":[0.49602,0.11899,0.03392],"object_to_goal_dist_end":0.19963,"object_to_goal_dist_start":0.19913,"object_z_max":0.03398,"peak_contact_force":21.21455,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":331.0,"raw_peak_contact_force":21.21455,"subtask_id":"reach_peg","tcp_end":[0.48734,0.12001,0.06048],"tcp_start":[0.48391,0.12348,0.10849],"tcp_to_object_dist_end":0.02804,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49074,0.08801,0.03965],"object_pos_start":[0.49608,0.1195,0.03385],"object_to_goal_dist_end":0.16827,"object_to_goal_dist_start":0.19963,"object_z_max":0.03964,"peak_contact_force":203.28543,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3634.0,"raw_peak_contact_force":562.44791,"subtask_id":"push_channel","tcp_end":[0.51427,0.08199,0.06497],"tcp_start":[0.48734,0.12001,0.06048],"tcp_to_object_dist_end":0.03509,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.50068,0.05327,0.02459],"object_pos_start":[0.49074,0.08801,0.03965],"object_to_goal_dist_end":0.13416,"object_to_goal_dist_start":0.16827,"object_z_max":0.04858,"peak_contact_force":0.5702,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":341.0,"raw_peak_contact_force":830.70174,"tcp_end":[0.51259,0.08165,0.14524],"tcp_start":[0.51427,0.08199,0.06497],"tcp_to_object_dist_end":0.12451,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76538,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.01117,"descend_1.contact_force":2.00533,"descend_1.descend_speed":0.04869,"push_1.push_distance":0.06428,"push_1.push_speed":0.05769,"retract_1.retract_speed":0.02243},"optimized_scores":{"best_composite_score":-0.02831,"best_fitness_score":0.08169,"best_task_score":0.0029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.5253,0.06677,0.05994],"force_p95":750.98717,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":872.97794,"mean_force":323.96256,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51444,0.06574,0.06283]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":430.0,"contact_point_centroid":[0.52669,0.11993,0.05993],"force_p95":385.86425,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":551.802,"mean_force":365.18414,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5281,0.0697,0.08909]},{"body_a":"attachment","body_b":"peg","contact_count":86.0,"contact_point_centroid":[0.51903,0.07362,0.05706],"force_p95":211.75018,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":332.21135,"mean_force":147.08367,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51388,0.06665,0.0629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.49806,0.0633,0.00919],"force_p95":188.2315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":235.86872,"mean_force":24.59431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52575,0.06919,0.0848]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52558,0.06063,0.05814],"force_p95":148.55132,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.68922,"mean_force":21.91847,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.514,0.06162,0.05901]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52695,0.11996,0.05996],"force_p95":62.89312,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.77312,"mean_force":47.26516,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53208,0.07083,0.08983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.50599,0.06298,0.00938],"force_p95":0.55266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.59549,"mean_force":0.68318,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51699,0.06747,0.08288]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52237,0.06486,0.05872],"force_p95":30.08157,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.08157,"mean_force":30.08157,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51051,0.06544,0.06043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":828.0,"contact_point_centroid":[0.50582,0.06302,0.00937],"force_p95":0.55606,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5629,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51175,0.13258,0.1979]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19811,0.29698]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47467,0.0581,0.0586],"force_p95":0.6474,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76667,"mean_force":0.17394,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52356,0.06742,0.08404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":267.0,"contact_point_centroid":[0.49537,0.06153,0.00941],"force_p95":0.55085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55334,"mean_force":0.54515,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53043,0.07048,0.12751]}],"total_contact_groups":12},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49511,0.06091,0.03403],"final_tcp_position":[0.53027,0.07056,0.1699],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":872.97794,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54199,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":862.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52463,0.0697,0.10541],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":220.0,"n_steps_budget":960.0,"object_pos_end":[0.50604,0.06298,0.03381],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14324,"object_z_max":0.03381,"peak_contact_force":30.59549,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":221.0,"raw_peak_contact_force":30.59549,"subtask_id":"reach_peg","tcp_end":[0.51047,0.06542,0.06024],"tcp_start":[0.52463,0.0697,0.10541],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":780.0,"object_pos_end":[0.49558,0.06095,0.03403],"object_pos_start":[0.50604,0.06298,0.03381],"object_to_goal_dist_end":0.14114,"object_to_goal_dist_start":0.14325,"object_z_max":0.03738,"peak_contact_force":367.64449,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1106.0,"raw_peak_contact_force":872.97794,"subtask_id":"push_channel","tcp_end":[0.53208,0.07079,0.0898],"tcp_start":[0.51047,0.06542,0.06024],"tcp_to_object_dist_end":0.06737,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06091,0.03403],"object_pos_start":[0.49558,0.06095,0.03403],"object_to_goal_dist_end":0.14112,"object_to_goal_dist_start":0.14114,"object_z_max":0.03404,"peak_contact_force":0.54623,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":275.0,"raw_peak_contact_force":69.77312,"tcp_end":[0.53027,0.07056,0.1699],"tcp_start":[0.53208,0.07079,0.0898],"tcp_to_object_dist_end":0.14068,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```