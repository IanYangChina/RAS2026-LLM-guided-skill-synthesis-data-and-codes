## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.3137 | 0.22 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0479 | 0.05 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3169 | 0.66 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2074 | 0.63 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3576 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.314) — your mutation base

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

- **Composite score**: 0.314
- **task_score** (E): 0.220
- **fitness_score**: 0.260  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre | 1.00 | 1.00 | 0.2301 |
| descend_contact | 1.00 | 1.00 | 0.0419 |
| push_channel | 1.00 | 1.00 | 0.0412 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.079) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.567 | 2.127 |
| descend_contact | descend | 1.00 / step_budget | (0.496, 0.142, 0.079)→(0.496, 0.125, 0.041) | (0.501, 0.099, 0.034)→(0.503, 0.095, 0.035) | 0.180→0.175 | 1.00 / 1.333 | 3.383 | 16.475 |
| push_channel | push | 1.00 / force_exceeded | (0.496, 0.125, 0.041)→(0.493, 0.084, 0.037) | (0.503, 0.095, 0.035)→(0.507, 0.058, 0.037) | 0.175→0.138 | 1.00 / 2.667 | 2694.182 | 19.496 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.330
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.330
- phase_score: 0.274
- phase_breakdown.push_score: 0.035
- phase_breakdown.contact_score: 0.808
- phase_breakdown.approach_score: 0.459

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.297
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.330
- **Median Q (composite search score)**: 0.326
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47561,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.11174,"descend_contact.descend_speed":0.07766,"push_channel.push_distance":0.15002,"push_channel.push_force_threshold":42.97296,"push_channel.push_speed":0.0536},"optimized_scores":{"best_composite_score":0.32555,"best_fitness_score":0.27222,"best_task_score":0.22542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":146.0,"contact_point_centroid":[0.50288,0.06401,0.00944],"force_p95":0.61517,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.34462,"mean_force":0.91147,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49823,0.10297,0.05954]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50084,0.0839,0.05086],"force_p95":12.91593,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.16522,"mean_force":9.40373,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49831,0.09575,0.0456]},{"body_a":"peg","body_b":"channel_base_body","contact_count":276.0,"contact_point_centroid":[0.50475,0.03147,0.00995],"force_p95":5.97076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.66955,"mean_force":3.45702,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49519,0.07583,0.03652]},{"body_a":"attachment","body_b":"peg","contact_count":297.0,"contact_point_centroid":[0.49967,0.06329,0.04133],"force_p95":6.30308,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.63682,"mean_force":3.12985,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49511,0.07461,0.03643]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":151.0,"contact_point_centroid":[0.52511,0.03948,0.02974],"force_p95":3.44394,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.93801,"mean_force":1.56602,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49472,0.0663,0.036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.55478,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55868,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49889,0.15499,0.18578]}],"total_contact_groups":6},"final_pose_error":0.11581,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50695,0.0314,0.03633],"final_tcp_position":[0.49471,0.05869,0.03601],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3920.93032,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54764,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":715.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49947,0.11181,0.07796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":150.0,"n_steps_budget":600.0,"object_pos_end":[0.50389,0.06387,0.03591],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14758,"object_z_max":0.03595,"peak_contact_force":9.33229,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":152.0,"raw_peak_contact_force":13.34462,"subtask_id":"contact","tcp_end":[0.49858,0.09306,0.04055],"tcp_start":[0.49947,0.11181,0.07796],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.0314,0.03633],"object_pos_start":[0.50389,0.06387,0.03591],"object_to_goal_dist_end":0.11167,"object_to_goal_dist_start":0.14398,"object_z_max":0.03639,"peak_contact_force":3920.93032,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":724.0,"raw_peak_contact_force":9.66955,"subtask_id":"push","tcp_end":[0.49471,0.05869,0.03601],"tcp_start":[0.49858,0.09306,0.04055],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.10265,"descend_contact.descend_speed":0.06927,"push_channel.push_distance":0.19609,"push_channel.push_force_threshold":39.24026,"push_channel.push_speed":0.02442},"optimized_scores":{"best_composite_score":0.35003,"best_fitness_score":0.29669,"best_task_score":0.33012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":133.0,"contact_point_centroid":[0.50336,0.10751,0.00944],"force_p95":18.3857,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.92062,"mean_force":2.14785,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50293,0.14593,0.06081]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50276,0.12765,0.05059],"force_p95":21.35146,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.69163,"mean_force":10.84688,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50136,0.13962,0.04692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":728.0,"contact_point_centroid":[0.50183,0.06453,0.00995],"force_p95":3.51425,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.67706,"mean_force":2.49823,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49733,0.11053,0.03719]},{"body_a":"attachment","body_b":"peg","contact_count":773.0,"contact_point_centroid":[0.49992,0.09808,0.0407],"force_p95":3.3657,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.27808,"mean_force":2.05876,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49728,0.10984,0.03713]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52503,0.06509,0.02886],"force_p95":4.84491,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.38046,"mean_force":1.54612,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49741,0.09287,0.03736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":666.0,"contact_point_centroid":[0.50358,0.11172,0.00937],"force_p95":0.60915,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55689,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.50224,0.17591,0.18529]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49983,0.19942,0.29879]}],"total_contact_groups":7},"final_pose_error":0.14622,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50699,0.05896,0.03601],"final_tcp_position":[0.49711,0.08723,0.03702],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3920.40198,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.61057,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":682.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50601,0.15363,0.07874],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":138.0,"n_steps_budget":600.0,"object_pos_end":[0.50579,0.10728,0.03452],"object_pos_start":[0.50377,0.11176,0.0338],"object_to_goal_dist_end":0.18745,"object_to_goal_dist_start":0.1919,"object_z_max":0.0356,"peak_contact_force":0.78991,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":153.0,"raw_peak_contact_force":21.92062,"subtask_id":"contact","tcp_end":[0.50098,0.13722,0.04167],"tcp_start":[0.50601,0.15363,0.07874],"tcp_to_object_dist_end":0.03116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":849.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.05896,0.03601],"object_pos_start":[0.50579,0.10728,0.03452],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.18745,"object_z_max":0.03604,"peak_contact_force":3920.40198,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1545.0,"raw_peak_contact_force":7.67706,"subtask_id":"push","tcp_end":[0.49711,0.08723,0.03702],"tcp_start":[0.50098,0.13722,0.04167],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36667,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre.approach_speed":0.07656,"descend_contact.descend_speed":0.04006,"push_channel.push_distance":0.17235,"push_channel.push_force_threshold":41.10963,"push_channel.push_speed":0.02028},"optimized_scores":{"best_composite_score":0.26556,"best_fitness_score":0.21223,"best_task_score":0.10411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":358.0,"contact_point_centroid":[0.47499,0.11538,0.03832],"force_p95":34.98494,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":41.14131,"mean_force":24.24528,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48667,0.11654,0.03651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.4967,0.11465,0.0095],"force_p95":9.33691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.15971,"mean_force":1.35055,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48546,0.15228,0.06011]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.49216,0.13353,0.04762],"force_p95":13.84392,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.871,"mean_force":7.00559,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48863,0.14509,0.04408]},{"body_a":"attachment","body_b":"peg","contact_count":624.0,"contact_point_centroid":[0.49469,0.11244,0.04231],"force_p95":5.50632,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.52964,"mean_force":2.50172,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48653,0.12194,0.03637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.50686,0.08506,0.00997],"force_p95":5.00713,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.9114,"mean_force":2.04587,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48655,0.12351,0.0364]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":307.0,"contact_point_centroid":[0.52507,0.09322,0.03428],"force_p95":4.29657,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.83582,"mean_force":2.39196,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48682,0.11488,0.03667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":668.0,"contact_point_centroid":[0.49618,0.1191,0.00944],"force_p95":0.60726,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55053,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49093,0.17937,0.18557]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_pre","phase_type":"approach","tcp_position_centroid":[0.49955,0.19927,0.29776]}],"total_contact_groups":8},"final_pose_error":0.13433,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50696,0.08227,0.03815],"final_tcp_position":[0.48684,0.10527,0.03663],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":241.21393,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11913,0.03402],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54389,"phase_name":"approach_pre","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48365,0.1604,0.07937],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":165.0,"n_steps_budget":810.0,"object_pos_end":[0.49819,0.11469,0.03537],"object_pos_start":[0.49602,0.11913,0.03402],"object_to_goal_dist_end":0.19476,"object_to_goal_dist_start":0.19926,"object_z_max":0.03623,"peak_contact_force":0.02546,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":178.0,"raw_peak_contact_force":14.15971,"subtask_id":"contact","tcp_end":[0.48961,0.14336,0.04019],"tcp_start":[0.48365,0.1604,0.07937],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.50696,0.08227,0.03815],"object_pos_start":[0.49819,0.11469,0.03537],"object_to_goal_dist_end":0.16243,"object_to_goal_dist_start":0.19476,"object_z_max":0.03824,"peak_contact_force":241.21393,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1922.0,"raw_peak_contact_force":41.14131,"subtask_id":"push","tcp_end":[0.48684,0.10527,0.03663],"tcp_start":[0.48961,0.14336,0.04019],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```