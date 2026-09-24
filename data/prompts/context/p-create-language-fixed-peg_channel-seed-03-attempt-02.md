## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.0213 | 0.01 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.2962 | 0.06 | ✅ accepted |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2210 | 0.05 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=-0.021) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach
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
    - 0.06
    - 0.06
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    descend_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.06], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.021
- **task_score** (E): 0.008
- **fitness_score**: 0.086  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1542 |
| descend | 0.67 | 1.00 | 0.1032 |
| push | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.165, 0.153) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.542 | 3.954 |
| descend | descend | 0.67 / force_exceeded | (0.505, 0.165, 0.153)→(0.497, 0.112, 0.067) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.667 | 13.485 | 13.488 |
| push | push | 0.00 / guard_failure | (0.497, 0.090, 0.061)→(0.497, 0.090, 0.061) | (0.502, 0.082, 0.034)→(0.502, 0.078, 0.035) | 0.162→0.158 | 1.00 / 2.000 | 45.037 | 46.283 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.008
- alignment_error: None
- force_efficiency: 0.089
- terminal_score: 0.004
- phase_score: 0.135
- phase_breakdown.approach_score: 0.089
- phase_breakdown.push_score: 0.015
- phase_breakdown.contact_score: 0.543

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.099
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.015
- **Median Q (composite search score)**: 0.081
- **K-run variance**: 0.0219
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.306


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64935,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13135,"descend.descend_force":6.89628,"descend.descend_speed":0.01038,"push.push_depth":0.19995,"push.push_max_time":4.73609,"push.push_speed":0.02316},"optimized_scores":{"best_composite_score":-0.23076,"best_fitness_score":0.09924,"best_task_score":0.01451},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":883.0,"contact_point_centroid":[0.49491,0.05344,0.00946],"force_p95":36.06079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.61398,"mean_force":7.88442,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48115,0.06493,0.06738]},{"body_a":"attachment","body_b":"peg","contact_count":257.0,"contact_point_centroid":[0.49312,0.04629,0.05932],"force_p95":37.70006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.2064,"mean_force":25.2788,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48263,0.04426,0.06417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.49459,0.05885,0.00933],"force_p95":0.61202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59053,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48258,0.17084,0.22151]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49852,0.1979,0.29475]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49417,0.05902,0.00939],"force_p95":0.55036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54591,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47542,0.11703,0.10795]}],"total_contact_groups":5},"final_pose_error":0.17855,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49589,0.05122,0.03652],"final_tcp_position":[0.48404,0.03503,0.06353],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":46.61398,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":840.0,"object_pos_end":[0.49421,0.05901,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54846,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":365.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46794,0.14504,0.1536],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,0.05916,0.03398],"object_pos_start":[0.49421,0.05901,0.03385],"object_to_goal_dist_end":0.13942,"object_to_goal_dist_start":0.13927,"object_z_max":0.03398,"peak_contact_force":0.54585,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55382,"subtask_id":"contact","tcp_end":[0.48303,0.09688,0.07717],"tcp_start":[0.46794,0.14504,0.1536],"tcp_to_object_dist_end":0.05838,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.4959,0.05125,0.03653],"object_pos_start":[0.49398,0.05916,0.03398],"object_to_goal_dist_end":0.13136,"object_to_goal_dist_start":0.13942,"object_z_max":0.03653,"peak_contact_force":46.61398,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1140.0,"raw_peak_contact_force":46.61398,"subtask_id":"push","tcp_end":[0.48404,0.03503,0.06353],"tcp_start":[0.48405,0.03508,0.06355],"tcp_to_object_dist_end":0.03366,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.4702,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.12193,"descend.descend_force":3.59283,"descend.descend_speed":0.00866,"push.push_depth":0.1993,"push.push_max_time":5.39999,"push.push_speed":0.02483},"optimized_scores":{"best_composite_score":0.08097,"best_fitness_score":0.07763,"best_task_score":0.00502},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.50165,0.07759,0.00931],"force_p95":39.71844,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.70531,"mean_force":35.01609,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5043,0.10665,0.06006]},{"body_a":"attachment","body_b":"peg","contact_count":41.0,"contact_point_centroid":[0.5102,0.09669,0.05812],"force_p95":39.26462,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.15263,"mean_force":34.58491,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5043,0.10665,0.06006]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.50595,0.08086,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.40502,"mean_force":0.57815,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.5155,0.13628,0.10515]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51094,0.09814,0.05878],"force_p95":19.00446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.00446,"mean_force":19.00446,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50492,0.10821,0.06129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50558,0.08086,0.00934],"force_p95":0.57106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59259,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51426,0.18106,0.22127]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50056,0.19855,0.2945]}],"total_contact_groups":6},"final_pose_error":0.22504,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50486,0.07802,0.03319],"final_tcp_position":[0.50391,0.10515,0.05929],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":46.70531,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":362.0,"n_steps_budget":870.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54821,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":369.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52854,0.16448,0.15278],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":19.40502,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":602.0,"raw_peak_contact_force":19.40502,"subtask_id":"contact","tcp_end":[0.5049,0.10812,0.06116],"tcp_start":[0.52854,0.16448,0.15278],"tcp_to_object_dist_end":0.03865,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,0.07814,0.03323],"object_pos_start":[0.50595,0.08087,0.03378],"object_to_goal_dist_end":0.15836,"object_to_goal_dist_start":0.1611,"object_z_max":0.03395,"peak_contact_force":46.70531,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":82.0,"raw_peak_contact_force":46.70531,"subtask_id":"push","tcp_end":[0.50391,0.10515,0.05929],"tcp_start":[0.50392,0.10519,0.05932],"tcp_to_object_dist_end":0.03755,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.36424,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11249,"descend.descend_force":6.16934,"descend.descend_speed":0.01004,"push.push_depth":0.17808,"push.push_max_time":4.57905,"push.push_speed":0.02328},"optimized_scores":{"best_composite_score":0.08593,"best_fitness_score":0.0826,"best_task_score":0.00378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49756,0.10042,0.00941],"force_p95":42.35428,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.52864,"mean_force":34.44386,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50333,0.13092,0.06074]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50977,0.12129,0.05852],"force_p95":41.9751,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.95765,"mean_force":34.03228,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50333,0.13092,0.06074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":617.0,"contact_point_centroid":[0.50603,0.10466,0.00939],"force_p95":0.57565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.50516,"mean_force":0.5787,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50988,0.15833,0.10563]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51028,0.12196,0.05881],"force_p95":20.07472,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.07472,"mean_force":20.07472,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50366,0.13157,0.06147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50531,0.10464,0.00936],"force_p95":0.60033,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.58162,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50908,0.19204,0.22212]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50022,0.19927,0.29532]}],"total_contact_groups":6},"final_pose_error":0.2055,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50509,0.1034,0.03386],"final_tcp_position":[0.50309,0.13024,0.06027],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":45.52864,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":900.0,"object_pos_end":[0.50593,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.52962,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":352.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51868,0.18546,0.15371],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14509,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":617.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.10455,0.03384],"object_pos_start":[0.50593,0.10472,0.03384],"object_to_goal_dist_end":0.18474,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":20.50516,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":618.0,"raw_peak_contact_force":20.50516,"subtask_id":"contact","tcp_end":[0.50365,0.1315,0.06134],"tcp_start":[0.51868,0.18546,0.15371],"tcp_to_object_dist_end":0.03858,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,0.10351,0.0339],"object_pos_start":[0.50592,0.10455,0.03384],"object_to_goal_dist_end":0.18369,"object_to_goal_dist_start":0.18474,"object_z_max":0.03395,"peak_contact_force":41.79254,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":36.0,"raw_peak_contact_force":45.52864,"subtask_id":"push","tcp_end":[0.50309,0.13024,0.06027],"tcp_start":[0.50311,0.13028,0.06031],"tcp_to_object_dist_end":0.0376,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```