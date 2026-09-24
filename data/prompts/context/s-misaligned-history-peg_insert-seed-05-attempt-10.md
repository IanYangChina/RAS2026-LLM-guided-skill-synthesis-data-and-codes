## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3  | 0.6642 | 0.96 | ❌ rejected |
| 9 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3  | 0.4732 | 0.67 | ❌ rejected |
| 8 | push → retract | linear_cartesian | linear_cartesian | impedance_control | position_control | force_exceeded | pose_tolerance | 4  | 0.6642 | 0.96 | ❌ rejected |
| 7 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3  | 0.6642 | 0.96 | ❌ rejected |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3  | 0.6642 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.96). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5244002338996298, 0.024635263178919502, 0.08]
- Frozen socket pose: [0.5244002338996298, 0.024635263178919502, 0.025] (static fixture for this episode)
- Goal object position: (0.5244002338996298, 0.024635263178919502, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5244, 0.0246, 0.08]
  frozen_socket_position: [0.5244, 0.0246, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5244002338996298, 0.024635263178919502, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5244002338996298, 0.024635263178919502, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.964, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996298, 0.024635263178919502, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5244002338996298, 0.024635263178919502, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.664) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
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
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.664
- **task_score** (E): 0.964
- **fitness_score**: 0.964  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 0.00 | 0.2092 |
| release_1 | 1.00 | 0.67 | 0.0090 |
| pull_1 | 1.00 | 0.00 | 0.1638 |
| release_2 | 1.00 | 0.67 | 0.1629 |
| release_3 | 1.00 | 0.67 | 0.0053 |
| grasp_1 | 1.00 | 1.00 | 0.0026 |
| retract_1 | 0.00 | 0.00 | 0.0993 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.091) | (0.504, -0.000, 0.340)→(0.509, -0.000, 0.129) | 0.260→0.050 | 0.00 / 0.000 | 0.000 | 0.000 |
| release_1 | release | 1.00 / step_budget | (0.496, -0.000, 0.091)→(0.490, -0.000, 0.084) | (0.509, -0.000, 0.129)→(0.504, -0.000, 0.122) | 0.050→0.042 | 0.67 / 0.667 | 18.601 | 21.544 |
| pull_1 | pull | 1.00 / time_limit | (0.490, -0.000, 0.084)→(0.494, 0.052, 0.240) | (0.504, -0.000, 0.122)→(0.501, 0.053, 0.279) | 0.042→0.206 | 0.00 / 0.000 | 0.000 | 45.208 |
| release_2 | release | 1.00 / step_budget | (0.494, 0.052, 0.240)→(0.492, 0.004, 0.084) | (0.501, 0.053, 0.279)→(0.506, 0.004, 0.122) | 0.206→0.042 | 0.67 / 0.667 | 14.738 | 17.143 |
| release_3 | release | 1.00 / time_limit | (0.492, 0.004, 0.084)→(0.493, 0.003, 0.080) | (0.506, 0.004, 0.122)→(0.507, 0.003, 0.117) | 0.042→0.038 | 0.67 / 0.667 | 46.041 | 176.733 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.003, 0.080)→(0.492, 0.003, 0.078) | (0.507, 0.003, 0.117)→(0.506, 0.003, 0.115) | 0.038→0.036 | 1.00 / 1.000 | 50.329 | 55.554 |
| retract_1 | retract | 0.00 / step_budget | (0.492, 0.003, 0.078)→(0.494, 0.003, 0.177) | (0.506, 0.003, 0.115)→(0.506, 0.003, 0.216) | 0.036→0.136 | 0.00 / 0.000 | 0.000 | 89.932 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.969
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.969
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.662
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.306


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5e5af3f51d5f63e3a348998ea00f94a7255959965642a40069d0a7b5ef8ede34`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `cc7f64fba434a86728ba6288ab9746a03660fc43702ba486c544717f06e4937d`; realized-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44633,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.12428,"push_1.push_depth":0.05234,"retract_1.speed":0.05163},"optimized_scores":{"best_composite_score":0.6609,"best_fitness_score":0.9609,"best_task_score":0.9609},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":431.0,"contact_point_centroid":[0.50401,-0.00538,0.07996],"force_p95":195.93546,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.86664,"mean_force":142.68962,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49327,0.00427,0.08396]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.50411,-0.00537,0.07998],"force_p95":70.99155,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.87444,"mean_force":66.55395,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49382,0.00481,0.08386]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.50303,-0.00537,0.07999],"force_p95":40.0979,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.51969,"mean_force":23.86518,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49007,0.00047,0.08476]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50396,-0.00537,0.07999],"force_p95":63.72183,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.13793,"mean_force":48.70954,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49388,0.00505,0.0838]},{"body_a":"attachment","body_b":"peg_socket","contact_count":95.0,"contact_point_centroid":[0.50391,-0.00537,0.07997],"force_p95":28.91664,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28.97878,"mean_force":24.97758,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49071,-0.00015,0.08478]},{"body_a":"attachment","body_b":"peg_socket","contact_count":78.0,"contact_point_centroid":[0.50345,-0.00537,0.07998],"force_p95":16.62573,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":16.65313,"mean_force":14.34822,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49243,0.00397,0.08396]}],"total_contact_groups":6},"final_pose_error":0.1676,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.49614,0.00498,0.179],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":205.86664,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50936,-6e-05,0.12918],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05006,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-7e-05,0.09139],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50449,-0.00012,0.12235],"object_pos_start":[0.50936,-6e-05,0.12918],"object_to_goal_dist_end":0.04259,"object_to_goal_dist_start":0.05006,"object_z_max":0.12918,"peak_contact_force":25.60572,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":95.0,"raw_peak_contact_force":28.97878,"tcp_end":[0.49071,-0.00014,0.0848],"tcp_start":[0.49623,-7e-05,0.09139],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50145,0.05272,0.27884],"object_pos_start":[0.50449,-0.00012,0.12235],"object_to_goal_dist_end":0.20572,"object_to_goal_dist_start":0.04259,"object_z_max":0.27863,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":21.0,"raw_peak_contact_force":68.51969,"tcp_end":[0.4937,0.05241,0.2396],"tcp_start":[0.49071,-0.00014,0.0848],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.00404,0.12156],"object_pos_start":[0.50145,0.05272,0.27884],"object_to_goal_dist_end":0.0422,"object_to_goal_dist_start":0.20572,"object_z_max":0.27898,"peak_contact_force":14.6849,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":78.0,"raw_peak_contact_force":16.65313,"tcp_end":[0.49242,0.00399,0.08397],"tcp_start":[0.4937,0.05241,0.2396],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.50801,0.00457,0.12134],"object_pos_start":[0.5061,0.00404,0.12156],"object_to_goal_dist_end":0.04236,"object_to_goal_dist_start":0.0422,"object_z_max":0.12156,"peak_contact_force":68.05089,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":431.0,"raw_peak_contact_force":205.86664,"tcp_end":[0.49378,0.00453,0.08396],"tcp_start":[0.49242,0.00399,0.08397],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50813,0.00509,0.12117],"object_pos_start":[0.50801,0.00457,0.12134],"object_to_goal_dist_end":0.04227,"object_to_goal_dist_start":0.04236,"object_z_max":0.12134,"peak_contact_force":63.24414,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":71.87444,"tcp_end":[0.49388,0.00504,0.0838],"tcp_start":[0.49378,0.00453,0.08396],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50739,0.00507,0.21738],"object_pos_start":[0.50813,0.00509,0.12117],"object_to_goal_dist_end":0.13767,"object_to_goal_dist_start":0.04227,"object_z_max":0.21728,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":66.13793,"tcp_end":[0.49614,0.00498,0.179],"tcp_start":[0.49388,0.00504,0.0838],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`; realized-scene SHA-256: `8fefb664610d091fa81ee0c279409778edf059cbe39fe254365372fa331a0db3`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44324,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.06761,"push_1.push_depth":0.05727,"retract_1.speed":0.04369},"optimized_scores":{"best_composite_score":0.66949,"best_fitness_score":0.96949,"best_task_score":0.96949},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":82.0,"contact_point_centroid":[0.47299,0.00012,0.0749],"force_p95":120.35494,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.55439,"mean_force":88.64813,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48693,0.00014,0.0695]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.49653,0.01749,0.07997],"force_p95":100.33969,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.14712,"mean_force":70.73816,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49189,0.0034,0.08166]},{"body_a":"attachment","body_b":"peg_socket","contact_count":376.0,"contact_point_centroid":[0.47304,0.00014,0.07079],"force_p95":24.61746,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.15254,"mean_force":21.88836,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48699,0.00018,0.06533]}],"total_contact_groups":3},"final_pose_error":0.1656,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.48935,0.00014,0.16223],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":136.55439,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50936,-6e-05,0.12918],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05006,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-7e-05,0.09139],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50359,-0.00018,0.121],"object_pos_start":[0.50936,-6e-05,0.12918],"object_to_goal_dist_end":0.04116,"object_to_goal_dist_start":0.05006,"object_z_max":0.12918,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4897,-0.0002,0.08349],"tcp_start":[0.49623,-7e-05,0.09139],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5011,0.05297,0.2783],"object_pos_start":[0.50359,-0.00018,0.121],"object_to_goal_dist_end":0.20526,"object_to_goal_dist_start":0.04116,"object_z_max":0.27809,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4933,0.05265,0.23907],"tcp_start":[0.4897,-0.0002,0.08349],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50556,0.00404,0.12078],"object_pos_start":[0.5011,0.05297,0.2783],"object_to_goal_dist_end":0.04135,"object_to_goal_dist_start":0.20526,"object_z_max":0.27844,"peak_contact_force":0.0,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49183,0.004,0.08321],"tcp_start":[0.4933,0.05265,0.23907],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":239.0,"n_steps_budget":600.0,"object_pos_end":[0.50514,0.00034,0.10836],"object_pos_start":[0.50556,0.00404,0.12078],"object_to_goal_dist_end":0.02882,"object_to_goal_dist_start":0.04135,"object_z_max":0.12078,"peak_contact_force":0.0,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":15.0,"raw_peak_contact_force":102.14712,"tcp_end":[0.49105,0.00031,0.07092],"tcp_start":[0.49183,0.004,0.08321],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50156,0.00023,0.10238],"object_pos_start":[0.50514,0.00034,0.10836],"object_to_goal_dist_end":0.02244,"object_to_goal_dist_start":0.02882,"object_z_max":0.10836,"peak_contact_force":21.68718,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":376.0,"raw_peak_contact_force":25.15254,"tcp_end":[0.48701,0.00018,0.06512],"tcp_start":[0.49105,0.00031,0.07092],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,0.0002,0.20049],"object_pos_start":[0.50156,0.00023,0.10238],"object_to_goal_dist_end":0.12049,"object_to_goal_dist_start":0.02244,"object_z_max":0.20038,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":82.0,"raw_peak_contact_force":136.55439,"tcp_end":[0.48935,0.00014,0.16223],"tcp_start":[0.48701,0.00018,0.06512],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`; realized-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56069,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"pull_1.pull_distance":0.05443,"push_1.push_depth":0.06152,"retract_1.speed":0.06389},"optimized_scores":{"best_composite_score":0.66227,"best_fitness_score":0.96227,"best_task_score":0.96227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":431.0,"contact_point_centroid":[0.50796,0.00178,0.07996],"force_p95":214.44348,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.18487,"mean_force":151.64955,"phase_index":4.0,"phase_name":"release_3","phase_type":"release","tcp_position_centroid":[0.49405,0.00384,0.08512]},{"body_a":"attachment","body_b":"peg_socket","contact_count":450.0,"contact_point_centroid":[0.50861,0.00178,0.07998],"force_p95":69.56151,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.6351,"mean_force":67.98737,"phase_index":5.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49471,0.00383,0.08522]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50869,0.00178,0.07999],"force_p95":64.63372,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.10467,"mean_force":50.4505,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4948,0.00387,0.08523]},{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.50444,0.00021,0.07999],"force_p95":40.56582,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.10448,"mean_force":25.31302,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49036,0.00034,0.08515]},{"body_a":"attachment","body_b":"peg_socket","contact_count":103.0,"contact_point_centroid":[0.50503,-0.00029,0.07997],"force_p95":35.55895,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.65352,"mean_force":31.33499,"phase_index":1.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49094,-0.00017,0.08509]},{"body_a":"attachment","body_b":"peg_socket","contact_count":110.0,"contact_point_centroid":[0.50712,0.00178,0.07997],"force_p95":34.67071,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.7772,"mean_force":30.58632,"phase_index":3.0,"phase_name":"release_2","phase_type":"release","tcp_position_centroid":[0.49315,0.00393,0.08498]}],"total_contact_groups":6},"final_pose_error":0.15729,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49767,0.00381,0.19074],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":222.18487,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50936,-6e-05,0.12918],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05006,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-7e-05,0.09139],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50469,-0.00016,0.1227],"object_pos_start":[0.50936,-6e-05,0.12918],"object_to_goal_dist_end":0.04296,"object_to_goal_dist_start":0.05006,"object_z_max":0.12918,"peak_contact_force":30.19722,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":103.0,"raw_peak_contact_force":35.65352,"tcp_end":[0.49094,-0.00017,0.08514],"tcp_start":[0.49623,-7e-05,0.09139],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50153,0.05261,0.27918],"object_pos_start":[0.50469,-0.00016,0.1227],"object_to_goal_dist_end":0.20601,"object_to_goal_dist_start":0.04296,"object_z_max":0.27897,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":24.0,"raw_peak_contact_force":67.10448,"tcp_end":[0.49381,0.0523,0.23993],"tcp_start":[0.49094,-0.00017,0.08514],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,0.00398,0.12264],"object_pos_start":[0.50153,0.05261,0.27918],"object_to_goal_dist_end":0.04336,"object_to_goal_dist_start":0.20601,"object_z_max":0.27931,"peak_contact_force":29.52953,"phase_name":"release_2","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":110.0,"raw_peak_contact_force":34.7772,"tcp_end":[0.49316,0.00393,0.08502],"tcp_start":[0.49381,0.0523,0.23993],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.50876,0.00384,0.12263],"object_pos_start":[0.50675,0.00398,0.12264],"object_to_goal_dist_end":0.04369,"object_to_goal_dist_start":0.04336,"object_z_max":0.12264,"peak_contact_force":70.0717,"phase_name":"release_3","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":431.0,"raw_peak_contact_force":222.18487,"tcp_end":[0.4946,0.0038,0.08522],"tcp_start":[0.49316,0.00393,0.08502],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50897,0.00391,0.12262],"object_pos_start":[0.50876,0.00384,0.12263],"object_to_goal_dist_end":0.04373,"object_to_goal_dist_start":0.04369,"object_z_max":0.12263,"peak_contact_force":66.05693,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":69.6351,"tcp_end":[0.4948,0.00387,0.08522],"tcp_start":[0.4946,0.0038,0.08522],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50836,0.00389,0.22928],"object_pos_start":[0.50897,0.00391,0.12262],"object_to_goal_dist_end":0.14957,"object_to_goal_dist_start":0.04373,"object_z_max":0.22915,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4.0,"raw_peak_contact_force":67.10467,"tcp_end":[0.49767,0.00381,0.19074],"tcp_start":[0.4948,0.00387,0.08522],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```