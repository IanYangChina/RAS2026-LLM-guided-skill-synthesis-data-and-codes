## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1557 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 3 | -0.0678 | 0.03 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1474 | 0.04 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.156) — your mutation base

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

- **Composite score**: 0.156
- **task_score** (E): 0.002
- **fitness_score**: 0.052  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1993 |
| descend_to_peg | 1.00 | 1.00 | 0.0687 |
| push_along_channel | 0.00 | 1.00 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.107, 0.127) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 2.000 | 18.238 | 18.238 |
| descend_to_peg | descend | 1.00 / force_exceeded | (0.505, 0.107, 0.127)→(0.500, 0.103, 0.060) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 3.000 | 184.241 | 294.187 |
| push_along_channel | push | 0.00 / guard_failure | (0.501, 0.102, 0.059)→(0.502, 0.101, 0.059) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.161 | 1.00 / 1.000 | 0.555 | 3.954 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.004
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.089
- phase_breakdown.approach_peg_score: 0.293
- phase_breakdown.insert_peg_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.054
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: 0.156
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.271


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.16981,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.13599,"descend_to_peg.descend_force_threshold":2.47169,"push_along_channel.push_distance":0.15266,"push_along_channel.push_tolerance":0.01016},"optimized_scores":{"best_composite_score":0.15705,"best_fitness_score":0.05371,"best_task_score":0.00121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49302,0.04791,0.00933],"force_p95":202.91595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.14007,"mean_force":131.5912,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48172,0.08048,0.06022]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49294,0.07656,0.05875],"force_p95":202.57061,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":211.75485,"mean_force":131.6869,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48172,0.08048,0.06022]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.49403,0.05919,0.00939],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.37188,"mean_force":0.57991,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4723,0.08309,0.09266]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49248,0.07689,0.05893],"force_p95":13.83821,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.83821,"mean_force":13.83821,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48124,0.08075,0.06059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":609.0,"contact_point_centroid":[0.4944,0.0589,0.00936],"force_p95":0.56326,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57023,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48167,0.14067,0.20858]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49889,0.19761,0.2962]}],"total_contact_groups":6},"final_pose_error":0.31163,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49483,0.05834,0.03368],"final_tcp_position":[0.48315,0.0797,0.0597],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":212.14007,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05906,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":14.37188,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":408.0,"raw_peak_contact_force":14.37188,"subtask_id":"approach_peg","tcp_end":[0.46599,0.08583,0.12686],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":407.0,"n_steps_budget":630.0,"object_pos_end":[0.49393,0.0589,0.03393],"object_pos_start":[0.49422,0.05906,0.03388],"object_to_goal_dist_end":0.13917,"object_to_goal_dist_start":0.13931,"object_z_max":0.03393,"peak_contact_force":212.14007,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":212.14007,"subtask_id":"approach_peg","tcp_end":[0.48129,0.08074,0.06044],"tcp_start":[0.46599,0.08583,0.12686],"tcp_to_object_dist_end":0.0366,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05877,0.03383],"object_pos_start":[0.49393,0.0589,0.03393],"object_to_goal_dist_end":0.13903,"object_to_goal_dist_start":0.13917,"object_z_max":0.03393,"peak_contact_force":0.54405,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":644.0,"raw_peak_contact_force":4.20518,"subtask_id":"insert_peg","tcp_end":[0.48315,0.0797,0.0597],"tcp_start":[0.48226,0.08017,0.05998],"tcp_to_object_dist_end":0.03503,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.69048,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.21598,"descend_to_peg.descend_force_threshold":10.13573,"push_along_channel.push_distance":0.11465,"push_along_channel.push_tolerance":0.02798},"optimized_scores":{"best_composite_score":0.15357,"best_fitness_score":0.05023,"best_task_score":0.00174},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.5195,0.09305,0.05831],"force_p95":314.13861,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":335.57227,"mean_force":180.49769,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51109,0.10153,0.05923]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51407,0.07375,0.00924],"force_p95":241.30076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":249.64387,"mean_force":159.68427,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51109,0.10153,0.05923]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52536,0.08,0.05821],"force_p95":142.4028,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":142.4028,"mean_force":142.4028,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5121,0.1009,0.05874]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.50603,0.08078,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.1685,"mean_force":0.6229,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51957,0.10403,0.09277]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51878,0.09347,0.05873],"force_p95":21.76561,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.76561,"mean_force":21.76561,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51047,0.10202,0.05995]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.5057,0.08092,0.00936],"force_p95":0.55815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57561,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51489,0.15089,0.2074]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50026,0.1975,0.29524]}],"total_contact_groups":7},"final_pose_error":0.27295,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50719,0.08002,0.03399],"final_tcp_position":[0.5132,0.1003,0.05843],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":335.57227,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":558.0,"n_steps_budget":630.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":22.1685,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":285.0,"raw_peak_contact_force":22.1685,"subtask_id":"approach_peg","tcp_end":[0.52998,0.10644,0.12598],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08086,0.03377],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":5.73325,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":335.57227,"subtask_id":"approach_peg","tcp_end":[0.51041,0.10201,0.05971],"tcp_start":[0.52998,0.10644,0.12598],"tcp_to_object_dist_end":0.03377,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,0.08055,0.03374],"object_pos_start":[0.50596,0.08086,0.03377],"object_to_goal_dist_end":0.16079,"object_to_goal_dist_start":0.16109,"object_z_max":0.0339,"peak_contact_force":0.54457,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":565.0,"raw_peak_contact_force":4.32595,"subtask_id":"insert_peg","tcp_end":[0.5132,0.1003,0.05843],"tcp_start":[0.5121,0.1009,0.05874],"tcp_to_object_dist_end":0.03235,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.72727,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.17717,"descend_to_peg.descend_force_threshold":7.75807,"push_along_channel.push_distance":0.15501,"push_along_channel.push_tolerance":0.02971},"optimized_scores":{"best_composite_score":0.15643,"best_fitness_score":0.0531,"best_task_score":0.00246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51765,0.11839,0.05838],"force_p95":314.2951,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":334.84985,"mean_force":176.5292,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50762,0.12483,0.05953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51315,0.098,0.00926],"force_p95":247.81244,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":256.4045,"mean_force":157.47891,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50762,0.12483,0.05953]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52528,0.10395,0.05822],"force_p95":136.67894,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.67894,"mean_force":136.67894,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5087,0.12426,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":294.0,"contact_point_centroid":[0.50606,0.10448,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.17269,"mean_force":0.60627,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51237,0.12692,0.09338]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51685,0.11872,0.05882],"force_p95":17.76108,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.76108,"mean_force":17.76108,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50692,0.12529,0.06024]},{"body_a":"peg","body_b":"channel_base_body","contact_count":503.0,"contact_point_centroid":[0.50554,0.10467,0.00937],"force_p95":0.57751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56884,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50938,0.16296,0.20885]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50002,0.19824,0.29594]}],"total_contact_groups":7},"final_pose_error":0.31347,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50711,0.10391,0.03393],"final_tcp_position":[0.50984,0.12373,0.05873],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":334.84985,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":530.0,"n_steps_budget":720.0,"object_pos_end":[0.50597,0.10471,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":18.17269,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":295.0,"raw_peak_contact_force":18.17269,"subtask_id":"approach_peg","tcp_end":[0.51957,0.12909,0.12735],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":294.0,"n_steps_budget":600.0,"object_pos_end":[0.50582,0.10462,0.03383],"object_pos_start":[0.50597,0.10471,0.03383],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":334.84985,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":334.84985,"subtask_id":"approach_peg","tcp_end":[0.50689,0.12529,0.06002],"tcp_start":[0.51957,0.12909,0.12735],"tcp_to_object_dist_end":0.03338,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,0.10436,0.03374],"object_pos_start":[0.50582,0.10462,0.03383],"object_to_goal_dist_end":0.18458,"object_to_goal_dist_start":0.18481,"object_z_max":0.03387,"peak_contact_force":0.57517,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":535.0,"raw_peak_contact_force":3.33087,"subtask_id":"insert_peg","tcp_end":[0.50984,0.12373,0.05873],"tcp_start":[0.5087,0.12426,0.05905],"tcp_to_object_dist_end":0.03182,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```