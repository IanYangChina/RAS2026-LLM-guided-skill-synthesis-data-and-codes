## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 11 | 0.0923 | 0.25 | ❌ rejected |
| 2 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 10 | -0.0961 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0697 | 0.63 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0676 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.092) — your mutation base

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

- **Composite score**: 0.092
- **task_score** (E): 0.249
- **fitness_score**: 0.332  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.400
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_peg | 1.00 | 1.00 | 0.1813 |
| descend_to_peg | 1.00 | 1.00 | 0.0818 |
| contact_peg | 1.00 | 1.00 | 0.0008 |
| push_to_goal | 1.00 | 1.00 | 0.0012 |
| retract_up | 1.00 | 1.00 | 0.0780 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.509, 0.120, 0.139) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.565 | 2.488 |
| descend_to_peg | approach | 1.00 / step_budget | (0.509, 0.120, 0.139)→(0.503, 0.107, 0.059) | (0.504, 0.095, 0.034)→(0.502, 0.049, 0.028) | 0.175→0.130 | 1.00 / 2.333 | 281.537 | 336.612 |
| contact_peg | contact | 1.00 / force_exceeded | (0.503, 0.107, 0.059)→(0.502, 0.106, 0.059) | (0.502, 0.049, 0.028)→(0.502, 0.046, 0.026) | 0.130→0.127 | 1.00 / 2.000 | 112.801 | 150.287 |
| push_to_goal | push | 1.00 / force_exceeded | (0.502, 0.106, 0.059)→(0.502, 0.106, 0.058) | (0.502, 0.046, 0.026)→(0.502, 0.046, 0.026) | 0.127→0.127 | 1.00 / 1.667 | 49.989 | 83.233 |
| retract_up | retract | 1.00 / step_budget | (0.502, 0.106, 0.058)→(0.499, 0.105, 0.136) | (0.502, 0.046, 0.026)→(0.503, 0.046, 0.024) | 0.127→0.127 | 1.00 / 1.000 | 0.663 | 281.777 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.276
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.276
- phase_score: 0.413
- phase_breakdown.reach_contact_score: 0.676
- phase_breakdown.push_to_goal_score: 0.036
- phase_breakdown.reach_pre_contact_score: 0.867

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.358
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.336
- **Median Q (composite search score)**: 0.116
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.46494,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.09786,"approach_above_peg.approach_speed":0.04653,"contact_peg.contact_force_threshold":5.38736,"contact_peg.contact_speed":0.03916,"descend_to_peg.descend_offset_y":0.01244,"descend_to_peg.descend_speed":0.01424,"push_to_goal.push_distance":0.1852,"push_to_goal.push_force_threshold":39.75746,"push_to_goal.push_speed":0.02686,"retract_up.retract_height":0.09083,"retract_up.retract_speed":0.02816},"optimized_scores":{"best_composite_score":0.04238,"best_fitness_score":0.28238,"best_task_score":0.13562},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":331.0,"contact_point_centroid":[0.50885,0.17996,-0.00011],"force_p95":237.98378,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.36581,"mean_force":215.86627,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.5057,0.12072,0.05702]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.50813,0.18086,-2e-05],"force_p95":233.48882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.92501,"mean_force":123.77712,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50462,0.12137,0.05695]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50948,0.17956,-7e-05],"force_p95":155.33763,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.33763,"mean_force":155.33763,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50542,0.1217,0.05846]},{"body_a":"peg","body_b":"channel_base_body","contact_count":639.0,"contact_point_centroid":[0.50607,0.08223,0.00872],"force_p95":1.41229,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.34734,"mean_force":3.43638,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50916,0.12211,0.07866]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.50778,0.12185,0.05669],"force_p95":103.27917,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.90687,"mean_force":63.06627,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50836,0.11977,0.06793]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.50869,0.18022,-5e-05],"force_p95":39.85631,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.84228,"mean_force":34.47725,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50494,0.12138,0.05755]},{"body_a":"peg","body_b":"channel_base_body","contact_count":956.0,"contact_point_centroid":[0.50604,0.06002,0.00806],"force_p95":0.68421,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.66077,"mean_force":0.64198,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50205,0.11988,0.09714]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.525,0.08494,0.02423],"force_p95":9.15215,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17503,"mean_force":3.24487,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50192,0.11979,0.10057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":639.0,"contact_point_centroid":[0.50573,0.10463,0.00937],"force_p95":0.57595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56403,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50468,0.17183,0.22108]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50382,0.2188,0.29028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.50616,0.05883,0.00805],"force_p95":0.68549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68738,"mean_force":0.60953,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50499,0.12139,0.05769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50656,0.08483,0.00807],"force_p95":0.52957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52957,"mean_force":0.52957,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50542,0.1217,0.05846]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.08455,0.02412],"force_p95":0.40175,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40175,"mean_force":0.40175,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50547,0.1215,0.05815]}],"total_contact_groups":13},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50517,0.06044,0.02413],"final_tcp_position":[0.50223,0.11995,0.13819],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":252.36581,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55192,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":671.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_pre_contact","tcp_end":[0.52005,0.12922,0.14533],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.50627,0.05983,0.02415],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.14086,"object_to_goal_dist_start":0.18477,"object_z_max":0.04088,"peak_contact_force":237.82502,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1000.0,"raw_peak_contact_force":252.36581,"subtask_id":"reach_contact","tcp_end":[0.50542,0.1217,0.05846],"tcp_start":[0.52005,0.12922,0.14533],"tcp_to_object_dist_end":0.07075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50627,0.05979,0.02414],"object_pos_start":[0.50627,0.05983,0.02415],"object_to_goal_dist_end":0.14082,"object_to_goal_dist_start":0.14086,"object_z_max":0.02415,"peak_contact_force":155.33763,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":155.33763,"subtask_id":"reach_contact","tcp_end":[0.50535,0.1216,0.05851],"tcp_start":[0.50542,0.1217,0.05846],"tcp_to_object_dist_end":0.07073,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05979,0.02413],"object_pos_start":[0.50627,0.05979,0.02414],"object_to_goal_dist_end":0.14082,"object_to_goal_dist_start":0.14082,"object_z_max":0.02414,"peak_contact_force":39.85631,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":46.0,"raw_peak_contact_force":61.84228,"subtask_id":"push_to_goal","tcp_end":[0.50475,0.12136,0.05688],"tcp_start":[0.50535,0.1216,0.05851],"tcp_to_object_dist_end":0.06975,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.50517,0.06044,0.02413],"object_pos_start":[0.50613,0.05979,0.02413],"object_to_goal_dist_end":0.14143,"object_to_goal_dist_start":0.14082,"object_z_max":0.02445,"peak_contact_force":0.68339,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":972.0,"raw_peak_contact_force":237.92501,"tcp_end":[0.50223,0.11995,0.13819],"tcp_start":[0.50475,0.12136,0.05688],"tcp_to_object_dist_end":0.12868,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95431,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.09386,"approach_above_peg.approach_speed":0.04034,"contact_peg.contact_force_threshold":8.44001,"contact_peg.contact_speed":0.0253,"descend_to_peg.descend_offset_y":0.01172,"descend_to_peg.descend_speed":0.0499,"push_to_goal.push_distance":0.16617,"push_to_goal.push_force_threshold":23.31901,"push_to_goal.push_speed":0.05077,"retract_up.retract_height":0.06568,"retract_up.retract_speed":0.02933},"optimized_scores":{"best_composite_score":0.11844,"best_fitness_score":0.35844,"best_task_score":0.27639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":147.0,"contact_point_centroid":[0.50194,0.1431,-0.00018],"force_p95":291.12296,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.58021,"mean_force":254.42194,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49944,0.08376,0.05679]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.50143,0.14429,-2e-05],"force_p95":295.56807,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.05053,"mean_force":162.95925,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49831,0.08587,0.05806]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50258,0.14295,-9e-05],"force_p95":160.39557,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.39557,"mean_force":160.39557,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49914,0.08569,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":433.0,"contact_point_centroid":[0.5029,0.05379,0.00914],"force_p95":1.18205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.26153,"mean_force":2.41814,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49922,0.08633,0.0849]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50044,0.08453,0.05741],"force_p95":88.94915,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.78387,"mean_force":50.40974,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49933,0.08332,0.0688]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50192,0.14363,-3e-05],"force_p95":83.89284,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.48092,"mean_force":46.56146,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49867,0.08568,0.0585]},{"body_a":"peg","body_b":"channel_base_body","contact_count":605.0,"contact_point_centroid":[0.49819,0.02275,0.00804],"force_p95":0.72553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.9095,"mean_force":0.63068,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49572,0.08454,0.08589]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47496,0.04656,0.02431],"force_p95":8.27303,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.53593,"mean_force":1.95602,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49729,0.08572,0.05921]},{"body_a":"peg","body_b":"channel_base_body","contact_count":735.0,"contact_point_centroid":[0.50307,0.06743,0.00935],"force_p95":0.55469,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55835,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49658,0.1566,0.22024]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52502,0.00188,0.03244],"force_p95":1.28602,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28602,"mean_force":1.28602,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49954,0.0831,0.05618]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49608,0.02628,0.00798],"force_p95":0.76943,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76967,"mean_force":0.61087,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49875,0.08554,0.0588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49832,-0.0022,0.00798],"force_p95":0.52357,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52357,"mean_force":0.52357,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49914,0.08569,0.05905]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50192,0.02324,0.02409],"final_tcp_position":[0.49571,0.08448,0.11422],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":322.58021,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54669,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":735.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_pre_contact","tcp_end":[0.50042,0.09404,0.14059],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.49691,0.02268,0.02406],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.10396,"object_to_goal_dist_start":0.14761,"object_z_max":0.04078,"peak_contact_force":277.42478,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":597.0,"raw_peak_contact_force":322.58021,"subtask_id":"reach_contact","tcp_end":[0.49914,0.08569,0.05905],"tcp_start":[0.50042,0.09404,0.14059],"tcp_to_object_dist_end":0.07211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49682,0.02273,0.02406],"object_pos_start":[0.49691,0.02268,0.02406],"object_to_goal_dist_end":0.10401,"object_to_goal_dist_start":0.10396,"object_z_max":0.02406,"peak_contact_force":160.39557,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":160.39557,"subtask_id":"reach_contact","tcp_end":[0.49907,0.08562,0.05912],"tcp_start":[0.49914,0.08569,0.05905],"tcp_to_object_dist_end":0.07204,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.49559,0.02274,0.02406],"object_pos_start":[0.49682,0.02273,0.02406],"object_to_goal_dist_end":0.10407,"object_to_goal_dist_start":0.10401,"object_z_max":0.02406,"peak_contact_force":33.60009,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":17.0,"raw_peak_contact_force":89.48092,"subtask_id":"push_to_goal","tcp_end":[0.49842,0.0858,0.05803],"tcp_start":[0.49907,0.08562,0.05912],"tcp_to_object_dist_end":0.07168,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.50192,0.02324,0.02409],"object_pos_start":[0.49559,0.02274,0.02406],"object_to_goal_dist_end":0.10447,"object_to_goal_dist_start":0.10407,"object_z_max":0.02479,"peak_contact_force":0.72552,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":619.0,"raw_peak_contact_force":317.05053,"tcp_end":[0.49571,0.08448,0.11422],"tcp_start":[0.49842,0.0858,0.05803],"tcp_to_object_dist_end":0.10914,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.51464,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.0828,"approach_above_peg.approach_speed":0.06006,"contact_peg.contact_force_threshold":11.55715,"contact_peg.contact_speed":0.03128,"descend_to_peg.descend_offset_y":0.01054,"descend_to_peg.descend_speed":0.01208,"push_to_goal.push_distance":0.18133,"push_to_goal.push_force_threshold":24.3132,"push_to_goal.push_speed":0.0278,"retract_up.retract_height":0.12553,"retract_up.retract_speed":0.04944},"optimized_scores":{"best_composite_score":0.11596,"best_fitness_score":0.35596,"best_task_score":0.33591},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":317.0,"contact_point_centroid":[0.50487,0.29834,-5e-05],"force_p95":357.39318,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.89036,"mean_force":214.65434,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.49995,0.11364,0.06521]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50642,0.1695,-1e-05],"force_p95":290.35579,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.35579,"mean_force":290.35579,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50202,0.11156,0.05848]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50298,0.27581,-7e-05],"force_p95":135.12838,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.12838,"mean_force":135.12838,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50296,0.11364,0.05967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":928.0,"contact_point_centroid":[0.50185,0.11386,0.00857],"force_p95":113.39765,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.09946,"mean_force":68.17285,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50169,0.1203,0.07325]},{"body_a":"attachment","body_b":"peg","contact_count":654.0,"contact_point_centroid":[0.50129,0.12268,0.05431],"force_p95":114.17902,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.27003,"mean_force":96.01095,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50093,0.11748,0.06503]},{"body_a":"world","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.50803,0.17013,-0.00025],"force_p95":102.39388,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.25019,"mean_force":55.63655,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.50302,0.11339,0.05911]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50661,0.16957,-2e-05],"force_p95":96.18825,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.37474,"mean_force":60.84241,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50213,0.11178,0.0586]},{"body_a":"world","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.50744,0.16992,-3e-05],"force_p95":64.68197,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.89315,"mean_force":44.78141,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5026,0.11284,0.05923]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.50292,0.05298,0.00805],"force_p95":0.65858,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99637,"mean_force":0.6177,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4994,0.11015,0.10641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.50364,0.11164,0.00938],"force_p95":0.61337,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55626,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49898,0.17427,0.2133]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50375,0.20564,0.29957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.5033,0.07956,0.00999],"force_p95":0.39638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40415,"mean_force":0.3246,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50252,0.11283,0.0594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.5033,0.07918,0.00999],"force_p95":0.18533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18701,"mean_force":0.17017,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50216,0.11183,0.05864]}],"total_contact_groups":13},"final_pose_error":0.02928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50328,0.05318,0.02415],"final_tcp_position":[0.49966,0.11027,0.15485],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":434.89036,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11176,0.03379],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59686,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_pre_contact","tcp_end":[0.50676,0.13554,0.13124],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.5031,0.06457,0.03678],"object_pos_start":[0.50368,0.11176,0.03379],"object_to_goal_dist_end":0.14464,"object_to_goal_dist_start":0.1919,"object_z_max":0.04079,"peak_contact_force":329.36008,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1946.0,"raw_peak_contact_force":434.89036,"subtask_id":"reach_contact","tcp_end":[0.50296,0.11364,0.05967],"tcp_start":[0.50676,0.13554,0.13124],"tcp_to_object_dist_end":0.05415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.50298,0.05666,0.03095],"object_pos_start":[0.5031,0.06457,0.03678],"object_to_goal_dist_end":0.13699,"object_to_goal_dist_start":0.14464,"object_z_max":0.03678,"peak_contact_force":22.66967,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12.0,"raw_peak_contact_force":135.12838,"subtask_id":"reach_contact","tcp_end":[0.5022,0.1119,0.05867],"tcp_start":[0.50296,0.11364,0.05967],"tcp_to_object_dist_end":0.06181,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50296,0.05472,0.02901],"object_pos_start":[0.50298,0.05666,0.03095],"object_to_goal_dist_end":0.1352,"object_to_goal_dist_start":0.13699,"object_z_max":0.03095,"peak_contact_force":76.50989,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":98.37474,"subtask_id":"push_to_goal","tcp_end":[0.50202,0.11156,0.05848],"tcp_start":[0.5022,0.1119,0.05867],"tcp_to_object_dist_end":0.06403,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50328,0.05318,0.02415],"object_pos_start":[0.50296,0.05472,0.02901],"object_to_goal_dist_end":0.13416,"object_to_goal_dist_start":0.1352,"object_z_max":0.02901,"peak_contact_force":0.57919,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":999.0,"raw_peak_contact_force":290.35579,"tcp_end":[0.49966,0.11027,0.15485],"tcp_start":[0.50202,0.11156,0.05848],"tcp_to_object_dist_end":0.14267,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```