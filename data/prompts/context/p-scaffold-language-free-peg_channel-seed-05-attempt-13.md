## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 10 | -0.4983 | 0.00 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0712 | 0.63 | ✅ accepted |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 10 | -0.0100 | 0.43 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.1444 | 0.02 | ❌ rejected |
| 9 | align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2070 | 0.20 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, 0.1046352631789195, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5244002338996304, -0.05536473682108051, 0.04) | final destination targets |
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

## Current Skill (Q=-0.498) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.498
- **task_score** (E): 0.003
- **fitness_score**: 0.092  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1668 |
| approach_1 | 1.00 | 1.00 | 0.1042 |
| contact_1 | 1.00 | 1.00 | 0.0178 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 1.00 | 1.00 | 0.1000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.102, 0.167) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.545 | 2.488 |
| approach_1 | approach | 1.00 / step_budget | (0.509, 0.102, 0.167)→(0.501, 0.095, 0.063) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.564 | 0.589 |
| contact_1 | contact | 1.00 / step_budget | (0.501, 0.095, 0.063)→(0.511, 0.096, 0.048) | (0.504, 0.095, 0.034)→(0.507, 0.095, 0.029) | 0.175→0.175 | 1.00 / 3.000 | 206.965 | 277.214 |
| push_1 | push | 0.00 / guard_failure | (0.511, 0.096, 0.049)→(0.511, 0.096, 0.049) | (0.507, 0.095, 0.029)→(0.507, 0.095, 0.029) | 0.175→0.175 | 1.00 / 3.000 | 164.407 | 164.407 |
| retract_1 | retract | 1.00 / step_budget | (0.511, 0.096, 0.049)→(0.508, 0.096, 0.148) | (0.507, 0.095, 0.029)→(0.505, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.530 | 171.872 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.010
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.010
- phase_score: 0.165
- phase_breakdown.reach_prepush_score: 0.434
- phase_breakdown.achieve_goal_score: 0.050

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.103
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.010
- **Median Q (composite search score)**: -0.504
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.357


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12121,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_height":0.13456,"align_1.speed":0.06644,"approach_1.speed":0.05092,"contact_1.speed":0.02934,"push_1.max_force":53.66526,"push_1.push_distance":0.15659,"push_1.push_duration":2.59319,"push_1.speed":0.02469,"retract_1.retract_height":0.12044,"retract_1.speed":0.06453},"optimized_scores":{"best_composite_score":-0.50405,"best_fitness_score":0.08595,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":159.0,"contact_point_centroid":[0.52508,0.10623,0.05999],"force_p95":247.58172,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":365.83941,"mean_force":201.15335,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51175,0.10633,0.0496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.51992,0.10511,0.00778],"force_p95":188.39532,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.01218,"mean_force":133.65344,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50883,0.10562,0.05227]},{"body_a":"attachment","body_b":"peg","contact_count":404.0,"contact_point_centroid":[0.52091,0.10502,0.05287],"force_p95":187.98472,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":190.50665,"mean_force":137.87524,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50903,0.10566,0.0519]},{"body_a":"peg","body_b":"channel_base_body","contact_count":324.0,"contact_point_centroid":[0.50595,0.1052,0.00926],"force_p95":23.47355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":176.87361,"mean_force":3.74864,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50907,0.10602,0.09893]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.5229,0.10575,0.05451],"force_p95":113.41225,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":176.37443,"mean_force":26.69569,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51102,0.10648,0.05393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52424,0.10638,0.00729],"force_p95":173.4638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.98024,"mean_force":167.52749,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51162,0.10653,0.04889]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.52352,0.10572,0.05099],"force_p95":172.9554,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.47305,"mean_force":167.00593,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51162,0.10653,0.04889]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52503,0.10649,0.06],"force_p95":68.31237,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.935,"mean_force":29.63309,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5116,0.10659,0.04902]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52505,0.10643,0.05999],"force_p95":71.22381,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.88448,"mean_force":63.83667,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51162,0.10653,0.04889]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":220.0,"contact_point_centroid":[0.52509,0.10511,0.05013],"force_p95":19.56082,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.21765,"mean_force":5.48756,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5094,0.10564,0.05145]},{"body_a":"peg","body_b":"channel_base_body","contact_count":503.0,"contact_point_centroid":[0.50554,0.10467,0.00937],"force_p95":0.57751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56884,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50926,0.15398,0.23571]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49987,0.19799,0.29708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50606,0.10467,0.00939],"force_p95":0.57566,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57647,"mean_force":0.54629,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51104,0.10807,0.12171]}],"total_contact_groups":13},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50523,0.10544,0.03379],"final_tcp_position":[0.50872,0.10593,0.14966],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":365.83941,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.10471,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.57517,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":535.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_prepush","tcp_end":[0.51959,0.11168,0.17943],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.10457,0.03384],"object_pos_start":[0.50597,0.10471,0.03383],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.5422,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":381.0,"raw_peak_contact_force":0.57647,"subtask_id":"reach_prepush","tcp_end":[0.50399,0.10478,0.06351],"tcp_start":[0.51959,0.11168,0.17943],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":419.0,"n_steps_budget":660.0,"object_pos_end":[0.50646,0.10553,0.02971],"object_pos_start":[0.50595,0.10457,0.03384],"object_to_goal_dist_end":0.18593,"object_to_goal_dist_start":0.18477,"object_z_max":0.03384,"peak_contact_force":241.80738,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1202.0,"raw_peak_contact_force":365.83941,"subtask_id":"reach_prepush","tcp_end":[0.51162,0.10652,0.04887],"tcp_start":[0.50399,0.10478,0.06351],"tcp_to_object_dist_end":0.01987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50645,0.10554,0.02971],"object_pos_start":[0.50646,0.10553,0.02971],"object_to_goal_dist_end":0.18594,"object_to_goal_dist_start":0.18593,"object_z_max":0.02972,"peak_contact_force":173.98024,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":173.98024,"subtask_id":"achieve_goal","tcp_end":[0.51161,0.10656,0.04892],"tcp_start":[0.51162,0.10654,0.0489],"tcp_to_object_dist_end":0.01992,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.50523,0.10544,0.03379],"object_pos_start":[0.50642,0.10556,0.02972],"object_to_goal_dist_end":0.18562,"object_to_goal_dist_start":0.18595,"object_z_max":0.03384,"peak_contact_force":0.53017,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":368.0,"raw_peak_contact_force":176.87361,"tcp_end":[0.50872,0.10593,0.14966],"tcp_start":[0.51161,0.10656,0.04892],"tcp_to_object_dist_end":0.11593,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.36994,"average_solve_count":346.0,"average_success_count":346.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_height":0.05102,"align_1.speed":0.01011,"approach_1.speed":0.08002,"contact_1.speed":0.00569,"push_1.max_force":59.67917,"push_1.push_distance":0.16121,"push_1.push_duration":4.79529,"push_1.speed":0.03024,"retract_1.retract_height":0.1344,"retract_1.speed":0.01247},"optimized_scores":{"best_composite_score":-0.48678,"best_fitness_score":0.10322,"best_task_score":0.01009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.51742,0.06783,0.0071],"force_p95":171.6039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.73803,"mean_force":124.27907,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50589,0.06866,0.0511]},{"body_a":"attachment","body_b":"peg","contact_count":984.0,"contact_point_centroid":[0.51789,0.06793,0.05175],"force_p95":171.01976,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.82582,"mean_force":125.67462,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50601,0.06866,0.05093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.50553,0.06584,0.00923],"force_p95":28.1721,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":148.6801,"mean_force":5.05556,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50782,0.06844,0.10539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52468,0.06444,0.00693],"force_p95":144.48388,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.8968,"mean_force":141.18985,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51018,0.06878,0.04886]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.5222,0.06774,0.05416],"force_p95":131.49039,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":141.0685,"mean_force":39.34506,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51033,0.06877,0.05359]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.52207,0.0678,0.05064],"force_p95":137.58406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.95743,"mean_force":134.1108,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51018,0.06878,0.04886]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52501,0.06632,0.05357],"force_p95":21.83029,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.02601,"mean_force":8.72805,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50861,0.0687,0.04934]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52503,0.06603,0.05387],"force_p95":17.77367,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.82457,"mean_force":16.76247,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51018,0.06878,0.04886]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52504,0.06606,0.05412],"force_p95":14.39889,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.42954,"mean_force":7.98304,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51042,0.06882,0.04915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":822.0,"contact_point_centroid":[0.50307,0.06749,0.00935],"force_p95":0.55328,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55711,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49887,0.13582,0.19546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.50291,0.06748,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54666,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49853,0.07147,0.08037]}],"total_contact_groups":11},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50558,0.06585,0.03378],"final_tcp_position":[0.50749,0.06839,0.16378],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":180.73803,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":838.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":822.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_prepush","tcp_end":[0.49955,0.07405,0.09751],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":600.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54343,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":0.55077,"subtask_id":"reach_prepush","tcp_end":[0.49873,0.06894,0.06261],"tcp_start":[0.49955,0.07405,0.09751],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.06605,0.02892],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.14663,"object_to_goal_dist_start":0.14762,"object_z_max":0.03381,"peak_contact_force":174.31186,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2061.0,"raw_peak_contact_force":180.73803,"subtask_id":"reach_prepush","tcp_end":[0.51016,0.06879,0.04884],"tcp_start":[0.49873,0.06894,0.06261],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50694,0.06604,0.02894],"object_pos_start":[0.50695,0.06605,0.02892],"object_to_goal_dist_end":0.14663,"object_to_goal_dist_start":0.14663,"object_z_max":0.02898,"peak_contact_force":144.8968,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":144.8968,"subtask_id":"achieve_goal","tcp_end":[0.51026,0.0688,0.04894],"tcp_start":[0.51021,0.06878,0.04889],"tcp_to_object_dist_end":0.02046,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,0.06585,0.03378],"object_pos_start":[0.50695,0.06605,0.02903],"object_to_goal_dist_end":0.14609,"object_to_goal_dist_start":0.14662,"object_z_max":0.03386,"peak_contact_force":0.54332,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":448.0,"raw_peak_contact_force":148.6801,"tcp_end":[0.50749,0.06839,0.16378],"tcp_start":[0.51026,0.0688,0.04894],"tcp_to_object_dist_end":0.13004,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.43056,"average_solve_count":288.0,"average_success_count":288.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.approach_height":0.17955,"align_1.speed":0.02685,"approach_1.speed":0.06756,"contact_1.speed":0.02819,"push_1.max_force":43.44906,"push_1.push_distance":0.08536,"push_1.push_duration":2.07192,"push_1.speed":0.02434,"retract_1.retract_height":0.10389,"retract_1.speed":0.01169},"optimized_scores":{"best_composite_score":-0.50416,"best_fitness_score":0.08584,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52506,0.11367,0.05999],"force_p95":204.00814,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.06472,"mean_force":147.85112,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5116,0.11379,0.04807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.51819,0.11206,0.00754],"force_p95":203.11472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":206.55558,"mean_force":136.05175,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50656,0.11272,0.05174]},{"body_a":"attachment","body_b":"peg","contact_count":407.0,"contact_point_centroid":[0.51867,0.11209,0.05239],"force_p95":202.70602,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":205.69982,"mean_force":139.98766,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50679,0.11277,0.0514]},{"body_a":"peg","body_b":"channel_base_body","contact_count":302.0,"contact_point_centroid":[0.50581,0.11193,0.00917],"force_p95":81.6111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.06212,"mean_force":10.00436,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50917,0.11346,0.08866]},{"body_a":"attachment","body_b":"peg","contact_count":52.0,"contact_point_centroid":[0.52326,0.11314,0.05363],"force_p95":165.61192,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.54365,"mean_force":55.01657,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51138,0.11406,0.05273]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51305,0.11451,0.00708],"force_p95":174.06413,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":174.34526,"mean_force":144.43293,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51145,0.11391,0.04779]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.52335,0.11316,0.05025],"force_p95":173.53125,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.81134,"mean_force":143.97934,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51145,0.11391,0.04779]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.11379,0.06],"force_p95":87.51951,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.5232,"mean_force":72.79121,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51145,0.11391,0.04779]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52501,0.11392,0.06],"force_p95":80.38549,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.81604,"mean_force":53.36138,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51152,0.11405,0.0482]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":155.0,"contact_point_centroid":[0.52508,0.11249,0.05061],"force_p95":12.50748,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.67561,"mean_force":3.95587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51025,0.11342,0.04887]},{"body_a":"peg","body_b":"channel_base_body","contact_count":413.0,"contact_point_centroid":[0.50355,0.11168,0.00935],"force_p95":0.62558,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56404,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50248,0.15888,0.25856]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.50366,0.1117,0.00941],"force_p95":0.59586,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6384,"mean_force":0.54406,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50253,0.11586,0.14278]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49967,0.19921,0.29943]}],"total_contact_groups":13},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50519,0.11239,0.03387],"final_tcp_position":[0.50847,0.11325,0.13206],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":285.06472,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11177,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51305,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":429.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_prepush","tcp_end":[0.50648,0.12037,0.22285],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.11176,0.0338],"object_pos_start":[0.50372,0.11177,0.03384],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.1919,"object_z_max":0.03392,"peak_contact_force":0.60751,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":522.0,"raw_peak_contact_force":0.6384,"subtask_id":"reach_prepush","tcp_end":[0.50037,0.1117,0.06309],"tcp_start":[0.50648,0.12037,0.22285],"tcp_to_object_dist_end":0.0295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":421.0,"n_steps_budget":660.0,"object_pos_end":[0.50674,0.1126,0.02918],"object_pos_start":[0.50378,0.11176,0.0338],"object_to_goal_dist_end":0.19303,"object_to_goal_dist_start":0.1919,"object_z_max":0.0338,"peak_contact_force":204.77641,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1057.0,"raw_peak_contact_force":285.06472,"subtask_id":"reach_prepush","tcp_end":[0.51145,0.11391,0.04778],"tcp_start":[0.50037,0.1117,0.06309],"tcp_to_object_dist_end":0.01923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50673,0.11261,0.02918],"object_pos_start":[0.50674,0.1126,0.02918],"object_to_goal_dist_end":0.19303,"object_to_goal_dist_start":0.19303,"object_z_max":0.02918,"peak_contact_force":174.34526,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":174.34526,"subtask_id":"achieve_goal","tcp_end":[0.51145,0.11394,0.04782],"tcp_start":[0.51146,0.11392,0.0478],"tcp_to_object_dist_end":0.01927,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.50519,0.11239,0.03387],"object_pos_start":[0.5067,0.11262,0.02917],"object_to_goal_dist_end":0.19255,"object_to_goal_dist_start":0.19304,"object_z_max":0.03395,"peak_contact_force":0.51672,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":365.0,"raw_peak_contact_force":190.06212,"tcp_end":[0.50847,0.11325,0.13206],"tcp_start":[0.51145,0.11394,0.04782],"tcp_to_object_dist_end":0.09825,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```