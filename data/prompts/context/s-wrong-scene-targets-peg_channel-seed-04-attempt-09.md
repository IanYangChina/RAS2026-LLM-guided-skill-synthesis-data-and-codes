## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3033 | 0.61 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | 0.4253 | 0.01 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.60 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3035 | 0.61 | ✅ accepted |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.0451 | 0.03 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, -0.07909379577485107, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, -0.07909379577485107, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5354444884457894, 0.08090620422514894, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5354444884457894, 0.08090620422514894, 0.04]
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, -0.07909379577485107, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=0.303) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
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

```

## Design Metrics

- **Composite score**: 0.303
- **task_score** (E): 0.606
- **fitness_score**: 0.330  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1819 |
| align_1 | 1.00 | 1.00 | 0.1259 |
| release_1 | 1.00 | 1.00 | 0.1711 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.083, 0.161) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.083, 0.161)→(0.501, 0.120, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.083, 0.034) | 0.165→0.164 | 1.00 / 1.000 | 0.492 | 62.594 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.120, 0.042)→(0.498, -0.051, 0.037) | (0.505, 0.083, 0.034)→(0.506, -0.080, 0.036) | 0.164→0.011 | 1.00 / 4.000 | 86.585 | 101.687 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.051, 0.037)→(0.498, -0.051, 0.037) | (0.506, -0.080, 0.036)→(0.506, -0.080, 0.036) | 0.011→0.011 | 1.00 / 4.000 | 91.639 | 91.639 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.970
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.970
- phase_score: 0.187
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.889
- phase_breakdown.push_score: 0.016

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.501
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.970
- **Median Q (composite search score)**: 0.273
- **K-run variance**: 0.0165
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.255


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,-0.07909,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,-0.07909,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88679,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00364,"align_1.lateral_offset_y":-0.00133,"insert_1.insertion_depth":0.10892,"insert_1.insertion_force":13.25466,"push_1.push_distance":0.10138,"push_1.push_speed":0.09905},"optimized_scores":{"best_composite_score":0.16345,"best_fitness_score":0.19012,"best_task_score":0.30848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":539.0,"contact_point_centroid":[0.54257,-0.00371,0.05999],"force_p95":78.29834,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.76929,"mean_force":58.27246,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4978,-0.00306,0.03683]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54265,-0.04969,0.05998],"force_p95":78.54492,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.54492,"mean_force":78.54492,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.498,-0.05366,0.03663]},{"body_a":"attachment","body_b":"peg","contact_count":863.0,"contact_point_centroid":[0.50387,0.00239,0.04485],"force_p95":23.32169,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.47476,"mean_force":8.23964,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49779,0.014,0.03687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":161.0,"contact_point_centroid":[0.50711,-0.1005,0.05837],"force_p95":24.02939,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.11074,"mean_force":20.49949,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49793,-0.05361,0.03665]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.50665,-0.02273,0.00983],"force_p95":15.86336,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.06881,"mean_force":6.29714,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49787,0.02098,0.03701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":404.0,"contact_point_centroid":[0.50618,0.08073,0.00938],"force_p95":0.59133,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.49328,"mean_force":0.62079,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49781,0.09813,0.09793]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50375,0.09869,0.05877],"force_p95":16.88421,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.08206,"mean_force":15.10359,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49982,0.10988,0.06041]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":395.0,"contact_point_centroid":[0.52508,-0.01614,0.02708],"force_p95":5.57082,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.0509,"mean_force":1.46447,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49779,0.01147,0.03686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49739,0.13766,0.2228]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.19803,0.29724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5069,-0.10048,0.01],"force_p95":1.39766,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39766,"mean_force":1.39766,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.498,-0.05366,0.03663]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50716,-0.06536,0.05623],"force_p95":1.12311,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.12311,"mean_force":1.12311,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.498,-0.05366,0.03663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52421,-0.07899,0.00999],"force_p95":0.39019,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39019,"mean_force":0.39019,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.498,-0.05366,0.03663]}],"total_contact_groups":13},"final_pose_error":0.02664,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50692,-0.08295,0.035],"final_tcp_position":[0.498,-0.05365,0.03663],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":88.76929,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.4968,0.08141,0.15615],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12272,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":404.0,"n_steps_budget":810.0,"object_pos_end":[0.506,0.08078,0.03381],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16101,"object_to_goal_dist_start":0.16113,"object_z_max":0.03383,"peak_contact_force":0.52939,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":406.0,"raw_peak_contact_force":17.49328,"tcp_end":[0.50112,0.1161,0.04088],"tcp_start":[0.4968,0.08141,0.15615],"tcp_to_object_dist_end":0.03636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,-0.08295,0.035],"object_pos_start":[0.506,0.08078,0.03381],"object_to_goal_dist_end":0.00903,"object_to_goal_dist_start":0.16101,"object_z_max":0.03717,"peak_contact_force":74.7477,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2641.0,"raw_peak_contact_force":88.76929,"tcp_end":[0.498,-0.05366,0.03663],"tcp_start":[0.50112,0.1161,0.04088],"tcp_to_object_dist_end":0.03066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50692,-0.08295,0.035],"object_pos_start":[0.50692,-0.08295,0.035],"object_to_goal_dist_end":0.00904,"object_to_goal_dist_start":0.00903,"object_z_max":0.035,"peak_contact_force":78.54492,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":78.54492,"tcp_end":[0.498,-0.05365,0.03663],"tcp_start":[0.498,-0.05366,0.03663],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89286,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00531,"align_1.lateral_offset_y":0.00746,"insert_1.insertion_depth":0.0742,"insert_1.insertion_force":5.56014,"push_1.push_distance":0.12709,"push_1.push_speed":0.09117},"optimized_scores":{"best_composite_score":0.27257,"best_fitness_score":0.29924,"best_task_score":0.5383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.51064,0.12501,0.05618],"force_p95":143.55379,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.73766,"mean_force":93.00291,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50251,0.13196,0.05793]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.50678,0.10574,0.00929],"force_p95":114.85879,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.0575,"mean_force":13.8039,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49844,0.11054,0.09817]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.54288,-0.00795,0.05999],"force_p95":76.44093,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":82.35926,"mean_force":56.77463,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49815,-0.00729,0.03683]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54266,-0.03573,0.05998],"force_p95":78.76479,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.76479,"mean_force":78.76479,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04043,0.0367]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":72.0,"contact_point_centroid":[0.52515,0.10548,0.0423],"force_p95":19.75791,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.94904,"mean_force":5.57903,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50371,0.13514,0.05357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":746.0,"contact_point_centroid":[0.50594,-0.0162,0.00989],"force_p95":13.93705,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.64522,"mean_force":5.04656,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49852,0.02767,0.03704]},{"body_a":"attachment","body_b":"peg","contact_count":887.0,"contact_point_centroid":[0.50363,0.01983,0.04246],"force_p95":13.47004,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.41999,"mean_force":4.07687,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49845,0.03148,0.03694]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":586.0,"contact_point_centroid":[0.52505,0.00174,0.02554],"force_p95":3.93626,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.86472,"mean_force":1.00425,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4985,0.02977,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4974,0.13861,0.22457]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49938,0.19833,0.29774]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50329,-0.05212,0.04119],"force_p95":0.58997,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.58997,"mean_force":0.58997,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04043,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50701,-0.08458,0.00999],"force_p95":0.54648,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54648,"mean_force":0.54648,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04043,0.0367]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.06925,0.03588],"force_p95":0.41224,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41224,"mean_force":0.41224,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04043,0.0367]}],"total_contact_groups":13},"final_pose_error":0.03975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.06935,0.03676],"final_tcp_position":[0.49806,-0.04043,0.0367],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":169.73766,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49682,0.08278,0.159],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12739,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":870.0,"object_pos_end":[0.50639,0.10218,0.03519],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18236,"object_to_goal_dist_start":0.18484,"object_z_max":0.03528,"peak_contact_force":0.40001,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":604.0,"raw_peak_contact_force":169.73766,"tcp_end":[0.50325,0.13955,0.04186],"tcp_start":[0.49682,0.08278,0.159],"tcp_to_object_dist_end":0.0381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.06935,0.03676],"object_pos_start":[0.50639,0.10218,0.03519],"object_to_goal_dist_end":0.01316,"object_to_goal_dist_start":0.18236,"object_z_max":0.03715,"peak_contact_force":72.51171,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2625.0,"raw_peak_contact_force":82.35926,"tcp_end":[0.49806,-0.04043,0.0367],"tcp_start":[0.50325,0.13955,0.04186],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50701,-0.06935,0.03676],"object_pos_start":[0.50701,-0.06935,0.03676],"object_to_goal_dist_end":0.01316,"object_to_goal_dist_start":0.01316,"object_z_max":0.03676,"peak_contact_force":78.76479,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":78.76479,"tcp_end":[0.49806,-0.04043,0.0367],"tcp_start":[0.49806,-0.04043,0.0367],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.09254,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.09254,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88793,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00146,"align_1.lateral_offset_y":0.00165,"insert_1.insertion_depth":0.10478,"insert_1.insertion_force":5.66259,"push_1.push_distance":0.10122,"push_1.push_speed":0.07624},"optimized_scores":{"best_composite_score":0.47384,"best_fitness_score":0.50051,"best_task_score":0.97038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":492.0,"contact_point_centroid":[0.54211,-0.02511,0.05999],"force_p95":118.79157,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.93261,"mean_force":70.3791,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49735,-0.02517,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54355,-0.05522,0.05998],"force_p95":117.60807,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.60807,"mean_force":117.60807,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05883,0.03649]},{"body_a":"attachment","body_b":"peg","contact_count":895.0,"contact_point_centroid":[0.50286,-0.0138,0.04396],"force_p95":79.78099,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.14881,"mean_force":21.62448,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49675,-0.00245,0.03701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.5052,-0.10227,0.05443],"force_p95":81.23107,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.70631,"mean_force":58.81717,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49846,-0.05761,0.03656]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5047,-0.07041,0.04872],"force_p95":69.40374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.40374,"mean_force":69.40374,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05883,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50463,-0.10298,0.05994],"force_p95":68.90872,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.90872,"mean_force":68.90872,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05883,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":710.0,"contact_point_centroid":[0.50582,-0.03362,0.00985],"force_p95":16.15915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.57355,"mean_force":5.91722,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49666,0.00853,0.03722]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":411.0,"contact_point_centroid":[0.52506,-0.00126,0.02199],"force_p95":7.3881,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.63666,"mean_force":2.29345,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49594,0.02478,0.03717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49745,0.14007,0.22965]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50571,-0.10552,0.00997],"force_p95":0.95651,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95651,"mean_force":0.95651,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05883,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49658,0.09388,0.10446]}],"total_contact_groups":11},"final_pose_error":0.02149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50464,-0.0878,0.03506],"final_tcp_position":[0.49896,-0.05883,0.03649],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":133.93261,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49683,0.08437,0.16739],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13481,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":870.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54546,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":414.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49851,0.10435,0.04199],"tcp_start":[0.49683,0.08437,0.16739],"tcp_to_object_dist_end":0.0381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50463,-0.0878,0.03505],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.01033,"object_to_goal_dist_start":0.14759,"object_z_max":0.03816,"peak_contact_force":112.49598,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2768.0,"raw_peak_contact_force":133.93261,"tcp_end":[0.49895,-0.05883,0.03649],"tcp_start":[0.49851,0.10435,0.04199],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50464,-0.0878,0.03506],"object_pos_start":[0.50463,-0.0878,0.03505],"object_to_goal_dist_end":0.01033,"object_to_goal_dist_start":0.01033,"object_z_max":0.03505,"peak_contact_force":117.60807,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":117.60807,"tcp_end":[0.49896,-0.05883,0.03649],"tcp_start":[0.49895,-0.05883,0.03649],"tcp_to_object_dist_end":0.02956,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```