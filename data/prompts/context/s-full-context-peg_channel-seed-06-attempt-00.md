## Search State

- **Seed**: 6
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.081) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.081
- **task_score** (E): 0.000
- **fitness_score**: 0.319  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2592 |
| lift_1 | 0.00 | 1.00 | 0.1708 |
| push_1 | 1.00 | 1.00 | 0.1869 |
| approach_1 | 0.33 | 1.00 | 0.1667 |
| approach_2 | 0.67 | 1.00 | 0.0437 |
| descend_1 | 0.67 | 0.67 | 0.0796 |
| grasp_1 | 1.00 | 0.67 | 0.0060 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.142, 0.049)→(0.430, 0.046, 0.174) | (0.501, 0.100, 0.034)→(0.503, 0.113, 0.027) | 0.180→0.194 | 1.00 / 1.000 | 0.598 | 1.939 |
| push_1 | push | 1.00 / step_budget | (0.430, 0.046, 0.174)→(0.494, -0.067, 0.041) | (0.503, 0.113, 0.027)→(0.515, 0.114, 0.027) | 0.194→0.195 | 1.00 / 1.667 | 44.019 | 95.537 |
| approach_1 | approach | 0.33 / step_budget | (0.494, -0.067, 0.041)→(0.499, 0.099, 0.041) | (0.515, 0.114, 0.027)→(0.548, 0.136, 0.028) | 0.195→0.228 | 1.00 / 2.333 | 144.027 | 196.811 |
| approach_2 | approach | 0.67 / step_budget | (0.499, 0.099, 0.041)→(0.501, 0.141, 0.038) | (0.548, 0.136, 0.028)→(0.584, 0.161, 0.014) | 0.228→0.276 | 1.00 / 2.000 | 89.327 | 156.396 |
| descend_1 | descend | 0.67 / step_budget | (0.501, 0.141, 0.038)→(0.562, 0.181, 0.022) | (0.584, 0.161, 0.014)→(0.644, 0.167, -1.592) | 0.276→1.797 | 0.67 / 1.333 | 138.708 | 313.514 |
| grasp_1 | grasp | 1.00 / step_budget | (0.562, 0.181, 0.022)→(0.559, 0.181, 0.018) | (0.644, 0.167, -1.592)→(0.689, 0.168, -5.833) | 1.797→6.043 | 0.67 / 1.333 | 37.258 | 48.899 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.680
- phase_breakdown.approach_score: 0.796
- phase_breakdown.push_score: 0.868
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.408
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.044
- **K-run variance**: 0.0083
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: align_1.lateral_offset_y
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40614,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00078,"approach_2.speed":0.04284,"lift_1.lift_height":0.13323,"push_1.push_distance":0.16841,"push_1.push_speed":0.03926},"optimized_scores":{"best_composite_score":-0.04394,"best_fitness_score":0.35606,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":453.0,"contact_point_centroid":[0.55498,0.11999,0.05993],"force_p95":248.85609,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.95359,"mean_force":204.08237,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50888,0.16546,0.03005]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.54383,0.08871,0.05994],"force_p95":150.30341,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.90207,"mean_force":116.10103,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49906,0.08836,0.03638]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.54876,0.10536,0.05999],"force_p95":111.78302,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.13566,"mean_force":63.54361,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50089,0.11746,0.0352]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.50392,-0.10004,0.065],"force_p95":116.83056,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.23412,"mean_force":100.30128,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49384,-0.08782,0.04382]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54049,-0.10001,0.06497],"force_p95":127.58544,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.80854,"mean_force":95.44821,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49713,-0.08785,0.04047]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":449.0,"contact_point_centroid":[0.55499,0.12,0.05998],"force_p95":72.03238,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.54058,"mean_force":62.76512,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5128,0.18353,0.02593]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54063,-0.10001,0.06495],"force_p95":66.34007,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.36765,"mean_force":59.85365,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49729,-0.08778,0.0404]},{"body_a":"attachment","body_b":"peg","contact_count":236.0,"contact_point_centroid":[0.5015,0.0738,0.04281],"force_p95":23.94712,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.7285,"mean_force":13.85695,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49826,0.06257,0.044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50362,0.07664,0.0095],"force_p95":18.66771,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.56154,"mean_force":3.85883,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49616,-0.00098,0.04683]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50879,-0.10004,0.065],"force_p95":20.38137,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.97808,"mean_force":5.99452,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49729,-0.08781,0.04039]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52517,0.11251,0.03835],"force_p95":8.4844,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.0862,"mean_force":1.20936,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.08303,0.03811]},{"body_a":"peg","body_b":"world","contact_count":373.0,"contact_point_centroid":[0.50688,0.1551,-0.00194],"force_p95":1.19282,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.72884,"mean_force":0.69867,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4998,0.12519,0.03624]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50682,0.11963,0.03316],"force_p95":7.58689,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.68714,"mean_force":2.44633,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49996,0.11286,0.03622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":42.0,"contact_point_centroid":[0.52508,0.11684,0.01748],"force_p95":2.68311,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.22319,"mean_force":0.71279,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49959,0.09118,0.03639]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.50441,0.11991,0.00978],"force_p95":1.32073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.18764,"mean_force":0.55185,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49921,0.09392,0.0364]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]}],"total_contact_groups":20},"final_pose_error":0.02764,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.35912,0.17899,0.01416],"final_tcp_position":[0.51232,0.18322,0.02615],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":277.95359,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54731,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55077,"tcp_end":[0.43006,0.02624,0.17825],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.16699,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.503,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":130.80854,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1121.0,"raw_peak_contact_force":151.23412,"tcp_end":[0.49724,-0.08785,0.04039],"tcp_start":[0.43006,0.02624,0.17825],"tcp_to_object_dist_end":0.15555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,0.11872,0.035],"object_pos_start":[0.503,0.06745,0.0338],"object_to_goal_dist_end":0.19891,"object_to_goal_dist_start":0.14761,"object_z_max":0.03977,"peak_contact_force":80.19677,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1275.0,"raw_peak_contact_force":158.90207,"tcp_end":[0.4997,0.08935,0.03638],"tcp_start":[0.49724,-0.08785,0.04039],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.49501,0.16116,0.0142],"object_pos_start":[0.50702,0.11872,0.035],"object_to_goal_dist_end":0.24258,"object_to_goal_dist_start":0.19891,"object_z_max":0.03516,"peak_contact_force":0.4611,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":595.0,"raw_peak_contact_force":155.13566,"tcp_end":[0.5038,0.14943,0.03355],"tcp_start":[0.4997,0.08935,0.03638],"tcp_to_object_dist_end":0.02427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.41806,0.17137,0.01416],"object_pos_start":[0.49501,0.16116,0.0142],"object_to_goal_dist_end":0.26565,"object_to_goal_dist_start":0.24258,"object_z_max":0.01421,"peak_contact_force":242.75013,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":937.0,"raw_peak_contact_force":277.95359,"tcp_end":[0.51232,0.18322,0.02615],"tcp_start":[0.5038,0.14943,0.03355],"tcp_to_object_dist_end":0.09576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.35912,0.17899,0.01416],"object_pos_start":[0.41806,0.17137,0.01416],"object_to_goal_dist_end":0.29595,"object_to_goal_dist_start":0.26565,"object_z_max":0.01416,"peak_contact_force":56.00339,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":899.0,"raw_peak_contact_force":73.54058,"tcp_end":[0.51303,0.18361,0.02583],"tcp_start":[0.51232,0.18322,0.02615],"tcp_to_object_dist_end":0.15442,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0241,"average_solve_count":332.0,"average_success_count":332.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00513,"approach_2.speed":0.0129,"lift_1.lift_height":0.16922,"push_1.push_distance":0.19945,"push_1.push_speed":0.05665},"optimized_scores":{"best_composite_score":0.00809,"best_fitness_score":0.40809,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":346.0,"contact_point_centroid":[0.55498,0.11999,0.05994],"force_p95":258.49271,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.12562,"mean_force":180.79607,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51221,0.17172,0.02803]},{"body_a":"peg","body_b":"world","contact_count":421.0,"contact_point_centroid":[0.50397,0.16113,-0.00246],"force_p95":98.8484,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.09063,"mean_force":26.4757,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51143,0.17039,0.0285]},{"body_a":"attachment","body_b":"peg","contact_count":246.0,"contact_point_centroid":[0.51314,0.16258,0.02891],"force_p95":99.97924,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.5893,"mean_force":44.49034,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50793,0.16428,0.03059]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.55499,0.12,0.05998],"force_p95":71.56549,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.15745,"mean_force":61.84288,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52013,0.18446,0.02353]},{"body_a":"peg","body_b":"world","contact_count":389.0,"contact_point_centroid":[0.50613,0.15039,-0.002],"force_p95":26.2442,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.88607,"mean_force":3.23608,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49662,0.12749,0.04198]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.51021,0.15083,0.03136],"force_p95":43.58215,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.38418,"mean_force":25.47748,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49919,0.15084,0.0359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50376,0.11218,0.00943],"force_p95":0.59838,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.27092,"mean_force":0.55584,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49324,0.00624,0.05098]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50104,0.09759,0.05358],"force_p95":2.71395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.05076,"mean_force":1.54882,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49674,0.08584,0.04967]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50352,0.11122,0.00941],"force_p95":0.60591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43975,"mean_force":0.54793,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46978,0.10378,0.10742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49753,0.12798,0.05958],"force_p95":1.1545,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.97536,"mean_force":0.44372,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4931,0.13894,0.06131]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.49887,0.16565,-0.00193],"force_p95":0.64428,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64473,"mean_force":0.60651,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52013,0.18446,0.02353]},{"body_a":"peg","body_b":"channel_base_body","contact_count":925.0,"contact_point_centroid":[0.50371,0.11158,0.00941],"force_p95":0.59061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63124,"mean_force":0.54392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4646,-0.01369,0.10327]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.50277,0.11984,0.00977],"force_p95":0.5402,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59821,"mean_force":0.42421,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49605,0.09785,0.04624]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]}],"total_contact_groups":15},"final_pose_error":0.0164,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50052,0.16667,0.01415],"final_tcp_position":[0.51955,0.18399,0.0238],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":305.12562,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03525,"peak_contact_force":0.61004,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1017.0,"raw_peak_contact_force":2.43975,"tcp_end":[0.43774,0.05553,0.1705],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.1619,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11173,0.03383],"object_pos_start":[0.50377,0.11176,0.0338],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.1919,"object_z_max":0.03402,"peak_contact_force":0.61195,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":925.0,"raw_peak_contact_force":0.63124,"tcp_end":[0.49305,-0.08062,0.04115],"tcp_start":[0.43774,0.05553,0.1705],"tcp_to_object_dist_end":0.19278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50389,0.12266,0.03531],"object_pos_start":[0.50369,0.11173,0.03383],"object_to_goal_dist_end":0.20275,"object_to_goal_dist_start":0.19186,"object_z_max":0.03548,"peak_contact_force":0.56078,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1011.0,"raw_peak_contact_force":3.27092,"tcp_end":[0.49713,0.09566,0.04751],"tcp_start":[0.49305,-0.08062,0.04115],"tcp_to_object_dist_end":0.03039,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.51021,0.15179,0.01281],"object_pos_start":[0.50389,0.12266,0.03531],"object_to_goal_dist_end":0.2336,"object_to_goal_dist_start":0.20275,"object_z_max":0.03531,"peak_contact_force":44.88607,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":474.0,"raw_peak_contact_force":44.88607,"tcp_end":[0.5,0.15354,0.03488],"tcp_start":[0.49713,0.09566,0.04751],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":421.0,"n_steps_budget":600.0,"object_pos_end":[0.49735,0.16494,0.01415],"object_pos_start":[0.51021,0.15179,0.01281],"object_to_goal_dist_end":0.24632,"object_to_goal_dist_start":0.2336,"object_z_max":0.01442,"peak_contact_force":173.37501,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1013.0,"raw_peak_contact_force":305.12562,"tcp_end":[0.51955,0.18399,0.0238],"tcp_start":[0.5,0.15354,0.03488],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50052,0.16667,0.01415],"object_pos_start":[0.49735,0.16494,0.01415],"object_to_goal_dist_end":0.24802,"object_to_goal_dist_start":0.24632,"object_z_max":0.01416,"peak_contact_force":55.77067,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":73.15745,"tcp_end":[0.52036,0.18456,0.02343],"tcp_start":[0.51955,0.18399,0.0238],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70445,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.01,"approach_2.speed":0.02724,"lift_1.lift_height":0.27988,"push_1.push_distance":0.19966,"push_1.push_speed":0.09716},"optimized_scores":{"best_composite_score":-0.20577,"best_fitness_score":0.19423,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":352.0,"contact_point_centroid":[0.52508,0.08724,0.05996],"force_p95":279.28285,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":428.25916,"mean_force":170.71047,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50398,0.08696,0.04397]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.54653,0.11402,0.05996],"force_p95":347.25873,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.09715,"mean_force":223.65067,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5005,0.11193,0.0391]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":419.0,"contact_point_centroid":[0.55489,0.12,0.05998],"force_p95":290.23781,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.4618,"mean_force":236.96174,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50042,0.12208,0.05311]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52506,0.11994,0.05995],"force_p95":246.15402,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.07548,"mean_force":192.67027,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5037,0.12477,0.05144]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":941.0,"contact_point_centroid":[0.54775,0.11768,0.05996],"force_p95":197.3137,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.1676,"mean_force":146.27493,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49984,0.11559,0.04352]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":955.0,"contact_point_centroid":[0.52504,0.11628,0.05997],"force_p95":180.10159,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.63812,"mean_force":120.05306,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49985,0.11549,0.04344]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47496,-0.0276,0.05989],"force_p95":131.13877,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.74423,"mean_force":76.33804,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4853,-0.02536,0.05457]},{"body_a":"peg","body_b":"world","contact_count":601.0,"contact_point_centroid":[0.49712,0.15864,-0.00186],"force_p95":0.72597,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.8278,"mean_force":0.61334,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4405,0.08822,0.1344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"world","contact_count":517.0,"contact_point_centroid":[0.77584,0.17181,-0.00188],"force_p95":0.72585,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87928,"mean_force":0.58646,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50623,0.12485,0.05087]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.58128,0.16401,-0.00199],"force_p95":0.72595,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72611,"mean_force":0.60602,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50041,0.04524,0.04538]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.68986,0.1683,-0.00199],"force_p95":0.72587,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72596,"mean_force":0.60602,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49984,0.11552,0.04347]},{"body_a":"peg","body_b":"world","contact_count":732.0,"contact_point_centroid":[0.51838,0.16125,-0.00199],"force_p95":0.72591,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72592,"mean_force":0.60602,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45686,0.01107,0.10615]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49585,0.11953,0.00942],"force_p95":0.60298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62344,"mean_force":0.52859,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46838,0.13841,0.07114]}],"total_contact_groups":15},"final_pose_error":0.09916,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[1.20693,0.15929,-17.52829],"final_tcp_position":[0.65301,0.17722,0.01727],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":428.25916,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50294,0.16045,0.01409],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.24186,"object_to_goal_dist_start":0.1996,"object_z_max":0.03393,"peak_contact_force":0.63703,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":998.0,"raw_peak_contact_force":2.8278,"tcp_end":[0.4234,0.05711,0.17396],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.2063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.53858,0.16225,0.01409],"object_pos_start":[0.50294,0.16045,0.01409],"object_to_goal_dist_end":0.24667,"object_to_goal_dist_start":0.24186,"object_z_max":0.01409,"peak_contact_force":0.63712,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":738.0,"raw_peak_contact_force":134.74423,"tcp_end":[0.49193,-0.03388,0.04255],"tcp_start":[0.4234,0.05711,0.17396],"tcp_to_object_dist_end":0.2036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63281,0.16614,0.01409],"object_pos_start":[0.53858,0.16225,0.01409],"object_to_goal_dist_end":0.28088,"object_to_goal_dist_start":0.24667,"object_z_max":0.0141,"peak_contact_force":351.3231,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1405.0,"raw_peak_contact_force":428.25916,"tcp_end":[0.50022,0.11233,0.03962],"tcp_start":[0.49193,-0.03388,0.04255],"tcp_to_object_dist_end":0.14535,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.74635,0.17053,0.01409],"object_pos_start":[0.63281,0.16614,0.01409],"object_to_goal_dist_end":0.35231,"object_to_goal_dist_start":0.28088,"object_z_max":0.0141,"peak_contact_force":222.63403,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2896.0,"raw_peak_contact_force":269.1676,"tcp_end":[0.50012,0.12145,0.04663],"tcp_start":[0.50022,0.11233,0.03962],"tcp_to_object_dist_end":0.25317,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[1.01802,0.16563,-4.80509],"object_pos_start":[0.74635,0.17053,0.01409],"object_to_goal_dist_end":4.87889,"object_to_goal_dist_start":0.35231,"object_z_max":0.01504,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":949.0,"raw_peak_contact_force":357.4618,"tcp_end":[0.65301,0.17722,0.01727],"tcp_start":[0.50012,0.12145,0.04663],"tcp_to_object_dist_end":4.83616,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[1.20693,0.15929,-17.52829],"object_pos_start":[1.01802,0.16563,-4.80509],"object_to_goal_dist_end":17.58414,"object_to_goal_dist_start":4.87889,"object_z_max":-4.80509,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.64472,0.17507,0.00351],"tcp_start":[0.65301,0.17722,0.01727],"tcp_to_object_dist_end":17.54082,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```