## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3576 | 0.77 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1856 | 0.68 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0481 | 0.16 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3414 | 0.69 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2134 | 0.67 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.358) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_pre
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
    - 0.04
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.22
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.358
- **task_score** (E): 0.768
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre | 1.00 | 1.00 | 0.2300 |
| descend_contact | 1.00 | 1.00 | 0.0422 |
| push_channel | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.079) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.562 | 2.127 |
| descend_contact | descend | 1.00 / step_budget | (0.496, 0.142, 0.079)→(0.496, 0.125, 0.041) | (0.501, 0.099, 0.034)→(0.503, 0.095, 0.035) | 0.180→0.175 | 1.00 / 1.333 | 1.973 | 18.950 |
| push_channel | push | 0.00 / guard_failure | (0.498, -0.022, 0.032)→(0.498, -0.022, 0.032) | (0.503, 0.095, 0.035)→(0.505, -0.049, 0.036) | 0.175→0.032 | 1.00 / 2.333 | 10.241 | 46.817 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.913
- alignment_error: None
- force_efficiency: 0.013
- terminal_score: 0.913
- phase_score: 0.581
- phase_breakdown.push_score: 0.525
- phase_breakdown.contact_score: 0.866
- phase_breakdown.approach_score: 0.462

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.714
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.437
- **K-run variance**: 0.0214
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09816,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.05872,"descend_contact.descend_speed":0.05874,"push_channel.push_distance":0.18144,"push_channel.push_speed":0.06419},"optimized_scores":{"best_composite_score":0.48367,"best_fitness_score":0.71367,"best_task_score":0.91297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":118.0,"contact_point_centroid":[0.50155,0.0141,0.05144],"force_p95":22.5741,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.34608,"mean_force":4.21083,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49843,0.0253,0.03488]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50145,-0.10026,0.05632],"force_p95":37.16897,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.83083,"mean_force":17.18798,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50047,-0.04749,0.03213]},{"body_a":"peg","body_b":"channel_base_body","contact_count":106.0,"contact_point_centroid":[0.50433,-0.00815,0.00909],"force_p95":23.6799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.47033,"mean_force":4.8914,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49839,0.03143,0.03531]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50385,0.0645,0.00941],"force_p95":7.75605,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.45867,"mean_force":1.50804,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49821,0.10329,0.06014]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50064,0.08404,0.04942],"force_p95":22.14257,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.1655,"mean_force":15.41012,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49834,0.09582,0.04561]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":46.0,"contact_point_centroid":[0.52538,0.00617,0.03481],"force_p95":6.74334,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.04343,"mean_force":1.55684,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49829,0.0361,0.0356]},{"body_a":"peg","body_b":"channel_base_body","contact_count":784.0,"contact_point_centroid":[0.50303,0.06748,0.00935],"force_p95":0.55349,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55762,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.4988,0.15508,0.18601]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47482,-0.02514,0.02239],"force_p95":1.0685,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13044,"mean_force":0.7238,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49868,0.00856,0.03387]},{"body_a":"peg","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.51917,-0.05767,0.07037],"force_p95":0.3923,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48168,"mean_force":0.0991,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49992,-0.03032,0.03265]}],"total_contact_groups":9},"final_pose_error":0.07021,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5006,-0.07861,0.03509],"final_tcp_position":[0.50043,-0.04883,0.03204],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":49.34608,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54722,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49944,0.11191,0.07819],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":152.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.06268,0.03494],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14289,"object_to_goal_dist_start":0.14764,"object_z_max":0.03585,"peak_contact_force":0.75457,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":152.0,"raw_peak_contact_force":22.45867,"subtask_id":"contact","tcp_end":[0.49866,0.09315,0.04044],"tcp_start":[0.49944,0.11191,0.07819],"tcp_to_object_dist_end":0.03182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.5009,-0.07842,0.03501],"object_pos_start":[0.50598,0.06268,0.03494],"object_to_goal_dist_end":0.00531,"object_to_goal_dist_start":0.14289,"object_z_max":0.04545,"peak_contact_force":23.0103,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":295.0,"raw_peak_contact_force":49.34608,"subtask_id":"push","tcp_end":[0.50043,-0.04883,0.03204],"tcp_start":[0.50048,-0.04852,0.03208],"tcp_to_object_dist_end":0.02975,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22652,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.09113,"descend_contact.descend_speed":0.04882,"push_channel.push_distance":0.17567,"push_channel.push_speed":0.03733},"optimized_scores":{"best_composite_score":0.4365,"best_fitness_score":0.6665,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_left_wall","contact_count":213.0,"contact_point_centroid":[0.52526,0.03241,0.03879],"force_p95":36.07127,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.32951,"mean_force":8.71415,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49869,0.06141,0.03491]},{"body_a":"attachment","body_b":"peg","contact_count":194.0,"contact_point_centroid":[0.50344,0.05102,0.04953],"force_p95":36.67475,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.1692,"mean_force":11.64678,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4988,0.06248,0.03508]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.5046,0.01412,0.00959],"force_p95":28.47331,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.02593,"mean_force":7.09832,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49912,0.05612,0.03518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":136.0,"contact_point_centroid":[0.50384,0.10696,0.00946],"force_p95":18.60864,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.01035,"mean_force":2.99186,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50286,0.14585,0.06069]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50235,0.12703,0.04618],"force_p95":21.62376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.82269,"mean_force":14.17067,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50123,0.13888,0.0453]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.50361,0.11166,0.00939],"force_p95":0.6079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55544,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.50224,0.176,0.18567]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49982,0.19942,0.29885]}],"total_contact_groups":7},"final_pose_error":0.04497,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50752,-0.05212,0.03774],"final_tcp_position":[0.49973,-0.02334,0.03201],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":45.32951,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11174,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.52364,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":690.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50596,0.15364,0.0788],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":140.0,"n_steps_budget":660.0,"object_pos_end":[0.50366,0.10767,0.0355],"object_pos_start":[0.50376,0.11174,0.03384],"object_to_goal_dist_end":0.18776,"object_to_goal_dist_start":0.19187,"object_z_max":0.0357,"peak_contact_force":0.12018,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":160.0,"raw_peak_contact_force":22.01035,"subtask_id":"contact","tcp_end":[0.50101,0.13731,0.04155],"tcp_start":[0.50596,0.15364,0.0788],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.50748,-0.05089,0.03764],"object_pos_start":[0.50366,0.10767,0.0355],"object_to_goal_dist_end":0.03015,"object_to_goal_dist_start":0.18776,"object_z_max":0.03855,"peak_contact_force":7.52426,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":491.0,"raw_peak_contact_force":45.32951,"subtask_id":"push","tcp_end":[0.49973,-0.02334,0.03201],"tcp_start":[0.4998,-0.02299,0.03208],"tcp_to_object_dist_end":0.02917,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96567,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.07104,"descend_contact.descend_speed":0.01727,"push_channel.push_distance":0.16713,"push_channel.push_speed":0.02817},"optimized_scores":{"best_composite_score":0.15254,"best_fitness_score":0.38254,"best_task_score":0.39178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":142.0,"contact_point_centroid":[0.49619,0.07046,0.04377],"force_p95":13.19406,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.77582,"mean_force":3.55757,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48991,0.08102,0.03498]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.50187,0.03684,0.0096],"force_p95":14.59539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.51669,"mean_force":4.61943,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49015,0.07711,0.03493]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":117.0,"contact_point_centroid":[0.52545,0.03132,0.03281],"force_p95":11.2691,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.59195,"mean_force":2.19337,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49063,0.05697,0.03372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":172.0,"contact_point_centroid":[0.49761,0.11472,0.00948],"force_p95":2.5202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.38173,"mean_force":0.91688,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48526,0.15242,0.06041]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49262,0.13442,0.05681],"force_p95":11.88011,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.0375,"mean_force":5.22129,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.488,0.14601,0.04611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":670.0,"contact_point_centroid":[0.49624,0.11907,0.00942],"force_p95":0.61755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5528,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49092,0.17939,0.18573]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49956,0.19927,0.29774]}],"total_contact_groups":7},"final_pose_error":0.05826,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50706,-0.01982,0.03673],"final_tcp_position":[0.49285,0.00586,0.03223],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":45.77582,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":695.0,"n_steps_budget":1000.0,"object_pos_end":[0.49598,0.1191,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.61493,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":694.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48366,0.16043,0.07952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":179.0,"n_steps_budget":1000.0,"object_pos_end":[0.49871,0.11511,0.03542],"object_pos_start":[0.49598,0.1191,0.03382],"object_to_goal_dist_end":0.19517,"object_to_goal_dist_start":0.19924,"object_z_max":0.03601,"peak_contact_force":5.04328,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":185.0,"raw_peak_contact_force":12.38173,"subtask_id":"contact","tcp_end":[0.4895,0.14324,0.04004],"tcp_start":[0.48366,0.16043,0.07952],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.01908,0.03635],"object_pos_start":[0.49871,0.11511,0.03542],"object_to_goal_dist_end":0.06143,"object_to_goal_dist_start":0.19517,"object_z_max":0.04215,"peak_contact_force":0.18809,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":343.0,"raw_peak_contact_force":45.77582,"subtask_id":"push","tcp_end":[0.49285,0.00586,0.03223],"tcp_start":[0.49287,0.00621,0.03227],"tcp_to_object_dist_end":0.02897,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```