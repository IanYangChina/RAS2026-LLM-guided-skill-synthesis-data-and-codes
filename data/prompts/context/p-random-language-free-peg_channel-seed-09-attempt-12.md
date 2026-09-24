## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2562 | 0.06 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 3 | 0.2503 | 0.00 | ❌ rejected |
| 10 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2612 | 0.04 | ❌ rejected |
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0850 | 0.00 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 5 | -0.1019 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=-0.256) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: -0.256
- **task_score** (E): 0.059
- **fitness_score**: 0.114  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1691 |
| pull_1 | 1.00 | 1.00 | 0.1295 |
| push_1 | 1.00 | 1.00 | 0.2025 |
| descend_1 | 1.00 | 1.00 | 0.1626 |
| descend_2 | 1.00 | 1.00 | 0.0203 |
| grasp_1 | 1.00 | 1.00 | 0.0014 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.499, 0.051, 0.380) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.549 | 4.034 |
| pull_1 | pull | 1.00 / time_limit | (0.499, 0.051, 0.380)→(0.498, -0.075, 0.351) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.546 | 0.552 |
| push_1 | push | 1.00 / time_limit | (0.498, -0.075, 0.351)→(0.496, -0.027, 0.154) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.545 | 0.552 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.027, 0.154)→(0.507, 0.097, 0.051) | (0.502, 0.066, 0.034)→(0.499, 0.073, 0.033) | 0.147→0.153 | 1.00 / 2.333 | 295.300 | 301.572 |
| descend_2 | descend | 1.00 / step_budget | (0.507, 0.097, 0.051)→(0.500, 0.109, 0.037) | (0.499, 0.073, 0.033)→(0.502, 0.045, 0.030) | 0.153→0.126 | 1.00 / 2.000 | 76.156 | 234.419 |
| grasp_1 | grasp | 1.00 / step_budget | (0.500, 0.109, 0.037)→(0.499, 0.109, 0.036) | (0.502, 0.045, 0.030)→(0.502, 0.045, 0.027) | 0.126→0.126 | 1.00 / 2.667 | 69.939 | 94.783 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.262
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.104
- phase_score: 0.149
- phase_breakdown.push_score: 0.064
- phase_breakdown.approach_score: 0.555
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.131
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.104
- **Median Q (composite search score)**: -0.257
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.293


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42051,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":15.05657,"pull_1.pull_distance":0.12003,"push_1.push_depth":0.05798,"push_1.push_distance":0.09333,"push_1.push_speed":0.03937},"optimized_scores":{"best_composite_score":-0.2386,"best_fitness_score":0.1314,"best_task_score":0.10431},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":84.0,"contact_point_centroid":[0.52515,0.08818,0.05993],"force_p95":271.28841,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.06887,"mean_force":230.42056,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50942,0.08817,0.05342]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":122.0,"contact_point_centroid":[0.54572,0.09933,0.05989],"force_p95":251.87283,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.45272,"mean_force":219.19918,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50064,0.09833,0.03689]},{"body_a":"attachment","body_b":"peg","contact_count":216.0,"contact_point_centroid":[0.51627,0.07828,0.05437],"force_p95":163.14004,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":202.70598,"mean_force":130.22731,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50649,0.08177,0.05617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":743.0,"contact_point_centroid":[0.50844,0.06805,0.00909],"force_p95":158.76498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.9924,"mean_force":37.66265,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49955,0.0374,0.09717]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":111.0,"contact_point_centroid":[0.52503,0.09848,0.05999],"force_p95":153.9469,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.09971,"mean_force":141.1717,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50074,0.09829,0.03705]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54578,0.09949,0.05998],"force_p95":87.48053,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.98319,"mean_force":70.79789,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.09848,0.03715]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.52501,0.09868,0.06],"force_p95":36.48382,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.26618,"mean_force":23.9503,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.09848,0.03715]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":132.0,"contact_point_centroid":[0.52529,0.06839,0.05705],"force_p95":36.64035,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.83655,"mean_force":15.57325,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50612,0.08036,0.05656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.50158,0.03791,0.00907],"force_p95":2.05995,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.50711,"mean_force":0.8998,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50233,0.09621,0.04059]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50549,0.08042,0.05391],"force_p95":10.54483,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.66794,"mean_force":7.06573,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50832,0.09073,0.05238]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52504,-0.0025,0.02504],"force_p95":9.57287,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.04528,"mean_force":3.1911,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5007,0.09836,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4993,0.19877,0.29989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50573,0.02087,0.00801],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73,"mean_force":0.60587,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50066,0.09848,0.03715]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47494,0.04298,0.05992],"force_p95":0.68441,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72377,"mean_force":0.41184,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50569,0.0923,0.04774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50601,0.06299,0.00938],"force_p95":0.55194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54651,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]}],"total_contact_groups":17},"final_pose_error":0.00914,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50618,0.02098,0.0241],"final_tcp_position":[0.50069,0.09845,0.03707],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":352.06887,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50593,0.06291,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14323,"object_z_max":0.03384,"peak_contact_force":0.54314,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34588,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06288,0.03386],"object_pos_start":[0.50593,0.06291,0.03384],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14317,"object_z_max":0.03386,"peak_contact_force":0.5494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55442,"tcp_end":[0.49626,-0.02917,0.16761],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.16265,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":743.0,"n_steps_budget":1000.0,"object_pos_end":[0.50024,0.06569,0.03149],"object_pos_start":[0.50594,0.06288,0.03386],"object_to_goal_dist_end":0.14594,"object_to_goal_dist_start":0.14313,"object_z_max":0.03388,"peak_contact_force":352.06887,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1175.0,"raw_peak_contact_force":352.06887,"tcp_end":[0.50849,0.09054,0.05259],"tcp_start":[0.49626,-0.02917,0.16761],"tcp_to_object_dist_end":0.03362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.50581,0.02094,0.0241],"object_pos_start":[0.50024,0.06569,0.03149],"object_to_goal_dist_end":0.10235,"object_to_goal_dist_start":0.14594,"object_z_max":0.04075,"peak_contact_force":224.94361,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":476.0,"raw_peak_contact_force":266.45272,"tcp_end":[0.50069,0.09845,0.03707],"tcp_start":[0.50849,0.09054,0.05259],"tcp_to_object_dist_end":0.07876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50618,0.02098,0.0241],"object_pos_start":[0.50581,0.02094,0.0241],"object_to_goal_dist_end":0.10241,"object_to_goal_dist_start":0.10235,"object_z_max":0.0241,"peak_contact_force":67.86804,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1350.0,"raw_peak_contact_force":94.98319,"tcp_end":[0.50066,0.0985,0.03715],"tcp_start":[0.50069,0.09845,0.03707],"tcp_to_object_dist_end":0.0788,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7093,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":17.46601,"pull_1.pull_distance":0.13979,"push_1.push_depth":0.04434,"push_1.push_distance":0.09312,"push_1.push_speed":0.07965},"optimized_scores":{"best_composite_score":-0.2567,"best_fitness_score":0.1133,"best_task_score":0.07273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":82.0,"contact_point_centroid":[0.52514,0.08155,0.05994],"force_p95":329.82093,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.21546,"mean_force":243.38254,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50935,0.08153,0.05336]},{"body_a":"attachment","body_b":"peg","contact_count":213.0,"contact_point_centroid":[0.51573,0.07168,0.0544],"force_p95":165.43133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":204.69226,"mean_force":125.90627,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50636,0.07524,0.05613]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50852,0.06192,0.00904],"force_p95":160.85943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.10591,"mean_force":39.55229,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49975,0.03809,0.09033]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52508,0.08552,0.05996],"force_p95":159.75118,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.84939,"mean_force":84.9964,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5075,0.08547,0.0501]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":444.0,"contact_point_centroid":[0.54369,0.09032,0.05996],"force_p95":91.32364,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.9352,"mean_force":76.99667,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4985,0.08971,0.03726]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":128.0,"contact_point_centroid":[0.52531,0.06135,0.05703],"force_p95":34.56178,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.20336,"mean_force":16.67787,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50569,0.07337,0.05675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50568,0.01288,0.00805],"force_p95":0.71072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.49319,"mean_force":0.68619,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49851,0.08971,0.03726]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52502,-0.01084,0.02411],"force_p95":9.28196,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.94859,"mean_force":3.01289,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49833,0.08968,0.03713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.506,0.05661,0.00937],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56302,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.1318,0.3483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49926,0.19868,0.29987]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47485,0.03671,0.05959],"force_p95":1.30494,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39133,"mean_force":0.75006,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50689,0.08581,0.04939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":64.0,"contact_point_centroid":[0.49901,0.04066,0.00979],"force_p95":0.70636,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92044,"mean_force":0.39892,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5037,0.08711,0.04463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50611,0.0566,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54674,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05664,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49661,-0.04805,0.24985]}],"total_contact_groups":14},"final_pose_error":0.00489,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50514,0.01319,0.02413],"final_tcp_position":[0.49924,0.08956,0.03795],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":336.21546,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54967,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1008.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.3467,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.54553,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34348,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55015,"tcp_end":[0.49618,-0.02089,0.15304],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.14257,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.49859,0.05376,0.03554],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13384,"object_to_goal_dist_start":0.13687,"object_z_max":0.03496,"peak_contact_force":328.98911,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1094.0,"raw_peak_contact_force":336.21546,"tcp_end":[0.50798,0.08513,0.05068],"tcp_start":[0.49618,-0.02089,0.15304],"tcp_to_object_dist_end":0.03608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":83.0,"n_steps_budget":600.0,"object_pos_end":[0.50414,0.01426,0.02821],"object_pos_start":[0.49859,0.05376,0.03554],"object_to_goal_dist_end":0.09508,"object_to_goal_dist_start":0.13384,"object_z_max":0.04115,"peak_contact_force":0.19513,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":160.84939,"tcp_end":[0.49924,0.08956,0.03795],"tcp_start":[0.50798,0.08513,0.05068],"tcp_to_object_dist_end":0.07609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50514,0.01319,0.02413],"object_pos_start":[0.50414,0.01426,0.02821],"object_to_goal_dist_end":0.09467,"object_to_goal_dist_start":0.09508,"object_z_max":0.02821,"peak_contact_force":70.75999,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":904.0,"raw_peak_contact_force":95.9352,"tcp_end":[0.49868,0.08974,0.03726],"tcp_start":[0.49924,0.08956,0.03795],"tcp_to_object_dist_end":0.07794,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79167,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":14.73746,"pull_1.pull_distance":0.15102,"push_1.push_depth":0.0868,"push_1.push_distance":0.12464,"push_1.push_speed":0.09859},"optimized_scores":{"best_composite_score":-0.2732,"best_fitness_score":0.0968,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":199.0,"contact_point_centroid":[0.52506,0.11955,0.05998],"force_p95":265.41829,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.95525,"mean_force":194.8763,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50861,0.11969,0.05142]},{"body_a":"peg","body_b":"channel_base_body","contact_count":784.0,"contact_point_centroid":[0.49926,0.08669,0.0088],"force_p95":209.36304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.4302,"mean_force":54.36948,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49427,0.04699,0.08435]},{"body_a":"attachment","body_b":"peg","contact_count":286.0,"contact_point_centroid":[0.50875,0.09267,0.05295],"force_p95":212.57524,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":215.99543,"mean_force":147.59325,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49787,0.09343,0.05516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":351.0,"contact_point_centroid":[0.50139,0.09995,0.00839],"force_p95":148.45877,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.35541,"mean_force":115.60722,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50737,0.12389,0.04908]},{"body_a":"attachment","body_b":"peg","contact_count":358.0,"contact_point_centroid":[0.5118,0.11392,0.04942],"force_p95":147.18464,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.22716,"mean_force":114.92295,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50724,0.12416,0.04887]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":419.0,"contact_point_centroid":[0.54737,0.12,0.05997],"force_p95":90.03762,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.43081,"mean_force":76.25276,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.498,0.13754,0.03457]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":352.0,"contact_point_centroid":[0.47439,0.0903,0.01907],"force_p95":41.05435,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.78471,"mean_force":34.93216,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50733,0.12405,0.04899]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49397,0.07995,0.00937],"force_p95":0.57014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.55973,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":93.0,"contact_point_centroid":[0.47492,0.08027,0.02878],"force_p95":2.50605,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.47155,"mean_force":0.64346,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49796,0.13751,0.03459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.49306,0.07982,0.00998],"force_p95":1.53579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.19494,"mean_force":0.55344,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49804,0.13755,0.03463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49929,0.19874,0.29988]},{"body_a":"attachment","body_b":"peg","contact_count":410.0,"contact_point_centroid":[0.49886,0.12559,0.03425],"force_p95":0.37425,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.66761,"mean_force":0.29886,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49804,0.13755,0.03462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.49382,0.07993,0.00938],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55037,"mean_force":0.54669,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49382,0.07998,0.00938],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49661,-0.05274,0.24429]}],"total_contact_groups":14},"final_pose_error":0.00489,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49334,0.10076,0.03194],"final_tcp_position":[0.50009,0.13789,0.03725],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":275.95525,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1007.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54922,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55037,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.35304,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.07995,0.03378],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54143,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.49623,-0.03032,0.14214],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.15461,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.4983,0.10039,0.03344],"object_pos_start":[0.49379,0.07995,0.03378],"object_to_goal_dist_end":0.18051,"object_to_goal_dist_start":0.16019,"object_z_max":0.0338,"peak_contact_force":204.84126,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1070.0,"raw_peak_contact_force":216.4302,"tcp_end":[0.5059,0.11602,0.04933],"tcp_start":[0.49623,-0.03032,0.14214],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":358.0,"n_steps_budget":600.0,"object_pos_end":[0.49486,0.09918,0.03694],"object_pos_start":[0.4983,0.10039,0.03344],"object_to_goal_dist_end":0.17928,"object_to_goal_dist_start":0.18051,"object_z_max":0.03841,"peak_contact_force":3.32902,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1260.0,"raw_peak_contact_force":275.95525,"tcp_end":[0.50009,0.13789,0.03725],"tcp_start":[0.5059,0.11602,0.04933],"tcp_to_object_dist_end":0.03906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49334,0.10076,0.03194],"object_pos_start":[0.49486,0.09918,0.03694],"object_to_goal_dist_end":0.18106,"object_to_goal_dist_start":0.17928,"object_z_max":0.03694,"peak_contact_force":71.1898,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1363.0,"raw_peak_contact_force":93.43081,"tcp_end":[0.49819,0.13761,0.03456],"tcp_start":[0.50009,0.13789,0.03725],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```