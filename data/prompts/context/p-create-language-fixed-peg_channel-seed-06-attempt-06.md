## Search State

- **Seed**: 6
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2738 | 0.69 | ❌ rejected |
| 5 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3201 | 0.68 | ❌ rejected |
| 4 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3254 | 0.70 | ✅ accepted |
| 3 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0151 | 0.08 | ❌ rejected |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.3490 | 0.28 | ✅ accepted |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.274) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_behind_peg
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: engage_peg
  type: align
  generator: linear_cartesian
  control: position_control
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
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through_channel
  type: push
  generator: impedance_motion
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
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 1.0
      - 0.0
      - 0.0
      align_with: channel_axis
  parameters:
    lateral_jitter:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **engage_peg** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **push_through_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[1.0, 0.0, 0.0], align_with=channel_axis
  - parameter_bindings:
    - lateral_jitter: status=consumed; consumers=retry.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.274
- **task_score** (E): 0.686
- **fitness_score**: 0.604  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 1.00 | 1.00 | 0.2489 |
| engage_peg | 1.00 | 1.00 | 0.0274 |
| push_through_channel | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.144, 0.059) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.543 | 2.127 |
| engage_peg | align | 1.00 / step_budget | (0.497, 0.144, 0.059)→(0.496, 0.127, 0.038) | (0.501, 0.099, 0.034)→(0.501, 0.097, 0.035) | 0.180→0.177 | 1.00 / 1.333 | 1.990 | 14.078 |
| push_through_channel | push | 0.00 / guard_failure | (0.493, 0.003, 0.033)→(0.493, 0.002, 0.033) | (0.501, 0.097, 0.035)→(0.501, -0.025, 0.038) | 0.177→0.063 | 1.00 / 3.333 | 21.316 | 51.827 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.656
- phase_breakdown.push_score: 0.606
- phase_breakdown.approach_score: 0.675
- phase_breakdown.contact_score: 0.787

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.794
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.454
- **K-run variance**: 0.0685
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30263,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.10812,"engage_peg.align_speed":0.03218,"push_through_channel.force_limit":45.60292,"push_through_channel.lateral_jitter":-0.00061,"push_through_channel.push_distance":0.20164,"push_through_channel.push_speed":0.04895},"optimized_scores":{"best_composite_score":0.45401,"best_fitness_score":0.78401,"best_task_score":0.95091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":269.0,"contact_point_centroid":[0.49844,0.00363,0.04724],"force_p95":38.28866,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.18659,"mean_force":8.39194,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49555,0.01499,0.03328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49831,-0.10146,0.0405],"force_p95":41.03448,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.23206,"mean_force":18.06473,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49479,-0.05537,0.03244]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":77.0,"contact_point_centroid":[0.47461,0.01294,0.04434],"force_p95":39.09157,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.93009,"mean_force":14.11849,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4957,0.04212,0.03332]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":47.0,"contact_point_centroid":[0.5253,-0.0437,0.04037],"force_p95":26.63527,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.12092,"mean_force":10.14418,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49508,-0.01534,0.03275]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.50235,-0.01513,0.00945],"force_p95":12.88278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.99563,"mean_force":3.78314,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49557,0.02326,0.03336]},{"body_a":"peg","body_b":"channel_base_body","contact_count":110.0,"contact_point_centroid":[0.5028,0.06587,0.00938],"force_p95":0.5629,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.29797,"mean_force":0.74722,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.49827,0.1056,0.04705]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50201,0.08508,0.05704],"force_p95":11.79985,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.97863,"mean_force":5.74758,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.49842,0.09691,0.03845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.50311,0.06748,0.00933],"force_p95":0.56003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56453,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49876,0.15842,0.17771]}],"total_contact_groups":8},"final_pose_error":0.04814,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49778,-0.08675,0.03823],"final_tcp_position":[0.49457,-0.05834,0.03218],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":46.18659,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54768,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":481.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach","tcp_end":[0.49977,0.11488,0.05822],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":110.0,"n_steps_budget":720.0,"object_pos_end":[0.50289,0.06586,0.03485],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14598,"object_to_goal_dist_start":0.14758,"object_z_max":0.0347,"peak_contact_force":0.48183,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":114.0,"raw_peak_contact_force":13.29797,"subtask_id":"contact","tcp_end":[0.49854,0.09558,0.03721],"tcp_start":[0.49977,0.11488,0.05822],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.49778,-0.08644,0.03803],"object_pos_start":[0.50289,0.06586,0.03485],"object_to_goal_dist_end":0.00709,"object_to_goal_dist_start":0.14598,"object_z_max":0.04172,"peak_contact_force":10.38628,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":584.0,"raw_peak_contact_force":46.18659,"subtask_id":"push","tcp_end":[0.49457,-0.05834,0.03218],"tcp_start":[0.49462,-0.05824,0.03224],"tcp_to_object_dist_end":0.02888,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27368,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.0926,"engage_peg.align_speed":0.0358,"push_through_channel.force_limit":47.81975,"push_through_channel.lateral_jitter":0.00185,"push_through_channel.push_distance":0.21965,"push_through_channel.push_speed":0.041},"optimized_scores":{"best_composite_score":0.46362,"best_fitness_score":0.79362,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50774,-0.10082,0.06009],"force_p95":52.45035,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.10682,"mean_force":36.93804,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49766,-0.05463,0.03425]},{"body_a":"attachment","body_b":"peg","contact_count":337.0,"contact_point_centroid":[0.49907,0.02404,0.04866],"force_p95":35.67117,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.44682,"mean_force":8.83134,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49839,0.03537,0.03496]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":150.0,"contact_point_centroid":[0.47467,0.01195,0.04405],"force_p95":35.33583,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.94177,"mean_force":13.76819,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49839,0.0408,0.03485]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.49849,0.0037,0.0095],"force_p95":12.56679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.49446,"mean_force":3.59368,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49841,0.04301,0.03508]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.5254,-0.06686,0.03833],"force_p95":20.33658,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.14942,"mean_force":4.91732,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49788,-0.03752,0.03449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":88.0,"contact_point_centroid":[0.50334,0.11004,0.00943],"force_p95":2.12991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.10225,"mean_force":1.32611,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.50295,0.14797,0.04849]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.5029,0.12934,0.04616],"force_p95":17.63272,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.66736,"mean_force":14.10424,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.5015,0.14127,0.04056]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.50351,0.11161,0.00938],"force_p95":0.61882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56073,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50223,0.1774,0.17527]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49977,0.19977,0.29842]}],"total_contact_groups":9},"final_pose_error":0.02475,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.08384,0.03567],"final_tcp_position":[0.49739,-0.05583,0.03395],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":54.10682,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11173,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54958,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":464.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach","tcp_end":[0.50592,0.15519,0.05891],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":88.0,"n_steps_budget":630.0,"object_pos_end":[0.50331,0.1099,0.03504],"object_pos_start":[0.50373,0.11173,0.03383],"object_to_goal_dist_end":0.18999,"object_to_goal_dist_start":0.19187,"object_z_max":0.03493,"peak_contact_force":0.39046,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":93.0,"raw_peak_contact_force":18.10225,"subtask_id":"contact","tcp_end":[0.50131,0.1399,0.03898],"tcp_start":[0.50592,0.15519,0.05891],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50728,-0.08322,0.03589],"object_pos_start":[0.50331,0.1099,0.03504],"object_to_goal_dist_end":0.00896,"object_to_goal_dist_start":0.18999,"object_z_max":0.04039,"peak_contact_force":17.51061,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":738.0,"raw_peak_contact_force":54.10682,"subtask_id":"push","tcp_end":[0.49739,-0.05583,0.03395],"tcp_start":[0.49746,-0.05574,0.03403],"tcp_to_object_dist_end":0.02918,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31746,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.07874,"engage_peg.align_speed":0.02266,"push_through_channel.force_limit":46.3895,"push_through_channel.lateral_jitter":-0.00792,"push_through_channel.push_distance":0.18715,"push_through_channel.push_speed":0.04308},"optimized_scores":{"best_composite_score":-0.09636,"best_fitness_score":0.23364,"best_task_score":0.10604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.4749,0.11998,0.03572],"force_p95":52.31656,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.18677,"mean_force":24.96474,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48642,0.12222,0.03381]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49149,0.12469,0.03879],"force_p95":9.20234,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.03166,"mean_force":2.76169,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48758,0.13605,0.03539]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50152,0.09119,0.00975],"force_p95":9.68369,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.00781,"mean_force":3.04785,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48709,0.13228,0.03479]},{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.49644,0.11567,0.00947],"force_p95":1.06312,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.83441,"mean_force":0.78188,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.48549,0.15371,0.04752]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.4925,0.1363,0.05547],"force_p95":9.47448,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.59591,"mean_force":4.02465,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.48766,0.14794,0.04049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":442.0,"contact_point_centroid":[0.49632,0.11901,0.00938],"force_p95":0.61022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56052,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49134,0.18012,0.17426]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.49942,0.19964,0.29666]}],"total_contact_groups":7},"final_pose_error":0.16373,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49967,0.09302,0.039],"final_tcp_position":[0.48642,0.12163,0.03369],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":55.18677,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.11909,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19922,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53319,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48436,0.16169,0.05923],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":121.0,"n_steps_budget":990.0,"object_pos_end":[0.49645,0.11617,0.03636],"object_pos_start":[0.49605,0.11909,0.03392],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19922,"object_z_max":0.03624,"peak_contact_force":5.09821,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":129.0,"raw_peak_contact_force":10.83441,"subtask_id":"contact","tcp_end":[0.48899,0.14511,0.0372],"tcp_start":[0.48436,0.16169,0.05923],"tcp_to_object_dist_end":0.0299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.49932,0.09392,0.03888],"object_pos_start":[0.49645,0.11617,0.03636],"object_to_goal_dist_end":0.17393,"object_to_goal_dist_start":0.19623,"object_z_max":0.039,"peak_contact_force":36.05205,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":69.0,"raw_peak_contact_force":55.18677,"subtask_id":"push","tcp_end":[0.48642,0.12163,0.03369],"tcp_start":[0.48643,0.12181,0.03374],"tcp_to_object_dist_end":0.031,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```