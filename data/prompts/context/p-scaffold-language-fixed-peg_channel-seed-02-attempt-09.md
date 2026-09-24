## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2805 | 0.30 | ❌ rejected |
| 8 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 13 | -0.4582 | 0.00 | ❌ rejected |
| 7 | align → approach → descend → align → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 14 | -0.4169 | 0.26 | ❌ rejected |
| 6 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4315 | 0.09 | ❌ rejected |
| 5 | approach → approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.4994 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.280) — your mutation base

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

- **Composite score**: -0.280
- **task_score** (E): 0.301
- **fitness_score**: 0.278  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1415 |
| descend_1 | 1.00 | 1.00 | 0.1491 |
| lateral_align | 1.00 | 1.00 | 0.0218 |
| contact_1 | 0.67 | 1.00 | 0.0064 |
| push_1 | 0.67 | 1.00 | 0.0736 |
| retract_1 | 1.00 | 1.00 | 0.1150 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.116, 0.190) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.116, 0.190)→(0.495, 0.108, 0.043) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.546 | 81.810 |
| lateral_align | align | 1.00 / step_budget | (0.495, 0.108, 0.043)→(0.505, 0.093, 0.032) | (0.498, 0.068, 0.034)→(0.501, 0.063, 0.034) | 0.148→0.143 | 1.00 / 2.000 | 226.481 | 282.480 |
| contact_1 | contact | 0.67 / force_exceeded | (0.505, 0.093, 0.032)→(0.503, 0.087, 0.031) | (0.501, 0.063, 0.034)→(0.499, 0.056, 0.034) | 0.143→0.137 | 1.00 / 2.000 | 6.710 | 7.318 |
| push_1 | push | 0.67 / step_budget | (0.503, 0.066, 0.030)→(0.502, -0.007, 0.027) | (0.499, 0.056, 0.034)→(0.495, -0.035, 0.041) | 0.137→0.046 | 1.00 / 1.333 | 0.144 | 66.944 |
| retract_1 | retract | 1.00 / step_budget | (0.502, -0.007, 0.027)→(0.499, -0.001, 0.142) | (0.495, -0.035, 0.041)→(0.499, -0.064, 0.033) | 0.046→0.020 | 1.00 / 1.667 | 0.549 | 31.683 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.827
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.409
- phase_score: 0.355
- phase_breakdown.approach_score: 0.041
- phase_breakdown.push_score: 0.388
- phase_breakdown.contact_score: 0.571

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.377
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.409
- **Median Q (composite search score)**: -0.273
- **K-run variance**: 0.0166
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87246,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14118,"approach_1.generator.speed":0.05015,"contact_1.contact_force_threshold":4.78648,"contact_1.generator.speed":0.04713,"descend_1.descend_speed":0.02454,"lateral_align.lateral_offset_x":0.02609,"lateral_align.lateral_offset_y":-0.00484,"push_1.generator.speed":0.03086,"push_1.push_depth":0.1689,"push_1.push_force_threshold":32.10632,"retract_1.retract_height":0.14473},"optimized_scores":{"best_composite_score":-0.12647,"best_fitness_score":0.37686,"best_task_score":0.40922},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52515,0.08493,0.05998],"force_p95":371.83224,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.82501,"mean_force":284.00755,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50823,0.08501,0.03135]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":212.0,"contact_point_centroid":[0.47484,-0.06214,0.05738],"force_p95":17.06439,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.71331,"mean_force":3.17409,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50334,-0.02642,0.08512]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50301,-0.04683,0.06152],"force_p95":27.20735,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.98948,"mean_force":6.54209,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50426,-0.03785,0.0292]},{"body_a":"attachment","body_b":"peg","contact_count":96.0,"contact_point_centroid":[0.50115,0.02636,0.02887],"force_p95":14.67193,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.55294,"mean_force":4.08073,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50584,0.03727,0.02796]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.08486,0.05999],"force_p95":24.82339,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.32645,"mean_force":21.19781,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5074,0.08487,0.03097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.49401,0.01598,0.00976],"force_p95":9.04471,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.55444,"mean_force":3.49986,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50606,0.04447,0.0284]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":198.0,"contact_point_centroid":[0.52516,-0.0746,0.02406],"force_p95":17.03997,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.55747,"mean_force":3.09412,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5032,-0.02544,0.08959]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":73.0,"contact_point_centroid":[0.47476,-0.00616,0.03984],"force_p95":12.21258,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.26442,"mean_force":3.16599,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50567,0.02045,0.02722]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.08487,0.05999],"force_p95":9.54745,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.54745,"mean_force":9.54745,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50745,0.08488,0.03106]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50725,-0.06705,0.06994],"force_p95":5.21396,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.95419,"mean_force":2.17368,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50404,-0.03793,0.02944]},{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.49687,-0.06529,0.00999],"force_p95":2.43102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.10102,"mean_force":0.60905,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50319,-0.02434,0.10209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.49667,0.05664,0.00959],"force_p95":1.55439,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.93016,"mean_force":0.67402,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50165,0.09134,0.03434]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.49562,0.06379,0.00934],"force_p95":0.6859,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57835,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48837,0.14899,0.25042]},{"body_a":"attachment","body_b":"peg","contact_count":76.0,"contact_point_centroid":[0.50178,0.07647,0.03311],"force_p95":1.67096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.33176,"mean_force":0.7685,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50525,0.08785,0.03258]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49884,0.19688,0.29761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":581.0,"contact_point_centroid":[0.49506,0.0639,0.0094],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54564,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48443,0.10814,0.12023]}],"total_contact_groups":17},"final_pose_error":0.02977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5,-0.06847,0.04043],"final_tcp_position":[0.50342,-0.02857,0.14238],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":384.82501,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.49522,0.06376,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54515,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":285.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.48081,0.11294,0.19891],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17278,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49522,0.06376,0.03391],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14397,"object_z_max":0.034,"peak_contact_force":0.5415,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":581.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49043,0.10374,0.04248],"tcp_start":[0.48081,0.11294,0.19891],"tcp_to_object_dist_end":0.04127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.49678,0.05679,0.034],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.13696,"object_to_goal_dist_start":0.14384,"object_z_max":0.03481,"peak_contact_force":302.7956,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":432.0,"raw_peak_contact_force":384.82501,"subtask_id":"contact","tcp_end":[0.50745,0.08488,0.03106],"tcp_start":[0.49043,0.10374,0.04248],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49679,0.05683,0.03398],"object_pos_start":[0.49678,0.05679,0.034],"object_to_goal_dist_end":0.137,"object_to_goal_dist_start":0.13696,"object_z_max":0.034,"peak_contact_force":9.54745,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":9.54745,"tcp_end":[0.50746,0.08488,0.03104],"tcp_start":[0.50745,0.08488,0.03106],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.4928,-0.06116,0.03914],"object_pos_start":[0.49679,0.05683,0.03398],"object_to_goal_dist_end":0.02018,"object_to_goal_dist_start":0.137,"object_z_max":0.03896,"peak_contact_force":0.38835,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":238.0,"raw_peak_contact_force":26.55294,"subtask_id":"push","tcp_end":[0.50591,-0.03498,0.02661],"tcp_start":[0.50746,0.08488,0.03104],"tcp_to_object_dist_end":0.03185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":228.0,"n_steps_budget":900.0,"object_pos_end":[0.5,-0.06847,0.04043],"object_pos_start":[0.4928,-0.06116,0.03914],"object_to_goal_dist_end":0.01154,"object_to_goal_dist_start":0.02018,"object_z_max":0.04388,"peak_contact_force":0.45923,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":577.0,"raw_peak_contact_force":36.71331,"tcp_end":[0.50342,-0.02857,0.14238],"tcp_start":[0.50591,-0.03498,0.02661],"tcp_to_object_dist_end":0.10953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1039,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13775,"approach_1.generator.speed":0.13079,"contact_1.contact_force_threshold":5.01433,"contact_1.generator.speed":0.02939,"descend_1.descend_speed":0.07229,"lateral_align.lateral_offset_x":0.01648,"lateral_align.lateral_offset_y":-0.00351,"push_1.generator.speed":0.02645,"push_1.push_depth":0.13448,"push_1.push_force_threshold":28.95726,"retract_1.retract_height":0.14481},"optimized_scores":{"best_composite_score":-0.44195,"best_fitness_score":0.22805,"best_task_score":0.22701},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47488,0.09868,0.05913],"force_p95":226.17794,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.32683,"mean_force":92.50788,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4864,0.09999,0.05738]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53082,0.0072,0.06],"force_p95":146.68999,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.68999,"mean_force":146.68999,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49426,0.0007,0.02567]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53085,0.00391,0.05997],"force_p95":53.0292,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.0996,"mean_force":52.39564,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49427,-0.00251,0.02562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":55.0,"contact_point_centroid":[0.49488,0.01112,0.00986],"force_p95":5.68701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.31189,"mean_force":2.39695,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49476,0.04454,0.02755]},{"body_a":"attachment","body_b":"peg","contact_count":72.0,"contact_point_centroid":[0.49471,0.02691,0.03245],"force_p95":5.04323,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.1848,"mean_force":1.82773,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49445,0.03879,0.02703]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47491,0.00674,0.03222],"force_p95":3.09155,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20811,"mean_force":1.21246,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49412,0.0369,0.02664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.49484,0.05896,0.00931],"force_p95":0.67373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60492,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48084,0.14537,0.2479]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49772,0.19456,0.29595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.49458,0.054,0.00955],"force_p95":1.96841,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.41754,"mean_force":0.78477,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49465,0.08919,0.03532]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.49768,0.07243,0.03338],"force_p95":2.05167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.86713,"mean_force":1.03801,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.49826,0.08431,0.03283]},{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.49533,0.03019,0.00987],"force_p95":1.09679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32652,"mean_force":0.69665,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49748,0.06926,0.02868]},{"body_a":"attachment","body_b":"peg","contact_count":362.0,"contact_point_centroid":[0.49682,0.05683,0.02871],"force_p95":0.74669,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.14081,"mean_force":0.42982,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49733,0.0688,0.02865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.49462,-0.05062,0.00944],"force_p95":0.92548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76834,"mean_force":0.56537,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49185,0.00752,0.08604]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47488,-0.04572,0.0553],"force_p95":0.55725,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66441,"mean_force":0.23228,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49209,0.00655,0.06724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":540.0,"contact_point_centroid":[0.49401,0.05904,0.00939],"force_p95":0.55031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54618,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47725,0.10343,0.11768]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49764,-0.01415,0.06036],"force_p95":0.24817,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27448,"mean_force":0.11419,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49391,-0.00305,0.02609]}],"total_contact_groups":16},"final_pose_error":0.02968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49361,-0.04884,0.03401],"final_tcp_position":[0.49195,0.00459,0.14157],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":244.32683,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":278.0,"n_steps_budget":780.0,"object_pos_end":[0.4941,0.05905,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13931,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54908,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":284.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46823,0.10821,0.19509],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.494,0.05886,0.0339],"object_pos_start":[0.4941,0.05905,0.03384],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13931,"object_z_max":0.0339,"peak_contact_force":0.55097,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":549.0,"raw_peak_contact_force":244.32683,"tcp_end":[0.48882,0.09908,0.04207],"tcp_start":[0.46823,0.10821,0.19509],"tcp_to_object_dist_end":0.04136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":163.0,"n_steps_budget":600.0,"object_pos_end":[0.49986,0.05011,0.03454],"object_pos_start":[0.494,0.05886,0.0339],"object_to_goal_dist_end":0.13022,"object_to_goal_dist_start":0.13913,"object_z_max":0.03486,"peak_contact_force":0.58898,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":216.0,"raw_peak_contact_force":3.41754,"subtask_id":"contact","tcp_end":[0.50212,0.0798,0.031],"tcp_start":[0.48882,0.09908,0.04207],"tcp_to_object_dist_end":0.02999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":412.0,"n_steps_budget":600.0,"object_pos_end":[0.49528,0.03169,0.035],"object_pos_start":[0.49986,0.05011,0.03454],"object_to_goal_dist_end":0.11191,"object_to_goal_dist_start":0.13022,"object_z_max":0.03503,"peak_contact_force":0.5044,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":769.0,"raw_peak_contact_force":2.32652,"tcp_end":[0.49612,0.06167,0.02951],"tcp_start":[0.50212,0.0798,0.031],"tcp_to_object_dist_end":0.03049,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.49392,-0.02898,0.03627],"object_pos_start":[0.49528,0.03169,0.035],"object_to_goal_dist_end":0.05152,"object_to_goal_dist_start":0.11191,"object_z_max":0.0367,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":160.0,"raw_peak_contact_force":146.68999,"subtask_id":"push","tcp_end":[0.49432,-0.0017,0.02567],"tcp_start":[0.49433,-0.001,0.0257],"tcp_to_object_dist_end":0.02927,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":224.0,"n_steps_budget":900.0,"object_pos_end":[0.49361,-0.04884,0.03401],"object_pos_start":[0.49384,-0.03019,0.03709],"object_to_goal_dist_end":0.03237,"object_to_goal_dist_start":0.05027,"object_z_max":0.03896,"peak_contact_force":0.52685,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":250.0,"raw_peak_contact_force":53.0996,"tcp_end":[0.49195,0.00459,0.14157],"tcp_start":[0.49432,-0.0017,0.02567],"tcp_to_object_dist_end":0.12011,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42105,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11814,"approach_1.generator.speed":0.19928,"contact_1.contact_force_threshold":1.19191,"contact_1.generator.speed":0.03353,"descend_1.descend_speed":0.10961,"lateral_align.lateral_offset_x":0.01861,"lateral_align.lateral_offset_y":0.00819,"push_1.generator.speed":0.04266,"push_1.push_depth":0.14973,"push_1.push_force_threshold":31.02266,"retract_1.retract_height":0.1417},"optimized_scores":{"best_composite_score":-0.27302,"best_fitness_score":0.23031,"best_task_score":0.26777},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":178.0,"contact_point_centroid":[0.5251,0.11546,0.05998],"force_p95":426.85716,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":459.19788,"mean_force":361.97731,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50814,0.11535,0.03481]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52503,0.11547,0.05999],"force_p95":25.08702,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.58781,"mean_force":11.60167,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50677,0.11515,0.03332]},{"body_a":"peg","body_b":"channel_base_body","contact_count":61.0,"contact_point_centroid":[0.50364,0.05365,0.00946],"force_p95":14.04442,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.99831,"mean_force":3.38275,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50546,0.08751,0.03112]},{"body_a":"attachment","body_b":"peg","contact_count":68.0,"contact_point_centroid":[0.50689,0.05454,0.04086],"force_p95":11.19573,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.83347,"mean_force":2.97603,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5051,0.06565,0.03008]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52511,0.01723,0.03335],"force_p95":6.9813,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.30352,"mean_force":1.79205,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50507,0.04756,0.02942]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.11548,0.05999],"force_p95":10.07876,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10.07876,"mean_force":10.07876,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50685,0.11517,0.03343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":171.0,"contact_point_centroid":[0.4987,-0.05482,0.0097],"force_p95":2.4014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.23712,"mean_force":0.7025,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50238,0.02397,0.09022]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52515,-0.08502,0.03447],"force_p95":4.77158,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.86308,"mean_force":1.14466,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50255,0.02164,0.10966]},{"body_a":"peg","body_b":"channel_base_body","contact_count":244.0,"contact_point_centroid":[0.50537,0.08082,0.00933],"force_p95":0.63801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.6093,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51851,0.15455,0.23734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50172,0.19511,0.29485]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":40.0,"contact_point_centroid":[0.47452,-0.04084,0.03149],"force_p95":2.32628,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42158,"mean_force":0.72593,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50301,0.01814,0.05017]},{"body_a":"peg","body_b":"channel_base_body","contact_count":49.0,"contact_point_centroid":[0.4929,-0.10013,0.02013],"force_p95":1.11284,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65906,"mean_force":0.46318,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50231,0.02637,0.10751]},{"body_a":"peg","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52325,-0.00822,0.06695],"force_p95":0.55548,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62447,"mean_force":0.20151,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,0.02057,0.02901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55048,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51687,0.12326,0.10957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":236.0,"contact_point_centroid":[0.50591,0.08098,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54678,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50768,0.1161,0.03596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52106,0.09068,0.00938],"force_p95":0.54458,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54458,"mean_force":0.54458,"phase_index":3.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50685,0.11517,0.03343]}],"total_contact_groups":18},"final_pose_error":0.02974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5048,-0.07352,0.02558],"final_tcp_position":[0.50255,0.02116,0.14166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":459.19788,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54702,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":280.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.53042,0.12646,0.17661],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":840.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.5464,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":390.0,"raw_peak_contact_force":0.55048,"tcp_end":[0.5048,0.12058,0.0435],"tcp_start":[0.53042,0.12646,0.17661],"tcp_to_object_dist_end":0.04088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":236.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":376.05725,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":414.0,"raw_peak_contact_force":459.19788,"subtask_id":"contact","tcp_end":[0.50685,0.11517,0.03343],"tcp_start":[0.5048,0.12058,0.0435],"tcp_to_object_dist_end":0.03429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":10.07876,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":10.07876,"tcp_end":[0.50685,0.11517,0.0334],"tcp_start":[0.50685,0.11517,0.03343],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.49946,-0.01371,0.04644],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.0666,"object_to_goal_dist_start":0.1611,"object_z_max":0.04634,"peak_contact_force":0.04405,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":166.0,"raw_peak_contact_force":27.58781,"subtask_id":"push","tcp_end":[0.50508,0.01507,0.02896],"tcp_start":[0.50685,0.11517,0.0334],"tcp_to_object_dist_end":0.03414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":223.0,"n_steps_budget":900.0,"object_pos_end":[0.5048,-0.07352,0.02558],"object_pos_start":[0.49946,-0.01371,0.04644],"object_to_goal_dist_end":0.01652,"object_to_goal_dist_start":0.0666,"object_z_max":0.04647,"peak_contact_force":0.66134,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":288.0,"raw_peak_contact_force":5.23712,"tcp_end":[0.50255,0.02116,0.14166],"tcp_start":[0.50508,0.01507,0.02896],"tcp_to_object_dist_end":0.14981,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```