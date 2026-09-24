## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 9 | -0.0271 | 0.37 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3579 | 0.72 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0324 | 0.00 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3576 | 0.73 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3601 | 0.73 | ✅ accepted |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.027) — your mutation base

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

- **Composite score**: -0.027
- **task_score** (E): 0.369
- **fitness_score**: 0.263  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1765 |
| approach_1 | 1.00 | 1.00 | 0.0935 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 1.00 | 1.00 | 0.1017 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.500, 0.117, 0.146) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.545 | 2.127 |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.117, 0.146)→(0.501, 0.089, 0.060) | (0.501, 0.099, 0.034)→(0.501, 0.040, 0.028) | 0.180→0.123 | 1.00 / 3.333 | 256.153 | 395.913 |
| contact_1 | contact | 1.00 / force_exceeded | (0.501, 0.089, 0.060)→(0.501, 0.089, 0.060) | (0.501, 0.040, 0.028)→(0.501, 0.040, 0.028) | 0.123→0.123 | 1.00 / 3.333 | 63.986 | 63.986 |
| push_1 | push | 0.00 / guard_failure | (0.501, 0.089, 0.060)→(0.501, 0.089, 0.060) | (0.501, 0.040, 0.028)→(0.501, 0.040, 0.028) | 0.123→0.123 | 1.00 / 3.000 | 53.675 | 85.630 |
| retract_1 | retract | 1.00 / time_limit | (0.501, 0.089, 0.060)→(0.499, 0.048, 0.142) | (0.501, 0.040, 0.028)→(0.501, 0.040, 0.031) | 0.123→0.122 | 1.00 / 1.333 | 0.402 | 252.806 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.820
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.820
- phase_score: 0.178
- phase_breakdown.reach_contact_score: 0.499
- phase_breakdown.reach_goal_score: 0.041

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.435
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.820
- **Median Q (composite search score)**: -0.099
- **K-run variance**: 0.0149
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55645,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.00234,"align_1.align_offset_y":-0.00166,"approach_1.approach_speed":0.05928,"contact_1.contact_force_threshold":12.32355,"contact_1.contact_speed":0.03295,"push_1.push_depth":0.15304,"push_1.push_speed":0.02241,"retract_1.retract_height":0.13375,"retract_1.retract_speed":0.09608},"optimized_scores":{"best_composite_score":0.14498,"best_fitness_score":0.43498,"best_task_score":0.82033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.50282,0.14239,-0.00018],"force_p95":652.94001,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":661.92815,"mean_force":421.25457,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50964,0.07928,0.05226]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":442.0,"contact_point_centroid":[0.47496,0.11994,0.05872],"force_p95":297.68559,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":567.75648,"mean_force":148.48455,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51208,0.08014,0.05643]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":170.0,"contact_point_centroid":[0.52504,0.0826,0.05798],"force_p95":267.95096,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.68683,"mean_force":139.98618,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51318,0.08108,0.05766]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":517.0,"contact_point_centroid":[0.52501,0.11994,0.05972],"force_p95":254.85675,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.72026,"mean_force":174.65766,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50579,0.07879,0.0689]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":168.0,"contact_point_centroid":[0.47496,0.11994,0.05786],"force_p95":238.52336,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.13777,"mean_force":122.24415,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50622,0.07871,0.06635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":861.0,"contact_point_centroid":[0.50413,0.05941,0.00906],"force_p95":129.73033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":165.54799,"mean_force":20.13228,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5033,0.07838,0.09019]},{"body_a":"attachment","body_b":"peg","contact_count":183.0,"contact_point_centroid":[0.50736,0.07937,0.05485],"force_p95":148.21162,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.00952,"mean_force":92.08764,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50757,0.07921,0.06513]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50307,0.14256,-9e-05],"force_p95":132.80483,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.63024,"mean_force":84.79936,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50987,0.07936,0.05233]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":159.0,"contact_point_centroid":[0.52501,0.11992,0.05998],"force_p95":131.74787,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.50579,"mean_force":78.91789,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51505,0.07081,0.06936]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50306,0.14251,-0.00012],"force_p95":82.38218,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.53959,"mean_force":71.68509,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50985,0.07931,0.05227]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50306,0.14251,-0.00011],"force_p95":47.33319,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.33319,"mean_force":47.33319,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50984,0.0793,0.05228]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.525,0.11998,0.06],"force_p95":24.90121,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":26.17987,"mean_force":13.19105,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50985,0.07931,0.05227]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49831,0.14418,0.22122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50162,-0.06379,0.00806],"force_p95":0.6441,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88428,"mean_force":0.6057,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5096,0.04555,0.0854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50248,-0.0388,0.00789],"force_p95":0.81246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82299,"mean_force":0.7232,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50985,0.07931,0.05227]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.525,0.11997,0.06],"force_p95":0.72221,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.72221,"mean_force":0.72221,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50984,0.0793,0.05228]}],"total_contact_groups":17},"final_pose_error":0.02532,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50154,-0.06379,0.02415],"final_tcp_position":[0.50061,-0.04121,0.1461],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":661.92815,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.50242,0.07875,0.15197],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":919.0,"n_steps_budget":1000.0,"object_pos_end":[0.50186,-0.06387,0.02387],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.02289,"object_to_goal_dist_start":0.14759,"object_z_max":0.04647,"peak_contact_force":346.70261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1807.0,"raw_peak_contact_force":661.92815,"subtask_id":"reach_contact","tcp_end":[0.50984,0.0793,0.05228],"tcp_start":[0.50242,0.07875,0.15197],"tcp_to_object_dist_end":0.14617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50186,-0.06378,0.02385],"object_pos_start":[0.50186,-0.06387,0.02387],"object_to_goal_dist_end":0.02296,"object_to_goal_dist_start":0.02289,"object_z_max":0.02387,"peak_contact_force":47.33319,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":47.33319,"subtask_id":"reach_contact","tcp_end":[0.50984,0.0793,0.05227],"tcp_start":[0.50984,0.0793,0.05228],"tcp_to_object_dist_end":0.1461,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50186,-0.06373,0.02385],"object_pos_start":[0.50186,-0.06378,0.02385],"object_to_goal_dist_end":0.023,"object_to_goal_dist_start":0.02296,"object_z_max":0.02385,"peak_contact_force":83.53959,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":83.53959,"subtask_id":"reach_goal","tcp_end":[0.50985,0.07933,0.05226],"tcp_start":[0.50985,0.07932,0.05227],"tcp_to_object_dist_end":0.14607,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50154,-0.06379,0.02415],"object_pos_start":[0.50186,-0.06374,0.02386],"object_to_goal_dist_end":0.02272,"object_to_goal_dist_start":0.02299,"object_z_max":0.02433,"peak_contact_force":0.64358,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1776.0,"raw_peak_contact_force":567.75648,"tcp_end":[0.50061,-0.04121,0.1461],"tcp_start":[0.50985,0.07933,0.05226],"tcp_to_object_dist_end":0.12403,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36508,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":-0.01212,"align_1.align_offset_y":0.01814,"approach_1.approach_speed":0.0362,"contact_1.contact_force_threshold":25.78343,"contact_1.contact_speed":0.0209,"push_1.push_depth":0.14807,"push_1.push_speed":0.02878,"retract_1.retract_height":0.10503,"retract_1.retract_speed":0.10779},"optimized_scores":{"best_composite_score":-0.09889,"best_fitness_score":0.19111,"best_task_score":0.17822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":154.0,"contact_point_centroid":[0.50337,0.27876,-4e-05],"force_p95":254.69659,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.48933,"mean_force":180.66404,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.08993,0.0654]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50284,0.11117,0.00847],"force_p95":122.92407,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.13799,"mean_force":63.78243,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49856,0.11142,0.08149]},{"body_a":"attachment","body_b":"peg","contact_count":597.0,"contact_point_centroid":[0.50122,0.1155,0.05364],"force_p95":124.44423,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.82841,"mean_force":106.6783,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50057,0.10093,0.06468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.50585,0.08569,0.00932],"force_p95":53.0522,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.41356,"mean_force":6.90265,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50162,0.09065,0.09362]},{"body_a":"attachment","body_b":"peg","contact_count":96.0,"contact_point_centroid":[0.50134,0.10019,0.05669],"force_p95":70.91936,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.273,"mean_force":34.17085,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50038,0.09049,0.0689]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50225,0.09103,0.00791],"force_p95":83.48229,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.85769,"mean_force":77.12826,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50046,0.08972,0.06451]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50143,0.10046,0.05347],"force_p95":82.64971,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.36229,"mean_force":77.44646,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50046,0.08972,0.06451]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49776,0.09875,0.00787],"force_p95":69.96134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.96134,"mean_force":69.96134,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50043,0.08969,0.06448]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50141,0.10054,0.05341],"force_p95":61.12729,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.12729,"mean_force":61.12729,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50043,0.08969,0.06448]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5039,0.27887,-3e-05],"force_p95":48.16156,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.16156,"mean_force":48.16156,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50043,0.08969,0.06448]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.50392,0.27889,-1e-05],"force_p95":40.28165,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.0873,"mean_force":31.94398,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50046,0.08972,0.06451]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":352.0,"contact_point_centroid":[0.52529,0.09362,0.01722],"force_p95":19.35801,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.34006,"mean_force":8.0947,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50019,0.09487,0.06479]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52549,0.08402,0.02528],"force_p95":16.71269,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.00308,"mean_force":7.70076,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50046,0.08972,0.06451]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":284.0,"contact_point_centroid":[0.5251,0.08332,0.0427],"force_p95":7.31352,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.66539,"mean_force":1.50524,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50111,0.09086,0.08612]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.5255,0.08404,0.01],"force_p95":9.79445,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.79445,"mean_force":9.79445,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50043,0.08969,0.06448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":767.0,"contact_point_centroid":[0.50366,0.11163,0.0094],"force_p95":0.60542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55312,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49447,0.17069,0.2168]}],"total_contact_groups":17},"final_pose_error":0.0102,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50698,0.08326,0.03377],"final_tcp_position":[0.50488,0.08475,0.12622],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":275.48933,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11172,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.51582,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":783.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.49557,0.13227,0.14373],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50798,0.08408,0.03078],"object_pos_start":[0.50371,0.11172,0.03383],"object_to_goal_dist_end":0.16453,"object_to_goal_dist_start":0.19186,"object_z_max":0.03386,"peak_contact_force":235.28878,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2103.0,"raw_peak_contact_force":275.48933,"subtask_id":"reach_contact","tcp_end":[0.50043,0.08969,0.06448],"tcp_start":[0.49557,0.13227,0.14373],"tcp_to_object_dist_end":0.03498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50797,0.08405,0.0308],"object_pos_start":[0.50798,0.08408,0.03078],"object_to_goal_dist_end":0.1645,"object_to_goal_dist_start":0.16453,"object_z_max":0.03078,"peak_contact_force":69.96134,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":69.96134,"subtask_id":"reach_contact","tcp_end":[0.50045,0.0897,0.06449],"tcp_start":[0.50043,0.08969,0.06448],"tcp_to_object_dist_end":0.03498,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50797,0.08402,0.03083],"object_pos_start":[0.50797,0.08405,0.0308],"object_to_goal_dist_end":0.16447,"object_to_goal_dist_start":0.1645,"object_z_max":0.03086,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":83.85769,"subtask_id":"reach_goal","tcp_end":[0.50049,0.08976,0.06457],"tcp_start":[0.50047,0.08974,0.06454],"tcp_to_object_dist_end":0.03503,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":539.0,"n_steps_budget":600.0,"object_pos_end":[0.50698,0.08326,0.03377],"object_pos_start":[0.50795,0.08397,0.03088],"object_to_goal_dist_end":0.16353,"object_to_goal_dist_start":0.16442,"object_z_max":0.03451,"peak_contact_force":0.01788,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":919.0,"raw_peak_contact_force":89.41356,"tcp_end":[0.50488,0.08475,0.12622],"tcp_start":[0.50049,0.08976,0.06457],"tcp_to_object_dist_end":0.09249,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69524,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.01833,"align_1.align_offset_y":0.0195,"approach_1.approach_speed":0.06612,"contact_1.contact_force_threshold":25.05903,"contact_1.contact_speed":0.02195,"push_1.push_depth":0.16219,"push_1.push_speed":0.03528,"retract_1.retract_height":0.13368,"retract_1.retract_speed":0.07643},"optimized_scores":{"best_composite_score":-0.12739,"best_fitness_score":0.16261,"best_task_score":0.10833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":56.0,"contact_point_centroid":[0.49654,0.28674,-0.00013],"force_p95":212.19991,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.32175,"mean_force":154.92148,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4934,0.09766,0.06457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":708.0,"contact_point_centroid":[0.49587,0.11901,0.0083],"force_p95":143.42769,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.60932,"mean_force":56.90317,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49693,0.12317,0.0846]},{"body_a":"attachment","body_b":"peg","contact_count":356.0,"contact_point_centroid":[0.49641,0.12518,0.05194],"force_p95":145.44259,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.08643,"mean_force":112.08586,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49612,0.11162,0.06266]},{"body_a":"peg","body_b":"channel_base_body","contact_count":772.0,"contact_point_centroid":[0.4933,0.1022,0.00934],"force_p95":53.57023,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.24773,"mean_force":6.05447,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49151,0.10434,0.10742]},{"body_a":"attachment","body_b":"peg","contact_count":101.0,"contact_point_centroid":[0.49438,0.11806,0.05654],"force_p95":90.27405,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.65193,"mean_force":41.63249,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49368,0.09911,0.06979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49056,0.10829,0.00762],"force_p95":89.0584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.49198,"mean_force":84.04419,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49389,0.09754,0.0645]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49462,0.11815,0.05255],"force_p95":88.64275,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.09916,"mean_force":83.54663,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49389,0.09754,0.0645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49653,0.11824,0.00758],"force_p95":74.66277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.66277,"mean_force":74.66277,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49386,0.09751,0.06446]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.4946,0.11824,0.05248],"force_p95":73.85683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.85683,"mean_force":73.85683,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49386,0.09751,0.06446]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.49671,0.28669,-4e-05],"force_p95":55.33095,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.33095,"mean_force":55.33095,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49386,0.09751,0.06446]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.49673,0.28671,-2e-05],"force_p95":49.29594,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.32515,"mean_force":39.42975,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49389,0.09754,0.0645]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.49675,0.28675,-0.0],"force_p95":24.65975,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.65975,"mean_force":24.65975,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49392,0.09758,0.06457]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":217.0,"contact_point_centroid":[0.47499,0.10006,0.05592],"force_p95":3.78456,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.82874,"mean_force":0.6839,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49168,0.10372,0.10335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":736.0,"contact_point_centroid":[0.49621,0.11912,0.00944],"force_p95":0.61111,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49727,0.17373,0.2146]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50462,0.2121,0.29586]}],"total_contact_groups":15},"final_pose_error":0.00987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49301,0.09997,0.03378],"final_tcp_position":[0.49128,0.10079,0.1544],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":250.32175,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11906,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.573,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":760.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.5018,0.14035,0.14363],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.49356,0.10058,0.03019],"object_pos_start":[0.49605,0.11906,0.0339],"object_to_goal_dist_end":0.18096,"object_to_goal_dist_start":0.19919,"object_z_max":0.03399,"peak_contact_force":186.46696,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1120.0,"raw_peak_contact_force":250.32175,"subtask_id":"reach_contact","tcp_end":[0.49386,0.09751,0.06446],"tcp_start":[0.5018,0.14035,0.14363],"tcp_to_object_dist_end":0.0344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49355,0.10054,0.03022],"object_pos_start":[0.49356,0.10058,0.03019],"object_to_goal_dist_end":0.18092,"object_to_goal_dist_start":0.18096,"object_z_max":0.03019,"peak_contact_force":74.66277,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":74.66277,"subtask_id":"reach_contact","tcp_end":[0.49387,0.09752,0.06447],"tcp_start":[0.49386,0.09751,0.06446],"tcp_to_object_dist_end":0.03439,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49356,0.10051,0.03026],"object_pos_start":[0.49355,0.10054,0.03022],"object_to_goal_dist_end":0.18089,"object_to_goal_dist_start":0.18092,"object_z_max":0.03029,"peak_contact_force":77.48438,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":89.49198,"subtask_id":"reach_goal","tcp_end":[0.49392,0.09758,0.06457],"tcp_start":[0.4939,0.09756,0.06453],"tcp_to_object_dist_end":0.03444,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":772.0,"n_steps_budget":840.0,"object_pos_end":[0.49301,0.09997,0.03378],"object_pos_start":[0.49356,0.10046,0.03031],"object_to_goal_dist_end":0.18021,"object_to_goal_dist_start":0.18084,"object_z_max":0.03479,"peak_contact_force":0.5443,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1091.0,"raw_peak_contact_force":101.24773,"tcp_end":[0.49128,0.10079,0.1544],"tcp_start":[0.49392,0.09758,0.06457],"tcp_to_object_dist_end":0.12063,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```