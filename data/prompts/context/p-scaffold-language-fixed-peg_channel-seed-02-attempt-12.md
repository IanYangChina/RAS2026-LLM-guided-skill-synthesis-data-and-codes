## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0063 | 0.30 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1405 | 0.11 | ❌ rejected |
| 10 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2463 | 0.22 | ❌ rejected |
| 9 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2805 | 0.30 | ❌ rejected |
| 8 | approach → descend → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 13 | -0.4582 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.006) — your mutation base

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

- **Composite score**: -0.006
- **task_score** (E): 0.297
- **fitness_score**: 0.350  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.233
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1762 |
| descend_1 | 1.00 | 0.00 | 0.1125 |
| contact_1 | 1.00 | 1.00 | 0.0091 |
| push_1 | 0.33 | 1.00 | 0.0777 |
| retract_1 | 1.00 | 1.00 | 0.1384 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.113, 0.150) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 3.659 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.113, 0.150)→(0.496, 0.093, 0.042) | (0.498, 0.068, 0.034)→(0.501, 0.058, 0.038) | 0.148→0.138 | 0.00 / 0.000 | 0.000 | 167.191 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.075, 0.033)→(0.494, 0.067, 0.032) | (0.501, 0.058, 0.038)→(0.497, 0.047, 0.032) | 0.138→0.128 | 1.00 / 2.333 | 1324.789 | 8.214 |
| push_1 | push | 0.33 / guard_failure | (0.494, 0.067, 0.032)→(0.495, -0.011, 0.028) | (0.502, 0.026, 0.032)→(0.505, -0.042, 0.034) | 0.107→0.040 | 1.00 / 2.333 | 29.367 | 40.392 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.042, 0.030)→(0.498, -0.035, 0.168) | (0.503, -0.071, 0.037)→(0.500, -0.081, 0.034) | 0.010→0.006 | 1.00 / 1.000 | 0.545 | 1.673 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.304
- phase_score: 0.444
- phase_breakdown.approach_score: 0.116
- phase_breakdown.push_score: 0.585
- phase_breakdown.contact_score: 0.351

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.426
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.457
- **Median Q (composite search score)**: 0.036
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.252


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18421,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10575,"approach_1.generator.speed":0.17484,"contact_1.contact_force_threshold":4.68238,"contact_1.generator.speed":0.03089,"descend_1.descend_lateral_y":0.02633,"descend_1.descend_z":0.00043,"descend_1.generator.speed":0.05545,"push_1.generator.speed":0.03205,"push_1.push_depth":0.10373,"retract_1.retract_height":0.16692},"optimized_scores":{"best_composite_score":0.03564,"best_fitness_score":0.42564,"best_task_score":0.45654},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":126.0,"contact_point_centroid":[0.50072,0.00674,0.03908],"force_p95":17.4986,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.42398,"mean_force":4.18751,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49467,0.01764,0.02823]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.52516,-0.00925,0.03249],"force_p95":11.39725,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.03555,"mean_force":2.86501,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49455,0.01851,0.02815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":68.0,"contact_point_centroid":[0.50601,-0.03034,0.00982],"force_p95":15.73055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.60225,"mean_force":4.46947,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49517,0.01359,0.02847]},{"body_a":"peg","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52109,-0.02581,0.06463],"force_p95":9.82383,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.88758,"mean_force":9.00379,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49649,-0.00459,0.02838]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.49523,0.06212,0.00941],"force_p95":0.55102,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.53519,"mean_force":0.64366,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48381,0.10063,0.10313]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.49192,0.08074,0.05496],"force_p95":7.72166,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.11762,"mean_force":4.54972,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48915,0.09254,0.05021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":604.0,"contact_point_centroid":[0.50282,0.03037,0.00996],"force_p95":4.95006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.43219,"mean_force":2.62922,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48925,0.07454,0.03274]},{"body_a":"attachment","body_b":"peg","contact_count":590.0,"contact_point_centroid":[0.49523,0.06262,0.04539],"force_p95":4.62711,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.93887,"mean_force":2.31771,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48927,0.07401,0.03248]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52501,0.03204,0.06],"force_p95":2.94951,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9705,"mean_force":1.88489,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.492,0.06076,0.02907]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.49559,0.06401,0.00934],"force_p95":0.67119,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57661,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48768,0.14489,0.23214]},{"body_a":"peg","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.49934,-0.10032,0.05161],"force_p95":1.1836,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67326,"mean_force":0.23379,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49815,-0.03614,0.05319]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.19593,0.29633]},{"body_a":"peg","body_b":"channel_base_body","contact_count":257.0,"contact_point_centroid":[0.50008,-0.08091,0.00943],"force_p95":0.6036,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77061,"mean_force":0.53821,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49801,-0.03132,0.09969]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.5048,-0.05441,0.06099],"force_p95":0.30734,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35447,"mean_force":0.08703,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50015,-0.04322,0.03036]}],"total_contact_groups":14},"final_pose_error":0.02955,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49969,-0.08149,0.03403],"final_tcp_position":[0.49827,-0.03549,0.16832],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":3919.3518,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":299.0,"n_steps_budget":660.0,"object_pos_end":[0.49502,0.06372,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54516,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":300.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.48018,0.11004,0.16465],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.49447,0.06179,0.03599],"object_pos_start":[0.49502,0.06372,0.03391],"object_to_goal_dist_end":0.14195,"object_to_goal_dist_start":0.14393,"object_z_max":0.03598,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":454.0,"raw_peak_contact_force":8.53519,"tcp_end":[0.48996,0.09141,0.0426],"tcp_start":[0.48018,0.11004,0.16465],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":661.0,"n_steps_budget":600.0,"object_pos_end":[0.49515,0.0604,0.0357],"object_pos_start":[0.49447,0.06179,0.03599],"object_to_goal_dist_end":0.14055,"object_to_goal_dist_start":0.14195,"object_z_max":0.03627,"peak_contact_force":3919.3518,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1208.0,"raw_peak_contact_force":6.43219,"subtask_id":"contact","tcp_end":[0.49226,0.06026,0.02914],"tcp_start":[0.4907,0.06995,0.03161],"tcp_to_object_dist_end":0.00717,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.50315,-0.07077,0.03714],"object_pos_start":[0.50684,0.03331,0.03627],"object_to_goal_dist_end":0.01016,"object_to_goal_dist_start":0.11357,"object_z_max":0.03826,"peak_contact_force":0.34856,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":311.0,"raw_peak_contact_force":33.42398,"tcp_end":[0.50053,-0.04231,0.03007],"tcp_start":[0.49226,0.06026,0.02914],"tcp_to_object_dist_end":0.02945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.49969,-0.08149,0.03403],"object_pos_start":[0.50315,-0.07077,0.03714],"object_to_goal_dist_end":0.00616,"object_to_goal_dist_start":0.01016,"object_z_max":0.03752,"peak_contact_force":0.54492,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":305.0,"raw_peak_contact_force":1.67326,"tcp_end":[0.49827,-0.03549,0.16832],"tcp_start":[0.50053,-0.04231,0.03007],"tcp_to_object_dist_end":0.14195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46154,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0787,"approach_1.generator.speed":0.18886,"contact_1.contact_force_threshold":4.51906,"contact_1.generator.speed":0.0419,"descend_1.descend_lateral_y":0.01511,"descend_1.descend_z":-0.0022,"descend_1.generator.speed":0.08148,"push_1.generator.speed":0.0346,"push_1.push_depth":0.13614,"retract_1.retract_height":0.17032},"optimized_scores":{"best_composite_score":-0.10264,"best_fitness_score":0.23736,"best_task_score":0.12961},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":98.0,"contact_point_centroid":[0.47499,0.07782,0.05991],"force_p95":425.66412,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.81022,"mean_force":360.9015,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48493,0.08212,0.05824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.49656,0.06248,0.00926],"force_p95":164.67722,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":210.10978,"mean_force":23.67631,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4778,0.08927,0.08386]},{"body_a":"attachment","body_b":"peg","contact_count":139.0,"contact_point_centroid":[0.49627,0.07615,0.05693],"force_p95":176.38467,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":209.63544,"mean_force":74.81559,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48621,0.08197,0.05728]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.49142,0.00031,0.04151],"force_p95":23.37721,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.09098,"mean_force":3.94893,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48835,0.01189,0.02979]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52543,-0.04103,0.02992],"force_p95":26.92767,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.34996,"mean_force":10.42597,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48833,0.01742,0.03025]},{"body_a":"peg","body_b":"channel_base_body","contact_count":111.0,"contact_point_centroid":[0.49707,-0.008,0.00868],"force_p95":9.79728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.94852,"mean_force":2.12028,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48869,0.04179,0.03307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.49624,0.0148,0.00896],"force_p95":10.98858,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.53317,"mean_force":1.65421,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49056,0.07495,0.0389]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.4749,0.03272,0.02441],"force_p95":10.85045,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.87233,"mean_force":5.05089,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49032,0.07342,0.03818]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47493,0.03332,0.02448],"force_p95":9.55266,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.8362,"mean_force":2.63607,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49005,0.073,0.03777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.49462,0.05885,0.00933],"force_p95":0.61732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59249,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47895,0.14005,0.21864]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49771,0.19467,0.29454]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52523,0.02569,0.05738],"force_p95":2.04578,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1953,"mean_force":1.08078,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49243,0.07862,0.04391]}],"total_contact_groups":12},"final_pose_error":0.11248,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50515,-0.05065,0.02821],"final_tcp_position":[0.48851,-0.01541,0.02752],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":474.81022,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":345.0,"n_steps_budget":720.0,"object_pos_end":[0.4942,0.05902,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54742,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":351.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.46642,0.10376,0.13803],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":456.0,"n_steps_budget":870.0,"object_pos_end":[0.50254,0.03436,0.04191],"object_pos_start":[0.4942,0.05902,0.03385],"object_to_goal_dist_end":0.1144,"object_to_goal_dist_start":0.13928,"object_z_max":0.04186,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":694.0,"raw_peak_contact_force":474.81022,"tcp_end":[0.49205,0.07786,0.04148],"tcp_start":[0.46642,0.10376,0.13803],"tcp_to_object_dist_end":0.04475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":58.0,"n_steps_budget":630.0,"object_pos_end":[0.49309,0.00824,0.02404],"object_pos_start":[0.50254,0.03436,0.04191],"object_to_goal_dist_end":0.08993,"object_to_goal_dist_start":0.1144,"object_z_max":0.04192,"peak_contact_force":10.92277,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":45.0,"raw_peak_contact_force":11.53317,"subtask_id":"contact","tcp_end":[0.49026,0.07318,0.03804],"tcp_start":[0.49029,0.07322,0.03809],"tcp_to_object_dist_end":0.06649,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.50515,-0.05065,0.02821],"object_pos_start":[0.49312,0.0084,0.02405],"object_to_goal_dist_end":0.03205,"object_to_goal_dist_start":0.09009,"object_z_max":0.03072,"peak_contact_force":44.09098,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":200.0,"raw_peak_contact_force":44.09098,"tcp_end":[0.48851,-0.01541,0.02752],"tcp_start":[0.49026,0.07318,0.03804],"tcp_to_object_dist_end":0.03897,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99338,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08835,"approach_1.generator.speed":0.13059,"contact_1.contact_force_threshold":4.92005,"contact_1.generator.speed":0.04291,"descend_1.descend_lateral_y":0.02649,"descend_1.descend_z":-0.00244,"descend_1.generator.speed":0.10741,"push_1.generator.speed":0.02874,"push_1.push_depth":0.13096,"retract_1.retract_height":0.16609},"optimized_scores":{"best_composite_score":0.04799,"best_fitness_score":0.38799,"best_task_score":0.30352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":76.0,"contact_point_centroid":[0.50335,0.03631,0.04706],"force_p95":34.48377,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.66025,"mean_force":10.53103,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,0.04795,0.02774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":57.0,"contact_point_centroid":[0.52514,0.01847,0.03687],"force_p95":34.54128,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.38755,"mean_force":10.04917,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,0.04722,0.02774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.50707,0.01189,0.00996],"force_p95":22.90675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.17778,"mean_force":10.9644,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.05754,0.02831]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.50532,0.07885,0.0094],"force_p95":0.55012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.22712,"mean_force":0.75867,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51778,0.11646,0.09439]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50657,0.0978,0.04801],"force_p95":15.58212,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.05151,"mean_force":8.0334,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50712,0.10976,0.04799]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.5027,0.03904,0.00993],"force_p95":3.58817,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.67532,"mean_force":1.98478,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49895,0.08495,0.03083]},{"body_a":"attachment","body_b":"peg","contact_count":724.0,"contact_point_centroid":[0.50154,0.07124,0.03998],"force_p95":3.30468,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.34801,"mean_force":1.70465,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49863,0.08313,0.0303]},{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.50549,0.08095,0.00934],"force_p95":0.57896,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59647,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51931,0.15227,0.22331]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50144,0.1957,0.29487]}],"total_contact_groups":9},"final_pose_error":0.11972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50777,-0.00334,0.03556],"final_tcp_position":[0.49708,0.02517,0.02695],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":44.09098,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":930.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5444,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":343.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.53121,0.12418,0.1474],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":315.0,"n_steps_budget":720.0,"object_pos_end":[0.50521,0.07833,0.03578],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.15847,"object_to_goal_dist_start":0.1611,"object_z_max":0.03578,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":321.0,"raw_peak_contact_force":18.22712,"tcp_end":[0.50554,0.1088,0.04111],"tcp_start":[0.53121,0.12418,0.1474],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":845.0,"n_steps_budget":600.0,"object_pos_end":[0.50352,0.07353,0.03537],"object_pos_start":[0.50521,0.07833,0.03578],"object_to_goal_dist_end":0.15364,"object_to_goal_dist_start":0.15847,"object_z_max":0.03586,"peak_contact_force":44.09098,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1481.0,"raw_peak_contact_force":6.67532,"subtask_id":"contact","tcp_end":[0.49809,0.06616,0.02944],"tcp_start":[0.49949,0.08315,0.03077],"tcp_to_object_dist_end":0.01091,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":87.0,"n_steps_budget":1000.0,"object_pos_end":[0.50777,-0.00334,0.03556],"object_pos_start":[0.50688,0.03715,0.03583],"object_to_goal_dist_end":0.07718,"object_to_goal_dist_start":0.11743,"object_z_max":0.03645,"peak_contact_force":43.66025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":159.0,"raw_peak_contact_force":43.66025,"tcp_end":[0.49708,0.02517,0.02695],"tcp_start":[0.49809,0.06616,0.02944],"tcp_to_object_dist_end":0.03165,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```