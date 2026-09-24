## Search State

- **Seed**: 8
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | pull → insert → descend | arc_cartesian | impedance_motion | linear_cartesian | impedance_control | impedance_control | position_control | time_limit | pose_tolerance | contact_detected | 4 | 0.0232 | 0.25 | ✅ accepted |

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

- Task name: door_push
- Frozen realised-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`
- Frozen initial hinge angle: -0.060 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: -0.0604
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=0.023) — your mutation base

```yaml
skill: door_push
phases:
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_angle:
      type: angle
      range:
      - 0.1
      - 1.2
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.023
- **task_score** (E): 0.253
- **fitness_score**: 0.253  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| pull_1 | 1.00 | 0.1715 |
| insert_1 | 1.00 | 0.0502 |
| descend_1 | 0.67 | 0.0050 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| pull_1 | pull | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.100, 0.231, 0.382) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| insert_1 | insert | 1.00 / step_budget | (0.100, 0.231, 0.382)→(0.100, 0.189, 0.355) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |
| descend_1 | descend | 0.67 / step_budget | (0.100, 0.189, 0.355)→(0.100, 0.185, 0.352) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.513
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.513
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.513
- **Median Q (composite search score)**: -0.078
- **K-run variance**: 0.0344
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.281


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23684,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.03862,"insert_1.insertion_depth":0.10906,"insert_1.insertion_force":4.64099,"pull_1.pull_angle":0.64792},"optimized_scores":{"best_composite_score":0.2833,"best_fitness_score":0.5133,"best_task_score":0.5133},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":269.0,"contact_point_centroid":[0.14826,0.19542,0.43264],"force_p95":16.36119,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.73265,"mean_force":11.68284,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.0997,0.25695,0.38929]},{"body_a":"door_panel","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.14574,0.14939,0.41662],"force_p95":18.05319,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.40313,"mean_force":14.31061,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.0996,0.21017,0.3686]},{"body_a":"door_panel","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.14478,0.12692,0.40358],"force_p95":13.23929,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.75551,"mean_force":10.84911,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09968,0.18677,0.35341]},{"body_a":"world","body_b":"door_panel","contact_count":1064.0,"contact_point_centroid":[0.29991,0.19779,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09967,0.31901,0.3813]},{"body_a":"world","body_b":"door_panel","contact_count":152.0,"contact_point_centroid":[0.30333,0.16279,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09958,0.21194,0.36973]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.30618,0.14967,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09968,0.18627,0.3531]}],"total_contact_groups":6},"final_pose_error":0.00494,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09967,0.18451,0.35198],"hinge_angle":0.20857,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.09965,0.23111,0.38257],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45793,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":209.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.09973,0.18865,0.35477],"tcp_start":[0.09965,0.23111,0.38257],"tcp_to_object_dist_end":0.414,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.09967,0.18451,0.35198],"tcp_start":[0.09973,0.18865,0.35477],"tcp_to_object_dist_end":0.40972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23684,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.05707,"insert_1.insertion_depth":0.07123,"insert_1.insertion_force":7.49551,"pull_1.pull_angle":0.68684},"optimized_scores":{"best_composite_score":-0.07841,"best_fitness_score":0.15159,"best_task_score":0.15159},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":102.0,"contact_point_centroid":[0.1455,0.14258,0.41242],"force_p95":18.0612,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.6343,"mean_force":14.49701,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09968,0.20309,0.36377]},{"body_a":"door_panel","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.14477,0.12658,0.40331],"force_p95":13.19605,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.84069,"mean_force":11.9673,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09969,0.18644,0.35314]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.30285,0.16488,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09969,0.32085,0.38037]},{"body_a":"world","body_b":"door_panel","contact_count":188.0,"contact_point_centroid":[0.30359,0.16123,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09967,0.21184,0.36944]},{"body_a":"world","body_b":"door_panel","contact_count":64.0,"contact_point_centroid":[0.30608,0.15003,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.0997,0.1871,0.35358]}],"total_contact_groups":5},"final_pose_error":0.00496,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09968,0.18454,0.35196],"hinge_angle":0.20867,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.09974,0.23065,0.38198],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45723,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":204.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.09974,0.18869,0.35474],"tcp_start":[0.09974,0.23065,0.38198],"tcp_to_object_dist_end":0.41399,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.09968,0.18454,0.35196],"tcp_start":[0.09974,0.18869,0.35474],"tcp_to_object_dist_end":0.40972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23684,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.05205,"insert_1.insertion_depth":0.09134,"insert_1.insertion_force":6.65714,"pull_1.pull_angle":0.91486},"optimized_scores":{"best_composite_score":-0.13532,"best_fitness_score":0.09468,"best_task_score":0.09468},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.14531,0.13775,0.40961],"force_p95":18.81966,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.96288,"mean_force":14.60468,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09971,0.19804,0.36052]},{"body_a":"door_panel","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.14477,0.12663,0.40331],"force_p95":13.20178,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.54143,"mean_force":12.00139,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09969,0.1865,0.35315]},{"body_a":"world","body_b":"door_panel","contact_count":1044.0,"contact_point_centroid":[0.30397,0.15911,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09969,0.32261,0.37943]},{"body_a":"world","body_b":"door_panel","contact_count":188.0,"contact_point_centroid":[0.30412,0.1585,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09969,0.21185,0.36938]},{"body_a":"world","body_b":"door_panel","contact_count":40.0,"contact_point_centroid":[0.30605,0.15017,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09971,0.18743,0.35375]}],"total_contact_groups":5},"final_pose_error":0.00493,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09968,0.18452,0.35194],"hinge_angle":0.20879,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","tcp_end":[0.09974,0.23065,0.38198],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45723,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":201.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.09975,0.18878,0.35476],"tcp_start":[0.09974,0.23065,0.38198],"tcp_to_object_dist_end":0.41406,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.09968,0.18452,0.35194],"tcp_start":[0.09975,0.18878,0.35476],"tcp_to_object_dist_end":0.40969,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```