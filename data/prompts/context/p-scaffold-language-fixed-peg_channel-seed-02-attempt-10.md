## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2463 | 0.22 | ❌ rejected |
| 9 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2805 | 0.30 | ❌ rejected |
| 8 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 13 | -0.4582 | 0.00 | ❌ rejected |
| 7 | align → approach → descend → align → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.4169 | 0.26 | ❌ rejected |
| 6 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4315 | 0.09 | ❌ rejected |

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

## Current Skill (Q=-0.246) — your mutation base

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

- **Composite score**: -0.246
- **task_score** (E): 0.216
- **fitness_score**: 0.174  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1559 |
| descend_1 | 1.00 | 1.00 | 0.1317 |
| align_1 | 1.00 | 1.00 | 0.0193 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.119, 0.172) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.544 | 3.659 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.119, 0.172)→(0.495, 0.108, 0.043) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 113.263 |
| align_1 | align | 1.00 / step_budget | (0.495, 0.108, 0.043)→(0.506, 0.097, 0.050) | (0.498, 0.068, 0.034)→(0.497, -0.011, 0.035) | 0.148→0.070 | 1.00 / 2.667 | 207.445 | 2843.132 |
| contact_1 | contact | 1.00 / force_exceeded | (0.506, 0.097, 0.050)→(0.506, 0.097, 0.050) | (0.497, -0.011, 0.035)→(0.497, -0.011, 0.035) | 0.070→0.070 | 1.00 / 2.667 | 78.226 | 79.936 |
| push_1 | push | 0.00 / guard_failure | (0.506, 0.097, 0.050)→(0.506, 0.097, 0.050) | (0.497, -0.011, 0.035)→(0.497, -0.011, 0.035) | 0.070→0.070 | 1.00 / 2.667 | 80.970 | 80.970 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.614
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.375
- phase_score: 0.152
- phase_breakdown.approach_score: 0.046
- phase_breakdown.push_score: 0.030
- phase_breakdown.contact_score: 0.624

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.241
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.375
- **Median Q (composite search score)**: -0.245
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00745,"align_1.lateral_offset_y":-0.00824,"approach_1.approach_height":0.13612,"approach_1.approach_speed":0.098,"contact_1.contact_force_threshold":3.24571,"contact_1.contact_speed":0.02854,"descend_1.descend_z":-0.00516,"push_1.push_depth":0.10697,"push_1.push_speed":0.03079,"retract_1.retract_height":0.14553},"optimized_scores":{"best_composite_score":-0.17863,"best_fitness_score":0.24137,"best_task_score":0.37525},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.53305,0.11715,0.05904],"force_p95":3326.37621,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4253.76002,"mean_force":1020.69871,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50153,0.09201,0.02936]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52621,0.09011,0.05949],"force_p95":3318.84196,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3999.85007,"mean_force":1504.04854,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50987,0.08299,0.02391]},{"body_a":"world","body_b":"link7","contact_count":334.0,"contact_point_centroid":[0.498,0.16002,-0.00011],"force_p95":354.81537,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":605.63942,"mean_force":303.17162,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49743,0.09721,0.0473]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47479,0.09837,0.02815],"force_p95":268.82931,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.77743,"mean_force":176.29923,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48637,0.0963,0.02719]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49832,0.15608,-3e-05],"force_p95":89.94602,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.32969,"mean_force":76.35986,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4993,0.09485,0.04986]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.49831,0.15604,-3e-05],"force_p95":86.05724,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.05724,"mean_force":86.05724,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49929,0.09482,0.04988]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50031,0.07889,0.02839],"force_p95":28.33178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.47337,"mean_force":19.18178,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5032,0.09002,0.02705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.49602,-0.02565,0.00943],"force_p95":1.21848,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.88589,"mean_force":0.76149,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49728,0.09708,0.04389]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.49592,0.0641,0.00934],"force_p95":0.68755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57942,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48827,0.14799,0.24738]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":26.0,"contact_point_centroid":[0.47481,-0.03497,0.05915],"force_p95":0.84151,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.34505,"mean_force":0.29221,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49653,0.0978,0.04529]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49876,0.19622,0.29708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":512.0,"contact_point_centroid":[0.49509,0.0639,0.0094],"force_p95":0.55038,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54568,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48435,0.10799,0.11509]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49742,-0.05145,0.00946],"force_p95":0.54533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54533,"mean_force":0.54533,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49929,0.09482,0.04988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50254,-0.05008,0.00947],"force_p95":0.54436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54446,"mean_force":0.54246,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4993,0.09485,0.04986]}],"total_contact_groups":14},"final_pose_error":0.23673,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49579,-0.03443,0.03456],"final_tcp_position":[0.49928,0.09481,0.04989],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":4253.76002,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.49494,0.06393,0.0339],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14415,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54476,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":277.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.48075,0.11252,0.19393],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.49485,0.06393,0.03398],"object_pos_start":[0.49494,0.06393,0.0339],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14415,"object_z_max":0.03398,"peak_contact_force":0.54683,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":512.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49012,0.10385,0.03737],"tcp_start":[0.48075,0.11252,0.19393],"tcp_to_object_dist_end":0.04035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.4963,-0.03431,0.03456],"object_pos_start":[0.49485,0.06393,0.03398],"object_to_goal_dist_end":0.04617,"object_to_goal_dist_start":0.14414,"object_z_max":0.04056,"peak_contact_force":274.09494,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":875.0,"raw_peak_contact_force":4253.76002,"tcp_end":[0.49931,0.09487,0.04984],"tcp_start":[0.49012,0.10385,0.03737],"tcp_to_object_dist_end":0.13011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49618,-0.03436,0.03456],"object_pos_start":[0.4963,-0.03431,0.03456],"object_to_goal_dist_end":0.04612,"object_to_goal_dist_start":0.04617,"object_z_max":0.03456,"peak_contact_force":86.49305,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":90.32969,"subtask_id":"contact","tcp_end":[0.49929,0.09482,0.04988],"tcp_start":[0.49929,0.09483,0.04988],"tcp_to_object_dist_end":0.13013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49579,-0.03443,0.03456],"object_pos_start":[0.49592,-0.03442,0.03456],"object_to_goal_dist_end":0.04609,"object_to_goal_dist_start":0.04608,"object_z_max":0.03456,"peak_contact_force":86.05724,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":86.05724,"subtask_id":"push","tcp_end":[0.49928,0.09481,0.04989],"tcp_start":[0.49929,0.09482,0.04988],"tcp_to_object_dist_end":0.13019,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7561,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0025,"align_1.lateral_offset_y":0.00337,"approach_1.approach_height":0.13226,"approach_1.approach_speed":0.15025,"contact_1.contact_force_threshold":5.77805,"contact_1.contact_speed":0.05094,"descend_1.descend_z":-0.00157,"push_1.push_depth":0.12515,"push_1.push_speed":0.03563,"retract_1.retract_height":0.15617},"optimized_scores":{"best_composite_score":-0.2451,"best_fitness_score":0.1749,"best_task_score":0.26228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.53355,0.11623,0.05945],"force_p95":2275.65348,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2810.05943,"mean_force":703.85694,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50166,0.08627,0.03564]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52598,0.08445,0.05984],"force_p95":2431.06317,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2544.15197,"mean_force":1244.73471,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50919,0.07655,0.02549]},{"body_a":"world","body_b":"link7","contact_count":206.0,"contact_point_centroid":[0.50189,0.15458,-0.00015],"force_p95":385.05703,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":504.62933,"mean_force":354.78869,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50144,0.09181,0.04745]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.4748,0.09834,0.05889],"force_p95":314.20386,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.68456,"mean_force":118.93738,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4861,0.1,0.05713]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50393,0.1531,-9e-05],"force_p95":60.96511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.96511,"mean_force":60.96511,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50431,0.09244,0.05043]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50391,0.1531,-9e-05],"force_p95":57.60554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.01419,"mean_force":53.07848,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50429,0.09243,0.05044]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49918,0.07401,0.03179],"force_p95":31.23669,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.47673,"mean_force":22.61588,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5019,0.08519,0.03049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.49402,-0.04295,0.00972],"force_p95":2.29144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.27557,"mean_force":0.9536,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50124,0.09092,0.0445]},{"body_a":"peg","body_b":"channel_base_body","contact_count":251.0,"contact_point_centroid":[0.49478,0.05909,0.00931],"force_p95":0.67255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60444,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48068,0.14489,0.24523]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49771,0.19459,0.29581]},{"body_a":"peg","body_b":"channel_base_body","contact_count":220.0,"contact_point_centroid":[0.49393,-0.10011,0.03332],"force_p95":1.21357,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90701,"mean_force":0.33299,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50115,0.09169,0.04695]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47497,-0.04578,0.04603],"force_p95":2.20017,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.37559,"mean_force":1.35926,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49981,0.08734,0.03814]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.49417,0.05892,0.00939],"force_p95":0.55032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54619,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47717,0.10319,0.11425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49381,-0.05564,0.00999],"force_p95":0.40859,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4086,"mean_force":0.40845,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50429,0.09243,0.05044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49381,-0.05564,0.00999],"force_p95":0.40814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40814,"mean_force":0.40814,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50431,0.09244,0.05043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49398,-0.1,0.03307],"force_p95":0.14579,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14579,"mean_force":0.14573,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50429,0.09243,0.05044]}],"total_contact_groups":17},"final_pose_error":0.28758,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49423,-0.06952,0.03748],"final_tcp_position":[0.50432,0.09244,0.05043],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":2810.05943,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":280.0,"n_steps_budget":720.0,"object_pos_end":[0.49404,0.059,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.544,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":286.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46807,0.1078,0.18996],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.0591,0.0339],"object_pos_start":[0.49404,0.059,0.03384],"object_to_goal_dist_end":0.13936,"object_to_goal_dist_start":0.13926,"object_z_max":0.0339,"peak_contact_force":0.54444,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":527.0,"raw_peak_contact_force":338.68456,"tcp_end":[0.48878,0.09902,0.04063],"tcp_start":[0.46807,0.1078,0.18996],"tcp_to_object_dist_end":0.04083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.49423,-0.06952,0.03748],"object_pos_start":[0.49407,0.0591,0.0339],"object_to_goal_dist_end":0.01223,"object_to_goal_dist_start":0.13936,"object_z_max":0.04033,"peak_contact_force":348.24006,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":816.0,"raw_peak_contact_force":2810.05943,"tcp_end":[0.50428,0.09243,0.05044],"tcp_start":[0.48878,0.09902,0.04063],"tcp_to_object_dist_end":0.16277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,-0.06952,0.03748],"object_pos_start":[0.49423,-0.06952,0.03748],"object_to_goal_dist_end":0.01223,"object_to_goal_dist_start":0.01223,"object_z_max":0.03748,"peak_contact_force":58.01419,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":58.01419,"subtask_id":"contact","tcp_end":[0.50431,0.09244,0.05043],"tcp_start":[0.5043,0.09243,0.05044],"tcp_to_object_dist_end":0.16278,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,-0.06952,0.03748],"object_pos_start":[0.49423,-0.06952,0.03748],"object_to_goal_dist_end":0.01223,"object_to_goal_dist_start":0.01223,"object_z_max":0.03748,"peak_contact_force":60.96511,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":60.96511,"subtask_id":"push","tcp_end":[0.50432,0.09244,0.05043],"tcp_start":[0.50431,0.09244,0.05043],"tcp_to_object_dist_end":0.16279,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93939,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00178,"align_1.lateral_offset_y":-0.01654,"approach_1.approach_height":0.08028,"approach_1.approach_speed":0.2792,"contact_1.contact_force_threshold":2.62425,"contact_1.contact_speed":0.06956,"descend_1.descend_z":0.00626,"push_1.push_depth":0.11871,"push_1.push_speed":0.03178,"retract_1.retract_height":0.11588},"optimized_scores":{"best_composite_score":-0.31509,"best_fitness_score":0.10491,"best_task_score":0.01183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52607,0.11337,0.05981],"force_p95":1350.07096,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1465.57696,"mean_force":747.19766,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51184,0.11094,0.04324]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53776,0.11939,0.05939],"force_p95":756.93501,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":788.58615,"mean_force":438.04315,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49699,0.10545,0.02689]},{"body_a":"world","body_b":"link7","contact_count":285.0,"contact_point_centroid":[0.50651,0.1659,-0.00016],"force_p95":402.6037,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":591.89644,"mean_force":368.0122,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50798,0.10237,0.04762]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51088,0.16319,-9e-05],"force_p95":95.88674,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.88674,"mean_force":95.88674,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.103,0.05096]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.51087,0.16321,-9e-05],"force_p95":91.27006,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.46395,"mean_force":82.87666,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51301,0.103,0.05094]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.10345,0.05098],"force_p95":35.19908,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.19908,"mean_force":35.19908,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.103,0.05096]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.525,0.10346,0.05096],"force_p95":30.01903,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.61179,"mean_force":25.78478,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51302,0.103,0.05094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49844,0.07121,0.00947],"force_p95":0.89892,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.59806,"mean_force":0.62699,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50685,0.10359,0.04506]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50491,0.09615,0.03865],"force_p95":6.41964,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.20583,"mean_force":2.21905,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50293,0.10451,0.03234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50547,0.08095,0.00934],"force_p95":0.58712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59849,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51586,0.17484,0.20542]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50117,0.19919,0.29237]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47459,0.06484,0.05891],"force_p95":0.9282,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08346,"mean_force":0.25608,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50064,0.09867,0.0383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50598,0.08073,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51724,0.12863,0.0913]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51225,0.05966,0.00942],"force_p95":0.54286,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54286,"mean_force":0.54286,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.103,0.05096]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50346,0.05538,0.00942],"force_p95":0.542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54201,"mean_force":0.54042,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51301,0.103,0.05094]}],"total_contact_groups":15},"final_pose_error":0.15114,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49984,0.07217,0.03412],"final_tcp_position":[0.51303,0.103,0.05096],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1465.57696,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54473,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":331.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52921,0.13529,0.13263],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":249.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54641,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":249.0,"raw_peak_contact_force":0.55023,"tcp_end":[0.5061,0.12228,0.04976],"tcp_start":[0.52921,0.13529,0.13263],"tcp_to_object_dist_end":0.04437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":376.0,"n_steps_budget":600.0,"object_pos_end":[0.49948,0.07198,0.03412],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.15209,"object_to_goal_dist_start":0.16112,"object_z_max":0.03797,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":723.0,"raw_peak_contact_force":1465.57696,"tcp_end":[0.51301,0.10302,0.05091],"tcp_start":[0.5061,0.12228,0.04976],"tcp_to_object_dist_end":0.0378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.49964,0.072,0.03412],"object_pos_start":[0.49948,0.07198,0.03412],"object_to_goal_dist_end":0.15212,"object_to_goal_dist_start":0.15209,"object_z_max":0.03412,"peak_contact_force":90.17135,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11.0,"raw_peak_contact_force":91.46395,"subtask_id":"contact","tcp_end":[0.51303,0.103,0.05096],"tcp_start":[0.51302,0.103,0.05095],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49984,0.07217,0.03412],"object_pos_start":[0.49979,0.0721,0.03412],"object_to_goal_dist_end":0.15228,"object_to_goal_dist_start":0.15221,"object_z_max":0.03412,"peak_contact_force":95.88674,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":95.88674,"subtask_id":"push","tcp_end":[0.51303,0.103,0.05096],"tcp_start":[0.51303,0.103,0.05096],"tcp_to_object_dist_end":0.03753,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```