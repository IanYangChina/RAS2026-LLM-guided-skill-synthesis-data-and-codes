## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0324 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3576 | 0.73 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3601 | 0.73 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3561 | 0.72 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=-0.032) — your mutation base

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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

- **Composite score**: -0.032
- **task_score** (E): 0.002
- **fitness_score**: 0.208  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2013 |
| approach_1 | 1.00 | 1.00 | 0.0702 |
| contact_1 | 1.00 | 1.00 | 0.0002 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.67 | 1.00 | 0.0855 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.100, 0.127) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.536 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.499, 0.100, 0.127)→(0.497, 0.124, 0.061) | (0.501, 0.099, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 47.499 | 55.904 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.124, 0.061)→(0.497, 0.124, 0.061) | (0.501, 0.100, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 20.959 | 20.959 |
| push_1 | push | 0.00 / guard_failure | (0.497, 0.124, 0.061)→(0.497, 0.124, 0.061) | (0.501, 0.100, 0.034)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 35.230 | 35.843 |
| retract_1 | retract | 0.67 / step_budget | (0.497, 0.124, 0.061)→(0.494, 0.132, 0.146) | (0.501, 0.100, 0.034)→(0.506, 0.113, 0.027) | 0.180→0.193 | 1.00 / 1.000 | 0.568 | 36.030 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.002
- phase_score: 0.354
- phase_breakdown.contact_score: 0.878
- phase_breakdown.push_score: 0.000
- phase_breakdown.precontact_score: 0.892

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.213
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.033
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.357


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45536,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00378,"align_1.lateral_offset_y":-0.00541,"approach_1.speed":0.03816,"contact_1.force_threshold":7.69366,"push_1.speed":0.09761,"retract_1.retract_height":0.06579,"retract_1.speed":0.07637},"optimized_scores":{"best_composite_score":-0.02663,"best_fitness_score":0.21337,"best_task_score":0.0022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50331,0.06779,0.00938],"force_p95":0.55073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.28916,"mean_force":2.09454,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50025,0.07989,0.0931]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50836,0.08481,0.05844],"force_p95":65.49912,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.82663,"mean_force":55.09749,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49938,0.09166,0.06209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":492.0,"contact_point_centroid":[0.50179,0.06754,0.00943],"force_p95":0.61419,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.53908,"mean_force":0.93936,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49606,0.09618,0.0889]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49892,0.08456,0.00933],"force_p95":36.42147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.5057,"mean_force":35.6634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49944,0.0922,0.06115]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.5065,0.08473,0.05899],"force_p95":32.41122,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.9722,"mean_force":7.00087,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49849,0.09279,0.06199]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5081,0.08495,0.05801],"force_p95":35.85417,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.93647,"mean_force":35.11346,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49944,0.0922,0.06115]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50832,0.08502,0.05807],"force_p95":31.54358,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.54358,"mean_force":31.54358,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49953,0.09211,0.06131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50894,0.08442,0.00935],"force_p95":31.50973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.50973,"mean_force":31.50973,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49953,0.09211,0.06131]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.50305,0.0675,0.00935],"force_p95":0.55487,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55902,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50074,0.13342,0.20944]}],"total_contact_groups":9},"final_pose_error":0.01008,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5027,0.06711,0.03392],"final_tcp_position":[0.49593,0.09312,0.11738],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":66.28916,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54338,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":695.0,"raw_peak_contact_force":2.06903,"subtask_id":"precontact","tcp_end":[0.50312,0.06947,0.12533],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.50325,0.06764,0.03389],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.1478,"object_to_goal_dist_start":0.14762,"object_z_max":0.03388,"peak_contact_force":66.28916,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":256.0,"raw_peak_contact_force":66.28916,"subtask_id":"contact","tcp_end":[0.49953,0.09211,0.06131],"tcp_start":[0.50312,0.06947,0.12533],"tcp_to_object_dist_end":0.03694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50316,0.06763,0.03386],"object_pos_start":[0.50325,0.06764,0.03389],"object_to_goal_dist_end":0.1478,"object_to_goal_dist_start":0.1478,"object_z_max":0.03389,"peak_contact_force":31.54358,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":31.54358,"subtask_id":"contact","tcp_end":[0.49947,0.09218,0.0612],"tcp_start":[0.49953,0.09211,0.06131],"tcp_to_object_dist_end":0.03692,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06762,0.03383],"object_pos_start":[0.50316,0.06763,0.03386],"object_to_goal_dist_end":0.14778,"object_to_goal_dist_start":0.1478,"object_z_max":0.03386,"peak_contact_force":36.5057,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":36.5057,"subtask_id":"push","tcp_end":[0.49934,0.09225,0.06102],"tcp_start":[0.4994,0.09222,0.0611],"tcp_to_object_dist_end":0.03688,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":492.0,"n_steps_budget":600.0,"object_pos_end":[0.5027,0.06711,0.03392],"object_pos_start":[0.503,0.0676,0.0338],"object_to_goal_dist_end":0.14726,"object_to_goal_dist_start":0.14776,"object_z_max":0.03516,"peak_contact_force":0.54069,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":520.0,"raw_peak_contact_force":36.53908,"tcp_end":[0.49593,0.09312,0.11738],"tcp_start":[0.49934,0.09225,0.06102],"tcp_to_object_dist_end":0.08767,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63462,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00444,"align_1.lateral_offset_y":-0.00562,"approach_1.speed":0.08102,"contact_1.force_threshold":3.5314,"push_1.speed":0.05476,"retract_1.retract_height":0.14753,"retract_1.speed":0.06469},"optimized_scores":{"best_composite_score":-0.03762,"best_fitness_score":0.20238,"best_task_score":0.00258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.5037,0.11167,0.0094],"force_p95":0.60064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.96682,"mean_force":1.27616,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50489,0.12283,0.09386]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.51025,0.1285,0.05845],"force_p95":45.97141,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.43802,"mean_force":34.04487,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50124,0.13545,0.06191]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50254,0.11156,0.00942],"force_p95":0.62937,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.33231,"mean_force":0.70404,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49769,0.14632,0.11365]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50819,0.12883,0.05899],"force_p95":31.20322,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.69649,"mean_force":4.91259,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49989,0.13668,0.06201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.4879,0.11999,0.00923],"force_p95":31.86395,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.94676,"mean_force":31.11868,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,0.13592,0.061]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50989,0.12875,0.0579],"force_p95":31.17089,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.25601,"mean_force":30.40481,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,0.13592,0.061]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51014,0.12877,0.05804],"force_p95":16.09874,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.09874,"mean_force":16.09874,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50122,0.13583,0.06123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51923,0.11999,0.00932],"force_p95":15.87434,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.87434,"mean_force":15.87434,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50122,0.13583,0.06123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.50357,0.11171,0.00937],"force_p95":0.6194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55822,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50437,0.15458,0.20976]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19913,0.29884]}],"total_contact_groups":10},"final_pose_error":0.04162,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50312,0.11132,0.03376],"final_tcp_position":[0.49792,0.1458,0.16803],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":47.96682,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.11181,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19194,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56538,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":607.0,"raw_peak_contact_force":2.06328,"subtask_id":"precontact","tcp_end":[0.51019,0.11175,0.12693],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":232.0,"n_steps_budget":630.0,"object_pos_end":[0.50372,0.11184,0.03374],"object_pos_start":[0.50378,0.11181,0.0338],"object_to_goal_dist_end":0.19198,"object_to_goal_dist_start":0.19194,"object_z_max":0.03392,"peak_contact_force":40.57532,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":237.0,"raw_peak_contact_force":47.96682,"subtask_id":"contact","tcp_end":[0.50122,0.13583,0.06123],"tcp_start":[0.51019,0.11175,0.12693],"tcp_to_object_dist_end":0.03656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50362,0.11184,0.03365],"object_pos_start":[0.50372,0.11184,0.03374],"object_to_goal_dist_end":0.19198,"object_to_goal_dist_start":0.19198,"object_z_max":0.03374,"peak_contact_force":16.09874,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":16.09874,"subtask_id":"contact","tcp_end":[0.50112,0.13589,0.06107],"tcp_start":[0.50122,0.13583,0.06123],"tcp_to_object_dist_end":0.03656,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50352,0.11183,0.03359],"object_pos_start":[0.50362,0.11184,0.03365],"object_to_goal_dist_end":0.19197,"object_to_goal_dist_start":0.19198,"object_z_max":0.03365,"peak_contact_force":31.94676,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":31.94676,"subtask_id":"push","tcp_end":[0.50094,0.13598,0.06083],"tcp_start":[0.50102,0.13594,0.06094],"tcp_to_object_dist_end":0.0365,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50312,0.11132,0.03376],"object_pos_start":[0.50344,0.11181,0.03354],"object_to_goal_dist_end":0.19145,"object_to_goal_dist_start":0.19195,"object_z_max":0.0354,"peak_contact_force":0.52652,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1033.0,"raw_peak_contact_force":34.33231,"tcp_end":[0.49792,0.1458,0.16803],"tcp_start":[0.50094,0.13598,0.06083],"tcp_to_object_dist_end":0.13872,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46154,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00123,"align_1.lateral_offset_y":-0.00561,"approach_1.speed":0.08806,"contact_1.force_threshold":5.15637,"push_1.speed":0.03713,"retract_1.retract_height":0.14599,"retract_1.speed":0.05387},"optimized_scores":{"best_composite_score":-0.03296,"best_fitness_score":0.20704,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":258.0,"contact_point_centroid":[0.49624,0.11914,0.00943],"force_p95":0.62226,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.45622,"mean_force":2.28051,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4868,0.13039,0.09345]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.5,0.13695,0.05814],"force_p95":51.8254,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.97197,"mean_force":40.87124,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49058,0.14308,0.06178]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.47832,0.11997,0.00919],"force_p95":38.9851,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.077,"mean_force":38.15795,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4908,0.14401,0.06043]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50005,0.13764,0.05715],"force_p95":38.2484,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.33774,"mean_force":37.4443,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4908,0.14401,0.06043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":153.0,"contact_point_centroid":[0.4904,0.11991,0.00951],"force_p95":10.31,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.21719,"mean_force":2.30407,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48816,0.14706,0.06685]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49865,0.13797,0.05811],"force_p95":34.24625,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.57668,"mean_force":7.73563,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48973,0.14487,0.06147]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50022,0.13763,0.05731],"force_p95":15.23585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.23585,"mean_force":15.23585,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49091,0.1439,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51178,0.11998,0.00931],"force_p95":15.0755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.0755,"mean_force":15.0755,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49091,0.1439,0.06061]},{"body_a":"peg","body_b":"world","contact_count":845.0,"contact_point_centroid":[0.49976,0.15807,-0.00191],"force_p95":0.72589,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.92087,"mean_force":0.61174,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4873,0.15547,0.11203]},{"body_a":"peg","body_b":"channel_base_body","contact_count":560.0,"contact_point_centroid":[0.49626,0.11905,0.00939],"force_p95":0.61418,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55646,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49158,0.15801,0.21]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49941,0.19872,0.29766]}],"total_contact_groups":11},"final_pose_error":0.05594,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.51179,0.15952,0.01409],"final_tcp_position":[0.48762,0.15614,0.15176],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":53.45622,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11911,0.03409],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50031,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":584.0,"raw_peak_contact_force":2.24822,"subtask_id":"precontact","tcp_end":[0.48509,0.11868,0.12784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.49617,0.11944,0.03366],"object_pos_start":[0.49603,0.11911,0.03409],"object_to_goal_dist_end":0.19957,"object_to_goal_dist_start":0.19923,"object_z_max":0.03412,"peak_contact_force":35.63276,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":269.0,"raw_peak_contact_force":53.45622,"subtask_id":"contact","tcp_end":[0.49091,0.1439,0.06061],"tcp_start":[0.48509,0.11868,0.12784],"tcp_to_object_dist_end":0.03678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49607,0.11943,0.03356],"object_pos_start":[0.49617,0.11944,0.03366],"object_to_goal_dist_end":0.19958,"object_to_goal_dist_start":0.19957,"object_z_max":0.03366,"peak_contact_force":15.23585,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":15.23585,"subtask_id":"contact","tcp_end":[0.49084,0.14398,0.06048],"tcp_start":[0.49091,0.1439,0.06061],"tcp_to_object_dist_end":0.03681,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49596,0.11942,0.03349],"object_pos_start":[0.49607,0.11943,0.03356],"object_to_goal_dist_end":0.19957,"object_to_goal_dist_start":0.19958,"object_z_max":0.03356,"peak_contact_force":37.23891,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":39.077,"subtask_id":"push","tcp_end":[0.49071,0.14408,0.06031],"tcp_start":[0.49077,0.14404,0.06039],"tcp_to_object_dist_end":0.03681,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51179,0.15952,0.01409],"object_pos_start":[0.49587,0.1194,0.03345],"object_to_goal_dist_end":0.2412,"object_to_goal_dist_start":0.19955,"object_z_max":0.03535,"peak_contact_force":0.63701,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1034.0,"raw_peak_contact_force":37.21719,"tcp_end":[0.48762,0.15614,0.15176],"tcp_start":[0.49071,0.14408,0.06031],"tcp_to_object_dist_end":0.13981,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```