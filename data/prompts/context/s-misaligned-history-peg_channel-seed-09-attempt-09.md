## Search State

- **Seed**: 9
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5  | -0.2242 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 10  | -0.3053 | 0.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11  | -0.1283 | 0.00 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 11  | -0.2298 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | contact_detected | time_limit | 4  | -0.2569 | 0.06 | ✅ accepted |

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

## Current Skill (Q=-0.257) — your mutation base

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

- **Composite score**: -0.257
- **task_score** (E): 0.057
- **fitness_score**: 0.113  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1691 |
| pull_1 | 1.00 | 1.00 | 0.1295 |
| push_1 | 1.00 | 1.00 | 0.2030 |
| descend_1 | 1.00 | 1.00 | 0.1636 |
| descend_2 | 0.67 | 0.67 | 0.0207 |
| grasp_1 | 1.00 | 1.00 | 0.0019 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.499, 0.051, 0.380) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.549 | 4.034 |
| pull_1 | pull | 1.00 / time_limit | (0.499, 0.051, 0.380)→(0.498, -0.075, 0.351) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.546 | 0.552 |
| push_1 | push | 1.00 / time_limit | (0.498, -0.075, 0.351)→(0.496, -0.028, 0.154) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.147 | 1.00 / 1.000 | 0.545 | 0.552 |
| descend_1 | descend | 1.00 / step_budget | (0.496, -0.028, 0.154)→(0.507, 0.097, 0.051) | (0.502, 0.066, 0.034)→(0.500, 0.074, 0.033) | 0.147→0.154 | 1.00 / 2.333 | 341.479 | 344.159 |
| descend_2 | descend | 0.67 / step_budget | (0.507, 0.097, 0.051)→(0.501, 0.110, 0.038) | (0.500, 0.074, 0.033)→(0.500, 0.050, 0.034) | 0.154→0.130 | 0.67 / 1.667 | 70.389 | 223.430 |
| grasp_1 | grasp | 1.00 / step_budget | (0.501, 0.110, 0.038)→(0.500, 0.110, 0.036) | (0.500, 0.050, 0.034)→(0.501, 0.047, 0.026) | 0.130→0.128 | 1.00 / 2.667 | 70.195 | 92.527 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.260
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.102
- phase_score: 0.149
- phase_breakdown.approach_score: 0.555
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.064

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.130
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.102
- **Median Q (composite search score)**: -0.258
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41361,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":23.30889,"pull_1.pull_distance":0.1233,"push_1.push_depth":0.05709,"push_1.push_distance":0.15374,"push_1.push_speed":0.05727},"optimized_scores":{"best_composite_score":-0.23973,"best_fitness_score":0.13027,"best_task_score":0.10159},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52515,0.08825,0.05993],"force_p95":307.11071,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.24872,"mean_force":233.0428,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50941,0.08823,0.0534]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":119.0,"contact_point_centroid":[0.5457,0.09922,0.05989],"force_p95":243.75868,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.55657,"mean_force":213.79438,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50064,0.09823,0.03684]},{"body_a":"attachment","body_b":"peg","contact_count":215.0,"contact_point_centroid":[0.51617,0.07838,0.05435],"force_p95":163.07464,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.38847,"mean_force":129.27301,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50648,0.08191,0.05613]},{"body_a":"peg","body_b":"channel_base_body","contact_count":741.0,"contact_point_centroid":[0.50843,0.068,0.00909],"force_p95":159.36356,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.51389,"mean_force":37.31032,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49954,0.03763,0.09717]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":111.0,"contact_point_centroid":[0.52503,0.09819,0.05999],"force_p95":155.83607,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.39344,"mean_force":136.42162,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50094,0.09801,0.0374]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.54576,0.09938,0.05998],"force_p95":85.74442,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.88684,"mean_force":70.27246,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.09838,0.03707]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.52501,0.09858,0.06],"force_p95":40.80428,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.60458,"mean_force":24.91195,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.09838,0.03707]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":132.0,"contact_point_centroid":[0.52529,0.06825,0.05707],"force_p95":37.12149,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.26834,"mean_force":15.92884,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50607,0.08043,0.05656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":217.0,"contact_point_centroid":[0.49744,0.04811,0.00982],"force_p95":0.5318,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.04491,"mean_force":0.61989,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50222,0.09631,0.04029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":445.0,"contact_point_centroid":[0.50296,0.02159,0.00811],"force_p95":0.77621,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.72943,"mean_force":0.63692,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.09839,0.03707]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5053,0.08037,0.0532],"force_p95":8.23165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.38441,"mean_force":6.36451,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50815,0.09113,0.05173]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,0.04541,0.02423],"force_p95":7.16361,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.35488,"mean_force":2.37922,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50068,0.0984,0.03707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4993,0.19877,0.29989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50601,0.06299,0.00938],"force_p95":0.55194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54651,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50599,0.06299,0.00939],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55442,"mean_force":0.54631,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,-0.052,0.25736]}],"total_contact_groups":17},"final_pose_error":0.00878,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50582,0.02132,0.0243],"final_tcp_position":[0.50072,0.09836,0.03699],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":402.24872,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54709,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34683,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50593,0.06291,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14323,"object_z_max":0.03384,"peak_contact_force":0.54314,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34588,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06288,0.03386],"object_pos_start":[0.50593,0.06291,0.03384],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14317,"object_z_max":0.03386,"peak_contact_force":0.5494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55442,"tcp_end":[0.49624,-0.02864,0.16752],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.16227,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.50008,0.06524,0.03157],"object_pos_start":[0.50594,0.06288,0.03386],"object_to_goal_dist_end":0.14548,"object_to_goal_dist_start":0.14313,"object_z_max":0.03388,"peak_contact_force":402.24872,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1171.0,"raw_peak_contact_force":402.24872,"tcp_end":[0.50835,0.09091,0.05198],"tcp_start":[0.49624,-0.02864,0.16752],"tcp_to_object_dist_end":0.03382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":220.0,"n_steps_budget":600.0,"object_pos_end":[0.49965,0.03188,0.03647],"object_pos_start":[0.50008,0.06524,0.03157],"object_to_goal_dist_end":0.11194,"object_to_goal_dist_start":0.14548,"object_z_max":0.04079,"peak_contact_force":208.66928,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":458.0,"raw_peak_contact_force":253.55657,"tcp_end":[0.50072,0.09836,0.03699],"tcp_start":[0.50835,0.09091,0.05198],"tcp_to_object_dist_end":0.06649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50582,0.02132,0.0243],"object_pos_start":[0.49965,0.03188,0.03647],"object_to_goal_dist_end":0.1027,"object_to_goal_dist_start":0.11194,"object_z_max":0.03647,"peak_contact_force":67.93984,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1349.0,"raw_peak_contact_force":92.88684,"tcp_end":[0.50068,0.09841,0.03707],"tcp_start":[0.50072,0.09836,0.03699],"tcp_to_object_dist_end":0.0783,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68421,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":8.86957,"pull_1.pull_distance":0.11117,"push_1.push_depth":0.03906,"push_1.push_distance":0.08459,"push_1.push_speed":0.08192},"optimized_scores":{"best_composite_score":-0.25806,"best_fitness_score":0.11194,"best_task_score":0.06867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":82.0,"contact_point_centroid":[0.52515,0.08237,0.05993],"force_p95":349.09172,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":401.76377,"mean_force":240.43888,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50933,0.08235,0.05328]},{"body_a":"attachment","body_b":"peg","contact_count":207.0,"contact_point_centroid":[0.5159,0.07241,0.05439],"force_p95":163.46672,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":202.16636,"mean_force":128.24307,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50634,0.07601,0.05617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.50849,0.06173,0.00906],"force_p95":159.27613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.45728,"mean_force":39.72898,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49976,0.03958,0.09083]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52506,0.08593,0.05997],"force_p95":121.63354,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":127.87989,"mean_force":59.40367,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50758,0.08588,0.05037]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":412.0,"contact_point_centroid":[0.54359,0.08869,0.05997],"force_p95":90.29842,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.17497,"mean_force":77.87214,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49837,0.08816,0.03731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":133.0,"contact_point_centroid":[0.52532,0.06161,0.05714],"force_p95":38.63939,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.42184,"mean_force":17.29552,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50587,0.07461,0.05661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.50466,0.01291,0.00798],"force_p95":0.77063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.71361,"mean_force":0.6663,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49845,0.08818,0.03741]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52505,0.03667,0.02457],"force_p95":8.9491,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.07351,"mean_force":3.05425,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4994,0.08843,0.03866]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.506,0.05661,0.00937],"force_p95":0.59948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56302,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.1318,0.3483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49926,0.19868,0.29987]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47483,0.0281,0.05781],"force_p95":1.26072,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47588,"mean_force":0.59766,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50644,0.08633,0.04879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":50.0,"contact_point_centroid":[0.50007,0.04114,0.00981],"force_p95":0.68954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89752,"mean_force":0.3639,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50453,0.08691,0.04594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.50611,0.0566,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54674,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05664,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,-0.04658,0.25038]}],"total_contact_groups":14},"final_pose_error":0.00495,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50426,0.01377,0.02405],"final_tcp_position":[0.50075,0.08847,0.04023],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":401.76377,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54967,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1008.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.3467,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50611,0.0566,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.54553,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.34348,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":0.54501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55015,"tcp_end":[0.49625,-0.01792,0.15401],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.1418,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.49966,0.05214,0.0371],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13217,"object_to_goal_dist_start":0.13687,"object_z_max":0.03658,"peak_contact_force":401.76377,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1084.0,"raw_peak_contact_force":401.76377,"tcp_end":[0.50791,0.08564,0.05074],"tcp_start":[0.49625,-0.01792,0.15401],"tcp_to_object_dist_end":0.0371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":67.0,"n_steps_budget":600.0,"object_pos_end":[0.50356,0.01476,0.02886],"object_pos_start":[0.49966,0.05214,0.0371],"object_to_goal_dist_end":0.09548,"object_to_goal_dist_start":0.13217,"object_z_max":0.04107,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":67.0,"raw_peak_contact_force":127.87989,"tcp_end":[0.50075,0.08847,0.04023],"tcp_start":[0.50791,0.08564,0.05074],"tcp_to_object_dist_end":0.07463,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50426,0.01377,0.02405],"object_pos_start":[0.50356,0.01476,0.02886],"object_to_goal_dist_end":0.09521,"object_to_goal_dist_start":0.09548,"object_z_max":0.02886,"peak_contact_force":72.96777,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":868.0,"raw_peak_contact_force":92.17497,"tcp_end":[0.49856,0.08819,0.0373],"tcp_start":[0.50075,0.08847,0.04023],"tcp_to_object_dist_end":0.07581,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79167,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"grasp_1.grip_force":14.64358,"pull_1.pull_distance":0.18644,"push_1.push_depth":0.09841,"push_1.push_distance":0.16269,"push_1.push_speed":0.09999},"optimized_scores":{"best_composite_score":-0.27287,"best_fitness_score":0.09713,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":294.0,"contact_point_centroid":[0.52507,0.11837,0.05997],"force_p95":271.36236,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.85234,"mean_force":223.46856,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50875,0.11851,0.05177]},{"body_a":"peg","body_b":"channel_base_body","contact_count":804.0,"contact_point_centroid":[0.49951,0.08663,0.00872],"force_p95":221.89329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":228.46523,"mean_force":54.9509,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4942,0.04338,0.08307]},{"body_a":"attachment","body_b":"peg","contact_count":298.0,"contact_point_centroid":[0.50857,0.09113,0.05262],"force_p95":225.80675,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.02404,"mean_force":146.82389,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49761,0.09132,0.05493]},{"body_a":"attachment","body_b":"peg","contact_count":444.0,"contact_point_centroid":[0.51404,0.11393,0.04972],"force_p95":157.68968,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.93674,"mean_force":132.10084,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50793,0.12323,0.04945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":437.0,"contact_point_centroid":[0.50353,0.10369,0.00819],"force_p95":156.53137,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.57894,"mean_force":131.17675,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50803,0.12293,0.04964]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":435.0,"contact_point_centroid":[0.5504,0.12,0.05997],"force_p95":85.72798,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.5197,"mean_force":74.94667,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49993,0.14184,0.03418]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":401.0,"contact_point_centroid":[0.47426,0.09537,0.01843],"force_p95":49.11459,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.88332,"mean_force":40.66568,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50804,0.12356,0.0495]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.49397,0.07995,0.00937],"force_p95":0.57014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.55973,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49843,0.13187,0.34825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49929,0.19874,0.29988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.49363,0.0829,0.00998],"force_p95":0.55277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15461,"mean_force":0.44455,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49994,0.14184,0.03419]},{"body_a":"attachment","body_b":"peg","contact_count":422.0,"contact_point_centroid":[0.50073,0.1299,0.03382],"force_p95":0.48726,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.79572,"mean_force":0.29338,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49995,0.14185,0.0342]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.47498,0.12,0.03445],"force_p95":0.91201,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05378,"mean_force":0.28531,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49986,0.14181,0.03411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":787.0,"contact_point_centroid":[0.49382,0.07993,0.00938],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55037,"mean_force":0.54669,"phase_index":1.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49812,-0.01441,0.37954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49382,0.07998,0.00938],"force_p95":0.55021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55021,"mean_force":0.54668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4966,-0.05629,0.24303]}],"total_contact_groups":14},"final_pose_error":0.00484,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49324,0.10501,0.03071],"final_tcp_position":[0.50128,0.14207,0.03587],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":288.85234,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1007.0,"raw_peak_contact_force":3.77147,"tcp_end":[0.49865,0.0507,0.38034],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.34783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":787.0,"n_steps_budget":840.0,"object_pos_end":[0.49382,0.07994,0.03378],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16017,"object_z_max":0.03378,"peak_contact_force":0.54922,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":787.0,"raw_peak_contact_force":0.55037,"tcp_end":[0.4984,-0.07534,0.3508],"tcp_start":[0.49865,0.0507,0.38034],"tcp_to_object_dist_end":0.35304,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.07995,0.03378],"object_pos_start":[0.49382,0.07994,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":0.54143,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55021,"tcp_end":[0.49622,-0.03738,0.13939],"tcp_start":[0.4984,-0.07534,0.3508],"tcp_to_object_dist_end":0.15788,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":804.0,"n_steps_budget":1000.0,"object_pos_end":[0.49947,0.10361,0.03165],"object_pos_start":[0.49379,0.07995,0.03378],"object_to_goal_dist_end":0.1838,"object_to_goal_dist_start":0.16019,"object_z_max":0.03379,"peak_contact_force":220.4242,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1102.0,"raw_peak_contact_force":228.46523,"tcp_end":[0.50581,0.11498,0.04933],"tcp_start":[0.49622,-0.03738,0.13939],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.49531,0.10356,0.03637],"object_pos_start":[0.49947,0.10361,0.03165],"object_to_goal_dist_end":0.18366,"object_to_goal_dist_start":0.1838,"object_z_max":0.03792,"peak_contact_force":2.49878,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1576.0,"raw_peak_contact_force":288.85234,"tcp_end":[0.50128,0.14207,0.03587],"tcp_start":[0.50581,0.11498,0.04933],"tcp_to_object_dist_end":0.03897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49324,0.10501,0.03071],"object_pos_start":[0.49531,0.10356,0.03637],"object_to_goal_dist_end":0.18537,"object_to_goal_dist_start":0.18366,"object_z_max":0.03637,"peak_contact_force":69.67628,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1358.0,"raw_peak_contact_force":92.5197,"tcp_end":[0.50012,0.14191,0.03417],"tcp_start":[0.50128,0.14207,0.03587],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```