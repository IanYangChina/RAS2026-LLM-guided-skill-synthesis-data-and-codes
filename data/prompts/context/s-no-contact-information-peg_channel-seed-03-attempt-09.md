## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.2959 | 0.33 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | 0.4871 | 0.21 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 5 | 0.0691 | 0.24 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1085 | 0.18 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.3167 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.296) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: reach_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
  parameters:
    contact_offset:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  guards:
  - id: contact_check
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_above
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - parameter_bindings:
    - contact_offset: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.296
- **task_score** (E): 0.326
- **fitness_score**: 0.526  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1425 |
| descend_1 | 1.00 | 0.1407 |
| push_1 | 1.00 | 0.1395 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.141, 0.173) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.141, 0.173)→(0.498, 0.107, 0.038) | (0.502, 0.082, 0.034)→(0.502, 0.077, 0.034) | 0.162→0.158 |
| push_1 | push | 1.00 / step_budget | (0.498, 0.107, 0.038)→(0.498, -0.032, 0.037) | (0.502, 0.077, 0.034)→(0.504, -0.064, 0.038) | 0.158→0.019 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.972
- alignment_error: None
- terminal_score: 0.295
- phase_score: 0.697
- phase_breakdown.reach_above_score: 0.118
- phase_breakdown.reach_goal_score: 0.945

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.536
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.467
- **Median Q (composite search score)**: 0.293
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09276,"descend_1.contact_offset":0.0208,"push_1.push_distance":0.15995,"push_1.push_tolerance":0.03441},"optimized_scores":{"best_composite_score":0.28838,"best_fitness_score":0.51838,"best_task_score":0.21668},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47493,0.09208,0.05987],"force_p95":295.15533,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.87853,"mean_force":155.22645,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48495,0.08798,0.05486]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.53424,0.08247,0.05973],"force_p95":265.31977,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.33294,"mean_force":186.90291,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48896,0.08225,0.03694]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":192.0,"contact_point_centroid":[0.5362,0.01714,0.05997],"force_p95":198.63442,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.5219,"mean_force":168.11933,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49106,0.01977,0.03747]},{"body_a":"attachment","body_b":"peg","contact_count":138.0,"contact_point_centroid":[0.49774,0.00912,0.04397],"force_p95":36.75146,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.92635,"mean_force":6.32301,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49105,0.02023,0.03747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":157.0,"contact_point_centroid":[0.49986,-0.01163,0.00949],"force_p95":36.6339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.59638,"mean_force":5.70217,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49091,0.02931,0.0375]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":87.0,"contact_point_centroid":[0.52535,-0.02354,0.01936],"force_p95":5.15828,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.18097,"mean_force":1.32704,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49142,0.00263,0.03751]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.49264,0.07254,0.04938],"force_p95":14.05537,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.82107,"mean_force":5.98499,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48763,0.08422,0.04331]},{"body_a":"peg","body_b":"channel_base_body","contact_count":706.0,"contact_point_centroid":[0.49481,0.05597,0.00947],"force_p95":6.94132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.64108,"mean_force":1.02891,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47724,0.10041,0.09106]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.51868,-0.03419,0.06904],"force_p95":5.93266,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.4819,"mean_force":2.51763,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49162,-0.00758,0.03751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.49459,0.05884,0.00933],"force_p95":0.63279,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59478,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48282,0.15731,0.21873]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.19692,0.29419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49536,-0.10055,0.06162],"force_p95":1.03613,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12183,"mean_force":0.64564,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49215,-0.04658,0.03725]}],"total_contact_groups":12},"final_pose_error":0.02997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4999,-0.082,0.03815],"final_tcp_position":[0.49208,-0.0479,0.03718],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05898,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.46849,0.11971,0.14927],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13294,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":713.0,"n_steps_budget":780.0,"object_pos_end":[0.49625,0.05262,0.03497],"object_pos_start":[0.49422,0.05898,0.03385],"object_to_goal_dist_end":0.13277,"object_to_goal_dist_start":0.13924,"object_z_max":0.03682,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.48932,0.08221,0.03675],"tcp_start":[0.46849,0.11971,0.14927],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":324.0,"n_steps_budget":990.0,"object_pos_end":[0.4999,-0.082,0.03815],"object_pos_start":[0.49625,0.05262,0.03497],"object_to_goal_dist_end":0.00273,"object_to_goal_dist_start":0.13277,"object_z_max":0.04209,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49208,-0.0479,0.03718],"tcp_start":[0.48932,0.08221,0.03675],"tcp_to_object_dist_end":0.035,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91176,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11572,"descend_1.contact_offset":0.02174,"push_1.push_distance":0.18038,"push_1.push_tolerance":0.02748},"optimized_scores":{"best_composite_score":0.30639,"best_fitness_score":0.53639,"best_task_score":0.29504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52511,0.1058,0.05995],"force_p95":308.82888,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.87251,"mean_force":293.83591,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50392,0.10572,0.04155]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.54537,-0.01249,0.05999],"force_p95":165.74217,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":194.38422,"mean_force":110.72963,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50056,-0.01202,0.037]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":81.0,"contact_point_centroid":[0.52501,-0.00327,0.06],"force_p95":136.60876,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.45536,"mean_force":105.58326,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50084,-0.00322,0.03738]},{"body_a":"attachment","body_b":"peg","contact_count":173.0,"contact_point_centroid":[0.50416,0.0077,0.03871],"force_p95":56.85789,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.07834,"mean_force":16.76257,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50088,0.01894,0.03748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50611,-0.10099,0.05343],"force_p95":74.85188,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.97096,"mean_force":39.30786,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50055,-0.0415,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":179.0,"contact_point_centroid":[0.50326,-0.02611,0.00963],"force_p95":36.76687,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.30904,"mean_force":9.87333,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5009,0.01297,0.03755]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":104.0,"contact_point_centroid":[0.52516,-0.01262,0.03164],"force_p95":19.00286,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.47433,"mean_force":4.02618,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50077,0.01567,0.03726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.50591,0.07799,0.00944],"force_p95":0.68897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.37201,"mean_force":1.19597,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5143,0.12203,0.1025]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.50574,0.09563,0.04827],"force_p95":27.74839,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.92811,"mean_force":10.60088,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50513,0.10739,0.04825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":255.0,"contact_point_centroid":[0.50545,0.08086,0.00933],"force_p95":0.61779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.6066,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51422,0.16793,0.22995]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50083,0.19728,0.29404]}],"total_contact_groups":11},"final_pose_error":0.03169,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5066,-0.07465,0.03979],"final_tcp_position":[0.50053,-0.04348,0.03684],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.52773,0.14034,0.17148],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15157,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":607.0,"n_steps_budget":900.0,"object_pos_end":[0.50432,0.07554,0.03407],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.15571,"object_to_goal_dist_start":0.1611,"object_z_max":0.03648,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50366,0.10568,0.04127],"tcp_start":[0.52773,0.14034,0.17148],"tcp_to_object_dist_end":0.031,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,-0.07465,0.03979],"object_pos_start":[0.50432,0.07554,0.03407],"object_to_goal_dist_end":0.00849,"object_to_goal_dist_start":0.15571,"object_z_max":0.04097,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50053,-0.04348,0.03684],"tcp_start":[0.50366,0.10568,0.04127],"tcp_to_object_dist_end":0.03189,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14211,"descend_1.contact_offset":0.02891,"push_1.push_distance":0.18435,"push_1.push_tolerance":0.02408},"optimized_scores":{"best_composite_score":0.29295,"best_fitness_score":0.52295,"best_task_score":0.46707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.54548,0.02665,0.05998],"force_p95":233.81509,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.28957,"mean_force":152.61472,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50072,0.02961,0.03664]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":289.0,"contact_point_centroid":[0.52501,0.02001,0.06],"force_p95":192.14032,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.75271,"mean_force":125.21832,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50072,0.01999,0.03673]},{"body_a":"attachment","body_b":"peg","contact_count":218.0,"contact_point_centroid":[0.50385,0.02271,0.04342],"force_p95":18.83494,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.53594,"mean_force":2.88814,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50077,0.03443,0.03663]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.50186,-0.00776,0.00962],"force_p95":6.04495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.06324,"mean_force":2.11516,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50076,0.03373,0.03666]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":52.0,"contact_point_centroid":[0.47478,0.02963,0.03938],"force_p95":3.96383,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.75718,"mean_force":1.29825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50083,0.06391,0.03654]},{"body_a":"peg","body_b":"channel_base_body","contact_count":724.0,"contact_point_centroid":[0.5058,0.10451,0.00939],"force_p95":0.57564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.27075,"mean_force":0.56132,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50881,0.14787,0.11598]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50564,0.12235,0.04561],"force_p95":6.86999,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.0904,"mean_force":4.27691,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5025,0.13433,0.03877]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":82.0,"contact_point_centroid":[0.52527,-0.02661,0.04302],"force_p95":1.05879,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.30899,"mean_force":0.47102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50066,0.00536,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50509,0.10445,0.00934],"force_p95":0.718,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.60681,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.509,0.17951,0.24427]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50057,0.198,0.29479]}],"total_contact_groups":10},"final_pose_error":0.04541,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50695,-0.03466,0.03532],"final_tcp_position":[0.5007,-0.0049,0.0368],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":214.0,"n_steps_budget":810.0,"object_pos_end":[0.50584,0.10467,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.51757,0.16244,0.1991],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17546,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.10411,0.03423],"object_pos_start":[0.50584,0.10467,0.03384],"object_to_goal_dist_end":0.1843,"object_to_goal_dist_start":0.18486,"object_z_max":0.03424,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50234,0.13408,0.03737],"tcp_start":[0.51757,0.16244,0.1991],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,-0.03466,0.03532],"object_pos_start":[0.50594,0.10411,0.03423],"object_to_goal_dist_end":0.0461,"object_to_goal_dist_start":0.1843,"object_z_max":0.0426,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.5007,-0.0049,0.0368],"tcp_start":[0.50234,0.13408,0.03737],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```