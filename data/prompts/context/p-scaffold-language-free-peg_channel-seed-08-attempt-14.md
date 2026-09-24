## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1871 | 0.00 | ❌ rejected |
| 13 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.4301 | 0.07 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.2059 | 0.16 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1693 | 0.00 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.2430 | 0.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=-0.187) — your mutation base

```yaml
skill: peg_channel
phases:
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
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
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

- **Composite score**: -0.187
- **task_score** (E): 0.001
- **fitness_score**: 0.103  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1599 |
| descend_1 | 1.00 | 1.00 | 0.0938 |
| contact_1 | 1.00 | 1.00 | 0.0169 |
| push_1 | 0.00 | 1.00 | 0.0011 |
| retract_1 | 1.00 | 1.00 | 0.0869 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.138, 0.156) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.527 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.138, 0.156)→(0.500, 0.087, 0.080) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.531 | 0.610 |
| contact_1 | contact | 1.00 / force_exceeded | (0.500, 0.087, 0.080)→(0.498, 0.083, 0.064) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 19.640 | 19.640 |
| push_1 | push | 0.00 / guard_failure | (0.499, 0.082, 0.063)→(0.500, 0.081, 0.063) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.667 | 61.851 | 193.737 |
| retract_1 | retract | 1.00 / step_budget | (0.500, 0.081, 0.063)→(0.497, 0.095, 0.149) | (0.503, 0.079, 0.034)→(0.503, 0.093, 0.027) | 0.159→0.173 | 1.00 / 1.000 | 0.565 | 37.493 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.006
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.002
- phase_score: 0.184
- phase_breakdown.reach_pre_contact_score: 0.676
- phase_breakdown.push_to_goal_score: 0.061

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.111
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: -0.182
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.242


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52381,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08693,"contact_1.contact_force_threshold":10.0155,"contact_1.contact_speed":0.02957,"descend_1.descend_speed":0.04666,"push_1.push_distance":0.20138,"push_1.push_speed":0.03937,"retract_1.retract_arc_height":0.08999,"retract_1.retract_speed":0.08972},"optimized_scores":{"best_composite_score":-0.20011,"best_fitness_score":0.08989,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.502,0.11998,0.00933],"force_p95":182.29475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":185.554,"mean_force":116.46436,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49039,0.12122,0.06338]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.5013,0.12087,0.05857],"force_p95":181.44616,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.71265,"mean_force":115.89592,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49039,0.12122,0.06338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.4961,0.1191,0.00931],"force_p95":1.31143,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.8826,"mean_force":1.04835,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48977,0.12924,0.07068]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.50241,0.12085,0.05781],"force_p95":17.62924,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.54788,"mean_force":3.12784,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49153,0.12027,0.06242]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.49632,0.11933,0.00944],"force_p95":0.60597,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.78653,"mean_force":0.70801,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49002,0.12311,0.07143]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50089,0.12104,0.05882],"force_p95":16.32156,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.32156,"mean_force":16.32156,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48999,0.1216,0.06376]},{"body_a":"peg","body_b":"world","contact_count":198.0,"contact_point_centroid":[0.49775,0.15541,-0.00164],"force_p95":1.0754,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.0352,"mean_force":0.62836,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48854,0.14092,0.11482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.49656,0.11903,0.00937],"force_p95":0.65659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.57317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49205,0.1854,0.22478]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4994,0.19907,0.29656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":332.0,"contact_point_centroid":[0.4959,0.11903,0.00947],"force_p95":0.59338,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65462,"mean_force":0.53837,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48723,0.14911,0.11853]}],"total_contact_groups":10},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49891,0.15999,0.01417],"final_tcp_position":[0.48877,0.13016,0.14586],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":185.554,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11899,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50812,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":273.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_pre_contact","tcp_end":[0.48578,0.17271,0.15913],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11937,0.03401],"object_pos_start":[0.49603,0.11899,0.03387],"object_to_goal_dist_end":0.1995,"object_to_goal_dist_start":0.19912,"object_z_max":0.03421,"peak_contact_force":0.49988,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":332.0,"raw_peak_contact_force":0.65462,"tcp_end":[0.4911,0.12502,0.07987],"tcp_start":[0.48578,0.17271,0.15913],"tcp_to_object_dist_end":0.04647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":98.0,"n_steps_budget":600.0,"object_pos_end":[0.49599,0.11982,0.03387],"object_pos_start":[0.49603,0.11937,0.03401],"object_to_goal_dist_end":0.19996,"object_to_goal_dist_start":0.1995,"object_z_max":0.03401,"peak_contact_force":16.78653,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":99.0,"raw_peak_contact_force":16.78653,"tcp_end":[0.49002,0.12157,0.06362],"tcp_start":[0.4911,0.12502,0.07987],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49611,0.1197,0.03377],"object_pos_start":[0.49599,0.11982,0.03387],"object_to_goal_dist_end":0.19983,"object_to_goal_dist_start":0.19996,"object_z_max":0.03387,"peak_contact_force":185.554,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":185.554,"subtask_id":"push_to_goal","tcp_end":[0.49163,0.12006,0.06286],"tcp_start":[0.49084,0.12079,0.06313],"tcp_to_object_dist_end":0.02943,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":294.0,"n_steps_budget":720.0,"object_pos_end":[0.49891,0.15999,0.01417],"object_pos_start":[0.49671,0.1191,0.03378],"object_to_goal_dist_end":0.24138,"object_to_goal_dist_start":0.19922,"object_z_max":0.03378,"peak_contact_force":0.60631,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":308.0,"raw_peak_contact_force":28.8826,"tcp_end":[0.48877,0.13016,0.14586],"tcp_start":[0.49163,0.12006,0.06286],"tcp_to_object_dist_end":0.13541,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25309,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05856,"contact_1.contact_force_threshold":7.31609,"contact_1.contact_speed":0.04099,"descend_1.descend_speed":0.05255,"push_1.push_distance":0.1702,"push_1.push_speed":0.02663,"retract_1.retract_arc_height":0.06027,"retract_1.retract_speed":0.05472},"optimized_scores":{"best_composite_score":-0.18225,"best_fitness_score":0.10775,"best_task_score":0.00218},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.51982,0.0516,0.00937],"force_p95":194.86595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":199.09003,"mean_force":163.11571,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5022,0.06629,0.06336]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51314,0.06659,0.05865],"force_p95":194.19649,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.42501,"mean_force":162.43178,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5022,0.06629,0.06336]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.51356,0.06879,0.05958],"force_p95":16.40252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.22524,"mean_force":7.75578,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50287,0.0704,0.06399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50511,0.06468,0.00946],"force_p95":8.20152,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.25039,"mean_force":1.47437,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50064,0.09226,0.10209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":92.0,"contact_point_centroid":[0.50634,0.06302,0.00938],"force_p95":0.55109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.78033,"mean_force":0.80997,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50276,0.06858,0.07153]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51283,0.06674,0.05878],"force_p95":24.29118,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.29118,"mean_force":24.29118,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50188,0.06667,0.06368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52521,0.06334,0.05895],"force_p95":5.61222,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.83405,"mean_force":1.14312,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50135,0.08783,0.07989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.50549,0.06292,0.00934],"force_p95":0.61526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58963,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51145,0.15964,0.22254]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50025,0.19755,0.29526]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.506,0.06312,0.00938],"force_p95":0.55199,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55501,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.513,0.09757,0.1166]}],"total_contact_groups":10},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50623,0.06207,0.03396],"final_tcp_position":[0.5005,0.07965,0.14959],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":199.09003,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54605,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_pre_contact","tcp_end":[0.5231,0.12344,0.15519],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.063,0.03381],"object_pos_start":[0.50596,0.06303,0.03381],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.5485,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":313.0,"raw_peak_contact_force":0.55501,"tcp_end":[0.50459,0.07068,0.07977],"tcp_start":[0.5231,0.12344,0.15519],"tcp_to_object_dist_end":0.04662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":92.0,"n_steps_budget":600.0,"object_pos_end":[0.50603,0.06296,0.03381],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14322,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":24.78033,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":93.0,"raw_peak_contact_force":24.78033,"tcp_end":[0.50188,0.06663,0.06353],"tcp_start":[0.50459,0.07068,0.07977],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.06283,0.03387],"object_pos_start":[0.50603,0.06296,0.03381],"object_to_goal_dist_end":0.14309,"object_to_goal_dist_start":0.14322,"object_z_max":0.034,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":199.09003,"subtask_id":"push_to_goal","tcp_end":[0.50337,0.06521,0.06302],"tcp_start":[0.50261,0.06588,0.06318],"tcp_to_object_dist_end":0.02938,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,0.06207,0.03396],"object_pos_start":[0.50673,0.06228,0.0342],"object_to_goal_dist_end":0.14234,"object_to_goal_dist_start":0.14256,"object_z_max":0.03818,"peak_contact_force":0.54938,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":409.0,"raw_peak_contact_force":46.22524,"tcp_end":[0.5005,0.07965,0.14959],"tcp_start":[0.50337,0.06521,0.06302],"tcp_to_object_dist_end":0.11709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10781,"contact_1.contact_force_threshold":8.90954,"contact_1.contact_speed":0.03003,"descend_1.descend_speed":0.04323,"push_1.push_distance":0.16868,"push_1.push_speed":0.04091,"retract_1.retract_arc_height":0.05397,"retract_1.retract_speed":0.07336},"optimized_scores":{"best_composite_score":-0.17901,"best_fitness_score":0.11099,"best_task_score":0.00152},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50914,0.04641,0.00929],"force_p95":192.87511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":196.56817,"mean_force":128.31242,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50282,0.05994,0.06324]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.51376,0.06021,0.05852],"force_p95":191.8661,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":195.56638,"mean_force":127.57421,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50282,0.05994,0.06324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":356.0,"contact_point_centroid":[0.50585,0.05992,0.00948],"force_p95":20.5703,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.37038,"mean_force":2.79823,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50138,0.08887,0.10216]},{"body_a":"attachment","body_b":"peg","contact_count":55.0,"contact_point_centroid":[0.51387,0.06355,0.05993],"force_p95":30.08537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.10368,"mean_force":14.87515,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50352,0.06641,0.06412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.50598,0.05632,0.00938],"force_p95":0.55647,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.35418,"mean_force":0.73125,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50358,0.06231,0.07149]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51342,0.0604,0.05875],"force_p95":16.89702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.89702,"mean_force":16.89702,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50248,0.06036,0.06362]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52519,0.0537,0.05876],"force_p95":11.73153,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.12855,"mean_force":2.81691,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50245,0.07988,0.07773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.50568,0.05656,0.00933],"force_p95":0.60212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59887,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51485,0.15619,0.22149]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5007,0.19673,0.29398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":313.0,"contact_point_centroid":[0.50619,0.0567,0.00938],"force_p95":0.59493,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62121,"mean_force":0.5462,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51667,0.09159,0.11625]}],"total_contact_groups":10},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5053,0.05572,0.03428],"final_tcp_position":[0.50119,0.07429,0.15057],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":196.56817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52804,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":341.0,"raw_peak_contact_force":4.44541,"subtask_id":"reach_pre_contact","tcp_end":[0.52924,0.1176,0.1545],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05658,0.03379],"object_pos_start":[0.50614,0.0566,0.03377],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13688,"object_z_max":0.03385,"peak_contact_force":0.54398,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":313.0,"raw_peak_contact_force":0.62121,"tcp_end":[0.5056,0.06443,0.07971],"tcp_start":[0.52924,0.1176,0.1545],"tcp_to_object_dist_end":0.04659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":91.0,"n_steps_budget":600.0,"object_pos_end":[0.5061,0.0566,0.03378],"object_pos_start":[0.50613,0.05658,0.03379],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13686,"object_z_max":0.03379,"peak_contact_force":17.35418,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":92.0,"raw_peak_contact_force":17.35418,"tcp_end":[0.50248,0.06032,0.06346],"tcp_start":[0.5056,0.06443,0.07971],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,0.05647,0.03372],"object_pos_start":[0.5061,0.0566,0.03378],"object_to_goal_dist_end":0.13675,"object_to_goal_dist_start":0.13688,"object_z_max":0.03378,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":196.56817,"subtask_id":"push_to_goal","tcp_end":[0.50401,0.05876,0.06282],"tcp_start":[0.50324,0.05948,0.06302],"tcp_to_object_dist_end":0.02928,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":358.0,"n_steps_budget":870.0,"object_pos_end":[0.5053,0.05572,0.03428],"object_pos_start":[0.50684,0.0559,0.03388],"object_to_goal_dist_end":0.13594,"object_to_goal_dist_start":0.13621,"object_z_max":0.03924,"peak_contact_force":0.53983,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":427.0,"raw_peak_contact_force":37.37038,"tcp_end":[0.50119,0.07429,0.15057],"tcp_start":[0.50401,0.05876,0.06282],"tcp_to_object_dist_end":0.11784,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```