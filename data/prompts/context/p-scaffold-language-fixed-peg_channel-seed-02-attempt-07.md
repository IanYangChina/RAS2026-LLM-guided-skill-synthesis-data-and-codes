## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → descend → align → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.4169 | 0.26 | ❌ rejected |
| 6 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4315 | 0.09 | ❌ rejected |
| 5 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4994 | 0.25 | ✅ accepted |
| 4 | approach → approach → descend → contact → push → retract | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 19 | 0.0959 | 0.39 | ✅ accepted |
| 3 | align → approach → descend → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.0353 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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

## Current Skill (Q=-0.417) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
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
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.12
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_1
  type: descend
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
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.005
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 8.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.015
      default: 0.005
      binds_to:
      - path: target.offset.y
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_check
    when: after_phase
    predicate: force_below
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.002
    - 0.0
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
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
      distance: 0.12
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: push_force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Design Metrics

- **Composite score**: -0.417
- **task_score** (E): 0.257
- **fitness_score**: 0.266  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.850

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2768 |
| approach_1 | 1.00 | 1.00 | 0.0858 |
| descend_1 | 1.00 | 0.67 | 0.0896 |
| align_2 | 1.00 | 1.00 | 0.0271 |
| contact_1 | 1.00 | 1.00 | 0.0083 |
| push_1 | 1.00 | 1.00 | 0.0655 |
| retract_1 | 1.00 | 1.00 | 0.1145 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.074, 0.054) | (0.494, 0.068, 0.040)→(0.500, 0.066, 0.030) | 0.151→0.146 | 1.00 / 2.000 | 236.044 | 372.178 |
| approach_1 | approach | 1.00 / step_budget | (0.502, 0.074, 0.054)→(0.497, 0.105, 0.134) | (0.500, 0.066, 0.030)→(0.499, 0.066, 0.034) | 0.146→0.146 | 1.00 / 1.000 | 0.541 | 78.833 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.105, 0.134)→(0.497, 0.089, 0.046) | (0.499, 0.066, 0.034)→(0.499, 0.050, 0.037) | 0.146→0.130 | 0.67 / 1.000 | 34.100 | 135.027 |
| align_2 | align | 1.00 / step_budget | (0.497, 0.089, 0.046)→(0.497, 0.065, 0.037) | (0.499, 0.050, 0.037)→(0.499, 0.021, 0.033) | 0.130→0.102 | 1.00 / 1.333 | 2.049 | 65.497 |
| contact_1 | contact | 1.00 / force_exceeded | (0.497, 0.065, 0.037)→(0.496, 0.057, 0.034) | (0.499, 0.021, 0.033)→(0.502, 0.011, 0.026) | 0.102→0.092 | 1.00 / 2.000 | 5.940 | 5.940 |
| push_1 | push | 1.00 / time_limit | (0.496, 0.057, 0.034)→(0.494, -0.008, 0.027) | (0.502, 0.011, 0.026)→(0.501, -0.044, 0.027) | 0.092→0.040 | 1.00 / 2.333 | 5.434 | 14.293 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.008, 0.027)→(0.492, -0.001, 0.142) | (0.501, -0.044, 0.027)→(0.500, -0.044, 0.024) | 0.040→0.040 | 1.00 / 1.000 | 0.571 | 26.018 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.699
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.424
- phase_score: 0.292
- phase_breakdown.approach_score: 0.191
- phase_breakdown.push_score: 0.248
- phase_breakdown.contact_score: 0.524

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.345
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.424
- **Median Q (composite search score)**: -0.421
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: contact_1.contact_offset_y
- **Final σ (mean)**: 0.317


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53081,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00914,"align_1.lateral_offset_y":-0.001,"align_2.align_x":-0.01224,"align_2.align_y":-0.01125,"approach_1.approach_height":0.11309,"approach_1.generator.speed":0.1282,"contact_1.contact_force_threshold":3.99536,"contact_1.contact_offset_y":0.015,"contact_1.generator.speed":0.04627,"descend_1.descend_z":0.01269,"push_1.generator.speed":0.01806,"push_1.push_depth":0.17965,"push_1.push_time":2.33843,"retract_1.retract_height":0.1774},"optimized_scores":{"best_composite_score":-0.3387,"best_fitness_score":0.34463,"best_task_score":0.4242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.50461,0.06635,0.00792],"force_p95":177.54991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.44777,"mean_force":130.29968,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49582,0.07863,0.05072]},{"body_a":"attachment","body_b":"peg","contact_count":262.0,"contact_point_centroid":[0.50522,0.07202,0.05293],"force_p95":177.1385,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.00286,"mean_force":140.72929,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49602,0.07896,0.05129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":899.0,"contact_point_centroid":[0.49611,0.06395,0.00926],"force_p95":100.97083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.21079,"mean_force":10.04821,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4925,0.12994,0.1643]},{"body_a":"attachment","body_b":"peg","contact_count":78.0,"contact_point_centroid":[0.50187,0.0704,0.05431],"force_p95":163.10459,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.64159,"mean_force":109.4468,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49002,0.07149,0.05418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":231.0,"contact_point_centroid":[0.49723,0.06173,0.00944],"force_p95":91.57542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.93804,"mean_force":8.76112,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49256,0.0913,0.0886]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50397,0.07878,0.05771],"force_p95":100.5894,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.44079,"mean_force":86.3992,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49349,0.08445,0.05832]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.4969,0.06386,0.00923],"force_p95":47.15758,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.19923,"mean_force":6.02939,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4924,0.08713,0.08385]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.50241,0.0657,0.0555],"force_p95":63.46441,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.5182,"mean_force":28.35441,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49273,0.07177,0.0551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":906.0,"contact_point_centroid":[0.50644,-0.03074,0.00951],"force_p95":4.49957,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.61052,"mean_force":2.12395,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48891,0.02103,0.03005]},{"body_a":"peg","body_b":"channel_base_body","contact_count":338.0,"contact_point_centroid":[0.50149,0.00661,0.00807],"force_p95":0.93297,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.03618,"mean_force":0.65509,"phase_index":4.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48939,0.06185,0.03667]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,-0.01797,0.02418],"force_p95":8.20925,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.6188,"mean_force":4.52331,"phase_index":4.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49036,0.05328,0.03592]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":512.0,"contact_point_centroid":[0.52502,-0.04633,0.02781],"force_p95":4.15717,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.49535,"mean_force":2.8207,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48935,0.0119,0.02934]},{"body_a":"attachment","body_b":"peg","contact_count":805.0,"contact_point_centroid":[0.49259,0.00188,0.04271],"force_p95":6.71435,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.00863,"mean_force":3.03885,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4892,0.01383,0.02944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":284.0,"contact_point_centroid":[0.49744,-0.04894,0.00831],"force_p95":0.76091,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.55596,"mean_force":0.67087,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48861,-0.00039,0.10022]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47494,-0.02545,0.02444],"force_p95":7.19403,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.32013,"mean_force":2.34894,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48836,0.00191,0.07941]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49947,0.19839,0.29707]}],"total_contact_groups":17},"final_pose_error":0.02965,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49591,-0.04793,0.02424],"final_tcp_position":[0.48889,-0.00498,0.17669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":180.44777,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.49726,0.06025,0.02803],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14079,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":141.51738,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1005.0,"raw_peak_contact_force":169.21079,"tcp_end":[0.49272,0.06804,0.04948],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":600.0,"object_pos_end":[0.49695,0.0612,0.03456],"object_pos_start":[0.49726,0.06025,0.02803],"object_to_goal_dist_end":0.14134,"object_to_goal_dist_start":0.14079,"object_z_max":0.03633,"peak_contact_force":0.5343,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":283.0,"raw_peak_contact_force":95.19923,"subtask_id":"approach","tcp_end":[0.4936,0.0986,0.1217],"tcp_start":[0.49272,0.06804,0.04948],"tcp_to_object_dist_end":0.09489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":231.0,"n_steps_budget":600.0,"object_pos_end":[0.49776,0.06107,0.03401],"object_pos_start":[0.49695,0.0612,0.03456],"object_to_goal_dist_end":0.14122,"object_to_goal_dist_start":0.14134,"object_z_max":0.03456,"peak_contact_force":101.93804,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":253.0,"raw_peak_contact_force":101.93804,"tcp_end":[0.49465,0.08418,0.05647],"tcp_start":[0.4936,0.0986,0.1217],"tcp_to_object_dist_end":0.03238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":600.0,"object_pos_end":[0.49544,0.03065,0.04012],"object_pos_start":[0.49776,0.06107,0.03401],"object_to_goal_dist_end":0.11075,"object_to_goal_dist_start":0.14122,"object_z_max":0.04005,"peak_contact_force":0.14481,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":546.0,"raw_peak_contact_force":180.44777,"tcp_end":[0.49109,0.07378,0.04116],"tcp_start":[0.49465,0.08418,0.05647],"tcp_to_object_dist_end":0.04336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":355.0,"n_steps_budget":600.0,"object_pos_end":[0.50612,0.00634,0.02418],"object_pos_start":[0.49544,0.03065,0.04012],"object_to_goal_dist_end":0.08799,"object_to_goal_dist_start":0.11075,"object_z_max":0.0402,"peak_contact_force":9.03618,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":340.0,"raw_peak_contact_force":9.03618,"subtask_id":"contact","tcp_end":[0.49037,0.0532,0.03592],"tcp_start":[0.49109,0.07378,0.04116],"tcp_to_object_dist_end":0.05081,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50433,-0.04747,0.02864],"object_pos_start":[0.50612,0.00634,0.02418],"object_to_goal_dist_end":0.03473,"object_to_goal_dist_start":0.08799,"object_z_max":0.02869,"peak_contact_force":1.04014,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2223.0,"raw_peak_contact_force":10.61052,"subtask_id":"push","tcp_end":[0.49098,-0.01189,0.02805],"tcp_start":[0.49037,0.0532,0.03592],"tcp_to_object_dist_end":0.038,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.49591,-0.04793,0.02424],"object_pos_start":[0.50433,-0.04747,0.02864],"object_to_goal_dist_end":0.03596,"object_to_goal_dist_start":0.03473,"object_z_max":0.02864,"peak_contact_force":0.64406,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":299.0,"raw_peak_contact_force":7.55596,"tcp_end":[0.48889,-0.00498,0.17669],"tcp_start":[0.49098,-0.01189,0.02805],"tcp_to_object_dist_end":0.15855,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.585,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01936,"align_1.lateral_offset_y":-0.00833,"align_2.align_x":-0.0002,"align_2.align_y":-0.01993,"approach_1.approach_height":0.14454,"approach_1.generator.speed":0.14056,"contact_1.contact_force_threshold":2.57758,"contact_1.contact_offset_y":0.00387,"contact_1.generator.speed":0.04914,"descend_1.descend_z":-0.0083,"push_1.generator.speed":0.02527,"push_1.push_depth":0.1797,"push_1.push_time":1.63061,"retract_1.retract_height":0.13137},"optimized_scores":{"best_composite_score":-0.42077,"best_fitness_score":0.26256,"best_task_score":0.19561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":50.0,"contact_point_centroid":[0.47497,0.05832,0.05982],"force_p95":417.95017,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":428.18127,"mean_force":366.88001,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48572,0.0631,0.05832]},{"body_a":"peg","body_b":"channel_base_body","contact_count":935.0,"contact_point_centroid":[0.49495,0.05885,0.00932],"force_p95":39.20404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.80906,"mean_force":7.21983,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4905,0.12314,0.16313]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.49831,0.06141,0.05674],"force_p95":142.20305,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.25701,"mean_force":68.47667,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48644,0.06235,0.05722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.49619,0.05569,0.00932],"force_p95":141.71281,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.07338,"mean_force":13.95384,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49121,0.08663,0.09423]},{"body_a":"attachment","body_b":"peg","contact_count":56.0,"contact_point_centroid":[0.50045,0.07267,0.05594],"force_p95":146.75604,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.56874,"mean_force":96.20559,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49299,0.0811,0.05521]},{"body_a":"peg","body_b":"channel_base_body","contact_count":317.0,"contact_point_centroid":[0.49442,0.0591,0.00932],"force_p95":24.23872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.7395,"mean_force":3.03215,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4894,0.08296,0.10063]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.49878,0.05641,0.05639],"force_p95":53.48645,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.76015,"mean_force":20.31051,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4885,0.06165,0.05642]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52664,-0.02768,0.06],"force_p95":64.23989,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.63046,"mean_force":60.72485,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49076,-0.03423,0.02497]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":137.0,"contact_point_centroid":[0.52592,-0.01873,0.06],"force_p95":19.5646,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.34842,"mean_force":14.18166,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49001,-0.02526,0.02499]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.4931,0.02566,0.04344],"force_p95":14.11291,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.48474,"mean_force":2.52413,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49064,0.03761,0.03169]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50104,-0.04134,0.00887],"force_p95":2.97653,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.73844,"mean_force":1.10466,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48879,-0.00482,0.02546]},{"body_a":"attachment","body_b":"peg","contact_count":532.0,"contact_point_centroid":[0.49478,-0.01551,0.04338],"force_p95":3.22324,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.69097,"mean_force":1.168,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48874,-0.00383,0.02549]},{"body_a":"peg","body_b":"channel_base_body","contact_count":262.0,"contact_point_centroid":[0.49781,0.00542,0.0085],"force_p95":4.10852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.02596,"mean_force":1.1009,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49034,0.0526,0.03191]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52508,-0.02749,0.02782],"force_p95":9.10471,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.12498,"mean_force":4.58262,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49093,0.03147,0.03181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":148.0,"contact_point_centroid":[0.52502,-0.05618,0.02591],"force_p95":5.59522,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.46121,"mean_force":2.53278,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4885,-0.00059,0.02551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49014,-0.10001,0.02559],"force_p95":5.27617,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.27617,"mean_force":5.27617,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49075,-0.03416,0.02497]}],"total_contact_groups":25},"final_pose_error":0.02991,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50025,-0.07051,0.02433],"final_tcp_position":[0.48835,-0.02804,0.12717],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":428.18127,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.4958,0.05603,0.02924],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13652,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":151.80906,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1111.0,"raw_peak_contact_force":428.18127,"tcp_end":[0.48865,0.05868,0.05166],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":317.0,"n_steps_budget":600.0,"object_pos_end":[0.49453,0.05601,0.03423],"object_pos_start":[0.4958,0.05603,0.02924],"object_to_goal_dist_end":0.13625,"object_to_goal_dist_start":0.13652,"object_z_max":0.03607,"peak_contact_force":0.54532,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":361.0,"raw_peak_contact_force":75.7395,"subtask_id":"approach","tcp_end":[0.49233,0.09544,0.15414],"tcp_start":[0.48865,0.05868,0.05166],"tcp_to_object_dist_end":0.12625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":410.0,"n_steps_budget":810.0,"object_pos_end":[0.49546,0.02142,0.03649],"object_pos_start":[0.49453,0.05601,0.03423],"object_to_goal_dist_end":0.10158,"object_to_goal_dist_start":0.13625,"object_z_max":0.04068,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":457.0,"raw_peak_contact_force":149.07338,"tcp_end":[0.49235,0.07788,0.03526],"tcp_start":[0.49233,0.09544,0.15414],"tcp_to_object_dist_end":0.05656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":275.0,"n_steps_budget":600.0,"object_pos_end":[0.50432,-0.00673,0.02805],"object_pos_start":[0.49546,0.02142,0.03649],"object_to_goal_dist_end":0.07436,"object_to_goal_dist_start":0.10158,"object_z_max":0.03649,"peak_contact_force":5.71581,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":355.0,"raw_peak_contact_force":15.48474,"tcp_end":[0.49103,0.02923,0.03186],"tcp_start":[0.49235,0.07788,0.03526],"tcp_to_object_dist_end":0.03853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":21.0,"n_steps_budget":600.0,"object_pos_end":[0.50325,-0.00858,0.0262],"object_pos_start":[0.50432,-0.00673,0.02805],"object_to_goal_dist_end":0.07282,"object_to_goal_dist_start":0.07436,"object_z_max":0.02806,"peak_contact_force":3.21492,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":29.0,"raw_peak_contact_force":3.21492,"subtask_id":"contact","tcp_end":[0.49055,0.02723,0.03022],"tcp_start":[0.49103,0.02923,0.03186],"tcp_to_object_dist_end":0.0382,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50021,-0.07096,0.02563],"object_pos_start":[0.50325,-0.00858,0.0262],"object_to_goal_dist_end":0.01698,"object_to_goal_dist_start":0.07282,"object_z_max":0.02636,"peak_contact_force":14.60828,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1818.0,"raw_peak_contact_force":24.34842,"subtask_id":"push","tcp_end":[0.49076,-0.03422,0.02497],"tcp_start":[0.49055,0.02723,0.03022],"tcp_to_object_dist_end":0.03794,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":196.0,"n_steps_budget":840.0,"object_pos_end":[0.50025,-0.07051,0.02433],"object_pos_start":[0.50021,-0.07096,0.02563],"object_to_goal_dist_end":0.01832,"object_to_goal_dist_start":0.01698,"object_z_max":0.02663,"peak_contact_force":0.57145,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":217.0,"raw_peak_contact_force":64.63046,"tcp_end":[0.48835,-0.02804,0.12717],"tcp_start":[0.49076,-0.03422,0.02497],"tcp_to_object_dist_end":0.1119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47872,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00521,"align_1.lateral_offset_y":0.00564,"align_2.align_x":0.01051,"align_2.align_y":-0.00123,"approach_1.approach_height":0.11089,"approach_1.generator.speed":0.24963,"contact_1.contact_force_threshold":3.7819,"contact_1.contact_offset_y":0.00079,"contact_1.generator.speed":0.02522,"descend_1.descend_z":0.00171,"push_1.generator.speed":0.01779,"push_1.push_depth":0.17999,"push_1.push_time":2.8758,"retract_1.retract_height":0.12135},"optimized_scores":{"best_composite_score":-0.4913,"best_fitness_score":0.19203,"best_task_score":0.15115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.53645,0.09623,0.0598],"force_p95":483.71674,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":519.14046,"mean_force":413.9023,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52459,0.0968,0.06134]},{"body_a":"peg","body_b":"channel_base_body","contact_count":277.0,"contact_point_centroid":[0.50739,0.08068,0.00926],"force_p95":115.61266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.0689,"mean_force":15.63098,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5041,0.11146,0.08357]},{"body_a":"attachment","body_b":"peg","contact_count":45.0,"contact_point_centroid":[0.51139,0.09703,0.05622],"force_p95":148.09941,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.30759,"mean_force":93.29728,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50438,0.10585,0.05608]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.5375,0.09643,0.05995],"force_p95":64.87046,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.56051,"mean_force":52.13312,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52565,0.0967,0.06177]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52511,0.07846,0.03847],"force_p95":11.35758,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.11311,"mean_force":4.41962,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5059,0.10549,0.05297]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49806,0.01439,0.00857],"force_p95":1.48755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.92139,"mean_force":0.83495,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50224,0.05637,0.03067]},{"body_a":"attachment","body_b":"peg","contact_count":427.0,"contact_point_centroid":[0.49938,0.0348,0.03054],"force_p95":1.6346,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.28554,"mean_force":0.80772,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50162,0.04656,0.03006]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":48.0,"contact_point_centroid":[0.47499,-0.00453,0.02538],"force_p95":6.62914,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.11694,"mean_force":3.62613,"phase_index":5.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50282,0.05793,0.03135]},{"body_a":"peg","body_b":"channel_base_body","contact_count":180.0,"contact_point_centroid":[0.50004,-0.01448,0.00817],"force_p95":0.74614,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.86725,"mean_force":0.66557,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4981,0.03026,0.07265]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52502,0.00655,0.02444],"force_p95":4.68936,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.75137,"mean_force":1.45084,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49796,0.02974,0.11746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.49915,0.04454,0.00983],"force_p95":4.86706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.56891,"mean_force":1.52672,"phase_index":4.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5079,0.0923,0.03707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":893.0,"contact_point_centroid":[0.50579,0.08087,0.00937],"force_p95":0.55088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51264,0.14148,0.16316]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47498,-0.03536,0.02557],"force_p95":3.29602,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20894,"mean_force":1.06851,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49994,0.02333,0.02942]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.0145,0.02655],"force_p95":4.16232,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.16232,"mean_force":4.16232,"phase_index":4.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50769,0.09201,0.0368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49987,0.19816,0.29583]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49861,0.01151,0.02953],"force_p95":1.69394,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.70323,"mean_force":1.61032,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50059,0.0233,0.02911]}],"total_contact_groups":19},"final_pose_error":0.02993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5029,-0.01496,0.02452],"final_tcp_position":[0.49802,0.02891,0.12118],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":519.14046,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":414.80568,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1024.0,"raw_peak_contact_force":519.14046,"tcp_end":[0.5256,0.09668,0.06175],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":215.0,"raw_peak_contact_force":65.56051,"subtask_id":"approach","tcp_end":[0.50641,0.11984,0.12496],"tcp_start":[0.5256,0.09668,0.06175],"tcp_to_object_dist_end":0.09917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":277.0,"n_steps_budget":600.0,"object_pos_end":[0.50518,0.06791,0.03951],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.148,"object_to_goal_dist_start":0.1611,"object_z_max":0.03936,"peak_contact_force":0.36106,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":337.0,"raw_peak_contact_force":154.0689,"tcp_end":[0.50451,0.10369,0.0448],"tcp_start":[0.50641,0.11984,0.12496],"tcp_to_object_dist_end":0.03618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.49824,0.03957,0.03156],"object_pos_start":[0.50518,0.06791,0.03951],"object_to_goal_dist_end":0.11988,"object_to_goal_dist_start":0.148,"object_z_max":0.04079,"peak_contact_force":0.28604,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":72.0,"raw_peak_contact_force":0.55945,"tcp_end":[0.50806,0.09266,0.03737],"tcp_start":[0.50451,0.10369,0.0448],"tcp_to_object_dist_end":0.05431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.4973,0.03526,0.02673],"object_pos_start":[0.49824,0.03957,0.03156],"object_to_goal_dist_end":0.11605,"object_to_goal_dist_start":0.11988,"object_z_max":0.03156,"peak_contact_force":5.56891,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":5.56891,"subtask_id":"contact","tcp_end":[0.5076,0.09191,0.0367],"tcp_start":[0.50806,0.09266,0.03737],"tcp_to_object_dist_end":0.05844,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49723,-0.01358,0.02567],"object_pos_start":[0.4973,0.03526,0.02673],"object_to_goal_dist_end":0.06801,"object_to_goal_dist_start":0.11605,"object_z_max":0.02673,"peak_contact_force":0.65366,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1478.0,"raw_peak_contact_force":7.92139,"subtask_id":"push","tcp_end":[0.5006,0.02332,0.02912],"tcp_start":[0.5076,0.09191,0.0367],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":180.0,"n_steps_budget":780.0,"object_pos_end":[0.5029,-0.01496,0.02452],"object_pos_start":[0.49723,-0.01358,0.02567],"object_to_goal_dist_end":0.06692,"object_to_goal_dist_start":0.06801,"object_z_max":0.02567,"peak_contact_force":0.49879,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":193.0,"raw_peak_contact_force":5.86725,"tcp_end":[0.49802,0.02891,0.12118],"tcp_start":[0.5006,0.02332,0.02912],"tcp_to_object_dist_end":0.10626,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```