## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 4 | -0.0374 | 0.01 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.037) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.037
- **task_score** (E): 0.009
- **fitness_score**: 0.193  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1646 |
| contact_1 | 1.00 | 0.1132 |
| push_1 | 1.00 | 0.0304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.200, 0.139) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 |
| contact_1 | descend | 1.00 / step_budget | (0.505, 0.200, 0.139)→(0.500, 0.135, 0.048) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 |
| push_1 | push | 1.00 / time_limit | (0.500, 0.135, 0.048)→(0.514, 0.108, 0.050) | (0.502, 0.081, 0.034)→(0.502, 0.079, 0.034) | 0.162→0.159 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.055
- alignment_error: None
- terminal_score: 0.028
- phase_score: 0.341
- phase_breakdown.push_through_score: 0.047
- phase_breakdown.approach_position_score: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.216
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.028
- **Median Q (composite search score)**: -0.042
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31537,"contact_1.contact_speed":0.0792,"push_1.push_duration":7.08532,"push_1.push_speed":0.10083},"optimized_scores":{"best_composite_score":-0.04241,"best_fitness_score":0.18759,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.53428,0.11823,0.05838],"force_p95":3116.62759,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3545.49635,"mean_force":1302.8113,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50393,0.09239,0.02781]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52606,0.09482,0.05969],"force_p95":2948.3639,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3118.21929,"mean_force":1503.24391,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50888,0.08689,0.02439]},{"body_a":"world","body_b":"link7","contact_count":871.0,"contact_point_centroid":[0.49198,0.15039,-7e-05],"force_p95":324.72144,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":571.13616,"mean_force":284.27874,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49892,0.09004,0.05006]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":46.0,"contact_point_centroid":[0.47494,0.11516,0.05963],"force_p95":538.37332,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.19491,"mean_force":433.51161,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.48527,0.11949,0.05769]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":285.0,"contact_point_centroid":[0.46596,0.11996,0.06],"force_p95":369.77125,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":381.58213,"mean_force":232.7464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.503,0.08703,0.05095]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":39.0,"contact_point_centroid":[0.47486,0.10449,0.0327],"force_p95":316.4631,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.19018,"mean_force":213.01441,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48637,0.10223,0.03121]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.49474,0.05906,0.00932],"force_p95":0.64881,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5988,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48311,0.18946,0.21341]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49865,0.19893,0.29361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4941,0.05893,0.0094],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54568,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49841,0.09122,0.04792]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.49407,0.05872,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54626,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.14304,0.08786]}],"total_contact_groups":10},"final_pose_error":0.19089,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49441,0.05896,0.03402],"final_tcp_position":[0.50538,0.08883,0.05097],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.05902,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_position","tcp_end":[0.46894,0.18073,0.13934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16301,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":281.0,"n_steps_budget":870.0,"object_pos_end":[0.49423,0.05903,0.03387],"object_pos_start":[0.49405,0.05902,0.03384],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.13928,"object_z_max":0.03388,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"contact_position","tcp_end":[0.48854,0.11171,0.04789],"tcp_start":[0.46894,0.18073,0.13934],"tcp_to_object_dist_end":0.05481,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49441,0.05896,0.03402],"object_pos_start":[0.49423,0.05903,0.03387],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.13929,"object_z_max":0.03402,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.50538,0.08883,0.05097],"tcp_start":[0.48854,0.11171,0.04789],"tcp_to_object_dist_end":0.03605,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.36358,"contact_1.contact_speed":0.17126,"push_1.push_duration":3.95625,"push_1.push_speed":0.12791},"optimized_scores":{"best_composite_score":-0.05554,"best_fitness_score":0.17446,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":689.0,"contact_point_centroid":[0.52514,0.11934,0.04929],"force_p95":296.5214,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1200.31396,"mean_force":244.31073,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51352,0.11741,0.04889]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.55496,0.11976,0.05954],"force_p95":945.54127,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":974.24642,"mean_force":631.79314,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51385,0.13495,0.01552]},{"body_a":"attachment","body_b":"world","contact_count":20.0,"contact_point_centroid":[0.51083,0.13904,-0.00098],"force_p95":603.14497,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":616.84338,"mean_force":331.89913,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50867,0.13098,0.00655]},{"body_a":"world","body_b":"link7","contact_count":905.0,"contact_point_centroid":[0.50363,0.17957,-0.0001],"force_p95":358.08524,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":595.76953,"mean_force":329.39469,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51282,0.11804,0.04776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":288.0,"contact_point_centroid":[0.50541,0.08092,0.00934],"force_p95":0.59527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59975,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5144,0.19946,0.21297]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50094,0.19969,0.29349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.50605,0.08092,0.00938],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54676,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.51717,0.1683,0.09313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50598,0.08084,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51275,0.11903,0.04555]}],"total_contact_groups":8},"final_pose_error":0.19494,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50595,0.08088,0.03378],"final_tcp_position":[0.51359,0.11512,0.04826],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_position","tcp_end":[0.52822,0.19972,0.13843],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1599,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":211.0,"n_steps_budget":840.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"contact_position","tcp_end":[0.50699,0.13466,0.04813],"tcp_start":[0.52822,0.19972,0.13843],"tcp_to_object_dist_end":0.05568,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.51359,0.11512,0.04826],"tcp_start":[0.50699,0.13466,0.04813],"tcp_to_object_dist_end":0.03795,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11884,"contact_1.contact_speed":0.09426,"push_1.push_duration":5.64652,"push_1.push_speed":0.11788},"optimized_scores":{"best_composite_score":-0.01419,"best_fitness_score":0.21581,"best_task_score":0.0277},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.55449,0.11913,0.05795],"force_p95":1298.84138,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1345.26333,"mean_force":707.44372,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53327,0.13339,0.01207]},{"body_a":"attachment","body_b":"world","contact_count":21.0,"contact_point_centroid":[0.53371,0.1502,-0.00074],"force_p95":567.11946,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":573.1951,"mean_force":322.00325,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53248,0.14162,0.00671]},{"body_a":"world","body_b":"link7","contact_count":903.0,"contact_point_centroid":[0.50869,0.18499,-0.0001],"force_p95":276.06817,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.09377,"mean_force":256.13105,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51626,0.12414,0.04894]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":304.0,"contact_point_centroid":[0.525,0.11999,0.05892],"force_p95":163.08943,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":267.56181,"mean_force":125.19411,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5181,0.11925,0.05038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":981.0,"contact_point_centroid":[0.50583,0.09853,0.00945],"force_p95":0.85923,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.16735,"mean_force":0.68472,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51737,0.1257,0.04628]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.50457,0.12081,0.05646],"force_p95":4.26745,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.08935,"mean_force":2.49464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51327,0.12173,0.05094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":290.0,"contact_point_centroid":[0.50544,0.10453,0.00936],"force_p95":0.60532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58536,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50934,0.21019,0.21336]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50053,0.20031,0.2945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.50601,0.10477,0.00939],"force_p95":0.57506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54628,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.51134,0.19018,0.09327]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52518,0.09803,0.02859],"force_p95":0.41188,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42969,"mean_force":0.25917,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51386,0.11909,0.0507]}],"total_contact_groups":10},"final_pose_error":0.17704,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50573,0.09586,0.03387],"final_tcp_position":[0.52298,0.12004,0.05005],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_position","tcp_end":[0.51869,0.22019,0.13817],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15623,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":206.0,"n_steps_budget":810.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"contact_position","tcp_end":[0.50515,0.15793,0.04846],"tcp_start":[0.51869,0.22019,0.13817],"tcp_to_object_dist_end":0.05533,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50573,0.09586,0.03387],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.17606,"object_to_goal_dist_start":0.18477,"object_z_max":0.03752,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through","tcp_end":[0.52298,0.12004,0.05005],"tcp_start":[0.50515,0.15793,0.04846],"tcp_to_object_dist_end":0.03383,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```