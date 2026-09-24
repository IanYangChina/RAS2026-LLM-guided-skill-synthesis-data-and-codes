## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 3 | -0.1739 | 0.00 | ❌ rejected |
| 10 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1222 | 0.03 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1805 | 0.00 | ❌ rejected |
| 7 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |

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

## Current Skill (Q=-0.174) — your mutation base

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

- **Composite score**: -0.174
- **task_score** (E): 0.000
- **fitness_score**: 0.006  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 0.00 | 1.00 | 0.0411 |
| descend | 0.00 | 1.00 | 0.0103 |
| push | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.173, 0.270) | (0.509, 0.098, 0.040)→(0.474, 0.125, 0.021) | 0.179→0.209 | 1.00 / 2.000 | 289.518 | 765.090 |
| descend | descend | 0.00 / step_budget | (0.505, 0.173, 0.270)→(0.508, 0.175, 0.271) | (0.474, 0.125, 0.021)→(0.470, 0.125, 0.021) | 0.209→0.209 | 1.00 / 2.333 | 96.387 | 96.387 |
| push | push | 0.00 / guard_failure | (0.508, 0.175, 0.271)→(0.508, 0.175, 0.271) | (0.470, 0.125, 0.021)→(0.470, 0.125, 0.021) | 0.209→0.209 | 1.00 / 2.000 | 435.919 | 1131.831 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.011
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.approach_peg_score: 0.057

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.007
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.173
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.289


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43158,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.08537,"push.force_threshold":26.20258,"push.push_distance":0.166},"optimized_scores":{"best_composite_score":-0.17318,"best_fitness_score":0.00682,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":140.0,"contact_point_centroid":[0.52575,0.1199,0.05938],"force_p95":605.96192,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1106.94602,"mean_force":353.44684,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49794,0.25645,0.2112]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":288.0,"contact_point_centroid":[0.52503,0.11994,0.0599],"force_p95":679.91883,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":758.7167,"mean_force":501.73179,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50017,0.18278,0.26786]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":820.0,"contact_point_centroid":[0.47498,0.11997,0.0599],"force_p95":486.57438,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":642.58555,"mean_force":357.16148,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50251,0.17911,0.26898]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":695.0,"contact_point_centroid":[0.47498,0.11997,0.05994],"force_p95":457.75344,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":480.28442,"mean_force":380.86385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50819,0.17593,0.26983]},{"body_a":"peg","body_b":"link6","contact_count":176.0,"contact_point_centroid":[0.50935,0.12546,0.0571],"force_p95":158.94708,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":220.25316,"mean_force":59.48581,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50921,0.25316,0.21835]},{"body_a":"peg","body_b":"world","contact_count":768.0,"contact_point_centroid":[0.47512,0.15792,-0.00188],"force_p95":0.97658,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.81901,"mean_force":3.17901,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51041,0.17902,0.26936]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.525,0.11997,0.0599],"force_p95":179.71664,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":179.71664,"mean_force":179.71664,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50487,0.18404,0.26795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":224.0,"contact_point_centroid":[0.50793,0.11724,0.0092],"force_p95":125.96984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.68847,"mean_force":38.48348,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48747,0.24247,0.19932]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.44209,0.16242,-0.00196],"force_p95":0.68372,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68373,"mean_force":0.60605,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50229,0.17969,0.26885]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.44703,0.18713,-0.00196],"force_p95":0.6837,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6837,"mean_force":0.6837,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50487,0.18404,0.26795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50096,0.19834,0.29649]}],"total_contact_groups":11},"final_pose_error":0.16601,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.44483,0.16226,0.01413],"final_tcp_position":[0.50491,0.18407,0.26798],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1106.94602,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.451,0.16164,0.01413],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.24791,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":482.05164,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2108.0,"raw_peak_contact_force":758.7167,"subtask_id":"approach_peg","tcp_end":[0.50807,0.17356,0.26933],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.26178,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4448,0.16225,0.01412],"object_pos_start":[0.451,0.16164,0.01413],"object_to_goal_dist_end":0.24981,"object_to_goal_dist_start":0.24791,"object_z_max":0.01413,"peak_contact_force":179.71664,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":179.71664,"tcp_end":[0.50487,0.18404,0.26795],"tcp_start":[0.50807,0.17356,0.26933],"tcp_to_object_dist_end":0.26175,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44483,0.16226,0.01413],"object_pos_start":[0.4448,0.16225,0.01412],"object_to_goal_dist_end":0.24981,"object_to_goal_dist_start":0.24981,"object_z_max":0.01412,"peak_contact_force":426.31997,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2019.0,"raw_peak_contact_force":1106.94602,"subtask_id":"push_to_goal","tcp_end":[0.50491,0.18407,0.26798],"tcp_start":[0.50487,0.18404,0.26795],"tcp_to_object_dist_end":0.26177,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43299,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.08838,"push.force_threshold":17.18144,"push.push_distance":0.1593},"optimized_scores":{"best_composite_score":-0.17316,"best_fitness_score":0.00684,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.52606,0.11946,0.05837],"force_p95":915.548,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1119.13834,"mean_force":420.85138,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.40136,0.26685,0.14709]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":292.0,"contact_point_centroid":[0.52504,0.11994,0.05992],"force_p95":683.82233,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":700.15,"mean_force":535.05226,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49848,0.18125,0.26828]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":818.0,"contact_point_centroid":[0.47498,0.11998,0.05995],"force_p95":456.82008,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":688.60308,"mean_force":384.17809,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49625,0.18254,0.26793]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":869.0,"contact_point_centroid":[0.47499,0.11997,0.05991],"force_p95":523.20524,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":635.83222,"mean_force":368.63235,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49671,0.18101,0.26921]},{"body_a":"peg","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.49809,0.13007,0.05436],"force_p95":189.87097,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.75391,"mean_force":109.10128,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.44128,0.26972,0.19195]},{"body_a":"peg","body_b":"world","contact_count":872.0,"contact_point_centroid":[0.47348,0.15494,-0.00193],"force_p95":0.93216,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.89115,"mean_force":5.09205,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49688,0.1863,0.26799]},{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.49138,0.11927,0.0091],"force_p95":142.51422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.34908,"mean_force":31.8674,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.43614,0.23737,0.17037]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":51.0,"contact_point_centroid":[0.47383,0.11949,0.01983],"force_p95":49.69648,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.95053,"mean_force":19.79192,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47854,0.23859,0.24746]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.52502,0.11998,0.05997],"force_p95":48.00953,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.00953,"mean_force":48.00953,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49661,0.18153,0.26836]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.05999],"force_p95":28.84616,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28.84616,"mean_force":28.84616,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49661,0.18153,0.26836]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.45837,0.14976,-0.00194],"force_p95":0.72616,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59905,"mean_force":0.60892,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49697,0.18101,0.26913]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":67.0,"contact_point_centroid":[0.45022,0.11999,0.0142],"force_p95":0.59357,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02822,"mean_force":0.16001,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49573,0.18154,0.2692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.44433,0.12,0.01],"force_p95":0.92087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92797,"mean_force":0.85702,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49998,0.18112,0.26825]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.45188,0.1739,-0.00196],"force_p95":0.60196,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60196,"mean_force":0.60196,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49661,0.18153,0.26836]}],"total_contact_groups":14},"final_pose_error":0.15933,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.45821,0.14974,0.01413],"final_tcp_position":[0.49664,0.18156,0.26835],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1119.13834,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46438,0.15163,0.01413],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.23577,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":385.95648,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2230.0,"raw_peak_contact_force":700.15,"subtask_id":"approach_peg","tcp_end":[0.49653,0.17745,0.27062],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25978,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45818,0.14975,0.01413],"object_pos_start":[0.46438,0.15163,0.01413],"object_to_goal_dist_end":0.23495,"object_to_goal_dist_start":0.23577,"object_z_max":0.0147,"peak_contact_force":48.00953,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":48.00953,"tcp_end":[0.49661,0.18153,0.26836],"tcp_start":[0.49653,0.17745,0.27062],"tcp_to_object_dist_end":0.25908,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.45821,0.14974,0.01413],"object_pos_start":[0.45818,0.14975,0.01413],"object_to_goal_dist_end":0.23494,"object_to_goal_dist_start":0.23495,"object_z_max":0.01413,"peak_contact_force":459.59572,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1960.0,"raw_peak_contact_force":1119.13834,"subtask_id":"push_to_goal","tcp_end":[0.49664,0.18156,0.26835],"tcp_start":[0.49661,0.18153,0.26836],"tcp_to_object_dist_end":0.25907,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49425,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.speed":0.09966,"push.force_threshold":18.14709,"push.push_distance":0.17196},"optimized_scores":{"best_composite_score":-0.17548,"best_fitness_score":0.00452,"best_task_score":8e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link6","contact_count":805.0,"contact_point_centroid":[0.47494,0.11996,0.0599],"force_p95":447.94611,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1169.40719,"mean_force":377.09168,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50431,0.17869,0.26675]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":43.0,"contact_point_centroid":[0.52503,0.11993,0.05987],"force_p95":684.59044,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1006.80323,"mean_force":364.469,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47604,0.25502,0.22114]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":563.0,"contact_point_centroid":[0.52516,0.11993,0.05993],"force_p95":707.81519,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":836.4031,"mean_force":415.09719,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50973,0.16344,0.27226]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":872.0,"contact_point_centroid":[0.47498,0.11998,0.05993],"force_p95":498.91454,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":631.41425,"mean_force":392.68853,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50929,0.16551,0.27193]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.53029,0.12,0.05998],"force_p95":61.43349,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.43349,"mean_force":61.43349,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52318,0.1603,0.27536]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50586,0.06296,0.00937],"force_p95":0.55508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56049,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49921,0.18601,0.25773]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49947,0.19362,0.27976]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,0.06304,0.00939],"force_p95":0.55181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54648,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50995,0.16504,0.2722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.51565,0.05424,0.00939],"force_p95":0.54833,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54857,"mean_force":0.54628,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52326,0.16048,0.27545]}],"total_contact_groups":9},"final_pose_error":0.17161,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50592,0.06291,0.03384],"final_tcp_position":[0.52315,0.16018,0.27531],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1169.40719,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06297,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54545,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2435.0,"raw_peak_contact_force":836.4031,"subtask_id":"approach_peg","tcp_end":[0.51048,0.1674,0.27111],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.25931,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.06302,0.03384],"object_pos_start":[0.50593,0.06297,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14323,"object_z_max":0.03385,"peak_contact_force":61.43349,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7.0,"raw_peak_contact_force":61.43349,"tcp_end":[0.52327,0.16054,0.27548],"tcp_start":[0.51048,0.1674,0.27111],"tcp_to_object_dist_end":0.26114,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.06291,0.03384],"object_pos_start":[0.50607,0.06302,0.03384],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14328,"object_z_max":0.03384,"peak_contact_force":421.84062,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1854.0,"raw_peak_contact_force":1169.40719,"subtask_id":"push_to_goal","tcp_end":[0.52315,0.16018,0.27531],"tcp_start":[0.52327,0.16054,0.27548],"tcp_to_object_dist_end":0.26089,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```