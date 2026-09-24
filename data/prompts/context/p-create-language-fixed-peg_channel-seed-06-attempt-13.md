## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.3200 | 0.02 | ❌ rejected |
| 12 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1442 | 0.56 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0809 | 0.60 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3150 | 0.68 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1157 | 0.53 | ❌ rejected |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.320) — your mutation base

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

- **Composite score**: -0.320
- **task_score** (E): 0.018
- **fitness_score**: 0.010  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind_peg | 0.00 | 1.00 | 0.1061 |
| engage_peg | 0.00 | 1.00 | 0.0367 |
| push_through_channel | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind_peg | approach | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.550, 0.128, 0.260) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 2.000 | 246.967 | 1710.135 |
| engage_peg | align | 0.00 / step_budget | (0.550, 0.128, 0.260)→(0.538, 0.108, 0.275) | (0.501, 0.099, 0.034)→(0.502, 0.110, 0.027) | 0.180→0.191 | 1.00 / 2.333 | 343.090 | 566.392 |
| push_through_channel | push | 0.00 / guard_failure | (0.537, 0.108, 0.276)→(0.537, 0.108, 0.276) | (0.502, 0.110, 0.027)→(0.502, 0.110, 0.027) | 0.191→0.191 | 1.00 / 1.667 | 124.519 | 226.952 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.052
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.052
- phase_score: 0.006
- phase_breakdown.push_score: 0.004
- phase_breakdown.approach_score: 0.008
- phase_breakdown.contact_score: 0.007

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.024
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.052
- **Median Q (composite search score)**: -0.327
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.304


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24324,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.05021,"engage_peg.align_speed":0.03576,"push_through_channel.lateral_jitter":-0.00541,"push_through_channel.lateral_offset":-0.01492,"push_through_channel.push_distance":0.22399,"push_through_channel.push_speed":0.04628},"optimized_scores":{"best_composite_score":-0.3057,"best_fitness_score":0.0243,"best_task_score":0.05227},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":848.0,"contact_point_centroid":[0.55094,0.11662,0.0597],"force_p95":477.52946,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1540.63069,"mean_force":398.90512,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.52192,0.15589,0.27283]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":875.0,"contact_point_centroid":[0.52553,0.08036,0.05995],"force_p95":625.82209,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":660.73938,"mean_force":312.29308,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.47505,0.04818,0.281]},{"body_a":"channel_right_wall","body_b":"link6","contact_count":535.0,"contact_point_centroid":[0.475,0.05774,0.05997],"force_p95":484.84256,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":598.52687,"mean_force":301.01287,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.47133,0.04163,0.27977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5051,0.07618,0.00944],"force_p95":49.23207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.99985,"mean_force":33.07294,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.4758,0.0487,0.28109]},{"body_a":"peg","body_b":"link6","contact_count":898.0,"contact_point_centroid":[0.50485,0.08048,0.05819],"force_p95":48.82456,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.52247,"mean_force":36.28636,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.47332,0.04555,0.28061]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.52502,0.0824,0.05994],"force_p95":118.26095,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.22944,"mean_force":82.54451,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.46112,0.04875,0.27797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.48932,0.06257,0.00924],"force_p95":95.535,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.4388,"mean_force":47.36959,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.46088,0.04875,0.27817]},{"body_a":"peg","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.50112,0.07706,0.05784],"force_p95":94.90764,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.82131,"mean_force":46.68503,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.46088,0.04875,0.27817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.51929,0.16087,0.26668]}],"total_contact_groups":9},"final_pose_error":0.22439,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50277,0.0591,0.03406],"final_tcp_position":[0.46003,0.0487,0.27891],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1540.63069,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":445.70633,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":1540.63069,"subtask_id":"approach","tcp_end":[0.50607,0.08842,0.2784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.24552,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50365,0.05933,0.03351],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.13953,"object_to_goal_dist_start":0.14759,"object_z_max":0.03506,"peak_contact_force":537.65548,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3308.0,"raw_peak_contact_force":660.73938,"subtask_id":"contact","tcp_end":[0.4612,0.04873,0.27792],"tcp_start":[0.50607,0.08842,0.2784],"tcp_to_object_dist_end":0.2483,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.5036,0.0593,0.03353],"object_pos_start":[0.50365,0.05933,0.03351],"object_to_goal_dist_end":0.1395,"object_to_goal_dist_start":0.13953,"object_z_max":0.0338,"peak_contact_force":97.4388,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":122.22944,"subtask_id":"push","tcp_end":[0.46003,0.0487,0.27891],"tcp_start":[0.46047,0.04874,0.27852],"tcp_to_object_dist_end":0.24944,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77895,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.10593,"engage_peg.align_speed":0.02055,"push_through_channel.lateral_jitter":0.00062,"push_through_channel.lateral_offset":-0.00674,"push_through_channel.push_distance":0.17734,"push_through_channel.push_speed":0.03548},"optimized_scores":{"best_composite_score":-0.32686,"best_fitness_score":0.00314,"best_task_score":0.00059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":776.0,"contact_point_centroid":[0.5548,0.10353,0.05968],"force_p95":508.11226,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1766.75872,"mean_force":380.37607,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.54622,0.1712,0.26078]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.55497,0.08641,0.05994],"force_p95":293.6022,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.46545,"mean_force":251.46477,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.59377,0.13009,0.26953]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55498,0.08894,0.05996],"force_p95":283.0691,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.0691,"mean_force":283.0691,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.58309,0.13446,0.27136]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50359,0.11165,0.00939],"force_p95":0.60422,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55171,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.54135,0.17537,0.25562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.5037,0.11159,0.00942],"force_p95":0.59745,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65366,"mean_force":0.54267,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.59373,0.13022,0.2693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50444,0.1138,0.00938],"force_p95":0.59264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59816,"mean_force":0.54855,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.58307,0.13436,0.27178]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50173,0.20104,0.29783]},{"body_a":"peg","body_b":"link6","contact_count":16.0,"contact_point_centroid":[0.51828,0.11984,0.05687],"force_p95":0.0,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.43612,0.25434,0.12335]}],"total_contact_groups":8},"final_pose_error":0.17721,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50376,0.11168,0.03379],"final_tcp_position":[0.58299,0.13421,0.27226],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1766.75872,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11177,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":293.74909,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1786.0,"raw_peak_contact_force":1766.75872,"subtask_id":"approach","tcp_end":[0.58243,0.14289,0.24858],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23085,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.1117,0.03379],"object_pos_start":[0.50373,0.11177,0.03381],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19191,"object_z_max":0.03406,"peak_contact_force":250.34524,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1975.0,"raw_peak_contact_force":541.46545,"subtask_id":"contact","tcp_end":[0.58309,0.13446,0.27136],"tcp_start":[0.58243,0.14289,0.24858],"tcp_to_object_dist_end":0.25151,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.1117,0.03379],"object_pos_start":[0.50369,0.1117,0.03379],"object_to_goal_dist_end":0.19184,"object_to_goal_dist_start":0.19184,"object_z_max":0.03379,"peak_contact_force":0.56139,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":283.0691,"subtask_id":"push","tcp_end":[0.58299,0.13421,0.27226],"tcp_start":[0.583,0.13425,0.27214],"tcp_to_object_dist_end":0.2523,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78788,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind_peg.approach_speed":0.09743,"engage_peg.align_speed":0.03173,"push_through_channel.lateral_jitter":0.00824,"push_through_channel.lateral_offset":-0.00029,"push_through_channel.push_distance":0.16786,"push_through_channel.push_speed":0.03238},"optimized_scores":{"best_composite_score":-0.3274,"best_fitness_score":0.0026,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link6","contact_count":773.0,"contact_point_centroid":[0.55483,0.10631,0.05972],"force_p95":453.25309,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1823.01496,"mean_force":362.66583,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.53601,0.17505,0.25967]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.55498,0.10109,0.05995],"force_p95":271.443,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.97161,"mean_force":242.25604,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.57857,0.13833,0.27429]},{"body_a":"channel_left_wall","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.55498,0.10359,0.05996],"force_p95":275.55615,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.55615,"mean_force":275.55615,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.56887,0.14215,0.27563]},{"body_a":"peg","body_b":"world","contact_count":164.0,"contact_point_centroid":[0.4966,0.15421,-0.00152],"force_p95":1.10157,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.8931,"mean_force":0.63222,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.57072,0.14144,0.27554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":952.0,"contact_point_centroid":[0.49613,0.11931,0.00943],"force_p95":0.60369,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54894,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.53228,0.17863,0.25448]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.50235,0.19968,0.29278]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.49752,0.17257,-0.00198],"force_p95":0.71264,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72598,"mean_force":0.60605,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.56886,0.14205,0.27607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":833.0,"contact_point_centroid":[0.49608,0.11928,0.00946],"force_p95":0.60175,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65497,"mean_force":0.53353,"phase_index":1.0,"phase_name":"engage_peg","phase_type":"align","tcp_position_centroid":[0.57997,0.13791,0.27375]},{"body_a":"peg","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.51068,0.1274,0.05733],"force_p95":0.0,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_behind_peg","phase_type":"approach","tcp_position_centroid":[0.43366,0.25033,0.1132]}],"total_contact_groups":9},"final_pose_error":0.16762,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49744,0.16001,0.0141],"final_tcp_position":[0.56877,0.1419,0.27659],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1823.01496,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.49596,0.11909,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":1.44579,"phase_name":"approach_behind_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1762.0,"raw_peak_contact_force":1823.01496,"subtask_id":"approach","tcp_end":[0.56244,0.15199,0.25243],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23085,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49739,0.16013,0.0141],"object_pos_start":[0.49596,0.11909,0.03382],"object_to_goal_dist_end":0.24154,"object_to_goal_dist_start":0.19923,"object_z_max":0.03408,"peak_contact_force":241.27031,"phase_name":"engage_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1974.0,"raw_peak_contact_force":496.97161,"subtask_id":"contact","tcp_end":[0.56887,0.14215,0.27563],"tcp_start":[0.56244,0.15199,0.25243],"tcp_to_object_dist_end":0.27172,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49741,0.16013,0.0141],"object_pos_start":[0.49739,0.16013,0.0141],"object_to_goal_dist_end":0.24153,"object_to_goal_dist_start":0.24154,"object_z_max":0.0141,"peak_contact_force":275.55615,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":275.55615,"subtask_id":"push","tcp_end":[0.56877,0.1419,0.27659],"tcp_start":[0.56879,0.14195,0.27646],"tcp_to_object_dist_end":0.27263,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```